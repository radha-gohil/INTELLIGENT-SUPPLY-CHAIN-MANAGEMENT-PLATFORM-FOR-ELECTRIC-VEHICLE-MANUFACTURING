import { useState } from "react";

import {
  Alert,
  Box,
  CircularProgress,
  CssBaseline,
  ThemeProvider,
  createTheme
} from "@mui/material";

import DashboardIcon from "@mui/icons-material/Dashboard";
import InventoryIcon from "@mui/icons-material/Inventory";
import PeopleIcon from "@mui/icons-material/People";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";

import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";

import Dashboard from "./pages/Dashboard";
import Procurement from "./pages/Procurement";
import Suppliers from "./pages/Suppliers";
import Inventory from "./pages/Inventory";
import Orders from "./pages/Orders";
import GraphRAG from "./pages/GraphRAG";
import Login from "./pages/Login";

import {
  useAuth
} from "./context/AuthContext";


// ============================================================
// THEME
// ============================================================

const theme = createTheme({

  palette: {

    mode: "light",

    primary: {
      main: "#1976d2"
    },

    background: {
      default: "#f5f7fb"
    }

  },

  typography: {

    fontFamily:
      "Inter, Roboto, Arial, sans-serif"

  }

});


// ============================================================
// APP
// ============================================================

function App() {

  // ==========================================================
  // AUTHENTICATION
  // ==========================================================

  const {
    user,
    loading
  } = useAuth();


  // ==========================================================
  // ACTIVE PAGE
  // ==========================================================

  const [
    activePage,
    setActivePage
  ] = useState(
    "dashboard"
  );


  // ==========================================================
  // INVENTORY -> PROCUREMENT CONTEXT
  // ==========================================================

  const [
    procurementContext,
    setProcurementContext
  ] = useState(
    null
  );


  // ==========================================================
  // LOADING AUTHENTICATION
  // ==========================================================

  if (loading) {

    return (

      <ThemeProvider
        theme={theme}
      >

        <CssBaseline />


        <Box
          sx={{
            minHeight: "100vh",

            display: "flex",

            flexDirection: "column",

            alignItems: "center",

            justifyContent: "center",

            gap: 2,

            backgroundColor:
              "background.default"
          }}
        >

          <CircularProgress />


          <Box
            sx={{
              color: "text.secondary",
              fontSize: 14
            }}
          >
            Loading EV Supply Chain...
          </Box>

        </Box>

      </ThemeProvider>

    );

  }


  // ==========================================================
  // NOT LOGGED IN
  // ==========================================================

  if (!user) {

    return (

      <ThemeProvider
        theme={theme}
      >

        <CssBaseline />

        <Login />

      </ThemeProvider>

    );

  }


  // ==========================================================
  // SIDEBAR MENU
  // ==========================================================

  const menuItems = [

    {
      id: "dashboard",
      label: "Dashboard",
      icon: <DashboardIcon />
    },

    {
      id: "inventory",
      label: "Inventory",
      icon: <InventoryIcon />
    },

    {
      id: "orders",
      label: "Orders",
      icon: <LocalShippingIcon />
    },

    {
      id: "suppliers",
      label: "Suppliers",
      icon: <PeopleIcon />
    },

    {
      id: "procurement",
      label: "Procurement",
      icon: <ShoppingCartIcon />
    },

    {
      id: "graph-rag",
      label: "AI Assistant",
      icon: <AutoAwesomeIcon />
    }

  ];


  // ==========================================================
  // INVENTORY -> PROCUREMENT
  // ==========================================================

  const handleProcureFromInventory = request => {

    setProcurementContext(
      request
    );


    sessionStorage.setItem(

      "inventoryProcurementRequest",

      JSON.stringify(
        request
      )

    );


    setActivePage(
      "procurement"
    );

  };


  // ==========================================================
  // CLEAR PROCUREMENT CONTEXT
  // ==========================================================

  const clearProcurementContext = () => {

    setProcurementContext(
      null
    );


    sessionStorage.removeItem(
      "inventoryProcurementRequest"
    );

  };


  // ==========================================================
  // PROCUREMENT -> ORDERS
  // ==========================================================

  const handleViewOrders = () => {

    clearProcurementContext();


    setActivePage(
      "orders"
    );

  };


  // ==========================================================
  // RENDER PAGE
  // ==========================================================

  const renderPage = () => {

    switch (
      activePage
    ) {

      // ====================================================
      // DASHBOARD
      // ====================================================

      case "dashboard":

        return (
          <Dashboard />
        );


      // ====================================================
      // INVENTORY
      // ====================================================

      case "inventory":

        return (

          <Inventory
            onProcure={
              handleProcureFromInventory
            }
          />

        );


      // ====================================================
      // ORDERS
      // ====================================================

      case "orders":

        return (
          <Orders />
        );


      // ====================================================
      // SUPPLIERS
      // ====================================================

      case "suppliers":

        return (
          <Suppliers />
        );


      // ====================================================
      // PROCUREMENT
      // ====================================================

      case "procurement":

        return (

          <Box>

            {/* =============================================
                INVENTORY PROCUREMENT BANNER
            ============================================= */}

            {procurementContext && (

              <Box
                sx={{
                  px: 3,
                  pt: 3
                }}
              >

                <Alert
                  severity={

                    procurementContext
                      .urgency ===
                      "URGENT"

                      ? "error"

                      : procurementContext
                          .urgency ===
                          "HIGH"

                        ? "warning"

                        : "info"

                  }

                  onClose={
                    clearProcurementContext
                  }
                >

                  Inventory procurement request:{" "}


                  <strong>
                    {
                      procurementContext
                        .vehicle_type
                    }
                  </strong>


                  {" → "}


                  <strong>
                    {
                      procurementContext
                        .part_name
                    }
                  </strong>


                  {" | Recommended quantity: "}


                  <strong>
                    {
                      Number(
                        procurementContext
                          .required_quantity
                        || 0
                      )
                        .toLocaleString()
                    }
                  </strong>


                  {" | Urgency: "}


                  <strong>
                    {
                      procurementContext
                        .urgency
                    }
                  </strong>

                </Alert>

              </Box>

            )}


            {/* =============================================
                PROCUREMENT PAGE
            ============================================= */}

            <Procurement

              initialRequest={
                procurementContext
              }

              onViewOrders={
                handleViewOrders
              }

            />

          </Box>

        );


      // ====================================================
      // GRAPH-RAG AI ASSISTANT
      // ====================================================

      case "graph-rag":

        return (
          <GraphRAG />
        );


      // ====================================================
      // DEFAULT
      // ====================================================

      default:

        return (
          <Dashboard />
        );

    }

  };


  // ==========================================================
  // APPLICATION
  // ==========================================================

  return (

    <ThemeProvider
      theme={theme}
    >

      <CssBaseline />


      <Box
        sx={{
          display: "flex",
          minHeight: "100vh"
        }}
      >

        {/* ===================================================
            SIDEBAR
        =================================================== */}

        <Sidebar

          menuItems={
            menuItems
          }

          activePage={
            activePage
          }

          setActivePage={
            setActivePage
          }

        />


        {/* ===================================================
            PAGE CONTENT
        =================================================== */}

        <Box
          sx={{
            flexGrow: 1,
            minWidth: 0,

            backgroundColor:
              "background.default"
          }}
        >

          <TopBar />


          {
            renderPage()
          }

        </Box>

      </Box>

    </ThemeProvider>

  );

}


export default App;