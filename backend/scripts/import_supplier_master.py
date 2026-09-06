import argparse
import csv

from backend.app.database.connection import (
    SessionLocal
)

from backend.app.models import (
    Supplier
)


# ============================================================
# QUALITY NORMALISATION
# ============================================================

def normalize_quality_rating(
    raw_value
):

    if raw_value is None:

        return None


    value_string = str(
        raw_value
    ).strip()


    if not value_string:

        return None


    value = float(
        value_string
    )


    # --------------------------------------------------------
    # Expected scale = 0 to 5
    # --------------------------------------------------------

    if 0 <= value <= 5:

        return round(
            value,
            2
        )


    # --------------------------------------------------------
    # Defensive correction:
    #
    # supplier_master.csv contains one value such as 90
    # while the remaining quality ratings are around 4.x.
    #
    # Treat a 0-100 value as a percentage-like rating and
    # convert to the 0-5 scale.
    #
    # Example:
    # 90 -> 4.5
    # --------------------------------------------------------

    if 5 < value <= 100:

        normalized = (
            value / 20
        )


        print(
            f"[WARNING] Quality rating "
            f"{value} detected. "
            f"Normalised to "
            f"{normalized:.2f}/5."
        )


        return round(
            normalized,
            2
        )


    raise ValueError(
        f"Invalid quality rating: "
        f"{raw_value}"
    )


# ============================================================
# OPTIONAL FLOAT
# ============================================================

def optional_float(
    value
):

    if value is None:

        return None


    value = str(
        value
    ).strip()


    if not value:

        return None


    return float(
        value
    )


# ============================================================
# OPTIONAL INTEGER
# ============================================================

def optional_int(
    value
):

    if value is None:

        return None


    value = str(
        value
    ).strip()


    if not value:

        return None


    return int(
        float(
            value
        )
    )


# ============================================================
# IMPORT
# ============================================================

def import_supplier_master(
    csv_path: str
):

    db = SessionLocal()


    created = 0
    updated = 0


    try:

        with open(
            csv_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            reader = csv.DictReader(
                csv_file
            )


            required_columns = {

                "supplier_id",
                "supplier_name",
                "location",
                "component_category",
                "lead_time_days",
                "unit_cost",
                "monthly_capacity",
                "quality_rating",
                "reliability_score",
                "status"

            }


            actual_columns = set(
                reader.fieldnames
                or []
            )


            missing_columns = (

                required_columns
                -
                actual_columns

            )


            if missing_columns:

                raise ValueError(

                    "Missing supplier-master "
                    "columns: "

                    + ", ".join(
                        sorted(
                            missing_columns
                        )
                    )

                )


            for row in reader:

                supplier_code = (

                    row[
                        "supplier_id"
                    ]
                    .strip()

                )


                status = (

                    row[
                        "status"
                    ]
                    .strip()
                    .upper()

                    or "ACTIVE"

                )


                supplier = (

                    db.query(
                        Supplier
                    )

                    .filter(
                        Supplier.supplier_code
                        == supplier_code
                    )

                    .first()

                )


                if supplier is None:

                    supplier = Supplier(

                        supplier_code=
                            supplier_code,

                        supplier_name=
                            row[
                                "supplier_name"
                            ].strip()

                    )


                    db.add(
                        supplier
                    )


                    created += 1


                else:

                    updated += 1


                # --------------------------------------------
                # MASTER DATA
                # --------------------------------------------

                supplier.supplier_name = (

                    row[
                        "supplier_name"
                    ]
                    .strip()

                )


                supplier.location = (

                    row[
                        "location"
                    ]
                    .strip()

                    or None

                )


                supplier.component_category = (

                    row[
                        "component_category"
                    ]
                    .strip()

                    or None

                )


                supplier.master_lead_time_days = (

                    optional_int(
                        row[
                            "lead_time_days"
                        ]
                    )

                )


                supplier.master_unit_cost = (

                    optional_float(
                        row[
                            "unit_cost"
                        ]
                    )

                )


                supplier.master_monthly_capacity = (

                    optional_int(
                        row[
                            "monthly_capacity"
                        ]
                    )

                )


                supplier.quality_rating = (

                    normalize_quality_rating(
                        row[
                            "quality_rating"
                        ]
                    )

                )


                supplier.baseline_reliability_score = (

                    optional_float(
                        row[
                            "reliability_score"
                        ]
                    )

                )


                supplier.status = (
                    status
                )


                supplier.is_active = (

                    status
                    ==
                    "ACTIVE"

                )


        db.commit()


        print(
            ""
        )

        print(
            "Supplier master import completed."
        )

        print(
            f"Created: {created}"
        )

        print(
            f"Updated: {updated}"
        )

        print(
            f"Total processed: "
            f"{created + updated}"
        )


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(

        description=(
            "Import supplier_master.csv "
            "into PostgreSQL."
        )

    )


    parser.add_argument(

        "--file",

        required=True,

        help=(
            "Path to supplier_master.csv"
        )

    )


    arguments = (
        parser.parse_args()
    )


    import_supplier_master(
        arguments.file
    )