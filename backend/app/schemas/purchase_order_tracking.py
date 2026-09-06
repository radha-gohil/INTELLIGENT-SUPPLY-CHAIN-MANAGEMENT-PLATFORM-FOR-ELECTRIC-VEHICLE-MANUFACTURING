from datetime import (
    date,
    datetime
)

from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


# ============================================================
# CREATE PURCHASE ORDER
# ============================================================

class PurchaseOrderCreateRequest(BaseModel):

    supplier_id: int = Field(
        gt=0
    )

    component_id: int = Field(
        gt=0
    )

    warehouse: str

    quantity_ordered: float = Field(
        gt=0
    )

    vehicle_id: Optional[int] = None

    required_date: Optional[date] = None

    urgency: Optional[str] = None


# ============================================================
# UPDATE TRACKING
# ============================================================

class PurchaseOrderTrackingUpdateRequest(BaseModel):

    tracking_stage: str

    current_location: Optional[str] = None

    tracking_notes: Optional[str] = None


# ============================================================
# RECEIVE ORDER
# ============================================================

class PurchaseOrderReceiveRequest(BaseModel):

    quantity_received: float = Field(
        gt=0
    )


# ============================================================
# RESPONSE
# ============================================================

class PurchaseOrderTrackingResponse(BaseModel):

    id: int

    po_number: str

    po_date: date

    supplier_id: int

    supplier_code: Optional[str] = None

    supplier_name: Optional[str] = None

    component_id: int

    part_id: Optional[str] = None

    part_name: Optional[str] = None

    vehicle_id: Optional[int] = None

    vehicle_code: Optional[str] = None

    vehicle_type: Optional[str] = None

    warehouse: str

    quantity_ordered: float

    quantity_received: float

    remaining_quantity: float

    unit_cost: float

    order_value: float

    order_status: str

    tracking_stage: Optional[str] = None

    current_location: Optional[str] = None

    tracking_notes: Optional[str] = None

    expected_delivery_date: Optional[date] = None

    actual_delivery_date: Optional[date] = None

    required_date: Optional[date] = None

    urgency: Optional[str] = None

    days_until_expected_arrival: Optional[int] = None

    is_delayed: bool

    last_tracking_update: Optional[datetime] = None

    dispatched_at: Optional[datetime] = None

    arrived_at_warehouse_at: Optional[datetime] = None

    source_type: str