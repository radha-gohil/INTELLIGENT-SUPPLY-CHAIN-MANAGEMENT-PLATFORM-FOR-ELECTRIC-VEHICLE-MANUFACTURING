from datetime import date, datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# CREATE PURCHASE ORDER REQUEST
# ============================================================

class PurchaseOrderCreateRequest(BaseModel):

    supplier_id: int

    component_id: int

    warehouse: str

    quantity_ordered: float = Field(
        ...,
        gt=0,
    )

    vehicle_id: Optional[int] = None

    required_date: Optional[date] = None

    urgency: Optional[str] = None


# ============================================================
# UPDATE PURCHASE ORDER TRACKING REQUEST
# ============================================================

class PurchaseOrderTrackingUpdateRequest(BaseModel):

    tracking_stage: str

    current_location: Optional[str] = None

    tracking_notes: Optional[str] = None


# ============================================================
# RECEIVE PURCHASE ORDER REQUEST
# ============================================================

class PurchaseOrderReceiveRequest(BaseModel):

    quantity_received: float = Field(
        ...,
        gt=0,
    )


# ============================================================
# PURCHASE ORDER TRACKING RESPONSE
# ============================================================

class PurchaseOrderTrackingResponse(BaseModel):

    id: int

    po_number: str

    po_date: date

    # --------------------------------------------------------
    # SUPPLIER
    # --------------------------------------------------------

    supplier_id: int

    supplier_code: Optional[str] = None

    supplier_name: Optional[str] = None

    # --------------------------------------------------------
    # COMPONENT
    # --------------------------------------------------------

    component_id: int

    part_id: Optional[str] = None

    part_name: Optional[str] = None

    # --------------------------------------------------------
    # VEHICLE
    # --------------------------------------------------------

    vehicle_id: Optional[int] = None

    vehicle_code: Optional[str] = None

    vehicle_type: Optional[str] = None

    # --------------------------------------------------------
    # WAREHOUSE
    # --------------------------------------------------------

    warehouse: str

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    quantity_ordered: float

    quantity_received: float

    remaining_quantity: float

    # --------------------------------------------------------
    # COST
    # --------------------------------------------------------

    unit_cost: float

    order_value: float

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    order_status: Optional[str] = None

    tracking_stage: Optional[str] = None

    current_location: Optional[str] = None

    tracking_notes: Optional[str] = None

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    expected_delivery_date: Optional[date] = None

    actual_delivery_date: Optional[date] = None

    required_date: Optional[date] = None

    urgency: Optional[str] = None

    days_until_expected_arrival: Optional[int] = None

    is_delayed: bool = False

    # --------------------------------------------------------
    # TRACKING TIMESTAMPS
    # --------------------------------------------------------

    last_tracking_update: Optional[datetime] = None

    dispatched_at: Optional[datetime] = None

    arrived_at_warehouse_at: Optional[datetime] = None

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    source_type: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# PURCHASE ORDER STATUS HISTORY RESPONSE
# ============================================================

class PurchaseOrderStatusHistoryResponse(BaseModel):

    id: int

    purchase_order_id: int

    from_stage: Optional[str] = None

    to_stage: str

    location: Optional[str] = None

    notes: Optional[str] = None

    changed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )