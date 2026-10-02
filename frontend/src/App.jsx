import { useState } from "react";

import {
  Alert,
  Box,
  CircularProgress,
  CssBaseline,
  ThemeProvider,
  createTheme
} from "@mui/material";

// ============================================================
// ICONS
// ============================================================

import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";

import Inventory2RoundedIcon from "@mui/icons-material/Inventory2Rounded";

import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";

import ShoppingCartRoundedIcon from "@mui/icons-material/ShoppingCartRounded";

import LocalShippingRoundedIcon from "@mui/icons-material/LocalShippingRounded";

import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";

import DirectionsCarFilledRoundedIcon from "@mui/icons-material/DirectionsCarFilledRounded";

// ============================================================
// LAYOUT COMPONENTS
// ============================================================

import Sidebar from "./components/Sidebar";

import TopBar from "./components/TopBar";

// ============================================================
// APPLICATION PAGES
// ============================================================

import Dashboard from "./pages/Dashboard";

import Inventory from "./pages/Inventory";

import Suppliers from "./pages/Suppliers";

import Procurement from "./pages/Procurement";

import Orders from "./pages/Orders";

import GraphRAG from "./pages/GraphRAG";

import Login from "./pages/Login";

// ============================================================
// AUTHENTICATION
// ============================================================

import { useAuth } from "./context/AuthContext";

// ============================================================
// ENTERPRISE THEME
// ============================================================

const theme = createTheme({
  palette: {
    mode: "light",

    primary: {
      main: "#0865CA",
      dark: "#074E9C",
      light: "#E7F1FF",
      contrastText: "#FFFFFF"
    },

    secondary: {
      main: "#0D9488"
    },

    success: {
      main: "#16A34A"
    },

    warning: {
      main: "#F59E0B"
    },

    error: {
      main: "#DC2626"
    },

    info: {
      main: "#0284C7"
    },

    background: {
      default: "#F4F7FB",
      paper: "#FFFFFF"
    },

    text: {
      primary: "#14263D",
      secondary: "#64748B"
    },

    divider: "#E4EAF2"
  },

  typography: {
    fontFamily:
      '"Inter", "Roboto", "Arial", sans-serif',

    h4: {
      fontWeight: 800,
      letterSpacing: "-0.6px"
    },

    h5: {
      fontWeight: 800,
      letterSpacing: "-0.4px"
    },

    h6: {
      fontWeight: 700
    },

    subtitle1: {
      fontWeight: 700
    },

    button: {
      textTransform: "none",
      fontWeight: 700
    }
  },

  shape: {
    borderRadius: 12
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          margin: 0,
          backgroundColor: "#F4F7FB"
        },

        "#root": {
          minHeight: "100vh",
          width: "100%"
        },

        "*": {
          boxSizing: "border-box"
        },

        "*::-webkit-scrollbar": {
          width: "7px",
          height: "7px"
        },

        "*::-webkit-scrollbar-thumb": {
          backgroundColor: "#C5D1DF",
          borderRadius: "10px"
        },

        "*::-webkit-scrollbar-track": {
          backgroundColor: "transparent"
        }
      }
    },

    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 9,
          boxShadow: "none",
          padding: "9px 17px",
          fontWeight: 700
        },

        contained: {
          "&:hover": {
            boxShadow:
              "0 4px 14px rgba(8,101,202,0.18)"
          }
        }
      }
    },

    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 13,
          border: "1px solid #E4EAF2",
          boxShadow:
            "0 3px 14px rgba(15,23,42,0.035)",
          backgroundColor: "#FFFFFF"
        }
      }
    },

    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12
        }
      }
    },

    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: "#F6F9FD"
        }
      }
    },

    MuiTableCell: {
      styleOverrides: {
        head: {
          color: "#475569",
          fontWeight: 800,
          fontSize: "12px",
          whiteSpace: "nowrap"
        },

        body: {
          color: "#334155",
          fontSize: "13px"
        }
      }
    },

    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 700
        }
      }
    },

    MuiTextField: {
      defaultProps: {
        size: "small"
      }
    },

    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 10
        }
      }
    }
  }
});

// ============================================================
// SIDEBAR MENU CONFIGURATION
// ============================================================

const MENU_ITEMS = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: <DashboardRoundedIcon />
  },

  {
    id: "inventory",
    label: "Inventory",
    icon: <Inventory2RoundedIcon />
  },

  {
    id: "suppliers",
    label: "Suppliers",
    icon: <GroupsRoundedIcon />
  },

  {
    id: "procurement",
    label: "Procurement",
    icon: <ShoppingCartRoundedIcon />
  },

  {
    id: "orders",
    label: "Orders",
    icon: <LocalShippingRoundedIcon />
  },

  {
    id: "graph-rag",
    label: "AI Assistant",
    icon: <AutoAwesomeRoundedIcon />
  }
];

// ============================================================
// AUTHENTICATION LOADING SCREEN
// ============================================================

function AuthenticationLoading() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100%",

        display: "flex",
        flexDirection: "column",

        alignItems: "center",
        justifyContent: "center",

        gap: 2,

        backgroundColor: "#F4F7FB"
      }}
    >
      <Box
        sx={{
          width: 70,
          height: 70,

          borderRadius: "18px",

          display: "flex",
          alignItems: "center",
          justifyContent: "center",

          background:
            "linear-gradient(135deg, #0865CA, #06B6D4)",

          boxShadow:
            "0 12px 30px rgba(8,101,202,0.2)"
        }}
      >
        <DirectionsCarFilledRoundedIcon
          sx={{
            fontSize: 36,
            color: "#FFFFFF"
          }}
        />
      </Box>

      <Box
        sx={{
          fontSize: 23,
          fontWeight: 800,
          color: "#14263D"
        }}
      >
        EV Supply Chain
      </Box>

      <Box
        sx={{
          fontSize: 13,
          color: "#64748B"
        }}
      >
        Preparing your supply chain dashboard...
      </Box>

      <CircularProgress
        size={28}
        thickness={4}
        sx={{ mt: 1 }}
      />
    </Box>
  );
}

// ============================================================
// MAIN APPLICATION
// ============================================================

function App() {
  // ==========================================================
  // AUTHENTICATION
  // ==========================================================

  const { user, loading } = useAuth();

  // ==========================================================
  // ACTIVE PAGE
  // ==========================================================

  const [activePage, setActivePage] = useState(
    "dashboard"
  );

  // ==========================================================
  // COLLAPSIBLE SIDEBAR
  // ==========================================================

  const [
    sidebarCollapsed,
    setSidebarCollapsed
  ] = useState(false);

  // ==========================================================
  // INVENTORY -> PROCUREMENT CONTEXT
  // ==========================================================

  const [
    procurementContext,
    setProcurementContext
  ] = useState(null);

  // ==========================================================
  // SIDEBAR TOGGLE
  // ==========================================================

  const toggleSidebar = () => {
    setSidebarCollapsed(previous => !previous);
  };

  // ==========================================================
  // INVENTORY -> PROCUREMENT
  // ==========================================================

  const handleProcureFromInventory = request => {
    if (!request) {
      return;
    }

    setProcurementContext(request);

    sessionStorage.setItem(
      "inventoryProcurementRequest",
      JSON.stringify(request)
    );

    setActivePage("procurement");
  };

  // ==========================================================
  // CLEAR PROCUREMENT CONTEXT
  // ==========================================================

  const clearProcurementContext = () => {
    setProcurementContext(null);

    sessionStorage.removeItem(
      "inventoryProcurementRequest"
    );
  };

  // ==========================================================
  // PROCUREMENT -> ORDERS
  // ==========================================================

  const handleViewOrders = () => {
    clearProcurementContext();

    setActivePage("orders");
  };

  // ==========================================================
  // AUTHENTICATION LOADING
  // ==========================================================

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />

        <AuthenticationLoading />
      </ThemeProvider>
    );
  }

  // ==========================================================
  // LOGIN PAGE
  // ==========================================================

  if (!user) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />

        <Login />
      </ThemeProvider>
    );
  }

  // ==========================================================
  // RENDER CURRENT PAGE
  // ==========================================================

  const renderPage = () => {
    switch (activePage) {
      // ======================================================
      // DASHBOARD
      // ======================================================

      case "dashboard":
        return <Dashboard />;

      // ======================================================
      // INVENTORY
      // ======================================================

      case "inventory":
        return (
          <Inventory
            onProcure={handleProcureFromInventory}
          />
        );

      // ======================================================
      // SUPPLIERS
      // ======================================================

      case "suppliers":
        return <Suppliers />;

      // ======================================================
      // PROCUREMENT
      // ======================================================

      case "procurement":
        return (
          <Box
            sx={{
              width: "100%",
              minWidth: 0
            }}
          >
            {/* INVENTORY PROCUREMENT REQUEST */}

            {procurementContext && (
              <Box
                sx={{
                  px: {
                    xs: 2,
                    md: 3
                  },
                  pt: 2
                }}
              >
                <Alert
                  severity={
                    procurementContext.urgency ===
                    "URGENT"
                      ? "error"
                      : procurementContext.urgency ===
                        "HIGH"
                      ? "warning"
                      : "info"
                  }
                  variant="outlined"
                  onClose={clearProcurementContext}
                  sx={{
                    backgroundColor: "#FFFFFF",

                    borderRadius: 2,

                    boxShadow:
                      "0 3px 12px rgba(15,23,42,0.03)"
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",

                      alignItems: "center",

                      flexWrap: "wrap",

                      gap: 0.6,

                      fontSize: 13
                    }}
                  >
                    <Box
                      component="span"
                      sx={{
                        fontWeight: 700
                      }}
                    >
                      Inventory procurement request:
                    </Box>

                    <Box
                      component="span"
                      sx={{
                        fontWeight: 600
                      }}
                    >
                      {procurementContext.vehicle_type ||
                        procurementContext.vehicle_code ||
                        "Vehicle"}
                    </Box>

                    <Box component="span">
                      →
                    </Box>

                    <Box
                      component="span"
                      sx={{
                        fontWeight: 700
                      }}
                    >
                      {procurementContext.part_name ||
                        procurementContext.component_name ||
                        "Component"}
                    </Box>

                    <Box
                      component="span"
                      sx={{
                        color: "text.secondary"
                      }}
                    >
                      | Recommended quantity:
                    </Box>

                    <Box
                      component="span"
                      sx={{
                        fontWeight: 800,
                        color: "primary.main"
                      }}
                    >
                      {Number(
                        procurementContext.required_quantity ||
                          0
                      ).toLocaleString()}
                    </Box>

                    <Box
                      component="span"
                      sx={{
                        color: "text.secondary"
                      }}
                    >
                      | Urgency:
                    </Box>

                    <Box
                      component="span"
                      sx={{
                        fontWeight: 800
                      }}
                    >
                      {procurementContext.urgency ||
                        "NORMAL"}
                    </Box>
                  </Box>
                </Alert>
              </Box>
            )}

            {/* PROCUREMENT PAGE */}

            <Procurement
              initialRequest={procurementContext}
              onViewOrders={handleViewOrders}
            />
          </Box>
        );

      // ======================================================
      // ORDERS
      // ======================================================

      case "orders":
        return <Orders />;

      // ======================================================
      // AI ASSISTANT
      // ======================================================

      case "graph-rag":
        return <GraphRAG />;

      // ======================================================
      // DEFAULT
      // ======================================================

      default:
        return <Dashboard />;
    }
  };

  // ==========================================================
  // MAIN APPLICATION LAYOUT
  // ==========================================================

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <Box
        sx={{
          display: "flex",

          width: "100%",

          minHeight: "100vh",

          overflowX: "hidden",

          backgroundColor: "background.default"
        }}
      >
        {/* ====================================================
            SIDEBAR
        ==================================================== */}

        <Sidebar
          menuItems={MENU_ITEMS}
          activePage={activePage}
          setActivePage={setActivePage}
          collapsed={sidebarCollapsed}
          onToggle={toggleSidebar}
        />

        {/* ====================================================
            MAIN CONTENT
        ==================================================== */}

        <Box
          component="main"
          sx={{
            flexGrow: 1,

            flexBasis: 0,

            minWidth: 0,

            minHeight: "100vh",

            display: "flex",

            flexDirection: "column",

            backgroundColor: "#F4F7FB"
          }}
        >
          {/* TOP NAVIGATION BAR */}

          <TopBar
            activePage={activePage}
            setActivePage={setActivePage}
            onToggleSidebar={toggleSidebar}
          />

          {/* FULL-WIDTH PAGE CONTENT */}

          <Box
            sx={{
              width: "100%",

              minWidth: 0,

              flexGrow: 1,

              "& > *": {
                maxWidth: "100%"
              }
            }}
          >
            {renderPage()}
          </Box>

          {/* FOOTER */}

          <Box
            component="footer"
            sx={{
              px: {
                xs: 2,
                md: 3
              },

              py: 1.5,

              mt: "auto",

              display: "flex",

              alignItems: "center",

              justifyContent: "space-between",

              flexWrap: "wrap",

              gap: 1,

              borderTop: "1px solid #E4EAF2",

              backgroundColor: "#FFFFFF"
            }}
          >
            <Box
              sx={{
                fontSize: 11,
                color: "#94A3B8"
              }}
            >
              © {new Date().getFullYear()} EV Supply Chain
            </Box>

            <Box
              sx={{
                fontSize: 11,
                color: "#94A3B8"
              }}
            >
              Intelligent Supply Chain Management
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;