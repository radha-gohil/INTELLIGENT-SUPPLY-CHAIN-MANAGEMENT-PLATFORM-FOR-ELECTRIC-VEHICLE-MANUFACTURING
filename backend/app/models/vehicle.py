from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String
)

from backend.app.database.connection import Base


# ============================================================
# VEHICLE MODEL
# ============================================================

class Vehicle(Base):

    __tablename__ = "vehicles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Business ID from CSV:
    # EV001, EV002...
    vehicle_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    vehicle_type = Column(
        String(150),
        nullable=False
    )

    vehicle_category = Column(
        String(100),
        nullable=False
    )

    use_case = Column(
        String(150),
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )