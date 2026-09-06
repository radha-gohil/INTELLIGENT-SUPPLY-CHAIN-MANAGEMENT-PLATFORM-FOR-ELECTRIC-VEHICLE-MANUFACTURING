from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from backend.app.database.connection import (
    SessionLocal
)

from backend.app.service.procurement_service import (
    ProcurementService
)

from backend.app.service.supplier_risk_service import (
    SupplierRiskService
)

from backend.app.service.procurement_decision_service import (
    ProcurementDecisionService
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/procurement",

    tags=[
        "Procurement Decision"
    ]

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
# INTELLIGENT SUPPLIER RECOMMENDATION
# ============================================================

@router.get(
    "/recommendation/{component_id}"
)
def get_supplier_recommendation(

    component_id: int,

    required_quantity: int,

    db: Session = Depends(get_db)

):

    # ========================================================
    # VALIDATE QUANTITY
    # ========================================================

    if required_quantity <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "Required quantity must be "
                "greater than zero."
            )

        )


    try:

        # ====================================================
        # GET SUPPLIER OPTIONS
        # ====================================================

        suppliers = (

            ProcurementService
            .get_supplier_options(

                db,

                component_id,

                required_quantity

            )

        )


        if not suppliers:

            raise HTTPException(

                status_code=404,

                detail=(
                    "No active suppliers found "
                    "for this component."
                )

            )


        # ====================================================
        # AI SUPPLIER RISK PREDICTION
        # ====================================================

        for supplier in suppliers:

            try:

                risk_result = (

                    SupplierRiskService
                    .predict_supplier_risk(

                        db,

                        supplier[
                            "supplier_id"
                        ]

                    )

                )


                # --------------------------------------------
                # Risk level
                # --------------------------------------------

                supplier[
                    "risk_level"
                ] = (

                    risk_result[
                        "risk_level"
                    ]

                )


                # --------------------------------------------
                # Risk probabilities
                # --------------------------------------------

                supplier[
                    "risk_probabilities"
                ] = (

                    risk_result[
                        "risk_probabilities"
                    ]

                )


                # --------------------------------------------
                # Risk confidence
                # --------------------------------------------

                supplier[
                    "risk_confidence"
                ] = (

                    risk_result[
                        "confidence"
                    ]

                )


            except ValueError:

                # --------------------------------------------
                # No performance data
                # --------------------------------------------

                supplier[
                    "risk_level"
                ] = "UNKNOWN"


                supplier[
                    "risk_probabilities"
                ] = {}


                supplier[
                    "risk_confidence"
                ] = 0.0


        # ====================================================
        # RANK SUPPLIERS
        # ====================================================

        ranked_suppliers = (

            ProcurementDecisionService
            .rank_suppliers(

                suppliers,

                required_quantity

            )

        )


        # ====================================================
        # RECOMMENDED SUPPLIER
        # ====================================================

        recommended_supplier = (

            ranked_suppliers[0]

            if ranked_suppliers

            else None

        )


        # ====================================================
        # DECISION WEIGHTS
        # ====================================================

        decision_weights = {

            "availability":
                ProcurementDecisionService
                .WEIGHTS[
                    "availability"
                ],

            "fulfillment":
                ProcurementDecisionService
                .WEIGHTS[
                    "fulfillment"
                ],

            "reliability":
                ProcurementDecisionService
                .WEIGHTS[
                    "reliability"
                ],

            "quality":
                ProcurementDecisionService
                .WEIGHTS[
                    "quality"
                ],

            "ai_risk":
                ProcurementDecisionService
                .WEIGHTS[
                    "ai_risk"
                ],

            "price":
                ProcurementDecisionService
                .WEIGHTS[
                    "price"
                ],

            "lead_time":
                ProcurementDecisionService
                .WEIGHTS[
                    "lead_time"
                ]

        }


        # ====================================================
        # RETURN COMPLETE PROCUREMENT DECISION
        # ====================================================

        return {

            "component_id":
                component_id,

            "required_quantity":
                required_quantity,

            "recommended_supplier":
                recommended_supplier,

            "supplier_options":
                ranked_suppliers,

            "decision_weights":
                decision_weights

        }


    # ========================================================
    # HTTP EXCEPTIONS
    # ========================================================

    except HTTPException:

        raise


    # ========================================================
    # VALIDATION / DATA ERRORS
    # ========================================================

    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e)

        )


    # ========================================================
    # MODEL FILE ERRORS
    # ========================================================

    except FileNotFoundError as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


    # ========================================================
    # UNEXPECTED ERRORS
    # ========================================================

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Supplier recommendation failed: "
                + str(e)
            )

        )