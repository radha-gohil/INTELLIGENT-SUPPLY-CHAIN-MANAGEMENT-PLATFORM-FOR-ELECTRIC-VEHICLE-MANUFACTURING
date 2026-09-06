import {
  useEffect,
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
  Grid,
  MenuItem,
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

import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import RefreshIcon from "@mui/icons-material/Refresh";
import InventoryIcon from "@mui/icons-material/Inventory";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

import {
  getPurchaseOrders,
  updatePurchaseOrderTracking,
  receivePurchaseOrder
} from "../services/api";


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

  ORDER_PLACED:
    "Order Placed",

  SUPPLIER_CONFIRMED:
    "Supplier Confirmed",

  READY_FOR_DISPATCH:
    "Ready for Dispatch",

  DISPATCHED:
    "Dispatched",

  IN_TRANSIT:
    "In Transit",

  ARRIVED_AT_WAREHOUSE:
    "Arrived at Warehouse",

  PARTIALLY_RECEIVED:
    "Partially Received",

  RECEIVED:
    "Received",

  CANCELLED:
    "Cancelled"

};


function formatNumber(
  value
) {

  return Number(
    value || 0
  ).toLocaleString();

}


function formatDate(
  value
) {

  if (!value) {

    return "-";

  }


  return new Date(
    `${value}T00:00:00`
  ).toLocaleDateString();

}


function TrackingChip({
  stage
}) {

  let color =
    "default";


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
    stage ===
    "ARRIVED_AT_WAREHOUSE"
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
        TRACKING_LABELS[
          stage
        ]
        ||
        stage
        ||
        "Not Tracked"
      }
    />

  );

}


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

            alignItems:
              "center"
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


          {icon}

        </Box>

      </CardContent>

    </Card>

  );

}


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


  const openTracking =
    order => {

      setSelectedOrder(
        order
      );


      setTrackingStage(
        order.tracking_stage
        ||
        "ORDER_PLACED"
      );


      setCurrentLocation(
        order.current_location
        ||
        ""
      );


      setTrackingNotes(
        order.tracking_notes
        ||
        ""
      );


      setTrackingDialogOpen(
        true
      );

    };


  const openReceive =
    order => {

      setSelectedOrder(
        order
      );


      setReceiveQuantity(
        order.remaining_quantity
        ||
        ""
      );


      setReceiveDialogOpen(
        true
      );

    };


  const saveTracking =
    async () => {

      try {

        setSubmitting(true);


        await updatePurchaseOrderTracking(

          selectedOrder.id,

          trackingStage,

          currentLocation,

          trackingNotes

        );


        setTrackingDialogOpen(
          false
        );


        await loadOrders();

      }

      catch (err) {

        setError(
          err?.message
          ||
          "Unable to update tracking."
        );

      }

      finally {

        setSubmitting(false);

      }

    };


  const saveReceipt =
    async () => {

      try {

        setSubmitting(true);


        await receivePurchaseOrder(

          selectedOrder.id,

          Number(
            receiveQuantity
          )

        );


        setReceiveDialogOpen(
          false
        );


        await loadOrders();

      }

      catch (err) {

        setError(
          err?.message
          ||
          "Unable to receive purchase order."
        );

      }

      finally {

        setSubmitting(false);

      }

    };


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

        order.order_status
        ===
        "DELIVERED"

    ).length;


  return (

    <Box sx={{ p: 3 }}>

      <Box
        sx={{
          display: "flex",

          justifyContent:
            "space-between",

          alignItems:
            "center",

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
            Track ordered components, delivery status, location and warehouse arrival
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


      {error && (

        <Alert
          severity="error"
          sx={{ mb: 3 }}
          onClose={() =>
            setError("")
          }
        >
          {error}
        </Alert>

      )}


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
            value={activeOrders}
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
            value={inTransit}
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
            value={delayed}
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
            value={received}
            subtitle="Completed orders"
            icon={
              <CheckCircleIcon />
            }
          />
        </Grid>

      </Grid>


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

          ) : orders.length === 0 ? (

            <Alert severity="info">
              No application-created purchase orders yet.
              Create an order from Procurement and it will appear here.
            </Alert>

          ) : (

            <TableContainer>

              <Table>

                <TableHead>

                  <TableRow>

                    <TableCell>
                      <strong>PO</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Component</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Supplier</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Vehicle</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Destination</strong>
                    </TableCell>

                    <TableCell align="right">
                      <strong>Ordered</strong>
                    </TableCell>

                    <TableCell align="right">
                      <strong>Remaining</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Stage</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Current Location</strong>
                    </TableCell>

                    <TableCell>
                      <strong>ETA</strong>
                    </TableCell>

                    <TableCell>
                      <strong>Action</strong>
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
                            order.vehicle_type
                            ||
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
                              order.tracking_notes
                              ||
                              ""
                            }
                          >
                            <Typography
                              variant="body2"
                            >
                              {
                                order.current_location
                                ||
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


                          {order
                            .days_until_expected_arrival
                            !== null && (

                            <Typography
                              variant="caption"
                              color={
                                order.is_delayed
                                  ? "error"
                                  : "text.secondary"
                              }
                            >
                              {
                                order
                                  .days_until_expected_arrival
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
                              onClick={() =>
                                openTracking(
                                  order
                                )
                              }
                            >
                              Track
                            </Button>


                            {order.order_status
                              !== "DELIVERED"
                              &&
                              order.order_status
                              !== "CANCELLED" && (

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


      {/* TRACKING DIALOG */}

      <Dialog
        open={
          trackingDialogOpen
        }
        onClose={() =>
          setTrackingDialogOpen(
            false
          )
        }
        fullWidth
        maxWidth="md"
      >

        <DialogTitle>
          Track Purchase Order
        </DialogTitle>


        <DialogContent>

          {selectedOrder && (

            <>

              <Typography
                fontWeight={700}
                sx={{
                  mb: 2
                }}
              >
                {
                  selectedOrder.po_number
                }
                {" • "}
                {
                  selectedOrder.part_name
                }
              </Typography>


              <Stepper
                activeStep={Math.max(
                  TRACKING_STAGES.indexOf(
                    trackingStage
                  ),
                  0
                )}
                alternativeLabel
                sx={{
                  mb: 4
                }}
              >

                {TRACKING_STAGES.map(
                  stage => (

                    <Step
                      key={stage}
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


              <Stack
                spacing={2}
              >

                <TextField
                  select
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

                  {Object
                    .entries(
                      TRACKING_LABELS
                    )
                    .map(
                      (
                        [value, label]
                      ) => (

                        <MenuItem
                          key={value}
                          value={value}
                        >
                          {label}
                        </MenuItem>

                      )
                    )}

                </TextField>


                <TextField
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
                  placeholder="Example: Chennai Logistics Hub"
                />


                <TextField
                  label="Tracking Notes"
                  multiline
                  minRows={3}
                  value={
                    trackingNotes
                  }
                  onChange={
                    event =>
                      setTrackingNotes(
                        event.target.value
                      )
                  }
                />

              </Stack>

            </>

          )}

        </DialogContent>


        <DialogActions>

          <Button
            onClick={() =>
              setTrackingDialogOpen(
                false
              )
            }
          >
            Cancel
          </Button>


          <Button
            variant="contained"
            onClick={
              saveTracking
            }
            disabled={
              submitting
            }
          >
            Update
          </Button>

        </DialogActions>

      </Dialog>


      {/* RECEIVE DIALOG */}

      <Dialog
        open={
          receiveDialogOpen
        }
        onClose={() =>
          setReceiveDialogOpen(
            false
          )
        }
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
                fullWidth
              />

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
            Receive Stock
          </Button>

        </DialogActions>

      </Dialog>

    </Box>

  );

}


export default Orders;