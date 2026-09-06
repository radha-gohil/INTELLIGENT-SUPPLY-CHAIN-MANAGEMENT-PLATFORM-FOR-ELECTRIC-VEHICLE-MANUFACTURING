from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Vehicle,
    Component,
    VehicleBOM
)


# ============================================================
# VEHICLE BOM
# ============================================================

VEHICLE_BOM = {

    # --------------------------------------------------------
    # ELECTRIC 2-WHEELER
    # --------------------------------------------------------

    "2W": {

        "P001": 1,      # Battery Pack
        "P002": 1,      # Battery Cells
        "P003": 1,      # BMS
        "P006": 1,      # Electric Motor
        "P008": 1,      # Motor Controller
        "P010": 1,      # DC-DC Converter
        "P014": 1,      # Charging Port
        "P019": 1,      # Wiring Harness
        "P021": 1,      # 12V Auxiliary Battery
        "P023": 1,      # Vehicle Sensor Module
        "P024": 1       # Telematics Control Unit

    },


    # --------------------------------------------------------
    # ELECTRIC 3-WHEELER PASSENGER
    # --------------------------------------------------------

    "3W_PASSENGER": {

        "P001": 1,
        "P002": 1,
        "P003": 1,
        "P006": 1,
        "P008": 1,
        "P010": 1,
        "P014": 1,
        "P019": 1,
        "P021": 1,
        "P022": 1,
        "P023": 1,
        "P024": 1

    },


    # --------------------------------------------------------
    # ELECTRIC 3-WHEELER GOODS
    # --------------------------------------------------------

    "3W_GOODS": {

        "P001": 1,
        "P002": 1,
        "P003": 1,
        "P006": 1,
        "P008": 1,
        "P009": 1,      # Reduction Gearbox
        "P010": 1,
        "P014": 1,
        "P019": 1,
        "P021": 1,
        "P022": 1,
        "P023": 1

    },


    # --------------------------------------------------------
    # ELECTRIC CAR
    # --------------------------------------------------------

    "CAR": {

        "P001": 1,      # Battery Pack
        "P002": 1,      # Battery Cells
        "P003": 1,      # BMS
        "P004": 8,      # Battery Modules
        "P005": 1,      # Battery Cooling Plate

        "P006": 1,      # Electric Motor
        "P007": 1,      # Inverter
        "P008": 1,      # Motor Controller
        "P009": 1,      # Reduction Gearbox

        "P010": 1,      # DC-DC Converter
        "P011": 1,      # On-board Charger
        "P012": 1,      # Power Distribution Unit
        "P013": 1,      # Vehicle Control Unit

        "P014": 1,      # Charging Port
        "P015": 1,      # Charging Cable

        "P016": 1,      # Thermal Management System
        "P017": 2,      # Cooling Pump

        "P018": 8,      # High Voltage Cable
        "P019": 1,      # Wiring Harness
        "P020": 6,      # High Voltage Connector

        "P021": 1,      # 12V Auxiliary Battery
        "P022": 1,      # Brake Control Unit
        "P023": 4,      # Vehicle Sensor Module
        "P024": 1,      # Telematics Control Unit

        "P025": 1,      # Steering Assembly
        "P026": 1       # Suspension Assembly

    },


    # --------------------------------------------------------
    # ELECTRIC BUS
    # --------------------------------------------------------

    "BUS": {

        "P001": 2,
        "P002": 2,
        "P003": 2,
        "P004": 16,
        "P005": 2,

        "P006": 2,
        "P007": 2,
        "P008": 2,
        "P009": 2,

        "P010": 2,
        "P011": 2,
        "P012": 2,
        "P013": 2,

        "P014": 2,
        "P015": 2,

        "P016": 2,
        "P017": 4,

        "P018": 16,
        "P019": 2,
        "P020": 12,

        "P021": 2,
        "P022": 2,
        "P023": 8,
        "P024": 2,

        "P025": 1,
        "P026": 1

    }

}


# ============================================================
# SEED FUNCTION
# ============================================================

def seed_vehicle_bom():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("VEHICLE BOM SEEDING")
        print("=" * 60)

        # ----------------------------------------------------
        # Remove existing BOM
        # ----------------------------------------------------

        print("\nClearing existing BOM data...")

        db.query(VehicleBOM).delete()

        db.commit()


        # ----------------------------------------------------
        # Load vehicles
        # ----------------------------------------------------

        vehicles = db.query(Vehicle).all()

        vehicle_map = {
            vehicle.vehicle_type: vehicle
            for vehicle in vehicles
        }


        # ----------------------------------------------------
        # Load components
        # ----------------------------------------------------

        components = db.query(Component).all()

        component_map = {
            component.part_id: component
            for component in components
        }


        # ----------------------------------------------------
        # Create BOM records
        # ----------------------------------------------------

        total_records = 0

        for vehicle_type, components_data in VEHICLE_BOM.items():

            if vehicle_type not in vehicle_map:

                print(
                    f"WARNING: Vehicle type "
                    f"{vehicle_type} not found."
                )

                continue


            vehicle = vehicle_map[vehicle_type]


            for part_id, quantity in components_data.items():

                if part_id not in component_map:

                    print(
                        f"WARNING: Component "
                        f"{part_id} not found."
                    )

                    continue


                component = component_map[part_id]


                bom_record = VehicleBOM(

                    vehicle_id=vehicle.id,

                    component_id=component.id,

                    quantity_required=quantity

                )

                db.add(bom_record)

                total_records += 1


        db.commit()


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print("\nBOM seeding completed.")

        print(
            f"Total BOM records created: {total_records}"
        )

        print("\nVehicle BOM summary:")

        for vehicle_type, components_data in VEHICLE_BOM.items():

            print(
                f"  {vehicle_type:15} "
                f"{len(components_data)} components"
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

    seed_vehicle_bom()