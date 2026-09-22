from backend.app.database.connection import (
    Base,
    engine,
)

# ============================================================
# IMPORT ALL SQLALCHEMY MODELS
#
# IMPORTANT:
# Models must be imported before Base.metadata.create_all()
# so SQLAlchemy knows about every table.
# ============================================================

from backend.app.models import (
    Vehicle,
    Component,
    Supplier,
    SupplierComponent,
    PurchaseOrderStatusHistory,
    SupplierAvailability,
    VehicleBOM,
    Inventory,
    InventoryTransaction,
    SupplierPerformance,
    PurchaseOrder,
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    print("Starting database initialization...")

    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables created successfully.")


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    initialize_database()