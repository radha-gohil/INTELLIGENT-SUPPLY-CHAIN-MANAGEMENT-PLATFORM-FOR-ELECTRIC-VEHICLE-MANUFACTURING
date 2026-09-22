from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# SHIPMENT RESPONSE
# ============================================================

class ShipmentResponse(BaseModel):

    id: int

    purchase_order_id: int

    shipment_number: str

    # --------------------------------------------------------
    # ROUTE
    # --------------------------------------------------------

    origin_location: str

    destination_location: str

    origin_latitude: Optional[float] = None

    origin_longitude: Optional[float] = None

    destination_latitude: Optional[float] = None

    destination_longitude: Optional[float] = None

    # --------------------------------------------------------
    # CURRENT GPS POSITION
    # --------------------------------------------------------

    current_latitude: Optional[float] = None

    current_longitude: Optional[float] = None

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status: str

    progress_percentage: float

    # --------------------------------------------------------
    # DISTANCE / SPEED
    # --------------------------------------------------------

    total_distance_km: Optional[float] = None

    remaining_distance_km: Optional[float] = None

    current_speed_kmph: Optional[float] = None

    # --------------------------------------------------------
    # ETA
    # --------------------------------------------------------

    estimated_arrival: Optional[datetime] = None

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    dispatched_at: Optional[datetime] = None

    arrived_at: Optional[datetime] = None

    last_location_update: Optional[datetime] = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# GPS TRACKING POINT RESPONSE
# ============================================================

class ShipmentTrackingPointResponse(BaseModel):

    id: int

    shipment_id: int

    latitude: float

    longitude: float

    speed_kmph: Optional[float] = None

    progress_percentage: float

    remaining_distance_km: Optional[float] = None

    location_name: Optional[str] = None

    status: str

    recorded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )