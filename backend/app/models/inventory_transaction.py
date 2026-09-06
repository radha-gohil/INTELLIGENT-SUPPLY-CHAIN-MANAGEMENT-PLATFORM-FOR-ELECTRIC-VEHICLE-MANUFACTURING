from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String
)

from backend.app.database.connection import Base


# ============================================================
# INVENTORY TRANSACTION MODEL
# ============================================================

class InventoryTransaction(Base):

    __tablename__ = "inventory_transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_id = Column(
        String(30),
        unique=True,
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

    warehouse = Column(
        String(100),
        nullable=False,
        index=True
    )

    transaction_type = Column(
        String(30),
        nullable=False,
        index=True
    )

    quantity = Column(
        Float,
        nullable=False
    )

    reference_id = Column(
        String(50),
        nullable=True,
        index=True
    )

    transaction_date = Column(
        DateTime,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )