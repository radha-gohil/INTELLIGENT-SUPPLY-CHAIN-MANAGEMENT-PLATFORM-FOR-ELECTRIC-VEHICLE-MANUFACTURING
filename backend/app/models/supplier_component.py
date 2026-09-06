from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint
)

from backend.app.database.connection import Base


# ============================================================
# SUPPLIER COMPONENT MODEL
# ============================================================

class SupplierComponent(Base):

    __tablename__ = "supplier_components"

    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "component_id",
            name="uq_supplier_component_pair"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey(
            "suppliers.id",
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

    supplier_part_code = Column(
        String(50),
        nullable=True
    )

    unit_price = Column(
        Float,
        nullable=True
    )

    minimum_order_quantity = Column(
        Integer,
        nullable=False,
        default=1
    )

    standard_lead_time_days = Column(
        Integer,
        nullable=True
    )

    maximum_capacity = Column(
        Integer,
        nullable=True
    )

    is_approved = Column(
        Boolean,
        nullable=False,
        default=True
    )