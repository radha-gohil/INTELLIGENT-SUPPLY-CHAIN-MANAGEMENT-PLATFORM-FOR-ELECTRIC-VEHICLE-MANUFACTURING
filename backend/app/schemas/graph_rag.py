from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GraphSummaryResponse(BaseModel):
    vehicles: int
    components: int
    suppliers: int
    warehouses: int
    purchase_orders: int
    total_relationships: int


class GraphQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        description="Supply-chain question for Graph-RAG",
    )


class GraphContextResponse(BaseModel):
    entity_type: str
    entity_id: str
    context: Dict[str, Any]


class VehicleContextResponse(BaseModel):
    vehicle: Dict[str, Any]
    components: List[Dict[str, Any]]
    supply_chain: List[Dict[str, Any]]


class ComponentContextResponse(BaseModel):
    component: Dict[str, Any]
    suppliers: List[Dict[str, Any]]
    inventory: List[Dict[str, Any]]
    purchase_orders: List[Dict[str, Any]]


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class VisualGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    error: Optional[str] = None


class GraphRAGResponse(BaseModel):
    status: str = "success"
    question: str
    intent: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    resolved_entities: List[Dict[str, Any]] = Field(default_factory=list)
    answer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    graph: VisualGraph = Field(default_factory=VisualGraph)
