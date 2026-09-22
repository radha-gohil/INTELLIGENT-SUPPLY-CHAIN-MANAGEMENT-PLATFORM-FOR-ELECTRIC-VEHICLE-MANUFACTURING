from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from backend.app.database.connection import Base


# ============================================================
# SHIPMENT MODEL
# ============================================================

class Shipment(Base):

    __tablename__ = "shipments"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ========================================================
    # PURCHASE ORDER
    #
    # One application purchase order can have one shipment.
    # ========================================================

    purchase_order_id = Column(
        Integer,
        ForeignKey(
            "purchase_orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # ========================================================
    # SHIPMENT IDENTIFICATION
    # ========================================================

    shipment_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    # ========================================================
    # ROUTE
    # ========================================================

    origin_location = Column(
        String(200),
        nullable=False,
    )

    destination_location = Column(
        String(200),
        nullable=False,
    )

    origin_latitude = Column(
        Float,
        nullable=True,
    )

    origin_longitude = Column(
        Float,
        nullable=True,
    )

    destination_latitude = Column(
        Float,
        nullable=True,
    )

    destination_longitude = Column(
        Float,
        nullable=True,
    )

    # ========================================================
    # CURRENT GPS POSITION
    # ========================================================

    current_latitude = Column(
        Float,
        nullable=True,
    )

    current_longitude = Column(
        Float,
        nullable=True,
    )

    # ========================================================
    # SHIPMENT STATUS
    # ========================================================

    status = Column(
        String(50),
        nullable=False,
        default="CREATED",
        index=True,
    )

    # CREATED
    # DISPATCHED
    # IN_TRANSIT
    # ARRIVED
    # COMPLETED
    # CANCELLED

    # ========================================================
    # PROGRESS
    # ========================================================

    progress_percentage = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    # ========================================================
    # DISTANCE / SPEED
    # ========================================================

    total_distance_km = Column(
        Float,
        nullable=True,
    )

    remaining_distance_km = Column(
        Float,
        nullable=True,
    )

    current_speed_kmph = Column(
        Float,
        nullable=True,
    )

    # ========================================================
    # ESTIMATED ARRIVAL
    # ========================================================

    estimated_arrival = Column(
        DateTime,
        nullable=True,
    )

    # ========================================================
    # TIMESTAMPS
    # ========================================================

    dispatched_at = Column(
        DateTime,
        nullable=True,
    )

    arrived_at = Column(
        DateTime,
        nullable=True,
    )

    last_location_update = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )