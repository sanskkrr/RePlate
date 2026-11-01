from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.sql import func

from app.database import Base


class Claim(Base):

    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)

    donation_id = Column(
        Integer,
        ForeignKey("donations.id"),
        nullable=False
    )

    ngo_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    beneficiaries = Column(Integer, nullable=False)

    message = Column(Text, nullable=True)

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )