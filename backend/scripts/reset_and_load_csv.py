from datetime import datetime

from pathlib import Path

import pandas as pd

from backend.app.database.connection import (
    Base,
    SessionLocal,
    engine
)

# IMPORTANT:
# Import every model before create_all()
# so SQLAlchemy knows every table.
from backend.app.models import (
    Component,
    Inventory,
    InventoryTransaction,
    PurchaseOrder,
    Supplier,
    SupplierAvailability,
    SupplierComponent,
    SupplierPerformance,
    Vehicle,
    VehicleBOM
)


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_DATABASE_NAME = "ev_supply_chain_v2"


BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)


DATA_DIR = (
    BACKEND_DIR
    / "data"
)


FILES = {

    "components":
        DATA_DIR
        / "component_master.csv",

    "inventory":
        DATA_DIR
        / "inventory.csv",

    "transactions":
        DATA_DIR
        / "inventory_transactions.csv",

    "purchase_orders":
        DATA_DIR
        / "purchase_orders.csv",

    "supplier_components":
        DATA_DIR
        / "supplier_component.csv",

    "suppliers":
        DATA_DIR
        / "supplier_master.csv",

    "vehicle_bom":
        DATA_DIR
        / "vehicle_bom.csv",

    "vehicles":
        DATA_DIR
        / "vehicle_master.csv"
}


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {

    "components": {
        "part_id",
        "part_name",
        "category",
        "sub_category",
        "unit",
        "criticality"
    },

    "inventory": {
        "part_id",
        "part_name",
        "warehouse",
        "available_stock",
        "safety_stock",
        "reorder_level",
        "inventory_status",
        "stock_ratio"
    },

    "transactions": {
        "transaction_id",
        "transaction_date",
        "part_id",
        "warehouse",
        "transaction_type",
        "quantity",
        "reference_id"
    },

    "purchase_orders": {
        "po_id",
        "po_date",
        "supplier_id",
        "part_id",
        "warehouse",
        "quantity_ordered",
        "quantity_received",
        "unit_cost",
        "expected_delivery_date",
        "actual_delivery_date",
        "order_status",
        "quantity_shortage",
        "delivery_delay_days",
        "order_value"
    },

    "supplier_components": {
        "supplier_id",
        "part_id",
        "unit_cost",
        "lead_time_days",
        "minimum_order_quantity",
        "monthly_capacity"
    },

    "suppliers": {
        "supplier_id",
        "supplier_name",
        "location",
        "component_category",
        "lead_time_days",
        "unit_cost",
        "monthly_capacity",
        "quality_rating",
        "reliability_score",
        "status"
    },

    "vehicle_bom": {
        "vehicle_id",
        "vehicle_type",
        "part_id",
        "part_name",
        "quantity_per_vehicle",
        "unit"
    },

    "vehicles": {
        "vehicle_id",
        "vehicle_type",
        "vehicle_category",
        "use_case"
    }
}


# ============================================================
# DATABASE SAFETY CHECK
# ============================================================

def verify_database():

    current_database = (
        engine.url.database
    )

    print(
        f"Connected database: "
        f"{current_database}"
    )


    if (
        current_database
        != EXPECTED_DATABASE_NAME
    ):

        raise RuntimeError(

            "\nDATABASE SAFETY CHECK FAILED.\n\n"
            f"Expected database: "
            f"{EXPECTED_DATABASE_NAME}\n"
            f"Connected database: "
            f"{current_database}\n\n"
            "Import cancelled to protect "
            "your old database."

        )


# ============================================================
# FILE CHECK
# ============================================================

def verify_files():

    print(
        "\nChecking CSV files..."
    )


    missing_files = []


    for name, path in FILES.items():

        if not path.exists():

            missing_files.append(
                str(path)
            )

        else:

            print(
                f"OK  {path.name}"
            )


    if missing_files:

        raise FileNotFoundError(

            "\nMissing CSV files:\n"
            +
            "\n".join(
                missing_files
            )

        )


# ============================================================
# LOAD CSV DATAFRAMES
# ============================================================

def load_dataframes():

    print(
        "\nReading CSV files..."
    )


    data = {}


    for name, path in FILES.items():

        dataframe = pd.read_csv(
            path
        )

        data[name] = dataframe


        print(
            f"{name:22s}: "
            f"{len(dataframe)} rows"
        )


    return data


# ============================================================
# COLUMN VALIDATION
# ============================================================

def validate_columns(
    data
):

    print(
        "\nValidating CSV columns..."
    )


    for name, required in (
        REQUIRED_COLUMNS.items()
    ):

        actual = set(
            data[name].columns
        )

        missing = (
            required
            - actual
        )


        if missing:

            raise ValueError(

                f"{name} is missing "
                f"columns: "
                f"{sorted(missing)}"

            )


    print(
        "All required columns exist."
    )


# ============================================================
# DUPLICATE VALIDATION
# ============================================================

def validate_duplicates(
    data
):

    print(
        "\nChecking duplicate keys..."
    )


    checks = [

        (
            "components",
            ["part_id"]
        ),

        (
            "vehicles",
            ["vehicle_id"]
        ),

        (
            "suppliers",
            ["supplier_id"]
        ),

        (
            "inventory",
            [
                "part_id",
                "warehouse"
            ]
        ),

        (
            "vehicle_bom",
            [
                "vehicle_id",
                "part_id"
            ]
        ),

        (
            "supplier_components",
            [
                "supplier_id",
                "part_id"
            ]
        ),

        (
            "purchase_orders",
            ["po_id"]
        ),

        (
            "transactions",
            ["transaction_id"]
        )

    ]


    for name, columns in checks:

        duplicates = (
            data[name]
            .duplicated(
                subset=columns
            )
            .sum()
        )


        if duplicates > 0:

            raise ValueError(

                f"{name}: found "
                f"{duplicates} duplicate "
                f"records for key "
                f"{columns}"

            )


        print(
            f"OK  {name}"
        )


# ============================================================
# FOREIGN KEY VALIDATION
# ============================================================

def validate_references(
    data
):

    print(
        "\nChecking CSV relationships..."
    )


    component_codes = set(
        data["components"][
            "part_id"
        ]
    )


    vehicle_codes = set(
        data["vehicles"][
            "vehicle_id"
        ]
    )


    supplier_codes = set(
        data["suppliers"][
            "supplier_id"
        ]
    )


    # --------------------------------------------------------
    # BOM
    # --------------------------------------------------------

    missing_bom_components = (

        set(
            data["vehicle_bom"][
                "part_id"
            ]
        )
        -
        component_codes

    )


    missing_bom_vehicles = (

        set(
            data["vehicle_bom"][
                "vehicle_id"
            ]
        )
        -
        vehicle_codes

    )


    if missing_bom_components:

        raise ValueError(
            "Vehicle BOM contains unknown "
            f"components: "
            f"{missing_bom_components}"
        )


    if missing_bom_vehicles:

        raise ValueError(
            "Vehicle BOM contains unknown "
            f"vehicles: "
            f"{missing_bom_vehicles}"
        )


    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    missing_inventory_components = (

        set(
            data["inventory"][
                "part_id"
            ]
        )
        -
        component_codes

    )


    if missing_inventory_components:

        raise ValueError(
            "Inventory contains unknown "
            f"components: "
            f"{missing_inventory_components}"
        )


    # --------------------------------------------------------
    # TRANSACTIONS
    # --------------------------------------------------------

    missing_transaction_components = (

        set(
            data["transactions"][
                "part_id"
            ]
        )
        -
        component_codes

    )


    if missing_transaction_components:

        raise ValueError(
            "Transactions contain unknown "
            f"components: "
            f"{missing_transaction_components}"
        )


    # --------------------------------------------------------
    # SUPPLIER COMPONENT
    # --------------------------------------------------------

    missing_sc_components = (

        set(
            data["supplier_components"][
                "part_id"
            ]
        )
        -
        component_codes

    )


    missing_sc_suppliers = (

        set(
            data["supplier_components"][
                "supplier_id"
            ]
        )
        -
        supplier_codes

    )


    if missing_sc_components:

        raise ValueError(
            "Supplier-component contains "
            f"unknown components: "
            f"{missing_sc_components}"
        )


    if missing_sc_suppliers:

        raise ValueError(
            "Supplier-component contains "
            f"unknown suppliers: "
            f"{missing_sc_suppliers}"
        )


    # --------------------------------------------------------
    # PURCHASE ORDERS
    # --------------------------------------------------------

    missing_po_components = (

        set(
            data["purchase_orders"][
                "part_id"
            ]
        )
        -
        component_codes

    )


    missing_po_suppliers = (

        set(
            data["purchase_orders"][
                "supplier_id"
            ]
        )
        -
        supplier_codes

    )


    if missing_po_components:

        raise ValueError(
            "Purchase orders contain "
            f"unknown components: "
            f"{missing_po_components}"
        )


    if missing_po_suppliers:

        raise ValueError(
            "Purchase orders contain "
            f"unknown suppliers: "
            f"{missing_po_suppliers}"
        )


    print(
        "All CSV relationships are valid."
    )


# ============================================================
# DATA QUALITY WARNINGS
# ============================================================

def show_data_quality_warnings(
    data
):

    print(
        "\nChecking data quality..."
    )


    suspicious_quality = (

        data["suppliers"][

            data["suppliers"][
                "quality_rating"
            ] > 5

        ]

    )


    if not suspicious_quality.empty:

        print(
            "\nWARNING:"
        )

        print(
            "Supplier quality ratings above "
            "5 were found."
        )

        print(
            "They will be stored exactly as "
            "provided in the CSV."
        )


        for _, row in (
            suspicious_quality.iterrows()
        ):

            print(

                f"  {row['supplier_id']} | "
                f"{row['supplier_name']} | "
                f"quality_rating="
                f"{row['quality_rating']}"

            )


    print(
        "\nData-quality check complete."
    )


# ============================================================
# INVENTORY STATUS
# ============================================================

def calculate_inventory_status(
    available_stock,
    safety_stock,
    reorder_level
):

    available_stock = float(
        available_stock
    )

    safety_stock = float(
        safety_stock
    )

    reorder_level = float(
        reorder_level
    )


    if available_stock <= 0:

        return "OUT_OF_STOCK"


    if (
        available_stock
        <= safety_stock
    ):

        return "CRITICAL"


    if (
        available_stock
        <= reorder_level
    ):

        return "REORDER_REQUIRED"


    return "NORMAL"


# ============================================================
# DATE HELPERS
# ============================================================

def parse_date(
    value
):

    if pd.isna(value):

        return None


    parsed = pd.to_datetime(
        value,
        errors="coerce"
    )


    if pd.isna(parsed):

        return None


    return parsed.date()


def parse_datetime(
    value
):

    if pd.isna(value):

        return None


    parsed = pd.to_datetime(
        value,
        errors="coerce"
    )


    if pd.isna(parsed):

        return None


    return parsed.to_pydatetime()


# ============================================================
# RESET DATABASE
# ============================================================

def reset_database():

    print(
        "\nResetting NEW database tables..."
    )


    Base.metadata.drop_all(
        bind=engine
    )


    Base.metadata.create_all(
        bind=engine
    )


    print(
        "Database tables created."
    )


# ============================================================
# LOAD COMPONENTS
# ============================================================

def insert_components(
    db,
    dataframe
):

    print(
        "\nLoading components..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        record = Component(

            part_id=str(
                row["part_id"]
            ).strip(),

            part_name=str(
                row["part_name"]
            ).strip(),

            category=str(
                row["category"]
            ).strip(),

            sub_category=str(
                row["sub_category"]
            ).strip(),

            unit=str(
                row["unit"]
            ).strip(),

            criticality=str(
                row["criticality"]
            ).strip().upper(),

            is_active=True

        )


        db.add(
            record
        )


    db.flush()


    components = (
        db.query(Component)
        .all()
    )


    component_map = {

        component.part_id:
            component.id

        for component
        in components

    }


    print(
        f"Loaded "
        f"{len(component_map)} "
        f"components."
    )


    return component_map


# ============================================================
# LOAD VEHICLES
# ============================================================

def insert_vehicles(
    db,
    dataframe
):

    print(
        "\nLoading vehicles..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        record = Vehicle(

            vehicle_code=str(
                row["vehicle_id"]
            ).strip(),

            vehicle_type=str(
                row["vehicle_type"]
            ).strip(),

            vehicle_category=str(
                row["vehicle_category"]
            ).strip(),

            use_case=str(
                row["use_case"]
            ).strip(),

            is_active=True

        )


        db.add(
            record
        )


    db.flush()


    vehicles = (
        db.query(Vehicle)
        .all()
    )


    vehicle_map = {

        vehicle.vehicle_code:
            vehicle.id

        for vehicle
        in vehicles

    }


    print(
        f"Loaded "
        f"{len(vehicle_map)} "
        f"vehicles."
    )


    return vehicle_map


# ============================================================
# LOAD SUPPLIERS
# ============================================================

def insert_suppliers(
    db,
    dataframe
):

    print(
        "\nLoading suppliers..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        status = str(
            row["status"]
        ).strip().upper()


        record = Supplier(

            supplier_code=str(
                row["supplier_id"]
            ).strip(),

            supplier_name=str(
                row["supplier_name"]
            ).strip(),

            location=str(
                row["location"]
            ).strip(),

            component_category=str(
                row["component_category"]
            ).strip(),

            standard_lead_time_days=int(
                row["lead_time_days"]
            ),

            default_unit_cost=float(
                row["unit_cost"]
            ),

            monthly_capacity=int(
                row["monthly_capacity"]
            ),

            quality_rating=float(
                row["quality_rating"]
            ),

            reliability_score=float(
                row["reliability_score"]
            ),

            status=status,

            is_active=(
                status == "ACTIVE"
            )

        )


        db.add(
            record
        )


    db.flush()


    suppliers = (
        db.query(Supplier)
        .all()
    )


    supplier_map = {

        supplier.supplier_code:
            supplier.id

        for supplier
        in suppliers

    }


    print(
        f"Loaded "
        f"{len(supplier_map)} "
        f"suppliers."
    )


    return supplier_map


# ============================================================
# LOAD VEHICLE BOM
# ============================================================

def insert_vehicle_bom(
    db,
    dataframe,
    vehicle_map,
    component_map
):

    print(
        "\nLoading vehicle BOM..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        record = VehicleBOM(

            vehicle_id=vehicle_map[
                str(
                    row["vehicle_id"]
                ).strip()
            ],

            component_id=component_map[
                str(
                    row["part_id"]
                ).strip()
            ],

            quantity_per_vehicle=float(
                row[
                    "quantity_per_vehicle"
                ]
            ),

            unit=str(
                row["unit"]
            ).strip()

        )


        db.add(
            record
        )


    db.flush()


    print(
        f"Loaded "
        f"{len(dataframe)} "
        f"BOM records."
    )


# ============================================================
# LOAD SUPPLIER COMPONENTS
# ============================================================

def insert_supplier_components(
    db,
    dataframe,
    supplier_map,
    component_map
):

    print(
        "\nLoading supplier-component mappings..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        supplier_code = str(
            row["supplier_id"]
        ).strip()

        part_code = str(
            row["part_id"]
        ).strip()


        record = SupplierComponent(

            supplier_id=(
                supplier_map[
                    supplier_code
                ]
            ),

            component_id=(
                component_map[
                    part_code
                ]
            ),

            unit_price=float(
                row["unit_cost"]
            ),

            minimum_order_quantity=int(
                row[
                    "minimum_order_quantity"
                ]
            ),

            standard_lead_time_days=int(
                row[
                    "lead_time_days"
                ]
            ),

            maximum_capacity=int(
                row[
                    "monthly_capacity"
                ]
            ),

            is_approved=True

        )


        db.add(
            record
        )


    db.flush()


    print(
        f"Loaded "
        f"{len(dataframe)} "
        f"supplier-component records."
    )


# ============================================================
# INITIALIZE SUPPLIER AVAILABILITY
# ============================================================

def insert_supplier_availability(
    db
):

    print(
        "\nInitializing supplier availability..."
    )


    supplier_components = (

        db.query(
            SupplierComponent
        )
        .all()

    )


    for item in supplier_components:

        capacity = int(
            item.maximum_capacity or 0
        )


        record = SupplierAvailability(

            supplier_id=(
                item.supplier_id
            ),

            component_id=(
                item.component_id
            ),

            available_quantity=(
                capacity
            ),

            committed_quantity=0,

            available_to_promise=(
                capacity
            ),

            expected_replenishment_quantity=0,

            expected_replenishment_date=None,

            last_updated=datetime.utcnow()

        )


        db.add(
            record
        )


    db.flush()


    print(
        f"Created "
        f"{len(supplier_components)} "
        f"supplier availability records."
    )


# ============================================================
# LOAD INVENTORY
# ============================================================

def insert_inventory(
    db,
    dataframe,
    component_map
):

    print(
        "\nLoading inventory..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        available = float(
            row["available_stock"]
        )

        safety = float(
            row["safety_stock"]
        )

        reorder = float(
            row["reorder_level"]
        )


        status = (
            calculate_inventory_status(
                available,
                safety,
                reorder
            )
        )


        record = Inventory(

            component_id=component_map[
                str(
                    row["part_id"]
                ).strip()
            ],

            warehouse=str(
                row["warehouse"]
            ).strip(),

            current_stock=available,

            reserved_stock=0,

            available_stock=available,

            safety_stock=safety,

            reorder_level=reorder,

            inventory_status=status,

            last_updated=datetime.utcnow()

        )


        db.add(
            record
        )


    db.flush()


    print(
        f"Loaded "
        f"{len(dataframe)} "
        f"inventory records."
    )


# ============================================================
# LOAD PURCHASE ORDERS
# ============================================================

def insert_purchase_orders(
    db,
    dataframe,
    supplier_map,
    component_map
):

    print(
        "\nLoading purchase orders..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        supplier_code = str(
            row["supplier_id"]
        ).strip()

        part_code = str(
            row["part_id"]
        ).strip()


        record = PurchaseOrder(

            po_number=str(
                row["po_id"]
            ).strip(),

            po_date=parse_date(
                row["po_date"]
            ),

            supplier_id=(
                supplier_map[
                    supplier_code
                ]
            ),

            component_id=(
                component_map[
                    part_code
                ]
            ),

            warehouse=str(
                row["warehouse"]
            ).strip(),

            quantity_ordered=float(
                row[
                    "quantity_ordered"
                ]
            ),

            quantity_received=float(
                row[
                    "quantity_received"
                ]
            ),

            unit_cost=float(
                row["unit_cost"]
            ),

            expected_delivery_date=(
                parse_date(
                    row[
                        "expected_delivery_date"
                    ]
                )
            ),

            actual_delivery_date=(
                parse_date(
                    row[
                        "actual_delivery_date"
                    ]
                )
            ),

            order_status=str(
                row["order_status"]
            ).strip().upper(),

            quantity_shortage=float(
                row[
                    "quantity_shortage"
                ]
            ),

            delivery_delay_days=int(
                row[
                    "delivery_delay_days"
                ]
            ),

            order_value=float(
                row["order_value"]
            )

        )


        db.add(
            record
        )


    db.flush()


    print(
        f"Loaded "
        f"{len(dataframe)} "
        f"purchase orders."
    )


# ============================================================
# BUILD SUPPLIER PERFORMANCE
# ============================================================

def build_supplier_performance(
    db,
    dataframe,
    supplier_map,
    component_map
):

    print(
        "\nBuilding supplier performance..."
    )


    grouped = dataframe.groupby(
        [
            "supplier_id",
            "part_id"
        ]
    )


    count = 0


    for (
        supplier_code,
        part_code
    ), group in grouped:

        total_orders = len(
            group
        )


        on_time_orders = int(
            (
                group[
                    "delivery_delay_days"
                ] <= 0
            ).sum()
        )


        late_orders = int(
            (
                group[
                    "delivery_delay_days"
                ] > 0
            ).sum()
        )


        ordered_quantity = int(
            group[
                "quantity_ordered"
            ].sum()
        )


        received_quantity = int(
            group[
                "quantity_received"
            ].sum()
        )


        # The provided PO CSV has no defective
        # quantity column, so we do not invent one.
        defective_quantity = 0


        late_group = group[

            group[
                "delivery_delay_days"
            ] > 0

        ]


        if late_group.empty:

            average_delay_days = 0.0

        else:

            average_delay_days = float(

                late_group[
                    "delivery_delay_days"
                ].mean()

            )


        performance_date = (

            pd.to_datetime(
                group["po_date"]
            )
            .max()
            .date()

        )


        record = SupplierPerformance(

            supplier_id=supplier_map[
                str(
                    supplier_code
                ).strip()
            ],

            component_id=component_map[
                str(
                    part_code
                ).strip()
            ],

            performance_date=(
                performance_date
            ),

            total_orders=(
                total_orders
            ),

            on_time_orders=(
                on_time_orders
            ),

            late_orders=(
                late_orders
            ),

            ordered_quantity=(
                ordered_quantity
            ),

            received_quantity=(
                received_quantity
            ),

            defective_quantity=(
                defective_quantity
            ),

            average_delay_days=(
                average_delay_days
            )

        )


        db.add(
            record
        )


        count += 1


    db.flush()


    print(
        f"Created "
        f"{count} "
        f"supplier performance records."
    )


# ============================================================
# LOAD INVENTORY TRANSACTIONS
# ============================================================

def insert_transactions(
    db,
    dataframe,
    component_map
):

    print(
        "\nLoading inventory transactions..."
    )


    for _, row in (
        dataframe.iterrows()
    ):

        transaction_date = (
            parse_datetime(
                row[
                    "transaction_date"
                ]
            )
        )


        record = InventoryTransaction(

            transaction_id=str(
                row[
                    "transaction_id"
                ]
            ).strip(),

            component_id=component_map[
                str(
                    row["part_id"]
                ).strip()
            ],

            warehouse=str(
                row["warehouse"]
            ).strip(),

            transaction_type=str(
                row[
                    "transaction_type"
                ]
            ).strip().upper(),

            quantity=float(
                row["quantity"]
            ),

            reference_id=str(
                row["reference_id"]
            ).strip(),

            transaction_date=(
                transaction_date
            ),

            created_at=(
                transaction_date
                or datetime.utcnow()
            )

        )


        db.add(
            record
        )


    db.flush()


    print(
        f"Loaded "
        f"{len(dataframe)} "
        f"inventory transactions."
    )


# ============================================================
# VERIFY DATABASE COUNTS
# ============================================================

def verify_database_counts(
    db
):

    print(
        "\n"
        "============================================"
    )

    print(
        "DATABASE VERIFICATION"
    )

    print(
        "============================================"
    )


    counts = {

        "Components":
            db.query(
                Component
            ).count(),

        "Vehicles":
            db.query(
                Vehicle
            ).count(),

        "Vehicle BOM":
            db.query(
                VehicleBOM
            ).count(),

        "Suppliers":
            db.query(
                Supplier
            ).count(),

        "Supplier Components":
            db.query(
                SupplierComponent
            ).count(),

        "Supplier Availability":
            db.query(
                SupplierAvailability
            ).count(),

        "Inventory":
            db.query(
                Inventory
            ).count(),

        "Purchase Orders":
            db.query(
                PurchaseOrder
            ).count(),

        "Supplier Performance":
            db.query(
                SupplierPerformance
            ).count(),

        "Inventory Transactions":
            db.query(
                InventoryTransaction
            ).count()

    }


    for name, count in (
        counts.items()
    ):

        print(
            f"{name:24s}: {count}"
        )


    print(
        "============================================"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        "============================================"
    )

    print(
        "EV SUPPLY CHAIN V2 DATABASE IMPORT"
    )

    print(
        "============================================"
    )


    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    verify_database()


    # --------------------------------------------------------
    # FILE VALIDATION
    # --------------------------------------------------------

    verify_files()


    data = (
        load_dataframes()
    )


    validate_columns(
        data
    )


    validate_duplicates(
        data
    )


    validate_references(
        data
    )


    show_data_quality_warnings(
        data
    )


    # --------------------------------------------------------
    # RESET ONLY THE NEW DATABASE
    # --------------------------------------------------------

    reset_database()


    # --------------------------------------------------------
    # DATABASE SESSION
    # --------------------------------------------------------

    db = SessionLocal()


    try:

        # ----------------------------------------------------
        # MASTER TABLES
        # ----------------------------------------------------

        component_map = (
            insert_components(
                db,
                data[
                    "components"
                ]
            )
        )


        vehicle_map = (
            insert_vehicles(
                db,
                data[
                    "vehicles"
                ]
            )
        )


        supplier_map = (
            insert_suppliers(
                db,
                data[
                    "suppliers"
                ]
            )
        )


        # ----------------------------------------------------
        # RELATIONSHIP TABLES
        # ----------------------------------------------------

        insert_vehicle_bom(

            db,

            data[
                "vehicle_bom"
            ],

            vehicle_map,

            component_map

        )


        insert_supplier_components(

            db,

            data[
                "supplier_components"
            ],

            supplier_map,

            component_map

        )


        # ----------------------------------------------------
        # CURRENT SUPPLIER CAPACITY BASELINE
        # ----------------------------------------------------

        insert_supplier_availability(
            db
        )


        # ----------------------------------------------------
        # INVENTORY
        # ----------------------------------------------------

        insert_inventory(

            db,

            data[
                "inventory"
            ],

            component_map

        )


        # ----------------------------------------------------
        # PURCHASE ORDER HISTORY
        # ----------------------------------------------------

        insert_purchase_orders(

            db,

            data[
                "purchase_orders"
            ],

            supplier_map,

            component_map

        )


        # ----------------------------------------------------
        # DERIVED SUPPLIER PERFORMANCE
        # ----------------------------------------------------

        build_supplier_performance(

            db,

            data[
                "purchase_orders"
            ],

            supplier_map,

            component_map

        )


        # ----------------------------------------------------
        # INVENTORY TRANSACTION HISTORY
        # ----------------------------------------------------

        insert_transactions(

            db,

            data[
                "transactions"
            ],

            component_map

        )


        # ----------------------------------------------------
        # SAVE EVERYTHING
        # ----------------------------------------------------

        db.commit()


        # ----------------------------------------------------
        # VERIFY
        # ----------------------------------------------------

        verify_database_counts(
            db
        )


        print(
            "\n"
            "DATABASE IMPORT COMPLETED SUCCESSFULLY."
        )


    except Exception as error:

        db.rollback()


        print(
            "\n"
            "DATABASE IMPORT FAILED."
        )


        print(
            f"\nError: {error}"
        )


        raise


    finally:

        db.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()