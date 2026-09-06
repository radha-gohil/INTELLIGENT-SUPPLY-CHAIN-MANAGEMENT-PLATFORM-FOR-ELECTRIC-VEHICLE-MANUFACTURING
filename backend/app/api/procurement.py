from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.service.procurement_service import (
    ProcurementService
)

from backend.app.schemas.procurement import (
    SupplierOptionResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/procurement",

    tags=["Procurement"]

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
# GET SUPPLIER OPTIONS
# ============================================================

@router.get(

    "/component/{component_id}",

    response_model=list[SupplierOptionResponse]

)
def get_supplier_options(

    component_id: int,

    required_quantity: int,

    db: Session = Depends(get_db)

):

    if required_quantity <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "Required quantity must be "
                "greater than zero."
            )

        )

    try:

        results = (

            ProcurementService
            .get_supplier_options(

                db,

                component_id,

                required_quantity

            )

        )

        return results

    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e)

        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Failed to retrieve supplier "
                "options: "
                + str(e)
            )

        )