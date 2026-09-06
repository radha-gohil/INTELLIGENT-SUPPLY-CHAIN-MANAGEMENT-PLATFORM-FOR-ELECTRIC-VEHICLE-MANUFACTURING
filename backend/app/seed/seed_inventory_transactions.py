import random

from datetime import datetime, timedelta

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Component,
    Inventory,
    InventoryTransaction
)


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)

TRANSACTION_COUNT = 5000

WAREHOUSES = [
    "Chennai",
    "Hosur",
    "Coimbatore",
    "Chengalpattu"
]

TRANSACTION_TYPES = [
    "RECEIPT",
    "ISSUE",
    "TRANSFER",
    "ADJUSTMENT"
]


# ============================================================
# TRANSACTION DATE RANGE
# ============================================================

START_DATE = datetime(2025, 1, 1)

END_DATE = datetime(2026, 8, 31)


# ============================================================
# GENERATE RANDOM DATE
# ============================================================

def generate_transaction_date():

    total_seconds = int(
        (END_DATE - START_DATE).total_seconds()
    )

    random_seconds = random.randint(
        0,
        total_seconds
    )

    return (
        START_DATE
        + timedelta(seconds=random_seconds)
    )


# ============================================================
# GENERATE REFERENCE ID
# ============================================================

def generate_reference_id(
    transaction_type,
    index
):

    if transaction_type == "RECEIPT":

        return f"PO{random.randint(1, 2000):05d}"

    elif transaction_type == "ISSUE":

        return f"ISS{random.randint(1, 3000):05d}"

    elif transaction_type == "TRANSFER":

        return f"TR{random.randint(1, 1500):05d}"

    else:

        return f"ADJ{random.randint(1, 1000):05d}"


# ============================================================
# GENERATE QUANTITY
# ============================================================

def generate_quantity(
    transaction_type,
    component
):

    criticality = component.criticality


    if criticality == "CRITICAL":

        minimum = 10
        maximum = 500

    elif criticality == "HIGH":

        minimum = 10
        maximum = 300

    else:

        minimum = 5
        maximum = 200


    quantity = random.randint(
        minimum,
        maximum
    )


    # --------------------------------------------------------
    # Adjustment can be positive or negative
    # --------------------------------------------------------

    if transaction_type == "ADJUSTMENT":

        quantity = random.randint(
            -100,
            100
        )

        # Avoid zero transaction
        if quantity == 0:

            quantity = 10


    return quantity


# ============================================================
# SELECT TRANSACTION TYPE
# ============================================================

def select_transaction_type():

    return random.choices(

        TRANSACTION_TYPES,

        weights=[
            35,     # RECEIPT
            45,     # ISSUE
            15,     # TRANSFER
            5       # ADJUSTMENT
        ],

        k=1

    )[0]


# ============================================================
# SEED TRANSACTIONS
# ============================================================

def seed_inventory_transactions():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("INVENTORY TRANSACTION SEEDING")
        print("=" * 60)


        # ----------------------------------------------------
        # Clear existing transactions
        # ----------------------------------------------------

        print("\nClearing existing transactions...")

        db.query(
            InventoryTransaction
        ).delete()

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


        if not components:

            raise ValueError(
                "No components found. "
                "Run master-data seeding first."
            )


        print(
            f"Components available: {len(components)}"
        )


        # ----------------------------------------------------
        # Generate transactions
        # ----------------------------------------------------

        transactions = []


        for i in range(
            TRANSACTION_COUNT
        ):

            component = random.choice(
                components
            )


            warehouse = random.choice(
                WAREHOUSES
            )


            transaction_type = (
                select_transaction_type()
            )


            quantity = generate_quantity(
                transaction_type,
                component
            )


            transaction_date = (
                generate_transaction_date()
            )


            reference_id = (
                generate_reference_id(
                    transaction_type,
                    i
                )
            )


            transaction = InventoryTransaction(

                transaction_id=(
                    f"TXN{i + 1:06d}"
                ),

                component_id=component.id,

                warehouse=warehouse,

                transaction_type=(
                    transaction_type
                ),

                quantity=quantity,

                reference_id=reference_id,

                transaction_date=(
                    transaction_date
                ),

                created_at=datetime.utcnow()
            )


            transactions.append(
                transaction
            )


        # ----------------------------------------------------
        # Bulk insert
        # ----------------------------------------------------

        db.add_all(
            transactions
        )

        db.commit()


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print("\nTransactions created.")

        print(
            f"Total transactions: "
            f"{len(transactions)}"
        )


        # ----------------------------------------------------
        # Transaction type summary
        # ----------------------------------------------------

        print("\nTransaction distribution:")


        for transaction_type in (
            TRANSACTION_TYPES
        ):

            count = sum(

                1

                for transaction
                in transactions

                if (
                    transaction.transaction_type
                    == transaction_type
                )
            )


            print(
                f"  {transaction_type:12}"
                f": {count}"
            )


        print("\nDate range:")

        print(
            f"  {START_DATE.date()} "
            f"to "
            f"{END_DATE.date()}"
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

    seed_inventory_transactions()