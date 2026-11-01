from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ClaimCreate(BaseModel):

    beneficiaries: int = Field(gt=0)

    message: Optional[str] = None


class ClaimDecision(BaseModel):

    decision: str

    def validate_decision(self):
        if self.decision not in ["accepted", "rejected"]:
            raise ValueError("Invalid decision")

        return self


class ClaimResponse(BaseModel):

    id: int

    donation_id: int

    ngo_id: int

    beneficiaries: int

    message: Optional[str]

    status: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)