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
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Stack,
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

import InventoryIcon from "@mui/icons-material/Inventory";
import SwapHorizIcon from "@mui/icons-material/SwapHoriz";
import AddBoxIcon from "@mui/icons-material/AddBox";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import TuneIcon from "@mui/icons-material/Tune";
import HistoryIcon from "@mui/icons-material/History";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import AssessmentIcon from "@mui/icons-material/Assessment";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

import {
  getInventoryVehicles,
  getVehicleInventoryComponents,
  getVehicleRequirementAnalysis,
  getInventory,
  getInventoryTransactions,
  receiveStock,
  issueStock,
  adjustStock,
  transferStock
} from "../services/api";


// ============================================================
// DEFAULT REQUIRED DATE
// ============================================================

function getDefaultRequiredDate() {

  const target =
    new Date();


  target.setDate(
    target.getDate() + 30
  );


  return target
    .toISOString()
    .split("T")[0];

}


// ============================================================
// NUMBER FORMAT
// ============================================================

function formatNumber(
  value
) {

  return Number(
    value || 0
  ).toLocaleString();

}


// ============================================================
// DATE FORMAT
// ============================================================

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


// ============================================================
// STATUS CHIP
// ============================================================

function StatusChip({
  status
}) {

  let color =
    "default";


  if (status === "NORMAL") {

    color = "success";

  }

  else if (
    status === "REORDER_REQUIRED"
  ) {

    color = "warning";

  }

  else if (
    status === "CRITICAL" ||
    status === "OUT_OF_STOCK"
  ) {

    color = "error";

  }


  return (
    <Chip
      label={
        status || "UNKNOWN"
      }
      color={color}
      size="small"
      sx={{
        fontWeight: 600
      }}
    />
  );

}


// ============================================================
// CRITICALITY CHIP
// ============================================================

function CriticalityChip({
  criticality
}) {

  const value =
    String(
      criticality || ""
    ).toUpperCase();


  let color =
    "default";


  if (value === "CRITICAL") {

    color = "error";

  }

  else if (value === "HIGH") {

    color = "warning";

  }

  else if (value === "MEDIUM") {

    color = "info";

  }

  else if (value === "LOW") {

    color = "success";

  }


  return (
    <Chip
      label={
        value || "UNKNOWN"
      }
      color={color}
      size="small"
      variant="outlined"
      sx={{
        fontWeight: 600
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

  let color =
    "default";


  if (urgency === "OK") {

    color = "success";

  }

  else if (
    urgency === "MEDIUM"
  ) {

    color = "info";

  }

  else if (
    urgency === "HIGH"
  ) {

    color = "warning";

  }

  else if (
    urgency === "URGENT"
  ) {

    color = "error";

  }


  return (
    <Chip
      label={
        urgency || "UNKNOWN"
      }
      color={color}
      size="small"
      sx={{
        fontWeight: 700
      }}
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

            alignItems:
              "center"
          }}
        >

          <Box>

            <Typography
              variant="body2"
              color="text.secondary"
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
              sx={{
                mt: 0.5
              }}
            >
              {subtitle}
            </Typography>

          </Box>


          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,

              display: "flex",

              alignItems:
                "center",

              justifyContent:
                "center",

              backgroundColor:
                "rgba(25,118,210,0.10)",

              color:
                "primary.main"
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
// INVENTORY
// ============================================================

function Inventory({
  onProcure
}) {

  // ==========================================================
  // VEHICLE
  // ==========================================================

  const [
    vehicles,
    setVehicles
  ] = useState([]);


  const [
    selectedVehicle,
    setSelectedVehicle
  ] = useState(null);


  const [
    vehicleLoading,
    setVehicleLoading
  ] = useState(true);


  // ==========================================================
  // BOM
  // ==========================================================

  const [
    vehicleInventory,
    setVehicleInventory
  ] = useState(null);


  const [
    vehicleInventoryLoading,
    setVehicleInventoryLoading
  ] = useState(false);


  // ==========================================================
  // PRODUCTION PLAN
  // ==========================================================

  const [
    plannedQuantity,
    setPlannedQuantity
  ] = useState(100);


  const [
    requiredDate,
    setRequiredDate
  ] = useState(
    getDefaultRequiredDate()
  );


  const [
    requirementAnalysis,
    setRequirementAnalysis
  ] = useState(null);


  const [
    analysisLoading,
    setAnalysisLoading
  ] = useState(false);


  // ==========================================================
  // GENERAL INVENTORY
  // ==========================================================

  const [
    inventory,
    setInventory
  ] = useState([]);


  const [
    transactions,
    setTransactions
  ] = useState([]);


  const [
    loading,
    setLoading
  ] = useState(true);


  const [
    transactionLoading,
    setTransactionLoading
  ] = useState(false);


  // ==========================================================
  // MESSAGES
  // ==========================================================

  const [
    error,
    setError
  ] = useState("");


  const [
    successMessage,
    setSuccessMessage
  ] = useState("");


  // ==========================================================
  // DIALOG
  // ==========================================================

  const [
    dialogOpen,
    setDialogOpen
  ] = useState(false);


  const [
    dialogType,
    setDialogType
  ] = useState("RECEIPT");


  const [
    submitting,
    setSubmitting
  ] = useState(false);


  const [
    formData,
    setFormData
  ] = useState({

    component_id: "",

    warehouse: "",

    quantity: "",

    reference_id: "",

    source_warehouse: "",

    destination_warehouse: ""

  });


  // ==========================================================
  // LOAD VEHICLE BOM
  // ==========================================================

  const loadVehicleInventory =
    async vehicle => {

      if (!vehicle?.id) {

        return;

      }


      try {

        setVehicleInventoryLoading(
          true
        );


        const data =
          await getVehicleInventoryComponents(
            vehicle.id
          );


        setVehicleInventory(
          data
        );

      }

      catch (err) {

        console.error(
          err
        );


        setError(

          err?.message ||
          "Unable to load vehicle BOM."

        );

      }

      finally {

        setVehicleInventoryLoading(
          false
        );

      }

    };


  // ==========================================================
  // SELECT VEHICLE
  // ==========================================================

  const handleVehicleSelect =
    async vehicle => {

      setSelectedVehicle(
        vehicle
      );


      setRequirementAnalysis(
        null
      );


      await loadVehicleInventory(
        vehicle
      );

    };


  // ==========================================================
  // LOAD VEHICLES
  // ==========================================================

  const loadVehicles =
    async () => {

      try {

        setVehicleLoading(
          true
        );


        const data =
          await getInventoryVehicles();


        const result =
          Array.isArray(data)
            ? data
            : [];


        setVehicles(
          result
        );


        if (
          result.length > 0
        ) {

          setSelectedVehicle(
            result[0]
          );


          await loadVehicleInventory(
            result[0]
          );

        }

      }

      catch (err) {

        setError(

          err?.message ||
          "Unable to load vehicles."

        );

      }

      finally {

        setVehicleLoading(
          false
        );

      }

    };


  // ==========================================================
  // LOAD INVENTORY
  // ==========================================================

  const loadInventory =
    async () => {

      try {

        setLoading(true);


        const data =
          await getInventory();


        setInventory(

          Array.isArray(data)
            ? data
            : []

        );

      }

      catch (err) {

        setError(

          err?.message ||
          "Unable to load inventory."

        );

      }

      finally {

        setLoading(false);

      }

    };


  // ==========================================================
  // TRANSACTIONS
  // ==========================================================

  const loadTransactions =
    async () => {

      try {

        setTransactionLoading(
          true
        );


        const data =
          await getInventoryTransactions();


        setTransactions(

          Array.isArray(data)
            ? data
            : []

        );

      }

      catch (err) {

        console.error(
          err
        );

      }

      finally {

        setTransactionLoading(
          false
        );

      }

    };


  // ==========================================================
  // INITIAL LOAD
  // ==========================================================

  useEffect(() => {

    loadVehicles();

    loadInventory();

    loadTransactions();

  }, []);


  // ==========================================================
  // ANALYZE REQUIREMENTS
  // ==========================================================

  const handleAnalyze =
    async () => {

      if (!selectedVehicle) {

        setError(
          "Select a vehicle first."
        );

        return;

      }


      const quantity =
        Number(
          plannedQuantity
        );


      if (
        !quantity ||
        quantity <= 0
      ) {

        setError(
          "Planned vehicle quantity must be greater than zero."
        );

        return;

      }


      if (!requiredDate) {

        setError(
          "Required date is required."
        );

        return;

      }


      try {

        setError("");


        setAnalysisLoading(
          true
        );


        const data =
          await getVehicleRequirementAnalysis(

            selectedVehicle.id,

            quantity,

            requiredDate

          );


        setRequirementAnalysis(
          data
        );

      }

      catch (err) {

        setError(

          err?.message ||
          "Requirement analysis failed."

        );

      }

      finally {

        setAnalysisLoading(
          false
        );

      }

    };


  // ==========================================================
  // PROCUREMENT HANDOFF
  // ==========================================================

  const handleProcure =
    component => {

      const request = {

        vehicle_id:
          selectedVehicle?.id,

        vehicle_code:
          selectedVehicle
            ?.vehicle_code,

        vehicle_type:
          selectedVehicle
            ?.vehicle_type,

        planned_vehicle_quantity:
          Number(
            plannedQuantity
          ),

        required_date:
          requiredDate,

        component_id:
          component.component_id,

        part_id:
          component.part_id,

        part_name:
          component.part_name,

        required_quantity:
          component
            .recommended_procurement_quantity,

        production_shortage:
          component
            .production_shortage,

        urgency:
          component.urgency

      };


      sessionStorage.setItem(

        "inventoryProcurementRequest",

        JSON.stringify(
          request
        )

      );


      if (onProcure) {

        onProcure(
          request
        );

      }

    };


  // ==========================================================
  // GENERAL SUMMARY
  // ==========================================================

  const totalRecords =
    inventory.length;


  const totalAvailableStock =
    inventory.reduce(

      (
        total,
        item
      ) =>

        total +
        Number(
          item.available_stock
          || 0
        ),

      0

    );


  const attentionRecords =
    inventory.filter(

      item =>

        item.inventory_status
        !== "NORMAL"

    ).length;


  // ==========================================================
  // WAREHOUSES
  // ==========================================================

  const warehouses = [

    ...new Set(

      inventory

        .map(
          item =>
            item.warehouse
        )

        .filter(Boolean)

    )

  ];


  // ==========================================================
  // DIALOG
  // ==========================================================

  const openDialog =
    type => {

      setDialogType(
        type
      );


      setFormData({

        component_id: "",

        warehouse: "",

        quantity: "",

        reference_id: "",

        source_warehouse: "",

        destination_warehouse: ""

      });


      setDialogOpen(true);

    };


  const closeDialog =
    () => {

      if (!submitting) {

        setDialogOpen(false);

      }

    };


  const handleChange =
    event => {

      const {
        name,
        value
      } = event.target;


      setFormData(
        previous => ({

          ...previous,

          [name]:
            value

        })
      );

    };


  // ==========================================================
  // STOCK OPERATION
  // ==========================================================

  const handleSubmit =
    async () => {

      try {

        setError("");


        const componentId =
          Number(
            formData.component_id
          );


        const quantity =
          Number(
            formData.quantity
          );


        if (!componentId) {

          setError(
            "Component ID is required."
          );

          return;

        }


        if (
          Number.isNaN(quantity)
        ) {

          setError(
            "Valid quantity is required."
          );

          return;

        }


        if (
          dialogType ===
          "ADJUSTMENT"
        ) {

          if (quantity === 0) {

            setError(
              "Adjustment quantity cannot be zero."
            );

            return;

          }

        }

        else if (
          quantity <= 0
        ) {

          setError(
            "Quantity must be greater than zero."
          );

          return;

        }


        setSubmitting(true);


        if (
          dialogType ===
          "RECEIPT"
        ) {

          if (
            !formData.warehouse
          ) {

            throw new Error(
              "Warehouse is required."
            );

          }


          await receiveStock(

            componentId,

            formData.warehouse,

            quantity,

            formData.reference_id
            || null

          );

        }


        else if (
          dialogType ===
          "ISSUE"
        ) {

          if (
            !formData.warehouse
          ) {

            throw new Error(
              "Warehouse is required."
            );

          }


          await issueStock(

            componentId,

            formData.warehouse,

            quantity,

            formData.reference_id
            || null

          );

        }


        else if (
          dialogType ===
          "ADJUSTMENT"
        ) {

          if (
            !formData.warehouse
          ) {

            throw new Error(
              "Warehouse is required."
            );

          }


          await adjustStock(

            componentId,

            formData.warehouse,

            quantity,

            formData.reference_id
            || null

          );

        }


        else if (
          dialogType ===
          "TRANSFER"
        ) {

          if (
            !formData
              .source_warehouse
          ) {

            throw new Error(
              "Source warehouse is required."
            );

          }


          if (
            !formData
              .destination_warehouse
          ) {

            throw new Error(
              "Destination warehouse is required."
            );

          }


          if (
            formData.source_warehouse
            ===
            formData.destination_warehouse
          ) {

            throw new Error(
              "Source and destination warehouses must be different."
            );

          }


          await transferStock(

            componentId,

            formData
              .source_warehouse,

            formData
              .destination_warehouse,

            quantity,

            formData.reference_id
            || null

          );

        }


        setDialogOpen(false);


        setSuccessMessage(
          `${dialogType} completed successfully.`
        );


        await loadInventory();

        await loadTransactions();


        if (selectedVehicle) {

          await loadVehicleInventory(
            selectedVehicle
          );

        }


        if (
          requirementAnalysis
        ) {

          await handleAnalyze();

        }

      }

      catch (err) {

        setError(

          err?.message ||
          "Inventory operation failed."

        );

      }

      finally {

        setSubmitting(false);

      }

    };


  return (

    <Box sx={{ p: 3 }}>

      {/* =====================================================
          HEADER
      ===================================================== */}

      <Box
        sx={{
          display: "flex",

          justifyContent:
            "space-between",

          alignItems: {
            xs: "flex-start",
            md: "center"
          },

          flexDirection: {
            xs: "column",
            md: "row"
          },

          gap: 2,

          mb: 3
        }}
      >

        <Box>

          <Typography
            variant="h5"
            fontWeight={700}
          >
            Vehicle Inventory Intelligence
          </Typography>


          <Typography
            color="text.secondary"
            sx={{ mt: 0.5 }}
          >
            Analyze vehicle BOM demand, inventory shortage, lead time and procurement urgency
          </Typography>

        </Box>


        <Stack
          direction={{
            xs: "column",
            sm: "row"
          }}
          spacing={1}
        >

          <Button
            variant="contained"
            startIcon={
              <AddBoxIcon />
            }
            onClick={() =>
              openDialog(
                "RECEIPT"
              )
            }
          >
            Receive
          </Button>


          <Button
            variant="outlined"
            startIcon={
              <RemoveCircleIcon />
            }
            onClick={() =>
              openDialog(
                "ISSUE"
              )
            }
          >
            Issue
          </Button>


          <Button
            variant="outlined"
            startIcon={
              <TuneIcon />
            }
            onClick={() =>
              openDialog(
                "ADJUSTMENT"
              )
            }
          >
            Adjust
          </Button>


          <Button
            variant="outlined"
            startIcon={
              <SwapHorizIcon />
            }
            onClick={() =>
              openDialog(
                "TRANSFER"
              )
            }
          >
            Transfer
          </Button>

        </Stack>

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


      {/* =====================================================
          VEHICLE
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
          >
            1. Select Vehicle
          </Typography>


          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mt: 0.5,
              mb: 2
            }}
          >
            The selected vehicle determines which BOM components are required.
          </Typography>


          {vehicleLoading ? (

            <CircularProgress
              size={30}
            />

          ) : (

            <Stack
              direction="row"
              spacing={1}
              useFlexGap
              flexWrap="wrap"
            >

              {vehicles.map(
                vehicle => (

                  <Button
                    key={
                      vehicle.id
                    }

                    variant={
                      selectedVehicle?.id
                      === vehicle.id
                        ? "contained"
                        : "outlined"
                    }

                    onClick={() =>
                      handleVehicleSelect(
                        vehicle
                      )
                    }

                    sx={{
                      textTransform:
                        "none"
                    }}
                  >

                    {
                      vehicle.vehicle_type
                    }

                  </Button>

                )
              )}

            </Stack>

          )}


          {selectedVehicle && (

            <Alert
              severity="info"
              sx={{ mt: 2 }}
            >
              Selected:{" "}
              <strong>
                {
                  selectedVehicle
                    .vehicle_type
                }
              </strong>
              {" "}(
              {
                selectedVehicle
                  .vehicle_code
              }
              )
            </Alert>

          )}

        </CardContent>

      </Card>


      {/* =====================================================
          PRODUCTION PLAN
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
          >
            2. Production Requirement
          </Typography>


          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mt: 0.5,
              mb: 2
            }}
          >
            Enter how many vehicles are planned and when the components are required.
          </Typography>


          <Grid
            container
            spacing={2}
            alignItems="center"
          >

            <Grid
              size={{
                xs: 12,
                md: 4
              }}
            >

              <TextField
                label="Planned Vehicles"
                type="number"
                fullWidth
                value={
                  plannedQuantity
                }
                onChange={
                  event =>
                    setPlannedQuantity(
                      event.target.value
                    )
                }
                inputProps={{
                  min: 1
                }}
              />

            </Grid>


            <Grid
              size={{
                xs: 12,
                md: 4
              }}
            >

              <TextField
                label="Required Date"
                type="date"
                fullWidth
                value={
                  requiredDate
                }
                onChange={
                  event =>
                    setRequiredDate(
                      event.target.value
                    )
                }
                InputLabelProps={{
                  shrink: true
                }}
              />

            </Grid>


            <Grid
              size={{
                xs: 12,
                md: 4
              }}
            >

              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={
                  <AssessmentIcon />
                }
                disabled={
                  analysisLoading
                }
                onClick={
                  handleAnalyze
                }
                sx={{
                  py: 1.7
                }}
              >

                {analysisLoading
                  ? (
                    <CircularProgress
                      size={22}
                      color="inherit"
                    />
                  )
                  : "Analyze Requirements"
                }

              </Button>

            </Grid>

          </Grid>

        </CardContent>

      </Card>


      {/* =====================================================
          ANALYSIS SUMMARY
      ===================================================== */}

      {requirementAnalysis && (

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

            <SummaryCard
              title="BOM Components"
              value={
                requirementAnalysis
                  .component_count
              }
              subtitle="Required components"
              icon={
                <InventoryIcon />
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

            <SummaryCard
              title="Stock Sufficient"
              value={
                requirementAnalysis
                  .sufficient_components
              }
              subtitle="Production requirement covered"
              icon={
                <CheckCircleIcon />
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

            <SummaryCard
              title="Need Procurement"
              value={
                requirementAnalysis
                  .procurement_components
              }
              subtitle="Including safety stock"
              icon={
                <ShoppingCartIcon />
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

            <SummaryCard
              title="Urgent"
              value={
                requirementAnalysis
                  .urgent_components
              }
              subtitle="Immediate action required"
              icon={
                <WarningAmberIcon />
              }
            />

          </Grid>

        </Grid>

      )}


      {/* =====================================================
          DECISION TABLE
      ===================================================== */}

      {requirementAnalysis && (

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
              3. Component Requirement & Procurement Decision
            </Typography>


            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                mt: 0.5,
                mb: 2
              }}
            >
              Urgent and high-priority components are shown first.
            </Typography>


            <TableContainer>

              <Table>

                <TableHead>

                  <TableRow>

                    <TableCell>
                      <strong>
                        Component
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Criticality
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Qty / Vehicle
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Required
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Available
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Incoming
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Production Gap
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Procure Qty
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Lead Time
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Urgency
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

                  {requirementAnalysis
                    .components
                    .map(
                      component => (

                        <TableRow
                          key={
                            component
                              .component_id
                          }
                          hover
                        >

                          <TableCell>

                            <Typography
                              fontWeight={600}
                              variant="body2"
                            >
                              {
                                component
                                  .part_name
                              }
                            </Typography>


                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {
                                component
                                  .part_id
                              }
                              {" • "}
                              {
                                component
                                  .category
                              }
                            </Typography>

                          </TableCell>


                          <TableCell>

                            <CriticalityChip
                              criticality={
                                component
                                  .criticality
                              }
                            />

                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              component
                                .quantity_per_vehicle
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                component
                                  .required_quantity
                              )
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                component
                                  .available_stock
                              )
                            }
                          </TableCell>


                          <TableCell
                            align="right"
                          >

                            <Typography
                              variant="body2"
                            >
                              {
                                formatNumber(
                                  component
                                    .incoming_quantity
                                )
                              }
                            </Typography>


                            {component
                              .incoming_expected_date && (

                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                ETA{" "}
                                {
                                  formatDate(
                                    component
                                      .incoming_expected_date
                                  )
                                }
                              </Typography>

                            )}

                          </TableCell>


                          <TableCell
                            align="right"
                          >

                            <Typography
                              fontWeight={
                                component
                                  .production_shortage
                                  > 0
                                  ? 700
                                  : 400
                              }
                              color={
                                component
                                  .production_shortage
                                  > 0
                                  ? "error"
                                  : "inherit"
                              }
                            >
                              {
                                formatNumber(
                                  component
                                    .production_shortage
                                )
                              }
                            </Typography>

                          </TableCell>


                          <TableCell
                            align="right"
                          >

                            <Typography
                              fontWeight={
                                component
                                  .procurement_required
                                  ? 700
                                  : 400
                              }
                            >
                              {
                                formatNumber(
                                  component
                                    .recommended_procurement_quantity
                                )
                              }
                            </Typography>

                          </TableCell>


                          <TableCell>

                            {component
                              .best_supplier_lead_time_days
                              !== null
                              ? (

                                <>

                                  <Typography
                                    variant="body2"
                                  >
                                    {
                                      component
                                        .best_supplier_lead_time_days
                                    }{" "}
                                    days
                                  </Typography>


                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    Est.{" "}
                                    {
                                      formatDate(
                                        component
                                          .estimated_arrival_date
                                      )
                                    }
                                  </Typography>

                                </>

                              )
                              : (

                                <Typography
                                  color="error"
                                  variant="body2"
                                >
                                  No supplier
                                </Typography>

                              )
                            }

                          </TableCell>


                          <TableCell>

                            <Tooltip
                              title={
                                component
                                  .urgency_reason
                              }
                              arrow
                            >

                              <Box
                                sx={{
                                  display:
                                    "inline-flex"
                                }}
                              >

                                <UrgencyChip
                                  urgency={
                                    component
                                      .urgency
                                  }
                                />

                              </Box>

                            </Tooltip>


                            {component
                              .lead_time_buffer_days
                              !== null && (

                              <Typography
                                variant="caption"
                                display="block"
                                color="text.secondary"
                                sx={{
                                  mt: 0.5
                                }}
                              >
                                Buffer:{" "}
                                {
                                  component
                                    .lead_time_buffer_days
                                }{" "}
                                days
                              </Typography>

                            )}

                          </TableCell>


                          <TableCell>

                            {component
                              .procurement_required
                              ? (

                                <Button
                                  variant="contained"
                                  size="small"
                                  startIcon={
                                    <ShoppingCartIcon />
                                  }
                                  color={
                                    component
                                      .urgency ===
                                      "URGENT"
                                      ? "error"
                                      : "primary"
                                  }
                                  onClick={() =>
                                    handleProcure(
                                      component
                                    )
                                  }
                                >
                                  Procure
                                </Button>

                              )
                              : (

                                <Chip
                                  label="Stock OK"
                                  color="success"
                                  size="small"
                                  variant="outlined"
                                />

                              )
                            }

                          </TableCell>

                        </TableRow>

                      )
                    )}

                </TableBody>

              </Table>

            </TableContainer>

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          BOM CURRENT VIEW
      ===================================================== */}

      {!requirementAnalysis && (

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
              Vehicle BOM & Current Inventory
            </Typography>


            {vehicleInventoryLoading ? (

              <Box
                sx={{
                  textAlign:
                    "center",

                  py: 4
                }}
              >
                <CircularProgress />
              </Box>

            ) : vehicleInventory ? (

              <TableContainer>

                <Table>

                  <TableHead>

                    <TableRow>

                      <TableCell>
                        <strong>
                          Component
                        </strong>
                      </TableCell>

                      <TableCell>
                        <strong>
                          Criticality
                        </strong>
                      </TableCell>

                      <TableCell
                        align="right"
                      >
                        <strong>
                          Qty / Vehicle
                        </strong>
                      </TableCell>

                      <TableCell
                        align="right"
                      >
                        <strong>
                          Available
                        </strong>
                      </TableCell>

                      <TableCell
                        align="right"
                      >
                        <strong>
                          Safety
                        </strong>
                      </TableCell>

                      <TableCell>
                        <strong>
                          Status
                        </strong>
                      </TableCell>

                    </TableRow>

                  </TableHead>


                  <TableBody>

                    {vehicleInventory
                      .components
                      .map(
                        component => (

                          <TableRow
                            key={
                              component
                                .component_id
                            }
                          >

                            <TableCell>

                              <Typography
                                variant="body2"
                                fontWeight={600}
                              >
                                {
                                  component
                                    .part_name
                                }
                              </Typography>


                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                {
                                  component
                                    .part_id
                                }
                              </Typography>

                            </TableCell>


                            <TableCell>

                              <CriticalityChip
                                criticality={
                                  component
                                    .criticality
                                }
                              />

                            </TableCell>


                            <TableCell
                              align="right"
                            >
                              {
                                component
                                  .quantity_per_vehicle
                              }
                            </TableCell>


                            <TableCell
                              align="right"
                            >
                              {
                                formatNumber(
                                  component
                                    .available_stock
                                )
                              }
                            </TableCell>


                            <TableCell
                              align="right"
                            >
                              {
                                formatNumber(
                                  component
                                    .safety_stock
                                )
                              }
                            </TableCell>


                            <TableCell>

                              <StatusChip
                                status={
                                  component
                                    .inventory_status
                                }
                              />

                            </TableCell>

                          </TableRow>

                        )
                      )}

                  </TableBody>

                </Table>

              </TableContainer>

            ) : (

              <Alert severity="info">
                Select a vehicle.
              </Alert>

            )}

          </CardContent>

        </Card>

      )}


      {/* =====================================================
          INVENTORY SUMMARY
      ===================================================== */}

      <Grid
        container
        spacing={2}
        sx={{ mb: 3 }}
      >

        <Grid
          size={{
            xs: 12,
            md: 4
          }}
        >

          <SummaryCard
            title="Inventory Records"
            value={
              totalRecords
            }
            subtitle="Warehouse records"
            icon={
              <InventoryIcon />
            }
          />

        </Grid>


        <Grid
          size={{
            xs: 12,
            md: 4
          }}
        >

          <SummaryCard
            title="Available Stock"
            value={
              totalAvailableStock
                .toLocaleString()
            }
            subtitle="Across all components"
            icon={
              <CheckCircleIcon />
            }
          />

        </Grid>


        <Grid
          size={{
            xs: 12,
            md: 4
          }}
        >

          <SummaryCard
            title="Attention Required"
            value={
              attentionRecords
            }
            subtitle="Warehouse stock alerts"
            icon={
              <WarningAmberIcon />
            }
          />

        </Grid>

      </Grid>


      {/* =====================================================
          TRANSACTIONS
      ===================================================== */}

      <Card
        elevation={0}
        sx={{
          border:
            "1px solid #e5e7eb",

          borderRadius: 3
        }}
      >

        <CardContent>

          <Stack
            direction="row"
            spacing={1}
            sx={{ mb: 2 }}
          >

            <HistoryIcon />


            <Box>

              <Typography
                variant="h6"
                fontWeight={600}
              >
                Recent Inventory Transactions
              </Typography>


              <Typography
                variant="body2"
                color="text.secondary"
              >
                Latest receipt, issue, transfer and adjustment operations
              </Typography>

            </Box>

          </Stack>


          {transactionLoading ? (

            <CircularProgress />

          ) : (

            <TableContainer>

              <Table>

                <TableHead>

                  <TableRow>

                    <TableCell>
                      <strong>
                        Transaction
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Component
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Warehouse
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Type
                      </strong>
                    </TableCell>

                    <TableCell
                      align="right"
                    >
                      <strong>
                        Quantity
                      </strong>
                    </TableCell>

                    <TableCell>
                      <strong>
                        Date
                      </strong>
                    </TableCell>

                  </TableRow>

                </TableHead>


                <TableBody>

                  {transactions
                    .slice(
                      0,
                      15
                    )
                    .map(
                      transaction => (

                        <TableRow
                          key={
                            transaction
                              .transaction_id
                          }
                        >

                          <TableCell>
                            {
                              transaction
                                .transaction_id
                            }
                          </TableCell>


                          <TableCell>
                            #
                            {
                              transaction
                                .component_id
                            }
                          </TableCell>


                          <TableCell>
                            {
                              transaction
                                .warehouse
                            }
                          </TableCell>


                          <TableCell>

                            <Chip
                              label={
                                transaction
                                  .transaction_type
                              }
                              size="small"
                              variant="outlined"
                            />

                          </TableCell>


                          <TableCell
                            align="right"
                          >
                            {
                              formatNumber(
                                transaction
                                  .quantity
                              )
                            }
                          </TableCell>


                          <TableCell>

                            {transaction
                              .transaction_date

                              ? new Date(
                                  transaction
                                    .transaction_date
                                )
                                  .toLocaleString()

                              : "-"
                            }

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


      {/* =====================================================
          STOCK DIALOG
      ===================================================== */}

      <Dialog
        open={
          dialogOpen
        }
        onClose={
          closeDialog
        }
        fullWidth
        maxWidth="sm"
      >

        <DialogTitle>

          {dialogType === "RECEIPT" &&
            "Receive Stock"}

          {dialogType === "ISSUE" &&
            "Issue Stock"}

          {dialogType === "ADJUSTMENT" &&
            "Adjust Stock"}

          {dialogType === "TRANSFER" &&
            "Transfer Stock"}

        </DialogTitle>


        <DialogContent>

          <Stack
            spacing={2}
            sx={{ mt: 1 }}
          >

            <TextField
              label="Component ID"
              name="component_id"
              type="number"
              fullWidth
              value={
                formData.component_id
              }
              onChange={
                handleChange
              }
            />


            {dialogType ===
            "TRANSFER" ? (

              <>

                <FormControl
                  fullWidth
                >

                  <InputLabel>
                    Source Warehouse
                  </InputLabel>


                  <Select
                    label="Source Warehouse"
                    name="source_warehouse"
                    value={
                      formData
                        .source_warehouse
                    }
                    onChange={
                      handleChange
                    }
                  >

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


                <FormControl
                  fullWidth
                >

                  <InputLabel>
                    Destination Warehouse
                  </InputLabel>


                  <Select
                    label="Destination Warehouse"
                    name="destination_warehouse"
                    value={
                      formData
                        .destination_warehouse
                    }
                    onChange={
                      handleChange
                    }
                  >

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

              </>

            ) : (

              <FormControl
                fullWidth
              >

                <InputLabel>
                  Warehouse
                </InputLabel>


                <Select
                  label="Warehouse"
                  name="warehouse"
                  value={
                    formData.warehouse
                  }
                  onChange={
                    handleChange
                  }
                >

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

            )}


            <TextField
              label={
                dialogType ===
                "ADJUSTMENT"

                ? "Adjustment Quantity"

                : "Quantity"
              }
              name="quantity"
              type="number"
              fullWidth
              value={
                formData.quantity
              }
              onChange={
                handleChange
              }
              helperText={
                dialogType ===
                  "ADJUSTMENT"
                  ? "Positive increases stock; negative decreases stock."
                  : ""
              }
            />


            <TextField
              label="Reference ID"
              name="reference_id"
              fullWidth
              value={
                formData.reference_id
              }
              onChange={
                handleChange
              }
            />

          </Stack>

        </DialogContent>


        <DialogActions>

          <Button
            onClick={
              closeDialog
            }
          >
            Cancel
          </Button>


          <Button
            variant="contained"
            onClick={
              handleSubmit
            }
            disabled={
              submitting
            }
          >

            {submitting
              ? (
                <CircularProgress
                  size={22}
                  color="inherit"
                />
              )
              : "Confirm"
            }

          </Button>

        </DialogActions>

      </Dialog>


      <Snackbar
        open={
          Boolean(
            successMessage
          )
        }
        autoHideDuration={
          3000
        }
        message={
          successMessage
        }
        onClose={() =>
          setSuccessMessage("")
        }
      />

    </Box>

  );

}


export default Inventory;