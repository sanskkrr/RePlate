from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database import Base


class Pickup(Base):

    __tablename__ = "pickups"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    claim_id = Column(
        Integer,
        ForeignKey("claims.id"),
        nullable=False,
        unique=True
    )

    volunteer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    pickup_time = Column(
        DateTime(timezone=True),
        nullable=False
    )

    pickup_address = Column(
        String(255),
        nullable=False
    )

    delivery_address = Column(
        String(255),
        nullable=False
    )

    verification_code = Column(
        String(6),
        nullable=False
    )

    status = Column(
        String(30),
        default="scheduled",
        nullable=False
    )

    picked_up_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )