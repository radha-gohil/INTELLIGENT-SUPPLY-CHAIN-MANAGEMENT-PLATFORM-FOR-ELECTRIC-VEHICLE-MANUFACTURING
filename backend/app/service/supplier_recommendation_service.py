from sqlalchemy.orm import Session

from backend.app.models import (
    Supplier,
    SupplierComponent,
    SupplierAvailability,
    Component
)

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
)

from backend.app.service.supplier_risk_service import (
    SupplierRiskService
)


class SupplierRecommendationService:

    # ========================================================
    # GET COMPONENT
    # ========================================================

    @staticmethod
    def get_component(
        db: Session,
        component_id: int
    ):

        component = (
            db.query(Component)
            .filter(
                Component.id == component_id
            )
            .first()
        )

        if component is None:

            raise ValueError(
                "Component not found."
            )

        return component


    # ========================================================
    # GET SUPPLIERS FOR COMPONENT
    # ========================================================

    @staticmethod
    def get_supplier_records(
        db: Session,
        component_id: int
    ):

        records = (

            db.query(
                Supplier,
                SupplierComponent,
                SupplierAvailability
            )

            .join(
                SupplierComponent,
                Supplier.id
                == SupplierComponent.supplier_id
            )

            .outerjoin(
                SupplierAvailability,

                (
                    SupplierAvailability.supplier_id
                    == SupplierComponent.supplier_id
                )

                &

                (
                    SupplierAvailability.component_id
                    == component_id
                )
            )

            .filter(

                SupplierComponent.component_id
                == component_id,

                Supplier.is_active == True,

                SupplierComponent.is_approved == True

            )

            .all()
        )

        return records


    # ========================================================
    # CALCULATE NORMALIZED SCORE
    # ========================================================

    @staticmethod
    def calculate_score(
        availability_score: float,
        lead_time_score: float,
        price_score: float,
        reliability_score: float,
        risk_score: float
    ):

        score = (

            availability_score * 0.30

            +

            lead_time_score * 0.15

            +

            price_score * 0.10

            +

            reliability_score * 0.30

            +

            risk_score * 0.15

        )

        return round(
            score,
            2
        )


    # ========================================================
    # RECOMMEND SUPPLIER
    # ========================================================

    @staticmethod
    def recommend_supplier(
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
        # Check component
        # ----------------------------------------------------

        SupplierRecommendationService.get_component(
            db,
            component_id
        )


        # ----------------------------------------------------
        # Get suppliers
        # ----------------------------------------------------

        records = (

            SupplierRecommendationService
            .get_supplier_records(

                db,
                component_id

            )
        )


        if not records:

            raise ValueError(
                "No approved active suppliers found "
                "for this component."
            )


        # ----------------------------------------------------
        # First pass: collect values
        # ----------------------------------------------------

        candidates = []


        for supplier, supplier_component, availability in records:

            # ------------------------------------------------
            # Availability
            # ------------------------------------------------

            if availability is None:

                available_to_promise = 0

            else:

                available_to_promise = (
                    availability.available_to_promise
                )


            # ------------------------------------------------
            # Capacity
            # ------------------------------------------------

            maximum_capacity = (

                supplier_component.maximum_capacity

            )


            # ------------------------------------------------
            # Can supplier fulfill requirement?
            # ------------------------------------------------

            fulfillment_ratio = (

                available_to_promise
                /
                required_quantity

            )


            # ------------------------------------------------
            # Reliability
            # ------------------------------------------------

            try:

                performance = (

                    SupplierPerformanceService
                    .calculate_supplier_performance(

                        db,
                        supplier.id

                    )
                )

                reliability_score = (

                    performance["reliability_score"]

                )

            except Exception:

                reliability_score = 0.0


            # ------------------------------------------------
            # Risk prediction
            # ------------------------------------------------

            try:

                risk_prediction = (

                    SupplierRiskService
                    .predict_supplier_risk(

                        db,
                        supplier.id

                    )
                )

                risk_level = (

                    risk_prediction["risk_level"]

                )

                risk_confidence = (

                    risk_prediction["confidence"]

                )

            except Exception:

                risk_level = "UNKNOWN"

                risk_confidence = 0.0


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

                risk_score = 0.0


            # ------------------------------------------------
            # Lead time
            # ------------------------------------------------

            lead_time = (

                supplier_component
                .standard_lead_time_days

            )


            # ------------------------------------------------
            # Price
            # ------------------------------------------------

            unit_price = (

                supplier_component.unit_price

            )


            candidates.append({

                "supplier": supplier,

                "supplier_component":
                    supplier_component,

                "availability":
                    availability,

                "available_to_promise":
                    available_to_promise,

                "fulfillment_ratio":
                    fulfillment_ratio,

                "maximum_capacity":
                    maximum_capacity,

                "reliability_score":
                    reliability_score,

                "risk_level":
                    risk_level,

                "risk_confidence":
                    risk_confidence,

                "risk_score":
                    risk_score,

                "lead_time":
                    lead_time,

                "unit_price":
                    unit_price

            })


        # ====================================================
        # NORMALIZATION VALUES
        # ====================================================

        max_atp = max(

            candidate["available_to_promise"]

            for candidate in candidates

        )


        lead_times = [

            candidate["lead_time"]

            for candidate in candidates

            if candidate["lead_time"] is not None

        ]


        prices = [

            candidate["unit_price"]

            for candidate in candidates

            if candidate["unit_price"] is not None

        ]


        min_lead_time = (

            min(lead_times)

            if lead_times

            else None

        )


        max_lead_time = (

            max(lead_times)

            if lead_times

            else None

        )


        min_price = (

            min(prices)

            if prices

            else None

        )


        max_price = (

            max(prices)

            if prices

            else None

        )


        # ====================================================
        # SCORE EACH SUPPLIER
        # ====================================================

        for candidate in candidates:

            # ------------------------------------------------
            # Availability score
            # ------------------------------------------------

            if max_atp > 0:

                availability_score = (

                    candidate["available_to_promise"]
                    /
                    max_atp

                ) * 100

            else:

                availability_score = 0.0


            # ------------------------------------------------
            # Lead-time score
            # ------------------------------------------------

            lead_time = candidate["lead_time"]


            if (

                lead_time is not None

                and min_lead_time is not None

                and max_lead_time is not None

            ):

                if max_lead_time == min_lead_time:

                    lead_time_score = 100.0

                else:

                    lead_time_score = (

                        (
                            max_lead_time
                            - lead_time
                        )
                        /
                        (
                            max_lead_time
                            - min_lead_time
                        )

                    ) * 100

            else:

                lead_time_score = 50.0


            # ------------------------------------------------
            # Price score
            # ------------------------------------------------

            price = candidate["unit_price"]


            if (

                price is not None

                and min_price is not None

                and max_price is not None

            ):

                if max_price == min_price:

                    price_score = 100.0

                else:

                    price_score = (

                        (
                            max_price
                            - price
                        )
                        /
                        (
                            max_price
                            - min_price
                        )

                    ) * 100

            else:

                price_score = 50.0


            # ------------------------------------------------
            # Reliability score
            # ------------------------------------------------

            reliability_score = (

                candidate["reliability_score"]

            )


            # ------------------------------------------------
            # Final recommendation score
            # ------------------------------------------------

            recommendation_score = (

                SupplierRecommendationService
                .calculate_score(

                    availability_score,

                    lead_time_score,

                    price_score,

                    reliability_score,

                    candidate["risk_score"]

                )

            )


            # ------------------------------------------------
            # Store scores
            # ------------------------------------------------

            candidate[
                "availability_score"
            ] = round(

                availability_score,
                2

            )


            candidate[
                "lead_time_score"
            ] = round(

                lead_time_score,
                2

            )


            candidate[
                "price_score"
            ] = round(

                price_score,
                2

            )


            candidate[
                "recommendation_score"
            ] = recommendation_score


        # ====================================================
        # SORT
        # ====================================================

        candidates.sort(

            key=lambda candidate:
                candidate["recommendation_score"],

            reverse=True

        )


        # ====================================================
        # BUILD RESPONSE
        # ====================================================

        formatted_candidates = []


        for candidate in candidates:

            supplier = candidate["supplier"]

            supplier_component = (

                candidate["supplier_component"]

            )


            # ------------------------------------------------
            # Reason
            # ------------------------------------------------

            if (

                candidate["available_to_promise"]
                >= required_quantity

            ):

                availability_text = (
                    "Can fulfill the required quantity"
                )

            elif (

                candidate["available_to_promise"] > 0

            ):

                availability_text = (
                    "Has partial available quantity"
                )

            else:

                availability_text = (
                    "Currently has no available quantity"
                )


            reason = (

                availability_text
                + ", "
                + "reliability score "
                + str(
                    candidate["reliability_score"]
                )
                + ", "
                + "risk level "
                + candidate["risk_level"]
            )


            formatted_candidates.append({

                "supplier_id":
                    supplier.id,

                "supplier_code":
                    supplier.supplier_code,

                "supplier_name":
                    supplier.supplier_name,

                "available_to_promise":
                    candidate[
                        "available_to_promise"
                    ],

                "unit_price":
                    supplier_component.unit_price,

                "standard_lead_time_days":
                    supplier_component
                    .standard_lead_time_days,

                "maximum_capacity":
                    supplier_component
                    .maximum_capacity,

                "reliability_score":
                    candidate[
                        "reliability_score"
                    ],

                "risk_level":
                    candidate[
                        "risk_level"
                    ],

                "risk_confidence":
                    candidate[
                        "risk_confidence"
                    ],

                "recommendation_score":
                    candidate[
                        "recommendation_score"
                    ],

                "recommendation_reason":
                    reason

            })


        # ====================================================
        # FINAL RESULT
        # ====================================================

        return {

            "component_id":
                component_id,

            "required_quantity":
                required_quantity,

            "recommended_supplier":
                formatted_candidates[0],

            "alternatives":
                formatted_candidates[1:]

        }