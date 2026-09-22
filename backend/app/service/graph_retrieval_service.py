from backend.app.database.neo4j_connection import Neo4jConnection


class GraphRetrievalService:
    """
    Retrieval layer for the EV Supply Chain Knowledge Graph.

    This service retrieves structured supply-chain information
    from Neo4j. It does not use an LLM.

    Graph structure:

        Vehicle --------REQUIRES--------> Component

        Supplier -------SUPPLIES--------> Component

        Component -----STOCKED_AT-------> Warehouse

        PurchaseOrder --ORDERED_FROM----> Supplier
        PurchaseOrder --FOR_COMPONENT---> Component
        PurchaseOrder --DELIVERED_TO----> Warehouse
        PurchaseOrder --FOR_VEHICLE-----> Vehicle
    """

    # ========================================================
    # GRAPH HEALTH / SUMMARY
    # ========================================================

    @staticmethod
    def get_graph_summary():
        """
        Return the current size of the Knowledge Graph.
        """

        query = """
        MATCH (n)

        WITH
            count(CASE WHEN n:Vehicle THEN 1 END) AS vehicles,
            count(CASE WHEN n:Component THEN 1 END) AS components,
            count(CASE WHEN n:Supplier THEN 1 END) AS suppliers,
            count(CASE WHEN n:Warehouse THEN 1 END) AS warehouses,
            count(CASE WHEN n:PurchaseOrder THEN 1 END)
                AS purchase_orders

        OPTIONAL MATCH ()-[r]->()

        RETURN
            vehicles,
            components,
            suppliers,
            warehouses,
            purchase_orders,
            count(r) AS total_relationships
        """

        result = Neo4jConnection.execute_read(query)

        if not result:
            return {
                "vehicles": 0,
                "components": 0,
                "suppliers": 0,
                "warehouses": 0,
                "purchase_orders": 0,
                "total_relationships": 0
            }

        return result[0]

    # ========================================================
    # NATURAL-LANGUAGE ENTITY SEARCH
    # ========================================================

    @staticmethod
    def search_entities(search_text: str, limit: int = 10):
        """
        Search known Knowledge Graph entities by their human-readable
        names and identifiers.

        Supported:
            Vehicle
            Component
            Supplier
            Warehouse

        This method is useful when the user asks:

            "Who supplies Battery Pack?"
            "Show Electric Car components."
            "Tell me about Battery Systems India."
            "Show inventory in Chennai."

        Instead of asking Gemini to guess an identifier, the actual
        Neo4j graph is searched.
        """

        if not search_text or not search_text.strip():
            return []

        query = """
        CALL {
            MATCH (v:Vehicle)

            WHERE
                toLower(v.vehicle_code)
                    = toLower($search_text)
                OR toLower(v.vehicle_type)
                    = toLower($search_text)
                OR toLower(v.vehicle_category)
                    = toLower($search_text)
                OR toLower(v.vehicle_type)
                    CONTAINS toLower($search_text)
                OR toLower($search_text)
                    CONTAINS toLower(v.vehicle_type)

            RETURN
                'vehicle' AS entity_type,
                v.vehicle_code AS entity_id,
                v.vehicle_type AS entity_name,
                v.vehicle_category AS secondary_name,
                CASE
                    WHEN toLower(v.vehicle_code)
                        = toLower($search_text)
                    THEN 100

                    WHEN toLower(v.vehicle_type)
                        = toLower($search_text)
                    THEN 95

                    WHEN toLower(v.vehicle_category)
                        = toLower($search_text)
                    THEN 90

                    ELSE 70
                END AS match_score

            UNION ALL

            MATCH (c:Component)

            WHERE
                toLower(c.part_id)
                    = toLower($search_text)
                OR toLower(c.part_name)
                    = toLower($search_text)
                OR toLower(c.part_name)
                    CONTAINS toLower($search_text)
                OR toLower($search_text)
                    CONTAINS toLower(c.part_name)

            RETURN
                'component' AS entity_type,
                c.part_id AS entity_id,
                c.part_name AS entity_name,
                c.category AS secondary_name,
                CASE
                    WHEN toLower(c.part_id)
                        = toLower($search_text)
                    THEN 100

                    WHEN toLower(c.part_name)
                        = toLower($search_text)
                    THEN 95

                    ELSE 70
                END AS match_score

            UNION ALL

            MATCH (s:Supplier)

            WHERE
                toLower(s.supplier_code)
                    = toLower($search_text)
                OR toLower(s.supplier_name)
                    = toLower($search_text)
                OR toLower(s.supplier_name)
                    CONTAINS toLower($search_text)
                OR toLower($search_text)
                    CONTAINS toLower(s.supplier_name)

            RETURN
                'supplier' AS entity_type,
                s.supplier_code AS entity_id,
                s.supplier_name AS entity_name,
                s.location AS secondary_name,
                CASE
                    WHEN toLower(s.supplier_code)
                        = toLower($search_text)
                    THEN 100

                    WHEN toLower(s.supplier_name)
                        = toLower($search_text)
                    THEN 95

                    ELSE 70
                END AS match_score

            UNION ALL

            MATCH (w:Warehouse)

            WHERE
                toLower(w.warehouse_name)
                    = toLower($search_text)
                OR toLower(w.warehouse_name)
                    CONTAINS toLower($search_text)
                OR toLower($search_text)
                    CONTAINS toLower(w.warehouse_name)

            RETURN
                'warehouse' AS entity_type,
                w.warehouse_name AS entity_id,
                w.warehouse_name AS entity_name,
                'Warehouse' AS secondary_name,
                CASE
                    WHEN toLower(w.warehouse_name)
                        = toLower($search_text)
                    THEN 95

                    ELSE 70
                END AS match_score
        }

        RETURN
            entity_type,
            entity_id,
            entity_name,
            secondary_name,
            match_score

        ORDER BY
            match_score DESC,
            entity_type,
            entity_name

        LIMIT $limit
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "search_text": search_text.strip(),
                "limit": limit
            }
        )

    # ========================================================
    # RESOLVE ENTITY FROM COMPLETE QUESTION
    # ========================================================

    @staticmethod
    def resolve_entity_from_question(question: str):
        """
        Search the complete user question for known graph entities.

        This is intentionally deterministic and graph-backed.

        Example:

            "Who supplies the Battery Pack?"

        returns:

            {
                "entity_type": "component",
                "entity_id": "P001",
                "entity_name": "Battery Pack"
            }
        """

        if not question or not question.strip():
            return None

        query = """
        CALL {
            MATCH (v:Vehicle)

            WHERE
                toLower($question)
                    CONTAINS toLower(v.vehicle_code)
                OR toLower($question)
                    CONTAINS toLower(v.vehicle_type)

            RETURN
                'vehicle' AS entity_type,
                v.vehicle_code AS entity_id,
                v.vehicle_type AS entity_name,
                v.vehicle_category AS secondary_name,

                CASE
                    WHEN toLower($question)
                        CONTAINS toLower(v.vehicle_code)
                    THEN 100
                    ELSE 90
                END AS match_score,

                size(v.vehicle_type) AS name_length

            UNION ALL

            MATCH (c:Component)

            WHERE
                toLower($question)
                    CONTAINS toLower(c.part_id)
                OR toLower($question)
                    CONTAINS toLower(c.part_name)

            RETURN
                'component' AS entity_type,
                c.part_id AS entity_id,
                c.part_name AS entity_name,
                c.category AS secondary_name,

                CASE
                    WHEN toLower($question)
                        CONTAINS toLower(c.part_id)
                    THEN 100
                    ELSE 90
                END AS match_score,

                size(c.part_name) AS name_length

            UNION ALL

            MATCH (s:Supplier)

            WHERE
                toLower($question)
                    CONTAINS toLower(s.supplier_code)
                OR toLower($question)
                    CONTAINS toLower(s.supplier_name)

            RETURN
                'supplier' AS entity_type,
                s.supplier_code AS entity_id,
                s.supplier_name AS entity_name,
                s.location AS secondary_name,

                CASE
                    WHEN toLower($question)
                        CONTAINS toLower(s.supplier_code)
                    THEN 100
                    ELSE 90
                END AS match_score,

                size(s.supplier_name) AS name_length

            UNION ALL

            MATCH (w:Warehouse)

            WHERE
                toLower($question)
                    CONTAINS toLower(w.warehouse_name)

            RETURN
                'warehouse' AS entity_type,
                w.warehouse_name AS entity_id,
                w.warehouse_name AS entity_name,
                'Warehouse' AS secondary_name,
                85 AS match_score,
                size(w.warehouse_name) AS name_length
        }

        RETURN
            entity_type,
            entity_id,
            entity_name,
            secondary_name,
            match_score

        ORDER BY
            match_score DESC,
            name_length DESC

        LIMIT 1
        """

        result = Neo4jConnection.execute_read(
            query,
            {
                "question": question.strip()
            }
        )

        if not result:
            return None

        return result[0]

    # ========================================================
    # RESOLVE ALL ENTITIES FROM QUESTION
    # ========================================================

    @staticmethod
    def resolve_entities_from_question(question: str):
        """
        Find all graph entities mentioned in the question.

        This supports questions containing more than one entity.

        Example:

            "How much Battery Pack stock is in Chennai?"

        can resolve:

            Component:
                Battery Pack -> P001

            Warehouse:
                Chennai
        """

        if not question or not question.strip():
            return []

        query = """
        CALL {
            MATCH (v:Vehicle)

            WHERE
                toLower($question)
                    CONTAINS toLower(v.vehicle_code)
                OR toLower($question)
                    CONTAINS toLower(v.vehicle_type)

            RETURN
                'vehicle' AS entity_type,
                v.vehicle_code AS entity_id,
                v.vehicle_type AS entity_name,
                v.vehicle_category AS secondary_name,

                CASE
                    WHEN toLower($question)
                        CONTAINS toLower(v.vehicle_code)
                    THEN 100
                    ELSE 90
                END AS match_score,

                size(v.vehicle_type) AS name_length

            UNION ALL

            MATCH (c:Component)

            WHERE
                toLower($question)
                    CONTAINS toLower(c.part_id)
                OR toLower($question)
                    CONTAINS toLower(c.part_name)

            RETURN
                'component' AS entity_type,
                c.part_id AS entity_id,
                c.part_name AS entity_name,
                c.category AS secondary_name,

                CASE
                    WHEN toLower($question)
                        CONTAINS toLower(c.part_id)
                    THEN 100
                    ELSE 90
                END AS match_score,

                size(c.part_name) AS name_length

            UNION ALL

            MATCH (s:Supplier)

            WHERE
                toLower($question)
                    CONTAINS toLower(s.supplier_code)
                OR toLower($question)
                    CONTAINS toLower(s.supplier_name)

            RETURN
                'supplier' AS entity_type,
                s.supplier_code AS entity_id,
                s.supplier_name AS entity_name,
                s.location AS secondary_name,

                CASE
                    WHEN toLower($question)
                        CONTAINS toLower(s.supplier_code)
                    THEN 100
                    ELSE 90
                END AS match_score,

                size(s.supplier_name) AS name_length

            UNION ALL

            MATCH (w:Warehouse)

            WHERE
                toLower($question)
                    CONTAINS toLower(w.warehouse_name)

            RETURN
                'warehouse' AS entity_type,
                w.warehouse_name AS entity_id,
                w.warehouse_name AS entity_name,
                'Warehouse' AS secondary_name,
                85 AS match_score,
                size(w.warehouse_name) AS name_length
        }

        RETURN DISTINCT
            entity_type,
            entity_id,
            entity_name,
            secondary_name,
            match_score,
            name_length

        ORDER BY
            match_score DESC,
            name_length DESC,
            entity_type
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "question": question.strip()
            }
        )

    # ========================================================
    # VEHICLE RETRIEVAL
    # ========================================================

    @staticmethod
    def get_vehicle(vehicle_code: str):
        """
        Retrieve one vehicle.
        """

        query = """
        MATCH (v:Vehicle {
            vehicle_code: $vehicle_code
        })

        RETURN
            v.vehicle_code AS vehicle_code,
            v.vehicle_type AS vehicle_type,
            v.vehicle_category AS vehicle_category,
            v.use_case AS use_case,
            v.is_active AS is_active
        """

        result = Neo4jConnection.execute_read(
            query,
            {
                "vehicle_code": vehicle_code
            }
        )

        if not result:
            return None

        return result[0]

    # ========================================================
    # VEHICLE BOM
    # ========================================================

    @staticmethod
    def get_vehicle_components(vehicle_code: str):
        """
        Retrieve all components required by a vehicle.
        """

        query = """
        MATCH (v:Vehicle {
            vehicle_code: $vehicle_code
        })-[r:REQUIRES]->(c:Component)

        RETURN
            v.vehicle_code AS vehicle_code,
            c.part_id AS part_id,
            c.part_name AS part_name,
            c.category AS category,
            c.sub_category AS sub_category,
            c.criticality AS criticality,
            c.unit AS unit,
            c.unit_cost AS unit_cost,
            r.quantity_per_vehicle AS quantity_per_vehicle,
            r.unit AS bom_unit

        ORDER BY
            c.criticality,
            c.part_id
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "vehicle_code": vehicle_code
            }
        )

    # ========================================================
    # COMPONENT RETRIEVAL
    # ========================================================

    @staticmethod
    def get_component(part_id: str):
        """
        Retrieve one component.
        """

        query = """
        MATCH (c:Component {
            part_id: $part_id
        })

        RETURN
            c.part_id AS part_id,
            c.part_name AS part_name,
            c.category AS category,
            c.sub_category AS sub_category,
            c.unit AS unit,
            c.unit_cost AS unit_cost,
            c.criticality AS criticality,
            c.is_active AS is_active
        """

        result = Neo4jConnection.execute_read(
            query,
            {
                "part_id": part_id
            }
        )

        if not result:
            return None

        return result[0]

    # ========================================================
    # COMPONENT SUPPLIERS
    # ========================================================

    @staticmethod
    def get_component_suppliers(part_id: str):
        """
        Retrieve suppliers capable of supplying a component.
        """

        query = """
        MATCH (s:Supplier)-[r:SUPPLIES]->(
            c:Component {
                part_id: $part_id
            }
        )

        RETURN
            c.part_id AS part_id,

            s.supplier_code AS supplier_code,
            s.supplier_name AS supplier_name,
            s.location AS supplier_location,
            s.quality_rating AS quality_rating,
            s.baseline_reliability_score AS reliability_score,
            s.status AS supplier_status,
            s.is_active AS supplier_active,

            r.unit_price AS unit_price,
            r.minimum_order_quantity AS minimum_order_quantity,
            r.standard_lead_time_days AS lead_time_days,
            r.maximum_capacity AS maximum_capacity,
            r.is_approved AS is_approved,

            r.available_quantity AS available_quantity,
            r.committed_quantity AS committed_quantity,
            r.available_to_promise AS available_to_promise,
            r.expected_replenishment_quantity
                AS expected_replenishment_quantity,
            r.expected_replenishment_date
                AS expected_replenishment_date

        ORDER BY
            r.is_approved DESC,
            r.available_to_promise DESC,
            r.standard_lead_time_days ASC,
            r.unit_price ASC
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "part_id": part_id
            }
        )

    # ========================================================
    # COMPONENT INVENTORY
    # ========================================================

    @staticmethod
    def get_component_inventory(part_id: str):
        """
        Retrieve inventory for a component across warehouses.
        """

        query = """
        MATCH (
            c:Component {
                part_id: $part_id
            }
        )-[r:STOCKED_AT]->(w:Warehouse)

        RETURN
            c.part_id AS part_id,
            c.part_name AS part_name,

            w.warehouse_name AS warehouse,

            r.current_stock AS current_stock,
            r.reserved_stock AS reserved_stock,
            r.available_stock AS available_stock,
            r.safety_stock AS safety_stock,
            r.reorder_level AS reorder_level,
            r.inventory_status AS inventory_status,
            r.last_updated AS last_updated

        ORDER BY
            w.warehouse_name
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "part_id": part_id
            }
        )

    # ========================================================
    # COMPONENT + WAREHOUSE INVENTORY
    # ========================================================

    @staticmethod
    def get_component_inventory_at_warehouse(
        part_id: str,
        warehouse_name: str
    ):
        """
        Retrieve inventory for one component at one warehouse.
        """

        query = """
        MATCH (
            c:Component {
                part_id: $part_id
            }
        )-[r:STOCKED_AT]->(
            w:Warehouse {
                warehouse_name: $warehouse_name
            }
        )

        RETURN
            c.part_id AS part_id,
            c.part_name AS part_name,
            c.category AS category,
            c.criticality AS criticality,

            w.warehouse_name AS warehouse,

            r.current_stock AS current_stock,
            r.reserved_stock AS reserved_stock,
            r.available_stock AS available_stock,
            r.safety_stock AS safety_stock,
            r.reorder_level AS reorder_level,
            r.inventory_status AS inventory_status,
            r.last_updated AS last_updated
        """

        result = Neo4jConnection.execute_read(
            query,
            {
                "part_id": part_id,
                "warehouse_name": warehouse_name
            }
        )

        if not result:
            return None

        return result[0]

    # ========================================================
    # COMPONENT PURCHASE ORDERS
    # ========================================================

    @staticmethod
    def get_component_purchase_orders(
        part_id: str,
        limit: int = 20
    ):
        """
        Retrieve purchase orders for a component.
        """

        query = """
        MATCH (
            po:PurchaseOrder
        )-[:FOR_COMPONENT]->(
            c:Component {
                part_id: $part_id
            }
        )

        OPTIONAL MATCH
            (po)-[:ORDERED_FROM]->(s:Supplier)

        OPTIONAL MATCH
            (po)-[:DELIVERED_TO]->(w:Warehouse)

        RETURN
            po.po_number AS po_number,
            po.po_date AS po_date,
            po.required_date AS required_date,
            po.quantity_ordered AS quantity_ordered,
            po.quantity_received AS quantity_received,
            po.quantity_shortage AS quantity_shortage,
            po.unit_cost AS unit_cost,
            po.order_value AS order_value,
            po.order_status AS order_status,
            po.tracking_stage AS tracking_stage,
            po.expected_delivery_date AS expected_delivery_date,
            po.actual_delivery_date AS actual_delivery_date,
            po.delivery_delay_days AS delivery_delay_days,
            po.source_type AS source_type,

            s.supplier_code AS supplier_code,
            s.supplier_name AS supplier_name,

            w.warehouse_name AS warehouse

        ORDER BY
            po.po_date DESC,
            po.po_number DESC

        LIMIT $limit
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "part_id": part_id,
                "limit": limit
            }
        )

    # ========================================================
    # SUPPLIER RETRIEVAL
    # ========================================================

    @staticmethod
    def get_supplier(supplier_code: str):
        """
        Retrieve one supplier.
        """

        query = """
        MATCH (s:Supplier {
            supplier_code: $supplier_code
        })

        RETURN
            s.supplier_code AS supplier_code,
            s.supplier_name AS supplier_name,
            s.location AS location,
            s.component_category AS component_category,
            s.master_lead_time_days AS master_lead_time_days,
            s.master_unit_cost AS master_unit_cost,
            s.master_monthly_capacity AS master_monthly_capacity,
            s.quality_rating AS quality_rating,
            s.baseline_reliability_score
                AS baseline_reliability_score,
            s.status AS status,
            s.is_active AS is_active
        """

        result = Neo4jConnection.execute_read(
            query,
            {
                "supplier_code": supplier_code
            }
        )

        if not result:
            return None

        return result[0]

    # ========================================================
    # SUPPLIER COMPONENTS
    # ========================================================

    @staticmethod
    def get_supplier_components(supplier_code: str):
        """
        Retrieve components supplied by a supplier.
        """

        query = """
        MATCH (
            s:Supplier {
                supplier_code: $supplier_code
            }
        )-[r:SUPPLIES]->(c:Component)

        RETURN
            s.supplier_code AS supplier_code,

            c.part_id AS part_id,
            c.part_name AS part_name,
            c.category AS category,
            c.criticality AS criticality,

            r.unit_price AS unit_price,
            r.minimum_order_quantity AS minimum_order_quantity,
            r.standard_lead_time_days AS lead_time_days,
            r.maximum_capacity AS maximum_capacity,
            r.is_approved AS is_approved,
            r.available_quantity AS available_quantity,
            r.committed_quantity AS committed_quantity,
            r.available_to_promise AS available_to_promise

        ORDER BY
            c.part_id
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "supplier_code": supplier_code
            }
        )

    # ========================================================
    # SUPPLIER PURCHASE ORDERS
    # ========================================================

    @staticmethod
    def get_supplier_purchase_orders(
        supplier_code: str,
        limit: int = 20
    ):
        """
        Retrieve recent purchase orders for a supplier.
        """

        query = """
        MATCH (
            po:PurchaseOrder
        )-[:ORDERED_FROM]->(
            s:Supplier {
                supplier_code: $supplier_code
            }
        )

        OPTIONAL MATCH
            (po)-[:FOR_COMPONENT]->(c:Component)

        OPTIONAL MATCH
            (po)-[:DELIVERED_TO]->(w:Warehouse)

        RETURN
            po.po_number AS po_number,
            po.po_date AS po_date,
            po.quantity_ordered AS quantity_ordered,
            po.quantity_received AS quantity_received,
            po.quantity_shortage AS quantity_shortage,
            po.unit_cost AS unit_cost,
            po.order_value AS order_value,
            po.order_status AS order_status,
            po.tracking_stage AS tracking_stage,
            po.expected_delivery_date AS expected_delivery_date,
            po.actual_delivery_date AS actual_delivery_date,
            po.delivery_delay_days AS delivery_delay_days,

            c.part_id AS part_id,
            c.part_name AS part_name,

            w.warehouse_name AS warehouse

        ORDER BY
            po.po_date DESC,
            po.po_number DESC

        LIMIT $limit
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "supplier_code": supplier_code,
                "limit": limit
            }
        )

    # ========================================================
    # WAREHOUSE RETRIEVAL
    # ========================================================

    @staticmethod
    def get_warehouse_inventory(warehouse_name: str):
        """
        Retrieve all components stocked at a warehouse.
        """

        query = """
        MATCH (
            c:Component
        )-[r:STOCKED_AT]->(
            w:Warehouse {
                warehouse_name: $warehouse_name
            }
        )

        RETURN
            w.warehouse_name AS warehouse,

            c.part_id AS part_id,
            c.part_name AS part_name,
            c.category AS category,
            c.criticality AS criticality,

            r.current_stock AS current_stock,
            r.reserved_stock AS reserved_stock,
            r.available_stock AS available_stock,
            r.safety_stock AS safety_stock,
            r.reorder_level AS reorder_level,
            r.inventory_status AS inventory_status

        ORDER BY
            c.part_id
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "warehouse_name": warehouse_name
            }
        )

    # ========================================================
    # PURCHASE ORDER RETRIEVAL
    # ========================================================

    @staticmethod
    def get_purchase_order(po_number: str):
        """
        Retrieve one purchase order with its connected entities.
        """

        query = """
        MATCH (po:PurchaseOrder {
            po_number: $po_number
        })

        OPTIONAL MATCH
            (po)-[:ORDERED_FROM]->(s:Supplier)

        OPTIONAL MATCH
            (po)-[:FOR_COMPONENT]->(c:Component)

        OPTIONAL MATCH
            (po)-[:DELIVERED_TO]->(w:Warehouse)

        OPTIONAL MATCH
            (po)-[:FOR_VEHICLE]->(v:Vehicle)

        RETURN
            po.po_number AS po_number,
            po.po_date AS po_date,
            po.required_date AS required_date,
            po.urgency AS urgency,

            po.quantity_ordered AS quantity_ordered,
            po.quantity_received AS quantity_received,
            po.quantity_shortage AS quantity_shortage,

            po.unit_cost AS unit_cost,
            po.order_value AS order_value,

            po.expected_delivery_date AS expected_delivery_date,
            po.actual_delivery_date AS actual_delivery_date,
            po.delivery_delay_days AS delivery_delay_days,

            po.order_status AS order_status,
            po.tracking_stage AS tracking_stage,
            po.current_location AS current_location,
            po.tracking_notes AS tracking_notes,
            po.last_tracking_update AS last_tracking_update,

            po.source_type AS source_type,

            s.supplier_code AS supplier_code,
            s.supplier_name AS supplier_name,

            c.part_id AS part_id,
            c.part_name AS part_name,

            w.warehouse_name AS warehouse,

            v.vehicle_code AS vehicle_code

        LIMIT 1
        """

        result = Neo4jConnection.execute_read(
            query,
            {
                "po_number": po_number
            }
        )

        if not result:
            return None

        return result[0]

    # ========================================================
    # VEHICLE SUPPLY CHAIN CONTEXT
    # ========================================================

    @staticmethod
    def get_vehicle_supply_chain_context(
        vehicle_code: str
    ):
        """
        Retrieve supply-chain context for every component
        required by a vehicle.
        """

        query = """
        MATCH (
            v:Vehicle {
                vehicle_code: $vehicle_code
            }
        )-[req:REQUIRES]->(c:Component)

        OPTIONAL MATCH
            (s:Supplier)-[sup:SUPPLIES]->(c)

        OPTIONAL MATCH
            (c)-[stock:STOCKED_AT]->(w:Warehouse)

        RETURN
            v.vehicle_code AS vehicle_code,
            v.vehicle_type AS vehicle_type,
            v.vehicle_category AS vehicle_category,

            c.part_id AS part_id,
            c.part_name AS part_name,
            c.category AS component_category,
            c.criticality AS criticality,

            req.quantity_per_vehicle AS quantity_per_vehicle,
            req.unit AS bom_unit,

            s.supplier_code AS supplier_code,
            s.supplier_name AS supplier_name,
            s.location AS supplier_location,

            sup.unit_price AS supplier_unit_price,
            sup.standard_lead_time_days AS lead_time_days,
            sup.maximum_capacity AS maximum_capacity,
            sup.available_to_promise AS available_to_promise,
            sup.is_approved AS supplier_approved,

            w.warehouse_name AS warehouse,
            stock.available_stock AS available_stock,
            stock.safety_stock AS safety_stock,
            stock.reorder_level AS reorder_level,
            stock.inventory_status AS inventory_status

        ORDER BY
            c.part_id,
            s.supplier_code,
            w.warehouse_name
        """

        return Neo4jConnection.execute_read(
            query,
            {
                "vehicle_code": vehicle_code
            }
        )

    # ========================================================
    # COMPONENT COMPLETE CONTEXT
    # ========================================================

    @classmethod
    def get_component_context(
        cls,
        part_id: str,
        purchase_order_limit: int = 10
    ):
        """
        Build structured context for one component.
        """

        component = cls.get_component(part_id)

        if component is None:
            return None

        suppliers = cls.get_component_suppliers(
            part_id
        )

        inventory = cls.get_component_inventory(
            part_id
        )

        purchase_orders = (
            cls.get_component_purchase_orders(
                part_id,
                purchase_order_limit
            )
        )

        return {
            "component": component,
            "suppliers": suppliers,
            "inventory": inventory,
            "purchase_orders": purchase_orders
        }

    # ========================================================
    # VEHICLE COMPLETE CONTEXT
    # ========================================================

    @classmethod
    def get_vehicle_context(
        cls,
        vehicle_code: str
    ):
        """
        Build structured Graph-RAG context for one vehicle.
        """

        vehicle = cls.get_vehicle(
            vehicle_code
        )

        if vehicle is None:
            return None

        components = cls.get_vehicle_components(
            vehicle_code
        )

        supply_chain = (
            cls.get_vehicle_supply_chain_context(
                vehicle_code
            )
        )

        return {
            "vehicle": vehicle,
            "components": components,
            "supply_chain": supply_chain
        }

    # ========================================================
    # FRONTEND KNOWLEDGE-GRAPH VISUALIZATION
    # ========================================================

    @staticmethod
    def _rows_to_visual_graph(rows):
        """Convert Neo4j relationship rows into frontend nodes and edges."""
        nodes = {}
        edges = {}

        for row in rows or []:
            source_id = row.get("source_id")
            target_id = row.get("target_id")
            relationship = row.get("relationship")

            if source_id:
                nodes[source_id] = {
                    "id": source_id,
                    "label": row.get("source_label") or source_id,
                    "type": row.get("source_type") or "Unknown",
                    "properties": row.get("source_properties") or {},
                }

            if target_id:
                nodes[target_id] = {
                    "id": target_id,
                    "label": row.get("target_label") or target_id,
                    "type": row.get("target_type") or "Unknown",
                    "properties": row.get("target_properties") or {},
                }

            if source_id and target_id and relationship:
                edge_id = f"{source_id}-{relationship}-{target_id}"
                edges[edge_id] = {
                    "id": edge_id,
                    "source": source_id,
                    "target": target_id,
                    "type": relationship,
                    "label": relationship,
                    "properties": row.get("relationship_properties") or {},
                }

        return {
            "nodes": list(nodes.values()),
            "edges": list(edges.values()),
        }

    @classmethod
    def get_visual_graph(
        cls,
        entity_type: str,
        entity_id: str = None,
        intent: str = "general",
        limit: int = 100,
    ):
        """
        Return the actual Neo4j subgraph used for frontend visualization.

        The result is generic and always has:
            {"nodes": [...], "edges": [...]}

        Relationship directions match the stored Neo4j graph:
            Vehicle -[:REQUIRES]-> Component
            Supplier -[:SUPPLIES]-> Component
            Component -[:STOCKED_AT]-> Warehouse
            PurchaseOrder -[:ORDERED_FROM]-> Supplier
            PurchaseOrder -[:FOR_COMPONENT]-> Component
            PurchaseOrder -[:DELIVERED_TO]-> Warehouse
            PurchaseOrder -[:FOR_VEHICLE]-> Vehicle
        """
        if not entity_type:
            return {"nodes": [], "edges": []}

        # Component + warehouse composite entity, e.g. P001@Chennai
        if entity_type == "component_warehouse" and entity_id and "@" in entity_id:
            part_id, warehouse_name = entity_id.split("@", 1)
            query = """
            MATCH (c:Component {part_id: $part_id})-[r:STOCKED_AT]->
                  (w:Warehouse {warehouse_name: $warehouse_name})
            RETURN
                c.part_id AS source_id,
                c.part_name AS source_label,
                'Component' AS source_type,
                properties(c) AS source_properties,
                type(r) AS relationship,
                properties(r) AS relationship_properties,
                w.warehouse_name AS target_id,
                w.warehouse_name AS target_label,
                'Warehouse' AS target_type,
                properties(w) AS target_properties
            LIMIT $limit
            """
            rows = Neo4jConnection.execute_read(
                query,
                {"part_id": part_id, "warehouse_name": warehouse_name, "limit": limit},
            )
            return cls._rows_to_visual_graph(rows)

        if entity_type == "component":
            if intent in {"supplier", "pricing", "lead_time"}:
                query = """
                MATCH (s:Supplier)-[r:SUPPLIES]->(c:Component {part_id: $entity_id})
                RETURN
                    s.supplier_code AS source_id,
                    s.supplier_name AS source_label,
                    'Supplier' AS source_type,
                    properties(s) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    c.part_id AS target_id,
                    c.part_name AS target_label,
                    'Component' AS target_type,
                    properties(c) AS target_properties
                LIMIT $limit
                """
            elif intent == "inventory":
                query = """
                MATCH (c:Component {part_id: $entity_id})-[r:STOCKED_AT]->(w:Warehouse)
                RETURN
                    c.part_id AS source_id,
                    c.part_name AS source_label,
                    'Component' AS source_type,
                    properties(c) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    w.warehouse_name AS target_id,
                    w.warehouse_name AS target_label,
                    'Warehouse' AS target_type,
                    properties(w) AS target_properties
                LIMIT $limit
                """
            elif intent == "purchase_order":
                query = """
                MATCH (po:PurchaseOrder)-[r:FOR_COMPONENT]->(c:Component {part_id: $entity_id})
                RETURN
                    po.po_number AS source_id,
                    po.po_number AS source_label,
                    'PurchaseOrder' AS source_type,
                    properties(po) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    c.part_id AS target_id,
                    c.part_name AS target_label,
                    'Component' AS target_type,
                    properties(c) AS target_properties
                LIMIT $limit
                """
            else:
                # General component view: suppliers + warehouses + purchase orders.
                query = """
                MATCH (c:Component {part_id: $entity_id})
                CALL (c) {
                    MATCH (s:Supplier)-[r:SUPPLIES]->(c)
                    RETURN
                        s.supplier_code AS source_id,
                        s.supplier_name AS source_label,
                        'Supplier' AS source_type,
                        properties(s) AS source_properties,
                        type(r) AS relationship,
                        properties(r) AS relationship_properties,
                        c.part_id AS target_id,
                        c.part_name AS target_label,
                        'Component' AS target_type,
                        properties(c) AS target_properties
                    UNION ALL
                    WITH c
                    MATCH (c)-[r:STOCKED_AT]->(w:Warehouse)
                    RETURN
                        c.part_id AS source_id,
                        c.part_name AS source_label,
                        'Component' AS source_type,
                        properties(c) AS source_properties,
                        type(r) AS relationship,
                        properties(r) AS relationship_properties,
                        w.warehouse_name AS target_id,
                        w.warehouse_name AS target_label,
                        'Warehouse' AS target_type,
                        properties(w) AS target_properties
                    UNION ALL
                    WITH c
                    MATCH (po:PurchaseOrder)-[r:FOR_COMPONENT]->(c)
                    RETURN
                        po.po_number AS source_id,
                        po.po_number AS source_label,
                        'PurchaseOrder' AS source_type,
                        properties(po) AS source_properties,
                        type(r) AS relationship,
                        properties(r) AS relationship_properties,
                        c.part_id AS target_id,
                        c.part_name AS target_label,
                        'Component' AS target_type,
                        properties(c) AS target_properties
                }
                RETURN *
                LIMIT $limit
                """

            rows = Neo4jConnection.execute_read(
                query,
                {"entity_id": entity_id, "limit": limit},
            )
            return cls._rows_to_visual_graph(rows)

        if entity_type == "vehicle":
            query = """
            MATCH (v:Vehicle {vehicle_code: $entity_id})-[r:REQUIRES]->(c:Component)
            RETURN
                v.vehicle_code AS source_id,
                v.vehicle_type AS source_label,
                'Vehicle' AS source_type,
                properties(v) AS source_properties,
                type(r) AS relationship,
                properties(r) AS relationship_properties,
                c.part_id AS target_id,
                c.part_name AS target_label,
                'Component' AS target_type,
                properties(c) AS target_properties
            LIMIT $limit
            """
            rows = Neo4jConnection.execute_read(query, {"entity_id": entity_id, "limit": limit})
            return cls._rows_to_visual_graph(rows)

        if entity_type == "supplier":
            query = """
            MATCH (s:Supplier {supplier_code: $entity_id})-[r:SUPPLIES]->(c:Component)
            RETURN
                s.supplier_code AS source_id,
                s.supplier_name AS source_label,
                'Supplier' AS source_type,
                properties(s) AS source_properties,
                type(r) AS relationship,
                properties(r) AS relationship_properties,
                c.part_id AS target_id,
                c.part_name AS target_label,
                'Component' AS target_type,
                properties(c) AS target_properties
            LIMIT $limit
            """
            rows = Neo4jConnection.execute_read(query, {"entity_id": entity_id, "limit": limit})
            return cls._rows_to_visual_graph(rows)

        if entity_type == "warehouse":
            query = """
            MATCH (c:Component)-[r:STOCKED_AT]->(w:Warehouse {warehouse_name: $entity_id})
            RETURN
                c.part_id AS source_id,
                c.part_name AS source_label,
                'Component' AS source_type,
                properties(c) AS source_properties,
                type(r) AS relationship,
                properties(r) AS relationship_properties,
                w.warehouse_name AS target_id,
                w.warehouse_name AS target_label,
                'Warehouse' AS target_type,
                properties(w) AS target_properties
            LIMIT $limit
            """
            rows = Neo4jConnection.execute_read(query, {"entity_id": entity_id, "limit": limit})
            return cls._rows_to_visual_graph(rows)

        if entity_type == "purchase_order":
            query = """
            MATCH (po:PurchaseOrder {po_number: $entity_id})
            CALL (po) {
                MATCH (po)-[r:ORDERED_FROM]->(s:Supplier)
                RETURN
                    po.po_number AS source_id,
                    po.po_number AS source_label,
                    'PurchaseOrder' AS source_type,
                    properties(po) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    s.supplier_code AS target_id,
                    s.supplier_name AS target_label,
                    'Supplier' AS target_type,
                    properties(s) AS target_properties
                UNION ALL
                WITH po
                MATCH (po)-[r:FOR_COMPONENT]->(c:Component)
                RETURN
                    po.po_number AS source_id,
                    po.po_number AS source_label,
                    'PurchaseOrder' AS source_type,
                    properties(po) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    c.part_id AS target_id,
                    c.part_name AS target_label,
                    'Component' AS target_type,
                    properties(c) AS target_properties
                UNION ALL
                WITH po
                MATCH (po)-[r:DELIVERED_TO]->(w:Warehouse)
                RETURN
                    po.po_number AS source_id,
                    po.po_number AS source_label,
                    'PurchaseOrder' AS source_type,
                    properties(po) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    w.warehouse_name AS target_id,
                    w.warehouse_name AS target_label,
                    'Warehouse' AS target_type,
                    properties(w) AS target_properties
                UNION ALL
                WITH po
                MATCH (po)-[r:FOR_VEHICLE]->(v:Vehicle)
                RETURN
                    po.po_number AS source_id,
                    po.po_number AS source_label,
                    'PurchaseOrder' AS source_type,
                    properties(po) AS source_properties,
                    type(r) AS relationship,
                    properties(r) AS relationship_properties,
                    v.vehicle_code AS target_id,
                    v.vehicle_type AS target_label,
                    'Vehicle' AS target_type,
                    properties(v) AS target_properties
            }
            RETURN *
            LIMIT $limit
            """
            rows = Neo4jConnection.execute_read(query, {"entity_id": entity_id, "limit": limit})
            return cls._rows_to_visual_graph(rows)

        return {"nodes": [], "edges": []}

