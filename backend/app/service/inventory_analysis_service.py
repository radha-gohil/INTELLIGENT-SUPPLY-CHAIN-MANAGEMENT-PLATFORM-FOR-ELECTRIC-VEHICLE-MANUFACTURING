from datetime import (
    date,
    timedelta
)

from sqlalchemy.orm import Session

from backend.app.models import (
    Vehicle,
    VehicleBOM,
    Component,
    Inventory,
    PurchaseOrder,
    SupplierComponent
)


# ============================================================
# INVENTORY ANALYSIS SERVICE
# ============================================================

class InventoryAnalysisService:

    # ========================================================
    # ACTIVE PURCHASE ORDER STATUSES
    # ========================================================

    ACTIVE_PO_STATUSES = {

        "PLACED",

        "APPROVED",

        "CONFIRMED",

        "IN_TRANSIT",

        "PARTIAL",

        "OPEN"

    }


    # ========================================================
    # CALCULATE INVENTORY STATUS
    # ========================================================

    @staticmethod
    def calculate_inventory_status(
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
    # GET INVENTORY TOTALS
    # ========================================================

    @staticmethod
    def get_component_inventory_totals(
        db: Session,
        component_id: int
    ):

        records = (

            db.query(Inventory)

            .filter(
                Inventory.component_id
                == component_id
            )

            .all()

        )


        current_stock = sum(

            float(
                item.current_stock or 0
            )

            for item in records

        )


        reserved_stock = sum(

            float(
                item.reserved_stock or 0
            )

            for item in records

        )


        available_stock = sum(

            float(
                item.available_stock or 0
            )

            for item in records

        )


        safety_stock = sum(

            float(
                item.safety_stock or 0
            )

            for item in records

        )


        reorder_level = sum(

            float(
                item.reorder_level or 0
            )

            for item in records

        )


        warehouses_requiring_attention = sum(

            1

            for item in records

            if item.inventory_status
            != "NORMAL"

        )


        return {

            "records":
                records,

            "warehouse_count":
                len(records),

            "current_stock":
                current_stock,

            "reserved_stock":
                reserved_stock,

            "available_stock":
                available_stock,

            "safety_stock":
                safety_stock,

            "reorder_level":
                reorder_level,

            "warehouses_requiring_attention":
                warehouses_requiring_attention

        }


    # ========================================================
    # GET CONFIRMED / ACTIVE INCOMING STOCK
    # ========================================================

    @staticmethod
    def get_incoming_purchase_orders(
        db: Session,
        component_id: int
    ):

        today = date.today()


        purchase_orders = (

            db.query(PurchaseOrder)

            .filter(
                PurchaseOrder.component_id
                == component_id,

                PurchaseOrder.order_status.in_(
                    InventoryAnalysisService
                    .ACTIVE_PO_STATUSES
                )
            )

            .all()

        )


        incoming_quantity = 0.0

        incoming_dates = []


        for purchase_order in purchase_orders:

            # ------------------------------------------------
            # Historical completed/received records should
            # NOT count as future incoming stock.
            # ------------------------------------------------

            if (
                purchase_order.actual_delivery_date
                is not None
            ):

                continue


            quantity_ordered = float(

                purchase_order
                .quantity_ordered
                or 0

            )


            quantity_received = float(

                purchase_order
                .quantity_received
                or 0

            )


            remaining_quantity = max(

                quantity_ordered
                -
                quantity_received,

                0

            )


            if remaining_quantity <= 0:

                continue


            incoming_quantity += (
                remaining_quantity
            )


            if (
                purchase_order
                .expected_delivery_date
                is not None
            ):

                incoming_dates.append(

                    purchase_order
                    .expected_delivery_date

                )


        incoming_expected_date = (

            min(incoming_dates)

            if incoming_dates

            else None

        )


        return {

            "incoming_quantity":
                incoming_quantity,

            "incoming_expected_date":
                incoming_expected_date,

            "incoming_is_overdue":

                (
                    incoming_expected_date
                    is not None
                    and
                    incoming_expected_date
                    < today
                )

        }


    # ========================================================
    # BEST SUPPLIER LEAD TIME
    # ========================================================

    @staticmethod
    def get_best_supplier_lead_time(
        db: Session,
        component_id: int
    ):

        supplier_component = (

            db.query(
                SupplierComponent
            )

            .filter(
                SupplierComponent.component_id
                == component_id,

                SupplierComponent.is_approved
                == True,

                SupplierComponent
                .standard_lead_time_days
                .isnot(None)
            )

            .order_by(
                SupplierComponent
                .standard_lead_time_days
                .asc()
            )

            .first()

        )


        if supplier_component is None:

            return None


        return int(

            supplier_component
            .standard_lead_time_days

        )


    # ========================================================
    # URGENCY ENGINE
    # ========================================================

    @staticmethod
    def calculate_urgency(
        recommended_procurement_quantity: float,
        production_shortage: float,
        required_quantity: float,
        criticality: str,
        days_remaining: int,
        best_lead_time: int | None
    ):

        criticality = str(
            criticality or ""
        ).upper()


        # ----------------------------------------------------
        # NO PROCUREMENT REQUIRED
        # ----------------------------------------------------

        if (
            recommended_procurement_quantity
            <= 0
        ):

            return (
                "OK",
                "Available and incoming stock cover the production requirement and safety stock."
            )


        # ----------------------------------------------------
        # ENOUGH FOR PRODUCTION BUT SAFETY STOCK NEEDS REFILL
        # ----------------------------------------------------

        if production_shortage <= 0:

            return (
                "MEDIUM",
                "Production demand is covered, but stock should be replenished to protect safety stock."
            )


        # ----------------------------------------------------
        # DATE ALREADY REACHED / PASSED
        # ----------------------------------------------------

        if days_remaining <= 0:

            return (
                "URGENT",
                "The required date has been reached and a production shortage exists."
            )


        # ----------------------------------------------------
        # NO SUPPLIER LEAD TIME
        # ----------------------------------------------------

        if best_lead_time is None:

            return (
                "URGENT",
                "A production shortage exists and no approved supplier lead time is available."
            )


        lead_time_buffer = (

            days_remaining
            -
            best_lead_time

        )


        # ----------------------------------------------------
        # SUPPLIER CANNOT ARRIVE IN TIME
        # ----------------------------------------------------

        if lead_time_buffer <= 0:

            return (
                "URGENT",
                "The best supplier lead time is equal to or longer than the time remaining."
            )


        shortage_ratio = (

            production_shortage
            /
            required_quantity

            if required_quantity > 0

            else 0

        )


        # ----------------------------------------------------
        # VERY SMALL TIME BUFFER
        # ----------------------------------------------------

        if lead_time_buffer <= 7:

            return (
                "HIGH",
                "Only a small delivery buffer remains before the required production date."
            )


        # ----------------------------------------------------
        # CRITICAL COMPONENT + LIMITED BUFFER
        # ----------------------------------------------------

        if (
            criticality == "CRITICAL"
            and
            lead_time_buffer <= 14
        ):

            return (
                "HIGH",
                "This is a critical component and the delivery buffer is limited."
            )


        # ----------------------------------------------------
        # LARGE PRODUCTION SHORTAGE
        # ----------------------------------------------------

        if (
            shortage_ratio >= 0.50
            and
            criticality in {
                "CRITICAL",
                "HIGH"
            }
        ):

            return (
                "HIGH",
                "A large percentage of the production requirement is currently unavailable."
            )


        # ----------------------------------------------------
        # NORMAL PROCUREMENT SHORTAGE
        # ----------------------------------------------------

        return (
            "MEDIUM",
            "Procurement is required, but the current supplier lead-time buffer is acceptable."
        )


    # ========================================================
    # GET VEHICLE BOM + CURRENT INVENTORY
    # ========================================================

    @staticmethod
    def get_vehicle_inventory(
        db: Session,
        vehicle_id: int
    ):

        vehicle = (

            db.query(Vehicle)

            .filter(
                Vehicle.id
                == vehicle_id,

                Vehicle.is_active
                == True
            )

            .first()

        )


        if vehicle is None:

            raise ValueError(
                "Vehicle not found."
            )


        bom_records = (

            db.query(
                VehicleBOM,
                Component
            )

            .join(
                Component,

                VehicleBOM.component_id
                ==
                Component.id
            )

            .filter(
                VehicleBOM.vehicle_id
                ==
                vehicle_id
            )

            .order_by(
                Component.part_id
            )

            .all()

        )


        components = []


        for bom, component in bom_records:

            inventory_totals = (

                InventoryAnalysisService
                .get_component_inventory_totals(

                    db=db,

                    component_id=(
                        component.id
                    )

                )

            )


            current_stock = (
                inventory_totals[
                    "current_stock"
                ]
            )


            reserved_stock = (
                inventory_totals[
                    "reserved_stock"
                ]
            )


            available_stock = (
                inventory_totals[
                    "available_stock"
                ]
            )


            safety_stock = (
                inventory_totals[
                    "safety_stock"
                ]
            )


            reorder_level = (
                inventory_totals[
                    "reorder_level"
                ]
            )


            if reorder_level > 0:

                stock_ratio = (

                    available_stock
                    /
                    reorder_level

                )

            else:

                stock_ratio = None


            inventory_status = (

                InventoryAnalysisService
                .calculate_inventory_status(

                    available_stock,
                    safety_stock,
                    reorder_level

                )

            )


            components.append({

                "component_id":
                    component.id,

                "part_id":
                    component.part_id,

                "part_name":
                    component.part_name,

                "category":
                    component.category,

                "sub_category":
                    component.sub_category,

                "criticality":
                    component.criticality,

                "quantity_per_vehicle":
                    float(
                        bom.quantity_per_vehicle
                    ),

                "unit":
                    bom.unit,

                "warehouse_count":
                    inventory_totals[
                        "warehouse_count"
                    ],

                "current_stock":
                    round(
                        current_stock,
                        2
                    ),

                "reserved_stock":
                    round(
                        reserved_stock,
                        2
                    ),

                "available_stock":
                    round(
                        available_stock,
                        2
                    ),

                "safety_stock":
                    round(
                        safety_stock,
                        2
                    ),

                "reorder_level":
                    round(
                        reorder_level,
                        2
                    ),

                "stock_ratio":

                    round(
                        stock_ratio,
                        3
                    )

                    if stock_ratio
                    is not None

                    else None,

                "inventory_status":
                    inventory_status,

                "warehouses_requiring_attention":

                    inventory_totals[
                        "warehouses_requiring_attention"
                    ]

            })


        return {

            "vehicle_id":
                vehicle.id,

            "vehicle_code":
                vehicle.vehicle_code,

            "vehicle_type":
                vehicle.vehicle_type,

            "vehicle_category":
                vehicle.vehicle_category,

            "use_case":
                vehicle.use_case,

            "component_count":
                len(components),

            "components":
                components

        }


    # ========================================================
    # VEHICLE REQUIREMENT ANALYSIS
    # ========================================================

    @staticmethod
    def analyze_vehicle_requirements(
        db: Session,
        vehicle_id: int,
        planned_quantity: int,
        required_date: date
    ):

        if planned_quantity <= 0:

            raise ValueError(
                "Planned vehicle quantity must be greater than zero."
            )


        vehicle = (

            db.query(Vehicle)

            .filter(
                Vehicle.id
                == vehicle_id,

                Vehicle.is_active
                == True
            )

            .first()

        )


        if vehicle is None:

            raise ValueError(
                "Vehicle not found."
            )


        today = date.today()


        days_remaining = (

            required_date
            -
            today

        ).days


        bom_records = (

            db.query(
                VehicleBOM,
                Component
            )

            .join(
                Component,

                VehicleBOM.component_id
                ==
                Component.id
            )

            .filter(
                VehicleBOM.vehicle_id
                ==
                vehicle_id
            )

            .order_by(
                Component.part_id
            )

            .all()

        )


        components = []


        for bom, component in bom_records:

            quantity_per_vehicle = float(

                bom.quantity_per_vehicle
                or 0

            )


            # ------------------------------------------------
            # REQUIRED PRODUCTION QUANTITY
            # ------------------------------------------------

            required_quantity = (

                planned_quantity
                *
                quantity_per_vehicle

            )


            # ------------------------------------------------
            # INVENTORY
            # ------------------------------------------------

            inventory_totals = (

                InventoryAnalysisService
                .get_component_inventory_totals(

                    db=db,

                    component_id=(
                        component.id
                    )

                )

            )


            available_stock = float(

                inventory_totals[
                    "available_stock"
                ]

            )


            safety_stock = float(

                inventory_totals[
                    "safety_stock"
                ]

            )


            reorder_level = float(

                inventory_totals[
                    "reorder_level"
                ]

            )


            inventory_status = (

                InventoryAnalysisService
                .calculate_inventory_status(

                    available_stock,
                    safety_stock,
                    reorder_level

                )

            )


            # ------------------------------------------------
            # INCOMING PO
            # ------------------------------------------------

            incoming_data = (

                InventoryAnalysisService
                .get_incoming_purchase_orders(

                    db=db,

                    component_id=(
                        component.id
                    )

                )

            )


            incoming_quantity = float(

                incoming_data[
                    "incoming_quantity"
                ]

            )


            # ------------------------------------------------
            # PRODUCTION SHORTAGE
            # ------------------------------------------------

            production_shortage = max(

                required_quantity
                -
                available_stock
                -
                incoming_quantity,

                0

            )


            # ------------------------------------------------
            # PROCUREMENT QUANTITY WITH SAFETY STOCK
            # ------------------------------------------------

            recommended_procurement_quantity = max(

                required_quantity
                +
                safety_stock
                -
                available_stock
                -
                incoming_quantity,

                0

            )


            # ------------------------------------------------
            # BEST SUPPLIER LEAD TIME
            # ------------------------------------------------

            best_lead_time = (

                InventoryAnalysisService
                .get_best_supplier_lead_time(

                    db=db,

                    component_id=(
                        component.id
                    )

                )

            )


            if best_lead_time is not None:

                estimated_arrival_date = (

                    today
                    +
                    timedelta(
                        days=best_lead_time
                    )

                )


                lead_time_buffer_days = (

                    days_remaining
                    -
                    best_lead_time

                )

            else:

                estimated_arrival_date = None

                lead_time_buffer_days = None


            # ------------------------------------------------
            # URGENCY
            # ------------------------------------------------

            urgency, urgency_reason = (

                InventoryAnalysisService
                .calculate_urgency(

                    recommended_procurement_quantity=(
                        recommended_procurement_quantity
                    ),

                    production_shortage=(
                        production_shortage
                    ),

                    required_quantity=(
                        required_quantity
                    ),

                    criticality=(
                        component.criticality
                    ),

                    days_remaining=(
                        days_remaining
                    ),

                    best_lead_time=(
                        best_lead_time
                    )

                )

            )


            procurement_required = (

                recommended_procurement_quantity
                >
                0

            )


            components.append({

                "component_id":
                    component.id,

                "part_id":
                    component.part_id,

                "part_name":
                    component.part_name,

                "category":
                    component.category,

                "sub_category":
                    component.sub_category,

                "criticality":
                    str(
                        component.criticality
                    ).upper(),

                "unit":
                    bom.unit,

                "quantity_per_vehicle":
                    quantity_per_vehicle,

                "planned_vehicle_quantity":
                    planned_quantity,

                "required_quantity":
                    round(
                        required_quantity,
                        2
                    ),

                "available_stock":
                    round(
                        available_stock,
                        2
                    ),

                "safety_stock":
                    round(
                        safety_stock,
                        2
                    ),

                "incoming_quantity":
                    round(
                        incoming_quantity,
                        2
                    ),

                "incoming_expected_date":
                    incoming_data[
                        "incoming_expected_date"
                    ],

                "production_shortage":
                    round(
                        production_shortage,
                        2
                    ),

                "recommended_procurement_quantity":
                    round(
                        recommended_procurement_quantity,
                        2
                    ),

                "best_supplier_lead_time_days":
                    best_lead_time,

                "estimated_arrival_date":
                    estimated_arrival_date,

                "days_remaining":
                    days_remaining,

                "lead_time_buffer_days":
                    lead_time_buffer_days,

                "inventory_status":
                    inventory_status,

                "urgency":
                    urgency,

                "urgency_reason":
                    urgency_reason,

                "procurement_required":
                    procurement_required

            })


        sufficient_components = sum(

            1

            for item in components

            if (
                item[
                    "production_shortage"
                ]
                <= 0
            )

        )


        shortage_components = sum(

            1

            for item in components

            if (
                item[
                    "production_shortage"
                ]
                > 0
            )

        )


        procurement_components = sum(

            1

            for item in components

            if item[
                "procurement_required"
            ]

        )


        urgent_components = sum(

            1

            for item in components

            if item[
                "urgency"
            ] == "URGENT"

        )


        high_priority_components = sum(

            1

            for item in components

            if item[
                "urgency"
            ] == "HIGH"

        )


        # Put urgent items at the top of the frontend table.

        urgency_order = {

            "URGENT": 0,

            "HIGH": 1,

            "MEDIUM": 2,

            "OK": 3

        }


        components.sort(

            key=lambda item: (

                urgency_order.get(
                    item["urgency"],
                    99
                ),

                item["part_id"]

            )

        )


        return {

            "vehicle_id":
                vehicle.id,

            "vehicle_code":
                vehicle.vehicle_code,

            "vehicle_type":
                vehicle.vehicle_type,

            "vehicle_category":
                vehicle.vehicle_category,

            "use_case":
                vehicle.use_case,

            "planned_vehicle_quantity":
                planned_quantity,

            "required_date":
                required_date,

            "component_count":
                len(components),

            "sufficient_components":
                sufficient_components,

            "shortage_components":
                shortage_components,

            "procurement_components":
                procurement_components,

            "urgent_components":
                urgent_components,

            "high_priority_components":
                high_priority_components,

            "components":
                components

        }