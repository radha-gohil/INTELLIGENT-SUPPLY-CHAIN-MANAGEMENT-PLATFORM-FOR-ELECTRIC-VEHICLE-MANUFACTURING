from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Component,
    Inventory
)

from backend.app.service.stock_movement_service import (
    StockMovementService
)


# ============================================================
# TEST STOCK MOVEMENT
# ============================================================

def test_stock_movement():

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Get first component
        # ----------------------------------------------------

        component = (
            db.query(Component)
            .filter(
                Component.is_active == True
            )
            .first()
        )


        if component is None:

            raise ValueError(
                "No active component found."
            )


        print(
            f"\nComponent: "
            f"{component.part_id} - "
            f"{component.part_name}"
        )


        # ----------------------------------------------------
        # Get Chennai inventory
        # ----------------------------------------------------

        inventory = (

            db.query(Inventory)

            .filter(
                Inventory.component_id
                == component.id,

                Inventory.warehouse
                == "Chennai"
            )

            .first()
        )


        if inventory is None:

            raise ValueError(
                "Chennai inventory not found."
            )


        print("\nBEFORE RECEIPT")

        print(
            "Current Stock:",
            inventory.current_stock
        )

        print(
            "Available Stock:",
            inventory.available_stock
        )

        print(
            "Status:",
            inventory.inventory_status
        )


        # ----------------------------------------------------
        # Receipt
        # ----------------------------------------------------

        updated_inventory = (

            StockMovementService.receive_stock(

                db=db,

                component_id=component.id,

                warehouse="Chennai",

                quantity=100,

                reference_id="TEST-PO-001"

            )
        )


        print("\nAFTER RECEIPT +100")

        print(
            "Current Stock:",
            updated_inventory.current_stock
        )

        print(
            "Available Stock:",
            updated_inventory.available_stock
        )

        print(
            "Status:",
            updated_inventory.inventory_status
        )


        # ----------------------------------------------------
        # Issue
        # ----------------------------------------------------

        updated_inventory = (

            StockMovementService.issue_stock(

                db=db,

                component_id=component.id,

                warehouse="Chennai",

                quantity=50,

                reference_id="TEST-ISSUE-001"

            )
        )


        print("\nAFTER ISSUE -50")

        print(
            "Current Stock:",
            updated_inventory.current_stock
        )

        print(
            "Available Stock:",
            updated_inventory.available_stock
        )

        print(
            "Status:",
            updated_inventory.inventory_status
        )


        print("\nTEST COMPLETED SUCCESSFULLY.")


    except Exception as e:

        print("\nTEST FAILED:")

        print(e)

        raise


    finally:

        db.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_stock_movement()