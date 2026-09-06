from sqlalchemy.orm import Session

from backend.app.models import (
    Supplier,
    SupplierPerformance
)


class SupplierPerformanceService:

    # ========================================================
    # QUALITY RATING -> 0-100 SCORE
    # ========================================================

    @staticmethod
    def quality_rating_to_score(
        quality_rating
    ):

        if quality_rating is None:

            return None

        try:

            rating = float(
                quality_rating
            )

        except (
            TypeError,
            ValueError
        ):

            return None


        # ----------------------------------------------------
        # Normal supplier-master rating: 0 to 5
        # ----------------------------------------------------

        if 0 <= rating <= 5:

            return (
                rating / 5
            ) * 100


        # ----------------------------------------------------
        # Defensive support for a rating already expressed
        # on a 0-100 scale.
        # ----------------------------------------------------

        if 5 < rating <= 100:

            return rating


        return None


    # ========================================================
    # CALCULATE PERFORMANCE FOR ONE SUPPLIER
    # ========================================================

    @staticmethod
    def calculate_supplier_performance(
        db: Session,
        supplier_id: int
    ):

        # ----------------------------------------------------
        # Supplier
        # ----------------------------------------------------

        supplier = (

            db.query(
                Supplier
            )

            .filter(
                Supplier.id
                == supplier_id
            )

            .first()

        )


        if supplier is None:

            raise ValueError(
                "Supplier not found."
            )


        # ----------------------------------------------------
        # Supplier master quality
        # ----------------------------------------------------

        baseline_quality_score = (
            SupplierPerformanceService
            .quality_rating_to_score(
                supplier.quality_rating
            )
        )


        baseline_reliability_score = (
            supplier
            .baseline_reliability_score
        )


        # ----------------------------------------------------
        # Historical performance records
        # ----------------------------------------------------

        records = (

            db.query(
                SupplierPerformance
            )

            .filter(
                SupplierPerformance.supplier_id
                == supplier_id
            )

            .all()

        )


        # ====================================================
        # NO HISTORICAL PERFORMANCE
        # ====================================================

        if not records:

            quality_score = (
                baseline_quality_score
                if baseline_quality_score is not None
                else 0.0
            )


            reliability_score = (
                float(
                    baseline_reliability_score
                )
                if baseline_reliability_score is not None
                else 0.0
            )


            return {

                "supplier_id":
                    supplier.id,

                "supplier_code":
                    supplier.supplier_code,

                "supplier_name":
                    supplier.supplier_name,

                "performance_data_available":
                    False,

                "total_orders":
                    0,

                "on_time_orders":
                    0,

                "late_orders":
                    0,

                "ordered_quantity":
                    0,

                "received_quantity":
                    0,

                "defective_quantity":
                    0,

                "on_time_delivery_rate":
                    0.0,

                "fill_rate":
                    0.0,

                "defect_rate":
                    0.0,

                "average_delay_days":
                    0.0,

                "quality_score":
                    round(
                        quality_score,
                        2
                    ),

                "quality_source":
                    (
                        "MASTER_RATING"
                        if baseline_quality_score
                        is not None
                        else "UNAVAILABLE"
                    ),

                "baseline_quality_rating":
                    supplier.quality_rating,

                "baseline_reliability_score":
                    baseline_reliability_score,

                "reliability_score":
                    round(
                        reliability_score,
                        2
                    )

            }


        # ====================================================
        # AGGREGATE HISTORICAL DATA
        # ====================================================

        total_orders = sum(

            record.total_orders

            for record
            in records

        )


        on_time_orders = sum(

            record.on_time_orders

            for record
            in records

        )


        late_orders = sum(

            record.late_orders

            for record
            in records

        )


        ordered_quantity = sum(

            record.ordered_quantity

            for record
            in records

        )


        received_quantity = sum(

            record.received_quantity

            for record
            in records

        )


        defective_quantity = sum(

            record.defective_quantity

            for record
            in records

        )


        # ====================================================
        # AVERAGE DELAY
        # ====================================================

        weighted_delay = sum(

            (
                record.average_delay_days
                *
                record.late_orders
            )

            for record
            in records

        )


        if late_orders > 0:

            average_delay_days = (
                weighted_delay
                /
                late_orders
            )

        else:

            average_delay_days = 0.0


        # ====================================================
        # ON-TIME DELIVERY RATE
        # ====================================================

        if total_orders > 0:

            on_time_delivery_rate = (

                on_time_orders
                /
                total_orders

            ) * 100

        else:

            on_time_delivery_rate = 0.0


        # ====================================================
        # FILL RATE
        # ====================================================

        if ordered_quantity > 0:

            fill_rate = (

                received_quantity
                /
                ordered_quantity

            ) * 100

        else:

            fill_rate = 0.0


        # ====================================================
        # DEFECT RATE
        # ====================================================

        if received_quantity > 0:

            defect_rate = (

                defective_quantity
                /
                received_quantity

            ) * 100

        else:

            defect_rate = 0.0


        # ====================================================
        # QUALITY SCORE
        # ====================================================
        #
        # The new historical PO dataset does not contain
        # defective quantity.
        #
        # Therefore:
        #
        # 1. If actual defect information exists -> use it.
        # 2. Otherwise use supplier-master quality rating.
        # 3. If neither exists -> fall back to calculated
        #    defect quality.
        # ====================================================

        actual_defect_information_available = (

            defective_quantity > 0

        )


        if actual_defect_information_available:

            quality_score = max(

                0,

                100
                -
                defect_rate

            )

            quality_source = (
                "HISTORICAL_DEFECT_DATA"
            )


        elif baseline_quality_score is not None:

            quality_score = (
                baseline_quality_score
            )

            quality_source = (
                "MASTER_RATING"
            )


        else:

            quality_score = max(

                0,

                100
                -
                defect_rate

            )

            quality_source = (
                "PERFORMANCE_FALLBACK"
            )


        # ====================================================
        # OPERATIONAL RELIABILITY SCORE
        # ====================================================
        #
        # Existing logic preserved:
        #
        # 50% On-time delivery
        # 30% Fill rate
        # 20% Quality
        # ====================================================

        reliability_score = (

            (
                on_time_delivery_rate
                *
                0.50
            )

            +

            (
                fill_rate
                *
                0.30
            )

            +

            (
                quality_score
                *
                0.20
            )

        )


        # ====================================================
        # RESULT
        # ====================================================

        return {

            "supplier_id":
                supplier.id,

            "supplier_code":
                supplier.supplier_code,

            "supplier_name":
                supplier.supplier_name,

            "performance_data_available":
                True,

            "total_orders":
                total_orders,

            "on_time_orders":
                on_time_orders,

            "late_orders":
                late_orders,

            "ordered_quantity":
                ordered_quantity,

            "received_quantity":
                received_quantity,

            "defective_quantity":
                defective_quantity,

            "on_time_delivery_rate":
                round(
                    on_time_delivery_rate,
                    2
                ),

            "fill_rate":
                round(
                    fill_rate,
                    2
                ),

            "defect_rate":
                round(
                    defect_rate,
                    2
                ),

            "average_delay_days":
                round(
                    average_delay_days,
                    2
                ),

            "quality_score":
                round(
                    quality_score,
                    2
                ),

            "quality_source":
                quality_source,

            "baseline_quality_rating":
                supplier.quality_rating,

            "baseline_reliability_score":
                baseline_reliability_score,

            "reliability_score":
                round(
                    reliability_score,
                    2
                )

        }


    # ========================================================
    # CALCULATE ALL SUPPLIERS
    # ========================================================

    @staticmethod
    def calculate_all_suppliers(
        db: Session
    ):

        suppliers = (

            db.query(
                Supplier
            )

            .filter(
                Supplier.is_active
                == True
            )

            .all()

        )


        results = []


        for supplier in suppliers:

            result = (

                SupplierPerformanceService
                .calculate_supplier_performance(

                    db,

                    supplier.id

                )

            )


            results.append(
                result
            )


        # ----------------------------------------------------
        # Highest operational reliability first
        # ----------------------------------------------------

        results.sort(

            key=lambda item:
                item[
                    "reliability_score"
                ],

            reverse=True

        )


        return results