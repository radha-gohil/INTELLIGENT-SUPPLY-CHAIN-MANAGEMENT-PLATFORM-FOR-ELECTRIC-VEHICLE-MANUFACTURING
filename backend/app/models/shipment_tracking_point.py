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
# SHIPMENT TRACKING POINT MODEL
# ============================================================

class ShipmentTrackingPoint(Base):

    __tablename__ = "shipment_tracking_points"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ========================================================
    # SHIPMENT
    # ========================================================

    shipment_id = Column(
        Integer,
        ForeignKey(
            "shipments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ========================================================
    # GPS POSITION
    # ========================================================

    latitude = Column(
        Float,
        nullable=False,
    )

    longitude = Column(
        Float,
        nullable=False,
    )

    # ========================================================
    # MOVEMENT INFORMATION
    # ========================================================

    speed_kmph = Column(
        Float,
        nullable=True,
    )

    progress_percentage = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    remaining_distance_km = Column(
        Float,
        nullable=True,
    )

    # ========================================================
    # LOCATION INFORMATION
    # ========================================================

    location_name = Column(
        String(200),
        nullable=True,
    )

    # ========================================================
    # STATUS
    # ========================================================

    status = Column(
        String(50),
        nullable=False,
        default="IN_TRANSIT",
    )

    # ========================================================
    # TIMESTAMP
    # ========================================================

    recorded_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )