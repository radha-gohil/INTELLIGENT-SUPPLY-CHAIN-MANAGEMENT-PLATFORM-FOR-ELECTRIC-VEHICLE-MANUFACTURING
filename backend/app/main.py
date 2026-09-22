from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)


from backend.app.api.inventory import (
    router as inventory_router
)

from backend.app.api.supplier_performance import (
    router as supplier_performance_router
)

from backend.app.api.supplier import (
    router as supplier_router
)

from backend.app.api.supplier_intelligence import (
    router as supplier_intelligence_router
)

from backend.app.api.supplier_metrics import (
    router as supplier_metrics_router
)

from backend.app.api.supplier_risk import (
    router as supplier_risk_router
)

from backend.app.api.supplier_selection import (
    router as supplier_selection_router
)

from backend.app.api.procurement import (
    router as procurement_router
)

from backend.app.api.supplier_details import (
    router as supplier_details_router
)

from backend.app.api.procurement_decision import (
    router as procurement_decision_router
)

from backend.app.api.graph_rag import (
    router as graph_rag_router
)

from backend.app.api.auth import (
    router as auth_router
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(

    title=
        "EV Supply Chain Management System",

    description=(
        "Intelligent Supply Chain Management "
        "Platform for Electric Vehicle Manufacturing"
    ),

    version=
        "1.1.0"

)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173",

        "http://127.0.0.1:5173"

    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],

)


# ============================================================
# AUTHENTICATION
# ============================================================

app.include_router(
    auth_router
)


# ============================================================
# INVENTORY
# ============================================================

app.include_router(
    inventory_router
)


# ============================================================
# SUPPLIERS
# ============================================================

app.include_router(
    supplier_router
)

app.include_router(
    supplier_details_router
)

app.include_router(
    supplier_intelligence_router
)

app.include_router(
    supplier_performance_router
)

app.include_router(
    supplier_metrics_router
)

app.include_router(
    supplier_risk_router
)

app.include_router(
    supplier_selection_router
)


# ============================================================
# PROCUREMENT
# ============================================================

app.include_router(
    procurement_router
)

app.include_router(
    procurement_decision_router
)


# ============================================================
# KNOWLEDGE GRAPH / GRAPH-RAG
# ============================================================

app.include_router(
    graph_rag_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "application":
            "EV Supply Chain Management System",

        "status":
            "running",

        "version":
            "1.1.0"

    }