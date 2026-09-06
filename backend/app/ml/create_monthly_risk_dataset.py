import os

import pandas as pd

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Supplier,
    SupplierPerformance
)

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
)


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = "data/ml"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "supplier_risk_training_dataset.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# HELPERS
# ============================================================

def safe_float(
    value,
    default=0.0
):

    if value is None:

        return default

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return default


def clamp(
    value,
    minimum=0.0,
    maximum=100.0
):

    return max(

        minimum,

        min(
            maximum,
            float(
                value
            )
        )

    )


# ============================================================
# CALCULATE RISK LABEL
# ============================================================
#
# Historical purchase-order data does NOT contain reliable
# product-defect measurements.
#
# Therefore:
#
# defective_quantity
# defect_rate
#
# are intentionally NOT used.
#
#
# Risk label is created using:
#
# 40% On-time delivery
# 25% Fill rate
# 20% Master quality
# 15% Delay performance
#
# ============================================================

def calculate_risk_label(

    on_time_delivery_rate,

    fill_rate,

    quality_score,

    average_delay_days

):

    # --------------------------------------------------------
    # Delay score
    #
    # 0 days delay     -> 100
    # 1 day delay      -> 90
    # 5 days delay     -> 50
    # 10+ days delay   -> 0
    # --------------------------------------------------------

    delay_score = clamp(

        100.0

        -

        (
            max(
                0.0,
                average_delay_days
            )

            *

            10.0
        )

    )


    # --------------------------------------------------------
    # Operational score
    # --------------------------------------------------------

    operational_score = (

        (
            clamp(
                on_time_delivery_rate
            )

            *

            0.40
        )

        +

        (
            clamp(
                fill_rate
            )

            *

            0.25
        )

        +

        (
            clamp(
                quality_score
            )

            *

            0.20
        )

        +

        (
            delay_score

            *

            0.15
        )

    )


    # --------------------------------------------------------
    # Risk category
    # --------------------------------------------------------

    if operational_score >= 85:

        risk_level = "LOW"

    elif operational_score >= 70:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"


    return (

        round(
            operational_score,
            2
        ),

        risk_level

    )


# ============================================================
# CREATE TRAINING DATASET
# ============================================================

def create_monthly_risk_dataset():

    db = SessionLocal()

    try:

        print(
            "=" * 70
        )

        print(
            "CREATING SUPPLIER RISK TRAINING DATASET"
        )

        print(
            "=" * 70
        )


        # ====================================================
        # ACTIVE SUPPLIERS
        # ====================================================

        suppliers = (

            db.query(
                Supplier
            )

            .filter(
                Supplier.is_active
                ==
                True
            )

            .order_by(
                Supplier.id
            )

            .all()

        )


        if not suppliers:

            raise ValueError(
                "No active suppliers found."
            )


        dataset = []


        # ====================================================
        # PROCESS EACH SUPPLIER
        # ====================================================

        for supplier in suppliers:

            performance_records = (

                db.query(
                    SupplierPerformance
                )

                .filter(

                    SupplierPerformance.supplier_id
                    ==
                    supplier.id

                )

                .order_by(

                    SupplierPerformance.performance_date,

                    SupplierPerformance.component_id

                )

                .all()

            )


            if not performance_records:

                print(

                    f"Skipping "
                    f"{supplier.supplier_code} "
                    f"- no performance records."

                )

                continue


            # =================================================
            # MASTER QUALITY
            #
            # Convert:
            #
            # 4.5 / 5 -> 90 / 100
            # =================================================

            quality_score = (

                SupplierPerformanceService
                .quality_rating_to_score(

                    supplier.quality_rating

                )

            )


            if quality_score is None:

                # Neutral fallback
                quality_score = 50.0


            # =================================================
            # BASELINE RELIABILITY
            #
            # Supports:
            #
            # 0.92 -> 92
            # 92   -> 92
            # =================================================

            baseline_reliability_score = (

                SupplierPerformanceService
                .normalize_reliability_score(

                    supplier
                    .baseline_reliability_score

                )

            )


            if baseline_reliability_score is None:

                # Neutral fallback
                baseline_reliability_score = 50.0


            # =================================================
            # ONE DATASET ROW PER PERFORMANCE RECORD
            # =================================================

            for record in performance_records:

                # ------------------------------------------------
                # Historical values
                # ------------------------------------------------

                total_orders = safe_float(
                    record.total_orders
                )


                on_time_orders = safe_float(
                    record.on_time_orders
                )


                late_orders = safe_float(
                    record.late_orders
                )


                ordered_quantity = safe_float(
                    record.ordered_quantity
                )


                received_quantity = safe_float(
                    record.received_quantity
                )


                average_delay_days = max(

                    0.0,

                    safe_float(
                        record.average_delay_days
                    )

                )


                # =================================================
                # ON-TIME DELIVERY RATE
                # =================================================

                if total_orders > 0:

                    on_time_delivery_rate = (

                        on_time_orders
                        /
                        total_orders

                    ) * 100

                else:

                    on_time_delivery_rate = 0.0


                # =================================================
                # LATE ORDER RATE
                # =================================================

                if total_orders > 0:

                    late_order_rate = (

                        late_orders
                        /
                        total_orders

                    ) * 100

                else:

                    late_order_rate = 0.0


                # =================================================
                # FILL RATE
                # =================================================

                if ordered_quantity > 0:

                    fill_rate = (

                        received_quantity
                        /
                        ordered_quantity

                    ) * 100

                else:

                    fill_rate = 0.0


                # ------------------------------------------------
                # Keep percentages valid
                # ------------------------------------------------

                on_time_delivery_rate = clamp(
                    on_time_delivery_rate
                )


                late_order_rate = clamp(
                    late_order_rate
                )


                fill_rate = clamp(
                    fill_rate
                )


                # =================================================
                # CREATE TARGET
                # =================================================

                (
                    operational_score,

                    risk_level

                ) = calculate_risk_label(

                    on_time_delivery_rate,

                    fill_rate,

                    quality_score,

                    average_delay_days

                )


                # =================================================
                # TRAINING ROW
                # =================================================

                dataset.append({

                    # --------------------------------------------
                    # Reference information
                    # --------------------------------------------

                    "supplier_id":
                        supplier.id,

                    "supplier_code":
                        supplier.supplier_code,

                    "component_id":
                        record.component_id,

                    "performance_date":
                        record.performance_date,


                    # --------------------------------------------
                    # MODEL FEATURES
                    # --------------------------------------------

                    "total_orders":
                        round(
                            total_orders,
                            2
                        ),

                    "late_order_rate":
                        round(
                            late_order_rate,
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

                    "baseline_reliability_score":
                        round(
                            baseline_reliability_score,
                            2
                        ),


                    # --------------------------------------------
                    # TARGET SUPPORT
                    # --------------------------------------------

                    "operational_score":
                        operational_score,

                    "risk_level":
                        risk_level

                })


        # ====================================================
        # CREATE DATAFRAME
        # ====================================================

        df = pd.DataFrame(
            dataset
        )


        if df.empty:

            raise ValueError(
                "Training dataset is empty."
            )


        # ====================================================
        # VALIDATE NUMERIC FEATURES
        # ====================================================

        feature_columns = [

            "total_orders",

            "late_order_rate",

            "on_time_delivery_rate",

            "fill_rate",

            "average_delay_days",

            "quality_score",

            "baseline_reliability_score"

        ]


        for column in feature_columns:

            df[
                column
            ] = pd.to_numeric(

                df[
                    column
                ],

                errors="coerce"

            )


        # ----------------------------------------------------
        # Remove invalid rows
        # ----------------------------------------------------

        df = df.dropna(

            subset=(

                feature_columns

                +

                [
                    "risk_level"
                ]

            )

        )


        if df.empty:

            raise ValueError(

                "No valid training rows remain "
                "after data validation."

            )


        # ====================================================
        # SORT DATA
        # ====================================================

        df = df.sort_values(

            by=[

                "supplier_id",

                "performance_date",

                "component_id"

            ]

        )


        # ====================================================
        # SAVE DATASET
        # ====================================================

        df.to_csv(

            OUTPUT_FILE,

            index=False

        )


        # ====================================================
        # SUMMARY
        # ====================================================

        print(
            "\nDataset created successfully."
        )


        print(
            f"Location: {OUTPUT_FILE}"
        )


        print(
            f"Rows: {len(df)}"
        )


        print(
            f"Columns: {len(df.columns)}"
        )


        print(
            "\nRisk distribution:"
        )


        print(

            df[
                "risk_level"
            ]
            .value_counts()

        )


        print(
            "\nFeatures used:"
        )


        for column in feature_columns:

            print(
                f"- {column}"
            )


        print(
            "\nDataset preview:"
        )


        print(

            df
            .head(
                10
            )
            .to_string(
                index=False
            )

        )


        print(
            "=" * 70
        )


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    create_monthly_risk_dataset()