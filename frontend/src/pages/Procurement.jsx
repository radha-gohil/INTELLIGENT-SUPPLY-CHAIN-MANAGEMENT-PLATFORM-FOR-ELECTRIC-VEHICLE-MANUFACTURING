import {
  useEffect,
  useMemo,
  useState
} from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography
} from "@mui/material";

import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import StoreIcon from "@mui/icons-material/Store";

import {
  getProcurementDecision,
  getSupplierIntelligence,
  getInventoryByComponent,
  getInventoryVehicles,
  getVehicleInventoryComponents,
  createPurchaseOrder
} from "../services/api";


// ============================================================
// GENERIC VALUE HELPER
// ============================================================

function getValue(
  object,
  possibleKeys,
  fallback = null
) {

  if (!object) {
    return fallback;
  }

  for (const key of possibleKeys) {

    if (
      object[key] !== undefined &&
      object[key] !== null
    ) {

      return object[key];

    }

  }

  return fallback;
}


// ============================================================
// NUMBER FORMAT
// ============================================================

function formatNumber(value) {

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "-";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return number.toLocaleString();
}


// ============================================================
// MONEY FORMAT
// ============================================================

function formatMoney(value) {

  const number =
    Number(value || 0);

  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2
    }
  ).format(number);
}


// ============================================================
// SCORE FORMAT
// ============================================================

function formatScore(value) {

  if (
    value === null ||
    value === undefined
  ) {
    return "-";
  }

  const number =
    Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return number.toFixed(4);
}


// ============================================================
// DATE FORMAT
// ============================================================

function formatDate(value) {

  if (!value) {
    return "-";
  }

  try {

    return new Date(
      `${value}T00:00:00`
    ).toLocaleDateString();

  } catch {

    return value;

  }
}


// ============================================================
// READ INVENTORY PROCUREMENT REQUEST
// ============================================================

function readStoredRequest() {

  try {

    const raw =
      sessionStorage.getItem(
        "inventoryProcurementRequest"
      );

    if (!raw) {
      return null;
    }

    return JSON.parse(raw);

  } catch {

    return null;

  }
}


// ============================================================
// SUPPLIER ID HELPER
// ============================================================

function extractSupplierId(value) {

  if (
    value === null ||
    value === undefined
  ) {
    return null;
  }

  if (typeof value === "number") {
    return value;
  }

  if (typeof value === "string") {

    const number =
      Number(value);

    return Number.isNaN(number)
      ? null
      : number;
  }

  return (
    Number(
      getValue(
        value,
        [
          "supplier_id",
          "id"
        ],
        null
      )
    ) || null
  );
}


// ============================================================
// RISK CHIP
// ============================================================

function RiskChip({
  riskLevel
}) {

  const value =
    String(
      riskLevel ||
      "UNAVAILABLE"
    ).toUpperCase();

  let color = "default";

  if (value === "LOW") {
    color = "success";
  }

  else if (value === "MEDIUM") {
    color = "warning";
  }

  else if (
    value === "HIGH" ||
    value === "CRITICAL"
  ) {
    color = "error";
  }

  return (
    <Chip
      label={value}
      size="small"
      color={color}
      sx={{
        fontWeight: 700
      }}
    />
  );
}


// ============================================================
// URGENCY CHIP
// ============================================================

function UrgencyChip({
  urgency
}) {

  const value =
    String(
      urgency ||
      "NORMAL"
    ).toUpperCase();

  let color = "success";

  if (value === "URGENT") {
    color = "error";
  }

  else if (value === "HIGH") {
    color = "warning";
  }

  else if (value === "MEDIUM") {
    color = "info";
  }

  return (
    <Chip
      label={value}
      size="small"
      color={color}
      sx={{
        fontWeight: 700
      }}
    />
  );
}


// ============================================================
// NORMALIZE COMPONENT
// ============================================================

function normalizeComponent(item) {

  const componentId =
    Number(
      getValue(
        item,
        [
          "component_id",
          "id"
        ],
        0
      )
    );

  if (!componentId) {
    return null;
  }

  return {

    component_id:
      componentId,

    component_name:
      getValue(
        item,
        [
          "component_name",
          "part_name",
          "name",
          "description"
        ],
        `Component ${componentId}`
      ),

    part_number:
      getValue(
        item,
        [
          "part_number",
          "part_id",
          "component_code",
          "part_code",
          "code"
        ],
        ""
      )

  };
}


// ============================================================
// NORMALIZE SUPPLIER
// ============================================================

function normalizeSupplier(
  option,
  intelligence
) {

  const supplierId =
    extractSupplierId(option);

  const commercial =
    intelligence || {};

  return {

    supplier_id:
      supplierId,

    supplier_code:
      getValue(
        option,
        [
          "supplier_code"
        ],
        commercial.supplier_code ||
        "-"
      ),

    supplier_name:
      getValue(
        option,
        [
          "supplier_name",
          "name"
        ],
        commercial.supplier_name ||
        `Supplier ${supplierId}`
      ),

    supplier_location:
      getValue(
        option,
        [
          "supplier_location",
          "location"
        ],
        commercial.supplier_location ||
        "-"
      ),

    final_score:
      getValue(
        option,
        [
          "final_score",
          "total_score",
          "weighted_score",
          "score"
        ],
        null
      ),

    availability_score:
      getValue(
        option,
        [
          "availability_score"
        ],
        null
      ),

    fulfillment_score:
      getValue(
        option,
        [
          "fulfillment_score"
        ],
        null
      ),

    reliability_score:
      getValue(
        option,
        [
          "reliability_score"
        ],
        null
      ),

    quality_score:
      getValue(
        option,
        [
          "quality_score"
        ],
        null
      ),

    ai_risk_score:
      getValue(
        option,
        [
          "ai_risk_score",
          "risk_score"
        ],
        null
      ),

    price_score:
      getValue(
        option,
        [
          "price_score"
        ],
        null
      ),

    lead_time_score:
      getValue(
        option,
        [
          "lead_time_score"
        ],
        null
      ),

    unit_price:
      Number(
        getValue(
          option,
          [
            "unit_price",
            "unit_cost",
            "price"
          ],
          commercial.unit_price ||
          0
        )
      ),

    minimum_order_quantity:
      Number(
        getValue(
          option,
          [
            "minimum_order_quantity",
            "moq"
          ],
          commercial.minimum_order_quantity ||
          1
        )
      ),

    standard_lead_time_days:
      Number(
        getValue(
          option,
          [
            "standard_lead_time_days",
            "lead_time_days",
            "lead_time"
          ],
          commercial.standard_lead_time_days ||
          0
        )
      ),

    maximum_capacity:
      getValue(
        option,
        [
          "maximum_capacity",
          "monthly_capacity",
          "capacity"
        ],
        commercial.maximum_capacity
      ),

    available_quantity:
      getValue(
        option,
        [
          "available_quantity"
        ],
        commercial.available_quantity
      ),

    committed_quantity:
      getValue(
        option,
        [
          "committed_quantity"
        ],
        commercial.committed_quantity
      ),

    available_to_promise:
      getValue(
        option,
        [
          "available_to_promise",
          "availability"
        ],
        commercial.available_to_promise
      ),

    is_approved:
      getValue(
        option,
        [
          "is_approved"
        ],
        commercial.is_approved
      ),

    risk_level:
      String(
        getValue(
          option,
          [
            "ai_risk_level",
            "risk_level"
          ],
          "UNAVAILABLE"
        )
      ).toUpperCase(),

    risk_confidence:
      getValue(
        option,
        [
          "ai_risk_confidence",
          "risk_confidence",
          "confidence"
        ],
        null
      ),

    raw:
      option

  };
}


// ============================================================
// PROCUREMENT COMPONENT
// ============================================================

function Procurement({
  initialRequest = null,
  onViewOrders
}) {

  // ==========================================================
  // INVENTORY REQUEST CONTEXT
  // ==========================================================

  const [
    requestContext,
    setRequestContext
  ] = useState(null);


  // ==========================================================
  // COMPONENTS
  // ==========================================================

  const [
    components,
    setComponents
  ] = useState([]);

  const [
    loadingComponents,
    setLoadingComponents
  ] = useState(false);

  const [
    componentId,
    setComponentId
  ] = useState("");

  const [
    requiredQuantity,
    setRequiredQuantity
  ] = useState("");


  // ==========================================================
  // PROCUREMENT DECISION
  // ==========================================================

  const [
    procurementDecision,
    setProcurementDecision
  ] = useState(null);

  const [
    suppliers,
    setSuppliers
  ] = useState([]);

  const [
    selectedSupplierId,
    setSelectedSupplierId
  ] = useState(null);

  const [
    recommendedSupplierId,
    setRecommendedSupplierId
  ] = useState(null);


  // ==========================================================
  // WAREHOUSES
  // ==========================================================

  const [
    warehouses,
    setWarehouses
  ] = useState([]);

  const [
    selectedWarehouse,
    setSelectedWarehouse
  ] = useState("");


  // ==========================================================
  // ORDER
  // ==========================================================

  const [
    orderQuantity,
    setOrderQuantity
  ] = useState("");

  const [
    createdOrder,
    setCreatedOrder
  ] = useState(null);


  // ==========================================================
  // UI
  // ==========================================================

  const [
    loading,
    setLoading
  ] = useState(false);

  const [
    placingOrder,
    setPlacingOrder
  ] = useState(false);

  const [
    error,
    setError
  ] = useState("");

  const [
    warning,
    setWarning
  ] = useState("");


  // ==========================================================
  // SELECTED COMPONENT
  // ==========================================================

  const selectedComponent =
    useMemo(
      () =>

        components.find(
          component =>
            Number(
              component.component_id
            ) ===
            Number(componentId)
        ) || null,

      [
        components,
        componentId
      ]
    );


  // ==========================================================
  // SELECTED SUPPLIER
  // ==========================================================

  const selectedSupplier =
    useMemo(
      () =>

        suppliers.find(
          supplier =>
            Number(
              supplier.supplier_id
            ) ===
            Number(
              selectedSupplierId
            )
        ) || null,

      [
        suppliers,
        selectedSupplierId
      ]
    );


  // ==========================================================
  // ESTIMATED ORDER VALUE
  // ==========================================================

  const estimatedOrderValue =
    useMemo(
      () => {

        if (!selectedSupplier) {
          return 0;
        }

        return (
          Number(
            orderQuantity || 0
          )
          *
          Number(
            selectedSupplier.unit_price ||
            0
          )
        );

      },
      [
        selectedSupplier,
        orderQuantity
      ]
    );


  // ==========================================================
  // QUANTITY VALIDATION
  // ==========================================================

  const quantityValidation =
    useMemo(
      () => {

        if (!selectedSupplier) {

          return {
            valid: false,
            message:
              "Select a supplier."
          };

        }

        const quantity =
          Number(orderQuantity);

        if (
          !quantity ||
          quantity <= 0
        ) {

          return {
            valid: false,
            message:
              "Order quantity must be greater than zero."
          };

        }

        const moq =
          Number(
            selectedSupplier
              .minimum_order_quantity ||
            1
          );

        if (quantity < moq) {

          return {
            valid: false,
            message:
              `Minimum order quantity is ${formatNumber(moq)}.`
          };

        }

        if (
          selectedSupplier.maximum_capacity !== null &&
          selectedSupplier.maximum_capacity !== undefined
        ) {

          const capacity =
            Number(
              selectedSupplier.maximum_capacity
            );

          if (
            capacity > 0 &&
            quantity > capacity
          ) {

            return {
              valid: false,
              message:
                `Supplier capacity is only ${formatNumber(capacity)} units.`
            };

          }

        }

        if (
          selectedSupplier.available_to_promise !== null &&
          selectedSupplier.available_to_promise !== undefined
        ) {

          const available =
            Number(
              selectedSupplier.available_to_promise
            );

          if (
            available >= 0 &&
            quantity > available
          ) {

            return {
              valid: false,
              message:
                `Supplier available-to-promise is ${formatNumber(available)} units.`
            };

          }

        }

        return {
          valid: true,
          message: ""
        };

      },
      [
        selectedSupplier,
        orderQuantity
      ]
    );


  // ==========================================================
  // LOAD ALL VEHICLE COMPONENTS
  // ==========================================================

  useEffect(
    () => {

      let cancelled = false;

      async function loadComponents() {

        try {

          setLoadingComponents(true);

          const vehicleResponse =
            await getInventoryVehicles();

          const vehicleList =
            Array.isArray(vehicleResponse)
              ? vehicleResponse
              : vehicleResponse?.vehicles ||
                vehicleResponse?.data ||
                [];

          const responses =
            await Promise.all(

              vehicleList.map(
                async vehicle => {

                  const vehicleId =
                    Number(
                      vehicle.vehicle_id ||
                      vehicle.id
                    );

                  if (!vehicleId) {
                    return [];
                  }

                  try {

                    const response =
                      await getVehicleInventoryComponents(
                        vehicleId
                      );

                    if (Array.isArray(response)) {
                      return response;
                    }

                    if (
                      Array.isArray(
                        response?.components
                      )
                    ) {
                      return response.components;
                    }

                    if (
                      Array.isArray(
                        response?.data
                      )
                    ) {
                      return response.data;
                    }

                    return [];

                  }

                  catch (vehicleError) {

                    console.error(
                      `Unable to load components for vehicle ${vehicleId}:`,
                      vehicleError
                    );

                    return [];

                  }

                }
              )

            );

          const componentMap =
            new Map();

          responses
            .flat()
            .forEach(
              item => {

                const component =
                  normalizeComponent(item);

                if (!component) {
                  return;
                }

                if (
                  !componentMap.has(
                    component.component_id
                  )
                ) {

                  componentMap.set(
                    component.component_id,
                    component
                  );

                }

              }
            );

          const list =
            Array.from(
              componentMap.values()
            ).sort(
              (a, b) => {

                const nameA =
                  String(
                    a.component_name || ""
                  );

                const nameB =
                  String(
                    b.component_name || ""
                  );

                return nameA.localeCompare(
                  nameB
                );

              }
            );

          if (!cancelled) {

            setComponents(list);

          }

        }

        catch (loadError) {

          console.error(
            "Unable to load procurement components:",
            loadError
          );

          if (!cancelled) {

            setError(
              "Unable to load vehicle component list."
            );

          }

        }

        finally {

          if (!cancelled) {

            setLoadingComponents(false);

          }

        }

      }

      loadComponents();

      return () => {
        cancelled = true;
      };

    },
    []
  );


  // ==========================================================
  // LOAD INVENTORY PROCUREMENT CONTEXT
  // ==========================================================

  useEffect(
    () => {

      const context =
        initialRequest ||
        readStoredRequest();

      if (!context) {
        return;
      }

      setRequestContext(
        context
      );

      const contextComponentId =
        Number(
          context.component_id
        );

      const contextQuantity =
        Number(
          context.required_quantity
        );

      if (
        contextComponentId > 0
      ) {

        setComponentId(
          String(
            contextComponentId
          )
        );

      }

      if (
        contextQuantity > 0
      ) {

        setRequiredQuantity(
          String(
            contextQuantity
          )
        );

        setOrderQuantity(
          String(
            contextQuantity
          )
        );

      }

      if (
        contextComponentId > 0 &&
        contextQuantity > 0
      ) {

        runProcurementAnalysis(
          contextComponentId,
          contextQuantity
        );

      }

    },
    [
      initialRequest
    ]
  );


  // ==========================================================
  // RUN PROCUREMENT ANALYSIS
  // ==========================================================

  async function runProcurementAnalysis(
    component,
    quantity
  ) {

    const numericComponent =
      Number(component);

    const numericQuantity =
      Number(quantity);

    if (
      !numericComponent ||
      numericComponent <= 0
    ) {

      setError(
        "Please select a component."
      );

      return;

    }

    if (
      !numericQuantity ||
      numericQuantity <= 0
    ) {

      setError(
        "Required quantity must be greater than zero."
      );

      return;

    }

    try {

      setLoading(true);

      setError("");

      setWarning("");

      setCreatedOrder(null);

      // ------------------------------------------------------
      // PROCUREMENT DECISION
      // ------------------------------------------------------

      const decision =
        await getProcurementDecision(
          numericComponent,
          numericQuantity
        );

      setProcurementDecision(
        decision
      );


      // ------------------------------------------------------
      // SUPPLIER INTELLIGENCE
      // ------------------------------------------------------

      let intelligence = [];

      try {

        const response =
          await getSupplierIntelligence(
            numericComponent
          );

        intelligence =
          Array.isArray(response)
            ? response
            : [];

      }

      catch (intelligenceError) {

        console.error(
          "Supplier intelligence unavailable:",
          intelligenceError
        );

      }


      // ------------------------------------------------------
      // CREATE INTELLIGENCE MAP
      // ------------------------------------------------------

      const intelligenceMap =
        new Map();

      intelligence.forEach(
        item => {

          intelligenceMap.set(
            Number(
              item.supplier_id
            ),
            item
          );

        }
      );


      // ------------------------------------------------------
      // RANKED SUPPLIERS
      // ------------------------------------------------------

      let rankedOptions = [];

      if (
        Array.isArray(
          decision?.supplier_options
        )
      ) {

        rankedOptions =
          decision.supplier_options;

      }

      else if (
        Array.isArray(
          decision?.ranked_suppliers
        )
      ) {

        rankedOptions =
          decision.ranked_suppliers;

      }

      else if (
        Array.isArray(
          decision?.suppliers
        )
      ) {

        rankedOptions =
          decision.suppliers;

      }


      // ------------------------------------------------------
      // FALLBACK
      // ------------------------------------------------------

      if (
        rankedOptions.length === 0 &&
        intelligence.length > 0
      ) {

        rankedOptions =
          intelligence;

        setWarning(
          "The procurement decision API returned no ranked supplier options. Supplier intelligence is being displayed."
        );

      }


      // ------------------------------------------------------
      // NORMALIZE SUPPLIERS
      // ------------------------------------------------------

      const normalized =
        rankedOptions

          .map(
            option => {

              const supplierId =
                extractSupplierId(
                  option
                );

              return normalizeSupplier(
                option,
                intelligenceMap.get(
                  Number(
                    supplierId
                  )
                )
              );

            }
          )

          .filter(
            supplier =>
              supplier.supplier_id
          );


      setSuppliers(
        normalized
      );


      // ------------------------------------------------------
      // RECOMMENDED SUPPLIER
      // ------------------------------------------------------

      const explicitRecommended =
        extractSupplierId(
          decision?.recommended_supplier
        )
        ||
        extractSupplierId(
          decision?.recommended_supplier_id
        );

      const recommendedId =
        explicitRecommended
        ||
        normalized[0]?.supplier_id
        ||
        null;

      setRecommendedSupplierId(
        recommendedId
      );

      setSelectedSupplierId(
        recommendedId
      );


      // ------------------------------------------------------
      // INITIAL ORDER QUANTITY
      // ------------------------------------------------------

      const recommendedSupplier =
        normalized.find(
          supplier =>
            Number(
              supplier.supplier_id
            ) ===
            Number(
              recommendedId
            )
        );

      const recommendedMOQ =
        Number(
          recommendedSupplier
            ?.minimum_order_quantity ||
          1
        );

      setOrderQuantity(
        String(
          Math.max(
            numericQuantity,
            recommendedMOQ
          )
        )
      );


      // ------------------------------------------------------
      // LOAD WAREHOUSES
      // ------------------------------------------------------

      try {

        const inventoryRows =
          await getInventoryByComponent(
            numericComponent
          );

        const warehouseList =
          [
            ...new Set(

              (
                Array.isArray(
                  inventoryRows
                )
                  ? inventoryRows
                  : []
              )

                .map(
                  row =>
                    row.warehouse
                )

                .filter(Boolean)

            )
          ];

        setWarehouses(
          warehouseList
        );

        if (
          warehouseList.length > 0
        ) {

          setSelectedWarehouse(
            warehouseList[0]
          );

        }

        else {

          setSelectedWarehouse("");

        }

      }

      catch (inventoryError) {

        console.error(
          "Unable to load warehouses:",
          inventoryError
        );

        setWarehouses([]);

        setSelectedWarehouse("");

      }

    }

    catch (analysisError) {

      console.error(
        "Procurement analysis failed:",
        analysisError
      );

      setProcurementDecision(null);

      setSuppliers([]);

      setSelectedSupplierId(null);

      setRecommendedSupplierId(null);

      setError(
        analysisError?.message ||
        "Unable to generate procurement recommendation."
      );

    }

    finally {

      setLoading(false);

    }

  }


  // ==========================================================
  // ANALYZE
  // ==========================================================

  async function handleAnalyze() {

    await runProcurementAnalysis(
      Number(componentId),
      Number(requiredQuantity)
    );

  }


  // ==========================================================
  // COMPONENT CHANGE
  // ==========================================================

  function handleComponentChange(event) {

    const value =
      event.target.value;

    setComponentId(value);

    setProcurementDecision(null);

    setSuppliers([]);

    setSelectedSupplierId(null);

    setRecommendedSupplierId(null);

    setCreatedOrder(null);

    setWarehouses([]);

    setSelectedWarehouse("");

    setError("");

    setWarning("");

  }


  // ==========================================================
  // SELECT SUPPLIER
  // ==========================================================

  function handleSupplierSelect(
    supplier
  ) {

    setSelectedSupplierId(
      supplier.supplier_id
    );

    const currentQuantity =
      Number(
        orderQuantity ||
        requiredQuantity ||
        0
      );

    const moq =
      Number(
        supplier.minimum_order_quantity ||
        1
      );

    if (
      currentQuantity < moq
    ) {

      setOrderQuantity(
        String(moq)
      );

    }

  }


  // ==========================================================
  // CREATE PURCHASE ORDER
  // ==========================================================

  async function handlePlaceOrder() {

    if (!selectedSupplier) {

      setError(
        "Select a supplier before placing the order."
      );

      return;

    }

    if (!selectedWarehouse) {

      setError(
        "Select a destination warehouse."
      );

      return;

    }

    if (
      !quantityValidation.valid
    ) {

      setError(
        quantityValidation.message
      );

      return;

    }

    try {

      setPlacingOrder(true);

      setError("");

      const payload = {

        supplier_id:
          Number(
            selectedSupplier.supplier_id
          ),

        component_id:
          Number(
            componentId
          ),

        warehouse:
          selectedWarehouse,

        quantity_ordered:
          Number(
            orderQuantity
          ),

        vehicle_id:
          requestContext?.vehicle_id
            ? Number(
                requestContext.vehicle_id
              )
            : null,

        required_date:
          requestContext?.required_date ||
          null,

        urgency:
          requestContext?.urgency ||
          null

      };

      const order =
        await createPurchaseOrder(
          payload
        );

      setCreatedOrder(
        order
      );

      sessionStorage.removeItem(
        "inventoryProcurementRequest"
      );

    }

    catch (orderError) {

      console.error(
        "PO creation failed:",
        orderError
      );

      setError(
        orderError?.message ||
        "Unable to create purchase order."
      );

    }

    finally {

      setPlacingOrder(false);

    }

  }


  // ==========================================================
  // VIEW ORDERS
  // ==========================================================

  function handleViewOrders() {

    if (onViewOrders) {

      onViewOrders(
        createdOrder
      );

    }

  }


  // ==========================================================
  // DECISION FACTORS
  // ==========================================================

  const decisionFactors =
    selectedSupplier
      ? [

          [
            "Availability",
            selectedSupplier
              .availability_score
          ],

          [
            "Fulfillment",
            selectedSupplier
              .fulfillment_score
          ],

          [
            "Reliability",
            selectedSupplier
              .reliability_score
          ],

          [
            "Quality",
            selectedSupplier
              .quality_score
          ],

          [
            "AI Risk",
            selectedSupplier
              .ai_risk_score
          ],

          [
            "Price",
            selectedSupplier
              .price_score
          ],

          [
            "Lead Time",
            selectedSupplier
              .lead_time_score
          ]

        ].filter(
          (
            [, value]
          ) =>
            value !== null &&
            value !== undefined
        )

      : [];


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <Box
      sx={{
        p: 3
      }}
    >

      {/* =====================================================
          HEADER
      ===================================================== */}

      <Box
        sx={{
          mb: 3
        }}
      >

        <Typography
          variant="h5"
          fontWeight={700}
        >
          Intelligent Procurement
        </Typography>

        <Typography
          color="text.secondary"
          sx={{
            mt: 0.5
          }}
        >
          AI-assisted supplier selection, risk evaluation and purchase-order creation
        </Typography>

      </Box>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <Alert
          severity="error"
          sx={{
            mb: 3
          }}
          onClose={() =>
            setError("")
          }
        >
          {error}
        </Alert>

      )}


      {/* =====================================================
          WARNING
      ===================================================== */}

      {warning && (

        <Alert
          severity="warning"
          sx={{
            mb: 3
          }}
          onClose={() =>
            setWarning("")
          }
        >
          {warning}
        </Alert>

      )}


      {/* =====================================================
          INVENTORY PROCUREMENT REQUEST
      ===================================================== */}

      {requestContext && (

        <Card
          elevation={0}
          sx={{
            border:
              "1px solid #e5e7eb",
            borderRadius: 3,
            mb: 3
          }}
        >

          <CardContent>

            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{
                mb: 2
              }}
            >

              <ShoppingCartIcon
                color="primary"
              />

              <Typography
                variant="h6"
                fontWeight={600}
              >
                Inventory Procurement Request
              </Typography>

            </Stack>


            <Grid
              container
              spacing={2}
            >

              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Vehicle
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    requestContext
                      .vehicle_type ||
                    "-"
                  }
                </Typography>

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  {
                    requestContext
                      .vehicle_code ||
                    ""
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Component
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    requestContext
                      .part_name ||
                    selectedComponent
                      ?.component_name ||
                    "-"
                  }
                </Typography>

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  {
                    requestContext
                      .part_id ||
                    selectedComponent
                      ?.part_number ||
                    ""
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 2
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Recommended Qty
                </Typography>

                <Typography
                  fontWeight={700}
                >
                  {
                    formatNumber(
                      requestContext
                        .required_quantity
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 2
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Required Date
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    formatDate(
                      requestContext
                        .required_date
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 2
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Urgency
                </Typography>

                <Box
                  sx={{
                    mt: 0.5
                  }}
                >

                  <UrgencyChip
                    urgency={
                      requestContext
                        .urgency
                    }
                  />

                </Box>

              </Grid>

            </Grid>

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          PROCUREMENT REQUIREMENT
      ===================================================== */}

      <Card
        elevation={0}
        sx={{
          border:
            "1px solid #e5e7eb",
          borderRadius: 3,
          mb: 3
        }}
      >

        <CardContent>

          <Typography
            variant="h6"
            fontWeight={600}
            sx={{
              mb: 2
            }}
          >
            1. Procurement Requirement
          </Typography>


          <Grid
            container
            spacing={2}
            alignItems="flex-start"
          >

            {/* COMPONENT DROPDOWN */}

            <Grid
              size={{
                xs: 12,
                md: 4
              }}
            >

              <FormControl
                fullWidth
                disabled={
                  loadingComponents
                }
              >

                <InputLabel>
                  Component
                </InputLabel>

                <Select
                  label="Component"
                  value={
                    componentId
                  }
                  onChange={
                    handleComponentChange
                  }
                >

                  {components.length === 0 && (

                    <MenuItem
                      value=""
                      disabled
                    >
                      {
                        loadingComponents
                          ? "Loading components..."
                          : "No components available"
                      }
                    </MenuItem>

                  )}


                  {components.map(
                    component => (

                      <MenuItem
                        key={
                          component
                            .component_id
                        }
                        value={
                          String(
                            component
                              .component_id
                          )
                        }
                      >

                        <Box>

                          <Typography
                            variant="body2"
                            fontWeight={600}
                          >
                            ID:{" "}
                            {
                              component
                                .component_id
                            }
                            {" | "}
                            {
                              component
                                .component_name
                            }
                          </Typography>

                          {component
                            .part_number && (

                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Part No:{" "}
                              {
                                component
                                  .part_number
                              }
                            </Typography>

                          )}

                        </Box>

                      </MenuItem>

                    )
                  )}

                </Select>

              </FormControl>


              <Typography
                variant="caption"
                color="text.secondary"
                sx={{
                  display: "block",
                  mt: 0.7,
                  ml: 1
                }}
              >

                {
                  loadingComponents
                    ? "Loading vehicle components..."
                    : `${components.length} vehicle component(s) available`
                }

              </Typography>

            </Grid>


            {/* REQUIRED QUANTITY */}

            <Grid
              size={{
                xs: 12,
                md: 4
              }}
            >

              <TextField
                label="Required Quantity"
                type="number"
                fullWidth
                value={
                  requiredQuantity
                }
                onChange={
                  event => {

                    setRequiredQuantity(
                      event.target.value
                    );

                    setOrderQuantity(
                      event.target.value
                    );

                  }
                }
                inputProps={{
                  min: 1
                }}
              />

            </Grid>


            {/* ANALYZE */}

            <Grid
              size={{
                xs: 12,
                md: 4
              }}
            >

              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={
                  loading
                    ? null
                    : <AutoAwesomeIcon />
                }
                disabled={
                  loading ||
                  !componentId ||
                  !requiredQuantity
                }
                onClick={
                  handleAnalyze
                }
                sx={{
                  py: 1.7
                }}
              >

                {loading
                  ? (
                    <CircularProgress
                      size={22}
                      color="inherit"
                    />
                  )
                  : "Analyze Suppliers"
                }

              </Button>

            </Grid>

          </Grid>


          {selectedComponent && (

            <Alert
              severity="info"
              sx={{
                mt: 2
              }}
            >

              Selected component:{" "}

              <strong>
                ID {selectedComponent.component_id}
                {" | "}
                {selectedComponent.component_name}
              </strong>

              {selectedComponent.part_number
                ? ` | Part No: ${selectedComponent.part_number}`
                : ""
              }

            </Alert>

          )}

        </CardContent>

      </Card>


      {/* =====================================================
          SUPPLIER RECOMMENDATION
      ===================================================== */}

      {suppliers.length > 0 && (

        <Card
          elevation={0}
          sx={{
            border:
              "1px solid #e5e7eb",
            borderRadius: 3,
            mb: 3
          }}
        >

          <CardContent>

            <Box
              sx={{
                display: "flex",
                justifyContent:
                  "space-between",
                alignItems: "center",
                mb: 2,
                gap: 2,
                flexWrap: "wrap"
              }}
            >

              <Box>

                <Typography
                  variant="h6"
                  fontWeight={600}
                >
                  2. AI Supplier Recommendation
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Suppliers are ranked using availability, fulfillment, reliability, quality, AI risk, price and lead time.
                </Typography>

              </Box>


              <Chip
                icon={
                  <AutoAwesomeIcon />
                }
                label={
                  `${suppliers.length} supplier option(s)`
                }
                color="primary"
                variant="outlined"
              />

            </Box>


            <TableContainer>

              <Table>

                <TableHead>

                  <TableRow>

                    <TableCell>
                      <strong>
                        Supplier
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Recommendation
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        AI Risk
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        ATP
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Unit Price
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Lead Time
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        MOQ
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Capacity
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Final Score
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Select
                      </strong>
                    </TableCell>

                  </TableRow>

                </TableHead>


                <TableBody>

                  {suppliers.map(
                    supplier => {

                      const selected =
                        Number(
                          selectedSupplierId
                        ) ===
                        Number(
                          supplier.supplier_id
                        );

                      const recommended =
                        Number(
                          recommendedSupplierId
                        ) ===
                        Number(
                          supplier.supplier_id
                        );

                      return (

                        <TableRow
                          key={
                            supplier.supplier_id
                          }
                          hover
                          selected={
                            selected
                          }
                        >

                          <TableCell>

                            <Typography
                              variant="body2"
                              fontWeight={700}
                            >
                              {
                                supplier
                                  .supplier_name
                              }
                            </Typography>

                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {
                                supplier
                                  .supplier_code
                              }

                              {" • "}

                              {
                                supplier
                                  .supplier_location
                              }
                            </Typography>

                          </TableCell>


                          <TableCell>

                            {recommended
                              ? (

                                <Chip
                                  icon={
                                    <AutoAwesomeIcon />
                                  }
                                  label="Recommended"
                                  color="success"
                                  size="small"
                                />

                              )
                              : (

                                <Chip
                                  label="Alternative"
                                  size="small"
                                  variant="outlined"
                                />

                              )
                            }

                          </TableCell>


                          <TableCell>

                            <Stack
                              spacing={0.5}
                            >

                              <RiskChip
                                riskLevel={
                                  supplier
                                    .risk_level
                                }
                              />

                              {supplier
                                .risk_confidence !== null &&
                               supplier
                                .risk_confidence !== undefined && (

                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Confidence{" "}
                                  {
                                    (
                                      Number(
                                        supplier
                                          .risk_confidence
                                      )
                                      *
                                      100
                                    ).toFixed(1)
                                  }
                                  %
                                </Typography>

                              )}

                            </Stack>

                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                supplier
                                  .available_to_promise
                              )
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatMoney(
                                supplier
                                  .unit_price
                              )
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                supplier
                                  .standard_lead_time_days
                              )
                            }{" "}
                            days
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                supplier
                                  .minimum_order_quantity
                              )
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                supplier
                                  .maximum_capacity
                              )
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            <strong>
                              {
                                formatScore(
                                  supplier
                                    .final_score
                                )
                              }
                            </strong>
                          </TableCell>


                          <TableCell>

                            <Button
                              variant={
                                selected
                                  ? "contained"
                                  : "outlined"
                              }
                              size="small"
                              onClick={() =>
                                handleSupplierSelect(
                                  supplier
                                )
                              }
                            >
                              {
                                selected
                                  ? "Selected"
                                  : "Select"
                              }
                            </Button>

                          </TableCell>

                        </TableRow>

                      );

                    }
                  )}

                </TableBody>

              </Table>

            </TableContainer>

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          SUPPLIER DECISION DETAILS
      ===================================================== */}

      {selectedSupplier && (

        <Card
          elevation={0}
          sx={{
            border:
              "1px solid #e5e7eb",
            borderRadius: 3,
            mb: 3
          }}
        >

          <CardContent>

            <Typography
              variant="h6"
              fontWeight={600}
            >
              Supplier Decision Details
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                mb: 2
              }}
            >
              {
                selectedSupplier
                  .supplier_name
              }
            </Typography>


            <Grid
              container
              spacing={2}
            >

              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Available-to-Promise
                </Typography>

                <Typography
                  variant="h6"
                  fontWeight={700}
                >
                  {
                    formatNumber(
                      selectedSupplier
                        .available_to_promise
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Unit Price
                </Typography>

                <Typography
                  variant="h6"
                  fontWeight={700}
                >
                  {
                    formatMoney(
                      selectedSupplier
                        .unit_price
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Lead Time
                </Typography>

                <Typography
                  variant="h6"
                  fontWeight={700}
                >
                  {
                    selectedSupplier
                      .standard_lead_time_days
                  }{" "}
                  days
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  AI Risk
                </Typography>

                <Box
                  sx={{
                    mt: 0.5
                  }}
                >

                  <RiskChip
                    riskLevel={
                      selectedSupplier
                        .risk_level
                    }
                  />

                </Box>

              </Grid>

            </Grid>


            {decisionFactors.length > 0 && (

              <>

                <Divider
                  sx={{
                    my: 2
                  }}
                />

                <Typography
                  variant="subtitle2"
                  fontWeight={700}
                  sx={{
                    mb: 1
                  }}
                >
                  Procurement Ranking Factors
                </Typography>

                <Stack
                  direction="row"
                  spacing={1}
                  useFlexGap
                  flexWrap="wrap"
                >

                  {decisionFactors.map(
                    (
                      [
                        label,
                        value
                      ]
                    ) => (

                      <Chip
                        key={label}
                        label={
                          `${label}: ${formatScore(value)}`
                        }
                        variant="outlined"
                        size="small"
                      />

                    )
                  )}

                </Stack>

              </>

            )}

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          CREATE PURCHASE ORDER
      ===================================================== */}

      {selectedSupplier && (

        <Card
          elevation={0}
          sx={{
            border:
              "1px solid #e5e7eb",
            borderRadius: 3,
            mb: 3
          }}
        >

          <CardContent>

            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{
                mb: 2
              }}
            >

              <StoreIcon
                color="primary"
              />

              <Typography
                variant="h6"
                fontWeight={600}
              >
                3. Create Purchase Order
              </Typography>

            </Stack>


            <Grid
              container
              spacing={2}
            >

              <Grid
                size={{
                  xs: 12,
                  md: 4
                }}
              >

                <FormControl
                  fullWidth
                >

                  <InputLabel>
                    Destination Warehouse
                  </InputLabel>

                  <Select
                    label="Destination Warehouse"
                    value={
                      selectedWarehouse
                    }
                    onChange={
                      event =>
                        setSelectedWarehouse(
                          event.target.value
                        )
                    }
                  >

                    {warehouses.length === 0 && (

                      <MenuItem
                        disabled
                        value=""
                      >
                        No warehouse available
                      </MenuItem>

                    )}

                    {warehouses.map(
                      warehouse => (

                        <MenuItem
                          key={
                            warehouse
                          }
                          value={
                            warehouse
                          }
                        >
                          {warehouse}
                        </MenuItem>

                      )
                    )}

                  </Select>

                </FormControl>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 4
                }}
              >

                <TextField
                  label="Order Quantity"
                  type="number"
                  fullWidth
                  value={
                    orderQuantity
                  }
                  onChange={
                    event =>
                      setOrderQuantity(
                        event.target.value
                      )
                  }
                  helperText={
                    `MOQ: ${formatNumber(
                      selectedSupplier
                        .minimum_order_quantity
                    )}`
                  }
                />

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 4
                }}
              >

                <TextField
                  label="Estimated Order Value"
                  fullWidth
                  value={
                    formatMoney(
                      estimatedOrderValue
                    )
                  }
                  InputProps={{
                    readOnly: true
                  }}
                />

              </Grid>

            </Grid>


            <Grid
              container
              spacing={2}
              sx={{
                mt: 1
              }}
            >

              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Component
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    selectedComponent
                      ?.component_name ||
                    componentId
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Supplier
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    selectedSupplier
                      .supplier_name
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Capacity
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    formatNumber(
                      selectedSupplier
                        .maximum_capacity
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Available-to-Promise
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    formatNumber(
                      selectedSupplier
                        .available_to_promise
                    )
                  }
                </Typography>

              </Grid>

            </Grid>


            {!quantityValidation.valid && (

              <Alert
                severity="warning"
                sx={{
                  mt: 2
                }}
              >
                {
                  quantityValidation
                    .message
                }
              </Alert>

            )}


            <Box
              sx={{
                display: "flex",
                justifyContent: "flex-end",
                mt: 3
              }}
            >

              <Button
                variant="contained"
                size="large"
                startIcon={
                  placingOrder
                    ? null
                    : <ShoppingCartIcon />
                }
                disabled={
                  placingOrder ||
                  !quantityValidation.valid ||
                  !selectedWarehouse
                }
                onClick={
                  handlePlaceOrder
                }
              >

                {placingOrder
                  ? (
                    <CircularProgress
                      size={22}
                      color="inherit"
                    />
                  )
                  : "Place Purchase Order"
                }

              </Button>

            </Box>

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          PURCHASE ORDER CREATED
      ===================================================== */}

      {createdOrder && (

        <Card
          elevation={0}
          sx={{
            border:
              "1px solid #c8e6c9",
            borderRadius: 3,
            mb: 3
          }}
        >

          <CardContent>

            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{
                mb: 2
              }}
            >

              <CheckCircleIcon
                color="success"
              />

              <Typography
                variant="h6"
                fontWeight={700}
                color="success.main"
              >
                Purchase Order Created Successfully
              </Typography>

            </Stack>


            <Alert
              severity="success"
              sx={{
                mb: 2
              }}
            >
              The supplier capacity has been committed and this order is now available in the Orders tracking module.
            </Alert>


            <Grid
              container
              spacing={2}
            >

              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  PO Number
                </Typography>

                <Typography
                  fontWeight={700}
                >
                  {
                    createdOrder
                      .po_number ||
                    "-"
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Supplier
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    createdOrder
                      .supplier_name ||
                    selectedSupplier
                      ?.supplier_name ||
                    "-"
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Expected Arrival
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    formatDate(
                      createdOrder
                        .expected_delivery_date
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Tracking Stage
                </Typography>

                <Box
                  sx={{
                    mt: 0.5
                  }}
                >

                  <Chip
                    label={
                      createdOrder
                        .tracking_stage ||
                      "ORDER_PLACED"
                    }
                    color="info"
                    size="small"
                  />

                </Box>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Quantity
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    formatNumber(
                      createdOrder
                        .quantity_ordered ||
                      orderQuantity
                    )
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Destination
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    createdOrder
                      .warehouse ||
                    selectedWarehouse ||
                    "-"
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Current Location
                </Typography>

                <Typography
                  fontWeight={600}
                >
                  {
                    createdOrder
                      .current_location ||
                    "-"
                  }
                </Typography>

              </Grid>


              <Grid
                size={{
                  xs: 12,
                  sm: 6,
                  md: 3
                }}
              >

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Order Value
                </Typography>

                <Typography
                  fontWeight={700}
                >
                  {
                    formatMoney(
                      createdOrder
                        .order_value ||
                      estimatedOrderValue
                    )
                  }
                </Typography>

              </Grid>

            </Grid>


            <Divider
              sx={{
                my: 2
              }}
            />


            <Box
              sx={{
                display: "flex",
                justifyContent: "flex-end"
              }}
            >

              <Button
                variant="contained"
                color="success"
                startIcon={
                  <LocalShippingIcon />
                }
                onClick={
                  handleViewOrders
                }
              >
                View Order Tracking
              </Button>

            </Box>

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          EMPTY STATE
      ===================================================== */}

      {!loading &&
       suppliers.length === 0 &&
       !createdOrder && (

        <Card
          elevation={0}
          sx={{
            border:
              "1px solid #e5e7eb",
            borderRadius: 3
          }}
        >

          <CardContent
            sx={{
              textAlign: "center",
              py: 6
            }}
          >

            <AutoAwesomeIcon
              sx={{
                fontSize: 50,
                color:
                  "text.secondary"
              }}
            />

            <Typography
              variant="h6"
              sx={{
                mt: 1
              }}
            >
              Procurement Decision Engine
            </Typography>

            <Typography
              color="text.secondary"
              sx={{
                mt: 0.5
              }}
            >
              Select a component and required quantity, or send a procurement requirement from Inventory.
            </Typography>

          </CardContent>

        </Card>

      )}

    </Box>

  );

}


export default Procurement;