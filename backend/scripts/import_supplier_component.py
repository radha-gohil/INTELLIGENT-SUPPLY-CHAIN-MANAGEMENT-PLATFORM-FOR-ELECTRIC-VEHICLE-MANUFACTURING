import argparse
import csv

from backend.app.database.connection import SessionLocal
from backend.app.models import (
    Component,
    Supplier,
    SupplierComponent
)


def parse_int(value, field_name):
    raw = str(value or "").strip()

    if not raw:
        raise ValueError(
            f"{field_name} is required."
        )

    return int(float(raw))


def parse_float(value, field_name):
    raw = str(value or "").strip()

    if not raw:
        raise ValueError(
            f"{field_name} is required."
        )

    return float(raw)


def import_supplier_components(csv_path: str):
    db = SessionLocal()
    created = 0
    updated = 0
    processed_pairs = set()
    imported_supplier_ids = set()

    try:
        with open(
            csv_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            required_columns = {
                "supplier_id",
                "part_id",
                "unit_cost",
                "lead_time_days",
                "minimum_order_quantity",
                "monthly_capacity"
            }

            actual_columns = set(reader.fieldnames or [])
            missing_columns = (
                required_columns - actual_columns
            )

            if missing_columns:
                raise ValueError(
                    "Missing supplier-component columns: "
                    + ", ".join(
                        sorted(missing_columns)
                    )
                )

            rows = list(reader)

        for row in rows:
            supplier_code = (
                row["supplier_id"].strip()
            )
            part_id = row["part_id"].strip()

            supplier = (
                db.query(Supplier)
                .filter(
                    Supplier.supplier_code
                    == supplier_code
                )
                .first()
            )

            if supplier is None:
                raise ValueError(
                    "Supplier not found for "
                    f"{supplier_code}. "
                    "Import supplier_master.csv first."
                )

            component = (
                db.query(Component)
                .filter(
                    Component.part_id == part_id
                )
                .first()
            )

            if component is None:
                raise ValueError(
                    "Component not found for "
                    f"{part_id}. "
                    "Import component_master.csv first."
                )

            imported_supplier_ids.add(
                supplier.id
            )

            pair = (
                supplier.id,
                component.id
            )

            if pair in processed_pairs:
                raise ValueError(
                    "Duplicate supplier-component "
                    "mapping detected for "
                    f"{supplier_code}/{part_id}."
                )

            processed_pairs.add(pair)

            mapping = (
                db.query(SupplierComponent)
                .filter(
                    SupplierComponent.supplier_id
                    == supplier.id,
                    SupplierComponent.component_id
                    == component.id
                )
                .first()
            )

            if mapping is None:
                mapping = SupplierComponent(
                    supplier_id=supplier.id,
                    component_id=component.id
                )
                db.add(mapping)
                created += 1
            else:
                updated += 1

            mapping.supplier_part_code = None

            mapping.unit_price = parse_float(
                row["unit_cost"],
                "unit_cost"
            )

            mapping.standard_lead_time_days = (
                parse_int(
                    row["lead_time_days"],
                    "lead_time_days"
                )
            )

            mapping.minimum_order_quantity = (
                parse_int(
                    row["minimum_order_quantity"],
                    "minimum_order_quantity"
                )
            )

            mapping.maximum_capacity = parse_int(
                row["monthly_capacity"],
                "monthly_capacity"
            )

            mapping.is_approved = True

        # Preserve old mappings for history but remove legacy
        # mappings from active procurement selection.
        if imported_supplier_ids:
            legacy_mappings = (
                db.query(SupplierComponent)
                .filter(
                    SupplierComponent.supplier_id.in_(
                        imported_supplier_ids
                    )
                )
                .all()
            )

            for mapping in legacy_mappings:
                key = (
                    mapping.supplier_id,
                    mapping.component_id
                )

                if key not in processed_pairs:
                    mapping.is_approved = False

        db.commit()

        print("")
        print(
            "Supplier-component import completed."
        )
        print(f"Created: {created}")
        print(f"Updated: {updated}")
        print(
            "Approved CSV mappings: "
            f"{len(processed_pairs)}"
        )

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Import supplier_component.csv "
            "into PostgreSQL."
        )
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to supplier_component.csv"
    )

    args = parser.parse_args()

    import_supplier_components(
        args.file
    )
