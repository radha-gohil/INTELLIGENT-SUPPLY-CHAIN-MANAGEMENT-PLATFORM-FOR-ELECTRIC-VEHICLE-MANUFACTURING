from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from backend.app.database.connection import Base


class PurchaseOrder(Base):

    __tablename__ = "purchase_orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    po_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    po_date = Column(
        Date,
        nullable=False,
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey(
            "suppliers.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    component_id = Column(
        Integer,
        ForeignKey(
            "components.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    # ========================================================
    # VEHICLE REQUIREMENT
    # ========================================================

    vehicle_id = Column(
        Integer,
        ForeignKey(
            "vehicles.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    required_date = Column(
        Date,
        nullable=True,
        index=True
    )

    urgency = Column(
        String(30),
        nullable=True,
        index=True
    )

    # ========================================================
    # DESTINATION
    # ========================================================

    warehouse = Column(
        String(100),
        nullable=False,
        index=True
    )

    # ========================================================
    # QUANTITY / VALUE
    # ========================================================

    quantity_ordered = Column(
        Float,
        nullable=False,
        default=0
    )

    quantity_received = Column(
        Float,
        nullable=False,
        default=0
    )

    unit_cost = Column(
        Float,
        nullable=False,
        default=0
    )

    order_value = Column(
        Float,
        nullable=False,
        default=0
    )

    # ========================================================
    # DELIVERY
    # ========================================================

    expected_delivery_date = Column(
        Date,
        nullable=True,
        index=True
    )

    actual_delivery_date = Column(
        Date,
        nullable=True
    )

    quantity_shortage = Column(
        Float,
        nullable=False,
        default=0
    )

    delivery_delay_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    # ========================================================
    # OPERATIONAL ORDER STATUS
    # ========================================================
    #
    # PLACED
    # CONFIRMED
    # IN_TRANSIT
    # PARTIAL
    # DELIVERED
    # CANCELLED
    #
    # ========================================================

    order_status = Column(
        String(40),
        nullable=False,
        index=True
    )

    # ========================================================
    # DETAILED LOGISTICS TRACKING
    # ========================================================
    #
    # ORDER_PLACED
    # SUPPLIER_CONFIRMED
    # READY_FOR_DISPATCH
    # DISPATCHED
    # IN_TRANSIT
    # ARRIVED_AT_WAREHOUSE
    # PARTIALLY_RECEIVED
    # RECEIVED
    # CANCELLED
    #
    # ========================================================

    tracking_stage = Column(
        String(50),
        nullable=True,
        index=True
    )

    current_location = Column(
        String(200),
        nullable=True
    )

    tracking_notes = Column(
        Text,
        nullable=True
    )

    last_tracking_update = Column(
        DateTime,
        nullable=True
    )

    dispatched_at = Column(
        DateTime,
        nullable=True
    )

    arrived_at_warehouse_at = Column(
        DateTime,
        nullable=True
    )

    # HISTORICAL_IMPORT / APP_ORDER
    source_type = Column(
        String(30),
        nullable=False,
        default="HISTORICAL_IMPORT",
        index=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )