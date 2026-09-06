from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


# ============================================================
# SUPPLIER OPTION
# ============================================================

class SupplierOptionResponse(BaseModel):

    # ========================================================
    # RANKING
    # ========================================================

    rank: int

    final_score: float


    # ========================================================
    # SUPPLIER
    # ========================================================

    supplier_id: int

    supplier_code: str

    supplier_name: str

    supplier_location: Optional[str] = None

    supplier_status: str


    # ========================================================
    # COMPONENT
    # ========================================================

    component_id: int

    part_id: str

    part_name: str

    criticality: str


    # ========================================================
    # COMMERCIAL TERMS
    # ========================================================

    supplier_part_code: Optional[str] = None

    unit_price: Optional[float] = None

    minimum_order_quantity: int

    standard_lead_time_days: Optional[int] = None

    maximum_capacity: Optional[int] = None

    is_approved: bool


    # ========================================================
    # AVAILABILITY
    # ========================================================

    availability_data_available: bool

    available_quantity: Optional[int] = None

    committed_quantity: Optional[int] = None

    available_to_promise: Optional[int] = None

    expected_replenishment_quantity: Optional[int] = None

    expected_replenishment_date: Optional[datetime] = None

    last_updated: Optional[datetime] = None


    # ========================================================
    # REQUIREMENT
    # ========================================================

    required_quantity: int

    recommended_order_quantity: int

    can_fulfill: bool

    capacity_can_fulfill: bool

    availability_confirmed: bool

    availability_percentage: float


    # ========================================================
    # HISTORICAL PERFORMANCE
    # ========================================================

    performance_data_available: bool

    total_orders: int

    on_time_delivery_rate: float

    fill_rate: float

    defect_rate: float

    average_delay_days: float

    quality_score: float

    quality_source: str

    reliability_score: float

    reliability_source: str


    # ========================================================
    # XGBOOST SUPPLIER RISK
    # ========================================================

    ai_risk_available: bool

    ai_risk_level: str

    ai_risk_confidence: Optional[float] = None

    ai_risk_probabilities: Dict[str, float]


    # ========================================================
    # DECISION SCORES - ALL 0 TO 100
    # ========================================================

    availability_score: float

    fulfillment_score: float

    reliability_decision_score: float

    quality_decision_score: float

    ai_risk_score: float

    price_score: float

    lead_time_score: float


# ============================================================
# PROCUREMENT RECOMMENDATION
# ============================================================

class ProcurementRecommendationResponse(BaseModel):

    component_id: int

    part_id: str

    part_name: str

    criticality: str

    required_quantity: int

    recommended_supplier_id: Optional[int] = None

    recommended_supplier: Optional[SupplierOptionResponse] = None

    supplier_options: list[SupplierOptionResponse]

    weights: Dict[str, float]