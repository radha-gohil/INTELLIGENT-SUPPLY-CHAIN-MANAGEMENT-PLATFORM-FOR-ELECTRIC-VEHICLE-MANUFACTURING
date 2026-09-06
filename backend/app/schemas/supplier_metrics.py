from typing import Optional

from pydantic import BaseModel


class SupplierMetricsResponse(BaseModel):

    supplier_id: int
    supplier_code: str
    supplier_name: str

    # ========================================================
    # DATA SOURCE INFORMATION
    # ========================================================

    performance_data_available: bool

    # ========================================================
    # HISTORICAL PROCUREMENT METRICS
    # ========================================================

    total_orders: int
    on_time_orders: int
    late_orders: int

    ordered_quantity: int
    received_quantity: int
    defective_quantity: int

    on_time_delivery_rate: float
    fill_rate: float
    defect_rate: float

    average_delay_days: float

    # ========================================================
    # QUALITY
    # ========================================================

    quality_score: float

    quality_source: str

    baseline_quality_rating: Optional[float] = None

    # ========================================================
    # RELIABILITY
    # ========================================================

    baseline_reliability_score: Optional[float] = None

    reliability_score: float