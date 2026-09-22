from fastapi import APIRouter, HTTPException, Query

from backend.app.service.graph_retrieval_service import (
    GraphRetrievalService
)

from backend.app.service.graph_rag_service import (
    GraphRAGService
)

from backend.app.schemas.graph_rag import (
    ComponentContextResponse,
    GraphQueryRequest,
    GraphSummaryResponse,
    VehicleContextResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/graph-rag",
    tags=["Graph RAG"]
)


# ============================================================
# GRAPH SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=GraphSummaryResponse
)
def get_graph_summary():
    """
    Return the current Knowledge Graph summary.
    """

    try:
        return GraphRetrievalService.get_graph_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve graph summary: {exc}"
        )


# ============================================================
# VEHICLE
# ============================================================

@router.get("/vehicle/{vehicle_code}")
def get_vehicle(vehicle_code: str):
    """
    Retrieve one vehicle from Neo4j.
    """

    try:
        result = GraphRetrievalService.get_vehicle(
            vehicle_code.upper()
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Vehicle {vehicle_code} not found."
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve vehicle: {exc}"
        )


# ============================================================
# VEHICLE BOM
# ============================================================

@router.get(
    "/vehicle/{vehicle_code}/components"
)
def get_vehicle_components(vehicle_code: str):
    """
    Retrieve components required by a vehicle.
    """

    try:
        vehicle = GraphRetrievalService.get_vehicle(
            vehicle_code.upper()
        )

        if vehicle is None:
            raise HTTPException(
                status_code=404,
                detail=f"Vehicle {vehicle_code} not found."
            )

        components = (
            GraphRetrievalService.get_vehicle_components(
                vehicle_code.upper()
            )
        )

        return {
            "vehicle_code": vehicle_code.upper(),
            "component_count": len(components),
            "components": components
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve vehicle components: {exc}"
        )


# ============================================================
# COMPLETE VEHICLE CONTEXT
# ============================================================

@router.get(
    "/vehicle/{vehicle_code}/context",
    response_model=VehicleContextResponse
)
def get_vehicle_context(vehicle_code: str):
    """
    Retrieve complete supply-chain context for a vehicle.
    """

    try:
        result = GraphRetrievalService.get_vehicle_context(
            vehicle_code.upper()
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Vehicle {vehicle_code} not found."
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve vehicle context: {exc}"
        )


# ============================================================
# COMPONENT
# ============================================================

@router.get("/component/{part_id}")
def get_component(part_id: str):
    """
    Retrieve one component.
    """

    try:
        result = GraphRetrievalService.get_component(
            part_id.upper()
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Component {part_id} not found."
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve component: {exc}"
        )


# ============================================================
# COMPONENT SUPPLIERS
# ============================================================

@router.get(
    "/component/{part_id}/suppliers"
)
def get_component_suppliers(part_id: str):
    """
    Retrieve suppliers for a component.
    """

    try:
        component = GraphRetrievalService.get_component(
            part_id.upper()
        )

        if component is None:
            raise HTTPException(
                status_code=404,
                detail=f"Component {part_id} not found."
            )

        suppliers = (
            GraphRetrievalService.get_component_suppliers(
                part_id.upper()
            )
        )

        return {
            "part_id": part_id.upper(),
            "supplier_count": len(suppliers),
            "suppliers": suppliers
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve component suppliers: {exc}"
        )


# ============================================================
# COMPONENT INVENTORY
# ============================================================

@router.get(
    "/component/{part_id}/inventory"
)
def get_component_inventory(part_id: str):
    """
    Retrieve warehouse inventory for a component.
    """

    try:
        component = GraphRetrievalService.get_component(
            part_id.upper()
        )

        if component is None:
            raise HTTPException(
                status_code=404,
                detail=f"Component {part_id} not found."
            )

        inventory = (
            GraphRetrievalService.get_component_inventory(
                part_id.upper()
            )
        )

        return {
            "part_id": part_id.upper(),
            "warehouse_count": len(inventory),
            "inventory": inventory
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve inventory: {exc}"
        )


# ============================================================
# COMPONENT PURCHASE ORDERS
# ============================================================

@router.get(
    "/component/{part_id}/purchase-orders"
)
def get_component_purchase_orders(
    part_id: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    )
):
    """
    Retrieve recent purchase orders for a component.
    """

    try:
        component = GraphRetrievalService.get_component(
            part_id.upper()
        )

        if component is None:
            raise HTTPException(
                status_code=404,
                detail=f"Component {part_id} not found."
            )

        orders = (
            GraphRetrievalService
            .get_component_purchase_orders(
                part_id.upper(),
                limit
            )
        )

        return {
            "part_id": part_id.upper(),
            "purchase_order_count": len(orders),
            "purchase_orders": orders
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve purchase orders: {exc}"
        )


# ============================================================
# COMPLETE COMPONENT CONTEXT
# ============================================================

@router.get(
    "/component/{part_id}/context",
    response_model=ComponentContextResponse
)
def get_component_context(
    part_id: str,
    purchase_order_limit: int = Query(
        default=10,
        ge=1,
        le=100
    )
):
    """
    Retrieve complete Graph-RAG context for a component.
    """

    try:
        result = GraphRetrievalService.get_component_context(
            part_id.upper(),
            purchase_order_limit
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Component {part_id} not found."
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve component context: {exc}"
        )


# ============================================================
# SUPPLIER
# ============================================================

@router.get("/supplier/{supplier_code}")
def get_supplier(supplier_code: str):
    """
    Retrieve supplier information.
    """

    try:
        result = GraphRetrievalService.get_supplier(
            supplier_code.upper()
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier {supplier_code} not found."
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve supplier: {exc}"
        )


# ============================================================
# SUPPLIER COMPONENTS
# ============================================================

@router.get(
    "/supplier/{supplier_code}/components"
)
def get_supplier_components(supplier_code: str):
    """
    Retrieve components supplied by a supplier.
    """

    try:
        supplier = GraphRetrievalService.get_supplier(
            supplier_code.upper()
        )

        if supplier is None:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier {supplier_code} not found."
            )

        components = (
            GraphRetrievalService.get_supplier_components(
                supplier_code.upper()
            )
        )

        return {
            "supplier_code": supplier_code.upper(),
            "component_count": len(components),
            "components": components
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve supplier components: {exc}"
        )


# ============================================================
# SUPPLIER PURCHASE ORDERS
# ============================================================

@router.get(
    "/supplier/{supplier_code}/purchase-orders"
)
def get_supplier_purchase_orders(
    supplier_code: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    )
):
    """
    Retrieve recent purchase orders for a supplier.
    """

    try:
        supplier = GraphRetrievalService.get_supplier(
            supplier_code.upper()
        )

        if supplier is None:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier {supplier_code} not found."
            )

        orders = (
            GraphRetrievalService
            .get_supplier_purchase_orders(
                supplier_code.upper(),
                limit
            )
        )

        return {
            "supplier_code": supplier_code.upper(),
            "purchase_order_count": len(orders),
            "purchase_orders": orders
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve supplier "
                f"purchase orders: {exc}"
            )
        )


# ============================================================
# WAREHOUSE INVENTORY
# ============================================================

@router.get(
    "/warehouse/{warehouse_name}/inventory"
)
def get_warehouse_inventory(
    warehouse_name: str
):
    """
    Retrieve all component inventory for a warehouse.
    """

    try:
        inventory = (
            GraphRetrievalService.get_warehouse_inventory(
                warehouse_name
            )
        )

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail=f"Warehouse {warehouse_name} not found."
            )

        return {
            "warehouse": warehouse_name,
            "component_count": len(inventory),
            "inventory": inventory
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve warehouse inventory: {exc}"
        )


# ============================================================
# PURCHASE ORDER
# ============================================================

@router.get(
    "/purchase-order/{po_number}"
)
def get_purchase_order(po_number: str):
    """
    Retrieve one purchase order and connected graph entities.
    """

    try:
        result = (
            GraphRetrievalService.get_purchase_order(
                po_number
            )
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Purchase order {po_number} not found."
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve purchase order: {exc}"
        )


# ============================================================
# GRAPH-RAG NATURAL LANGUAGE QUESTION
# ============================================================

@router.post("/ask")
def ask_graph_rag(
    request: GraphQueryRequest
):
    """
    Ask a natural-language question about the EV supply chain.

    Processing flow:

        User Question
              |
              v
        GraphRAGService
              |
              v
        Entity Detection
              |
              v
        GraphRetrievalService
              |
              v
        Neo4j Knowledge Graph
              |
              v
        Relevant Graph Context
              |
              v
        Gemini
              |
              v
        Grounded Answer
    """

    try:
        service = GraphRAGService()

        result = service.ask(
            request.question
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Graph-RAG query failed: {exc}"
        )