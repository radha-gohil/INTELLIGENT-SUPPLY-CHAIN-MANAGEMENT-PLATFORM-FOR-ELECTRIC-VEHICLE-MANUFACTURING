from sqlalchemy.orm import Session

from backend.app.models import (
    Component,
    Supplier,
    SupplierComponent,
    SupplierAvailability
)

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
)

from backend.app.service.supplier_risk_service import (
    SupplierRiskService
)


class SupplierSelectionService:

    # ========================================================
    # NORMALIZATION FUNCTIONS
    # ========================================================

    @staticmethod
    def normalize_higher_is_better(
        value,
        minimum,
        maximum
    ):

        if maximum == minimum:

            return 100.0

        score = (

            (value - minimum)
            /
            (maximum - minimum)

        ) * 100

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )


    @staticmethod
    def normalize_lower_is_better(
        value,
        minimum,
        maximum
    ):

        if maximum == minimum:

            return 100.0

        score = (

            (maximum - value)
            /
            (maximum - minimum)

        ) * 100

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )


    # ========================================================
    # GENERATE SUPPLIER EXPLANATION
    # ========================================================

    @staticmethod
    def generate_explanation(
        supplier,
        required_quantity
    ):

        reasons = []

        warnings = []

        # ----------------------------------------------------
        # Availability
        # ----------------------------------------------------

        if supplier["can_fulfill"]:

            reasons.append(

                "The supplier can fulfill the complete "
                "required quantity."

            )

        else:

            warnings.append(

                "The supplier cannot currently fulfill "
                "the complete required quantity."

            )

        # ----------------------------------------------------
        # Reliability
        # ----------------------------------------------------

        reliability = supplier[
            "reliability_score"
        ]

        if reliability >= 90:

            reasons.append(

                f"High historical reliability "
                f"({reliability:.2f}%)."

            )

        elif reliability >= 75:

            reasons.append(

                f"Moderate historical reliability "
                f"({reliability:.2f}%)."

            )

        else:

            warnings.append(

                f"Low historical reliability "
                f"({reliability:.2f}%)."

            )

        # ----------------------------------------------------
        # AI Risk
        # ----------------------------------------------------

        risk = supplier[
            "risk_level"
        ]

        if risk == "LOW":

            reasons.append(

                "The AI model predicts LOW supplier risk."

            )

        elif risk == "MEDIUM":

            warnings.append(

                "The AI model predicts MEDIUM supplier risk."

            )

        elif risk == "HIGH":

            warnings.append(

                "The AI model predicts HIGH supplier risk."

            )

        else:

            warnings.append(

                "Supplier risk could not be determined."

            )

        # ----------------------------------------------------
        # Quality
        # ----------------------------------------------------

        defect_rate = supplier[
            "defect_rate"
        ]

        if defect_rate <= 1:

            reasons.append(

                f"Very low defect rate "
                f"({defect_rate:.2f}%)."

            )

        elif defect_rate <= 3:

            reasons.append(

                f"Acceptable defect rate "
                f"({defect_rate:.2f}%)."

            )

        else:

            warnings.append(

                f"High defect rate "
                f"({defect_rate:.2f}%)."

            )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        price_score = supplier[
            "price_score"
        ]

        if price_score >= 80:

            reasons.append(

                "The supplier has a competitive unit price."

            )

        elif price_score < 40:

            warnings.append(

                "The supplier has a relatively high unit price."

            )

        # ----------------------------------------------------
        # Lead time
        # ----------------------------------------------------

        lead_time = supplier[
            "standard_lead_time_days"
        ]

        if lead_time is not None:

            if lead_time <= 5:

                reasons.append(

                    f"Short standard lead time "
                    f"({lead_time} days)."

                )

            elif lead_time <= 10:

                reasons.append(

                    f"Moderate standard lead time "
                    f"({lead_time} days)."

                )

            else:

                warnings.append(

                    f"Long standard lead time "
                    f"({lead_time} days)."

                )

        # ----------------------------------------------------
        # Build summary
        # ----------------------------------------------------

        if supplier["can_fulfill"]:

            summary = (

                f"{supplier['supplier_name']} is recommended "
                f"for {required_quantity:,} units because it "
                f"provides sufficient availability and achieves "
                f"an overall supplier score of "
                f"{supplier['supplier_score']:.2f}."

            )

        else:

            summary = (

                f"{supplier['supplier_name']} has the highest "
                f"available score among the evaluated suppliers, "
                f"but it cannot currently fulfill the complete "
                f"requirement of {required_quantity:,} units."

            )

        return {

            "summary":
                summary,

            "reasons":
                reasons,

            "warnings":
                warnings

        }


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
        # Validate quantity
        # ----------------------------------------------------

        if required_quantity <= 0:

            raise ValueError(
                "Required quantity must be greater than zero."
            )

        # ----------------------------------------------------
        # Get component
        # ----------------------------------------------------

        component = (

            db.query(Component)

            .filter(

                Component.id == component_id,

                Component.is_active == True

            )

            .first()

        )

        if component is None:

            raise ValueError(
                "Component not found or inactive."
            )

        # ----------------------------------------------------
        # Get supplier-component relationships
        # ----------------------------------------------------

        supplier_components = (

            db.query(SupplierComponent)

            .filter(

                SupplierComponent.component_id
                == component_id

            )

            .all()

        )

        results = []

        # ====================================================
        # COLLECT SUPPLIER DATA
        # ====================================================

        for supplier_component in supplier_components:

            # ------------------------------------------------
            # Get supplier
            # ------------------------------------------------

            supplier = (

                db.query(Supplier)

                .filter(

                    Supplier.id
                    == supplier_component.supplier_id,

                    Supplier.is_active == True

                )

                .first()

            )

            if supplier is None:

                continue

            # ------------------------------------------------
            # Approved suppliers only
            # ------------------------------------------------

            if not supplier_component.is_approved:

                continue

            # ------------------------------------------------
            # Availability
            # ------------------------------------------------

            availability = (

                db.query(SupplierAvailability)

                .filter(

                    SupplierAvailability.supplier_id
                    == supplier.id,

                    SupplierAvailability.component_id
                    == component_id

                )

                .first()

            )

            if availability is None:

                available_quantity = 0

                committed_quantity = 0

                available_to_promise = 0

                expected_replenishment_quantity = 0

                expected_replenishment_date = None

            else:

                available_quantity = (
                    availability.available_quantity
                )

                committed_quantity = (
                    availability.committed_quantity
                )

                available_to_promise = (
                    availability.available_to_promise
                )

                expected_replenishment_quantity = (
                    availability.expected_replenishment_quantity
                )

                expected_replenishment_date = (
                    availability.expected_replenishment_date
                )

            # ------------------------------------------------
            # Fulfillment
            # ------------------------------------------------

            can_fulfill = (

                available_to_promise
                >= required_quantity

            )

            # ------------------------------------------------
            # Supplier performance
            # ------------------------------------------------

            try:

                performance = (

                    SupplierPerformanceService
                    .calculate_supplier_performance(

                        db,

                        supplier.id

                    )

                )

            except ValueError:

                performance = {

                    "reliability_score": 0.0,

                    "on_time_delivery_rate": 0.0,

                    "fill_rate": 0.0,

                    "defect_rate": 0.0,

                    "average_delay_days": 0.0

                }

            # ------------------------------------------------
            # AI supplier risk
            # ------------------------------------------------

            try:

                risk = (

                    SupplierRiskService
                    .predict_supplier_risk(

                        db,

                        supplier.id

                    )

                )

                risk_level = risk["risk_level"]

                risk_confidence = risk["confidence"]

            except Exception:

                risk_level = "UNKNOWN"

                risk_confidence = 0.0

            # ------------------------------------------------
            # Commercial data
            # ------------------------------------------------

            unit_price = (

                supplier_component.unit_price

                if supplier_component.unit_price
                is not None

                else component.unit_cost

            )

            minimum_order_quantity = (

                supplier_component.minimum_order_quantity

            )

            lead_time = (

                supplier_component.standard_lead_time_days

            )

            maximum_capacity = (

                supplier_component.maximum_capacity

            )

            # ------------------------------------------------
            # Quality score
            # ------------------------------------------------

            quality_score = max(

                0.0,

                100.0
                -
                performance["defect_rate"]

            )

            # ------------------------------------------------
            # Risk score
            # ------------------------------------------------

            if risk_level == "LOW":

                risk_score = 100.0

            elif risk_level == "MEDIUM":

                risk_score = 60.0

            elif risk_level == "HIGH":

                risk_score = 20.0

            else:

                risk_score = 40.0

            # ------------------------------------------------
            # Store supplier
            # ------------------------------------------------

            results.append({

                "supplier_id":
                    supplier.id,

                "supplier_code":
                    supplier.supplier_code,

                "supplier_name":
                    supplier.supplier_name,

                "component_id":
                    component.id,

                "component_part_id":
                    component.part_id,

                "component_name":
                    component.part_name,

                "required_quantity":
                    required_quantity,

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

                "can_fulfill":
                    can_fulfill,

                "unit_price":
                    unit_price,

                "minimum_order_quantity":
                    minimum_order_quantity,

                "standard_lead_time_days":
                    lead_time,

                "maximum_capacity":
                    maximum_capacity,

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

                "reliability_score":
                    performance[
                        "reliability_score"
                    ],

                "risk_level":
                    risk_level,

                "risk_confidence":
                    risk_confidence,

                "quality_score":
                    quality_score,

                "risk_score":
                    risk_score

            })

        # ====================================================
        # NO SUPPLIERS
        # ====================================================

        if not results:

            return {

                "component_id":
                    component.id,

                "component_part_id":
                    component.part_id,

                "component_name":
                    component.part_name,

                "required_quantity":
                    required_quantity,

                "supplier_count":
                    0,

                "recommended_supplier":
                    None,

                "suppliers":
                    []

            }

        # ====================================================
        # NORMALIZATION VALUES
        # ====================================================

        prices = [

            r["unit_price"]

            for r in results

            if r["unit_price"] is not None

        ]

        lead_times = [

            r["standard_lead_time_days"]

            for r in results

            if r["standard_lead_time_days"]
            is not None

        ]

        availabilities = [

            r["available_to_promise"]

            for r in results

        ]

        if prices:

            min_price = min(prices)

            max_price = max(prices)

        else:

            min_price = 0

            max_price = 0

        if lead_times:

            min_lead_time = min(lead_times)

            max_lead_time = max(lead_times)

        else:

            min_lead_time = 0

            max_lead_time = 0

        min_availability = min(
            availabilities
        )

        max_availability = max(
            availabilities
        )

        # ====================================================
        # CALCULATE SCORES
        # ====================================================

        for result in results:

            # ------------------------------------------------
            # Availability
            # ------------------------------------------------

            availability_score = (

                SupplierSelectionService
                .normalize_higher_is_better(

                    result[
                        "available_to_promise"
                    ],

                    min_availability,

                    max_availability

                )

            )

            # ------------------------------------------------
            # Price
            # ------------------------------------------------

            if result["unit_price"] is None:

                price_score = 50.0

            else:

                price_score = (

                    SupplierSelectionService
                    .normalize_lower_is_better(

                        result["unit_price"],

                        min_price,

                        max_price

                    )

                )

            # ------------------------------------------------
            # Lead time
            # ------------------------------------------------

            if result[
                "standard_lead_time_days"
            ] is None:

                lead_time_score = 50.0

            else:

                lead_time_score = (

                    SupplierSelectionService
                    .normalize_lower_is_better(

                        result[
                            "standard_lead_time_days"
                        ],

                        min_lead_time,

                        max_lead_time

                    )

                )

            # ------------------------------------------------
            # Reliability
            # ------------------------------------------------

            reliability_score = (

                result[
                    "reliability_score"
                ]

            )

            # ------------------------------------------------
            # Quality
            # ------------------------------------------------

            quality_score = (

                result[
                    "quality_score"
                ]

            )

            # ------------------------------------------------
            # Risk
            # ------------------------------------------------

            risk_score = (

                result[
                    "risk_score"
                ]

            )

            # ------------------------------------------------
            # Final score
            # ------------------------------------------------

            overall_score = (

                availability_score * 0.25

                +

                reliability_score * 0.25

                +

                risk_score * 0.20

                +

                quality_score * 0.15

                +

                price_score * 0.10

                +

                lead_time_score * 0.05

            )

            result["availability_score"] = round(
                availability_score,
                2
            )

            result["price_score"] = round(
                price_score,
                2
            )

            result["lead_time_score"] = round(
                lead_time_score,
                2
            )

            result["supplier_score"] = round(
                overall_score,
                2
            )

        # ====================================================
        # SORT
        # ====================================================

        results.sort(

            key=lambda x: (

                x["can_fulfill"],

                x["supplier_score"]

            ),

            reverse=True

        )

        # ====================================================
        # RANK
        # ====================================================

        for index, result in enumerate(

            results,

            start=1

        ):

            result["rank"] = index

        # ====================================================
        # SELECT RECOMMENDED SUPPLIER
        # ====================================================

        fulfillable_suppliers = [

            result

            for result in results

            if result["can_fulfill"]

        ]

        if fulfillable_suppliers:

            recommended_supplier = (

                fulfillable_suppliers[0]

            )

        else:

            recommended_supplier = results[0]

        # ====================================================
        # GENERATE EXPLANATION
        # ====================================================

        explanation = (

            SupplierSelectionService
            .generate_explanation(

                recommended_supplier,

                required_quantity

            )

        )

        # ====================================================
        # RETURN FINAL RESULT
        # ====================================================

        return {

            "component_id":
                component.id,

            "component_part_id":
                component.part_id,

            "component_name":
                component.part_name,

            "required_quantity":
                required_quantity,

            "supplier_count":
                len(results),

            "recommended_supplier":
                recommended_supplier,

            "recommendation_explanation":
                explanation,

            "suppliers":
                results

        }