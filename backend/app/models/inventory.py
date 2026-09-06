from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint
)

from backend.app.database.connection import Base


# ============================================================
# INVENTORY MODEL
# ============================================================

class Inventory(Base):

    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "component_id",
            "warehouse",
            name="uq_inventory_component_warehouse"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
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

    warehouse = Column(
        String(100),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # PHYSICAL STOCK
    # --------------------------------------------------------

    current_stock = Column(
        Float,
        nullable=False,
        default=0
    )

    reserved_stock = Column(
        Float,
        nullable=False,
        default=0
    )

    available_stock = Column(
        Float,
        nullable=False,
        default=0
    )

    # --------------------------------------------------------
    # INVENTORY CONTROL
    # --------------------------------------------------------

    safety_stock = Column(
        Float,
        nullable=False,
        default=0
    )

    reorder_level = Column(
        Float,
        nullable=False,
        default=0
    )

    inventory_status = Column(
        String(30),
        nullable=False,
        default="NORMAL",
        index=True
    )

    last_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )