from datetime import datetime, timedelta
import random

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Vehicle,
    Component,
    Supplier,
    SupplierComponent,
    SupplierAvailability
)


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)


# ============================================================
# VEHICLE MASTER DATA
# ============================================================

VEHICLES = [

    {
        "vehicle_code": "EV-2W",
        "vehicle_type": "2W",
        "vehicle_name": "Electric Scooter",
        "manufacturer": "EV Manufacturer A"
    },

    {
        "vehicle_code": "EV-3WP",
        "vehicle_type": "3W_PASSENGER",
        "vehicle_name": "Electric Passenger 3-Wheeler",
        "manufacturer": "EV Manufacturer A"
    },

    {
        "vehicle_code": "EV-3WG",
        "vehicle_type": "3W_GOODS",
        "vehicle_name": "Electric Goods 3-Wheeler",
        "manufacturer": "EV Manufacturer A"
    },

    {
        "vehicle_code": "EV-CAR",
        "vehicle_type": "CAR",
        "vehicle_name": "Electric Passenger Car",
        "manufacturer": "EV Manufacturer A"
    },

    {
        "vehicle_code": "EV-BUS",
        "vehicle_type": "BUS",
        "vehicle_name": "Electric Bus",
        "manufacturer": "EV Manufacturer A"
    }

]


# ============================================================
# COMPONENT MASTER DATA
# ============================================================

COMPONENTS = [

    # --------------------------------------------------------
    # BATTERY SYSTEM
    # --------------------------------------------------------

    {
        "part_id": "P001",
        "part_name": "Battery Pack",
        "category": "Battery System",
        "unit": "unit",
        "unit_cost": 85000,
        "criticality": "CRITICAL"
    },

    {
        "part_id": "P002",
        "part_name": "Battery Cells",
        "category": "Battery System",
        "unit": "cell",
        "unit_cost": 850,
        "criticality": "CRITICAL"
    },

    {
        "part_id": "P003",
        "part_name": "Battery Management System",
        "category": "Battery System",
        "unit": "unit",
        "unit_cost": 6500,
        "criticality": "CRITICAL"
    },

    {
        "part_id": "P004",
        "part_name": "Battery Module",
        "category": "Battery System",
        "unit": "unit",
        "unit_cost": 18000,
        "criticality": "CRITICAL"
    },

    {
        "part_id": "P005",
        "part_name": "Battery Cooling Plate",
        "category": "Battery System",
        "unit": "unit",
        "unit_cost": 4500,
        "criticality": "HIGH"
    },


    # --------------------------------------------------------
    # POWERTRAIN
    # --------------------------------------------------------

    {
        "part_id": "P006",
        "part_name": "Electric Motor",
        "category": "Powertrain",
        "unit": "unit",
        "unit_cost": 32000,
        "criticality": "CRITICAL"
    },

    {
        "part_id": "P007",
        "part_name": "Inverter",
        "category": "Power Electronics",
        "unit": "unit",
        "unit_cost": 22000,
        "criticality": "CRITICAL"
    },

    {
        "part_id": "P008",
        "part_name": "Motor Controller",
        "category": "Power Electronics",
        "unit": "unit",
        "unit_cost": 12000,
        "criticality": "HIGH"
    },

    {
        "part_id": "P009",
        "part_name": "Reduction Gearbox",
        "category": "Powertrain",
        "unit": "unit",
        "unit_cost": 18000,
        "criticality": "HIGH"
    },


    # --------------------------------------------------------
    # POWER ELECTRONICS
    # --------------------------------------------------------

    {
        "part_id": "P010",
        "part_name": "DC-DC Converter",
        "category": "Power Electronics",
        "unit": "unit",
        "unit_cost": 7500,
        "criticality": "HIGH"
    },

    {
        "part_id": "P011",
        "part_name": "On-board Charger",
        "category": "Power Electronics",
        "unit": "unit",
        "unit_cost": 14000,
        "criticality": "HIGH"
    },

    {
        "part_id": "P012",
        "part_name": "Power Distribution Unit",
        "category": "Power Electronics",
        "unit": "unit",
        "unit_cost": 11000,
        "criticality": "HIGH"
    },

    {
        "part_id": "P013",
        "part_name": "Vehicle Control Unit",
        "category": "Electronics",
        "unit": "unit",
        "unit_cost": 9500,
        "criticality": "HIGH"
    },


    # --------------------------------------------------------
    # CHARGING
    # --------------------------------------------------------

    {
        "part_id": "P014",
        "part_name": "Charging Port",
        "category": "Charging",
        "unit": "unit",
        "unit_cost": 5000,
        "criticality": "MEDIUM"
    },

    {
        "part_id": "P015",
        "part_name": "Charging Cable",
        "category": "Charging",
        "unit": "unit",
        "unit_cost": 3500,
        "criticality": "MEDIUM"
    },


    # --------------------------------------------------------
    # THERMAL MANAGEMENT
    # --------------------------------------------------------

    {
        "part_id": "P016",
        "part_name": "Thermal Management System",
        "category": "Thermal Management",
        "unit": "unit",
        "unit_cost": 16000,
        "criticality": "HIGH"
    },

    {
        "part_id": "P017",
        "part_name": "Cooling Pump",
        "category": "Thermal Management",
        "unit": "unit",
        "unit_cost": 5500,
        "criticality": "MEDIUM"
    },


    # --------------------------------------------------------
    # ELECTRICAL
    # --------------------------------------------------------

    {
        "part_id": "P018",
        "part_name": "High Voltage Cable",
        "category": "Electrical",
        "unit": "meter",
        "unit_cost": 750,
        "criticality": "HIGH"
    },

    {
        "part_id": "P019",
        "part_name": "Wiring Harness",
        "category": "Electrical",
        "unit": "set",
        "unit_cost": 4500,
        "criticality": "HIGH"
    },

    {
        "part_id": "P020",
        "part_name": "High Voltage Connector",
        "category": "Electrical",
        "unit": "unit",
        "unit_cost": 900,
        "criticality": "MEDIUM"
    },

    {
        "part_id": "P021",
        "part_name": "12V Auxiliary Battery",
        "category": "Electrical",
        "unit": "unit",
        "unit_cost": 6000,
        "criticality": "MEDIUM"
    },


    # --------------------------------------------------------
    # CONTROL & SENSORS
    # --------------------------------------------------------

    {
        "part_id": "P022",
        "part_name": "Brake Control Unit",
        "category": "Control System",
        "unit": "unit",
        "unit_cost": 8500,
        "criticality": "HIGH"
    },

    {
        "part_id": "P023",
        "part_name": "Vehicle Sensor Module",
        "category": "Sensors",
        "unit": "unit",
        "unit_cost": 4200,
        "criticality": "MEDIUM"
    },

    {
        "part_id": "P024",
        "part_name": "Telematics Control Unit",
        "category": "Electronics",
        "unit": "unit",
        "unit_cost": 7000,
        "criticality": "MEDIUM"
    },


    # --------------------------------------------------------
    # MECHANICAL
    # --------------------------------------------------------

    {
        "part_id": "P025",
        "part_name": "Steering Assembly",
        "category": "Mechanical",
        "unit": "unit",
        "unit_cost": 9000,
        "criticality": "HIGH"
    },

    {
        "part_id": "P026",
        "part_name": "Suspension Assembly",
        "category": "Mechanical",
        "unit": "set",
        "unit_cost": 12500,
        "criticality": "HIGH"
    }

]


# ============================================================
# SUPPLIER MASTER DATA
# ============================================================

SUPPLIERS = [

    {
        "supplier_code": "SUP001",
        "supplier_name": "VoltCell Technologies",
        "location": "Bengaluru",
        "contact_email": "supply@voltcell.example",
        "contact_phone": "+91-9000000001",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP002",
        "supplier_name": "PowerDrive Systems",
        "location": "Pune",
        "contact_email": "orders@powerdrive.example",
        "contact_phone": "+91-9000000002",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP003",
        "supplier_name": "Electra Components",
        "location": "Chennai",
        "contact_email": "sales@electra.example",
        "contact_phone": "+91-9000000003",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP004",
        "supplier_name": "GreenMotion Components",
        "location": "Ahmedabad",
        "contact_email": "sales@greenmotion.example",
        "contact_phone": "+91-9000000004",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP005",
        "supplier_name": "EVCore Manufacturing",
        "location": "Hyderabad",
        "contact_email": "procurement@evcore.example",
        "contact_phone": "+91-9000000005",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP006",
        "supplier_name": "EnergyTech Solutions",
        "location": "Mumbai",
        "contact_email": "orders@energytech.example",
        "contact_phone": "+91-9000000006",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP007",
        "supplier_name": "AutoElectro Systems",
        "location": "Gurugram",
        "contact_email": "supply@autoelectro.example",
        "contact_phone": "+91-9000000007",
        "status": "ACTIVE"
    },

    {
        "supplier_code": "SUP008",
        "supplier_name": "DriveTech Industries",
        "location": "Hosur",
        "contact_email": "orders@drivetech.example",
        "contact_phone": "+91-9000000008",
        "status": "ACTIVE"
    }

]


# ============================================================
# SUPPLIER-COMPONENT CONFIGURATION
# ============================================================

SUPPLIER_COMPONENT_MAP = {

    "SUP001": [
        "P001",
        "P002",
        "P003",
        "P004",
        "P005"
    ],

    "SUP002": [
        "P006",
        "P007",
        "P008",
        "P009"
    ],

    "SUP003": [
        "P010",
        "P011",
        "P012",
        "P013",
        "P014"
    ],

    "SUP004": [
        "P015",
        "P016",
        "P017",
        "P018",
        "P019"
    ],

    "SUP005": [
        "P003",
        "P006",
        "P008",
        "P013",
        "P020",
        "P021"
    ],

    "SUP006": [
        "P001",
        "P002",
        "P007",
        "P010",
        "P011",
        "P016"
    ],

    "SUP007": [
        "P012",
        "P013",
        "P019",
        "P020",
        "P022",
        "P023",
        "P024"
    ],

    "SUP008": [
        "P006",
        "P009",
        "P017",
        "P025",
        "P026"
    ]

}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_supplier_performance_profile(supplier_code):

    profiles = {

        "SUP001": {
            "price_factor": 1.00,
            "lead_time": (7, 14),
            "capacity": (5000, 12000)
        },

        "SUP002": {
            "price_factor": 1.02,
            "lead_time": (10, 20),
            "capacity": (4000, 10000)
        },

        "SUP003": {
            "price_factor": 0.98,
            "lead_time": (5, 12),
            "capacity": (3000, 9000)
        },

        "SUP004": {
            "price_factor": 1.04,
            "lead_time": (12, 25),
            "capacity": (2500, 8000)
        },

        "SUP005": {
            "price_factor": 1.01,
            "lead_time": (8, 18),
            "capacity": (3500, 10000)
        },

        "SUP006": {
            "price_factor": 1.06,
            "lead_time": (15, 30),
            "capacity": (4000, 11000)
        },

        "SUP007": {
            "price_factor": 0.99,
            "lead_time": (6, 15),
            "capacity": (3000, 8500)
        },

        "SUP008": {
            "price_factor": 1.03,
            "lead_time": (10, 22),
            "capacity": (2500, 7500)
        }

    }

    return profiles[supplier_code]


# ============================================================
# SEED DATABASE
# ============================================================

def seed_database():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("EV SUPPLY CHAIN - MASTER DATA SEEDING")
        print("=" * 60)


        # ----------------------------------------------------
        # CLEAR EXISTING DATA
        # ----------------------------------------------------

        print("\nClearing existing master data...")

        db.query(SupplierAvailability).delete()
        db.query(SupplierComponent).delete()
        db.query(Supplier).delete()
        db.query(Component).delete()
        db.query(Vehicle).delete()

        db.commit()


        # ----------------------------------------------------
        # VEHICLES
        # ----------------------------------------------------

        print("\nCreating vehicles...")

        vehicle_objects = {}

        for data in VEHICLES:

            vehicle = Vehicle(
                vehicle_code=data["vehicle_code"],
                vehicle_type=data["vehicle_type"],
                vehicle_name=data["vehicle_name"],
                manufacturer=data["manufacturer"],
                is_active=True
            )

            db.add(vehicle)

            vehicle_objects[
                data["vehicle_type"]
            ] = vehicle


        db.flush()

        print(
            f"Vehicles created: {len(vehicle_objects)}"
        )


        # ----------------------------------------------------
        # COMPONENTS
        # ----------------------------------------------------

        print("\nCreating components...")

        component_objects = {}

        for data in COMPONENTS:

            component = Component(
                part_id=data["part_id"],
                part_name=data["part_name"],
                category=data["category"],
                unit=data["unit"],
                unit_cost=data["unit_cost"],
                criticality=data["criticality"],
                is_active=True
            )

            db.add(component)

            component_objects[
                data["part_id"]
            ] = component


        db.flush()

        print(
            f"Components created: {len(component_objects)}"
        )


        # ----------------------------------------------------
        # SUPPLIERS
        # ----------------------------------------------------

        print("\nCreating suppliers...")

        supplier_objects = {}

        for data in SUPPLIERS:

            supplier = Supplier(
                supplier_code=data["supplier_code"],
                supplier_name=data["supplier_name"],
                location=data["location"],
                contact_email=data["contact_email"],
                contact_phone=data["contact_phone"],
                status=data["status"],
                is_active=True
            )

            db.add(supplier)

            supplier_objects[
                data["supplier_code"]
            ] = supplier


        db.flush()

        print(
            f"Suppliers created: {len(supplier_objects)}"
        )


        # ----------------------------------------------------
        # SUPPLIER-COMPONENT RELATIONSHIPS
        # ----------------------------------------------------

        print("\nCreating supplier-component relationships...")

        supplier_component_objects = []

        for supplier_code, part_ids in SUPPLIER_COMPONENT_MAP.items():

            supplier = supplier_objects[supplier_code]

            profile = get_supplier_performance_profile(
                supplier_code
            )

            for part_id in part_ids:

                component = component_objects[part_id]

                base_price = component.unit_cost

                price_factor = profile["price_factor"]

                unit_price = round(
                    base_price * price_factor,
                    2
                )

                lead_time = random.randint(
                    profile["lead_time"][0],
                    profile["lead_time"][1]
                )

                maximum_capacity = random.randint(
                    profile["capacity"][0],
                    profile["capacity"][1]
                )

                minimum_order_quantity = random.choice(
                    [10, 25, 50, 100, 250]
                )

                relationship = SupplierComponent(

                    supplier_id=supplier.id,

                    component_id=component.id,

                    supplier_part_code=(
                        f"{supplier_code}-{part_id}"
                    ),

                    unit_price=unit_price,

                    minimum_order_quantity=(
                        minimum_order_quantity
                    ),

                    standard_lead_time_days=(
                        lead_time
                    ),

                    maximum_capacity=(
                        maximum_capacity
                    ),

                    is_approved=True
                )

                db.add(relationship)

                supplier_component_objects.append(
                    relationship
                )


        db.flush()

        print(
            "Supplier-component relationships created:",
            len(supplier_component_objects)
        )


        # ----------------------------------------------------
        # SUPPLIER AVAILABILITY
        # ----------------------------------------------------

        print("\nCreating supplier availability...")

        availability_count = 0

        for relationship in supplier_component_objects:

            supplier_id = relationship.supplier_id

            component_id = relationship.component_id

            capacity = relationship.maximum_capacity

            # Current supplier stock
            available_quantity = random.randint(
                int(capacity * 0.20),
                int(capacity * 0.80)
            )

            # Quantity already committed
            committed_quantity = random.randint(
                0,
                int(available_quantity * 0.35)
            )

            # Actual quantity available to promise
            available_to_promise = max(
                available_quantity - committed_quantity,
                0
            )

            # Expected incoming replenishment
            expected_replenishment_quantity = random.randint(
                0,
                int(capacity * 0.50)
            )

            # Some suppliers have replenishment,
            # some currently do not.
            if expected_replenishment_quantity > 0:

                replenishment_days = random.randint(
                    5,
                    30
                )

                expected_replenishment_date = (
                    datetime.utcnow()
                    + timedelta(days=replenishment_days)
                )

            else:

                expected_replenishment_date = None


            availability = SupplierAvailability(

                supplier_id=supplier_id,

                component_id=component_id,

                available_quantity=(
                    available_quantity
                ),

                committed_quantity=(
                    committed_quantity
                ),

                available_to_promise=(
                    available_to_promise
                ),

                expected_replenishment_quantity=(
                    expected_replenishment_quantity
                ),

                expected_replenishment_date=(
                    expected_replenishment_date
                ),

                last_updated=datetime.utcnow()
            )

            db.add(availability)

            availability_count += 1


        db.commit()


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("MASTER DATA SEEDING COMPLETED")
        print("=" * 60)

        print(
            f"Vehicles                  : {len(VEHICLES)}"
        )

        print(
            f"Components                : {len(COMPONENTS)}"
        )

        print(
            f"Suppliers                 : {len(SUPPLIERS)}"
        )

        print(
            "Supplier-Component Links  :",
            len(supplier_component_objects)
        )

        print(
            "Availability Records      :",
            availability_count
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

    seed_database()