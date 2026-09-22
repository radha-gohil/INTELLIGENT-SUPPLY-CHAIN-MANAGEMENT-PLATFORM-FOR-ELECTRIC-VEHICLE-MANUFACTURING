from datetime import datetime, timedelta
from math import atan2, cos, radians, sin, sqrt
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models import (
    PurchaseOrder,
    PurchaseOrderStatusHistory,
    Shipment,
    ShipmentTrackingPoint,
    Supplier,
)


# ============================================================
# SHIPMENT TRACKING SERVICE
# ============================================================

class ShipmentTrackingService:

    # ========================================================
    # SIMULATED LOCATION COORDINATES
    #
    # IMPORTANT:
    # These are simulation coordinates for the academic
    # shipment tracking system.
    #
    # They are NOT actual supplier GPS coordinates.
    # ========================================================

    LOCATION_COORDINATES = {

        # Supplier state-level simulation origins

        "Tamil Nadu": (
            12.9165,
            79.1325,
        ),

        "Karnataka": (
            12.9716,
            77.5946,
        ),

        "Gujarat": (
            23.0225,
            72.5714,
        ),

        "Maharashtra": (
            18.5204,
            73.8567,
        ),

        # Destination warehouses

        "Chennai": (
            13.0827,
            80.2707,
        ),

        "Hosur": (
            12.7409,
            77.8253,
        ),

        "Coimbatore": (
            11.0168,
            76.9558,
        ),

        "Chengalpattu": (
            12.6819,
            79.9888,
        ),
    }

    # ========================================================
    # GPS SIMULATION SETTINGS
    # ========================================================

    TOTAL_SIMULATION_STEPS = 10

    DEFAULT_SPEED_KMPH = 55.0

    # ========================================================
    # UTC TIME
    # ========================================================

    @staticmethod
    def utc_now():

        return datetime.utcnow()

    # ========================================================
    # NORMALIZE LOCATION
    # ========================================================

    @staticmethod
    def normalize_location(
        location: Optional[str],
    ) -> Optional[str]:

        if location is None:
            return None

        location = location.strip()

        if not location:
            return None

        return location

    # ========================================================
    # GET COORDINATES FOR LOCATION
    # ========================================================

    @staticmethod
    def get_location_coordinates(
        location: Optional[str],
    ):

        location = (
            ShipmentTrackingService
            .normalize_location(
                location
            )
        )

        if location is None:
            return None

        # Exact match

        for (
            location_name,
            coordinates,
        ) in (
            ShipmentTrackingService
            .LOCATION_COORDINATES
            .items()
        ):

            if (
                location.lower()
                ==
                location_name.lower()
            ):

                return coordinates

        # Partial match

        for (
            location_name,
            coordinates,
        ) in (
            ShipmentTrackingService
            .LOCATION_COORDINATES
            .items()
        ):

            if (
                location_name.lower()
                in
                location.lower()
            ):

                return coordinates

        return None

    # ========================================================
    # HAVERSINE DISTANCE
    # ========================================================

    @staticmethod
    def calculate_distance_km(
        latitude_1: float,
        longitude_1: float,
        latitude_2: float,
        longitude_2: float,
    ) -> float:

        earth_radius_km = 6371.0

        lat1 = radians(
            latitude_1
        )

        lon1 = radians(
            longitude_1
        )

        lat2 = radians(
            latitude_2
        )

        lon2 = radians(
            longitude_2
        )

        delta_latitude = (
            lat2 - lat1
        )

        delta_longitude = (
            lon2 - lon1
        )

        a = (
            sin(
                delta_latitude / 2
            ) ** 2
            +
            cos(lat1)
            *
            cos(lat2)
            *
            sin(
                delta_longitude / 2
            ) ** 2
        )

        c = (
            2
            *
            atan2(
                sqrt(a),
                sqrt(1 - a),
            )
        )

        distance = (
            earth_radius_km
            *
            c
        )

        return round(
            distance,
            2,
        )

    # ========================================================
    # INTERPOLATE GPS POSITION
    # ========================================================

    @staticmethod
    def interpolate_position(
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
        progress_percentage: float,
    ):

        progress = (
            progress_percentage
            /
            100.0
        )

        latitude = (
            origin_latitude
            +
            (
                destination_latitude
                -
                origin_latitude
            )
            *
            progress
        )

        longitude = (
            origin_longitude
            +
            (
                destination_longitude
                -
                origin_longitude
            )
            *
            progress
        )

        return (
            round(
                latitude,
                6,
            ),
            round(
                longitude,
                6,
            ),
        )

    # ========================================================
    # CALCULATE ETA
    # ========================================================

    @staticmethod
    def calculate_eta(
        remaining_distance_km: float,
        speed_kmph: float,
    ):

        if (
            speed_kmph is None
            or
            speed_kmph <= 0
        ):

            return None

        if remaining_distance_km <= 0:

            return (
                ShipmentTrackingService
                .utc_now()
            )

        hours_remaining = (
            remaining_distance_km
            /
            speed_kmph
        )

        estimated_arrival = (
            ShipmentTrackingService
            .utc_now()
            +
            timedelta(
                hours=hours_remaining
            )
        )

        return estimated_arrival

    # ========================================================
    # GENERATE SHIPMENT NUMBER
    # ========================================================

    @staticmethod
    def generate_shipment_number(
        purchase_order_id: int,
    ):

        timestamp = (
            ShipmentTrackingService
            .utc_now()
            .strftime(
                "%Y%m%d%H%M%S%f"
            )
        )

        return (
            f"SHP-"
            f"{purchase_order_id}-"
            f"{timestamp}"
        )

    # ========================================================
    # ADD PO STATUS HISTORY
    #
    # We define this here instead of importing
    # PurchaseOrderService.
    #
    # Why?
    #
    # PurchaseOrderService imports ShipmentTrackingService.
    # Importing PurchaseOrderService here would create a
    # circular import.
    # ========================================================

    @staticmethod
    def add_purchase_order_history(
        db: Session,
        purchase_order_id: int,
        from_stage,
        to_stage,
        location=None,
        notes=None,
    ):

        history = (
            PurchaseOrderStatusHistory(

                purchase_order_id=(
                    purchase_order_id
                ),

                from_stage=(
                    str(from_stage)
                    .strip()
                    .upper()
                    if from_stage
                    else None
                ),

                to_stage=(
                    str(to_stage)
                    .strip()
                    .upper()
                ),

                location=(
                    str(location)
                    .strip()
                    if location
                    else None
                ),

                notes=notes,

                changed_at=(
                    ShipmentTrackingService
                    .utc_now()
                ),
            )
        )

        db.add(history)

        return history

    # ========================================================
    # GET SHIPMENT BY SHIPMENT ID
    # ========================================================

    @staticmethod
    def get_shipment(
        db: Session,
        shipment_id: int,
    ):

        shipment = (
            db.query(
                Shipment
            )
            .filter(
                Shipment.id
                ==
                shipment_id
            )
            .first()
        )

        if shipment is None:

            raise ValueError(
                "Shipment not found."
            )

        return shipment

    # ========================================================
    # GET SHIPMENT BY PURCHASE ORDER
    # ========================================================

    @staticmethod
    def get_shipment_by_purchase_order(
        db: Session,
        purchase_order_id: int,
    ):

        shipment = (
            db.query(
                Shipment
            )
            .filter(
                Shipment.purchase_order_id
                ==
                purchase_order_id
            )
            .first()
        )

        return shipment

    # ========================================================
    # CREATE SHIPMENT
    #
    # commit=True
    #     Used when shipment endpoint is called directly.
    #
    # commit=False
    #     Used by PurchaseOrderService so PO + shipment +
    #     history + initial GPS point can be committed
    #     together.
    # ========================================================

    @staticmethod
    def create_shipment(
        db: Session,
        purchase_order_id: int,
        commit: bool = True,
    ):

        # ----------------------------------------------------
        # FIND PURCHASE ORDER
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

        # ----------------------------------------------------
        # ONLY APP ORDERS
        # ----------------------------------------------------

        if (
            purchase_order.source_type
            !=
            "APP_ORDER"
        ):

            raise ValueError(
                "Shipment tracking is available "
                "only for application-created "
                "purchase orders."
            )

        # ----------------------------------------------------
        # SHIPMENT STARTS AFTER DISPATCH
        # ----------------------------------------------------

        allowed_stages = {
            "DISPATCHED",
            "IN_TRANSIT",
        }

        if (
            purchase_order.tracking_stage
            not in
            allowed_stages
        ):

            raise ValueError(
                "Shipment can be created only "
                "after the purchase order "
                "is dispatched."
            )

        # ----------------------------------------------------
        # PREVENT DUPLICATE SHIPMENT
        # ----------------------------------------------------

        existing_shipment = (
            ShipmentTrackingService
            .get_shipment_by_purchase_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                ),
            )
        )

        if existing_shipment is not None:

            return existing_shipment

        # ----------------------------------------------------
        # SUPPLIER
        # ----------------------------------------------------

        supplier = (
            db.query(
                Supplier
            )
            .filter(
                Supplier.id
                ==
                purchase_order.supplier_id
            )
            .first()
        )

        if supplier is None:

            raise ValueError(
                "Supplier not found."
            )

        # ----------------------------------------------------
        # ORIGIN
        # ----------------------------------------------------

        origin_location = (
            supplier.location
        )

        if not origin_location:

            raise ValueError(
                "Supplier location is missing. "
                "GPS shipment simulation "
                "cannot start."
            )

        # ----------------------------------------------------
        # DESTINATION
        # ----------------------------------------------------

        destination_location = (
            purchase_order.warehouse
        )

        if not destination_location:

            raise ValueError(
                "Purchase order warehouse "
                "is missing."
            )

        # ----------------------------------------------------
        # ORIGIN COORDINATES
        # ----------------------------------------------------

        origin_coordinates = (
            ShipmentTrackingService
            .get_location_coordinates(
                origin_location
            )
        )

        if origin_coordinates is None:

            raise ValueError(
                "GPS simulator does not have "
                "coordinates for supplier "
                f"location: {origin_location}"
            )

        # ----------------------------------------------------
        # DESTINATION COORDINATES
        # ----------------------------------------------------

        destination_coordinates = (
            ShipmentTrackingService
            .get_location_coordinates(
                destination_location
            )
        )

        if destination_coordinates is None:

            raise ValueError(
                "GPS simulator does not have "
                "coordinates for warehouse: "
                f"{destination_location}"
            )

        (
            origin_latitude,
            origin_longitude,
        ) = origin_coordinates

        (
            destination_latitude,
            destination_longitude,
        ) = destination_coordinates

        # ----------------------------------------------------
        # ROUTE DISTANCE
        # ----------------------------------------------------

        total_distance_km = (
            ShipmentTrackingService
            .calculate_distance_km(

                origin_latitude,
                origin_longitude,

                destination_latitude,
                destination_longitude,
            )
        )

        speed = (
            ShipmentTrackingService
            .DEFAULT_SPEED_KMPH
        )

        estimated_arrival = (
            ShipmentTrackingService
            .calculate_eta(

                remaining_distance_km=(
                    total_distance_km
                ),

                speed_kmph=speed,
            )
        )

        now = (
            ShipmentTrackingService
            .utc_now()
        )

        # ----------------------------------------------------
        # CREATE SHIPMENT
        # ----------------------------------------------------

        shipment = Shipment(

            purchase_order_id=(
                purchase_order.id
            ),

            shipment_number=(
                ShipmentTrackingService
                .generate_shipment_number(
                    purchase_order.id
                )
            ),

            origin_location=(
                origin_location
            ),

            destination_location=(
                destination_location
            ),

            origin_latitude=(
                origin_latitude
            ),

            origin_longitude=(
                origin_longitude
            ),

            destination_latitude=(
                destination_latitude
            ),

            destination_longitude=(
                destination_longitude
            ),

            current_latitude=(
                origin_latitude
            ),

            current_longitude=(
                origin_longitude
            ),

            status="DISPATCHED",

            progress_percentage=0.0,

            total_distance_km=(
                total_distance_km
            ),

            remaining_distance_km=(
                total_distance_km
            ),

            current_speed_kmph=0.0,

            estimated_arrival=(
                estimated_arrival
            ),

            dispatched_at=(
                purchase_order.dispatched_at
                or
                now
            ),

            arrived_at=None,

            last_location_update=now,

            created_at=now,
        )

        try:

            db.add(
                shipment
            )

            # Need shipment ID for initial GPS point.

            db.flush()

            # ------------------------------------------------
            # INITIAL GPS POINT
            # ------------------------------------------------

            initial_tracking_point = (
                ShipmentTrackingPoint(

                    shipment_id=(
                        shipment.id
                    ),

                    latitude=(
                        origin_latitude
                    ),

                    longitude=(
                        origin_longitude
                    ),

                    speed_kmph=0.0,

                    progress_percentage=0.0,

                    remaining_distance_km=(
                        total_distance_km
                    ),

                    location_name=(
                        origin_location
                    ),

                    status="DISPATCHED",

                    recorded_at=now,
                )
            )

            db.add(
                initial_tracking_point
            )

            # ------------------------------------------------
            # IMPORTANT TRANSACTION CONTROL
            # ------------------------------------------------

            if commit:

                db.commit()

                db.refresh(
                    shipment
                )

            else:

                # Push SQL changes without committing.
                #
                # PurchaseOrderService will commit the whole
                # PO + shipment transaction.

                db.flush()

            return shipment

        except Exception:

            # Only rollback here when this service owns
            # the transaction.
            #
            # With commit=False, the parent service owns
            # rollback handling.

            if commit:

                db.rollback()

            raise

    # ========================================================
    # SIMULATE NEXT GPS LOCATION
    #
    # This method now automatically synchronizes:
    #
    # Shipment DISPATCHED -> IN_TRANSIT
    # PO       DISPATCHED -> IN_TRANSIT
    #
    # and:
    #
    # Shipment IN_TRANSIT -> ARRIVED
    # PO       IN_TRANSIT -> ARRIVED_AT_WAREHOUSE
    # ========================================================

    @staticmethod
    def simulate_next_location(
        db: Session,
        purchase_order_id: int,
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

        if (
            purchase_order.source_type
            !=
            "APP_ORDER"
        ):

            raise ValueError(
                "Shipment simulation is available "
                "only for application-created "
                "purchase orders."
            )

        # ----------------------------------------------------
        # SHIPMENT
        # ----------------------------------------------------

        shipment = (
            ShipmentTrackingService
            .get_shipment_by_purchase_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                ),
            )
        )

        if shipment is None:

            raise ValueError(
                "Shipment has not been created "
                "for this purchase order."
            )

        # ----------------------------------------------------
        # STOP AFTER ARRIVAL / COMPLETION / CANCELLATION
        # ----------------------------------------------------

        if shipment.status in {
            "ARRIVED",
            "COMPLETED",
            "CANCELLED",
        }:

            raise ValueError(
                "Shipment is no longer in transit."
            )

        current_progress = float(
            shipment.progress_percentage
            or
            0.0
        )

        # ----------------------------------------------------
        # MOVE ONE SIMULATION STEP
        # ----------------------------------------------------

        progress_increment = (
            100.0
            /
            ShipmentTrackingService
            .TOTAL_SIMULATION_STEPS
        )

        new_progress = (
            current_progress
            +
            progress_increment
        )

        new_progress = min(
            100.0,
            new_progress,
        )

        # ----------------------------------------------------
        # NEXT GPS POSITION
        # ----------------------------------------------------

        (
            new_latitude,
            new_longitude,
        ) = (
            ShipmentTrackingService
            .interpolate_position(

                shipment.origin_latitude,

                shipment.origin_longitude,

                shipment.destination_latitude,

                shipment.destination_longitude,

                new_progress,
            )
        )

        # ----------------------------------------------------
        # REMAINING DISTANCE
        # ----------------------------------------------------

        remaining_distance = (
            ShipmentTrackingService
            .calculate_distance_km(

                new_latitude,
                new_longitude,

                shipment.destination_latitude,
                shipment.destination_longitude,
            )
        )

        now = (
            ShipmentTrackingService
            .utc_now()
        )

        # ----------------------------------------------------
        # ARRIVED
        # ----------------------------------------------------

        if new_progress >= 100.0:

            new_progress = 100.0

            new_latitude = (
                shipment.destination_latitude
            )

            new_longitude = (
                shipment.destination_longitude
            )

            remaining_distance = 0.0

            speed = 0.0

            status = "ARRIVED"

            location_name = (
                shipment.destination_location
            )

            estimated_arrival = now

        # ----------------------------------------------------
        # IN TRANSIT
        # ----------------------------------------------------

        else:

            speed = (
                ShipmentTrackingService
                .DEFAULT_SPEED_KMPH
            )

            status = "IN_TRANSIT"

            location_name = (
                "In Transit"
            )

            estimated_arrival = (
                ShipmentTrackingService
                .calculate_eta(

                    remaining_distance_km=(
                        remaining_distance
                    ),

                    speed_kmph=speed,
                )
            )

        try:

            # ------------------------------------------------
            # UPDATE SHIPMENT
            # ------------------------------------------------

            shipment.current_latitude = (
                new_latitude
            )

            shipment.current_longitude = (
                new_longitude
            )

            shipment.progress_percentage = (
                new_progress
            )

            shipment.remaining_distance_km = (
                remaining_distance
            )

            shipment.current_speed_kmph = (
                speed
            )

            shipment.status = (
                status
            )

            shipment.estimated_arrival = (
                estimated_arrival
            )

            shipment.last_location_update = (
                now
            )

            if status == "ARRIVED":

                shipment.arrived_at = (
                    now
                )

            # ------------------------------------------------
            # STORE GPS HISTORY
            # ------------------------------------------------

            tracking_point = (
                ShipmentTrackingPoint(

                    shipment_id=(
                        shipment.id
                    ),

                    latitude=(
                        new_latitude
                    ),

                    longitude=(
                        new_longitude
                    ),

                    speed_kmph=(
                        speed
                    ),

                    progress_percentage=(
                        new_progress
                    ),

                    remaining_distance_km=(
                        remaining_distance
                    ),

                    location_name=(
                        location_name
                    ),

                    status=(
                        status
                    ),

                    recorded_at=(
                        now
                    ),
                )
            )

            db.add(
                tracking_point
            )

            # =================================================
            # PO SYNCHRONIZATION
            # =================================================

            current_po_stage = (
                purchase_order.tracking_stage
                or
                "ORDER_PLACED"
            )

            # ------------------------------------------------
            # FIRST GPS MOVEMENT
            #
            # DISPATCHED -> IN_TRANSIT
            # ------------------------------------------------

            if (
                status == "IN_TRANSIT"
                and
                current_po_stage == "DISPATCHED"
            ):

                previous_stage = (
                    current_po_stage
                )

                purchase_order.tracking_stage = (
                    "IN_TRANSIT"
                )

                purchase_order.order_status = (
                    "IN_TRANSIT"
                )

                purchase_order.current_location = (
                    "In Transit"
                )

                purchase_order.tracking_notes = (
                    "Shipment is in transit. "
                    "GPS tracking started."
                )

                purchase_order.last_tracking_update = (
                    now
                )

                if (
                    purchase_order.dispatched_at
                    is None
                ):

                    purchase_order.dispatched_at = (
                        shipment.dispatched_at
                        or
                        now
                    )

                ShipmentTrackingService \
                    .add_purchase_order_history(

                        db=db,

                        purchase_order_id=(
                            purchase_order.id
                        ),

                        from_stage=(
                            previous_stage
                        ),

                        to_stage=(
                            "IN_TRANSIT"
                        ),

                        location=(
                            "In Transit"
                        ),

                        notes=(
                            "Shipment entered transit "
                            "after the first GPS update."
                        ),
                    )

            # ------------------------------------------------
            # KEEP PO LOCATION UPDATED WHILE MOVING
            # ------------------------------------------------

            elif (
                status == "IN_TRANSIT"
                and
                current_po_stage == "IN_TRANSIT"
            ):

                purchase_order.current_location = (
                    "In Transit"
                )

                purchase_order.last_tracking_update = (
                    now
                )

            # ------------------------------------------------
            # GPS ARRIVAL
            #
            # IN_TRANSIT -> ARRIVED_AT_WAREHOUSE
            # ------------------------------------------------

            if status == "ARRIVED":

                current_po_stage = (
                    purchase_order.tracking_stage
                    or
                    "IN_TRANSIT"
                )

                # Normally this will be IN_TRANSIT.
                #
                # We also tolerate DISPATCHED for safety,
                # for example if simulation state was restored
                # from an unusual development/test condition.

                if current_po_stage in {
                    "DISPATCHED",
                    "IN_TRANSIT",
                }:

                    previous_stage = (
                        current_po_stage
                    )

                    purchase_order.tracking_stage = (
                        "ARRIVED_AT_WAREHOUSE"
                    )

                    purchase_order.order_status = (
                        "IN_TRANSIT"
                    )

                    purchase_order.current_location = (
                        purchase_order.warehouse
                    )

                    purchase_order.tracking_notes = (
                        "Shipment arrived at "
                        "the destination warehouse."
                    )

                    purchase_order.last_tracking_update = (
                        now
                    )

                    purchase_order \
                        .arrived_at_warehouse_at = (
                            now
                        )

                    ShipmentTrackingService \
                        .add_purchase_order_history(

                            db=db,

                            purchase_order_id=(
                                purchase_order.id
                            ),

                            from_stage=(
                                previous_stage
                            ),

                            to_stage=(
                                "ARRIVED_AT_WAREHOUSE"
                            ),

                            location=(
                                purchase_order.warehouse
                            ),

                            notes=(
                                "GPS shipment simulation "
                                "reached the destination "
                                "warehouse."
                            ),
                        )

                elif (
                    current_po_stage
                    not in {
                        "ARRIVED_AT_WAREHOUSE",
                        "PARTIALLY_RECEIVED",
                        "RECEIVED",
                    }
                ):

                    raise ValueError(
                        "Shipment reached the destination, "
                        "but the purchase order is in an "
                        "invalid tracking stage: "
                        f"{current_po_stage}"
                    )

            # ------------------------------------------------
            # ONE TRANSACTION
            #
            # Shipment state
            # GPS point
            # PO state
            # PO history
            #
            # all commit together.
            # ------------------------------------------------

            db.commit()

            db.refresh(
                shipment
            )

            return shipment

        except Exception:

            db.rollback()

            raise

    # ========================================================
    # GET GPS TRACKING HISTORY
    # ========================================================

    @staticmethod
    def get_tracking_history(
        db: Session,
        purchase_order_id: int,
    ):

        shipment = (
            ShipmentTrackingService
            .get_shipment_by_purchase_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                ),
            )
        )

        if shipment is None:

            raise ValueError(
                "Shipment not found for this "
                "purchase order."
            )

        tracking_points = (
            db.query(
                ShipmentTrackingPoint
            )
            .filter(
                ShipmentTrackingPoint
                .shipment_id
                ==
                shipment.id
            )
            .order_by(
                ShipmentTrackingPoint
                .recorded_at
                .asc(),

                ShipmentTrackingPoint
                .id
                .asc(),
            )
            .all()
        )

        return tracking_points

    # ========================================================
    # COMPLETE SHIPMENT
    #
    # Called when the complete PO quantity is received.
    #
    # commit=True:
    #     Can be called independently.
    #
    # commit=False:
    #     Used by PurchaseOrderService.receive_order()
    #     so inventory + PO + shipment are one transaction.
    # ========================================================

    @staticmethod
    def complete_shipment(
        db: Session,
        purchase_order_id: int,
        commit: bool = True,
    ):

        shipment = (
            ShipmentTrackingService
            .get_shipment_by_purchase_order(

                db=db,

                purchase_order_id=(
                    purchase_order_id
                ),
            )
        )

        # Shipment may not exist for older orders.

        if shipment is None:

            return None

        if shipment.status == "COMPLETED":

            return shipment

        # ----------------------------------------------------
        # MUST ARRIVE BEFORE COMPLETION
        # ----------------------------------------------------

        if shipment.status != "ARRIVED":

            raise ValueError(
                "Shipment cannot be completed "
                "before it arrives at the warehouse."
            )

        now = (
            ShipmentTrackingService
            .utc_now()
        )

        try:

            shipment.status = (
                "COMPLETED"
            )

            shipment.progress_percentage = (
                100.0
            )

            shipment.remaining_distance_km = (
                0.0
            )

            shipment.current_speed_kmph = (
                0.0
            )

            shipment.current_latitude = (
                shipment.destination_latitude
            )

            shipment.current_longitude = (
                shipment.destination_longitude
            )

            shipment.estimated_arrival = (
                shipment.arrived_at
                or
                now
            )

            shipment.last_location_update = (
                now
            )

            # ------------------------------------------------
            # TRANSACTION CONTROL
            # ------------------------------------------------

            if commit:

                db.commit()

                db.refresh(
                    shipment
                )

            else:

                # Parent PurchaseOrderService.receive_order()
                # owns the final commit.

                db.flush()

            return shipment

        except Exception:

            if commit:

                db.rollback()

            raise