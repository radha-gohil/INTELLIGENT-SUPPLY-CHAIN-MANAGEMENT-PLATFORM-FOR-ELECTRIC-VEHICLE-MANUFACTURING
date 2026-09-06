from sqlalchemy.orm import Session

from backend.app.models import (
    Supplier,
    SupplierPerformance
)


class SupplierPerformanceService:

    # ========================================================
    # QUALITY RATING -> 0-100
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
        # Example:
        #
        # 4.5 / 5
        # becomes
        # 90 / 100
        # ----------------------------------------------------

        if 0 <= rating <= 5:

            return (
                rating / 5
            ) * 100


        # ----------------------------------------------------
        # Defensive support if CSV already contains percentage
        #
        # Example:
        # 90 -> 90
        # ----------------------------------------------------

        if 5 < rating <= 100:

            return rating


        return None


    # ========================================================
    # NORMALIZE RELIABILITY SCORE
    # ========================================================

    @staticmethod
    def normalize_reliability_score(
        reliability_score
    ):

        if reliability_score is None:
            return None

        try:

            score = float(
                reliability_score
            )

        except (
            TypeError,
            ValueError
        ):

            return None


        # ----------------------------------------------------
        # Support decimal reliability
        #
        # Example:
        # 0.92 -> 92
        # ----------------------------------------------------

        if 0 <= score <= 1:

            return score * 100


        # ----------------------------------------------------
        # Already percentage
        #
        # Example:
        # 92 -> 92
        # ----------------------------------------------------

        if 1 < score <= 100:

            return score


        return None


    # ========================================================
    # SAFE NUMERIC VALUE
    # ========================================================

    @staticmethod
    def safe_number(
        value,
        default=0.0
    ):

        if value is None:
            return default

        try:
            return float(value)

        except (
            TypeError,
            ValueError
        ):
            return default


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


        # ====================================================
        # MASTER / BASELINE DATA
        # ====================================================

        baseline_quality_score = (

            SupplierPerformanceService
            .quality_rating_to_score(
                supplier.quality_rating
            )

        )


        baseline_reliability_score = (

            SupplierPerformanceService
            .normalize_reliability_score(
                supplier.baseline_reliability_score
            )

        )


        # ====================================================
        # HISTORICAL PERFORMANCE DATA
        # ====================================================

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
        # NO HISTORICAL DATA
        # ====================================================

        if not records:

            quality_score = (

                baseline_quality_score

                if baseline_quality_score
                is not None

                else 0.0

            )


            reliability_score = (

                baseline_reliability_score

                if baseline_reliability_score
                is not None

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
                    (
                        round(
                            baseline_reliability_score,
                            2
                        )

                        if baseline_reliability_score
                        is not None

                        else None
                    ),

                "reliability_score":
                    round(
                        reliability_score,
                        2
                    ),

                "reliability_source":
                    (
                        "MASTER_BASELINE"

                        if baseline_reliability_score
                        is not None

                        else "UNAVAILABLE"
                    )

            }


        # ====================================================
        # AGGREGATE HISTORICAL DATA
        # ====================================================

        total_orders = sum(

            SupplierPerformanceService
            .safe_number(
                record.total_orders
            )

            for record
            in records

        )


        on_time_orders = sum(

            SupplierPerformanceService
            .safe_number(
                record.on_time_orders
            )

            for record
            in records

        )


        late_orders = sum(

            SupplierPerformanceService
            .safe_number(
                record.late_orders
            )

            for record
            in records

        )


        ordered_quantity = sum(

            SupplierPerformanceService
            .safe_number(
                record.ordered_quantity
            )

            for record
            in records

        )


        received_quantity = sum(

            SupplierPerformanceService
            .safe_number(
                record.received_quantity
            )

            for record
            in records

        )


        defective_quantity = sum(

            SupplierPerformanceService
            .safe_number(
                record.defective_quantity
            )

            for record
            in records

        )


        # ====================================================
        # HISTORICAL DATA ACTUALLY AVAILABLE?
        # ====================================================

        performance_data_available = (

            total_orders > 0
            or ordered_quantity > 0

        )


        # ====================================================
        # AVERAGE DELAY
        # ====================================================

        weighted_delay = sum(

            (
                SupplierPerformanceService
                .safe_number(
                    record.average_delay_days
                )

                *

                SupplierPerformanceService
                .safe_number(
                    record.late_orders
                )
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


        # Keep percentage valid
        on_time_delivery_rate = max(
            0.0,
            min(
                100.0,
                on_time_delivery_rate
            )
        )


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


        fill_rate = max(
            0.0,
            min(
                100.0,
                fill_rate
            )
        )


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


        defect_rate = max(
            0.0,
            min(
                100.0,
                defect_rate
            )
        )


        # ====================================================
        # QUALITY SCORE
        # ====================================================
        #
        # IMPORTANT:
        #
        # purchase_orders.csv does NOT contain a defect column.
        #
        # Therefore zero defective quantity imported from that
        # dataset must NOT automatically mean perfect quality.
        #
        # We use supplier_master quality_rating unless actual
        # defect quantities exist.
        # ====================================================

        actual_defect_information_available = (

            defective_quantity > 0

        )


        if actual_defect_information_available:

            quality_score = max(

                0.0,

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

            quality_score = 0.0

            quality_source = (
                "UNAVAILABLE"
            )


        # ====================================================
        # OPERATIONAL RELIABILITY
        # ====================================================
        #
        # 50% On-Time Delivery
        # 30% Fill Rate
        # 20% Quality
        # ====================================================

        if performance_data_available:

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

            reliability_source = (
                "HISTORICAL_PERFORMANCE"
            )


        elif baseline_reliability_score is not None:

            reliability_score = (
                baseline_reliability_score
            )

            reliability_source = (
                "MASTER_BASELINE"
            )


        else:

            reliability_score = 0.0

            reliability_source = (
                "UNAVAILABLE"
            )


        reliability_score = max(
            0.0,
            min(
                100.0,
                reliability_score
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
                performance_data_available,

            "total_orders":
                int(total_orders),

            "on_time_orders":
                int(on_time_orders),

            "late_orders":
                int(late_orders),

            "ordered_quantity":
                round(
                    ordered_quantity,
                    2
                ),

            "received_quantity":
                round(
                    received_quantity,
                    2
                ),

            "defective_quantity":
                round(
                    defective_quantity,
                    2
                ),

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
                (
                    round(
                        baseline_reliability_score,
                        2
                    )

                    if baseline_reliability_score
                    is not None

                    else None
                ),

            "reliability_score":
                round(
                    reliability_score,
                    2
                ),

            "reliability_source":
                reliability_source

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

            .order_by(
                Supplier.id
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