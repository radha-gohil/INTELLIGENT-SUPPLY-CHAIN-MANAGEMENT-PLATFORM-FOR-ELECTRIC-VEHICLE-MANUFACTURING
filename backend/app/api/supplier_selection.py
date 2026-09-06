from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.service.supplier_selection_service import (
    SupplierSelectionService
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/supplier-selection",

    tags=["Supplier Selection"]

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
# FIND AND RANK SUPPLIERS
# ============================================================

@router.get(
    "/component/{component_id}"
)
def select_suppliers(

    component_id: int,

    required_quantity: int,

    db: Session = Depends(get_db)

):

    try:

        result = (

            SupplierSelectionService
            .get_supplier_options(

                db,

                component_id,

                required_quantity

            )

        )

        return result


    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e)

        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Supplier selection failed: "
                + str(e)
            )

        )