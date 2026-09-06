from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from backend.app.database.connection import (
    SessionLocal
)

from backend.app.models import (
    Component,
    Supplier,
    SupplierAvailability,
    SupplierComponent
)

from backend.app.schemas.supplier_intelligence import (
    SupplierIntelligenceResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/supplier-intelligence",

    tags=[
        "Supplier Intelligence"
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
# GET SUPPLIER INTELLIGENCE FOR COMPONENT
# ============================================================

@router.get(
    "/component/{component_id}",
    response_model=list[
        SupplierIntelligenceResponse
    ]
)
def get_supplier_intelligence(
    component_id: int,
    db: Session = Depends(
        get_db
    )
):

    # ========================================================
    # COMPONENT VALIDATION
    # ========================================================

    component = (

        db.query(
            Component
        )

        .filter(
            Component.id
            == component_id
        )

        .first()

    )


    if component is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Component not found."
            )

        )


    # ========================================================
    # SUPPLIER-COMPONENT MAPPINGS
    # ========================================================

    supplier_components = (

        db.query(
            SupplierComponent
        )

        .filter(
            SupplierComponent.component_id
            == component_id
        )

        .all()

    )


    results = []


    # ========================================================
    # BUILD SUPPLIER INTELLIGENCE
    # ========================================================

    for supplier_component in supplier_components:

        # ----------------------------------------------------
        # Supplier
        # ----------------------------------------------------

        supplier = (

            db.query(
                Supplier
            )

            .filter(
                Supplier.id
                == supplier_component.supplier_id
            )

            .first()

        )


        if supplier is None:

            continue


        # ----------------------------------------------------
        # Ignore inactive suppliers from procurement
        # intelligence.
        # ----------------------------------------------------

        if not supplier.is_active:

            continue


        # ----------------------------------------------------
        # Dynamic availability
        # ----------------------------------------------------

        availability = (

            db.query(
                SupplierAvailability
            )

            .filter(

                SupplierAvailability.supplier_id
                == supplier.id,

                SupplierAvailability.component_id
                == component_id

            )

            .first()

        )


        # ====================================================
        # AVAILABILITY STATE
        # ====================================================

        if availability is None:

            availability_data_available = False

            available_quantity = None

            committed_quantity = None

            available_to_promise = None

            expected_replenishment_quantity = None

            expected_replenishment_date = None

            last_updated = None


        else:

            availability_data_available = True

            available_quantity = (
                availability
                .available_quantity
            )

            committed_quantity = (
                availability
                .committed_quantity
            )

            available_to_promise = (
                availability
                .available_to_promise
            )

            expected_replenishment_quantity = (
                availability
                .expected_replenishment_quantity
            )

            expected_replenishment_date = (
                availability
                .expected_replenishment_date
            )

            last_updated = (
                availability
                .last_updated
            )


        # ====================================================
        # RESULT
        # ====================================================

        result = {

            # ------------------------------------------------
            # Supplier master
            # ------------------------------------------------

            "supplier_id":
                supplier.id,

            "supplier_code":
                supplier.supplier_code,

            "supplier_name":
                supplier.supplier_name,

            "supplier_location":
                supplier.location,

            "supplier_status":
                supplier.status,

            "component_category":
                supplier.component_category,

            "quality_rating":
                supplier.quality_rating,

            "baseline_reliability_score":
                supplier.baseline_reliability_score,


            # ------------------------------------------------
            # Component
            # ------------------------------------------------

            "component_id":
                component_id,


            # ------------------------------------------------
            # Component-specific commercial information
            # ------------------------------------------------

            "supplier_part_code":
                supplier_component
                .supplier_part_code,

            "unit_price":
                supplier_component
                .unit_price,

            "minimum_order_quantity":
                supplier_component
                .minimum_order_quantity,

            "standard_lead_time_days":
                supplier_component
                .standard_lead_time_days,

            "maximum_capacity":
                supplier_component
                .maximum_capacity,

            "is_approved":
                supplier_component
                .is_approved,


            # ------------------------------------------------
            # Availability
            # ------------------------------------------------

            "availability_data_available":
                availability_data_available,

            "available_quantity":
                available_quantity,

            "committed_quantity":
                committed_quantity,

            "available_to_promise":
                available_to_promise,

            "expected_replenishment_quantity":
                expected_replenishment_quantity,

            "expected_replenishment_date":
                expected_replenishment_date,

            "last_updated":
                last_updated

        }


        results.append(
            result
        )


    # ========================================================
    # SORTING
    #
    # Approved first.
    # Suppliers with actual ATP data next.
    # Higher ATP first when ATP exists.
    # ========================================================

    results.sort(

        key=lambda item: (

            not item[
                "is_approved"
            ],

            not item[
                "availability_data_available"
            ],

            -(
                item[
                    "available_to_promise"
                ]
                or 0
            )

        )

    )


    return results