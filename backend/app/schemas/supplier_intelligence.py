from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SupplierIntelligenceResponse(BaseModel):

    # ========================================================
    # SUPPLIER MASTER
    # ========================================================

    supplier_id: int

    supplier_code: str

    supplier_name: str

    supplier_location: Optional[str] = None

    supplier_status: str

    component_category: Optional[str] = None


    # ========================================================
    # MASTER QUALITY / RELIABILITY
    # ========================================================

    # Normalized 0 - 5
    quality_rating: Optional[float] = None

    # Normalized 0 - 100
    baseline_reliability_score: Optional[float] = None


    # ========================================================
    # OPERATIONAL PERFORMANCE
    # ========================================================

    performance_data_available: bool

    on_time_delivery_rate: float

    fill_rate: float

    quality_score: float

    quality_source: str

    operational_reliability_score: float

    reliability_source: str


    # ========================================================
    # COMPONENT
    # ========================================================

    component_id: int


    # ========================================================
    # COMPONENT-SPECIFIC COMMERCIAL TERMS
    # ========================================================

    supplier_part_code: Optional[str] = None

    unit_price: Optional[float] = None

    minimum_order_quantity: int

    standard_lead_time_days: Optional[int] = None

    maximum_capacity: Optional[int] = None

    is_approved: bool


    # ========================================================
    # SUPPLIER AVAILABILITY
    # ========================================================

    availability_data_available: bool

    available_quantity: Optional[int] = None

    committed_quantity: Optional[int] = None

    available_to_promise: Optional[int] = None

    expected_replenishment_quantity: Optional[int] = None

    expected_replenishment_date: Optional[datetime] = None

    last_updated: Optional[datetime] = None