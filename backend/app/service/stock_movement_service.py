from datetime import (
    datetime,
    timezone
)

from sqlalchemy.orm import Session

from backend.app.models import (
    Inventory,
    InventoryTransaction,
    Component
)


# ============================================================
# UTC TIME
# ============================================================

def utc_now():

    return (

        datetime
        .now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )

    )


# ============================================================
# STOCK MOVEMENT SERVICE
# ============================================================

class StockMovementService:

    # ========================================================
    # FIND COMPONENT
    # ========================================================

    @staticmethod
    def get_component(
        db: Session,
        component_id: int
    ):

        return (

            db.query(Component)

            .filter(
                Component.id
                == component_id
            )

            .first()

        )


    # ========================================================
    # FIND INVENTORY
    # ========================================================

    @staticmethod
    def get_inventory(
        db: Session,
        component_id: int,
        warehouse: str
    ):

        return (

            db.query(Inventory)

            .filter(
                Inventory.component_id
                == component_id,

                Inventory.warehouse
                == warehouse
            )

            .first()

        )


    # ========================================================
    # CALCULATE STATUS
    # ========================================================

    @staticmethod
    def calculate_status(
        available_stock: float,
        safety_stock: float,
        reorder_level: float
    ):

        if available_stock <= 0:

            return "OUT_OF_STOCK"


        if available_stock <= safety_stock:

            return "CRITICAL"


        if available_stock <= reorder_level:

            return "REORDER_REQUIRED"


        return "NORMAL"


    # ========================================================
    # RECALCULATE INVENTORY
    # ========================================================

    @staticmethod
    def recalculate_inventory(
        inventory: Inventory
    ):

        inventory.available_stock = max(

            float(
                inventory.current_stock
                or 0
            )

            -

            float(
                inventory.reserved_stock
                or 0
            ),

            0

        )


        inventory.inventory_status = (

            StockMovementService
            .calculate_status(

                available_stock=(
                    inventory.available_stock
                ),

                safety_stock=float(
                    inventory.safety_stock
                    or 0
                ),

                reorder_level=float(
                    inventory.reorder_level
                    or 0
                )

            )

        )


        inventory.last_updated = (
            utc_now()
        )


    # ========================================================
    # VALIDATE COMPONENT
    # ========================================================

    @staticmethod
    def validate_component(
        db: Session,
        component_id: int
    ):

        component = (

            StockMovementService
            .get_component(

                db=db,

                component_id=(
                    component_id
                )

            )

        )


        if component is None:

            raise ValueError(
                "Component not found."
            )


        return component


    # ========================================================
    # RECEIVE STOCK
    # ========================================================

    @staticmethod
    def receive_stock(
        db: Session,
        component_id: int,
        warehouse: str,
        quantity: float,
        reference_id=None
    ):

        if quantity <= 0:

            raise ValueError(
                "Receipt quantity must be greater than 0."
            )


        StockMovementService.validate_component(

            db,
            component_id

        )


        inventory = (

            StockMovementService
            .get_inventory(

                db,
                component_id,
                warehouse

            )

        )


        if inventory is None:

            raise ValueError(
                "Inventory record not found."
            )


        inventory.current_stock = (

            float(
                inventory.current_stock
                or 0
            )

            +
            float(quantity)

        )


        StockMovementService.recalculate_inventory(
            inventory
        )


        transaction = InventoryTransaction(

            transaction_id=(

                StockMovementService
                .generate_transaction_id(
                    db
                )

            ),

            component_id=component_id,

            warehouse=warehouse,

            transaction_type="RECEIPT",

            quantity=quantity,

            reference_id=reference_id,

            transaction_date=utc_now(),

            created_at=utc_now()

        )


        db.add(transaction)

        db.commit()

        db.refresh(inventory)


        return inventory


    # ========================================================
    # ISSUE STOCK
    # ========================================================

    @staticmethod
    def issue_stock(
        db: Session,
        component_id: int,
        warehouse: str,
        quantity: float,
        reference_id=None
    ):

        if quantity <= 0:

            raise ValueError(
                "Issue quantity must be greater than 0."
            )


        StockMovementService.validate_component(

            db,
            component_id

        )


        inventory = (

            StockMovementService
            .get_inventory(

                db,
                component_id,
                warehouse

            )

        )


        if inventory is None:

            raise ValueError(
                "Inventory record not found."
            )


        if (
            float(
                inventory.available_stock
                or 0
            )
            <
            float(quantity)
        ):

            raise ValueError(

                "Insufficient available stock. "
                f"Available: "
                f"{inventory.available_stock}, "
                f"Requested: {quantity}"

            )


        inventory.current_stock = (

            float(
                inventory.current_stock
                or 0
            )

            -
            float(quantity)

        )


        StockMovementService.recalculate_inventory(
            inventory
        )


        transaction = InventoryTransaction(

            transaction_id=(

                StockMovementService
                .generate_transaction_id(
                    db
                )

            ),

            component_id=component_id,

            warehouse=warehouse,

            transaction_type="ISSUE",

            quantity=quantity,

            reference_id=reference_id,

            transaction_date=utc_now(),

            created_at=utc_now()

        )


        db.add(transaction)

        db.commit()

        db.refresh(inventory)


        return inventory


    # ========================================================
    # ADJUST STOCK
    # ========================================================

    @staticmethod
    def adjust_stock(
        db: Session,
        component_id: int,
        warehouse: str,
        quantity: float,
        reference_id=None
    ):

        if quantity == 0:

            raise ValueError(
                "Adjustment quantity cannot be zero."
            )


        StockMovementService.validate_component(

            db,
            component_id

        )


        inventory = (

            StockMovementService
            .get_inventory(

                db,
                component_id,
                warehouse

            )

        )


        if inventory is None:

            raise ValueError(
                "Inventory record not found."
            )


        new_stock = (

            float(
                inventory.current_stock
                or 0
            )

            +
            float(quantity)

        )


        if new_stock < 0:

            raise ValueError(
                "Adjustment would create negative stock."
            )


        inventory.current_stock = (
            new_stock
        )


        StockMovementService.recalculate_inventory(
            inventory
        )


        transaction = InventoryTransaction(

            transaction_id=(

                StockMovementService
                .generate_transaction_id(
                    db
                )

            ),

            component_id=component_id,

            warehouse=warehouse,

            transaction_type="ADJUSTMENT",

            quantity=quantity,

            reference_id=reference_id,

            transaction_date=utc_now(),

            created_at=utc_now()

        )


        db.add(transaction)

        db.commit()

        db.refresh(inventory)


        return inventory


    # ========================================================
    # TRANSFER STOCK
    # ========================================================

    @staticmethod
    def transfer_stock(
        db: Session,
        component_id: int,
        source_warehouse: str,
        destination_warehouse: str,
        quantity: float,
        reference_id=None
    ):

        if quantity <= 0:

            raise ValueError(
                "Transfer quantity must be greater than 0."
            )


        if (
            source_warehouse
            ==
            destination_warehouse
        ):

            raise ValueError(
                "Source and destination warehouses must be different."
            )


        StockMovementService.validate_component(

            db,
            component_id

        )


        source_inventory = (

            StockMovementService
            .get_inventory(

                db,
                component_id,
                source_warehouse

            )

        )


        destination_inventory = (

            StockMovementService
            .get_inventory(

                db,
                component_id,
                destination_warehouse

            )

        )


        if source_inventory is None:

            raise ValueError(
                "Source warehouse inventory not found."
            )


        if destination_inventory is None:

            raise ValueError(
                "Destination warehouse inventory not found."
            )


        if (
            float(
                source_inventory.available_stock
                or 0
            )
            <
            float(quantity)
        ):

            raise ValueError(

                "Insufficient stock at source warehouse. "
                f"Available: "
                f"{source_inventory.available_stock}, "
                f"Requested: {quantity}"

            )


        source_inventory.current_stock = (

            float(
                source_inventory.current_stock
                or 0
            )

            -
            float(quantity)

        )


        destination_inventory.current_stock = (

            float(
                destination_inventory.current_stock
                or 0
            )

            +
            float(quantity)

        )


        StockMovementService.recalculate_inventory(
            source_inventory
        )


        StockMovementService.recalculate_inventory(
            destination_inventory
        )


        # ----------------------------------------------------
        # IMPORTANT:
        # Generate different IDs for OUT and IN.
        # ----------------------------------------------------

        source_transaction_id = (

            StockMovementService
            .generate_transaction_id(

                db,
                offset=0

            )

        )


        destination_transaction_id = (

            StockMovementService
            .generate_transaction_id(

                db,
                offset=1

            )

        )


        source_transaction = InventoryTransaction(

            transaction_id=(
                source_transaction_id
            ),

            component_id=component_id,

            warehouse=source_warehouse,

            transaction_type="TRANSFER_OUT",

            quantity=quantity,

            reference_id=reference_id,

            transaction_date=utc_now(),

            created_at=utc_now()

        )


        destination_transaction = InventoryTransaction(

            transaction_id=(
                destination_transaction_id
            ),

            component_id=component_id,

            warehouse=destination_warehouse,

            transaction_type="TRANSFER_IN",

            quantity=quantity,

            reference_id=reference_id,

            transaction_date=utc_now(),

            created_at=utc_now()

        )


        db.add(
            source_transaction
        )


        db.add(
            destination_transaction
        )


        db.commit()


        db.refresh(
            source_inventory
        )


        db.refresh(
            destination_inventory
        )


        return {

            "source":
                source_inventory,

            "destination":
                destination_inventory

        }


    # ========================================================
    # GENERATE TRANSACTION ID
    # ========================================================

    @staticmethod
    def generate_transaction_id(
        db: Session,
        offset: int = 0
    ):

        last_transaction = (

            db.query(
                InventoryTransaction
            )

            .order_by(
                InventoryTransaction
                .id
                .desc()
            )

            .first()

        )


        if last_transaction is None:

            next_number = (
                1 + offset
            )

        else:

            next_number = (

                last_transaction.id
                +
                1
                +
                offset

            )


        return (
            f"TXN{next_number:06d}"
        )