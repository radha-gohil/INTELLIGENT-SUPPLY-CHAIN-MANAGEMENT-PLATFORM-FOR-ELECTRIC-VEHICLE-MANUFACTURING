from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint
)

from backend.app.database.connection import Base


# ============================================================
# VEHICLE BOM MODEL
# ============================================================

class VehicleBOM(Base):

    __tablename__ = "vehicle_bom"

    __table_args__ = (
        UniqueConstraint(
            "vehicle_id",
            "component_id",
            name="uq_vehicle_bom_vehicle_component"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    vehicle_id = Column(
        Integer,
        ForeignKey(
            "vehicles.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    component_id = Column(
        Integer,
        ForeignKey(
            "components.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    quantity_per_vehicle = Column(
        Float,
        nullable=False,
        default=1
    )

    unit = Column(
        String(30),
        nullable=False,
        default="Unit"
    )