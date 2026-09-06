from math import ceil

from sqlalchemy.orm import Session

from backend.app.models import (
    Component,
    Supplier,
    SupplierAvailability,
    SupplierComponent
)

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
)

from backend.app.service.supplier_risk_service import (
    SupplierRiskService
)


# ============================================================
# PROCUREMENT SERVICE
# ============================================================

class ProcurementService:

    # ========================================================
    # DECISION WEIGHTS
    # ========================================================

    WEIGHTS = {

        "availability": 0.15,

        "fulfillment": 0.20,

        "reliability": 0.25,

        "quality": 0.10,

        "ai_risk": 0.15,

        "price": 0.10,

        "lead_time": 0.05

    }


    # ========================================================
    # CLAMP SCORE
    # ========================================================

    @staticmethod
    def clamp_score(value):

        try:

            value = float(value)

        except (
            TypeError,
            ValueError
        ):

            return 0.0


        return max(
            0.0,
            min(
                100.0,
                value
            )
        )


    # ========================================================
    # XGBOOST RISK -> SAFE SUPPLIER SCORE
    # ========================================================

    @staticmethod
    def calculate_ai_risk_score(
        risk_result
    ):

        if not risk_result:

            return 50.0


        probabilities = (
            risk_result.get(
                "risk_probabilities"
            )
            or {}
        )


        # ----------------------------------------------------
        # Prefer the complete probability distribution.
        #
        # LOW    = safest
        # MEDIUM = moderate
        # HIGH   = risky
        # ----------------------------------------------------

        if probabilities:

            low_probability = float(
                probabilities.get(
                    "LOW",
                    0
                )
                or 0
            )

            medium_probability = float(
                probabilities.get(
                    "MEDIUM",
                    0
                )
                or 0
            )

            high_probability = float(
                probabilities.get(
                    "HIGH",
                    0
                )
                or 0
            )

            critical_probability = float(
                probabilities.get(
                    "CRITICAL",
                    0
                )
                or 0
            )


            score = (

                low_probability
                * 100

                +

                medium_probability
                * 50

                +

                high_probability
                * 10

                +

                critical_probability
                * 0

            )


            return (
                ProcurementService
                .clamp_score(
                    score
                )
            )


        # ----------------------------------------------------
        # Fallback if only risk label exists
        # ----------------------------------------------------

        risk_level = str(

            risk_result.get(
                "risk_level",
                "UNKNOWN"
            )

        ).upper()


        fallback_scores = {

            "LOW": 100.0,

            "MEDIUM": 50.0,

            "HIGH": 10.0,

            "CRITICAL": 0.0,

            "UNKNOWN": 50.0

        }


        return fallback_scores.get(
            risk_level,
            50.0
        )


    # ========================================================
    # NORMALIZE PRICE
    # ========================================================

    @staticmethod
    def calculate_price_score(
        price,
        minimum_price,
        maximum_price
    ):

        if price is None:

            return 0.0


        price = float(price)


        if (
            minimum_price is None
            or
            maximum_price is None
        ):

            return 0.0


        if maximum_price == minimum_price:

            return 100.0


        score = (

            (
                maximum_price
                -
                price
            )

            /
            (
                maximum_price
                -
                minimum_price
            )

        ) * 100


        return (
            ProcurementService
            .clamp_score(
                score
            )
        )


    # ========================================================
    # NORMALIZE LEAD TIME
    # ========================================================

    @staticmethod
    def calculate_lead_time_score(
        lead_time,
        minimum_lead_time,
        maximum_lead_time
    ):

        if lead_time is None:

            return 0.0


        lead_time = float(
            lead_time
        )


        if (
            minimum_lead_time is None
            or
            maximum_lead_time is None
        ):

            return 0.0


        if (
            maximum_lead_time
            ==
            minimum_lead_time
        ):

            return 100.0


        score = (

            (
                maximum_lead_time
                -
                lead_time
            )

            /
            (
                maximum_lead_time
                -
                minimum_lead_time
            )

        ) * 100


        return (
            ProcurementService
            .clamp_score(
                score
            )
        )


    # ========================================================
    # GET SUPPLIER OPTIONS
    # ========================================================

    @staticmethod
    def get_supplier_options(
        db: Session,
        component_id: int,
        required_quantity: int
    ):

        # ----------------------------------------------------
        # Requirement validation
        # ----------------------------------------------------

        required_quantity = int(
            required_quantity
        )


        if required_quantity <= 0:

            raise ValueError(
                "Required quantity must be greater than zero."
            )


        # ----------------------------------------------------
        # Component
        # ----------------------------------------------------

        component = (

            db.query(
                Component
            )

            .filter(

                Component.id
                ==
                component_id,

                Component.is_active
                ==
                True

            )

            .first()

        )


        if component is None:

            raise ValueError(
                "Component not found."
            )


        # ----------------------------------------------------
        # Approved + active suppliers only
        # ----------------------------------------------------

        supplier_rows = (

            db.query(
                SupplierComponent,
                Supplier
            )

            .join(

                Supplier,

                Supplier.id
                ==
                SupplierComponent.supplier_id

            )

            .filter(

                SupplierComponent.component_id
                ==
                component_id,

                SupplierComponent.is_approved
                ==
                True,

                Supplier.is_active
                ==
                True

            )

            .all()

        )


        if not supplier_rows:

            return []


        results = []


        # ====================================================
        # BUILD BASE SUPPLIER RECORDS
        # ====================================================

        for (
            supplier_component,
            supplier
        ) in supplier_rows:

            # ------------------------------------------------
            # Commercial
            # ------------------------------------------------

            minimum_order_quantity = int(

                supplier_component
                .minimum_order_quantity

                or 1

            )


            recommended_order_quantity = int(

                ceil(

                    max(

                        required_quantity,

                        minimum_order_quantity

                    )

                )

            )


            maximum_capacity = (

                int(
                    supplier_component
                    .maximum_capacity
                )

                if supplier_component
                .maximum_capacity
                is not None

                else None

            )


            # ------------------------------------------------
            # Capacity
            # ------------------------------------------------

            capacity_can_fulfill = (

                maximum_capacity is None

                or

                maximum_capacity <= 0

                or

                maximum_capacity
                >=
                recommended_order_quantity

            )


            # ------------------------------------------------
            # Availability
            # ------------------------------------------------

            availability = (

                db.query(
                    SupplierAvailability
                )

                .filter(

                    SupplierAvailability.supplier_id
                    ==
                    supplier.id,

                    SupplierAvailability.component_id
                    ==
                    component_id

                )

                .first()

            )


            if availability is None:

                availability_data_available = False

                available_quantity = None

                committed_quantity = None

                available_to_promise = None

                replenishment_quantity = None

                replenishment_date = None

                last_updated = None

                availability_confirmed = False

                availability_percentage = 0.0


            else:

                availability_data_available = True

                available_quantity = int(
                    availability.available_quantity
                    or 0
                )

                committed_quantity = int(
                    availability.committed_quantity
                    or 0
                )

                available_to_promise = int(
                    availability.available_to_promise
                    or 0
                )

                replenishment_quantity = int(
                    availability
                    .expected_replenishment_quantity
                    or 0
                )

                replenishment_date = (
                    availability
                    .expected_replenishment_date
                )

                last_updated = (
                    availability.last_updated
                )


                availability_confirmed = (

                    available_to_promise
                    >=
                    recommended_order_quantity

                )


                availability_percentage = min(

                    (
                        available_to_promise
                        /
                        recommended_order_quantity
                    )
                    * 100,

                    100

                )


            # ------------------------------------------------
            # A supplier without a live availability row
            # can still remain a candidate because the PO
            # service allows it.
            #
            # But availability score stays 0 because ATP
            # cannot be confirmed.
            # ------------------------------------------------

            can_fulfill = (

                capacity_can_fulfill

                and

                (
                    not availability_data_available

                    or

                    availability_confirmed
                )

            )


            # ------------------------------------------------
            # Historical performance
            #
            # SINGLE SOURCE OF TRUTH
            # ------------------------------------------------

            performance = (

                SupplierPerformanceService
                .calculate_supplier_performance(

                    db,

                    supplier.id

                )

            )


            # ------------------------------------------------
            # XGBoost supplier risk
            # ------------------------------------------------

            try:

                risk_result = (

                    SupplierRiskService
                    .predict_supplier_risk(

                        db,

                        supplier.id

                    )

                )

                ai_risk_available = True

                ai_risk_level = (
                    risk_result.get(
                        "risk_level",
                        "UNKNOWN"
                    )
                )

                ai_risk_confidence = (
                    risk_result.get(
                        "confidence"
                    )
                )

                ai_risk_probabilities = (
                    risk_result.get(
                        "risk_probabilities"
                    )
                    or {}
                )


            except Exception:

                risk_result = None

                ai_risk_available = False

                ai_risk_level = "UNKNOWN"

                ai_risk_confidence = None

                ai_risk_probabilities = {}


            ai_risk_score = (

                ProcurementService
                .calculate_ai_risk_score(
                    risk_result
                )

            )


            # ------------------------------------------------
            # Scores already known
            # ------------------------------------------------

            availability_score = (

                ProcurementService
                .clamp_score(
                    availability_percentage
                )

            )


            fulfillment_score = (

                ProcurementService
                .clamp_score(

                    performance[
                        "fill_rate"
                    ]

                )

            )


            reliability_decision_score = (

                ProcurementService
                .clamp_score(

                    performance[
                        "reliability_score"
                    ]

                )

            )


            quality_decision_score = (

                ProcurementService
                .clamp_score(

                    performance[
                        "quality_score"
                    ]

                )

            )


            # ------------------------------------------------
            # Base record
            # ------------------------------------------------

            result = {

                # Supplier
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


                # Component
                "component_id":
                    component.id,

                "part_id":
                    component.part_id,

                "part_name":
                    component.part_name,

                "criticality":
                    component.criticality,


                # Commercial
                "supplier_part_code":
                    supplier_component
                    .supplier_part_code,

                "unit_price":
                    (
                        float(
                            supplier_component
                            .unit_price
                        )

                        if supplier_component
                        .unit_price
                        is not None

                        else None
                    ),

                "minimum_order_quantity":
                    minimum_order_quantity,

                "standard_lead_time_days":
                    (
                        int(
                            supplier_component
                            .standard_lead_time_days
                        )

                        if supplier_component
                        .standard_lead_time_days
                        is not None

                        else None
                    ),

                "maximum_capacity":
                    maximum_capacity,

                "is_approved":
                    supplier_component
                    .is_approved,


                # Availability
                "availability_data_available":
                    availability_data_available,

                "available_quantity":
                    available_quantity,

                "committed_quantity":
                    committed_quantity,

                "available_to_promise":
                    available_to_promise,

                "expected_replenishment_quantity":
                    replenishment_quantity,

                "expected_replenishment_date":
                    replenishment_date,

                "last_updated":
                    last_updated,


                # Requirement
                "required_quantity":
                    required_quantity,

                "recommended_order_quantity":
                    recommended_order_quantity,

                "can_fulfill":
                    can_fulfill,

                "capacity_can_fulfill":
                    capacity_can_fulfill,

                "availability_confirmed":
                    availability_confirmed,

                "availability_percentage":
                    round(
                        availability_percentage,
                        2
                    ),


                # Historical performance
                "performance_data_available":
                    performance[
                        "performance_data_available"
                    ],

                "total_orders":
                    performance[
                        "total_orders"
                    ],

                "on_time_delivery_rate":
                    performance[
                        "on_time_delivery_rate"
                    ],

                "fill_rate":
                    performance[
                        "fill_rate"
                    ],

                "defect_rate":
                    performance[
                        "defect_rate"
                    ],

                "average_delay_days":
                    performance[
                        "average_delay_days"
                    ],

                "quality_score":
                    performance[
                        "quality_score"
                    ],

                "quality_source":
                    performance[
                        "quality_source"
                    ],

                "reliability_score":
                    performance[
                        "reliability_score"
                    ],

                "reliability_source":
                    performance[
                        "reliability_source"
                    ],


                # XGBoost
                "ai_risk_available":
                    ai_risk_available,

                "ai_risk_level":
                    ai_risk_level,

                "ai_risk_confidence":
                    ai_risk_confidence,

                "ai_risk_probabilities":
                    ai_risk_probabilities,


                # Decision factors
                "availability_score":
                    round(
                        availability_score,
                        2
                    ),

                "fulfillment_score":
                    round(
                        fulfillment_score,
                        2
                    ),

                "reliability_decision_score":
                    round(
                        reliability_decision_score,
                        2
                    ),

                "quality_decision_score":
                    round(
                        quality_decision_score,
                        2
                    ),

                "ai_risk_score":
                    round(
                        ai_risk_score,
                        2
                    ),

                # Calculated after comparing
                # all candidate suppliers
                "price_score":
                    0.0,

                "lead_time_score":
                    0.0,

                "final_score":
                    0.0,

                "rank":
                    0

            }


            results.append(
                result
            )


        # ====================================================
        # RELATIVE PRICE NORMALIZATION
        # ====================================================

        valid_prices = [

            item[
                "unit_price"
            ]

            for item
            in results

            if item[
                "unit_price"
            ]
            is not None

        ]


        minimum_price = (

            min(
                valid_prices
            )

            if valid_prices

            else None

        )


        maximum_price = (

            max(
                valid_prices
            )

            if valid_prices

            else None

        )


        # ====================================================
        # RELATIVE LEAD TIME NORMALIZATION
        # ====================================================

        valid_lead_times = [

            item[
                "standard_lead_time_days"
            ]

            for item
            in results

            if item[
                "standard_lead_time_days"
            ]
            is not None

        ]


        minimum_lead_time = (

            min(
                valid_lead_times
            )

            if valid_lead_times

            else None

        )


        maximum_lead_time = (

            max(
                valid_lead_times
            )

            if valid_lead_times

            else None

        )


        # ====================================================
        # FINAL WEIGHTED SCORE
        # ====================================================

        for result in results:

            price_score = (

                ProcurementService
                .calculate_price_score(

                    result[
                        "unit_price"
                    ],

                    minimum_price,

                    maximum_price

                )

            )


            lead_time_score = (

                ProcurementService
                .calculate_lead_time_score(

                    result[
                        "standard_lead_time_days"
                    ],

                    minimum_lead_time,

                    maximum_lead_time

                )

            )


            result[
                "price_score"
            ] = round(
                price_score,
                2
            )


            result[
                "lead_time_score"
            ] = round(
                lead_time_score,
                2
            )


            final_score = (

                result[
                    "availability_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "availability"
                ]

                +

                result[
                    "fulfillment_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "fulfillment"
                ]

                +

                result[
                    "reliability_decision_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "reliability"
                ]

                +

                result[
                    "quality_decision_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "quality"
                ]

                +

                result[
                    "ai_risk_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "ai_risk"
                ]

                +

                result[
                    "price_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "price"
                ]

                +

                result[
                    "lead_time_score"
                ]
                *
                ProcurementService
                .WEIGHTS[
                    "lead_time"
                ]

            )


            # -----------------------------------------------
            # Capacity constraint penalty
            #
            # Supplier that cannot satisfy monthly capacity
            # should not outrank a feasible supplier.
            # -----------------------------------------------

            if not result[
                "capacity_can_fulfill"
            ]:

                final_score *= 0.50


            result[
                "final_score"
            ] = round(
                ProcurementService
                .clamp_score(
                    final_score
                ),
                2
            )


        # ====================================================
        # RANK
        # ====================================================
        #
        # 1. Suppliers that can fulfill
        # 2. Highest weighted score
        # 3. Shorter lead time
        # 4. Lower price
        # ====================================================

        results.sort(

            key=lambda item: (

                not item[
                    "can_fulfill"
                ],

                -item[
                    "final_score"
                ],

                (
                    item[
                        "standard_lead_time_days"
                    ]

                    if item[
                        "standard_lead_time_days"
                    ]
                    is not None

                    else 999999
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


        for (
            index,
            result
        ) in enumerate(
            results,
            start=1
        ):

            result[
                "rank"
            ] = index


        return results


    # ========================================================
    # GET PROCUREMENT RECOMMENDATION
    # ========================================================

    @staticmethod
    def get_recommendation(
        db: Session,
        component_id: int,
        required_quantity: int
    ):

        required_quantity = int(
            required_quantity
        )


        if required_quantity <= 0:

            raise ValueError(
                "Required quantity must be greater than zero."
            )


        component = (

            db.query(
                Component
            )

            .filter(

                Component.id
                ==
                component_id,

                Component.is_active
                ==
                True

            )

            .first()

        )


        if component is None:

            raise ValueError(
                "Component not found."
            )


        supplier_options = (

            ProcurementService
            .get_supplier_options(

                db,

                component_id,

                required_quantity

            )

        )


        recommended_supplier = (

            supplier_options[0]

            if supplier_options

            else None

        )


        return {

            "component_id":
                component.id,

            "part_id":
                component.part_id,

            "part_name":
                component.part_name,

            "criticality":
                component.criticality,

            "required_quantity":
                required_quantity,

            "recommended_supplier_id":
                (
                    recommended_supplier[
                        "supplier_id"
                    ]

                    if recommended_supplier

                    else None
                ),

            "recommended_supplier":
                recommended_supplier,

            "supplier_options":
                supplier_options,

            "weights": {

                key:
                    round(
                        value * 100,
                        2
                    )

                for (
                    key,
                    value
                )
                in
                ProcurementService
                .WEIGHTS
                .items()

            }

        }