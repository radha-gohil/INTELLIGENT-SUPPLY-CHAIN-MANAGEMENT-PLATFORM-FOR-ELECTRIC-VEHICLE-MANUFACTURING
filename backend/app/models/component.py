from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    String
)

from backend.app.database.connection import Base


# ============================================================
# COMPONENT MODEL
# ============================================================

class Component(Base):

    __tablename__ = "components"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Business ID from CSV:
    # P001, P002, P003...
    part_id = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    part_name = Column(
        String(150),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False,
        index=True
    )

    sub_category = Column(
        String(100),
        nullable=True
    )

    unit = Column(
        String(30),
        nullable=False,
        default="Unit"
    )

    # Kept for compatibility with existing backend code.
    # Actual supplier-specific price is stored in
    # supplier_components.unit_price.
    unit_cost = Column(
        Float,
        nullable=True
    )

    criticality = Column(
        String(30),
        nullable=False,
        default="MEDIUM",
        index=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )