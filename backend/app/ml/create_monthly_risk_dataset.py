import os

import pandas as pd

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Supplier,
    SupplierPerformance
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
# CALCULATE RISK
# ============================================================

def calculate_risk(
    on_time_delivery_rate,
    fill_rate,
    defect_rate,
    average_delay_days
):

    # --------------------------------------------------------
    # Quality score
    # --------------------------------------------------------

    quality_score = max(
        0,
        100 - (defect_rate * 10)
    )


    # --------------------------------------------------------
    # Delay score
    #
    # 0 days = 100
    # Increasing delay reduces score
    # --------------------------------------------------------

    delay_score = max(
        0,
        100 - (average_delay_days * 10)
    )


    # --------------------------------------------------------
    # Overall operational score
    # --------------------------------------------------------

    operational_score = (

        (on_time_delivery_rate * 0.40)

        +

        (fill_rate * 0.25)

        +

        (quality_score * 0.20)

        +

        (delay_score * 0.15)

    )


    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    if operational_score >= 85:

        risk_level = "LOW"

    elif operational_score >= 70:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"


    return (
        round(operational_score, 2),
        risk_level
    )


# ============================================================
# CREATE TRAINING DATASET
# ============================================================

def create_monthly_risk_dataset():

    db = SessionLocal()

    try:

        print("=" * 70)
        print("CREATING MONTHLY SUPPLIER RISK TRAINING DATASET")
        print("=" * 70)


        # ----------------------------------------------------
        # Get suppliers
        # ----------------------------------------------------

        suppliers = (
            db.query(Supplier)
            .filter(
                Supplier.is_active == True
            )
            .all()
        )


        if not suppliers:

            raise ValueError(
                "No active suppliers found."
            )


        dataset = []


        # ----------------------------------------------------
        # Process supplier performance records
        # ----------------------------------------------------

        for supplier in suppliers:

            records = (

                db.query(SupplierPerformance)

                .filter(
                    SupplierPerformance.supplier_id
                    == supplier.id
                )

                .order_by(
                    SupplierPerformance.performance_date
                )

                .all()

            )


            if not records:

                print(
                    f"Skipping "
                    f"{supplier.supplier_code} "
                    f"- no performance records."
                )

                continue


            for record in records:

                # ------------------------------------------------
                # Basic values
                # ------------------------------------------------

                total_orders = (
                    record.total_orders
                )

                on_time_orders = (
                    record.on_time_orders
                )

                late_orders = (
                    record.late_orders
                )

                ordered_quantity = (
                    record.ordered_quantity
                )

                received_quantity = (
                    record.received_quantity
                )

                defective_quantity = (
                    record.defective_quantity
                )


                # ------------------------------------------------
                # On-time delivery rate
                # ------------------------------------------------

                if total_orders > 0:

                    on_time_delivery_rate = (

                        on_time_orders
                        / total_orders

                    ) * 100

                else:

                    on_time_delivery_rate = 0.0


                # ------------------------------------------------
                # Fill rate
                # ------------------------------------------------

                if ordered_quantity > 0:

                    fill_rate = (

                        received_quantity
                        / ordered_quantity

                    ) * 100

                else:

                    fill_rate = 0.0


                # ------------------------------------------------
                # Defect rate
                # ------------------------------------------------

                if received_quantity > 0:

                    defect_rate = (

                        defective_quantity
                        / received_quantity

                    ) * 100

                else:

                    defect_rate = 0.0


                # ------------------------------------------------
                # Delay
                # ------------------------------------------------

                average_delay_days = (

                    record.average_delay_days

                    if record.average_delay_days
                    is not None

                    else 0.0

                )


                # ------------------------------------------------
                # Calculate operational score
                # ------------------------------------------------

                operational_score, risk_level = (

                    calculate_risk(

                        on_time_delivery_rate,

                        fill_rate,

                        defect_rate,

                        average_delay_days

                    )

                )


                # ------------------------------------------------
                # Create dataset row
                # ------------------------------------------------

                dataset.append({

                    "supplier_id":
                        supplier.id,

                    "supplier_code":
                        supplier.supplier_code,

                    "component_id":
                        record.component_id,

                    "performance_date":
                        record.performance_date,

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

                    "operational_score":
                        operational_score,

                    "risk_level":
                        risk_level

                })


        # ----------------------------------------------------
        # Convert to DataFrame
        # ----------------------------------------------------

        df = pd.DataFrame(
            dataset
        )


        if df.empty:

            raise ValueError(
                "Training dataset is empty."
            )


        # ----------------------------------------------------
        # Sort dataset
        # ----------------------------------------------------

        df = df.sort_values(
            by=[
                "supplier_id",
                "performance_date"
            ]
        )


        # ----------------------------------------------------
        # Save dataset
        # ----------------------------------------------------

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print("\nDataset created successfully.")

        print(
            f"Location: {OUTPUT_FILE}"
        )

        print(
            f"Rows: {len(df)}"
        )

        print(
            f"Columns: {len(df.columns)}"
        )


        print("\nRisk distribution:")

        print(
            df["risk_level"]
            .value_counts()
        )


        print("\nSupplier distribution:")

        print(
            df["supplier_code"]
            .value_counts()
        )


        print("\nDataset preview:")

        print(
            df.head(10)
            .to_string(
                index=False
            )
        )


        print("=" * 70)


    except Exception as e:

        db.rollback()

        print("\nERROR:")
        print(e)

        raise


    finally:

        db.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_monthly_risk_dataset()