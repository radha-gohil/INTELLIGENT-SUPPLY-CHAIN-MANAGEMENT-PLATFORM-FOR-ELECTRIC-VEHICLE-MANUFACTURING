from sqlalchemy import text

from backend.app.database.connection import (
    engine
)


EXPECTED_DATABASE_NAME = (
    "ev_supply_chain_v2"
)


def main():

    database_name = (
        engine.url.database
    )


    print(
        f"Connected database: "
        f"{database_name}"
    )


    if (
        database_name
        !=
        EXPECTED_DATABASE_NAME
    ):

        raise RuntimeError(

            "Safety check failed. "
            "Tracking migration can only run "
            "on ev_supply_chain_v2."

        )


    statements = [

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS vehicle_id INTEGER
        REFERENCES vehicles(id)
        ON DELETE SET NULL
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS required_date DATE
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS urgency VARCHAR(30)
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS tracking_stage VARCHAR(50)
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS current_location VARCHAR(200)
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS tracking_notes TEXT
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS last_tracking_update TIMESTAMP
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS dispatched_at TIMESTAMP
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS arrived_at_warehouse_at TIMESTAMP
        """,

        """
        ALTER TABLE purchase_orders
        ADD COLUMN IF NOT EXISTS source_type VARCHAR(30)
        NOT NULL DEFAULT 'HISTORICAL_IMPORT'
        """,

        """
        UPDATE purchase_orders
        SET source_type = 'HISTORICAL_IMPORT'
        WHERE source_type IS NULL
        """

    ]


    with engine.begin() as connection:

        for statement in statements:

            connection.execute(
                text(statement)
            )


    print(
        "Purchase-order tracking migration completed."
    )


if __name__ == "__main__":

    main()