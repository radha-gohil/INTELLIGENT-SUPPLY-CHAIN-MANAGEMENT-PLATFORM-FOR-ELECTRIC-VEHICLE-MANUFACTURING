import random
from datetime import date

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Supplier,
    SupplierComponent,
    SupplierPerformance
)


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)


# ============================================================
# SUPPLIER PERFORMANCE PROFILES
# ============================================================

SUPPLIER_PROFILES = {

    "SUP001": {
        "on_time_range": (0.92, 0.98),
        "fill_rate_range": (0.97, 1.00),
        "defect_rate_range": (0.002, 0.012),
        "delay_range": (0.5, 2.0)
    },

    "SUP002": {
        "on_time_range": (0.82, 0.92),
        "fill_rate_range": (0.94, 0.99),
        "defect_rate_range": (0.005, 0.020),
        "delay_range": (1.5, 4.0)
    },

    "SUP003": {
        "on_time_range": (0.94, 0.99),
        "fill_rate_range": (0.98, 1.00),
        "defect_rate_range": (0.001, 0.010),
        "delay_range": (0.3, 1.5)
    },

    "SUP004": {
        "on_time_range": (0.70, 0.85),
        "fill_rate_range": (0.88, 0.96),
        "defect_rate_range": (0.015, 0.045),
        "delay_range": (3.0, 7.0)
    },

    "SUP005": {
        "on_time_range": (0.86, 0.95),
        "fill_rate_range": (0.94, 0.99),
        "defect_rate_range": (0.008, 0.025),
        "delay_range": (1.0, 3.5)
    },

    "SUP006": {
        "on_time_range": (0.75, 0.88),
        "fill_rate_range": (0.90, 0.97),
        "defect_rate_range": (0.010, 0.035),
        "delay_range": (2.5, 6.0)
    },

    "SUP007": {
        "on_time_range": (0.90, 0.97),
        "fill_rate_range": (0.96, 1.00),
        "defect_rate_range": (0.003, 0.015),
        "delay_range": (0.5, 2.5)
    },

    "SUP008": {
        "on_time_range": (0.80, 0.91),
        "fill_rate_range": (0.91, 0.98),
        "defect_rate_range": (0.010, 0.030),
        "delay_range": (2.0, 5.0)
    }
}


# ============================================================
# MONTHS TO GENERATE
# ============================================================

MONTHS = [

    date(2025, 1, 1),
    date(2025, 2, 1),
    date(2025, 3, 1),
    date(2025, 4, 1),
    date(2025, 5, 1),
    date(2025, 6, 1),
    date(2025, 7, 1),
    date(2025, 8, 1),
    date(2025, 9, 1),
    date(2025, 10, 1),
    date(2025, 11, 1),
    date(2025, 12, 1),

    date(2026, 1, 1),
    date(2026, 2, 1),
    date(2026, 3, 1),
    date(2026, 4, 1),
    date(2026, 5, 1),
    date(2026, 6, 1),
    date(2026, 7, 1),
    date(2026, 8, 1)
]


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_profile(supplier_code):

    if supplier_code in SUPPLIER_PROFILES:

        return SUPPLIER_PROFILES[supplier_code]

    return {
        "on_time_range": (0.80, 0.95),
        "fill_rate_range": (0.90, 0.99),
        "defect_rate_range": (0.005, 0.030),
        "delay_range": (1.0, 4.0)
    }


# ============================================================
# SEED FUNCTION
# ============================================================

def seed_supplier_performance():

    db = SessionLocal()

    try:

        print("=" * 70)
        print("SUPPLIER PERFORMANCE DATA SEEDING")
        print("=" * 70)


        # ----------------------------------------------------
        # Clear existing performance data
        # ----------------------------------------------------

        print("\nClearing existing supplier performance data...")

        db.query(SupplierPerformance).delete()

        db.commit()


        # ----------------------------------------------------
        # Load suppliers
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
                "No suppliers found."
            )


        print(
            f"Active suppliers found: {len(suppliers)}"
        )


        total_records = 0


        # ----------------------------------------------------
        # Generate supplier + component performance
        # ----------------------------------------------------

        for supplier in suppliers:

            profile = get_profile(
                supplier.supplier_code
            )


            # ------------------------------------------------
            # Find components supplied by this supplier
            # ------------------------------------------------

            supplier_components = (

                db.query(SupplierComponent)

                .filter(
                    SupplierComponent.supplier_id
                    == supplier.id
                )

                .all()
            )


            if not supplier_components:

                print(
                    f"WARNING: "
                    f"{supplier.supplier_code} "
                    f"has no component mappings."
                )

                continue


            for supplier_component in supplier_components:

                component_id = (
                    supplier_component.component_id
                )


                for performance_month in MONTHS:

                    # ----------------------------------------
                    # Number of orders in the month
                    # ----------------------------------------

                    total_orders = random.randint(
                        6,
                        20
                    )


                    # ----------------------------------------
                    # On-time delivery
                    # ----------------------------------------

                    on_time_rate = random.uniform(
                        profile["on_time_range"][0],
                        profile["on_time_range"][1]
                    )


                    on_time_orders = round(
                        total_orders
                        * on_time_rate
                    )


                    on_time_orders = min(
                        on_time_orders,
                        total_orders
                    )


                    late_orders = (
                        total_orders
                        - on_time_orders
                    )


                    # ----------------------------------------
                    # Ordered quantity
                    # ----------------------------------------

                    ordered_quantity = random.randint(
                        500,
                        5000
                    )


                    # ----------------------------------------
                    # Fill rate
                    # ----------------------------------------

                    fill_rate = random.uniform(
                        profile["fill_rate_range"][0],
                        profile["fill_rate_range"][1]
                    )


                    received_quantity = round(
                        ordered_quantity
                        * fill_rate
                    )


                    received_quantity = min(
                        received_quantity,
                        ordered_quantity
                    )


                    # ----------------------------------------
                    # Defect rate
                    # ----------------------------------------

                    defect_rate = random.uniform(
                        profile["defect_rate_range"][0],
                        profile["defect_rate_range"][1]
                    )


                    defective_quantity = round(
                        received_quantity
                        * defect_rate
                    )


                    # ----------------------------------------
                    # Average delay
                    # ----------------------------------------

                    if late_orders > 0:

                        average_delay_days = round(
                            random.uniform(
                                profile["delay_range"][0],
                                profile["delay_range"][1]
                            ),
                            2
                        )

                    else:

                        average_delay_days = 0.0


                    # ----------------------------------------
                    # Create performance record
                    # ----------------------------------------

                    performance = SupplierPerformance(

                        supplier_id=supplier.id,

                        component_id=component_id,

                        performance_date=performance_month,

                        total_orders=total_orders,

                        on_time_orders=on_time_orders,

                        late_orders=late_orders,

                        ordered_quantity=ordered_quantity,

                        received_quantity=received_quantity,

                        defective_quantity=defective_quantity,

                        average_delay_days=average_delay_days
                    )


                    db.add(
                        performance
                    )

                    total_records += 1


        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        db.commit()


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print("\nSupplier performance seeding completed.")

        print(
            f"Total records created: {total_records}"
        )

        print(
            f"Months generated: {len(MONTHS)}"
        )

        print(
            f"Suppliers: {len(suppliers)}"
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

    seed_supplier_performance()