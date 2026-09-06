import {
  useEffect,
  useState
} from "react";

import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography
} from "@mui/material";

import InventoryIcon from "@mui/icons-material/Inventory";
import PeopleIcon from "@mui/icons-material/People";
import WarningIcon from "@mui/icons-material/Warning";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";

import {
  getInventory,
  getSuppliers,
  getAllSupplierMetrics
} from "../services/api";


// ============================================================
// DASHBOARD CARD
// ============================================================

function DashboardCard({
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
              variant="body2"
              color="text.secondary"
            >
              {title}
            </Typography>


            <Typography
              variant="h4"
              fontWeight={700}
              sx={{ mt: 1 }}
            >
              {value}
            </Typography>


            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 0.5 }}
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
              alignItems: "center",
              justifyContent: "center",
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
// DASHBOARD
// ============================================================

function Dashboard() {

  const [inventory, setInventory] =
    useState([]);

  const [suppliers, setSuppliers] =
    useState([]);

  const [supplierMetrics, setSupplierMetrics] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


// ============================================================
// LOAD DASHBOARD DATA
// ============================================================

  const loadDashboardData = async () => {

    try {

      setLoading(true);

      setError("");


      // ------------------------------------------------------
      // LOAD INVENTORY
      // ------------------------------------------------------

      let inventoryData = [];

      try {

        const data =
          await getInventory();

        inventoryData =
          Array.isArray(data)
            ? data
            : [];

      }

      catch (inventoryError) {

        console.error(
          "Failed to load dashboard inventory:",
          inventoryError
        );

      }


      // ------------------------------------------------------
      // LOAD SUPPLIERS
      // ------------------------------------------------------

      let suppliersData = [];

      try {

        const data =
          await getSuppliers();

        suppliersData =
          Array.isArray(data)
            ? data
            : [];

      }

      catch (supplierError) {

        console.error(
          "Failed to load dashboard suppliers:",
          supplierError
        );

      }


      // ------------------------------------------------------
      // LOAD SUPPLIER METRICS
      // ------------------------------------------------------

      let metricsData = [];

      try {

        const data =
          await getAllSupplierMetrics();

        metricsData =
          Array.isArray(data)
            ? data
            : [];

      }

      catch (metricsError) {

        console.error(
          "Failed to load supplier metrics:",
          metricsError
        );

      }


      setInventory(
        inventoryData
      );

      setSuppliers(
        suppliersData
      );

      setSupplierMetrics(
        metricsData
      );


      // ------------------------------------------------------
      // CHECK WHETHER EVERYTHING FAILED
      // ------------------------------------------------------

      if (
        inventoryData.length === 0 &&
        suppliersData.length === 0 &&
        metricsData.length === 0
      ) {

        setError(
          "Unable to load dashboard data. Please make sure the FastAPI backend is running."
        );

      }

    }

    catch (err) {

      console.error(
        "Dashboard loading failed:",
        err
      );

      setError(
        err?.message ||
        "Failed to load dashboard data."
      );

    }

    finally {

      setLoading(false);

    }

  };


// ============================================================
// INITIAL LOAD
// ============================================================

  useEffect(() => {

    loadDashboardData();

  }, []);


// ============================================================
// COMPONENT COUNT
// ============================================================
//
// Inventory records are used as the currently available
// component/inventory records because there is no separate
// component endpoint in the current api.js.
// ============================================================

  const componentCount =
    inventory.length;


// ============================================================
// SUPPLIER COUNT
// ============================================================

  const supplierCount =
    suppliers.length;


// ============================================================
// HIGH-RISK SUPPLIER COUNT
// ============================================================
//
// Supports several possible field names so the dashboard
// remains compatible with the supplier metrics response.
// ============================================================

  const highRiskSuppliers =
    supplierMetrics.filter(
      metric => {

        const risk =
          String(
            metric.risk_level ||
            metric.risk_status ||
            metric.supplier_risk ||
            metric.risk_category ||
            ""
          ).toUpperCase();


        return (
          risk === "HIGH" ||
          risk === "CRITICAL" ||
          risk === "HIGH_RISK" ||
          risk === "CRITICAL_RISK"
        );

      }
    ).length;


// ============================================================
// LOADING SCREEN
// ============================================================

  if (loading) {

    return (

      <Box
        sx={{
          p: 3
        }}
      >

        <Typography
          variant="h5"
          fontWeight={700}
        >
          Dashboard
        </Typography>


        <Typography
          color="text.secondary"
          sx={{
            mt: 0.5,
            mb: 3
          }}
        >
          Overview of your EV supply chain
        </Typography>


        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: 300
          }}
        >

          <CircularProgress />

        </Box>

      </Box>

    );

  }


// ============================================================
// RENDER
// ============================================================

  return (

    <Box sx={{ p: 3 }}>

      {/* =====================================================
          HEADER
      ===================================================== */}

      <Typography
        variant="h5"
        fontWeight={700}
      >
        Dashboard
      </Typography>


      <Typography
        color="text.secondary"
        sx={{
          mt: 0.5,
          mb: 3
        }}
      >
        Overview of your EV supply chain
      </Typography>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <Alert
          severity="warning"
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
          SUMMARY CARDS
      ===================================================== */}

      <Grid
        container
        spacing={2}
      >

        {/* ===================================================
            COMPONENTS
        =================================================== */}

        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}
        >

          <DashboardCard
            title="Components"
            value={
              componentCount
            }
            subtitle="Active inventory records"
            icon={
              <InventoryIcon />
            }
          />

        </Grid>


        {/* ===================================================
            SUPPLIERS
        =================================================== */}

        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}
        >

          <DashboardCard
            title="Suppliers"
            value={
              supplierCount
            }
            subtitle="Active suppliers"
            icon={
              <PeopleIcon />
            }
          />

        </Grid>


        {/* ===================================================
            HIGH RISK
        =================================================== */}

        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}
        >

          <DashboardCard
            title="High Risk"
            value={
              highRiskSuppliers
            }
            subtitle="Suppliers requiring attention"
            icon={
              <WarningIcon />
            }
          />

        </Grid>


        {/* ===================================================
            PROCUREMENT
        =================================================== */}

        <Grid
          size={{
            xs: 12,
            sm: 6,
            md: 3
          }}
        >

          <DashboardCard
            title="Procurement"
            value="--"
            subtitle="Active requirements"
            icon={
              <ShoppingCartIcon />
            }
          />

        </Grid>

      </Grid>


      {/* =====================================================
          INTELLIGENT SUPPLY CHAIN
      ===================================================== */}

      <Card
        elevation={0}
        sx={{
          mt: 3,
          border:
            "1px solid #e5e7eb",
          borderRadius: 3
        }}
      >

        <CardContent>

          <Typography
            variant="h6"
            fontWeight={600}
          >
            Intelligent Supply Chain
          </Typography>


          <Typography
            color="text.secondary"
            sx={{
              mt: 1
            }}
          >
            Real-time inventory and supplier
            information is now connected to the
            dashboard. Supplier risk information
            is also being loaded from the backend.
          </Typography>

        </CardContent>

      </Card>

    </Box>

  );

}


export default Dashboard;