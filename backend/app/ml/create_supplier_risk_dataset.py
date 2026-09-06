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
    "supplier_risk_dataset.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# CREATE DATASET
# ============================================================

def create_supplier_risk_dataset():

    db = SessionLocal()

    try:

        print("=" * 70)
        print("CREATING SUPPLIER RISK DATASET")
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
        # Process each supplier
        # ----------------------------------------------------

        for supplier in suppliers:

            records = (
                db.query(SupplierPerformance)
                .filter(
                    SupplierPerformance.supplier_id
                    == supplier.id
                )
                .all()
            )


            if not records:

                print(
                    f"Skipping {supplier.supplier_code} "
                    f"- no performance records."
                )

                continue


            # ------------------------------------------------
            # Aggregate historical performance
            # ------------------------------------------------

            total_orders = sum(
                r.total_orders
                for r in records
            )

            on_time_orders = sum(
                r.on_time_orders
                for r in records
            )

            late_orders = sum(
                r.late_orders
                for r in records
            )

            ordered_quantity = sum(
                r.ordered_quantity
                for r in records
            )

            received_quantity = sum(
                r.received_quantity
                for r in records
            )

            defective_quantity = sum(
                r.defective_quantity
                for r in records
            )


            # ------------------------------------------------
            # Performance metrics
            # ------------------------------------------------

            if total_orders > 0:

                on_time_delivery_rate = (
                    on_time_orders
                    / total_orders
                ) * 100

            else:

                on_time_delivery_rate = 0


            if ordered_quantity > 0:

                fill_rate = (
                    received_quantity
                    / ordered_quantity
                ) * 100

            else:

                fill_rate = 0


            if received_quantity > 0:

                defect_rate = (
                    defective_quantity
                    / received_quantity
                ) * 100

            else:

                defect_rate = 0


            # ------------------------------------------------
            # Average delay
            # ------------------------------------------------

            total_delay = sum(

                r.average_delay_days
                * r.late_orders

                for r in records

            )


            if late_orders > 0:

                average_delay_days = (
                    total_delay
                    / late_orders
                )

            else:

                average_delay_days = 0


            # ------------------------------------------------
            # Reliability score
            # ------------------------------------------------

            quality_score = max(
                0,
                100 - defect_rate
            )


            reliability_score = (

                (on_time_delivery_rate * 0.50)

                +

                (fill_rate * 0.30)

                +

                (quality_score * 0.20)

            )


            # ------------------------------------------------
            # Risk label
            #
            # This is our initial business-rule label.
            #
            # Later XGBoost will learn the relationship
            # between supplier features and risk.
            # ------------------------------------------------

            if reliability_score >= 90:

                risk_level = "LOW"

            elif reliability_score >= 75:

                risk_level = "MEDIUM"

            else:

                risk_level = "HIGH"


            # ------------------------------------------------
            # Create row
            # ------------------------------------------------

            dataset.append({

                "supplier_id":
                    supplier.id,

                "supplier_code":
                    supplier.supplier_code,

                "supplier_name":
                    supplier.supplier_name,

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

                "reliability_score":
                    round(
                        reliability_score,
                        2
                    ),

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
                "No supplier performance data available."
            )


        # ----------------------------------------------------
        # Save dataset
        # ----------------------------------------------------

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )


        # ----------------------------------------------------
        # Display information
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


        print("\nDataset preview:")

        print(
            df.head()
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

    create_supplier_risk_dataset()