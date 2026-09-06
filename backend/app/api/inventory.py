from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from backend.app.database.connection import (
    SessionLocal
)

from backend.app.models import (
    Inventory,
    InventoryTransaction,
    Vehicle
)

from backend.app.schemas.inventory import (
    InventoryResponse,
    ReceiptRequest,
    IssueRequest,
    AdjustmentRequest,
    TransferRequest,
    TransactionResponse
)

from backend.app.schemas.vehicle import (
    VehicleResponse
)

from backend.app.schemas.vehicle_inventory import (
    VehicleInventoryAnalysisResponse,
    VehicleRequirementAnalysisResponse
)

from backend.app.schemas.purchase_order_tracking import (
    PurchaseOrderCreateRequest,
    PurchaseOrderTrackingUpdateRequest,
    PurchaseOrderReceiveRequest,
    PurchaseOrderTrackingResponse
)

from backend.app.service.stock_movement_service import (
    StockMovementService
)

from backend.app.service.inventory_analysis_service import (
    InventoryAnalysisService
)

from backend.app.service.purchase_order_service import (
    PurchaseOrderService
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# GET VEHICLES
# ============================================================

@router.get(
    "/vehicles",
    response_model=list[VehicleResponse]
)
def get_inventory_vehicles(
    db: Session = Depends(get_db)
):

    vehicles = (
        db.query(Vehicle)
        .filter(
            Vehicle.is_active == True
        )
        .order_by(
            Vehicle.id
        )
        .all()
    )

    return vehicles


# ============================================================
# VEHICLE BOM + CURRENT INVENTORY
# ============================================================

@router.get(
    "/vehicle/{vehicle_id}/components",
    response_model=VehicleInventoryAnalysisResponse
)
def get_vehicle_inventory_components(
    vehicle_id: int,
    db: Session = Depends(get_db)
):

    try:

        return (
            InventoryAnalysisService
            .get_vehicle_inventory(
                db=db,
                vehicle_id=vehicle_id
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


# ============================================================
# VEHICLE REQUIREMENT ANALYSIS
# ============================================================

@router.get(
    "/vehicle/{vehicle_id}/requirements",
    response_model=VehicleRequirementAnalysisResponse
)
def get_vehicle_requirement_analysis(

    vehicle_id: int,

    planned_quantity: int = Query(
        ...,
        gt=0
    ),

    required_date: date = Query(
        ...
    ),

    db: Session = Depends(get_db)

):

    try:

        return (
            InventoryAnalysisService
            .analyze_vehicle_requirements(

                db=db,

                vehicle_id=vehicle_id,

                planned_quantity=(
                    planned_quantity
                ),

                required_date=(
                    required_date
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# GET ALL INVENTORY
# ============================================================

@router.get(
    "",
    response_model=list[InventoryResponse]
)
def get_inventory(
    db: Session = Depends(get_db)
):

    return (
        db.query(Inventory)
        .order_by(
            Inventory.component_id,
            Inventory.warehouse
        )
        .all()
    )


# ============================================================
# GET INVENTORY BY COMPONENT
# ============================================================

@router.get(
    "/component/{component_id}",
    response_model=list[InventoryResponse]
)
def get_inventory_by_component(
    component_id: int,
    db: Session = Depends(get_db)
):

    records = (
        db.query(Inventory)
        .filter(
            Inventory.component_id
            == component_id
        )
        .order_by(
            Inventory.warehouse
        )
        .all()
    )


    if not records:

        raise HTTPException(
            status_code=404,
            detail=(
                "Inventory records not found "
                "for this component."
            )
        )


    return records


# ============================================================
# GET INVENTORY BY WAREHOUSE
# ============================================================

@router.get(
    "/warehouse/{warehouse}",
    response_model=list[InventoryResponse]
)
def get_inventory_by_warehouse(
    warehouse: str,
    db: Session = Depends(get_db)
):

    records = (
        db.query(Inventory)
        .filter(
            Inventory.warehouse
            == warehouse
        )
        .order_by(
            Inventory.component_id
        )
        .all()
    )


    if not records:

        raise HTTPException(
            status_code=404,
            detail=(
                "Inventory records not found "
                "for this warehouse."
            )
        )


    return records


# ============================================================
# GET INVENTORY TRANSACTIONS
# ============================================================

@router.get(
    "/transactions/all",
    response_model=list[TransactionResponse]
)
def get_inventory_transactions(
    db: Session = Depends(get_db)
):

    return (
        db.query(
            InventoryTransaction
        )
        .order_by(
            InventoryTransaction
            .transaction_date
            .desc()
        )
        .all()
    )


# ============================================================
# ============================================================
#
# PURCHASE ORDER ROUTES
#
# IMPORTANT:
# These routes must remain ABOVE /{inventory_id}.
#
# ============================================================
# ============================================================


# ============================================================
# GET PURCHASE ORDERS
# ============================================================

@router.get(
    "/orders",
    response_model=list[
        PurchaseOrderTrackingResponse
    ]
)
def get_purchase_orders(

    include_historical: bool = False,

    db: Session = Depends(get_db)

):

    return (
        PurchaseOrderService
        .get_orders(

            db=db,

            include_historical=(
                include_historical
            )
        )
    )


# ============================================================
# CREATE PURCHASE ORDER
# ============================================================

@router.post(
    "/orders",
    response_model=PurchaseOrderTrackingResponse
)
def create_purchase_order(

    request: PurchaseOrderCreateRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            PurchaseOrderService
            .create_order(

                db=db,

                supplier_id=(
                    request.supplier_id
                ),

                component_id=(
                    request.component_id
                ),

                warehouse=(
                    request.warehouse
                ),

                quantity_ordered=(
                    request.quantity_ordered
                ),

                vehicle_id=(
                    request.vehicle_id
                ),

                required_date=(
                    request.required_date
                ),

                urgency=(
                    request.urgency
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# GET ONE PURCHASE ORDER
# ============================================================

@router.get(
    "/orders/{purchase_order_id}",
    response_model=PurchaseOrderTrackingResponse
)
def get_purchase_order(

    purchase_order_id: int,

    db: Session = Depends(get_db)

):

    try:

        return (
            PurchaseOrderService
            .get_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


# ============================================================
# UPDATE PURCHASE ORDER TRACKING
# ============================================================

@router.patch(
    "/orders/{purchase_order_id}/tracking",
    response_model=PurchaseOrderTrackingResponse
)
def update_purchase_order_tracking(

    purchase_order_id: int,

    request: PurchaseOrderTrackingUpdateRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            PurchaseOrderService
            .update_tracking(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                ),

                tracking_stage=(
                    request.tracking_stage
                ),

                current_location=(
                    request.current_location
                ),

                tracking_notes=(
                    request.tracking_notes
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# RECEIVE PURCHASE ORDER
# ============================================================

@router.post(
    "/orders/{purchase_order_id}/receive",
    response_model=PurchaseOrderTrackingResponse
)
def receive_purchase_order(

    purchase_order_id: int,

    request: PurchaseOrderReceiveRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            PurchaseOrderService
            .receive_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                ),

                quantity_received=(
                    request.quantity_received
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# ============================================================
#
# STOCK MOVEMENT OPERATIONS
#
# ============================================================
# ============================================================


# ============================================================
# RECEIVE STOCK
# ============================================================

@router.post(
    "/receipt",
    response_model=InventoryResponse
)
def receive_stock(

    request: ReceiptRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            StockMovementService
            .receive_stock(

                db=db,

                component_id=(
                    request.component_id
                ),

                warehouse=(
                    request.warehouse
                ),

                quantity=(
                    request.quantity
                ),

                reference_id=(
                    request.reference_id
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# ISSUE STOCK
# ============================================================

@router.post(
    "/issue",
    response_model=InventoryResponse
)
def issue_stock(

    request: IssueRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            StockMovementService
            .issue_stock(

                db=db,

                component_id=(
                    request.component_id
                ),

                warehouse=(
                    request.warehouse
                ),

                quantity=(
                    request.quantity
                ),

                reference_id=(
                    request.reference_id
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# ADJUST STOCK
# ============================================================

@router.post(
    "/adjustment",
    response_model=InventoryResponse
)
def adjust_stock(

    request: AdjustmentRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            StockMovementService
            .adjust_stock(

                db=db,

                component_id=(
                    request.component_id
                ),

                warehouse=(
                    request.warehouse
                ),

                quantity=(
                    request.quantity
                ),

                reference_id=(
                    request.reference_id
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# TRANSFER STOCK
# ============================================================

@router.post(
    "/transfer"
)
def transfer_stock(

    request: TransferRequest,

    db: Session = Depends(get_db)

):

    try:

        return (
            StockMovementService
            .transfer_stock(

                db=db,

                component_id=(
                    request.component_id
                ),

                source_warehouse=(
                    request.source_warehouse
                ),

                destination_warehouse=(
                    request.destination_warehouse
                ),

                quantity=(
                    request.quantity
                ),

                reference_id=(
                    request.reference_id
                )
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


# ============================================================
# GET SINGLE INVENTORY RECORD
# ============================================================
#
# IMPORTANT:
# Keep this dynamic route at the END.
#
# Otherwise strings such as:
#
# /inventory/orders
#
# may be interpreted as:
#
# inventory_id = "orders"
#
# ============================================================

@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def get_inventory_record(

    inventory_id: int,

    db: Session = Depends(get_db)

):

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.id
            == inventory_id
        )
        .first()
    )


    if inventory is None:

        raise HTTPException(
            status_code=404,
            detail="Inventory record not found."
        )


    return inventory