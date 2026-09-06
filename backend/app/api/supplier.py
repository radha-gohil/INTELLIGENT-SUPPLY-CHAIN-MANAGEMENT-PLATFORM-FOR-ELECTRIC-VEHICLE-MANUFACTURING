from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Supplier,
    SupplierComponent,
    SupplierAvailability,
    Component
)

from backend.app.schemas.supplier import (
    SupplierResponse,
    SupplierComponentResponse,
    SupplierAvailabilityResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
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
# GET ALL SUPPLIERS
# ============================================================

@router.get(
    "",
    response_model=list[SupplierResponse]
)
def get_suppliers(
    db: Session = Depends(get_db)
):

    suppliers = (

        db.query(Supplier)

        .order_by(
            Supplier.id
        )

        .all()

    )

    return suppliers


# ============================================================
# GET SUPPLIERS FOR COMPONENT
#
# IMPORTANT:
# Static routes must stay BEFORE /{supplier_id}
# ============================================================

@router.get(
    "/component/{component_id}",
    response_model=list[SupplierComponentResponse]
)
def get_suppliers_for_component(
    component_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check component
    # --------------------------------------------------------

    component = (

        db.query(Component)

        .filter(
            Component.id == component_id
        )

        .first()

    )

    if component is None:

        raise HTTPException(
            status_code=404,
            detail="Component not found."
        )


    # --------------------------------------------------------
    # Approved supplier-component mappings
    # --------------------------------------------------------

    supplier_components = (

        db.query(SupplierComponent)

        .join(
            Supplier,
            Supplier.id
            == SupplierComponent.supplier_id
        )

        .filter(

            SupplierComponent.component_id
            == component_id,

            SupplierComponent.is_approved
            == True,

            Supplier.is_active
            == True

        )

        .order_by(
            SupplierComponent.unit_price.asc()
        )

        .all()

    )

    return supplier_components


# ============================================================
# GET SUPPLIER AVAILABILITY FOR COMPONENT
#
# IMPORTANT:
# Static route before /{supplier_id}
# ============================================================

@router.get(
    "/availability/component/{component_id}",
    response_model=list[SupplierAvailabilityResponse]
)
def get_supplier_availability(
    component_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check component
    # --------------------------------------------------------

    component = (

        db.query(Component)

        .filter(
            Component.id == component_id
        )

        .first()

    )

    if component is None:

        raise HTTPException(
            status_code=404,
            detail="Component not found."
        )


    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    availability = (

        db.query(SupplierAvailability)

        .join(
            Supplier,
            Supplier.id
            == SupplierAvailability.supplier_id
        )

        .filter(

            SupplierAvailability.component_id
            == component_id,

            Supplier.is_active
            == True

        )

        .order_by(
            SupplierAvailability.available_to_promise.desc()
        )

        .all()

    )

    return availability


# ============================================================
# GET COMPONENTS SUPPLIED BY ONE SUPPLIER
#
# This endpoint is required by the Suppliers frontend page.
# ============================================================

@router.get(
    "/{supplier_id}/components",
    response_model=list[SupplierComponentResponse]
)
def get_supplier_components(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check supplier
    # --------------------------------------------------------

    supplier = (

        db.query(Supplier)

        .filter(
            Supplier.id == supplier_id
        )

        .first()

    )

    if supplier is None:

        raise HTTPException(
            status_code=404,
            detail="Supplier not found."
        )


    # --------------------------------------------------------
    # Supplier-component mappings
    # --------------------------------------------------------

    supplier_components = (

        db.query(SupplierComponent)

        .filter(
            SupplierComponent.supplier_id
            == supplier_id
        )

        .order_by(
            SupplierComponent.component_id
        )

        .all()

    )

    return supplier_components


# ============================================================
# GET SUPPLIER BY ID
#
# KEEP THIS ROUTE LAST.
#
# Otherwise paths such as:
# /component/1
# /availability/component/1
#
# can be interpreted as supplier_id.
# ============================================================

@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    supplier = (

        db.query(Supplier)

        .filter(
            Supplier.id == supplier_id
        )

        .first()

    )

    if supplier is None:

        raise HTTPException(
            status_code=404,
            detail="Supplier not found."
        )

    return supplier