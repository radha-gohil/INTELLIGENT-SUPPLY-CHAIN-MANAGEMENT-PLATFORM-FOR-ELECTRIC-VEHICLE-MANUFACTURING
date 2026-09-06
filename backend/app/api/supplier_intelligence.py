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

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
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
    # APPROVED + ACTIVE SUPPLIER MAPPINGS
    # ========================================================
    #
    # Important:
    #
    # Procurement intelligence should only consider:
    #
    # 1. Approved supplier-component mappings
    # 2. Active suppliers
    #
    # ========================================================

    supplier_records = (

        db.query(
            SupplierComponent,
            Supplier
        )

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

        .all()

    )


    results = []


    # ========================================================
    # BUILD SUPPLIER INTELLIGENCE
    # ========================================================

    for (
        supplier_component,
        supplier
    ) in supplier_records:

        # ====================================================
        # SUPPLIER PERFORMANCE
        # ====================================================

        performance = (

            SupplierPerformanceService
            .calculate_supplier_performance(

                db,

                supplier.id

            )

        )


        # ====================================================
        # NORMALIZE MASTER QUALITY RATING
        # ====================================================
        #
        # supplier_master.csv should normally contain:
        #
        # 4.5 -> 4.5 / 5
        #
        # But older imported data may contain:
        #
        # 90 -> 90 / 100
        #
        # Convert both to 0 - 5.
        # ====================================================

        quality_score_from_master = (

            SupplierPerformanceService
            .quality_rating_to_score(
                supplier.quality_rating
            )

        )


        if quality_score_from_master is None:

            normalized_quality_rating = None

        else:

            normalized_quality_rating = round(

                quality_score_from_master
                /
                20,

                2

            )


        # ====================================================
        # SUPPLIER AVAILABILITY
        # ====================================================

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
        # NO AVAILABILITY RECORD
        # ====================================================

        if availability is None:

            availability_data_available = False

            available_quantity = None

            committed_quantity = None

            available_to_promise = None

            expected_replenishment_quantity = None

            expected_replenishment_date = None

            last_updated = None


        # ====================================================
        # AVAILABILITY RECORD AVAILABLE
        # ====================================================

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


            # ------------------------------------------------
            # Master quality / reliability
            # ------------------------------------------------

            "quality_rating":
                normalized_quality_rating,

            "baseline_reliability_score":
                performance[
                    "baseline_reliability_score"
                ],


            # ------------------------------------------------
            # Operational performance
            # ------------------------------------------------

            "performance_data_available":
                performance[
                    "performance_data_available"
                ],

            "on_time_delivery_rate":
                performance[
                    "on_time_delivery_rate"
                ],

            "fill_rate":
                performance[
                    "fill_rate"
                ],

            "quality_score":
                performance[
                    "quality_score"
                ],

            "quality_source":
                performance[
                    "quality_source"
                ],

            "operational_reliability_score":
                performance[
                    "reliability_score"
                ],

            "reliability_source":
                performance[
                    "reliability_source"
                ],


            # ------------------------------------------------
            # Component
            # ------------------------------------------------

            "component_id":
                component_id,


            # ------------------------------------------------
            # Component-specific supplier terms
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
    # ========================================================
    #
    # This is NOT procurement ranking.
    #
    # It only makes Supplier Intelligence easier to inspect.
    #
    # Priority:
    #
    # availability data
    #      ↓
    # ATP
    #      ↓
    # operational reliability
    #      ↓
    # price
    #
    # Final procurement ranking will still happen inside
    # ProcurementService.
    # ========================================================

    results.sort(

        key=lambda item: (

            not item[
                "availability_data_available"
            ],

            -(
                item[
                    "available_to_promise"
                ]
                or 0
            ),

            -(
                item[
                    "operational_reliability_score"
                ]
                or 0
            ),

            (
                item[
                    "unit_price"
                ]

                if item[
                    "unit_price"
                ]
                is not None

                else float(
                    "inf"
                )
            )

        )

    )


    return results