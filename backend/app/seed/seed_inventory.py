import random
from datetime import datetime

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Component,
    Inventory
)


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)


WAREHOUSES = [
    "Chennai",
    "Hosur",
    "Coimbatore",
    "Chengalpattu"
]


# ============================================================
# INVENTORY GENERATION RULES
# ============================================================

INVENTORY_RANGES = {

    "CRITICAL": {
        "min": 500,
        "max": 8000
    },

    "HIGH": {
        "min": 300,
        "max": 5000
    },

    "MEDIUM": {
        "min": 200,
        "max": 3000
    }

}


# ============================================================
# INVENTORY STATUS FUNCTION
# ============================================================

def calculate_inventory_status(
    available_stock,
    safety_stock,
    reorder_level
):

    if available_stock <= 0:

        return "OUT_OF_STOCK"

    elif available_stock <= safety_stock:

        return "CRITICAL"

    elif available_stock <= reorder_level:

        return "REORDER_REQUIRED"

    else:

        return "NORMAL"


# ============================================================
# GENERATE STOCK
# ============================================================

def generate_stock(criticality):

    stock_range = INVENTORY_RANGES[criticality]

    current_stock = random.randint(
        stock_range["min"],
        stock_range["max"]
    )

    reserved_percentage = random.uniform(
        0.05,
        0.30
    )

    reserved_stock = round(
        current_stock * reserved_percentage
    )

    available_stock = max(
        current_stock - reserved_stock,
        0
    )

    return (
        current_stock,
        reserved_stock,
        available_stock
    )


# ============================================================
# SEED INVENTORY
# ============================================================

def seed_inventory():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("INVENTORY DATA SEEDING")
        print("=" * 60)


        # ----------------------------------------------------
        # Clear existing inventory
        # ----------------------------------------------------

        print("\nClearing existing inventory...")

        db.query(Inventory).delete()

        db.commit()


        # ----------------------------------------------------
        # Load components
        # ----------------------------------------------------

        components = (
            db.query(Component)
            .filter(
                Component.is_active == True
            )
            .all()
        )


        print(
            f"Active components found: {len(components)}"
        )


        # ----------------------------------------------------
        # Create inventory
        # ----------------------------------------------------

        total_records = 0


        for component in components:

            for warehouse in WAREHOUSES:

                # --------------------------------------------
                # Generate stock
                # --------------------------------------------

                (
                    current_stock,
                    reserved_stock,
                    available_stock
                ) = generate_stock(
                    component.criticality
                )


                # --------------------------------------------
                # Safety stock
                # --------------------------------------------

                safety_stock = round(
                    current_stock * random.uniform(
                        0.10,
                        0.20
                    )
                )


                # --------------------------------------------
                # Reorder level
                # --------------------------------------------

                reorder_level = round(
                    current_stock * random.uniform(
                        0.20,
                        0.35
                    )
                )


                # --------------------------------------------
                # Status
                # --------------------------------------------

                inventory_status = calculate_inventory_status(
                    available_stock,
                    safety_stock,
                    reorder_level
                )


                # --------------------------------------------
                # Create inventory record
                # --------------------------------------------

                inventory = Inventory(

                    component_id=component.id,

                    warehouse=warehouse,

                    current_stock=current_stock,

                    reserved_stock=reserved_stock,

                    available_stock=available_stock,

                    safety_stock=safety_stock,

                    reorder_level=reorder_level,

                    inventory_status=inventory_status,

                    last_updated=datetime.utcnow()
                )


                db.add(inventory)

                total_records += 1


        db.commit()


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print("\nInventory seeding completed.")

        print(
            f"Total inventory records: {total_records}"
        )

        print(
            f"Components: {len(components)}"
        )

        print(
            f"Warehouses: {len(WAREHOUSES)}"
        )

        print(
            f"Expected records: "
            f"{len(components) * len(WAREHOUSES)}"
        )

        print("\nWarehouses:")

        for warehouse in WAREHOUSES:

            print(
                f"  - {warehouse}"
            )

        print("=" * 60)


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

    seed_inventory()