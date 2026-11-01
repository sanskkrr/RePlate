from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class PickupCreate(BaseModel):

    claim_id: int = Field(gt=0)

    pickup_time: datetime

    pickup_address: str

    delivery_address: str


class VolunteerAssignment(BaseModel):

    volunteer_id: int = Field(gt=0)


class PickupVerification(BaseModel):

    verification_code: str = Field(
        min_length=6,
        max_length=6
    )


class PickupResponse(BaseModel):

    id: int

    claim_id: int

    volunteer_id: Optional[int]

    pickup_time: datetime

    pickup_address: str

    delivery_address: str

    status: str

    picked_up_at: Optional[datetime]

    delivered_at: Optional[datetime]

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class PickupCreatedResponse(PickupResponse):
    verification_code: str