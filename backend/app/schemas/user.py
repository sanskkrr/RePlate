from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal


UserRole = Literal["donor", "ngo", "volunteer", "admin"]


class UserRegister(BaseModel):

    full_name: str = Field(min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(min_length=8)

    role: Literal["donor", "ngo", "volunteer"]

    phone: Optional[str] = None

    organization_name: Optional[str] = None

    address: Optional[str] = None


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class UserResponse(BaseModel):

    id: int

    full_name: str

    email: EmailStr

    role: UserRole

    phone: Optional[str] = None

    organization_name: Optional[str] = None

    is_verified: bool

    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user: UserResponse