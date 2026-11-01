from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone

from app.database import get_db

from app.models.user import User
from app.models.donation import Donation

from app.schemas.donation import (
    DonationCreate,
    DonationUpdate,
    DonationResponse
)

from app.utils.dependencies import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/donations",
    tags=["Food Donations"]
)


# CREATE DONATION

@router.post("/", response_model=DonationResponse, status_code=201)
def create_donation(
    donation_data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    donation = Donation(
        **donation_data.model_dump(),
        donor_id=current_user.id
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    return donation


# VIEW ALL AVAILABLE DONATIONS

@router.get("/", response_model=list[DonationResponse])
def get_donations(
    search: str = Query(default=None),
    category: str = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Donation).filter(
        Donation.status == "available",
        Donation.pickup_deadline > datetime.now(timezone.utc),
        Donation.safe_until > datetime.now(timezone.utc)
    )

    if search:

        query = query.filter(
            or_(
                Donation.food_name.ilike(f"%{search}%"),
                Donation.description.ilike(f"%{search}%")
            )
        )

    if category:

        query = query.filter(
            Donation.food_category == category
        )

    return query.order_by(
        Donation.created_at.desc()
    ).all()


# VIEW MY DONATIONS

@router.get("/my-donations", response_model=list[DonationResponse])
def get_my_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    return db.query(Donation).filter(
        Donation.donor_id == current_user.id
    ).order_by(
        Donation.created_at.desc()
    ).all()


# VIEW DONATION DETAILS

@router.get("/{donation_id}", response_model=DonationResponse)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    donation = db.query(Donation).filter(
        Donation.id == donation_id
    ).first()

    if not donation:

        raise HTTPException(
            status_code=404,
            detail="Donation not found"
        )

    return donation


# UPDATE DONATION

@router.patch("/{donation_id}", response_model=DonationResponse)
def update_donation(
    donation_id: int,
    donation_data: DonationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    donation = db.query(Donation).filter(
        Donation.id == donation_id,
        Donation.donor_id == current_user.id
    ).first()

    if not donation:

        raise HTTPException(
            status_code=404,
            detail="Donation not found"
        )

    if donation.status != "available":

        raise HTTPException(
            status_code=400,
            detail="Only available donations can be edited"
        )

    updates = donation_data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(donation, key, value)

    db.commit()
    db.refresh(donation)

    return donation


# CANCEL DONATION

@router.delete("/{donation_id}")
def cancel_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("donor"))
):

    donation = db.query(Donation).filter(
        Donation.id == donation_id,
        Donation.donor_id == current_user.id
    ).first()

    if not donation:

        raise HTTPException(
            status_code=404,
            detail="Donation not found"
        )

    if donation.status != "available":

        raise HTTPException(
            status_code=400,
            detail="This donation cannot be cancelled"
        )

    donation.status = "cancelled"

    db.commit()

    return {
        "message": "Donation cancelled successfully"
    }