import secrets

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User
from app.models.claim import Claim
from app.models.donation import Donation
from app.models.pickup import Pickup

from app.schemas.pickup import (
    PickupCreate,
    VolunteerAssignment,
    PickupVerification,
    PickupResponse,
    PickupCreatedResponse
)

from app.utils.dependencies import (
    require_role,
    get_current_user
)


router = APIRouter(
    prefix="/pickups",
    tags=["Pickup & Delivery"]
)


# 1. CREATE PICKUP SCHEDULE

@router.post("/", response_model=PickupCreatedResponse, status_code=201)
def create_pickup(
    data: PickupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    claim = db.query(Claim).filter(
        Claim.id == data.claim_id
    ).first()

    if not claim:
        raise HTTPException(404, "Claim not found")

    if claim.status != "accepted":
        raise HTTPException(
            400,
            "Only accepted claims can be scheduled"
        )

    donation = db.query(Donation).filter(
        Donation.id == claim.donation_id
    ).first()

    if not donation or donation.donor_id != current_user.id:
        raise HTTPException(
            403,
            "You cannot schedule this pickup"
        )

    if data.pickup_time.tzinfo is None:
        raise HTTPException(
            422,
            "Pickup time must include timezone"
        )

    if data.pickup_time <= datetime.now(timezone.utc):
        raise HTTPException(
            400,
            "Pickup time must be in the future"
        )

    if data.pickup_time > donation.pickup_deadline:
        raise HTTPException(
            400,
            "Pickup time exceeds the pickup deadline"
        )

    existing = db.query(Pickup).filter(
        Pickup.claim_id == claim.id
    ).first()

    if existing:
        raise HTTPException(
            400,
            "Pickup already scheduled"
        )

    pickup = Pickup(
        claim_id=claim.id,
        pickup_time=data.pickup_time,
        pickup_address=data.pickup_address,
        delivery_address=data.delivery_address,
        verification_code=f"{secrets.randbelow(1000000):06d}",
        status="scheduled"
    )

    db.add(pickup)
    db.commit()
    db.refresh(pickup)

    return pickup


# 2. ASSIGN VOLUNTEER

@router.patch("/{pickup_id}/assign", response_model=PickupResponse)
def assign_volunteer(
    pickup_id: int,
    data: VolunteerAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    pickup = db.query(Pickup).filter(
        Pickup.id == pickup_id
    ).first()

    if not pickup:
        raise HTTPException(404, "Pickup not found")

    claim = db.query(Claim).filter(
        Claim.id == pickup.claim_id
    ).first()

    donation = db.query(Donation).filter(
        Donation.id == claim.donation_id
    ).first()

    if donation.donor_id != current_user.id:
        raise HTTPException(
            403,
            "You cannot assign this pickup"
        )

    if pickup.status != "scheduled":
        raise HTTPException(
            400,
            "Volunteer cannot be changed after pickup"
        )

    volunteer = db.query(User).filter(
        User.id == data.volunteer_id,
        User.role == "volunteer",
        User.is_active == True
    ).first()

    if not volunteer:
        raise HTTPException(
            404,
            "Active volunteer not found"
        )

    pickup.volunteer_id = volunteer.id

    db.commit()
    db.refresh(pickup)

    return pickup


# 3. VIEW MY PICKUPS

@router.get("/my-pickups", response_model=list[PickupResponse])
def get_my_pickups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Pickup)

    if current_user.role == "volunteer":

        query = query.filter(
            Pickup.volunteer_id == current_user.id
        )

    elif current_user.role == "donor":

        query = query.join(
            Claim,
            Pickup.claim_id == Claim.id
        ).join(
            Donation,
            Claim.donation_id == Donation.id
        ).filter(
            Donation.donor_id == current_user.id
        )

    elif current_user.role == "ngo":

        query = query.join(
            Claim,
            Pickup.claim_id == Claim.id
        ).filter(
            Claim.ngo_id == current_user.id
        )

    else:
        raise HTTPException(403, "Unauthorized")

    return query.order_by(
        Pickup.created_at.desc()
    ).all()


# 4. VOLUNTEER CONFIRMS FOOD PICKUP

@router.patch("/{pickup_id}/confirm-pickup", response_model=PickupResponse)
def confirm_pickup(
    pickup_id: int,
    data: PickupVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("volunteer"))
):

    pickup = db.query(Pickup).filter(
        Pickup.id == pickup_id
    ).with_for_update().first()

    if not pickup:
        raise HTTPException(404, "Pickup not found")

    if pickup.volunteer_id != current_user.id:
        raise HTTPException(
            403,
            "This pickup is not assigned to you"
        )

    if pickup.status != "scheduled":
        raise HTTPException(
            400,
            "Pickup cannot be confirmed in its current status"
        )

    if not secrets.compare_digest(
        pickup.verification_code,
        data.verification_code
    ):
        raise HTTPException(
            400,
            "Invalid verification code"
        )

    pickup.status = "picked_up"

    pickup.picked_up_at = datetime.now(timezone.utc)

    donation = db.query(Donation).join(
        Claim,
        Claim.donation_id == Donation.id
    ).filter(
        Claim.id == pickup.claim_id
    ).first()

    donation.status = "picked_up"

    db.commit()
    db.refresh(pickup)

    return pickup


# 5. NGO CONFIRMS DELIVERY

@router.patch("/{pickup_id}/confirm-delivery", response_model=PickupResponse)
def confirm_delivery(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ngo":
        raise HTTPException(
            403,
            "Only NGOs can confirm delivery"
        )

    pickup = db.query(Pickup).filter(
        Pickup.id == pickup_id
    ).with_for_update().first()

    if not pickup:
        raise HTTPException(404, "Pickup not found")

    claim = db.query(Claim).filter(
        Claim.id == pickup.claim_id
    ).first()

    if claim.ngo_id != current_user.id:
        raise HTTPException(
            403,
            "You cannot confirm this delivery"
        )

    if pickup.status != "picked_up":
        raise HTTPException(
            400,
            "Food must be picked up before delivery confirmation"
        )

    pickup.status = "delivered"

    pickup.delivered_at = datetime.now(timezone.utc)

    donation = db.query(Donation).filter(
        Donation.id == claim.donation_id
    ).first()

    donation.status = "completed"

    db.commit()
    db.refresh(pickup)

    return pickup