from sqlalchemy.orm import Session

from backend.app.models import (
    Supplier,
    SupplierComponent,
    SupplierAvailability,
    SupplierPerformance,
    Component
)


class ProcurementService:

    # ============================================================
    # GET SUPPLIER OPTIONS FOR A COMPONENT
    # ============================================================

    @staticmethod
    def get_supplier_options(
        db: Session,
        component_id: int,
        required_quantity: int
    ):

        # --------------------------------------------------------
        # Validate component
        # --------------------------------------------------------

        component = (
            db.query(Component)
            .filter(
                Component.id == component_id,
                Component.is_active == True
            )
            .first()
        )

        if component is None:

            raise ValueError(
                "Component not found."
            )

        # --------------------------------------------------------
        # Find suppliers providing this component
        # --------------------------------------------------------

        supplier_components = (
            db.query(SupplierComponent)
            .filter(
                SupplierComponent.component_id
                == component_id
            )
            .all()
        )

        results = []

        # --------------------------------------------------------
        # Process every supplier
        # --------------------------------------------------------

        for supplier_component in supplier_components:

            supplier = (
                db.query(Supplier)
                .filter(
                    Supplier.id
                    == supplier_component.supplier_id,

                    Supplier.is_active == True
                )
                .first()
            )

            if supplier is None:
                continue

            # ----------------------------------------------------
            # Availability
            # ----------------------------------------------------

            availability = (
                db.query(SupplierAvailability)
                .filter(
                    SupplierAvailability.supplier_id
                    == supplier.id,

                    SupplierAvailability.component_id
                    == component_id
                )
                .first()
            )

            if availability:

                available_quantity = (
                    availability.available_quantity
                )

                committed_quantity = (
                    availability.committed_quantity
                )

                available_to_promise = (
                    availability.available_to_promise
                )

                replenishment_quantity = (
                    availability
                    .expected_replenishment_quantity
                )

                replenishment_date = (
                    availability
                    .expected_replenishment_date
                )

                last_updated = (
                    availability.last_updated
                )

            else:

                available_quantity = 0

                committed_quantity = 0

                available_to_promise = 0

                replenishment_quantity = 0

                replenishment_date = None

                last_updated = None

            # ----------------------------------------------------
            # Historical performance
            # ----------------------------------------------------

            performance_records = (
                db.query(SupplierPerformance)
                .filter(
                    SupplierPerformance.supplier_id
                    == supplier.id
                )
                .all()
            )

            # ----------------------------------------------------
            # Calculate reliability
            # ----------------------------------------------------

            total_orders = sum(
                record.total_orders
                for record in performance_records
            )

            on_time_orders = sum(
                record.on_time_orders
                for record in performance_records
            )

            ordered_quantity = sum(
                record.ordered_quantity
                for record in performance_records
            )

            received_quantity = sum(
                record.received_quantity
                for record in performance_records
            )

            defective_quantity = sum(
                record.defective_quantity
                for record in performance_records
            )

            late_orders = sum(
                record.late_orders
                for record in performance_records
            )

            total_delay = sum(
                record.average_delay_days
                * record.late_orders
                for record in performance_records
            )

            # ----------------------------------------------------
            # Delivery rate
            # ----------------------------------------------------

            if total_orders > 0:

                on_time_delivery_rate = (
                    on_time_orders
                    / total_orders
                ) * 100

            else:

                on_time_delivery_rate = 0.0

            # ----------------------------------------------------
            # Fill rate
            # ----------------------------------------------------

            if ordered_quantity > 0:

                fill_rate = (
                    received_quantity
                    / ordered_quantity
                ) * 100

            else:

                fill_rate = 0.0

            # ----------------------------------------------------
            # Defect rate
            # ----------------------------------------------------

            if received_quantity > 0:

                defect_rate = (
                    defective_quantity
                    / received_quantity
                ) * 100

            else:

                defect_rate = 0.0

            # ----------------------------------------------------
            # Average delay
            # ----------------------------------------------------

            if late_orders > 0:

                average_delay_days = (
                    total_delay
                    / late_orders
                )

            else:

                average_delay_days = 0.0

            # ----------------------------------------------------
            # Reliability score
            # ----------------------------------------------------

            quality_score = max(
                0,
                100 - defect_rate
            )

            reliability_score = (

                (on_time_delivery_rate * 0.50)

                +

                (fill_rate * 0.30)

                +

                (quality_score * 0.20)

            )

            # ----------------------------------------------------
            # Capacity
            # ----------------------------------------------------

            maximum_capacity = (
                supplier_component.maximum_capacity
            )

            # ----------------------------------------------------
            # Can supplier fulfill order?
            # ----------------------------------------------------

            can_fulfill = (
                available_to_promise
                >= required_quantity
            )

            # ----------------------------------------------------
            # Availability percentage
            # ----------------------------------------------------

            if required_quantity > 0:

                availability_percentage = min(
                    (
                        available_to_promise
                        / required_quantity
                    ) * 100,
                    100
                )

            else:

                availability_percentage = 100.0

            # ----------------------------------------------------
            # Build supplier record
            # ----------------------------------------------------

            result = {

                "supplier_id":
                    supplier.id,

                "supplier_code":
                    supplier.supplier_code,

                "supplier_name":
                    supplier.supplier_name,

                "supplier_location":
                    supplier.location,

                "supplier_status":
                    supplier.status,

                "component_id":
                    component.id,

                "part_id":
                    component.part_id,

                "part_name":
                    component.part_name,

                "criticality":
                    component.criticality,

                # Commercial
                "supplier_part_code":
                    supplier_component.supplier_part_code,

                "unit_price":
                    supplier_component.unit_price,

                "minimum_order_quantity":
                    supplier_component
                    .minimum_order_quantity,

                "standard_lead_time_days":
                    supplier_component
                    .standard_lead_time_days,

                "maximum_capacity":
                    maximum_capacity,

                "is_approved":
                    supplier_component.is_approved,

                # Availability
                "available_quantity":
                    available_quantity,

                "committed_quantity":
                    committed_quantity,

                "available_to_promise":
                    available_to_promise,

                "expected_replenishment_quantity":
                    replenishment_quantity,

                "expected_replenishment_date":
                    replenishment_date,

                "last_updated":
                    last_updated,

                # Requirement
                "required_quantity":
                    required_quantity,

                "can_fulfill":
                    can_fulfill,

                "availability_percentage":
                    round(
                        availability_percentage,
                        2
                    ),

                # Performance
                "total_orders":
                    total_orders,

                "on_time_delivery_rate":
                    round(
                        on_time_delivery_rate,
                        2
                    ),

                "fill_rate":
                    round(
                        fill_rate,
                        2
                    ),

                "defect_rate":
                    round(
                        defect_rate,
                        2
                    ),

                "average_delay_days":
                    round(
                        average_delay_days,
                        2
                    ),

                "reliability_score":
                    round(
                        reliability_score,
                        2
                    )
            }

            results.append(result)

        # --------------------------------------------------------
        # Sort
        #
        # Approved suppliers first
        # Fulfillable suppliers next
        # Higher reliability next
        # --------------------------------------------------------

        results.sort(
            key=lambda x: (

                not x["is_approved"],

                not x["can_fulfill"],

                -x["reliability_score"],

                x["standard_lead_time_days"]
                if x["standard_lead_time_days"]
                is not None
                else 999999

            )
        )

        return results