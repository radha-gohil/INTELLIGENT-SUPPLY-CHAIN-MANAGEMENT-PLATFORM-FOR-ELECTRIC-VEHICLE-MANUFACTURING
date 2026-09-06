from datetime import (
    date,
    datetime,
    timedelta,
    timezone
)

from math import ceil

from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models import (
    Component,
    Inventory,
    InventoryTransaction,
    PurchaseOrder,
    Supplier,
    SupplierAvailability,
    SupplierComponent,
    Vehicle
)

from backend.app.service.stock_movement_service import (
    StockMovementService
)


# ============================================================
# UTC TIME
# ============================================================

def utc_now():

    return (
        datetime
        .now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


# ============================================================
# PURCHASE ORDER SERVICE
# ============================================================

class PurchaseOrderService:

    # ========================================================
    # TRACKING STAGES
    # ========================================================

    ALLOWED_TRACKING_STAGES = {

        "ORDER_PLACED",

        "SUPPLIER_CONFIRMED",

        "READY_FOR_DISPATCH",

        "DISPATCHED",

        "IN_TRANSIT",

        "ARRIVED_AT_WAREHOUSE",

        "PARTIALLY_RECEIVED",

        "RECEIVED",

        "CANCELLED"

    }


    # ========================================================
    # GENERATE PURCHASE ORDER NUMBER
    # ========================================================

    @staticmethod
    def generate_po_number():

        current_date = (
            date.today()
            .strftime(
                "%Y%m%d"
            )
        )


        random_code = (
            uuid4()
            .hex[:8]
            .upper()
        )


        return (
            f"EVPO-{current_date}-{random_code}"
        )


    # ========================================================
    # VERIFY APP-CREATED ORDER
    # ========================================================

    @staticmethod
    def validate_application_order(
        purchase_order
    ):

        if (
            purchase_order.source_type
            != "APP_ORDER"
        ):

            raise ValueError(
                "Historical purchase orders cannot be modified."
            )


    # ========================================================
    # SERIALIZE PURCHASE ORDER
    # ========================================================

    @staticmethod
    def serialize_order(

        purchase_order,

        supplier=None,

        component=None,

        vehicle=None

    ):

        today = date.today()


        quantity_ordered = float(
            purchase_order.quantity_ordered
            or 0
        )


        quantity_received = float(
            purchase_order.quantity_received
            or 0
        )


        remaining_quantity = max(

            quantity_ordered
            -
            quantity_received,

            0
        )


        # ----------------------------------------------------
        # DAYS UNTIL EXPECTED ARRIVAL
        # ----------------------------------------------------

        if (
            purchase_order
            .expected_delivery_date
            is not None
        ):

            days_until_expected_arrival = (

                purchase_order
                .expected_delivery_date
                -
                today

            ).days

        else:

            days_until_expected_arrival = None


        # ----------------------------------------------------
        # DELAY STATUS
        # ----------------------------------------------------

        is_delayed = bool(

            remaining_quantity > 0

            and

            purchase_order
            .expected_delivery_date
            is not None

            and

            purchase_order
            .expected_delivery_date
            < today

            and

            purchase_order.order_status
            not in {
                "DELIVERED",
                "CANCELLED"
            }

        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "id":
                purchase_order.id,

            "po_number":
                purchase_order.po_number,

            "po_date":
                purchase_order.po_date,

            # ------------------------------------------------
            # SUPPLIER
            # ------------------------------------------------

            "supplier_id":
                purchase_order.supplier_id,

            "supplier_code":

                supplier.supplier_code

                if supplier

                else None,

            "supplier_name":

                supplier.supplier_name

                if supplier

                else None,

            # ------------------------------------------------
            # COMPONENT
            # ------------------------------------------------

            "component_id":
                purchase_order.component_id,

            "part_id":

                component.part_id

                if component

                else None,

            "part_name":

                component.part_name

                if component

                else None,

            # ------------------------------------------------
            # VEHICLE
            # ------------------------------------------------

            "vehicle_id":
                purchase_order.vehicle_id,

            "vehicle_code":

                vehicle.vehicle_code

                if vehicle

                else None,

            "vehicle_type":

                vehicle.vehicle_type

                if vehicle

                else None,

            # ------------------------------------------------
            # DESTINATION
            # ------------------------------------------------

            "warehouse":
                purchase_order.warehouse,

            # ------------------------------------------------
            # QUANTITY
            # ------------------------------------------------

            "quantity_ordered":
                quantity_ordered,

            "quantity_received":
                quantity_received,

            "remaining_quantity":
                remaining_quantity,

            # ------------------------------------------------
            # VALUE
            # ------------------------------------------------

            "unit_cost":
                float(
                    purchase_order.unit_cost
                    or 0
                ),

            "order_value":
                float(
                    purchase_order.order_value
                    or 0
                ),

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            "order_status":
                purchase_order.order_status,

            "tracking_stage":
                purchase_order.tracking_stage,

            "current_location":
                purchase_order.current_location,

            "tracking_notes":
                purchase_order.tracking_notes,

            # ------------------------------------------------
            # DELIVERY
            # ------------------------------------------------

            "expected_delivery_date":
                purchase_order
                .expected_delivery_date,

            "actual_delivery_date":
                purchase_order
                .actual_delivery_date,

            "required_date":
                purchase_order.required_date,

            "urgency":
                purchase_order.urgency,

            "days_until_expected_arrival":
                days_until_expected_arrival,

            "is_delayed":
                is_delayed,

            # ------------------------------------------------
            # TRACKING TIMES
            # ------------------------------------------------

            "last_tracking_update":
                purchase_order
                .last_tracking_update,

            "dispatched_at":
                purchase_order
                .dispatched_at,

            "arrived_at_warehouse_at":
                purchase_order
                .arrived_at_warehouse_at,

            "source_type":
                purchase_order.source_type

        }


    # ========================================================
    # GET ONE PURCHASE ORDER
    # ========================================================

    @staticmethod
    def get_order(

        db: Session,

        purchase_order_id: int

    ):

        row = (

            db.query(
                PurchaseOrder,
                Supplier,
                Component,
                Vehicle
            )

            .join(
                Supplier,

                PurchaseOrder.supplier_id
                ==
                Supplier.id
            )

            .join(
                Component,

                PurchaseOrder.component_id
                ==
                Component.id
            )

            .outerjoin(
                Vehicle,

                PurchaseOrder.vehicle_id
                ==
                Vehicle.id
            )

            .filter(
                PurchaseOrder.id
                ==
                purchase_order_id
            )

            .first()

        )


        if row is None:

            raise ValueError(
                "Purchase order not found."
            )


        (
            purchase_order,
            supplier,
            component,
            vehicle
        ) = row


        return (
            PurchaseOrderService
            .serialize_order(

                purchase_order=(
                    purchase_order
                ),

                supplier=(
                    supplier
                ),

                component=(
                    component
                ),

                vehicle=(
                    vehicle
                )
            )
        )


    # ========================================================
    # GET PURCHASE ORDERS
    # ========================================================

    @staticmethod
    def get_orders(

        db: Session,

        include_historical: bool = False

    ):

        query = (

            db.query(
                PurchaseOrder,
                Supplier,
                Component,
                Vehicle
            )

            .join(
                Supplier,

                PurchaseOrder.supplier_id
                ==
                Supplier.id
            )

            .join(
                Component,

                PurchaseOrder.component_id
                ==
                Component.id
            )

            .outerjoin(
                Vehicle,

                PurchaseOrder.vehicle_id
                ==
                Vehicle.id
            )

        )


        # ----------------------------------------------------
        # DEFAULT:
        # Show only orders created from our application.
        #
        # Historical CSV POs can still be requested using:
        #
        # include_historical=true
        # ----------------------------------------------------

        if not include_historical:

            query = query.filter(

                PurchaseOrder.source_type
                ==
                "APP_ORDER"

            )


        rows = (

            query

            .order_by(
                PurchaseOrder.id.desc()
            )

            .all()

        )


        results = []


        for row in rows:

            (
                purchase_order,
                supplier,
                component,
                vehicle
            ) = row


            results.append(

                PurchaseOrderService
                .serialize_order(

                    purchase_order=(
                        purchase_order
                    ),

                    supplier=(
                        supplier
                    ),

                    component=(
                        component
                    ),

                    vehicle=(
                        vehicle
                    )
                )

            )


        return results


    # ========================================================
    # CREATE PURCHASE ORDER
    # ========================================================

    @staticmethod
    def create_order(

        db: Session,

        supplier_id: int,

        component_id: int,

        warehouse: str,

        quantity_ordered: float,

        vehicle_id=None,

        required_date=None,

        urgency=None

    ):

        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        quantity_ordered = float(
            quantity_ordered
        )


        if quantity_ordered <= 0:

            raise ValueError(
                "Purchase order quantity must be greater than zero."
            )


        # ----------------------------------------------------
        # SUPPLIER
        # ----------------------------------------------------

        supplier = (

            db.query(Supplier)

            .filter(
                Supplier.id
                ==
                supplier_id
            )

            .first()

        )


        if supplier is None:

            raise ValueError(
                "Supplier not found."
            )


        if not supplier.is_active:

            raise ValueError(
                "Selected supplier is inactive."
            )


        # ----------------------------------------------------
        # COMPONENT
        # ----------------------------------------------------

        component = (

            db.query(Component)

            .filter(
                Component.id
                ==
                component_id
            )

            .first()

        )


        if component is None:

            raise ValueError(
                "Component not found."
            )


        # ----------------------------------------------------
        # DESTINATION WAREHOUSE
        # ----------------------------------------------------

        warehouse = str(
            warehouse
        ).strip()


        if not warehouse:

            raise ValueError(
                "Destination warehouse is required."
            )


        destination_inventory = (

            db.query(Inventory)

            .filter(
                Inventory.component_id
                ==
                component_id,

                Inventory.warehouse
                ==
                warehouse
            )

            .first()

        )


        if destination_inventory is None:

            raise ValueError(

                "Selected destination warehouse "
                "does not contain an inventory "
                "record for this component."

            )


        # ----------------------------------------------------
        # SUPPLIER-COMPONENT RELATIONSHIP
        # ----------------------------------------------------

        supplier_component = (

            db.query(
                SupplierComponent
            )

            .filter(
                SupplierComponent.supplier_id
                ==
                supplier_id,

                SupplierComponent.component_id
                ==
                component_id,

                SupplierComponent.is_approved
                ==
                True
            )

            .first()

        )


        if supplier_component is None:

            raise ValueError(

                "The selected supplier is not "
                "approved for this component."

            )


        # ----------------------------------------------------
        # MOQ
        # ----------------------------------------------------

        minimum_order_quantity = float(

            supplier_component
            .minimum_order_quantity

            or 1

        )


        if (
            quantity_ordered
            <
            minimum_order_quantity
        ):

            raise ValueError(

                "Requested quantity is below "
                "the supplier minimum order quantity. "
                f"MOQ: {minimum_order_quantity}"

            )


        # ----------------------------------------------------
        # MONTHLY / MAX CAPACITY
        # ----------------------------------------------------

        maximum_capacity = float(

            supplier_component
            .maximum_capacity

            or 0

        )


        if (
            maximum_capacity > 0
            and
            quantity_ordered
            >
            maximum_capacity
        ):

            raise ValueError(

                "Requested quantity exceeds "
                "supplier maximum capacity. "
                f"Capacity: {maximum_capacity}"

            )


        # ----------------------------------------------------
        # SUPPLIER AVAILABILITY
        # ----------------------------------------------------

        supplier_availability = (

            db.query(
                SupplierAvailability
            )

            .filter(
                SupplierAvailability.supplier_id
                ==
                supplier_id,

                SupplierAvailability.component_id
                ==
                component_id
            )

            .first()

        )


        if supplier_availability is not None:

            available_to_promise = float(

                supplier_availability
                .available_to_promise

                or 0

            )


            if (
                quantity_ordered
                >
                available_to_promise
            ):

                raise ValueError(

                    "Requested quantity exceeds "
                    "supplier available-to-promise. "
                    f"Available-to-promise: "
                    f"{available_to_promise}"

                )


        # ----------------------------------------------------
        # VEHICLE
        # ----------------------------------------------------

        vehicle = None


        if vehicle_id is not None:

            vehicle = (

                db.query(Vehicle)

                .filter(
                    Vehicle.id
                    ==
                    vehicle_id
                )

                .first()

            )


            if vehicle is None:

                raise ValueError(
                    "Vehicle not found."
                )


        # ----------------------------------------------------
        # LEAD TIME
        #
        # IMPORTANT:
        # Supplier-component mapping is the source.
        # ----------------------------------------------------

        lead_time_days = int(

            supplier_component
            .standard_lead_time_days

            or 0

        )


        expected_delivery_date = (

            date.today()

            +
            timedelta(
                days=lead_time_days
            )

        )


        # ----------------------------------------------------
        # PRICE
        #
        # IMPORTANT:
        # Component-specific supplier price.
        # ----------------------------------------------------

        unit_cost = float(

            supplier_component
            .unit_price

            or 0

        )


        order_value = (

            quantity_ordered
            *
            unit_cost

        )


        # ----------------------------------------------------
        # CREATE PO
        # ----------------------------------------------------

        purchase_order = PurchaseOrder(

            po_number=(
                PurchaseOrderService
                .generate_po_number()
            ),

            po_date=(
                date.today()
            ),

            supplier_id=(
                supplier_id
            ),

            component_id=(
                component_id
            ),

            vehicle_id=(
                vehicle_id
            ),

            required_date=(
                required_date
            ),

            urgency=(

                str(
                    urgency
                ).upper()

                if urgency

                else None

            ),

            warehouse=(
                warehouse
            ),

            quantity_ordered=(
                quantity_ordered
            ),

            quantity_received=0,

            unit_cost=(
                unit_cost
            ),

            expected_delivery_date=(
                expected_delivery_date
            ),

            actual_delivery_date=None,

            order_status=(
                "PLACED"
            ),

            tracking_stage=(
                "ORDER_PLACED"
            ),

            current_location=(
                supplier.location
                or
                supplier.supplier_name
            ),

            tracking_notes=(
                "Purchase order created."
            ),

            last_tracking_update=(
                utc_now()
            ),

            dispatched_at=None,

            arrived_at_warehouse_at=None,

            # Remaining order quantity
            quantity_shortage=(
                quantity_ordered
            ),

            delivery_delay_days=0,

            order_value=(
                order_value
            ),

            source_type=(
                "APP_ORDER"
            )

        )


        db.add(
            purchase_order
        )


        # ----------------------------------------------------
        # RESERVE SUPPLIER CAPACITY
        # ----------------------------------------------------

        if (
            supplier_availability
            is not None
        ):

            reserved_units = int(
                ceil(
                    quantity_ordered
                )
            )


            supplier_availability.committed_quantity = (

                int(
                    supplier_availability
                    .committed_quantity
                    or 0
                )

                +
                reserved_units

            )


            supplier_availability.available_to_promise = max(

                int(
                    supplier_availability
                    .available_quantity
                    or 0
                )

                -

                int(
                    supplier_availability
                    .committed_quantity
                    or 0
                ),

                0

            )


            supplier_availability.last_updated = (
                utc_now()
            )


        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        db.commit()

        db.refresh(
            purchase_order
        )


        return (
            PurchaseOrderService
            .get_order(

                db=db,

                purchase_order_id=(
                    purchase_order.id
                )
            )
        )


    # ========================================================
    # UPDATE PURCHASE ORDER TRACKING
    # ========================================================

    @staticmethod
    def update_tracking(

        db: Session,

        purchase_order_id: int,

        tracking_stage: str,

        current_location=None,

        tracking_notes=None

    ):

        purchase_order = (

            db.query(
                PurchaseOrder
            )

            .filter(
                PurchaseOrder.id
                ==
                purchase_order_id
            )

            .first()

        )


        if purchase_order is None:

            raise ValueError(
                "Purchase order not found."
            )


        PurchaseOrderService.validate_application_order(
            purchase_order
        )


        if (
            purchase_order.order_status
            ==
            "CANCELLED"
        ):

            raise ValueError(
                "Cancelled purchase orders cannot be updated."
            )


        stage = str(
            tracking_stage
        ).strip().upper()


        if (
            stage
            not in
            PurchaseOrderService
            .ALLOWED_TRACKING_STAGES
        ):

            raise ValueError(
                "Invalid tracking stage."
            )


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


        # ----------------------------------------------------
        # PROTECT STOCK LOGIC
        #
        # RECEIVED / PARTIALLY_RECEIVED should normally be set
        # by the Receive action, not manually.
        # ----------------------------------------------------

        if (
            stage
            ==
            "RECEIVED"
            and
            remaining_quantity > 0
        ):

            raise ValueError(

                "This order still has unreceived quantity. "
                "Use the Receive action first."

            )


        if (
            stage
            ==
            "PARTIALLY_RECEIVED"
            and
            (
                quantity_received <= 0
                or
                remaining_quantity <= 0
            )
        ):

            raise ValueError(

                "PARTIALLY_RECEIVED can only be used "
                "after a partial stock receipt."

            )


        previous_status = (
            purchase_order.order_status
        )


        purchase_order.tracking_stage = (
            stage
        )


        if current_location:

            purchase_order.current_location = (
                str(
                    current_location
                ).strip()
            )


        if tracking_notes is not None:

            purchase_order.tracking_notes = (
                tracking_notes
            )


        purchase_order.last_tracking_update = (
            utc_now()
        )


        # ----------------------------------------------------
        # ORDER PLACED
        # ----------------------------------------------------

        if stage == "ORDER_PLACED":

            purchase_order.order_status = (
                "PLACED"
            )


        # ----------------------------------------------------
        # SUPPLIER CONFIRMED
        # ----------------------------------------------------

        elif stage == "SUPPLIER_CONFIRMED":

            purchase_order.order_status = (
                "CONFIRMED"
            )


        # ----------------------------------------------------
        # READY FOR DISPATCH
        # ----------------------------------------------------

        elif stage == "READY_FOR_DISPATCH":

            purchase_order.order_status = (
                "CONFIRMED"
            )


        # ----------------------------------------------------
        # DISPATCHED
        # ----------------------------------------------------

        elif stage == "DISPATCHED":

            purchase_order.order_status = (
                "CONFIRMED"
            )


            if (
                purchase_order.dispatched_at
                is None
            ):

                purchase_order.dispatched_at = (
                    utc_now()
                )


        # ----------------------------------------------------
        # IN TRANSIT
        # ----------------------------------------------------

        elif stage == "IN_TRANSIT":

            purchase_order.order_status = (
                "IN_TRANSIT"
            )


            if (
                purchase_order.dispatched_at
                is None
            ):

                purchase_order.dispatched_at = (
                    utc_now()
                )


        # ----------------------------------------------------
        # ARRIVED AT WAREHOUSE
        # ----------------------------------------------------

        elif stage == "ARRIVED_AT_WAREHOUSE":

            purchase_order.order_status = (
                "IN_TRANSIT"
            )


            purchase_order.current_location = (

                current_location

                or

                purchase_order.warehouse

            )


            if (
                purchase_order
                .arrived_at_warehouse_at
                is None
            ):

                purchase_order.arrived_at_warehouse_at = (
                    utc_now()
                )


        # ----------------------------------------------------
        # PARTIAL RECEIPT
        # ----------------------------------------------------

        elif stage == "PARTIALLY_RECEIVED":

            purchase_order.order_status = (
                "PARTIAL"
            )


        # ----------------------------------------------------
        # RECEIVED
        # ----------------------------------------------------

        elif stage == "RECEIVED":

            purchase_order.order_status = (
                "DELIVERED"
            )


            purchase_order.actual_delivery_date = (
                purchase_order.actual_delivery_date
                or
                date.today()
            )


            purchase_order.current_location = (
                purchase_order.warehouse
            )


        # ----------------------------------------------------
        # CANCELLED
        # ----------------------------------------------------

        elif stage == "CANCELLED":

            purchase_order.order_status = (
                "CANCELLED"
            )


            # ------------------------------------------------
            # RELEASE UNUSED SUPPLIER CAPACITY
            # ------------------------------------------------

            if (
                previous_status
                !=
                "CANCELLED"
            ):

                remaining_units = int(

                    ceil(
                        remaining_quantity
                    )

                )


                availability = (

                    db.query(
                        SupplierAvailability
                    )

                    .filter(
                        SupplierAvailability.supplier_id
                        ==
                        purchase_order.supplier_id,

                        SupplierAvailability.component_id
                        ==
                        purchase_order.component_id
                    )

                    .first()

                )


                if availability is not None:

                    availability.committed_quantity = max(

                        int(
                            availability
                            .committed_quantity
                            or 0
                        )

                        -
                        remaining_units,

                        0

                    )


                    availability.available_to_promise = max(

                        int(
                            availability
                            .available_quantity
                            or 0
                        )

                        -

                        int(
                            availability
                            .committed_quantity
                            or 0
                        ),

                        0

                    )


                    availability.last_updated = (
                        utc_now()
                    )


        db.commit()


        return (
            PurchaseOrderService
            .get_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                )
            )
        )


    # ========================================================
    # RECEIVE PURCHASE ORDER
    # ========================================================

    @staticmethod
    def receive_order(

        db: Session,

        purchase_order_id: int,

        quantity_received: float

    ):

        # ----------------------------------------------------
        # PURCHASE ORDER
        # ----------------------------------------------------

        purchase_order = (

            db.query(
                PurchaseOrder
            )

            .filter(
                PurchaseOrder.id
                ==
                purchase_order_id
            )

            .first()

        )


        if purchase_order is None:

            raise ValueError(
                "Purchase order not found."
            )


        PurchaseOrderService.validate_application_order(
            purchase_order
        )


        # ----------------------------------------------------
        # STATUS VALIDATION
        # ----------------------------------------------------

        if (
            purchase_order.order_status
            ==
            "CANCELLED"
        ):

            raise ValueError(
                "Cancelled purchase order cannot be received."
            )


        if (
            purchase_order.order_status
            ==
            "DELIVERED"
        ):

            raise ValueError(
                "Purchase order has already been fully received."
            )


        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        quantity_received = float(
            quantity_received
        )


        if quantity_received <= 0:

            raise ValueError(
                "Received quantity must be greater than zero."
            )


        ordered_quantity = float(

            purchase_order
            .quantity_ordered

            or 0

        )


        already_received = float(

            purchase_order
            .quantity_received

            or 0

        )


        remaining_quantity = max(

            ordered_quantity
            -
            already_received,

            0

        )


        if quantity_received > remaining_quantity:

            raise ValueError(

                "Received quantity exceeds "
                "the remaining PO quantity. "
                f"Remaining quantity: "
                f"{remaining_quantity}"

            )


        # ----------------------------------------------------
        # DESTINATION INVENTORY
        # ----------------------------------------------------

        inventory = (

            db.query(Inventory)

            .filter(
                Inventory.component_id
                ==
                purchase_order.component_id,

                Inventory.warehouse
                ==
                purchase_order.warehouse
            )

            .first()

        )


        if inventory is None:

            raise ValueError(

                "Destination inventory record "
                "does not exist."

            )


        # ----------------------------------------------------
        # UPDATE INVENTORY
        #
        # IMPORTANT:
        # We do this inside the SAME transaction as the PO.
        # ----------------------------------------------------

        inventory.current_stock = (

            float(
                inventory.current_stock
                or 0
            )

            +
            quantity_received

        )


        StockMovementService.recalculate_inventory(
            inventory
        )


        # ----------------------------------------------------
        # INVENTORY TRANSACTION
        # ----------------------------------------------------

        transaction_time = (
            utc_now()
        )


        inventory_transaction = (
            InventoryTransaction(

                transaction_id=(

                    StockMovementService
                    .generate_transaction_id(
                        db
                    )

                ),

                component_id=(
                    purchase_order.component_id
                ),

                warehouse=(
                    purchase_order.warehouse
                ),

                transaction_type=(
                    "RECEIPT"
                ),

                quantity=(
                    quantity_received
                ),

                reference_id=(
                    purchase_order.po_number
                ),

                transaction_date=(
                    transaction_time
                ),

                created_at=(
                    transaction_time
                )
            )
        )


        db.add(
            inventory_transaction
        )


        # ----------------------------------------------------
        # UPDATE PURCHASE ORDER
        # ----------------------------------------------------

        purchase_order.quantity_received = (

            already_received
            +
            quantity_received

        )


        remaining_after_receipt = max(

            ordered_quantity
            -
            float(
                purchase_order
                .quantity_received
                or 0
            ),

            0

        )


        purchase_order.quantity_shortage = (
            remaining_after_receipt
        )


        purchase_order.last_tracking_update = (
            utc_now()
        )


        purchase_order.current_location = (
            purchase_order.warehouse
        )


        # ----------------------------------------------------
        # FULL RECEIPT
        # ----------------------------------------------------

        if remaining_after_receipt <= 0:

            purchase_order.order_status = (
                "DELIVERED"
            )


            purchase_order.tracking_stage = (
                "RECEIVED"
            )


            purchase_order.actual_delivery_date = (
                date.today()
            )


            if (
                purchase_order
                .arrived_at_warehouse_at
                is None
            ):

                purchase_order.arrived_at_warehouse_at = (
                    utc_now()
                )


        # ----------------------------------------------------
        # PARTIAL RECEIPT
        # ----------------------------------------------------

        else:

            purchase_order.order_status = (
                "PARTIAL"
            )


            purchase_order.tracking_stage = (
                "PARTIALLY_RECEIVED"
            )


            if (
                purchase_order
                .arrived_at_warehouse_at
                is None
            ):

                purchase_order.arrived_at_warehouse_at = (
                    utc_now()
                )


        # ----------------------------------------------------
        # DELIVERY DELAY
        # ----------------------------------------------------

        if (
            purchase_order
            .expected_delivery_date
            is not None
        ):

            purchase_order.delivery_delay_days = max(

                (
                    date.today()

                    -

                    purchase_order
                    .expected_delivery_date

                ).days,

                0

            )


        # ----------------------------------------------------
        # RELEASE SUPPLIER COMMITMENT
        # ----------------------------------------------------

        availability = (

            db.query(
                SupplierAvailability
            )

            .filter(
                SupplierAvailability.supplier_id
                ==
                purchase_order.supplier_id,

                SupplierAvailability.component_id
                ==
                purchase_order.component_id
            )

            .first()

        )


        if availability is not None:

            received_units = int(
                ceil(
                    quantity_received
                )
            )


            availability.committed_quantity = max(

                int(
                    availability
                    .committed_quantity
                    or 0
                )

                -
                received_units,

                0

            )


            availability.available_to_promise = max(

                int(
                    availability
                    .available_quantity
                    or 0
                )

                -

                int(
                    availability
                    .committed_quantity
                    or 0
                ),

                0

            )


            availability.last_updated = (
                utc_now()
            )


        # ----------------------------------------------------
        # COMMIT INVENTORY + TRANSACTION + PO TOGETHER
        # ----------------------------------------------------

        try:

            db.commit()

        except Exception:

            db.rollback()

            raise


        # ----------------------------------------------------
        # RETURN UPDATED ORDER
        # ----------------------------------------------------

        return (
            PurchaseOrderService
            .get_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                )
            )
        )