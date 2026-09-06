from pydantic import BaseModel
from typing import Dict


class SupplierRiskResponse(BaseModel):

    supplier_id: int

    supplier_code: str

    supplier_name: str

    risk_level: str

    confidence: float

    risk_probabilities: Dict[str, float]