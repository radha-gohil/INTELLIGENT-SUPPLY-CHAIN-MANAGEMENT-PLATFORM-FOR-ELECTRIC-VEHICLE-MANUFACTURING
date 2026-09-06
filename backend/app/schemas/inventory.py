from datetime import datetime

from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


# ============================================================
# INVENTORY RESPONSE
# ============================================================

class InventoryResponse(BaseModel):

    id: int

    component_id: int

    warehouse: str

    current_stock: float

    reserved_stock: float

    available_stock: float

    safety_stock: float

    reorder_level: float

    inventory_status: str

    class Config:
        from_attributes = True


# ============================================================
# RECEIPT REQUEST
# ============================================================

class ReceiptRequest(BaseModel):

    component_id: int = Field(
        gt=0
    )

    warehouse: str

    quantity: float = Field(
        gt=0
    )

    reference_id: Optional[str] = None


# ============================================================
# ISSUE REQUEST
# ============================================================

class IssueRequest(BaseModel):

    component_id: int = Field(
        gt=0
    )

    warehouse: str

    quantity: float = Field(
        gt=0
    )

    reference_id: Optional[str] = None


# ============================================================
# ADJUSTMENT REQUEST
# ============================================================

class AdjustmentRequest(BaseModel):

    component_id: int = Field(
        gt=0
    )

    warehouse: str

    quantity: float

    reference_id: Optional[str] = None


# ============================================================
# TRANSFER REQUEST
# ============================================================

class TransferRequest(BaseModel):

    component_id: int = Field(
        gt=0
    )

    source_warehouse: str

    destination_warehouse: str

    quantity: float = Field(
        gt=0
    )

    reference_id: Optional[str] = None


# ============================================================
# TRANSACTION RESPONSE
# ============================================================

class TransactionResponse(BaseModel):

    transaction_id: str

    component_id: int

    warehouse: str

    transaction_type: str

    quantity: float

    reference_id: Optional[str] = None

    transaction_date: datetime

    class Config:
        from_attributes = True