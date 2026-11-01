from pydantic import BaseModel, Field, ConfigDict, model_validator

from datetime import datetime
from typing import Optional


class DonationCreate(BaseModel):

    food_name: str = Field(min_length=2, max_length=150)

    food_category: str

    description: Optional[str] = None

    quantity: float = Field(gt=0)

    quantity_unit: str = "portions"

    preparation_time: datetime

    safe_until: datetime

    pickup_deadline: datetime

    storage_conditions: str

    pickup_address: str

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    @model_validator(mode="after")
    def validate_deadlines(self):

        if self.preparation_time.tzinfo is None:
            raise ValueError("Preparation time must include timezone")

        if self.safe_until.tzinfo is None:
            raise ValueError("Safe-until time must include timezone")

        if self.pickup_deadline.tzinfo is None:
            raise ValueError("Pickup deadline must include timezone")

        if self.safe_until <= self.preparation_time:
            raise ValueError("Safe-until must be after preparation time")

        if self.pickup_deadline <= self.preparation_time:
            raise ValueError("Pickup deadline must be after preparation time")

        if self.pickup_deadline > self.safe_until:
            raise ValueError("Pickup deadline cannot exceed safe-until time")

        return self


class DonationUpdate(BaseModel):

    food_name: Optional[str] = None

    food_category: Optional[str] = None

    description: Optional[str] = None

    quantity: Optional[float] = Field(default=None, gt=0)

    quantity_unit: Optional[str] = None

    preparation_time: Optional[datetime] = None

    safe_until: Optional[datetime] = None

    pickup_deadline: Optional[datetime] = None

    storage_conditions: Optional[str] = None

    pickup_address: Optional[str] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None


class DonationResponse(BaseModel):

    id: int

    donor_id: int

    food_name: str

    food_category: str

    description: Optional[str]

    quantity: float

    quantity_unit: str

    preparation_time: datetime

    safe_until: datetime

    pickup_deadline: datetime

    storage_conditions: str

    pickup_address: str

    latitude: Optional[float]

    longitude: Optional[float]

    image_url: Optional[str]

    status: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)