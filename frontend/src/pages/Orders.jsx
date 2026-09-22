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
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography
} from "@mui/material";

import {
  CircleMarker,
  MapContainer,
  Polyline,
  Popup,
  TileLayer,
  useMap
} from "react-leaflet";

import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import RefreshIcon from "@mui/icons-material/Refresh";
import InventoryIcon from "@mui/icons-material/Inventory";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import RouteIcon from "@mui/icons-material/Route";
import SpeedIcon from "@mui/icons-material/Speed";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import MyLocationIcon from "@mui/icons-material/MyLocation";

import {
  getPurchaseOrders,
  updatePurchaseOrderTracking,
  receivePurchaseOrder,
  getPurchaseOrderHistory,
  getPurchaseOrderShipment,
  getShipmentTrackingHistory,
  simulateShipmentLocation
} from "../services/api";


// ============================================================
// TRACKING CONFIGURATION
// ============================================================

const TRACKING_STAGES = [
  "ORDER_PLACED",
  "SUPPLIER_CONFIRMED",
  "READY_FOR_DISPATCH",
  "DISPATCHED",
  "IN_TRANSIT",
  "ARRIVED_AT_WAREHOUSE",
  "RECEIVED"
];


const TRACKING_LABELS = {
  ORDER_PLACED: "Order Placed",
  SUPPLIER_CONFIRMED: "Supplier Confirmed",
  READY_FOR_DISPATCH: "Ready for Dispatch",
  DISPATCHED: "Dispatched",
  IN_TRANSIT: "In Transit",
  ARRIVED_AT_WAREHOUSE: "Arrived at Warehouse",
  PARTIALLY_RECEIVED: "Partially Received",
  RECEIVED: "Received",
  CANCELLED: "Cancelled"
};


// Only these stages are controlled manually.
// IN_TRANSIT and ARRIVED_AT_WAREHOUSE are controlled
// automatically by the GPS simulator.
// PARTIALLY_RECEIVED and RECEIVED are controlled by receiving.
const MANUAL_TRACKING_STAGES = [
  "ORDER_PLACED",
  "SUPPLIER_CONFIRMED",
  "READY_FOR_DISPATCH",
  "DISPATCHED"
];


// ============================================================
// FORMAT HELPERS
// ============================================================

function formatNumber(value) {
  return Number(
    value || 0
  ).toLocaleString();
}


function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString();
}


function formatDateTime(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
}


function formatDecimal(
  value,
  digits = 1
) {
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

  return number.toFixed(digits);
}


// ============================================================
// TRACKING HELPERS
// ============================================================

function normalizeStepperStage(stage) {
  if (
    stage === "PARTIALLY_RECEIVED"
  ) {
    return "ARRIVED_AT_WAREHOUSE";
  }

  return stage || "ORDER_PLACED";
}


function getActiveStep(stage) {
  const normalized =
    normalizeStepperStage(stage);

  const index =
    TRACKING_STAGES.indexOf(
      normalized
    );

  return index >= 0
    ? index
    : 0;
}


function getAllowedManualStages(
  currentStage
) {
  if (
    currentStage === "ORDER_PLACED"
  ) {
    return [
      "ORDER_PLACED",
      "SUPPLIER_CONFIRMED"
    ];
  }

  if (
    currentStage === "SUPPLIER_CONFIRMED"
  ) {
    return [
      "SUPPLIER_CONFIRMED",
      "READY_FOR_DISPATCH"
    ];
  }

  if (
    currentStage === "READY_FOR_DISPATCH"
  ) {
    return [
      "READY_FOR_DISPATCH",
      "DISPATCHED"
    ];
  }

  if (
    currentStage === "DISPATCHED"
  ) {
    return [
      "DISPATCHED"
    ];
  }

  return [];
}


// ============================================================
// TRACKING CHIP
// ============================================================

function TrackingChip({
  stage
}) {
  let color = "default";

  if (
    stage === "RECEIVED"
  ) {
    color = "success";
  }
  else if (
    stage === "IN_TRANSIT" ||
    stage === "DISPATCHED"
  ) {
    color = "info";
  }
  else if (
    stage === "ARRIVED_AT_WAREHOUSE" ||
    stage === "PARTIALLY_RECEIVED"
  ) {
    color = "warning";
  }
  else if (
    stage === "CANCELLED"
  ) {
    color = "error";
  }

  return (
    <Chip
      size="small"
      color={color}
      label={
        TRACKING_LABELS[stage] ||
        stage ||
        "Not Tracked"
      }
    />
  );
}


// ============================================================
// SUMMARY CARD
// ============================================================

function SummaryCard({
  title,
  value,
  subtitle,
  icon
}) {
  return (
    <Card
      elevation={0}
      sx={{
        border:
          "1px solid #e5e7eb",
        borderRadius: 3,
        height: "100%"
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent:
              "space-between",
            alignItems: "center"
          }}
        >
          <Box>
            <Typography
              color="text.secondary"
              variant="body2"
            >
              {title}
            </Typography>

            <Typography
              variant="h4"
              fontWeight={700}
              sx={{
                mt: 1
              }}
            >
              {value}
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              {subtitle}
            </Typography>
          </Box>

          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              fontSize: 32
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}


// ============================================================
// SHIPMENT METRIC
// ============================================================

function ShipmentMetric({
  icon,
  title,
  value
}) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        borderRadius: 2,
        height: "100%"
      }}
    >
      <Stack
        direction="row"
        spacing={1.5}
        alignItems="center"
      >
        {icon}

        <Box>
          <Typography
            variant="caption"
            color="text.secondary"
          >
            {title}
          </Typography>

          <Typography
            fontWeight={700}
          >
            {value}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
}


// ============================================================
// MAP AUTO FIT
// ============================================================

function MapAutoFit({
  positions
}) {
  const map = useMap();

  useEffect(() => {
    if (
      !positions ||
      positions.length === 0
    ) {
      return;
    }

    if (
      positions.length === 1
    ) {
      map.setView(
        positions[0],
        9
      );

      return;
    }

    map.fitBounds(
      positions,
      {
        padding: [40, 40]
      }
    );
  }, [
    map,
    positions
  ]);

  return null;
}


// ============================================================
// SHIPMENT MAP
// ============================================================

function ShipmentMap({
  shipment,
  trackingPoints
}) {
  const origin =
    useMemo(() => {
      if (
        shipment?.origin_latitude === null ||
        shipment?.origin_latitude === undefined ||
        shipment?.origin_longitude === null ||
        shipment?.origin_longitude === undefined
      ) {
        return null;
      }

      return [
        Number(
          shipment.origin_latitude
        ),
        Number(
          shipment.origin_longitude
        )
      ];
    }, [
      shipment
    ]);


  const destination =
    useMemo(() => {
      if (
        shipment?.destination_latitude === null ||
        shipment?.destination_latitude === undefined ||
        shipment?.destination_longitude === null ||
        shipment?.destination_longitude === undefined
      ) {
        return null;
      }

      return [
        Number(
          shipment.destination_latitude
        ),
        Number(
          shipment.destination_longitude
        )
      ];
    }, [
      shipment
    ]);


  const current =
    useMemo(() => {
      if (
        shipment?.current_latitude === null ||
        shipment?.current_latitude === undefined ||
        shipment?.current_longitude === null ||
        shipment?.current_longitude === undefined
      ) {
        return origin;
      }

      return [
        Number(
          shipment.current_latitude
        ),
        Number(
          shipment.current_longitude
        )
      ];
    }, [
      shipment,
      origin
    ]);


  const historyPositions =
    useMemo(() => {
      if (
        !Array.isArray(
          trackingPoints
        )
      ) {
        return [];
      }

      return trackingPoints
        .filter(
          point =>
            point.latitude !== null &&
            point.latitude !== undefined &&
            point.longitude !== null &&
            point.longitude !== undefined
        )
        .map(
          point => [
            Number(
              point.latitude
            ),
            Number(
              point.longitude
            )
          ]
        );
    }, [
      trackingPoints
    ]);


  const travelledRoute =
    useMemo(() => {
      const route = [];

      if (origin) {
        route.push(origin);
      }

      historyPositions.forEach(
        position => {
          route.push(position);
        }
      );

      if (current) {
        const last =
          route[
            route.length - 1
          ];

        if (
          !last ||
          last[0] !== current[0] ||
          last[1] !== current[1]
        ) {
          route.push(current);
        }
      }

      return route;
    }, [
      origin,
      current,
      historyPositions
    ]);


  const completeRoute =
    useMemo(() => {
      if (
        origin &&
        destination
      ) {
        return [
          origin,
          destination
        ];
      }

      return [];
    }, [
      origin,
      destination
    ]);


  const bounds =
    useMemo(() => {
      return [
        origin,
        current,
        destination
      ].filter(Boolean);
    }, [
      origin,
      current,
      destination
    ]);


  if (
    !origin ||
    !destination
  ) {
    return (
      <Alert severity="warning">
        Shipment coordinates are not available.
      </Alert>
    );
  }


  return (
    <Box>
      <Alert
        severity="info"
        sx={{
          mb: 2
        }}
      >
        This is simulated GPS tracking for the project
        prototype. Supplier locations use simulation
        coordinates and do not represent the supplier's
        actual GPS position.
      </Alert>


      <Box
        sx={{
          height: 400,
          width: "100%",
          borderRadius: 2,
          overflow: "hidden",
          border:
            "1px solid #e5e7eb"
        }}
      >
        <MapContainer
          center={origin}
          zoom={7}
          style={{
            height: "100%",
            width: "100%"
          }}
        >
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          <MapAutoFit
            positions={bounds}
          />


          {/* COMPLETE SIMULATED ROUTE */}

          {completeRoute.length >
            1 && (
            <Polyline
              positions={
                completeRoute
              }
              pathOptions={{
                dashArray:
                  "8 8",
                weight: 3
              }}
            />
          )}


          {/* TRAVELLED ROUTE */}

          {travelledRoute.length >
            1 && (
            <Polyline
              positions={
                travelledRoute
              }
              pathOptions={{
                weight: 5
              }}
            />
          )}


          {/* SUPPLIER */}

          <CircleMarker
            center={origin}
            radius={10}
            pathOptions={{
              fillOpacity: 1
            }}
          >
            <Popup>
              <strong>
                Supplier Origin
              </strong>

              <br />

              {
                shipment.origin_location
              }
            </Popup>
          </CircleMarker>


          {/* WAREHOUSE */}

          <CircleMarker
            center={destination}
            radius={10}
            pathOptions={{
              fillOpacity: 1
            }}
          >
            <Popup>
              <strong>
                Destination Warehouse
              </strong>

              <br />

              {
                shipment.destination_location
              }
            </Popup>
          </CircleMarker>


          {/* CURRENT VEHICLE POSITION */}

          {current && (
            <CircleMarker
              center={current}
              radius={12}
              pathOptions={{
                fillOpacity: 1
              }}
            >
              <Popup>
                <strong>
                  Shipment Vehicle
                </strong>

                <br />

                Status:{" "}
                {
                  shipment.status
                }

                <br />

                Progress:{" "}
                {
                  formatDecimal(
                    shipment.progress_percentage,
                    0
                  )
                }
                %
              </Popup>
            </CircleMarker>
          )}
        </MapContainer>
      </Box>
    </Box>
  );
}


// ============================================================
// ORDERS PAGE
// ============================================================

function Orders() {
  const [
    orders,
    setOrders
  ] = useState([]);


  const [
    loading,
    setLoading
  ] = useState(true);


  const [
    error,
    setError
  ] = useState("");


  const [
    success,
    setSuccess
  ] = useState("");


  const [
    selectedOrder,
    setSelectedOrder
  ] = useState(null);


  const [
    trackingDialogOpen,
    setTrackingDialogOpen
  ] = useState(false);


  const [
    receiveDialogOpen,
    setReceiveDialogOpen
  ] = useState(false);


  const [
    trackingStage,
    setTrackingStage
  ] = useState("");


  const [
    currentLocation,
    setCurrentLocation
  ] = useState("");


  const [
    trackingNotes,
    setTrackingNotes
  ] = useState("");


  const [
    receiveQuantity,
    setReceiveQuantity
  ] = useState("");


  const [
    submitting,
    setSubmitting
  ] = useState(false);


  const [
    shipmentLoading,
    setShipmentLoading
  ] = useState(false);


  const [
    shipment,
    setShipment
  ] = useState(null);


  const [
    shipmentHistory,
    setShipmentHistory
  ] = useState([]);


  const [
    orderHistory,
    setOrderHistory
  ] = useState([]);


  // ============================================================
  // LOAD ORDERS
  // ============================================================

  const loadOrders =
    async () => {
      try {
        setLoading(true);

        setError("");

        const data =
          await getPurchaseOrders(
            false
          );

        setOrders(
          Array.isArray(data)
            ? data
            : []
        );
      }
      catch (err) {
        setError(
          err?.message ||
          "Unable to load purchase orders."
        );
      }
      finally {
        setLoading(false);
      }
    };


  useEffect(() => {
    loadOrders();
  }, []);


  // ============================================================
  // REFRESH CURRENT ORDER
  // ============================================================

  const refreshSelectedOrder =
    async (
      orderId
    ) => {
      const data =
        await getPurchaseOrders(
          false
        );

      const list =
        Array.isArray(data)
          ? data
          : [];

      setOrders(list);

      const updated =
        list.find(
          order =>
            Number(order.id) ===
            Number(orderId)
        );

      if (updated) {
        setSelectedOrder(
          updated
        );

        setTrackingStage(
          updated.tracking_stage ||
          "ORDER_PLACED"
        );

        setCurrentLocation(
          updated.current_location ||
          ""
        );

        setTrackingNotes(
          updated.tracking_notes ||
          ""
        );
      }

      return updated;
    };


  // ============================================================
  // LOAD SHIPMENT / HISTORY
  // ============================================================

  const loadShipmentData =
    async (
      orderId,
      showLoader = true
    ) => {
      if (!orderId) {
        return;
      }

      try {
        if (showLoader) {
          setShipmentLoading(
            true
          );
        }


        // --------------------------------
        // ORDER STATUS HISTORY
        // --------------------------------

        try {
          const historyResult =
            await getPurchaseOrderHistory(
              orderId
            );

          setOrderHistory(
            Array.isArray(
              historyResult
            )
              ? historyResult
              : []
          );
        }
        catch {
          setOrderHistory([]);
        }


        // --------------------------------
        // SHIPMENT
        // --------------------------------

        try {
          const shipmentResult =
            await getPurchaseOrderShipment(
              orderId
            );

          setShipment(
            shipmentResult ||
            null
          );


          // --------------------------------
          // GPS HISTORY
          // --------------------------------

          try {
            const gpsHistory =
              await getShipmentTrackingHistory(
                orderId
              );

            setShipmentHistory(
              Array.isArray(
                gpsHistory
              )
                ? gpsHistory
                : []
            );
          }
          catch {
            setShipmentHistory([]);
          }
        }
        catch {
          // Shipment does not exist before dispatch.
          setShipment(null);
          setShipmentHistory([]);
        }
      }
      finally {
        if (showLoader) {
          setShipmentLoading(
            false
          );
        }
      }
    };


  // ============================================================
  // OPEN TRACKING DIALOG
  // ============================================================

  const openTracking =
    async order => {
      setError("");
      setSuccess("");

      setSelectedOrder(
        order
      );

      setTrackingStage(
        order.tracking_stage ||
        "ORDER_PLACED"
      );

      setCurrentLocation(
        order.current_location ||
        ""
      );

      setTrackingNotes(
        order.tracking_notes ||
        ""
      );

      setShipment(null);
      setShipmentHistory([]);
      setOrderHistory([]);

      setTrackingDialogOpen(
        true
      );

      await loadShipmentData(
        order.id
      );
    };


  // ============================================================
  // OPEN RECEIVE DIALOG
  // ============================================================

  const openReceive =
    order => {
      setError("");

      setSelectedOrder(
        order
      );

      setReceiveQuantity(
        order.remaining_quantity ||
        ""
      );

      setReceiveDialogOpen(
        true
      );
    };


  // ============================================================
  // SAVE MANUAL TRACKING
  // ============================================================

  const saveTracking =
    async () => {
      if (!selectedOrder) {
        return;
      }

      try {
        setSubmitting(true);

        setError("");
        setSuccess("");


        await updatePurchaseOrderTracking(
          selectedOrder.id,
          trackingStage,
          currentLocation,
          trackingNotes
        );


        const updated =
          await refreshSelectedOrder(
            selectedOrder.id
          );


        await loadShipmentData(
          selectedOrder.id,
          false
        );


        if (
          updated?.tracking_stage ===
          "DISPATCHED"
        ) {
          setSuccess(
            "Order dispatched successfully. Shipment tracking has been created automatically."
          );
        }
        else {
          setSuccess(
            "Purchase order tracking updated successfully."
          );
        }
      }
      catch (err) {
        setError(
          err?.message ||
          "Unable to update tracking."
        );
      }
      finally {
        setSubmitting(false);
      }
    };


  // ============================================================
  // SIMULATE NEXT GPS LOCATION
  // ============================================================

  const simulateNextGPS =
    async () => {
      if (!selectedOrder) {
        return;
      }

      try {
        setSubmitting(true);

        setError("");
        setSuccess("");


        await simulateShipmentLocation(
          selectedOrder.id
        );


        const updated =
          await refreshSelectedOrder(
            selectedOrder.id
          );


        await loadShipmentData(
          selectedOrder.id,
          false
        );


        if (
          updated?.tracking_stage ===
          "ARRIVED_AT_WAREHOUSE"
        ) {
          setSuccess(
            "Shipment has arrived at the destination warehouse. The order is now ready to receive."
          );
        }
        else {
          setSuccess(
            "Next simulated GPS position generated successfully."
          );
        }
      }
      catch (err) {
        setError(
          err?.message ||
          "Unable to simulate the next GPS location."
        );
      }
      finally {
        setSubmitting(false);
      }
    };


  // ============================================================
  // RECEIVE PURCHASE ORDER
  // ============================================================

  const saveReceipt =
    async () => {
      if (!selectedOrder) {
        return;
      }


      const quantity =
        Number(
          receiveQuantity
        );


      if (
        !Number.isFinite(
          quantity
        ) ||
        quantity <= 0
      ) {
        setError(
          "Enter a valid received quantity greater than zero."
        );

        return;
      }


      if (
        quantity >
        Number(
          selectedOrder.remaining_quantity ||
          0
        )
      ) {
        setError(
          "Received quantity cannot be greater than the remaining order quantity."
        );

        return;
      }


      try {
        setSubmitting(true);

        setError("");
        setSuccess("");


        await receivePurchaseOrder(
          selectedOrder.id,
          quantity
        );


        setReceiveDialogOpen(
          false
        );


        const updated =
          await refreshSelectedOrder(
            selectedOrder.id
          );


        await loadShipmentData(
          selectedOrder.id,
          false
        );


        if (
          updated?.tracking_stage ===
          "RECEIVED"
        ) {
          setSuccess(
            "Purchase order fully received. Inventory has been updated and the shipment is complete."
          );
        }
        else {
          setSuccess(
            "Partial receipt recorded successfully. Inventory has been updated."
          );
        }
      }
      catch (err) {
        setError(
          err?.message ||
          "Unable to receive purchase order."
        );
      }
      finally {
        setSubmitting(false);
      }
    };


  // ============================================================
  // SUMMARY COUNTS
  // ============================================================

  const activeOrders =
    orders.filter(
      order =>
        ![
          "DELIVERED",
          "CANCELLED"
        ].includes(
          order.order_status
        )
    ).length;


  const inTransit =
    orders.filter(
      order =>
        [
          "DISPATCHED",
          "IN_TRANSIT"
        ].includes(
          order.tracking_stage
        )
    ).length;


  const delayed =
    orders.filter(
      order =>
        order.is_delayed
    ).length;


  const received =
    orders.filter(
      order =>
        order.order_status ===
        "DELIVERED" ||
        order.tracking_stage ===
        "RECEIVED"
    ).length;


  // ============================================================
  // RECEIVE PERMISSION
  // ============================================================

  const canReceive =
    selectedOrder &&
    [
      "ARRIVED_AT_WAREHOUSE",
      "PARTIALLY_RECEIVED"
    ].includes(
      selectedOrder.tracking_stage
    );


  // ============================================================
  // GPS PERMISSION
  // ============================================================

  const canSimulateGPS =
    shipment &&
    [
      "DISPATCHED",
      "IN_TRANSIT"
    ].includes(
      shipment.status
    ) &&
    Number(
      shipment.progress_percentage ||
      0
    ) < 100;


  // ============================================================
  // CURRENT MANUAL OPTIONS
  // ============================================================

  const manualOptions =
    selectedOrder
      ? getAllowedManualStages(
          selectedOrder.tracking_stage
        )
      : [];


  // ============================================================
  // PAGE
  // ============================================================

  return (
    <Box
      sx={{
        p: 3
      }}
    >
      {/* ==================================================== */}
      {/* HEADER */}
      {/* ==================================================== */}

      <Box
        sx={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          mb: 3
        }}
      >
        <Box>
          <Typography
            variant="h5"
            fontWeight={700}
          >
            Purchase Order Tracking
          </Typography>

          <Typography
            color="text.secondary"
          >
            Track purchase orders, shipment lifecycle,
            simulated GPS movement and warehouse receipt
          </Typography>
        </Box>


        <Button
          variant="outlined"
          startIcon={
            <RefreshIcon />
          }
          onClick={
            loadOrders
          }
        >
          Refresh
        </Button>
      </Box>


      {/* ==================================================== */}
      {/* PAGE MESSAGES */}
      {/* ==================================================== */}

      {error && (
        <Alert
          severity="error"
          sx={{
            mb: 2
          }}
          onClose={() =>
            setError("")
          }
        >
          {error}
        </Alert>
      )}


      {success && (
        <Alert
          severity="success"
          sx={{
            mb: 2
          }}
          onClose={() =>
            setSuccess("")
          }
        >
          {success}
        </Alert>
      )}


      {/* ==================================================== */}
      {/* SUMMARY */}
      {/* ==================================================== */}

      <Grid
        container
        spacing={2}
        sx={{
          mb: 3
        }}
      >
        <Grid
          size={{
            xs: 12,
            md: 3
          }}
        >
          <SummaryCard
            title="Active Orders"
            value={
              activeOrders
            }
            subtitle="Still being fulfilled"
            icon={
              <InventoryIcon />
            }
          />
        </Grid>


        <Grid
          size={{
            xs: 12,
            md: 3
          }}
        >
          <SummaryCard
            title="In Transit"
            value={
              inTransit
            }
            subtitle="Currently moving"
            icon={
              <LocalShippingIcon />
            }
          />
        </Grid>


        <Grid
          size={{
            xs: 12,
            md: 3
          }}
        >
          <SummaryCard
            title="Delayed"
            value={
              delayed
            }
            subtitle="Past expected arrival"
            icon={
              <WarningAmberIcon />
            }
          />
        </Grid>


        <Grid
          size={{
            xs: 12,
            md: 3
          }}
        >
          <SummaryCard
            title="Received"
            value={
              received
            }
            subtitle="Completed orders"
            icon={
              <CheckCircleIcon />
            }
          />
        </Grid>
      </Grid>


      {/* ==================================================== */}
      {/* PURCHASE ORDER TABLE */}
      {/* ==================================================== */}

      <Card
        elevation={0}
        sx={{
          border:
            "1px solid #e5e7eb",
          borderRadius: 3
        }}
      >
        <CardContent>
          {loading ? (
            <Box
              sx={{
                display: "flex",
                justifyContent:
                  "center",
                py: 6
              }}
            >
              <CircularProgress />
            </Box>
          ) : orders.length ===
            0 ? (
            <Alert severity="info">
              No application-created purchase orders yet.
              Create an order from Procurement and it will
              appear here.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>
                        PO
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Component
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Supplier
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Vehicle
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Destination
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Ordered
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Remaining
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Stage
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Current Location
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        ETA
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Action
                      </strong>
                    </TableCell>
                  </TableRow>
                </TableHead>


                <TableBody>
                  {orders.map(
                    order => (
                      <TableRow
                        key={
                          order.id
                        }
                        hover
                      >
                        <TableCell>
                          {
                            order.po_number
                          }
                        </TableCell>


                        <TableCell>
                          <Typography
                            variant="body2"
                            fontWeight={600}
                          >
                            {
                              order.part_name
                            }
                          </Typography>

                          <Typography
                            variant="caption"
                            color="text.secondary"
                          >
                            {
                              order.part_id
                            }
                          </Typography>
                        </TableCell>


                        <TableCell>
                          {
                            order.supplier_name
                          }
                        </TableCell>


                        <TableCell>
                          {
                            order.vehicle_type ||
                            "-"
                          }
                        </TableCell>


                        <TableCell>
                          {
                            order.warehouse
                          }
                        </TableCell>


                        <TableCell
                          align="right"
                        >
                          {
                            formatNumber(
                              order.quantity_ordered
                            )
                          }
                        </TableCell>


                        <TableCell
                          align="right"
                        >
                          {
                            formatNumber(
                              order.remaining_quantity
                            )
                          }
                        </TableCell>


                        <TableCell>
                          <TrackingChip
                            stage={
                              order.tracking_stage
                            }
                          />
                        </TableCell>


                        <TableCell>
                          <Tooltip
                            title={
                              order.tracking_notes ||
                              ""
                            }
                          >
                            <Typography
                              variant="body2"
                            >
                              {
                                order.current_location ||
                                "-"
                              }
                            </Typography>
                          </Tooltip>
                        </TableCell>


                        <TableCell>
                          <Typography
                            variant="body2"
                            color={
                              order.is_delayed
                                ? "error"
                                : "inherit"
                            }
                          >
                            {
                              formatDate(
                                order.expected_delivery_date
                              )
                            }
                          </Typography>

                          {order.days_until_expected_arrival !==
                            null &&
                            order.days_until_expected_arrival !==
                              undefined && (
                            <Typography
                              variant="caption"
                              color={
                                order.is_delayed
                                  ? "error"
                                  : "text.secondary"
                              }
                            >
                              {
                                order.days_until_expected_arrival
                              }{" "}
                              day(s)
                            </Typography>
                          )}
                        </TableCell>


                        <TableCell>
                          <Stack
                            direction="row"
                            spacing={1}
                          >
                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={
                                <LocalShippingIcon />
                              }
                              onClick={() =>
                                openTracking(
                                  order
                                )
                              }
                            >
                              Track
                            </Button>


                            {[
                              "ARRIVED_AT_WAREHOUSE",
                              "PARTIALLY_RECEIVED"
                            ].includes(
                              order.tracking_stage
                            ) && (
                              <Button
                                size="small"
                                variant="contained"
                                onClick={() =>
                                  openReceive(
                                    order
                                  )
                                }
                              >
                                Receive
                              </Button>
                            )}
                          </Stack>
                        </TableCell>
                      </TableRow>
                    )
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>


      {/* ==================================================== */}
      {/* ADVANCED TRACKING DIALOG */}
      {/* ==================================================== */}

      <Dialog
        open={
          trackingDialogOpen
        }
        onClose={() => {
          if (!submitting) {
            setTrackingDialogOpen(
              false
            );
          }
        }}
        fullWidth
        maxWidth="lg"
      >
        <DialogTitle>
          Purchase Order & Shipment Tracking
        </DialogTitle>


        <DialogContent>
          {selectedOrder && (
            <Stack
              spacing={3}
              sx={{
                mt: 1
              }}
            >
              {/* ============================================ */}
              {/* ORDER HEADER */}
              {/* ============================================ */}

              <Stack
                direction={{
                  xs: "column",
                  sm: "row"
                }}
                justifyContent="space-between"
                alignItems={{
                  xs: "flex-start",
                  sm: "center"
                }}
                spacing={1}
              >
                <Box>
                  <Typography
                    variant="h6"
                    fontWeight={700}
                  >
                    {
                      selectedOrder.po_number
                    }
                  </Typography>

                  <Typography
                    color="text.secondary"
                  >
                    {
                      selectedOrder.part_name
                    }

                    {" • "}

                    {
                      selectedOrder.supplier_name
                    }

                    {" → "}

                    {
                      selectedOrder.warehouse
                    }
                  </Typography>
                </Box>


                <TrackingChip
                  stage={
                    selectedOrder.tracking_stage
                  }
                />
              </Stack>


              <Divider />


              {/* ============================================ */}
              {/* ORDER LIFECYCLE */}
              {/* ============================================ */}

              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  sx={{
                    mb: 2
                  }}
                >
                  Order Lifecycle
                </Typography>


                <Stepper
                  activeStep={
                    getActiveStep(
                      selectedOrder.tracking_stage
                    )
                  }
                  alternativeLabel
                >
                  {TRACKING_STAGES.map(
                    stage => (
                      <Step
                        key={
                          stage
                        }
                      >
                        <StepLabel>
                          {
                            TRACKING_LABELS[
                              stage
                            ]
                          }
                        </StepLabel>
                      </Step>
                    )
                  )}
                </Stepper>


                {selectedOrder.tracking_stage ===
                  "PARTIALLY_RECEIVED" && (
                  <Alert
                    severity="warning"
                    sx={{
                      mt: 2
                    }}
                  >
                    Shipment has been partially received.
                    Remaining quantity:{" "}
                    <strong>
                      {
                        formatNumber(
                          selectedOrder.remaining_quantity
                        )
                      }
                    </strong>
                  </Alert>
                )}
              </Box>


              <Divider />


              {/* ============================================ */}
              {/* MANUAL PRE-DISPATCH CONTROL */}
              {/* ============================================ */}

              {MANUAL_TRACKING_STAGES.includes(
                selectedOrder.tracking_stage
              ) && (
                <Box>
                  <Typography
                    variant="subtitle1"
                    fontWeight={700}
                    sx={{
                      mb: 2
                    }}
                  >
                    Order Status Update
                  </Typography>


                  <Alert
                    severity="info"
                    sx={{
                      mb: 2
                    }}
                  >
                    Before dispatch, the order stage can be
                    updated manually. After dispatch, shipment
                    movement is controlled by the simulated
                    GPS tracker.
                  </Alert>


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
                      <TextField
                        select
                        fullWidth
                        label="Tracking Stage"
                        value={
                          trackingStage
                        }
                        onChange={
                          event =>
                            setTrackingStage(
                              event.target.value
                            )
                        }
                      >
                        {manualOptions.map(
                          stage => (
                            <MenuItem
                              key={
                                stage
                              }
                              value={
                                stage
                              }
                            >
                              {
                                TRACKING_LABELS[
                                  stage
                                ]
                              }
                            </MenuItem>
                          )
                        )}
                      </TextField>
                    </Grid>


                    <Grid
                      size={{
                        xs: 12,
                        md: 4
                      }}
                    >
                      <TextField
                        fullWidth
                        label="Current Location"
                        value={
                          currentLocation
                        }
                        onChange={
                          event =>
                            setCurrentLocation(
                              event.target.value
                            )
                        }
                        placeholder="Supplier / logistics location"
                      />
                    </Grid>


                    <Grid
                      size={{
                        xs: 12,
                        md: 4
                      }}
                    >
                      <TextField
                        fullWidth
                        label="Tracking Notes"
                        value={
                          trackingNotes
                        }
                        onChange={
                          event =>
                            setTrackingNotes(
                              event.target.value
                            )
                        }
                        placeholder="Optional notes"
                      />
                    </Grid>
                  </Grid>


                  <Box
                    sx={{
                      mt: 2
                    }}
                  >
                    <Button
                      variant="contained"
                      onClick={
                        saveTracking
                      }
                      disabled={
                        submitting
                      }
                    >
                      {
                        submitting
                          ? "Updating..."
                          : trackingStage ===
                            "DISPATCHED"
                            ? "Dispatch Order"
                            : "Update Order Stage"
                      }
                    </Button>
                  </Box>
                </Box>
              )}


              {/* ============================================ */}
              {/* LOADING SHIPMENT */}
              {/* ============================================ */}

              {shipmentLoading && (
                <Box
                  sx={{
                    display: "flex",
                    justifyContent:
                      "center",
                    py: 4
                  }}
                >
                  <CircularProgress />
                </Box>
              )}


              {/* ============================================ */}
              {/* BEFORE SHIPMENT EXISTS */}
              {/* ============================================ */}

              {!shipmentLoading &&
                !shipment &&
                [
                  "ORDER_PLACED",
                  "SUPPLIER_CONFIRMED",
                  "READY_FOR_DISPATCH"
                ].includes(
                  selectedOrder.tracking_stage
                ) && (
                  <Alert severity="info">
                    Shipment GPS tracking will become
                    available automatically after this
                    purchase order is dispatched.
                  </Alert>
                )}


              {/* ============================================ */}
              {/* SHIPMENT */}
              {/* ============================================ */}

              {!shipmentLoading &&
                shipment && (
                  <>
                    <Divider />


                    <Box>
                      <Stack
                        direction={{
                          xs: "column",
                          sm: "row"
                        }}
                        justifyContent="space-between"
                        alignItems={{
                          xs: "flex-start",
                          sm: "center"
                        }}
                        spacing={1}
                        sx={{
                          mb: 2
                        }}
                      >
                        <Box>
                          <Typography
                            variant="h6"
                            fontWeight={700}
                          >
                            Simulated GPS Shipment Tracking
                          </Typography>

                          <Typography
                            color="text.secondary"
                          >
                            Shipment:{" "}
                            {
                              shipment.shipment_number
                            }
                          </Typography>
                        </Box>


                        <Chip
                          icon={
                            <LocalShippingIcon />
                          }
                          label={
                            shipment.status
                          }
                          color={
                            shipment.status ===
                            "COMPLETED"
                              ? "success"
                              : shipment.status ===
                                "ARRIVED"
                                ? "warning"
                                : "info"
                          }
                        />
                      </Stack>


                      {/* ==================================== */}
                      {/* PROGRESS */}
                      {/* ==================================== */}

                      <Box
                        sx={{
                          mb: 3
                        }}
                      >
                        <Stack
                          direction="row"
                          justifyContent="space-between"
                          sx={{
                            mb: 1
                          }}
                        >
                          <Typography
                            fontWeight={600}
                          >
                            Shipment Progress
                          </Typography>

                          <Typography
                            fontWeight={700}
                          >
                            {
                              formatDecimal(
                                shipment.progress_percentage,
                                0
                              )
                            }
                            %
                          </Typography>
                        </Stack>


                        <LinearProgress
                          variant="determinate"
                          value={
                            Math.min(
                              100,
                              Math.max(
                                0,
                                Number(
                                  shipment.progress_percentage ||
                                  0
                                )
                              )
                            )
                          }
                          sx={{
                            height: 10,
                            borderRadius: 10
                          }}
                        />
                      </Box>


                      {/* ==================================== */}
                      {/* METRICS */}
                      {/* ==================================== */}

                      <Grid
                        container
                        spacing={2}
                        sx={{
                          mb: 3
                        }}
                      >
                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}
                        >
                          <ShipmentMetric
                            icon={
                              <RouteIcon />
                            }
                            title="Remaining Distance"
                            value={`${formatDecimal(
                              shipment.remaining_distance_km
                            )} km`}
                          />
                        </Grid>


                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}
                        >
                          <ShipmentMetric
                            icon={
                              <SpeedIcon />
                            }
                            title="Current Speed"
                            value={`${formatDecimal(
                              shipment.current_speed_kmph
                            )} km/h`}
                          />
                        </Grid>


                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}
                        >
                          <ShipmentMetric
                            icon={
                              <AccessTimeIcon />
                            }
                            title="Estimated Arrival"
                            value={
                              formatDateTime(
                                shipment.estimated_arrival
                              )
                            }
                          />
                        </Grid>


                        <Grid
                          size={{
                            xs: 12,
                            sm: 6,
                            md: 3
                          }}
                        >
                          <ShipmentMetric
                            icon={
                              <MyLocationIcon />
                            }
                            title="Last GPS Update"
                            value={
                              formatDateTime(
                                shipment.last_location_update
                              )
                            }
                          />
                        </Grid>
                      </Grid>


                      {/* ==================================== */}
                      {/* ORIGIN / DESTINATION */}
                      {/* ==================================== */}

                      <Grid
                        container
                        spacing={2}
                        sx={{
                          mb: 3
                        }}
                      >
                        <Grid
                          size={{
                            xs: 12,
                            md: 6
                          }}
                        >
                          <Paper
                            variant="outlined"
                            sx={{
                              p: 2,
                              borderRadius: 2
                            }}
                          >
                            <Stack
                              direction="row"
                              spacing={1}
                            >
                              <LocationOnIcon />

                              <Box>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Supplier Origin
                                </Typography>

                                <Typography
                                  fontWeight={700}
                                >
                                  {
                                    shipment.origin_location
                                  }
                                </Typography>
                              </Box>
                            </Stack>
                          </Paper>
                        </Grid>


                        <Grid
                          size={{
                            xs: 12,
                            md: 6
                          }}
                        >
                          <Paper
                            variant="outlined"
                            sx={{
                              p: 2,
                              borderRadius: 2
                            }}
                          >
                            <Stack
                              direction="row"
                              spacing={1}
                            >
                              <LocationOnIcon />

                              <Box>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Destination Warehouse
                                </Typography>

                                <Typography
                                  fontWeight={700}
                                >
                                  {
                                    shipment.destination_location
                                  }
                                </Typography>
                              </Box>
                            </Stack>
                          </Paper>
                        </Grid>
                      </Grid>


                      {/* ==================================== */}
                      {/* MAP */}
                      {/* ==================================== */}

                      <ShipmentMap
                        shipment={
                          shipment
                        }
                        trackingPoints={
                          shipmentHistory
                        }
                      />


                      {/* ==================================== */}
                      {/* GPS BUTTON */}
                      {/* ==================================== */}

                      {canSimulateGPS && (
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent:
                              "center",
                            mt: 3
                          }}
                        >
                          <Button
                            variant="contained"
                            size="large"
                            startIcon={
                              <MyLocationIcon />
                            }
                            onClick={
                              simulateNextGPS
                            }
                            disabled={
                              submitting
                            }
                          >
                            {
                              submitting
                                ? "Generating GPS Update..."
                                : "Simulate Next GPS Update"
                            }
                          </Button>
                        </Box>
                      )}


                      {/* ==================================== */}
                      {/* ARRIVED */}
                      {/* ==================================== */}

                      {shipment.status ===
                        "ARRIVED" && (
                        <Alert
                          severity="success"
                          sx={{
                            mt: 3
                          }}
                        >
                          Shipment has arrived at{" "}
                          <strong>
                            {
                              shipment.destination_location
                            }
                          </strong>
                          . The purchase order can now be
                          received into inventory.
                        </Alert>
                      )}


                      {/* ==================================== */}
                      {/* COMPLETED */}
                      {/* ==================================== */}

                      {shipment.status ===
                        "COMPLETED" && (
                        <Alert
                          severity="success"
                          sx={{
                            mt: 3
                          }}
                        >
                          Shipment completed and the purchase
                          order has been fully received.
                        </Alert>
                      )}
                    </Box>


                    {/* ====================================== */}
                    {/* GPS HISTORY */}
                    {/* ====================================== */}

                    <Divider />


                    <Box>
                      <Typography
                        variant="h6"
                        fontWeight={700}
                        sx={{
                          mb: 2
                        }}
                      >
                        GPS Tracking History
                      </Typography>


                      {shipmentHistory.length ===
                        0 ? (
                        <Alert severity="info">
                          No GPS tracking points have been
                          generated yet.
                        </Alert>
                      ) : (
                        <TableContainer
                          component={
                            Paper
                          }
                          variant="outlined"
                        >
                          <Table
                            size="small"
                          >
                            <TableHead>
                              <TableRow>
                                <TableCell>
                                  Progress
                                </TableCell>

                                <TableCell>
                                  Location
                                </TableCell>

                                <TableCell>
                                  Latitude
                                </TableCell>

                                <TableCell>
                                  Longitude
                                </TableCell>

                                <TableCell>
                                  Speed
                                </TableCell>

                                <TableCell>
                                  Remaining
                                </TableCell>

                                <TableCell>
                                  Status
                                </TableCell>

                                <TableCell>
                                  Time
                                </TableCell>
                              </TableRow>
                            </TableHead>


                            <TableBody>
                              {[...shipmentHistory]
                                .reverse()
                                .map(
                                  point => (
                                    <TableRow
                                      key={
                                        point.id
                                      }
                                    >
                                      <TableCell>
                                        {
                                          formatDecimal(
                                            point.progress_percentage,
                                            0
                                          )
                                        }
                                        %
                                      </TableCell>

                                      <TableCell>
                                        {
                                          point.location_name ||
                                          "-"
                                        }
                                      </TableCell>

                                      <TableCell>
                                        {
                                          formatDecimal(
                                            point.latitude,
                                            5
                                          )
                                        }
                                      </TableCell>

                                      <TableCell>
                                        {
                                          formatDecimal(
                                            point.longitude,
                                            5
                                          )
                                        }
                                      </TableCell>

                                      <TableCell>
                                        {
                                          formatDecimal(
                                            point.speed_kmph
                                          )
                                        }{" "}
                                        km/h
                                      </TableCell>

                                      <TableCell>
                                        {
                                          formatDecimal(
                                            point.remaining_distance_km
                                          )
                                        }{" "}
                                        km
                                      </TableCell>

                                      <TableCell>
                                        <Chip
                                          size="small"
                                          label={
                                            point.status
                                          }
                                        />
                                      </TableCell>

                                      <TableCell>
                                        {
                                          formatDateTime(
                                            point.recorded_at
                                          )
                                        }
                                      </TableCell>
                                    </TableRow>
                                  )
                                )}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      )}
                    </Box>
                  </>
                )}


              {/* ============================================ */}
              {/* ORDER STATUS HISTORY */}
              {/* ============================================ */}

              <Divider />


              <Box>
                <Typography
                  variant="h6"
                  fontWeight={700}
                  sx={{
                    mb: 2
                  }}
                >
                  Order Status History
                </Typography>


                {orderHistory.length ===
                  0 ? (
                  <Alert severity="info">
                    No order status history available.
                  </Alert>
                ) : (
                  <Stack
                    spacing={1.5}
                  >
                    {orderHistory.map(
                      item => (
                        <Paper
                          key={
                            item.id
                          }
                          variant="outlined"
                          sx={{
                            p: 2,
                            borderRadius: 2
                          }}
                        >
                          <Stack
                            direction={{
                              xs: "column",
                              sm: "row"
                            }}
                            justifyContent="space-between"
                            spacing={1}
                          >
                            <Box>
                              <Typography
                                fontWeight={700}
                              >
                                {item.from_stage
                                  ? `${
                                      TRACKING_LABELS[
                                        item.from_stage
                                      ] ||
                                      item.from_stage
                                    } → `
                                  : ""}

                                {
                                  TRACKING_LABELS[
                                    item.to_stage
                                  ] ||
                                  item.to_stage
                                }
                              </Typography>


                              {item.location && (
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                >
                                  Location:{" "}
                                  {
                                    item.location
                                  }
                                </Typography>
                              )}


                              {item.notes && (
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                >
                                  {
                                    item.notes
                                  }
                                </Typography>
                              )}
                            </Box>


                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {
                                formatDateTime(
                                  item.changed_at
                                )
                              }
                            </Typography>
                          </Stack>
                        </Paper>
                      )
                    )}
                  </Stack>
                )}
              </Box>


              {/* ============================================ */}
              {/* RECEIVE AFTER WAREHOUSE ARRIVAL */}
              {/* ============================================ */}

              {canReceive && (
                <>
                  <Divider />

                  <Alert
                    severity="success"
                    action={
                      <Button
                        color="inherit"
                        size="small"
                        onClick={() =>
                          openReceive(
                            selectedOrder
                          )
                        }
                      >
                        Receive Stock
                      </Button>
                    }
                  >
                    Shipment is at the warehouse and can now
                    be received into inventory.
                  </Alert>
                </>
              )}
            </Stack>
          )}
        </DialogContent>


        <DialogActions>
          <Button
            onClick={() =>
              setTrackingDialogOpen(
                false
              )
            }
            disabled={
              submitting
            }
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>


      {/* ==================================================== */}
      {/* RECEIVE DIALOG */}
      {/* ==================================================== */}

      <Dialog
        open={
          receiveDialogOpen
        }
        onClose={() => {
          if (!submitting) {
            setReceiveDialogOpen(
              false
            );
          }
        }}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>
          Receive Purchase Order
        </DialogTitle>


        <DialogContent>
          {selectedOrder && (
            <Stack
              spacing={2}
              sx={{
                mt: 1
              }}
            >
              <Alert
                severity="info"
              >
                Remaining quantity:{" "}
                <strong>
                  {
                    formatNumber(
                      selectedOrder.remaining_quantity
                    )
                  }
                </strong>

                <br />

                Destination:{" "}

                <strong>
                  {
                    selectedOrder.warehouse
                  }
                </strong>
              </Alert>


              <TextField
                label="Quantity Received"
                type="number"
                value={
                  receiveQuantity
                }
                onChange={
                  event =>
                    setReceiveQuantity(
                      event.target.value
                    )
                }
                slotProps={{
                  htmlInput: {
                    min: 1,
                    max:
                      selectedOrder.remaining_quantity
                  }
                }}
                fullWidth
              />


              <Typography
                variant="caption"
                color="text.secondary"
              >
                Partial receipts are supported. Receiving the
                full remaining quantity completes the purchase
                order and shipment.
              </Typography>
            </Stack>
          )}
        </DialogContent>


        <DialogActions>
          <Button
            onClick={() =>
              setReceiveDialogOpen(
                false
              )
            }
            disabled={
              submitting
            }
          >
            Cancel
          </Button>


          <Button
            variant="contained"
            onClick={
              saveReceipt
            }
            disabled={
              submitting
            }
          >
            {
              submitting
                ? "Receiving..."
                : "Receive Stock"
            }
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}


export default Orders;