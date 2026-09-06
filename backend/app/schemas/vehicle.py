from pydantic import BaseModel


# ============================================================
# VEHICLE RESPONSE
# ============================================================

class VehicleResponse(BaseModel):

    id: int

    vehicle_code: str

    vehicle_type: str

    vehicle_category: str

    use_case: str | None = None

    is_active: bool

    class Config:
        from_attributes = True