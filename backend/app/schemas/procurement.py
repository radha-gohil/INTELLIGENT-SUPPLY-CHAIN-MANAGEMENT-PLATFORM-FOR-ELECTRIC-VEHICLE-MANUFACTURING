from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SupplierOptionResponse(BaseModel):

    supplier_id: int

    supplier_code: str

    supplier_name: str

    supplier_location: Optional[str] = None

    supplier_status: str

    component_id: int

    part_id: str

    part_name: str

    criticality: str

    supplier_part_code: Optional[str] = None

    unit_price: Optional[float] = None

    minimum_order_quantity: int

    standard_lead_time_days: Optional[int] = None

    maximum_capacity: Optional[int] = None

    is_approved: bool

    available_quantity: int

    committed_quantity: int

    available_to_promise: int

    expected_replenishment_quantity: int

    expected_replenishment_date: Optional[datetime] = None

    last_updated: Optional[datetime] = None

    required_quantity: int

    can_fulfill: bool

    availability_percentage: float

    total_orders: int

    on_time_delivery_rate: float

    fill_rate: float

    defect_rate: float

    average_delay_days: float

    reliability_score: float