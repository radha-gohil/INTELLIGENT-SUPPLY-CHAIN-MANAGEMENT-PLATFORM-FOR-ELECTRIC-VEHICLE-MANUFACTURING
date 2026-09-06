from pydantic import BaseModel
from datetime import date


class SupplierPerformanceResponse(BaseModel):

    id: int

    supplier_id: int

    component_id: int

    performance_date: date

    total_orders: int

    on_time_orders: int

    late_orders: int

    ordered_quantity: int

    received_quantity: int

    defective_quantity: int

    average_delay_days: float

    class Config:
        from_attributes = True