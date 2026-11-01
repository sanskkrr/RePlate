from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db

from app.models.user import User
from app.models.donation import Donation
from app.models.claim import Claim

from app.schemas.claim import (
    ClaimCreate,
    ClaimDecision,
    ClaimResponse
)

from app.utils.dependencies import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/claims",
    tags=["Donation Claims"]
)


# ----------------------------------
# 1. NGO REQUESTS A DONATION
# ----------------------------------

@router.post("/", response_model=ClaimResponse, status_code=201)
def create_claim(
    donation_id: int,
    claim_data: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ngo"))
):

    donation = db.query(Donation).filter(
        Donation.id == donation_id
    ).with_for_update().first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail="Donation not found"
        )

    if donation.status != "available":
        raise HTTPException(
            status_code=400,
            detail="Donation is no longer available"
        )

    if donation.donor_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot claim your own donation"
        )

    now = datetime.now(timezone.utc)

    if donation.safe_until <= now:
        raise HTTPException(
            status_code=400,
            detail="Food safety deadline has passed"
        )

    if donation.pickup_deadline <= now:
        raise HTTPException(
            status_code=400,
            detail="Pickup deadline has passed"
        )

    existing_claim = db.query(Claim).filter(
        Claim.donation_id == donation_id,
        Claim.ngo_id == current_user.id,
        Claim.status == "pending"
    ).first()

    if existing_claim:
        raise HTTPException(
            status_code=400,
            detail="You have already requested this donation"
        )

    claim = Claim(
        donation_id=donation_id,
        ngo_id=current_user.id,
        beneficiaries=claim_data.beneficiaries,
        message=claim_data.message,
        status="pending"
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    return claim


# ----------------------------------
# 2. NGO VIEWS ITS REQUESTS
# ----------------------------------

@router.get("/my-requests", response_model=list[ClaimResponse])
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ngo"))
):

    return db.query(Claim).filter(
        Claim.ngo_id == current_user.id
    ).order_by(
        Claim.created_at.desc()
    ).all()


# ----------------------------------
# 3. DONOR VIEWS INCOMING REQUESTS
# ----------------------------------

@router.get("/received", response_model=list[ClaimResponse])
def get_received_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    return db.query(Claim).join(
        Donation,
        Claim.donation_id == Donation.id
    ).filter(
        Donation.donor_id == current_user.id
    ).order_by(
        Claim.created_at.desc()
    ).all()


# ----------------------------------
# 4. DONOR ACCEPTS OR REJECTS
# ----------------------------------

@router.patch("/{claim_id}/decision", response_model=ClaimResponse)
def decide_claim(
    claim_id: int,
    decision_data: ClaimDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    if decision_data.decision not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be accepted or rejected"
        )

    claim = db.query(Claim).filter(
        Claim.id == claim_id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found"
        )

    donation = db.query(Donation).filter(
        Donation.id == claim.donation_id
    ).with_for_update().first()

    if not donation or donation.donor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot manage this claim"
        )

    if claim.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="This request has already been processed"
        )

    if decision_data.decision == "accepted":

        if donation.status != "available":
            raise HTTPException(
                status_code=400,
                detail="Donation is no longer available"
            )

        if donation.safe_until <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=400,
                detail="Food safety deadline has passed"
            )

        claim.status = "accepted"

        donation.status = "claimed"

        # Reject other pending requests for this donation
        other_claims = db.query(Claim).filter(
            Claim.donation_id == donation.id,
            Claim.id != claim.id,
            Claim.status == "pending"
        ).all()

        for other in other_claims:
            other.status = "rejected"

    else:

        claim.status = "rejected"

    db.commit()
    db.refresh(claim)

    return claim