from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
)

from backend.app.schemas.supplier_metrics import (
    SupplierMetricsResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/supplier-metrics",

    tags=["Supplier Metrics"]
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
# GET ONE SUPPLIER METRICS
# ============================================================

@router.get(
    "/supplier/{supplier_id}",
    response_model=SupplierMetricsResponse
)
def get_supplier_metrics(

    supplier_id: int,

    db: Session = Depends(get_db)

):

    try:

        result = (

            SupplierPerformanceService
            .calculate_supplier_performance(

                db,

                supplier_id

            )
        )

        return result

    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e)

        )


# ============================================================
# GET ALL SUPPLIER METRICS
# ============================================================

@router.get(
    "",
    response_model=list[SupplierMetricsResponse]
)
def get_all_supplier_metrics(

    db: Session = Depends(get_db)

):

    results = (

        SupplierPerformanceService
        .calculate_all_suppliers(

            db

        )
    )

    return results