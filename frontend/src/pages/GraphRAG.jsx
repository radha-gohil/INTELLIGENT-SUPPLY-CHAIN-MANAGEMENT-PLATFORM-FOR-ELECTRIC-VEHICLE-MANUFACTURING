import { useCallback, useMemo, useState } from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Drawer,
  IconButton,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography
} from "@mui/material";

import AccountTreeIcon from "@mui/icons-material/AccountTree";
import SearchIcon from "@mui/icons-material/Search";
import InventoryIcon from "@mui/icons-material/Inventory";
import PeopleIcon from "@mui/icons-material/People";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import HubIcon from "@mui/icons-material/Hub";
import WarehouseIcon from "@mui/icons-material/Warehouse";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import CloseIcon from "@mui/icons-material/Close";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { askGraphRAG } from "../services/api";


// ============================================================
// SUGGESTED GRAPH QUESTIONS
// ============================================================

const suggestedQuestions = [
  {
    label: "Battery Pack Suppliers",
    question: "Who supplies the Battery Pack?",
    icon: <PeopleIcon fontSize="small" />
  },
  {
    label: "Electric Car BOM",
    question: "How many components are required for the Electric Car?",
    icon: <DirectionsCarIcon fontSize="small" />
  },
  {
    label: "Chennai Stock",
    question: "How much Battery Pack stock is available in Chennai?",
    icon: <InventoryIcon fontSize="small" />
  },
  {
    label: "Supplier Components",
    question: "What components are supplied by Battery Systems India?",
    icon: <HubIcon fontSize="small" />
  }
];


// ============================================================
// FORMAT LABEL
// ============================================================

function formatLabel(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  return String(value)
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) => character.toUpperCase()
    );
}


// ============================================================
// FORMAT VALUE
// ============================================================

function formatValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "number") {
    return value.toLocaleString();
  }

  if (typeof value === "object") {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }

  return String(value);
}


// ============================================================
// ENTITY ICON
// ============================================================

function getEntityIcon(type) {
  const normalizedType = String(type || "").toLowerCase();

  switch (normalizedType) {
    case "vehicle":
      return <DirectionsCarIcon fontSize="small" />;

    case "component":
      return <HubIcon fontSize="small" />;

    case "supplier":
      return <PeopleIcon fontSize="small" />;

    case "warehouse":
      return <WarehouseIcon fontSize="small" />;

    case "purchaseorder":
    case "purchase_order":
      return <LocalShippingIcon fontSize="small" />;

    default:
      return <AccountTreeIcon fontSize="small" />;
  }
}


// ============================================================
// ENTITY STYLE
// ============================================================

function getEntityStyle(type) {
  const normalizedType = String(type || "").toLowerCase();

  switch (normalizedType) {
    case "vehicle":
      return {
        border: "#7c3aed",
        background: "#f5f3ff",
        badge: "#ede9fe"
      };

    case "component":
      return {
        border: "#2563eb",
        background: "#eff6ff",
        badge: "#dbeafe"
      };

    case "supplier":
      return {
        border: "#16a34a",
        background: "#f0fdf4",
        badge: "#dcfce7"
      };

    case "warehouse":
      return {
        border: "#d97706",
        background: "#fffbeb",
        badge: "#fef3c7"
      };

    case "purchaseorder":
    case "purchase_order":
      return {
        border: "#475569",
        background: "#f8fafc",
        badge: "#e2e8f0"
      };

    default:
      return {
        border: "#64748b",
        background: "#f8fafc",
        badge: "#e2e8f0"
      };
  }
}


// ============================================================
// CUSTOM NEO4J NODE
// ============================================================

function Neo4jNode({ data }) {
  const style = getEntityStyle(data.type);

  const handleClick = (event) => {
    event.stopPropagation();

    if (data.onSelect) {
      data.onSelect(data.original);
    }
  };

  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        style={{
          width: 9,
          height: 9,
          background: style.border,
          border: "2px solid #ffffff"
        }}
      />

      <Paper
        elevation={3}
        onClick={handleClick}
        sx={{
          width: 220,
          minHeight: 105,
          borderRadius: 3,
          border: `2px solid ${style.border}`,
          backgroundColor: style.background,
          cursor: "pointer",
          overflow: "hidden",
          transition: "transform 0.15s ease, box-shadow 0.15s ease",

          "&:hover": {
            transform: "translateY(-2px)",
            boxShadow: "0 10px 24px rgba(15,23,42,0.14)"
          }
        }}
      >
        <Box sx={{ p: 1.5 }}>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
          >
            <Box
              sx={{
                width: 34,
                height: 34,
                borderRadius: 2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: style.badge,
                color: style.border,
                flexShrink: 0
              }}
            >
              {getEntityIcon(data.type)}
            </Box>

            <Box
              sx={{
                minWidth: 0,
                flex: 1
              }}
            >
              <Typography
                fontWeight={700}
                fontSize={14}
                noWrap
                title={data.label}
              >
                {data.label || data.id}
              </Typography>

              <Typography
                variant="caption"
                color="text.secondary"
                noWrap
              >
                {data.id}
              </Typography>
            </Box>
          </Stack>

          <Divider sx={{ my: 1.2 }} />

          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            justifyContent="space-between"
          >
            <Chip
              size="small"
              label={formatLabel(data.type)}
              sx={{
                height: 23,
                backgroundColor: style.badge,
                fontSize: 11,
                fontWeight: 700
              }}
            />

            <Tooltip title="Click to inspect properties">
              <InfoOutlinedIcon
                sx={{
                  fontSize: 17,
                  color: "text.secondary"
                }}
              />
            </Tooltip>
          </Stack>
        </Box>
      </Paper>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          width: 9,
          height: 9,
          background: style.border,
          border: "2px solid #ffffff"
        }}
      />
    </>
  );
}


// ============================================================
// NODE TYPES
// ============================================================

const nodeTypes = {
  neo4jNode: Neo4jNode
};


// ============================================================
// CREATE GRAPH LAYOUT
// ============================================================

function createGraphLayout(
  graphNodes,
  graphEdges,
  onNodeSelect
) {
  if (!Array.isArray(graphNodes)) {
    return {
      nodes: [],
      edges: []
    };
  }

  const groups = {};

  graphNodes.forEach((node) => {
    const type = node.type || "Entity";

    if (!groups[type]) {
      groups[type] = [];
    }

    groups[type].push(node);
  });

  const preferredTypeOrder = [
    "Vehicle",
    "PurchaseOrder",
    "Supplier",
    "Component",
    "Warehouse"
  ];

  const existingTypes = Object.keys(groups);

  const orderedTypes = [
    ...preferredTypeOrder.filter(
      (type) => groups[type]
    ),
    ...existingTypes.filter(
      (type) => !preferredTypeOrder.includes(type)
    )
  ];

  const horizontalGap = 290;
  const verticalGap = 210;

  const positionedNodes = [];

  orderedTypes.forEach((type, rowIndex) => {
    const nodesInRow = groups[type];

    const totalWidth = Math.max(
      0,
      (nodesInRow.length - 1) * horizontalGap
    );

    nodesInRow.forEach((node, index) => {
      const x =
        index * horizontalGap -
        totalWidth / 2;

      const y =
        rowIndex * verticalGap;

      positionedNodes.push({
        id: String(node.id),

        type: "neo4jNode",

        position: {
          x,
          y
        },

        data: {
          id: node.id,

          label:
            node.label ||
            node.name ||
            node.id,

          type:
            node.type ||
            "Entity",

          properties:
            node.properties ||
            {},

          original: node,

          onSelect: onNodeSelect
        }
      });
    });
  });

  const positionedEdges =
    Array.isArray(graphEdges)
      ? graphEdges.map((edge, index) => {
          const relationshipType =
            edge.type ||
            edge.label ||
            "RELATED_TO";

          return {
            id: String(
              edge.id ||
                `${edge.source}-${relationshipType}-${edge.target}-${index}`
            ),

            source: String(edge.source),

            target: String(edge.target),

            label: relationshipType,

            type: "smoothstep",

            animated: false,

            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 20,
              height: 20
            },

            style: {
              strokeWidth: 2,
              stroke: "#64748b"
            },

            labelStyle: {
              fontSize: 11,
              fontWeight: 700,
              fill: "#475569"
            },

            labelBgStyle: {
              fill: "#ffffff",
              fillOpacity: 0.94
            },

            labelBgPadding: [
              6,
              4
            ],

            labelBgBorderRadius: 4,

            data: {
              original: edge
            }
          };
        })
      : [];

  return {
    nodes: positionedNodes,
    edges: positionedEdges
  };
}


// ============================================================
// INTERACTIVE KNOWLEDGE GRAPH
// ============================================================

function KnowledgeGraph({ result }) {
  const [
    selectedItem,
    setSelectedItem
  ] = useState(null);

  const [
    selectedKind,
    setSelectedKind
  ] = useState(null);

  const graph =
    result?.graph ||
    {};

  const rawNodes =
    Array.isArray(graph.nodes)
      ? graph.nodes
      : [];

  const rawEdges =
    Array.isArray(graph.edges)
      ? graph.edges
      : [];

  // ----------------------------------------------------------
  // NODE CLICK
  // ----------------------------------------------------------

  const handleNodeSelect =
    useCallback((node) => {
      setSelectedKind("node");
      setSelectedItem(node);
    }, []);

  // ----------------------------------------------------------
  // CREATE GRAPH
  // ----------------------------------------------------------

  const initialGraph =
    useMemo(
      () =>
        createGraphLayout(
          rawNodes,
          rawEdges,
          handleNodeSelect
        ),
      [
        rawNodes,
        rawEdges,
        handleNodeSelect
      ]
    );

  const [
    nodes,
    ,
    onNodesChange
  ] = useNodesState(
    initialGraph.nodes
  );

  const [
    edges,
    ,
    onEdgesChange
  ] = useEdgesState(
    initialGraph.edges
  );

  // ----------------------------------------------------------
  // RELATIONSHIP CLICK
  // ----------------------------------------------------------

  const handleEdgeClick =
    useCallback(
      (event, edge) => {
        event.stopPropagation();

        const originalEdge =
          edge?.data?.original ||
          edge;

        setSelectedKind(
          "relationship"
        );

        setSelectedItem(
          originalEdge
        );
      },
      []
    );

  // ----------------------------------------------------------
  // EMPTY GRAPH
  // ----------------------------------------------------------

  if (rawNodes.length === 0) {
    return (
      <Box
        sx={{
          py: 7,
          textAlign: "center"
        }}
      >
        <AccountTreeIcon
          sx={{
            fontSize: 54,
            color: "text.secondary"
          }}
        />

        <Typography
          variant="h6"
          fontWeight={700}
          sx={{ mt: 1 }}
        >
          No graph data found
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 0.5 }}
        >
          Try another supply-chain graph question.
        </Typography>
      </Box>
    );
  }

  const selectedProperties =
    selectedItem?.properties ||
    {};

  return (
    <>
      {/* ==================================================== */}
      {/* ENTITY LEGEND */}
      {/* ==================================================== */}

      <Stack
        direction="row"
        spacing={1}
        useFlexGap
        flexWrap="wrap"
        sx={{ mb: 2 }}
      >
        {[
          ...new Set(
            rawNodes
              .map((node) => node.type)
              .filter(Boolean)
          )
        ].map((type) => {
          const style =
            getEntityStyle(type);

          return (
            <Chip
              key={type}
              size="small"
              icon={
                getEntityIcon(type)
              }
              label={
                formatLabel(type)
              }
              sx={{
                backgroundColor:
                  style.badge,
                fontWeight: 600
              }}
            />
          );
        })}
      </Stack>

      {/* ==================================================== */}
      {/* GRAPH */}
      {/* ==================================================== */}

      <Box
        sx={{
          width: "100%",

          height: {
            xs: 520,
            md: 680
          },

          border:
            "1px solid #e2e8f0",

          borderRadius: 3,

          overflow: "hidden",

          backgroundColor:
            "#f8fafc"
        }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}

          onNodesChange={
            onNodesChange
          }

          onEdgesChange={
            onEdgesChange
          }

          onEdgeClick={
            handleEdgeClick
          }

          onPaneClick={() => {
            setSelectedItem(null);
            setSelectedKind(null);
          }}

          fitView

          fitViewOptions={{
            padding: 0.2
          }}

          minZoom={0.1}

          maxZoom={2.5}

          nodesDraggable

          nodesConnectable={false}

          elementsSelectable

          proOptions={{
            hideAttribution: true
          }}
        >
          <Background
            gap={22}
            size={1}
          />

          <Controls
            showInteractive={false}
          />

          <MiniMap
            pannable
            zoomable
            nodeStrokeWidth={3}
          />
        </ReactFlow>
      </Box>

      {/* ==================================================== */}
      {/* PROPERTY DRAWER */}
      {/* ==================================================== */}

      <Drawer
        anchor="right"

        open={
          Boolean(selectedItem)
        }

        onClose={() => {
          setSelectedItem(null);
          setSelectedKind(null);
        }}

        PaperProps={{
          sx: {
            width: {
              xs: "90%",
              sm: 420
            }
          }
        }}
      >
        {selectedItem && (
          <Box sx={{ p: 3 }}>
            {/* HEADER */}

            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="flex-start"
            >
              <Box sx={{ pr: 2 }}>
                <Typography
                  variant="overline"
                  color="text.secondary"
                >
                  {selectedKind === "node"
                    ? "Neo4j Node"
                    : "Neo4j Relationship"}
                </Typography>

                <Typography
                  variant="h6"
                  fontWeight={700}
                >
                  {selectedKind === "node"
                    ? (
                        selectedItem.label ||
                        selectedItem.id ||
                        "Node"
                      )
                    : (
                        selectedItem.type ||
                        selectedItem.label ||
                        "Relationship"
                      )}
                </Typography>
              </Box>

              <IconButton
                onClick={() => {
                  setSelectedItem(null);
                  setSelectedKind(null);
                }}
              >
                <CloseIcon />
              </IconButton>
            </Stack>

            <Divider sx={{ my: 2 }} />

            {/* NODE INFORMATION */}

            {selectedKind === "node" && (
              <Stack
                spacing={1.5}
                sx={{ mb: 3 }}
              >
                <Box>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Node ID
                  </Typography>

                  <Typography
                    fontWeight={600}
                  >
                    {selectedItem.id || "—"}
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Node Type
                  </Typography>

                  <Typography
                    fontWeight={600}
                  >
                    {formatLabel(
                      selectedItem.type
                    )}
                  </Typography>
                </Box>
              </Stack>
            )}

            {/* RELATIONSHIP INFORMATION */}

            {selectedKind ===
              "relationship" && (
              <Stack
                spacing={1.5}
                sx={{ mb: 3 }}
              >
                <Box>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Relationship
                  </Typography>

                  <Typography
                    fontWeight={600}
                  >
                    {selectedItem.type ||
                      selectedItem.label ||
                      "—"}
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Source
                  </Typography>

                  <Typography
                    fontWeight={600}
                  >
                    {selectedItem.source ||
                      "—"}
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Target
                  </Typography>

                  <Typography
                    fontWeight={600}
                  >
                    {selectedItem.target ||
                      "—"}
                  </Typography>
                </Box>
              </Stack>
            )}

            {/* PROPERTIES */}

            <Typography
              fontWeight={700}
              sx={{ mb: 1.5 }}
            >
              Properties
            </Typography>

            {Object.keys(
              selectedProperties
            ).length === 0 ? (
              <Alert severity="info">
                No additional properties
                were returned for this
                {selectedKind === "node"
                  ? " node."
                  : " relationship."}
              </Alert>
            ) : (
              <Stack spacing={1}>
                {Object.entries(
                  selectedProperties
                ).map(
                  ([key, value]) => (
                    <Paper
                      key={key}
                      variant="outlined"
                      sx={{
                        p: 1.5,
                        borderRadius: 2
                      }}
                    >
                      <Typography
                        variant="caption"
                        color="text.secondary"
                      >
                        {formatLabel(key)}
                      </Typography>

                      <Typography
                        variant="body2"
                        fontWeight={600}
                        sx={{
                          wordBreak:
                            "break-word",

                          whiteSpace:
                            "pre-wrap"
                        }}
                      >
                        {formatValue(value)}
                      </Typography>
                    </Paper>
                  )
                )}
              </Stack>
            )}
          </Box>
        )}
      </Drawer>
    </>
  );
}


// ============================================================
// MAIN KNOWLEDGE GRAPH PAGE
// ============================================================

function GraphRAG() {
  const [
    question,
    setQuestion
  ] = useState("");

  const [
    result,
    setResult
  ] = useState(null);

  const [
    loading,
    setLoading
  ] = useState(false);

  const [
    error,
    setError
  ] = useState("");


  // ==========================================================
  // SEARCH KNOWLEDGE GRAPH
  // ==========================================================

  const handleSearch =
    async (
      customQuestion = null
    ) => {
      const finalQuestion =
        typeof customQuestion ===
        "string"
          ? customQuestion
          : question;

      if (
        !finalQuestion.trim()
      ) {
        setError(
          "Please enter a supply-chain graph question."
        );

        return;
      }

      setQuestion(
        finalQuestion
      );

      setLoading(true);

      setError("");

      try {
        const response =
          await askGraphRAG(
            finalQuestion
          );

        setResult(
          response
        );
      } catch (err) {
        console.error(
          "Knowledge Graph error:",
          err
        );

        setResult(null);

        setError(
          err?.message ||
            "Unable to retrieve the Knowledge Graph."
        );
      } finally {
        setLoading(false);
      }
    };


  // ==========================================================
  // ENTER KEY
  // ==========================================================

  const handleKeyDown =
    (event) => {
      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {
        event.preventDefault();

        handleSearch();
      }
    };


  // ==========================================================
  // CLEAR
  // ==========================================================

  const handleClear = () => {
    setQuestion("");
    setResult(null);
    setError("");
  };


  // ==========================================================
  // PAGE
  // ==========================================================

  return (
    <Box
      sx={{
        p: {
          xs: 2,
          md: 3
        },

        maxWidth: 1600,

        mx: "auto"
      }}
    >
      {/* ==================================================== */}
      {/* HEADER */}
      {/* ==================================================== */}

      <Box sx={{ mb: 3 }}>
        <Stack
          direction="row"
          spacing={1.5}
          alignItems="center"
        >
          <AccountTreeIcon
            color="primary"
            sx={{
              fontSize: 34
            }}
          />

          <Box>
            <Typography
              variant="h4"
              fontWeight={700}
            >
              Supply Chain Knowledge Graph
            </Typography>

            <Typography
              color="text.secondary"
              sx={{ mt: 0.25 }}
            >
              Explore EV supply-chain entities
              and relationships stored in Neo4j.
            </Typography>
          </Box>
        </Stack>
      </Box>


      {/* ==================================================== */}
      {/* SEARCH SECTION */}
      {/* ==================================================== */}

      <Paper
        elevation={0}
        sx={{
          p: 3,

          mb: 3,

          border:
            "1px solid #e5e7eb",

          borderRadius: 3
        }}
      >
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          sx={{ mb: 2 }}
        >
          <SearchIcon
            color="primary"
          />

          <Typography
            variant="h6"
            fontWeight={700}
          >
            Search Knowledge Graph
          </Typography>
        </Stack>


        {/* SUGGESTED QUESTIONS */}

        <Stack
          direction="row"
          spacing={1}
          useFlexGap
          flexWrap="wrap"
          sx={{ mb: 2.5 }}
        >
          {suggestedQuestions.map(
            (item) => (
              <Chip
                key={item.label}

                icon={item.icon}

                label={item.label}

                clickable

                variant="outlined"

                disabled={loading}

                onClick={() =>
                  handleSearch(
                    item.question
                  )
                }
              />
            )
          )}
        </Stack>


        {/* QUESTION INPUT */}

        <TextField
          fullWidth

          multiline

          minRows={2}

          maxRows={4}

          value={question}

          placeholder={
            "Example: Who supplies the Battery Pack?"
          }

          disabled={loading}

          onChange={(event) =>
            setQuestion(
              event.target.value
            )
          }

          onKeyDown={
            handleKeyDown
          }
        />


        {/* ACTION BUTTONS */}

        <Box
          sx={{
            mt: 2,

            display: "flex",

            justifyContent:
              "flex-end",

            gap: 1
          }}
        >
          <Button
            variant="outlined"
            disabled={loading}
            onClick={handleClear}
          >
            Clear
          </Button>

          <Button
            variant="contained"

            startIcon={
              loading ? (
                <CircularProgress
                  size={18}
                  color="inherit"
                />
              ) : (
                <SearchIcon />
              )
            }

            disabled={
              loading ||
              !question.trim()
            }

            onClick={() =>
              handleSearch()
            }
          >
            {loading
              ? "Searching..."
              : "Search Graph"}
          </Button>
        </Box>
      </Paper>


      {/* ==================================================== */}
      {/* ERROR */}
      {/* ==================================================== */}

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>
      )}


      {/* ==================================================== */}
      {/* LOADING */}
      {/* ==================================================== */}

      {loading && (
        <Paper
          elevation={0}
          sx={{
            p: 6,

            textAlign: "center",

            borderRadius: 3,

            border:
              "1px solid #e5e7eb"
          }}
        >
          <CircularProgress />

          <Typography
            fontWeight={700}
            sx={{ mt: 2 }}
          >
            Retrieving Neo4j Knowledge Graph...
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 0.5 }}
          >
            Finding matching entities and
            relationships.
          </Typography>
        </Paper>
      )}


      {/* ==================================================== */}
      {/* EMPTY STATE */}
      {/* ==================================================== */}

      {!result &&
        !loading &&
        !error && (
          <Paper
            elevation={0}
            sx={{
              minHeight: 420,

              display: "flex",

              alignItems: "center",

              justifyContent:
                "center",

              border:
                "1px solid #e5e7eb",

              borderRadius: 3
            }}
          >
            <Box
              sx={{
                textAlign: "center",
                p: 4
              }}
            >
              <AccountTreeIcon
                sx={{
                  fontSize: 70,

                  color:
                    "primary.main",

                  opacity: 0.8
                }}
              />

              <Typography
                variant="h6"
                fontWeight={700}
                sx={{ mt: 1.5 }}
              >
                Explore the Knowledge Graph
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mt: 0.5,
                  maxWidth: 500
                }}
              >
                Search for a vehicle,
                component, supplier,
                warehouse or purchase order
                to visualize its Neo4j
                relationships.
              </Typography>
            </Box>
          </Paper>
        )}


      {/* ==================================================== */}
      {/* KNOWLEDGE GRAPH */}
      {/* ==================================================== */}

      {result &&
        !loading && (
          <Card
            variant="outlined"
            sx={{
              borderRadius: 3
            }}
          >
            <CardContent
              sx={{ p: 3 }}
            >
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
              >
                <AccountTreeIcon
                  color="primary"
                />

                <Box>
                  <Typography
                    variant="h6"
                    fontWeight={700}
                  >
                    Knowledge Graph
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                  >
                    Drag nodes, zoom, pan and
                    click entities or
                    relationships to inspect
                    their Neo4j properties.
                  </Typography>
                </Box>
              </Stack>

              <Divider
                sx={{ my: 2 }}
              />

              <KnowledgeGraph
                key={
                  `${
                    result.question || ""
                  }-${
                    result.entity_id || ""
                  }-${Date.now()}`
                }

                result={result}
              />
            </CardContent>
          </Card>
        )}
    </Box>
  );
}


export default GraphRAG;