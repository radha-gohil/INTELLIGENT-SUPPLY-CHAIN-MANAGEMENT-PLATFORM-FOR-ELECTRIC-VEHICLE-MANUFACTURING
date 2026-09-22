from sqlalchemy.orm import Session

from backend.app.database.neo4j_connection import Neo4jConnection

from backend.app.models.vehicle import Vehicle
from backend.app.models.component import Component
from backend.app.models.vehicle_bom import VehicleBOM

from backend.app.models.supplier import Supplier
from backend.app.models.supplier_component import SupplierComponent
from backend.app.models.supplier_availability import SupplierAvailability

from backend.app.models.inventory import Inventory
from backend.app.models.purchase_order import PurchaseOrder


# ============================================================
# KNOWLEDGE GRAPH SYNC SERVICE
# ============================================================

class KnowledgeGraphSyncService:
    """
    Synchronizes PostgreSQL supply-chain data into Neo4j AuraDB.

    Stage 1:
        Vehicle
        Component
        Vehicle -> REQUIRES -> Component

    Stage 2:
        Supplier
        Supplier -> SUPPLIES -> Component

    Stage 3:
        Warehouse
        Component -> STOCKED_AT -> Warehouse

    Stage 4:
        PurchaseOrder
        PurchaseOrder -> ORDERED_FROM -> Supplier
        PurchaseOrder -> FOR_COMPONENT -> Component
        PurchaseOrder -> DELIVERED_TO -> Warehouse
        PurchaseOrder -> FOR_VEHICLE -> Vehicle
    """

    # ========================================================
    # CONSTRAINTS
    # ========================================================

    @staticmethod
    def create_constraints():

        queries = [
            """
            CREATE CONSTRAINT vehicle_code_unique IF NOT EXISTS
            FOR (v:Vehicle)
            REQUIRE v.vehicle_code IS UNIQUE
            """,

            """
            CREATE CONSTRAINT component_part_id_unique IF NOT EXISTS
            FOR (c:Component)
            REQUIRE c.part_id IS UNIQUE
            """,

            """
            CREATE CONSTRAINT supplier_code_unique IF NOT EXISTS
            FOR (s:Supplier)
            REQUIRE s.supplier_code IS UNIQUE
            """,

            """
            CREATE CONSTRAINT warehouse_name_unique IF NOT EXISTS
            FOR (w:Warehouse)
            REQUIRE w.warehouse_name IS UNIQUE
            """,

            """
            CREATE CONSTRAINT purchase_order_number_unique IF NOT EXISTS
            FOR (po:PurchaseOrder)
            REQUIRE po.po_number IS UNIQUE
            """
        ]

        for query in queries:
            Neo4jConnection.execute_write(query)

        return {
            "status": "success",
            "message": "Knowledge Graph constraints created."
        }

    # ========================================================
    # STAGE 1
    # VEHICLES
    # ========================================================

    @staticmethod
    def sync_vehicles(db: Session):

        vehicles = (
            db.query(Vehicle)
            .order_by(Vehicle.id)
            .all()
        )

        query = """
        MERGE (v:Vehicle {
            vehicle_code: $vehicle_code
        })

        SET
            v.postgres_id = $postgres_id,
            v.vehicle_type = $vehicle_type,
            v.vehicle_category = $vehicle_category,
            v.use_case = $use_case,
            v.is_active = $is_active

        RETURN v.vehicle_code AS vehicle_code
        """

        synced = 0

        for vehicle in vehicles:

            Neo4jConnection.execute_write(
                query,
                {
                    "vehicle_code": vehicle.vehicle_code,
                    "postgres_id": vehicle.id,
                    "vehicle_type": vehicle.vehicle_type,
                    "vehicle_category": vehicle.vehicle_category,
                    "use_case": vehicle.use_case,
                    "is_active": vehicle.is_active
                }
            )

            synced += 1

        return {
            "status": "success",
            "vehicles_synced": synced
        }

    # ========================================================
    # STAGE 1
    # COMPONENTS
    # ========================================================

    @staticmethod
    def sync_components(db: Session):

        components = (
            db.query(Component)
            .order_by(Component.id)
            .all()
        )

        query = """
        MERGE (c:Component {
            part_id: $part_id
        })

        SET
            c.postgres_id = $postgres_id,
            c.part_name = $part_name,
            c.category = $category,
            c.sub_category = $sub_category,
            c.unit = $unit,
            c.unit_cost = $unit_cost,
            c.criticality = $criticality,
            c.is_active = $is_active

        RETURN c.part_id AS part_id
        """

        synced = 0

        for component in components:

            Neo4jConnection.execute_write(
                query,
                {
                    "part_id": component.part_id,
                    "postgres_id": component.id,
                    "part_name": component.part_name,
                    "category": component.category,
                    "sub_category": component.sub_category,
                    "unit": component.unit,
                    "unit_cost": component.unit_cost,
                    "criticality": component.criticality,
                    "is_active": component.is_active
                }
            )

            synced += 1

        return {
            "status": "success",
            "components_synced": synced
        }

    # ========================================================
    # STAGE 1
    # VEHICLE -> REQUIRES -> COMPONENT
    # ========================================================

    @staticmethod
    def sync_vehicle_bom(db: Session):

        rows = (
            db.query(
                VehicleBOM,
                Vehicle,
                Component
            )
            .join(
                Vehicle,
                Vehicle.id == VehicleBOM.vehicle_id
            )
            .join(
                Component,
                Component.id == VehicleBOM.component_id
            )
            .order_by(VehicleBOM.id)
            .all()
        )

        query = """
        MATCH (v:Vehicle {
            vehicle_code: $vehicle_code
        })

        MATCH (c:Component {
            part_id: $part_id
        })

        MERGE (v)-[r:REQUIRES]->(c)

        SET
            r.quantity_per_vehicle =
                $quantity_per_vehicle,

            r.unit =
                $unit,

            r.postgres_bom_id =
                $postgres_bom_id

        RETURN
            v.vehicle_code AS vehicle_code,
            c.part_id AS part_id
        """

        synced = 0

        for bom, vehicle, component in rows:

            Neo4jConnection.execute_write(
                query,
                {
                    "vehicle_code":
                        vehicle.vehicle_code,

                    "part_id":
                        component.part_id,

                    "quantity_per_vehicle":
                        bom.quantity_per_vehicle,

                    "unit":
                        bom.unit,

                    "postgres_bom_id":
                        bom.id
                }
            )

            synced += 1

        return {
            "status": "success",
            "bom_relationships_synced": synced
        }

    # ========================================================
    # STAGE 2
    # SUPPLIERS
    # ========================================================

    @staticmethod
    def sync_suppliers(db: Session):

        suppliers = (
            db.query(Supplier)
            .order_by(Supplier.id)
            .all()
        )

        query = """
        MERGE (s:Supplier {
            supplier_code: $supplier_code
        })

        SET
            s.postgres_id =
                $postgres_id,

            s.supplier_name =
                $supplier_name,

            s.location =
                $location,

            s.component_category =
                $component_category,

            s.master_lead_time_days =
                $master_lead_time_days,

            s.master_unit_cost =
                $master_unit_cost,

            s.master_monthly_capacity =
                $master_monthly_capacity,

            s.quality_rating =
                $quality_rating,

            s.baseline_reliability_score =
                $baseline_reliability_score,

            s.status =
                $status,

            s.is_active =
                $is_active

        RETURN s.supplier_code AS supplier_code
        """

        synced = 0

        for supplier in suppliers:

            Neo4jConnection.execute_write(
                query,
                {
                    "supplier_code":
                        supplier.supplier_code,

                    "postgres_id":
                        supplier.id,

                    "supplier_name":
                        supplier.supplier_name,

                    "location":
                        supplier.location,

                    "component_category":
                        supplier.component_category,

                    "master_lead_time_days":
                        supplier.master_lead_time_days,

                    "master_unit_cost":
                        supplier.master_unit_cost,

                    "master_monthly_capacity":
                        supplier.master_monthly_capacity,

                    "quality_rating":
                        supplier.quality_rating,

                    "baseline_reliability_score":
                        supplier.baseline_reliability_score,

                    "status":
                        supplier.status,

                    "is_active":
                        supplier.is_active
                }
            )

            synced += 1

        return {
            "status": "success",
            "suppliers_synced": synced
        }

    # ========================================================
    # STAGE 2
    # SUPPLIER -> SUPPLIES -> COMPONENT
    # ========================================================

    @staticmethod
    def sync_supplier_components(db: Session):

        rows = (
            db.query(
                SupplierComponent,
                Supplier,
                Component
            )
            .join(
                Supplier,
                Supplier.id ==
                SupplierComponent.supplier_id
            )
            .join(
                Component,
                Component.id ==
                SupplierComponent.component_id
            )
            .order_by(SupplierComponent.id)
            .all()
        )

        query = """
        MATCH (s:Supplier {
            supplier_code: $supplier_code
        })

        MATCH (c:Component {
            part_id: $part_id
        })

        MERGE (s)-[r:SUPPLIES]->(c)

        SET
            r.postgres_supplier_component_id =
                $postgres_supplier_component_id,

            r.supplier_part_code =
                $supplier_part_code,

            r.unit_price =
                $unit_price,

            r.minimum_order_quantity =
                $minimum_order_quantity,

            r.standard_lead_time_days =
                $standard_lead_time_days,

            r.maximum_capacity =
                $maximum_capacity,

            r.is_approved =
                $is_approved

        RETURN
            s.supplier_code AS supplier_code,
            c.part_id AS part_id
        """

        synced = 0

        for supplier_component, supplier, component in rows:

            Neo4jConnection.execute_write(
                query,
                {
                    "supplier_code":
                        supplier.supplier_code,

                    "part_id":
                        component.part_id,

                    "postgres_supplier_component_id":
                        supplier_component.id,

                    "supplier_part_code":
                        supplier_component.supplier_part_code,

                    "unit_price":
                        supplier_component.unit_price,

                    "minimum_order_quantity":
                        supplier_component.minimum_order_quantity,

                    "standard_lead_time_days":
                        supplier_component.standard_lead_time_days,

                    "maximum_capacity":
                        supplier_component.maximum_capacity,

                    "is_approved":
                        supplier_component.is_approved
                }
            )

            synced += 1

        return {
            "status": "success",
            "supplier_component_relationships_synced":
                synced
        }

    # ========================================================
    # STAGE 2
    # SUPPLIER AVAILABILITY
    # ========================================================

    @staticmethod
    def sync_supplier_availability(db: Session):

        rows = (
            db.query(
                SupplierAvailability,
                Supplier,
                Component
            )
            .join(
                Supplier,
                Supplier.id ==
                SupplierAvailability.supplier_id
            )
            .join(
                Component,
                Component.id ==
                SupplierAvailability.component_id
            )
            .order_by(SupplierAvailability.id)
            .all()
        )

        query = """
        MATCH (s:Supplier {
            supplier_code: $supplier_code
        })

        MATCH (c:Component {
            part_id: $part_id
        })

        MATCH (s)-[r:SUPPLIES]->(c)

        SET
            r.available_quantity =
                $available_quantity,

            r.committed_quantity =
                $committed_quantity,

            r.available_to_promise =
                $available_to_promise,

            r.expected_replenishment_quantity =
                $expected_replenishment_quantity,

            r.expected_replenishment_date =
                $expected_replenishment_date,

            r.availability_last_updated =
                $availability_last_updated

        RETURN
            s.supplier_code AS supplier_code,
            c.part_id AS part_id
        """

        synced = 0

        for availability, supplier, component in rows:

            expected_date = None

            if availability.expected_replenishment_date:
                expected_date = (
                    availability
                    .expected_replenishment_date
                    .isoformat()
                )

            last_updated = None

            if availability.last_updated:
                last_updated = (
                    availability
                    .last_updated
                    .isoformat()
                )

            Neo4jConnection.execute_write(
                query,
                {
                    "supplier_code":
                        supplier.supplier_code,

                    "part_id":
                        component.part_id,

                    "available_quantity":
                        availability.available_quantity,

                    "committed_quantity":
                        availability.committed_quantity,

                    "available_to_promise":
                        availability.available_to_promise,

                    "expected_replenishment_quantity":
                        availability.expected_replenishment_quantity,

                    "expected_replenishment_date":
                        expected_date,

                    "availability_last_updated":
                        last_updated
                }
            )

            synced += 1

        return {
            "status": "success",
            "supplier_availability_synced": synced
        }

    # ========================================================
    # STAGE 3
    # WAREHOUSE NODES
    # ========================================================

    @staticmethod
    def sync_warehouses(db: Session):

        warehouse_rows = (
            db.query(Inventory.warehouse)
            .distinct()
            .order_by(Inventory.warehouse)
            .all()
        )

        query = """
        MERGE (w:Warehouse {
            warehouse_name: $warehouse_name
        })

        RETURN w.warehouse_name AS warehouse_name
        """

        synced = 0

        for warehouse_row in warehouse_rows:

            warehouse_name = warehouse_row[0]

            Neo4jConnection.execute_write(
                query,
                {
                    "warehouse_name": warehouse_name
                }
            )

            synced += 1

        return {
            "status": "success",
            "warehouses_synced": synced
        }

    # ========================================================
    # STAGE 3
    # COMPONENT -> STOCKED_AT -> WAREHOUSE
    # ========================================================

    @staticmethod
    def sync_inventory(db: Session):

        rows = (
            db.query(
                Inventory,
                Component
            )
            .join(
                Component,
                Component.id ==
                Inventory.component_id
            )
            .order_by(Inventory.id)
            .all()
        )

        query = """
        MATCH (c:Component {
            part_id: $part_id
        })

        MATCH (w:Warehouse {
            warehouse_name: $warehouse_name
        })

        MERGE (c)-[r:STOCKED_AT]->(w)

        SET
            r.postgres_inventory_id =
                $postgres_inventory_id,

            r.current_stock =
                $current_stock,

            r.reserved_stock =
                $reserved_stock,

            r.available_stock =
                $available_stock,

            r.safety_stock =
                $safety_stock,

            r.reorder_level =
                $reorder_level,

            r.inventory_status =
                $inventory_status,

            r.last_updated =
                $last_updated

        RETURN
            c.part_id AS part_id,
            w.warehouse_name AS warehouse_name
        """

        synced = 0

        for inventory, component in rows:

            last_updated = None

            if inventory.last_updated:
                last_updated = (
                    inventory.last_updated.isoformat()
                )

            Neo4jConnection.execute_write(
                query,
                {
                    "part_id":
                        component.part_id,

                    "warehouse_name":
                        inventory.warehouse,

                    "postgres_inventory_id":
                        inventory.id,

                    "current_stock":
                        inventory.current_stock,

                    "reserved_stock":
                        inventory.reserved_stock,

                    "available_stock":
                        inventory.available_stock,

                    "safety_stock":
                        inventory.safety_stock,

                    "reorder_level":
                        inventory.reorder_level,

                    "inventory_status":
                        inventory.inventory_status,

                    "last_updated":
                        last_updated
                }
            )

            synced += 1

        return {
            "status": "success",
            "inventory_relationships_synced": synced
        }

    # ========================================================
    # STAGE 4
    # PURCHASE ORDERS - OPTIMIZED BATCH SYNC
    # ========================================================

    @staticmethod
    def sync_purchase_orders(db: Session):

        BATCH_SIZE = 200

        rows = (
            db.query(
                PurchaseOrder,
                Supplier,
                Component,
                Vehicle
            )
            .join(
                Supplier,
                Supplier.id == PurchaseOrder.supplier_id
            )
            .join(
                Component,
                Component.id == PurchaseOrder.component_id
            )
            .outerjoin(
                Vehicle,
                Vehicle.id == PurchaseOrder.vehicle_id
            )
            .order_by(PurchaseOrder.id)
            .all()
        )

        query = """
        UNWIND $purchase_orders AS row

        MATCH (s:Supplier {
            supplier_code: row.supplier_code
        })

        MATCH (c:Component {
            part_id: row.part_id
        })

        MERGE (w:Warehouse {
            warehouse_name: row.warehouse_name
        })

        MERGE (po:PurchaseOrder {
            po_number: row.po_number
        })

        SET
            po.postgres_id =
                row.postgres_id,

            po.po_date =
                row.po_date,

            po.required_date =
                row.required_date,

            po.urgency =
                row.urgency,

            po.warehouse =
                row.warehouse_name,

            po.quantity_ordered =
                row.quantity_ordered,

            po.quantity_received =
                row.quantity_received,

            po.unit_cost =
                row.unit_cost,

            po.order_value =
                row.order_value,

            po.expected_delivery_date =
                row.expected_delivery_date,

            po.actual_delivery_date =
                row.actual_delivery_date,

            po.quantity_shortage =
                row.quantity_shortage,

            po.delivery_delay_days =
                row.delivery_delay_days,

            po.order_status =
                row.order_status,

            po.tracking_stage =
                row.tracking_stage,

            po.current_location =
                row.current_location,

            po.tracking_notes =
                row.tracking_notes,

            po.last_tracking_update =
                row.last_tracking_update,

            po.dispatched_at =
                row.dispatched_at,

            po.arrived_at_warehouse_at =
                row.arrived_at_warehouse_at,

            po.source_type =
                row.source_type,

            po.created_at =
                row.created_at

        MERGE (po)-[:ORDERED_FROM]->(s)

        MERGE (po)-[:FOR_COMPONENT]->(c)

        MERGE (po)-[:DELIVERED_TO]->(w)

        FOREACH (
            vehicle_code IN
            CASE
                WHEN row.vehicle_code IS NOT NULL
                THEN [row.vehicle_code]
                ELSE []
            END |

            MERGE (v:Vehicle {
                vehicle_code: vehicle_code
            })

            MERGE (po)-[:FOR_VEHICLE]->(v)
        )

        RETURN count(po) AS processed
        """

        purchase_order_data = []

        vehicle_relationships = 0

        for purchase_order, supplier, component, vehicle in rows:

            vehicle_code = None

            if vehicle is not None:
                vehicle_code = vehicle.vehicle_code
                vehicle_relationships += 1

            purchase_order_data.append(
                {
                    "po_number":
                        purchase_order.po_number,

                    "postgres_id":
                        purchase_order.id,

                    "supplier_code":
                        supplier.supplier_code,

                    "part_id":
                        component.part_id,

                    "vehicle_code":
                        vehicle_code,

                    "warehouse_name":
                        purchase_order.warehouse,

                    "po_date":
                        (
                            purchase_order.po_date.isoformat()
                            if purchase_order.po_date
                            else None
                        ),

                    "required_date":
                        (
                            purchase_order.required_date.isoformat()
                            if purchase_order.required_date
                            else None
                        ),

                    "urgency":
                        purchase_order.urgency,

                    "quantity_ordered":
                        purchase_order.quantity_ordered,

                    "quantity_received":
                        purchase_order.quantity_received,

                    "unit_cost":
                        purchase_order.unit_cost,

                    "order_value":
                        purchase_order.order_value,

                    "expected_delivery_date":
                        (
                            purchase_order
                            .expected_delivery_date
                            .isoformat()
                            if purchase_order.expected_delivery_date
                            else None
                        ),

                    "actual_delivery_date":
                        (
                            purchase_order
                            .actual_delivery_date
                            .isoformat()
                            if purchase_order.actual_delivery_date
                            else None
                        ),

                    "quantity_shortage":
                        purchase_order.quantity_shortage,

                    "delivery_delay_days":
                        purchase_order.delivery_delay_days,

                    "order_status":
                        purchase_order.order_status,

                    "tracking_stage":
                        purchase_order.tracking_stage,

                    "current_location":
                        purchase_order.current_location,

                    "tracking_notes":
                        purchase_order.tracking_notes,

                    "last_tracking_update":
                        (
                            purchase_order
                            .last_tracking_update
                            .isoformat()
                            if purchase_order.last_tracking_update
                            else None
                        ),

                    "dispatched_at":
                        (
                            purchase_order
                            .dispatched_at
                            .isoformat()
                            if purchase_order.dispatched_at
                            else None
                        ),

                    "arrived_at_warehouse_at":
                        (
                            purchase_order
                            .arrived_at_warehouse_at
                            .isoformat()
                            if purchase_order.arrived_at_warehouse_at
                            else None
                        ),

                    "source_type":
                        purchase_order.source_type,

                    "created_at":
                        (
                            purchase_order.created_at.isoformat()
                            if purchase_order.created_at
                            else None
                        )
                }
            )

        total = len(purchase_order_data)

        synced = 0

        print(
            f"   Total purchase orders to sync: {total}"
        )

        for start in range(
            0,
            total,
            BATCH_SIZE
        ):

            end = min(
                start + BATCH_SIZE,
                total
            )

            batch = purchase_order_data[start:end]

            Neo4jConnection.execute_write(
                query,
                {
                    "purchase_orders": batch
                }
            )

            synced += len(batch)

            print(
                f"   Synced {synced}/{total} "
                f"purchase orders..."
            )

        return {
            "status": "success",
            "purchase_orders_synced":
                synced,
            "for_vehicle_relationships_synced":
                vehicle_relationships,
            "batch_size":
                BATCH_SIZE
        }

    # ========================================================
    # VERIFY COMPLETE GRAPH
    # ========================================================

    @staticmethod
    def verify_graph():

        queries = {
            "vehicles": """
                MATCH (v:Vehicle)
                RETURN count(v) AS count
            """,

            "components": """
                MATCH (c:Component)
                RETURN count(c) AS count
            """,

            "suppliers": """
                MATCH (s:Supplier)
                RETURN count(s) AS count
            """,

            "warehouses": """
                MATCH (w:Warehouse)
                RETURN count(w) AS count
            """,

            "purchase_orders": """
                MATCH (po:PurchaseOrder)
                RETURN count(po) AS count
            """,

            "requires_relationships": """
                MATCH (:Vehicle)-[r:REQUIRES]->(:Component)
                RETURN count(r) AS count
            """,

            "supplies_relationships": """
                MATCH (:Supplier)-[r:SUPPLIES]->(:Component)
                RETURN count(r) AS count
            """,

            "stocked_at_relationships": """
                MATCH (:Component)-[r:STOCKED_AT]->(:Warehouse)
                RETURN count(r) AS count
            """,

            "ordered_from_relationships": """
                MATCH (:PurchaseOrder)-[r:ORDERED_FROM]->(:Supplier)
                RETURN count(r) AS count
            """,

            "for_component_relationships": """
                MATCH (:PurchaseOrder)-[r:FOR_COMPONENT]->(:Component)
                RETURN count(r) AS count
            """,

            "delivered_to_relationships": """
                MATCH (:PurchaseOrder)-[r:DELIVERED_TO]->(:Warehouse)
                RETURN count(r) AS count
            """,

            "for_vehicle_relationships": """
                MATCH (:PurchaseOrder)-[r:FOR_VEHICLE]->(:Vehicle)
                RETURN count(r) AS count
            """
        }

        verification = {}

        for name, query in queries.items():

            result = Neo4jConnection.execute_read(query)

            if result:
                verification[name] = result[0]["count"]
            else:
                verification[name] = 0

        return verification

    # ========================================================
    # RUN STAGE 1
    # ========================================================

    @classmethod
    def sync_stage_one(cls, db: Session):

        print()
        print("=" * 60)
        print("KNOWLEDGE GRAPH SYNC - STAGE 1")
        print("=" * 60)

        print()
        print("1. Creating constraints...")
        cls.create_constraints()
        print("   Constraints ready.")

        print()
        print("2. Synchronizing vehicles...")
        vehicles = cls.sync_vehicles(db)

        print(
            f"   Vehicles synced: "
            f"{vehicles['vehicles_synced']}"
        )

        print()
        print("3. Synchronizing components...")
        components = cls.sync_components(db)

        print(
            f"   Components synced: "
            f"{components['components_synced']}"
        )

        print()
        print("4. Synchronizing Vehicle BOM...")
        bom = cls.sync_vehicle_bom(db)

        print(
            f"   REQUIRES relationships synced: "
            f"{bom['bom_relationships_synced']}"
        )

        verification = cls.verify_graph()

        print()
        print("5. Verification...")

        print(
            f"   Vehicle nodes: "
            f"{verification['vehicles']}"
        )

        print(
            f"   Component nodes: "
            f"{verification['components']}"
        )

        print(
            f"   REQUIRES relationships: "
            f"{verification['requires_relationships']}"
        )

        print()
        print("=" * 60)
        print("STAGE 1 KNOWLEDGE GRAPH SYNC COMPLETE")
        print("=" * 60)

        return {
            "status": "success",
            "vehicles": vehicles,
            "components": components,
            "bom": bom,
            "verification": verification
        }

    # ========================================================
    # RUN STAGE 2
    # ========================================================

    @classmethod
    def sync_stage_two(cls, db: Session):

        print()
        print("=" * 60)
        print("KNOWLEDGE GRAPH SYNC - STAGE 2")
        print("=" * 60)

        print()
        print("1. Creating/updating constraints...")
        cls.create_constraints()
        print("   Constraints ready.")

        print()
        print("2. Synchronizing suppliers...")
        suppliers = cls.sync_suppliers(db)

        print(
            f"   Suppliers synced: "
            f"{suppliers['suppliers_synced']}"
        )

        print()
        print("3. Creating SUPPLIES relationships...")

        supplier_components = (
            cls.sync_supplier_components(db)
        )

        print(
            "   SUPPLIES relationships synced: "
            f"{supplier_components[
                'supplier_component_relationships_synced'
            ]}"
        )

        print()
        print("4. Synchronizing supplier availability...")

        availability = (
            cls.sync_supplier_availability(db)
        )

        print(
            f"   Availability records synced: "
            f"{availability[
                'supplier_availability_synced'
            ]}"
        )

        verification = cls.verify_graph()

        print()
        print("5. Verification...")

        print(
            f"   Vehicle nodes: "
            f"{verification['vehicles']}"
        )

        print(
            f"   Component nodes: "
            f"{verification['components']}"
        )

        print(
            f"   Supplier nodes: "
            f"{verification['suppliers']}"
        )

        print(
            f"   REQUIRES relationships: "
            f"{verification['requires_relationships']}"
        )

        print(
            f"   SUPPLIES relationships: "
            f"{verification['supplies_relationships']}"
        )

        print()
        print("=" * 60)
        print("STAGE 2 KNOWLEDGE GRAPH SYNC COMPLETE")
        print("=" * 60)

        return {
            "status": "success",
            "suppliers": suppliers,
            "supplier_components":
                supplier_components,
            "availability": availability,
            "verification": verification
        }

    # ========================================================
    # RUN STAGE 3
    # ========================================================

    @classmethod
    def sync_stage_three(cls, db: Session):

        print()
        print("=" * 60)
        print("KNOWLEDGE GRAPH SYNC - STAGE 3")
        print("=" * 60)

        print()
        print("1. Creating/updating constraints...")
        cls.create_constraints()
        print("   Constraints ready.")

        print()
        print("2. Synchronizing warehouses...")
        warehouses = cls.sync_warehouses(db)

        print(
            f"   Warehouses synced: "
            f"{warehouses['warehouses_synced']}"
        )

        print()
        print("3. Synchronizing inventory...")
        inventory = cls.sync_inventory(db)

        print(
            f"   STOCKED_AT relationships synced: "
            f"{inventory[
                'inventory_relationships_synced'
            ]}"
        )

        print()
        print("4. Verifying complete Knowledge Graph...")

        verification = cls.verify_graph()

        print()
        print("   NODES")

        print(
            f"   Vehicle nodes: "
            f"{verification['vehicles']}"
        )

        print(
            f"   Component nodes: "
            f"{verification['components']}"
        )

        print(
            f"   Supplier nodes: "
            f"{verification['suppliers']}"
        )

        print(
            f"   Warehouse nodes: "
            f"{verification['warehouses']}"
        )

        print()
        print("   RELATIONSHIPS")

        print(
            f"   REQUIRES: "
            f"{verification['requires_relationships']}"
        )

        print(
            f"   SUPPLIES: "
            f"{verification['supplies_relationships']}"
        )

        print(
            f"   STOCKED_AT: "
            f"{verification['stocked_at_relationships']}"
        )

        print()
        print("=" * 60)
        print("STAGE 3 KNOWLEDGE GRAPH SYNC COMPLETE")
        print("=" * 60)

        return {
            "status": "success",
            "warehouses": warehouses,
            "inventory": inventory,
            "verification": verification
        }

    # ========================================================
    # RUN STAGE 4
    # ========================================================

    @classmethod
    def sync_stage_four(cls, db: Session):

        print()
        print("=" * 60)
        print("KNOWLEDGE GRAPH SYNC - STAGE 4")
        print("=" * 60)

        print()
        print("1. Creating/updating constraints...")

        cls.create_constraints()

        print("   Constraints ready.")

        print()
        print("2. Synchronizing purchase orders...")

        purchase_orders = cls.sync_purchase_orders(db)

        print()
        print(
            f"   PurchaseOrder nodes synced: "
            f"{purchase_orders[
                'purchase_orders_synced'
            ]}"
        )

        print(
            f"   FOR_VEHICLE relationships expected: "
            f"{purchase_orders[
                'for_vehicle_relationships_synced'
            ]}"
        )

        print()
        print("3. Verifying complete Knowledge Graph...")

        verification = cls.verify_graph()

        print()
        print("   NODES")

        print(
            f"   Vehicle nodes: "
            f"{verification['vehicles']}"
        )

        print(
            f"   Component nodes: "
            f"{verification['components']}"
        )

        print(
            f"   Supplier nodes: "
            f"{verification['suppliers']}"
        )

        print(
            f"   Warehouse nodes: "
            f"{verification['warehouses']}"
        )

        print(
            f"   PurchaseOrder nodes: "
            f"{verification['purchase_orders']}"
        )

        print()
        print("   RELATIONSHIPS")

        print(
            f"   REQUIRES: "
            f"{verification['requires_relationships']}"
        )

        print(
            f"   SUPPLIES: "
            f"{verification['supplies_relationships']}"
        )

        print(
            f"   STOCKED_AT: "
            f"{verification['stocked_at_relationships']}"
        )

        print(
            f"   ORDERED_FROM: "
            f"{verification['ordered_from_relationships']}"
        )

        print(
            f"   FOR_COMPONENT: "
            f"{verification['for_component_relationships']}"
        )

        print(
            f"   DELIVERED_TO: "
            f"{verification['delivered_to_relationships']}"
        )

        print(
            f"   FOR_VEHICLE: "
            f"{verification['for_vehicle_relationships']}"
        )

        print()
        print("=" * 60)
        print("STAGE 4 KNOWLEDGE GRAPH SYNC COMPLETE")
        print("=" * 60)

        return {
            "status": "success",
            "purchase_orders": purchase_orders,
            "verification": verification
        }

    # ========================================================
    # RUN ALL STAGES
    # ========================================================

    @classmethod
    def sync_all(cls, db: Session):
        """
        Re-synchronize the complete Knowledge Graph from
        PostgreSQL.

        MERGE makes repeated synchronization safe.
        """

        print()
        print("=" * 60)
        print("FULL KNOWLEDGE GRAPH SYNCHRONIZATION")
        print("=" * 60)

        cls.create_constraints()

        # Stage 1
        vehicles = cls.sync_vehicles(db)
        components = cls.sync_components(db)
        bom = cls.sync_vehicle_bom(db)

        # Stage 2
        suppliers = cls.sync_suppliers(db)
        supplier_components = (
            cls.sync_supplier_components(db)
        )
        availability = (
            cls.sync_supplier_availability(db)
        )

        # Stage 3
        warehouses = cls.sync_warehouses(db)
        inventory = cls.sync_inventory(db)

        # Stage 4
        purchase_orders = (
            cls.sync_purchase_orders(db)
        )

        verification = cls.verify_graph()

        print()
        print("FINAL KNOWLEDGE GRAPH COUNTS")
        print("-" * 60)

        print(
            f"Vehicles:        "
            f"{verification['vehicles']}"
        )

        print(
            f"Components:      "
            f"{verification['components']}"
        )

        print(
            f"Suppliers:       "
            f"{verification['suppliers']}"
        )

        print(
            f"Warehouses:      "
            f"{verification['warehouses']}"
        )

        print(
            f"PurchaseOrders:  "
            f"{verification['purchase_orders']}"
        )

        print()

        print(
            f"REQUIRES:        "
            f"{verification['requires_relationships']}"
        )

        print(
            f"SUPPLIES:        "
            f"{verification['supplies_relationships']}"
        )

        print(
            f"STOCKED_AT:      "
            f"{verification['stocked_at_relationships']}"
        )

        print(
            f"ORDERED_FROM:    "
            f"{verification['ordered_from_relationships']}"
        )

        print(
            f"FOR_COMPONENT:   "
            f"{verification['for_component_relationships']}"
        )

        print(
            f"DELIVERED_TO:    "
            f"{verification['delivered_to_relationships']}"
        )

        print(
            f"FOR_VEHICLE:     "
            f"{verification['for_vehicle_relationships']}"
        )

        print()
        print("=" * 60)
        print("FULL KNOWLEDGE GRAPH SYNC COMPLETE")
        print("=" * 60)

        return {
            "status": "success",
            "vehicles": vehicles,
            "components": components,
            "bom": bom,
            "suppliers": suppliers,
            "supplier_components":
                supplier_components,
            "availability": availability,
            "warehouses": warehouses,
            "inventory": inventory,
            "purchase_orders":
                purchase_orders,
            "verification": verification
        }