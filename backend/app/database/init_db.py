from backend.app.database.connection import Base, engine

from backend.app.models import (
    Vehicle,
    Component,
    Supplier,
    SupplierComponent,
    SupplierAvailability,
    SupplierPerformance,
    VehicleBOM
)


def initialize_database():

    print("Starting database initialization...")

    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables created successfully.")


if __name__ == "__main__":
    initialize_database()