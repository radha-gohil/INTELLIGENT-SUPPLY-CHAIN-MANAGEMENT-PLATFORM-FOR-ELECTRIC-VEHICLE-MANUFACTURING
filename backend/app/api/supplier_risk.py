from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.service.supplier_risk_service import (
    SupplierRiskService
)

from backend.app.schemas.supplier_risk import (
    SupplierRiskResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/supplier-risk",

    tags=["Supplier Risk"]

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
# PREDICT SUPPLIER RISK
# ============================================================

@router.get(

    "/supplier/{supplier_id}",

    response_model=SupplierRiskResponse

)
def predict_supplier_risk(

    supplier_id: int,

    db: Session = Depends(get_db)

):

    try:

        result = (

            SupplierRiskService
            .predict_supplier_risk(

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


    except FileNotFoundError as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Supplier risk prediction failed: "
                + str(e)
            )

        )