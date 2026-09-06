from datetime import date
from typing import Optional

from pydantic import BaseModel


# ============================================================
# VEHICLE BOM INVENTORY COMPONENT
# ============================================================

class VehicleBOMInventoryComponentResponse(BaseModel):

    component_id: int

    part_id: str

    part_name: str

    category: str

    sub_category: Optional[str] = None

    criticality: str

    quantity_per_vehicle: float

    unit: str

    warehouse_count: int

    current_stock: float

    reserved_stock: float

    available_stock: float

    safety_stock: float

    reorder_level: float

    stock_ratio: Optional[float] = None

    inventory_status: str

    warehouses_requiring_attention: int


# ============================================================
# VEHICLE INVENTORY RESPONSE
# ============================================================

class VehicleInventoryAnalysisResponse(BaseModel):

    vehicle_id: int

    vehicle_code: str

    vehicle_type: str

    vehicle_category: str

    use_case: Optional[str] = None

    component_count: int

    components: list[
        VehicleBOMInventoryComponentResponse
    ]


# ============================================================
# VEHICLE REQUIREMENT COMPONENT
# ============================================================

class VehicleRequirementComponentResponse(BaseModel):

    component_id: int

    part_id: str

    part_name: str

    category: str

    sub_category: Optional[str] = None

    criticality: str

    unit: str

    quantity_per_vehicle: float

    planned_vehicle_quantity: int

    required_quantity: float

    available_stock: float

    safety_stock: float

    incoming_quantity: float

    incoming_expected_date: Optional[date] = None

    production_shortage: float

    recommended_procurement_quantity: float

    best_supplier_lead_time_days: Optional[int] = None

    estimated_arrival_date: Optional[date] = None

    days_remaining: int

    lead_time_buffer_days: Optional[int] = None

    inventory_status: str

    urgency: str

    urgency_reason: str

    procurement_required: bool


# ============================================================
# VEHICLE REQUIREMENT ANALYSIS
# ============================================================

class VehicleRequirementAnalysisResponse(BaseModel):

    vehicle_id: int

    vehicle_code: str

    vehicle_type: str

    vehicle_category: str

    use_case: Optional[str] = None

    planned_vehicle_quantity: int

    required_date: date

    component_count: int

    sufficient_components: int

    shortage_components: int

    procurement_components: int

    urgent_components: int

    high_priority_components: int

    components: list[
        VehicleRequirementComponentResponse
    ]