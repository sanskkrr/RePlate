from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.database import Base


class Donation(Base):

    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)

    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    food_name = Column(String(150), nullable=False)

    food_category = Column(String(50), nullable=False)

    description = Column(Text, nullable=True)

    quantity = Column(Float, nullable=False)

    quantity_unit = Column(String(30), default="portions")

    preparation_time = Column(DateTime(timezone=True), nullable=False)

    safe_until = Column(DateTime(timezone=True), nullable=False)

    pickup_deadline = Column(DateTime(timezone=True), nullable=False)

    storage_conditions = Column(String(255), nullable=False)

    pickup_address = Column(String(255), nullable=False)

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    image_url = Column(String(500), nullable=True)

    status = Column(String(30), default="available", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())