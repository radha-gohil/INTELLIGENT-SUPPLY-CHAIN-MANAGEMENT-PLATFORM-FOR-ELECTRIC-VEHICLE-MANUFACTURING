from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Supplier,
    SupplierPerformance
)

from backend.app.schemas.supplier_performance import (
    SupplierPerformanceResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/supplier-performance",
    tags=["Supplier Performance"]
)


# ============================================================
# DATABASE
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# GET ALL PERFORMANCE RECORDS
# ============================================================

@router.get(
    "",
    response_model=list[SupplierPerformanceResponse]
)
def get_all_performance(
    db: Session = Depends(get_db)
):

    records = (

        db.query(
            SupplierPerformance
        )

        .order_by(
            SupplierPerformance
            .performance_date
            .desc()
        )

        .all()
    )

    return records


# ============================================================
# GET PERFORMANCE BY SUPPLIER
# ============================================================

@router.get(
    "/supplier/{supplier_id}",
    response_model=list[SupplierPerformanceResponse]
)
def get_supplier_performance(
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


    records = (

        db.query(
            SupplierPerformance
        )

        .filter(
            SupplierPerformance.supplier_id
            == supplier_id
        )

        .order_by(
            SupplierPerformance
            .performance_date
            .desc()
        )

        .all()
    )

    return records


# ============================================================
# GET PERFORMANCE BY SUPPLIER + COMPONENT
# ============================================================

@router.get(
    "/supplier/{supplier_id}/component/{component_id}",
    response_model=list[SupplierPerformanceResponse]
)
def get_supplier_component_performance(
    supplier_id: int,
    component_id: int,
    db: Session = Depends(get_db)
):

    records = (

        db.query(
            SupplierPerformance
        )

        .filter(
            SupplierPerformance.supplier_id
            == supplier_id,

            SupplierPerformance.component_id
            == component_id
        )

        .order_by(
            SupplierPerformance
            .performance_date
            .desc()
        )

        .all()
    )

    return records