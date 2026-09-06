from typing import Optional

from pydantic import BaseModel


# ============================================================
# SUPPLIER RECOMMENDATION
# ============================================================

class SupplierRecommendation(BaseModel):

    supplier_id: int

    supplier_code: str

    supplier_name: str

    available_to_promise: int

    unit_price: Optional[float] = None

    standard_lead_time_days: Optional[int] = None

    maximum_capacity: Optional[int] = None

    reliability_score: float

    risk_level: str

    risk_confidence: float

    recommendation_score: float

    recommendation_reason: str


# ============================================================
# RESPONSE
# ============================================================

class SupplierRecommendationResponse(BaseModel):

    component_id: int

    required_quantity: int

    recommended_supplier: SupplierRecommendation

    alternatives: list[SupplierRecommendation]