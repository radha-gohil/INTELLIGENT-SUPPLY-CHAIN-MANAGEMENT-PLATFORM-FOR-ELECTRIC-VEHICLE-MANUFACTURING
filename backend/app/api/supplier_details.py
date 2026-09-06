from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal

from backend.app.models import (
    Supplier,
    SupplierComponent,
    SupplierAvailability,
    Component
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/supplier-details",
    tags=["Supplier Details"]
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ============================================================
# GET SUPPLIER DETAILS
# ============================================================

@router.get(
    "/supplier/{supplier_id}"
)
def get_supplier_details(

    supplier_id: int,

    db: Session = Depends(get_db)

):

    # ========================================================
    # FIND SUPPLIER
    # ========================================================

    supplier = (

        db.query(Supplier)

        .filter(
            Supplier.id == supplier_id
        )

        .first()

    )


    if supplier is None:

        raise HTTPException(
            status_code=404,
            detail="Supplier not found."
        )


    # ========================================================
    # FIND COMPONENTS SUPPLIED
    # ========================================================

    supplier_components = (

        db.query(SupplierComponent)

        .filter(

            SupplierComponent.supplier_id
            == supplier_id

        )

        .all()

    )


    components = []


    # ========================================================
    # BUILD COMPONENT INFORMATION
    # ========================================================

    for supplier_component in supplier_components:


        # ----------------------------------------------------
        # COMPONENT
        # ----------------------------------------------------

        component = (

            db.query(Component)

            .filter(

                Component.id
                == supplier_component.component_id

            )

            .first()

        )


        if component is None:

            continue


        # ----------------------------------------------------
        # AVAILABILITY
        # ----------------------------------------------------

        availability = (

            db.query(SupplierAvailability)

            .filter(

                SupplierAvailability.supplier_id
                == supplier_id,

                SupplierAvailability.component_id
                == component.id

            )

            .first()

        )


        # ----------------------------------------------------
        # DEFAULT VALUES
        # ----------------------------------------------------

        available_quantity = 0

        committed_quantity = 0

        available_to_promise = 0

        expected_replenishment_quantity = 0

        expected_replenishment_date = None

        last_updated = None


        # ----------------------------------------------------
        # IF AVAILABILITY EXISTS
        # ----------------------------------------------------

        if availability is not None:

            available_quantity = (

                availability.available_quantity

            )

            committed_quantity = (

                availability.committed_quantity

            )

            available_to_promise = (

                availability.available_to_promise

            )

            expected_replenishment_quantity = (

                availability.expected_replenishment_quantity

            )

            expected_replenishment_date = (

                availability.expected_replenishment_date

            )

            last_updated = (

                availability.last_updated

            )


        # ----------------------------------------------------
        # COMPONENT RESULT
        # ----------------------------------------------------

        components.append({

            "component_id":
                component.id,

            "part_id":
                component.part_id,

            "part_name":
                component.part_name,

            "category":
                component.category,

            "unit":
                component.unit,

            "criticality":
                component.criticality,


            # Supplier commercial information
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
                supplier_component.is_approved,


            # Availability
            "available_quantity":
                available_quantity,

            "committed_quantity":
                committed_quantity,

            "available_to_promise":
                available_to_promise,

            "expected_replenishment_quantity":
                expected_replenishment_quantity,

            "expected_replenishment_date":
                expected_replenishment_date,

            "last_updated":
                last_updated

        })


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "supplier_id":
            supplier.id,

        "supplier_code":
            supplier.supplier_code,

        "supplier_name":
            supplier.supplier_name,

        "location":
            supplier.location,

        "contact_email":
            supplier.contact_email,

        "contact_phone":
            supplier.contact_phone,

        "status":
            supplier.status,

        "is_active":
            supplier.is_active,

        "components":
            components

    }