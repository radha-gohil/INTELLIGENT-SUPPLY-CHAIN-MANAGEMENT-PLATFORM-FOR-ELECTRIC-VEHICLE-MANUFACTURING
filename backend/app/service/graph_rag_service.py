import json
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai

from backend.app.service.graph_retrieval_service import (
    GraphRetrievalService,
)


load_dotenv()


class GraphRAGService:
    """
    Graph-RAG question-answering service for the EV Supply Chain
    Management Platform.

    Flow:

        User Question
              |
              v
        Explicit ID Detection
              |
              v
        Neo4j Natural-Language Entity Resolution
              |
              v
        Intent Detection
              |
              v
        Graph Retrieval Service
              |
              v
        Neo4j Knowledge Graph
              |
              v
        Relevant Graph Context
              |
              v
        Gemini
              |
              v
        Grounded Answer
    """

    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured in the .env file."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    # ========================================================
    # EXPLICIT ID DETECTION
    # ========================================================

    @staticmethod
    def detect_entity(
        question: str
    ) -> Dict[str, Optional[str]]:
        """
        Detect explicit supply-chain identifiers.

        Supported examples:

            EV004
            P001
            S001
            PO001

        Natural-language names are resolved separately using Neo4j.
        """

        question_upper = question.upper()

        # ----------------------------------------------------
        # Vehicle
        # ----------------------------------------------------

        vehicle_match = re.search(
            r"\bEV\d{3}\b",
            question_upper
        )

        if vehicle_match:
            return {
                "entity_type": "vehicle",
                "entity_id": vehicle_match.group(0)
            }

        # ----------------------------------------------------
        # Component
        # ----------------------------------------------------

        component_match = re.search(
            r"\bP\d{3}\b",
            question_upper
        )

        if component_match:
            return {
                "entity_type": "component",
                "entity_id": component_match.group(0)
            }

        # ----------------------------------------------------
        # Supplier
        # ----------------------------------------------------

        supplier_match = re.search(
            r"\bS\d{3}\b",
            question_upper
        )

        if supplier_match:
            return {
                "entity_type": "supplier",
                "entity_id": supplier_match.group(0)
            }

        # ----------------------------------------------------
        # Purchase Order
        # ----------------------------------------------------

        po_match = re.search(
            r"\bPO[-_]?[A-Z0-9]+\b",
            question_upper
        )

        if po_match:
            return {
                "entity_type": "purchase_order",
                "entity_id": po_match.group(0)
            }

        return {
            "entity_type": None,
            "entity_id": None
        }

    # ========================================================
    # QUESTION INTENT DETECTION
    # ========================================================

    @staticmethod
    def detect_intent(
        question: str
    ) -> str:
        """
        Detect the main supply-chain information requested.

        This is intentionally lightweight.

        Gemini generates the final answer, while this method helps
        select the most useful Neo4j context.
        """

        text = question.lower()

        # ----------------------------------------------------
        # Inventory
        # ----------------------------------------------------

        inventory_words = [
            "stock",
            "inventory",
            "available stock",
            "availability in",
            "warehouse stock",
            "safety stock",
            "reorder level",
            "out of stock"
        ]

        if any(
            word in text
            for word in inventory_words
        ):
            return "inventory"

        # ----------------------------------------------------
        # Supplier
        # ----------------------------------------------------

        supplier_words = [
            "supplier",
            "suppliers",
            "supplies",
            "supply",
            "provide",
            "provides",
            "vendor",
            "vendors",
            "who supplies",
            "who provides"
        ]

        if any(
            word in text
            for word in supplier_words
        ):
            return "supplier"

        # ----------------------------------------------------
        # Purchase Order
        # ----------------------------------------------------

        purchase_order_words = [
            "purchase order",
            "purchase orders",
            "po ",
            "order status",
            "ordered",
            "delivery",
            "delivered",
            "delay",
            "delayed",
            "tracking"
        ]

        if any(
            word in text
            for word in purchase_order_words
        ):
            return "purchase_order"

        # ----------------------------------------------------
        # BOM / Vehicle Components
        # ----------------------------------------------------

        bom_words = [
            "component",
            "components",
            "bom",
            "bill of materials",
            "required for",
            "requires",
            "parts",
            "part list"
        ]

        if any(
            word in text
            for word in bom_words
        ):
            return "bom"

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        price_words = [
            "price",
            "cost",
            "unit price",
            "cheapest",
            "expensive"
        ]

        if any(
            word in text
            for word in price_words
        ):
            return "pricing"

        # ----------------------------------------------------
        # Lead Time
        # ----------------------------------------------------

        lead_time_words = [
            "lead time",
            "lead-time",
            "fastest",
            "delivery time"
        ]

        if any(
            word in text
            for word in lead_time_words
        ):
            return "lead_time"

        return "general"

    # ========================================================
    # NATURAL-LANGUAGE ENTITY RESOLUTION
    # ========================================================

    @staticmethod
    def resolve_question_entities(
        question: str
    ) -> List[Dict[str, Any]]:
        """
        Resolve all graph entities mentioned in a question.

        Neo4j performs the resolution.

        Example:

            "How much Battery Pack stock is in Chennai?"

        may resolve:

            Battery Pack -> P001
            Chennai -> Warehouse
        """

        return (
            GraphRetrievalService
            .resolve_entities_from_question(
                question
            )
        )

    # ========================================================
    # ENTITY HELPERS
    # ========================================================

    @staticmethod
    def find_entity(
        entities: List[Dict[str, Any]],
        entity_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Return the highest-ranked entity of a requested type.
        """

        for entity in entities:

            if (
                entity.get("entity_type")
                == entity_type
            ):
                return entity

        return None

    # ========================================================
    # EXPLICIT ENTITY CONTEXT
    # ========================================================

    @staticmethod
    def retrieve_context(
        entity_type: Optional[str],
        entity_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Retrieve context using an explicit graph identifier.
        """

        # ----------------------------------------------------
        # Vehicle
        # ----------------------------------------------------

        if entity_type == "vehicle":

            result = (
                GraphRetrievalService
                .get_vehicle_context(
                    entity_id
                )
            )

            if result is None:
                return {
                    "status": "not_found",
                    "message": (
                        f"Vehicle {entity_id} was not found "
                        "in the Knowledge Graph."
                    )
                }

            return {
                "status": "success",
                "entity_type": "vehicle",
                "entity_id": entity_id,
                "data": result
            }

        # ----------------------------------------------------
        # Component
        # ----------------------------------------------------

        if entity_type == "component":

            result = (
                GraphRetrievalService
                .get_component_context(
                    entity_id,
                    purchase_order_limit=10
                )
            )

            if result is None:
                return {
                    "status": "not_found",
                    "message": (
                        f"Component {entity_id} was not found "
                        "in the Knowledge Graph."
                    )
                }

            return {
                "status": "success",
                "entity_type": "component",
                "entity_id": entity_id,
                "data": result
            }

        # ----------------------------------------------------
        # Supplier
        # ----------------------------------------------------

        if entity_type == "supplier":

            supplier = (
                GraphRetrievalService
                .get_supplier(
                    entity_id
                )
            )

            if supplier is None:
                return {
                    "status": "not_found",
                    "message": (
                        f"Supplier {entity_id} was not found "
                        "in the Knowledge Graph."
                    )
                }

            components = (
                GraphRetrievalService
                .get_supplier_components(
                    entity_id
                )
            )

            purchase_orders = (
                GraphRetrievalService
                .get_supplier_purchase_orders(
                    entity_id,
                    limit=10
                )
            )

            return {
                "status": "success",
                "entity_type": "supplier",
                "entity_id": entity_id,
                "data": {
                    "supplier": supplier,
                    "components": components,
                    "purchase_orders": purchase_orders
                }
            }

        # ----------------------------------------------------
        # Purchase Order
        # ----------------------------------------------------

        if entity_type == "purchase_order":

            purchase_order = (
                GraphRetrievalService
                .get_purchase_order(
                    entity_id
                )
            )

            if purchase_order is None:
                return {
                    "status": "not_found",
                    "message": (
                        f"Purchase order {entity_id} "
                        "was not found in the "
                        "Knowledge Graph."
                    )
                }

            return {
                "status": "success",
                "entity_type": "purchase_order",
                "entity_id": entity_id,
                "data": {
                    "purchase_order":
                        purchase_order
                }
            }

        # ----------------------------------------------------
        # Graph Summary
        # ----------------------------------------------------

        graph_summary = (
            GraphRetrievalService
            .get_graph_summary()
        )

        return {
            "status": "success",
            "entity_type": "graph",
            "entity_id": None,
            "data": {
                "graph_summary": graph_summary
            }
        }

    # ========================================================
    # NATURAL-LANGUAGE CONTEXT RETRIEVAL
    # ========================================================

    @classmethod
    def retrieve_natural_language_context(
        cls,
        question: str,
        entities: List[Dict[str, Any]],
        intent: str
    ) -> Dict[str, Any]:
        """
        Build graph context from entities detected by Neo4j.

        This supports entity combinations such as:

            Component + Warehouse
            Component
            Vehicle
            Supplier
            Warehouse
        """

        vehicle = cls.find_entity(
            entities,
            "vehicle"
        )

        component = cls.find_entity(
            entities,
            "component"
        )

        supplier = cls.find_entity(
            entities,
            "supplier"
        )

        warehouse = cls.find_entity(
            entities,
            "warehouse"
        )

        # ----------------------------------------------------
        # Component + Warehouse
        # ----------------------------------------------------

        if component and warehouse:

            part_id = component["entity_id"]

            warehouse_name = (
                warehouse["entity_id"]
            )

            inventory = (
                GraphRetrievalService
                .get_component_inventory_at_warehouse(
                    part_id,
                    warehouse_name
                )
            )

            component_data = (
                GraphRetrievalService
                .get_component(
                    part_id
                )
            )

            return {
                "status": "success",
                "entity_type":
                    "component_warehouse",
                "entity_id":
                    f"{part_id}@{warehouse_name}",
                "resolved_entities": entities,
                "intent": intent,
                "data": {
                    "component":
                        component_data,
                    "warehouse":
                        warehouse_name,
                    "inventory":
                        inventory
                }
            }

        # ----------------------------------------------------
        # Component
        # ----------------------------------------------------

        if component:

            part_id = component["entity_id"]

            # Supplier-specific component question
            if intent in {
                "supplier",
                "pricing",
                "lead_time"
            }:

                component_data = (
                    GraphRetrievalService
                    .get_component(
                        part_id
                    )
                )

                suppliers = (
                    GraphRetrievalService
                    .get_component_suppliers(
                        part_id
                    )
                )

                return {
                    "status": "success",
                    "entity_type": "component",
                    "entity_id": part_id,
                    "resolved_entities": entities,
                    "intent": intent,
                    "data": {
                        "component":
                            component_data,
                        "suppliers":
                            suppliers
                    }
                }

            # Inventory question
            if intent == "inventory":

                component_data = (
                    GraphRetrievalService
                    .get_component(
                        part_id
                    )
                )

                inventory = (
                    GraphRetrievalService
                    .get_component_inventory(
                        part_id
                    )
                )

                return {
                    "status": "success",
                    "entity_type": "component",
                    "entity_id": part_id,
                    "resolved_entities": entities,
                    "intent": intent,
                    "data": {
                        "component":
                            component_data,
                        "inventory":
                            inventory
                    }
                }

            # Purchase-order question
            if intent == "purchase_order":

                component_data = (
                    GraphRetrievalService
                    .get_component(
                        part_id
                    )
                )

                purchase_orders = (
                    GraphRetrievalService
                    .get_component_purchase_orders(
                        part_id,
                        limit=20
                    )
                )

                return {
                    "status": "success",
                    "entity_type": "component",
                    "entity_id": part_id,
                    "resolved_entities": entities,
                    "intent": intent,
                    "data": {
                        "component":
                            component_data,
                        "purchase_orders":
                            purchase_orders
                    }
                }

            # General component context
            context = (
                GraphRetrievalService
                .get_component_context(
                    part_id,
                    purchase_order_limit=10
                )
            )

            if context is None:
                return {
                    "status": "not_found",
                    "message": (
                        f"Component {part_id} "
                        "was not found."
                    )
                }

            return {
                "status": "success",
                "entity_type": "component",
                "entity_id": part_id,
                "resolved_entities": entities,
                "intent": intent,
                "data": context
            }

        # ----------------------------------------------------
        # Vehicle
        # ----------------------------------------------------

        if vehicle:

            vehicle_code = vehicle["entity_id"]

            context = (
                GraphRetrievalService
                .get_vehicle_context(
                    vehicle_code
                )
            )

            if context is None:
                return {
                    "status": "not_found",
                    "message": (
                        f"Vehicle {vehicle_code} "
                        "was not found."
                    )
                }

            return {
                "status": "success",
                "entity_type": "vehicle",
                "entity_id": vehicle_code,
                "resolved_entities": entities,
                "intent": intent,
                "data": context
            }

        # ----------------------------------------------------
        # Supplier
        # ----------------------------------------------------

        if supplier:

            supplier_code = (
                supplier["entity_id"]
            )

            supplier_data = (
                GraphRetrievalService
                .get_supplier(
                    supplier_code
                )
            )

            components = (
                GraphRetrievalService
                .get_supplier_components(
                    supplier_code
                )
            )

            purchase_orders = (
                GraphRetrievalService
                .get_supplier_purchase_orders(
                    supplier_code,
                    limit=10
                )
            )

            return {
                "status": "success",
                "entity_type": "supplier",
                "entity_id": supplier_code,
                "resolved_entities": entities,
                "intent": intent,
                "data": {
                    "supplier":
                        supplier_data,
                    "components":
                        components,
                    "purchase_orders":
                        purchase_orders
                }
            }

        # ----------------------------------------------------
        # Warehouse
        # ----------------------------------------------------

        if warehouse:

            warehouse_name = (
                warehouse["entity_id"]
            )

            inventory = (
                GraphRetrievalService
                .get_warehouse_inventory(
                    warehouse_name
                )
            )

            return {
                "status": "success",
                "entity_type": "warehouse",
                "entity_id": warehouse_name,
                "resolved_entities": entities,
                "intent": intent,
                "data": {
                    "warehouse":
                        warehouse_name,
                    "inventory":
                        inventory
                }
            }

        # ----------------------------------------------------
        # No known entity
        # ----------------------------------------------------

        graph_summary = (
            GraphRetrievalService
            .get_graph_summary()
        )

        return {
            "status": "success",
            "entity_type": "graph",
            "entity_id": None,
            "resolved_entities": [],
            "intent": intent,
            "data": {
                "graph_summary":
                    graph_summary
            }
        }

    # ========================================================
    # CONTEXT SERIALIZATION
    # ========================================================

    @staticmethod
    def prepare_context(
        context: Dict[str, Any]
    ) -> str:
        """
        Convert structured Neo4j context to JSON.
        """

        return json.dumps(
            context,
            indent=2,
            default=str
        )

    # ========================================================
    # PROMPT CREATION
    # ========================================================

    @staticmethod
    def build_prompt(
        question: str,
        graph_context: str
    ) -> str:
        """
        Build a grounded Graph-RAG prompt.
        """

        return f"""
You are the AI decision-support assistant for an Electric Vehicle
Manufacturing Supply Chain Management Platform.

Your task is to answer the user's question using ONLY the
Knowledge Graph context provided below.

The Knowledge Graph may contain:

- Vehicles
- Vehicle BOM requirements
- Components
- Suppliers
- Supplier-component relationships
- Supplier availability
- Supplier lead times
- Supplier capacity
- Supplier pricing
- Warehouse inventory
- Safety stock
- Reorder levels
- Inventory status
- Purchase orders
- Purchase-order quantities
- Delivery information
- Delivery delays
- Purchase-order tracking information

IMPORTANT RULES:

1. Use the supplied Knowledge Graph context as the factual
   source of truth.

2. Do not invent suppliers, components, quantities, prices,
   inventory levels, purchase orders, lead times, vehicles,
   warehouses, delivery information or other values.

3. If information required to answer the question is not
   present in the supplied context, clearly say that it is
   not available in the retrieved Knowledge Graph context.

4. Never invent an entity identifier.

5. If an entity was resolved from the user's natural-language
   question, use the resolved entity information supplied in
   the context.

6. Keep numerical values exactly consistent with the supplied
   Knowledge Graph data.

7. NEVER add quantities that use different measurement units.

   For example:

       4 Units
       8 Meters
       8 Liters
       1 Set

   must NOT be combined into one total quantity.

8. For a vehicle BOM question, distinguish between:

       - number of distinct component types
       - quantity_per_vehicle for each component

   Do not calculate a combined BOM quantity when the BOM
   contains different measurement units.

9. For inventory questions, distinguish between:

       current_stock
       reserved_stock
       available_stock
       safety_stock
       reorder_level

10. For supplier questions, distinguish between:

       unit_price
       lead_time_days
       maximum_capacity
       available_quantity
       committed_quantity
       available_to_promise

11. Do not claim a supplier is the "best supplier" unless the
    supplied context contains sufficient decision criteria for
    that conclusion.

12. If the user asks which suppliers provide a component,
    list only suppliers actually connected to that component
    in the supplied graph context.

13. If the question specifies a warehouse, answer using that
    warehouse's inventory record rather than inventory from
    other warehouses.

14. Clearly distinguish graph facts from interpretation.

15. Keep the answer concise and directly related to the
    user's question.

USER QUESTION:

{question}

KNOWLEDGE GRAPH CONTEXT:

{graph_context}

Answer the user's question using only the supplied context.
"""

    # ========================================================
    # GEMINI ANSWER GENERATION
    # ========================================================

    def generate_answer(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate the final grounded answer with Gemini.
        """

        graph_context = self.prepare_context(
            context
        )

        prompt = self.build_prompt(
            question=question,
            graph_context=graph_context
        )

        interaction = (
            self.client.interactions.create(
                model=self.model,
                input=prompt
            )
        )

        answer = interaction.output_text

        if not answer:
            return (
                "The language model did not return "
                "an answer."
            )

        return answer.strip()

    # ========================================================
    # FRONTEND VISUAL GRAPH
    # ========================================================

    @staticmethod
    def retrieve_visual_graph(
        context: Dict[str, Any],
        intent: str,
    ) -> Dict[str, Any]:
        """Retrieve a graph-ready Neo4j subgraph for the current answer."""
        entity_type = context.get("entity_type")
        entity_id = context.get("entity_id")

        if not entity_type or entity_type == "graph":
            return {"nodes": [], "edges": []}

        try:
            return GraphRetrievalService.get_visual_graph(
                entity_type=entity_type,
                entity_id=entity_id,
                intent=intent,
                limit=100,
            )
        except Exception as exc:
            # Graph visualization must not break Graph-RAG answering.
            return {
                "nodes": [],
                "edges": [],
                "error": str(exc),
            }

    # ========================================================
    # MAIN GRAPH-RAG PIPELINE
    # ========================================================

    def ask(
        self,
        question: str
    ) -> Dict[str, Any]:
        """
        Complete Graph-RAG pipeline.

        Resolution order:

            1. Validate question
            2. Detect explicit database identifier
            3. Resolve natural-language entities from Neo4j
            4. Detect question intent
            5. Retrieve relevant graph context
            6. Send grounded context to Gemini
            7. Return answer + trace information
        """

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if not question or not question.strip():

            return {
                "status": "error",
                "question": question,
                "message":
                    "Question cannot be empty."
            }

        clean_question = question.strip()

        # ----------------------------------------------------
        # Intent
        # ----------------------------------------------------

        intent = self.detect_intent(
            clean_question
        )

        # ----------------------------------------------------
        # Explicit ID detection
        # ----------------------------------------------------

        explicit_entity = self.detect_entity(
            clean_question
        )

        explicit_type = (
            explicit_entity["entity_type"]
        )

        explicit_id = (
            explicit_entity["entity_id"]
        )

        # ----------------------------------------------------
        # Resolve all natural-language graph entities
        # ----------------------------------------------------

        resolved_entities = (
            self.resolve_question_entities(
                clean_question
            )
        )

        # ----------------------------------------------------
        # Explicit ID exists
        # ----------------------------------------------------

        if explicit_type and explicit_id:

            # Even when an explicit ID exists, use natural-language
            # context when multiple entities are present.
            #
            # Example:
            #
            #   "How much P001 stock is in Chennai?"
            #
            # We need both P001 and Chennai.

            warehouse = self.find_entity(
                resolved_entities,
                "warehouse"
            )

            component = self.find_entity(
                resolved_entities,
                "component"
            )

            if (
                explicit_type == "component"
                and warehouse
            ):

                part_id = explicit_id

                warehouse_name = (
                    warehouse["entity_id"]
                )

                inventory = (
                    GraphRetrievalService
                    .get_component_inventory_at_warehouse(
                        part_id,
                        warehouse_name
                    )
                )

                component_data = (
                    GraphRetrievalService
                    .get_component(
                        part_id
                    )
                )

                context = {
                    "status": "success",
                    "entity_type":
                        "component_warehouse",
                    "entity_id":
                        f"{part_id}@{warehouse_name}",
                    "resolved_entities":
                        resolved_entities,
                    "intent":
                        intent,
                    "data": {
                        "component":
                            component_data,
                        "warehouse":
                            warehouse_name,
                        "inventory":
                            inventory
                    }
                }

            elif (
                explicit_type == "component"
                and component
            ):

                context = (
                    self.retrieve_natural_language_context(
                        question=clean_question,
                        entities=resolved_entities,
                        intent=intent
                    )
                )

            else:

                context = self.retrieve_context(
                    entity_type=explicit_type,
                    entity_id=explicit_id
                )

                context["intent"] = intent
                context["resolved_entities"] = (
                    resolved_entities
                )

        # ----------------------------------------------------
        # No explicit ID
        # ----------------------------------------------------

        else:

            context = (
                self.retrieve_natural_language_context(
                    question=clean_question,
                    entities=resolved_entities,
                    intent=intent
                )
            )

        # ----------------------------------------------------
        # Context retrieval failure
        # ----------------------------------------------------

        if context.get("status") != "success":

            return {
                "status": "not_found",
                "question": clean_question,
                "intent": intent,
                "entity_type":
                    context.get("entity_type"),
                "entity_id":
                    context.get("entity_id"),
                "resolved_entities":
                    resolved_entities,
                "answer": context.get(
                    "message",
                    (
                        "Requested information "
                        "was not found."
                    )
                ),
                "context": context,
                "graph": {"nodes": [], "edges": []}
            }

        # ----------------------------------------------------
        # Gemini grounded answer
        # ----------------------------------------------------

        answer = self.generate_answer(
            question=clean_question,
            context=context
        )

        # ----------------------------------------------------
        # Neo4j subgraph for frontend visualization
        # ----------------------------------------------------

        visual_graph = self.retrieve_visual_graph(
            context=context,
            intent=intent,
        )

        # ----------------------------------------------------
        # Traceable response
        # ----------------------------------------------------

        return {
            "status": "success",
            "question": clean_question,
            "intent": intent,
            "entity_type":
                context.get(
                    "entity_type",
                    explicit_type or "graph"
                ),
            "entity_id":
                context.get(
                    "entity_id",
                    explicit_id
                ),
            "resolved_entities":
                resolved_entities,
            "answer": answer,
            "context": context,
            "graph": visual_graph
        }