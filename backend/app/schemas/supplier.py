from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ============================================================
# SUPPLIER RESPONSE
# ============================================================

class SupplierResponse(BaseModel):

    id: int

    supplier_code: str
    supplier_name: str

    location: Optional[str] = None
    component_category: Optional[str] = None

    master_lead_time_days: Optional[int] = None
    master_unit_cost: Optional[float] = None
    master_monthly_capacity: Optional[int] = None

    quality_rating: Optional[float] = None
    baseline_reliability_score: Optional[float] = None

    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    status: str
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================
# SUPPLIER COMPONENT RESPONSE
# ============================================================

class SupplierComponentResponse(BaseModel):

    id: int

    supplier_id: int
    component_id: int

    supplier_part_code: Optional[str] = None

    unit_price: Optional[float] = None

    minimum_order_quantity: int

    standard_lead_time_days: Optional[int] = None

    maximum_capacity: Optional[int] = None

    is_approved: bool

    class Config:
        from_attributes = True


# ============================================================
# SUPPLIER AVAILABILITY RESPONSE
# ============================================================

class SupplierAvailabilityResponse(BaseModel):

    id: int

    supplier_id: int
    component_id: int

    available_quantity: int
    committed_quantity: int
    available_to_promise: int

    expected_replenishment_quantity: int

    expected_replenishment_date: Optional[datetime] = None

    last_updated: datetime

    class Config:
        from_attributes = True