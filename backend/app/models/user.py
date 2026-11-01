from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(20), nullable=False)

    phone = Column(String(20), nullable=True)

    organization_name = Column(String(150), nullable=True)

    address = Column(String(255), nullable=True)

    latitude = Column(String(30), nullable=True)

    longitude = Column(String(30), nullable=True)

    is_verified = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())