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
# GET SUPPLIER BY ID
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


# ============================================================
# GET SUPPLIER COMPONENT INFORMATION
# ============================================================

@router.get(
    "/component/{component_id}",
    response_model=list[SupplierComponentResponse]
)
def get_suppliers_for_component(
    component_id: int,
    db: Session = Depends(get_db)
):

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


    supplier_components = (

        db.query(SupplierComponent)

        .filter(
            SupplierComponent.component_id
            == component_id
        )

        .all()
    )

    return supplier_components


# ============================================================
# GET SUPPLIER AVAILABILITY
# ============================================================

@router.get(
    "/availability/component/{component_id}",
    response_model=list[SupplierAvailabilityResponse]
)
def get_supplier_availability(
    component_id: int,
    db: Session = Depends(get_db)
):

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


    availability = (

        db.query(SupplierAvailability)

        .filter(
            SupplierAvailability.component_id
            == component_id
        )

        .all()
    )

    return availability