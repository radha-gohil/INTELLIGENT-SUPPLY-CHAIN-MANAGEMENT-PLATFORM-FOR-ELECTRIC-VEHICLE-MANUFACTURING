from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from backend.app.database.connection import Base


class PurchaseOrderStatusHistory(Base):
    __tablename__ = "purchase_order_status_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey(
            "purchase_orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    from_stage = Column(
        String(50),
        nullable=True,
        index=True,
    )

    to_stage = Column(
        String(50),
        nullable=False,
        index=True,
    )

    location = Column(
        String(200),
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    changed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )