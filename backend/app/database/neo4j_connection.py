import os

import httpx
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# NEO4J AURA CONFIGURATION
# ============================================================

NEO4J_HOST = os.getenv("NEO4J_HOST")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

if not NEO4J_HOST:
    raise ValueError(
        "NEO4J_HOST is not set in the .env file."
    )

if not NEO4J_USERNAME:
    raise ValueError(
        "NEO4J_USERNAME is not set in the .env file."
    )

if not NEO4J_PASSWORD:
    raise ValueError(
        "NEO4J_PASSWORD is not set in the .env file."
    )


# ============================================================
# NEO4J AURA QUERY API CONNECTION
# ============================================================

class Neo4jConnection:
    """
    Connection manager for Neo4j AuraDB using the
    HTTPS Query API instead of the Bolt protocol.

    This is useful on networks where the Bolt TLS
    connection on port 7687 is interrupted.
    """

    @classmethod
    def _get_query_url(cls):
        """
        Build the Neo4j Query API endpoint.
        """

        return (
            f"https://{NEO4J_HOST}"
            f"/db/{NEO4J_DATABASE}/query/v2"
        )

    # --------------------------------------------------------
    # EXECUTE CYPHER QUERY
    # --------------------------------------------------------

    @classmethod
    def execute_query(
        cls,
        query: str,
        parameters: dict | None = None
    ):
        """
        Execute a Cypher query using the Neo4j Aura
        HTTPS Query API.
        """

        url = cls._get_query_url()

        payload = {
            "statement": query,
            "parameters": parameters or {}
        }

        try:

            response = httpx.post(
                url,
                json=payload,
                auth=(
                    NEO4J_USERNAME,
                    NEO4J_PASSWORD
                ),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

            response.raise_for_status()

            result = response.json()

            return result

        except httpx.HTTPStatusError as exc:

            try:
                error_body = exc.response.json()
            except Exception:
                error_body = exc.response.text

            raise RuntimeError(
                "Neo4j Aura Query API returned an error.\n"
                f"HTTP status: {exc.response.status_code}\n"
                f"Response: {error_body}"
            ) from exc

        except httpx.RequestError as exc:

            raise RuntimeError(
                "Unable to connect to Neo4j Aura "
                "through HTTPS.\n"
                f"Reason: {exc}"
            ) from exc

    # --------------------------------------------------------
    # VERIFY CONNECTION
    # --------------------------------------------------------

    @classmethod
    def verify_connection(cls):
        """
        Verify that Python can communicate with AuraDB.
        """

        result = cls.execute_query(
            """
            RETURN
                1 AS test,
                'Neo4j AuraDB connected successfully'
                AS message
            """
        )

        data = result.get("data", {})

        fields = data.get("fields", [])
        values = data.get("values", [])

        if not values:
            raise RuntimeError(
                "Neo4j responded, but the test query "
                "returned no data."
            )

        first_row = values[0]

        row = dict(zip(fields, first_row))

        return {
            "status": "connected",
            "database": NEO4J_DATABASE,
            "test": row.get("test"),
            "message": row.get("message")
        }

    # --------------------------------------------------------
    # EXECUTE READ QUERY
    # --------------------------------------------------------

    @classmethod
    def execute_read(
        cls,
        query: str,
        parameters: dict | None = None
    ):
        """
        Execute a Cypher read query and return rows
        as dictionaries.
        """

        result = cls.execute_query(
            query,
            parameters
        )

        data = result.get("data", {})

        fields = data.get("fields", [])
        values = data.get("values", [])

        return [
            dict(zip(fields, row))
            for row in values
        ]

    # --------------------------------------------------------
    # EXECUTE WRITE QUERY
    # --------------------------------------------------------

    @classmethod
    def execute_write(
        cls,
        query: str,
        parameters: dict | None = None
    ):
        """
        Execute a Cypher write query.
        """

        return cls.execute_query(
            query,
            parameters
        )