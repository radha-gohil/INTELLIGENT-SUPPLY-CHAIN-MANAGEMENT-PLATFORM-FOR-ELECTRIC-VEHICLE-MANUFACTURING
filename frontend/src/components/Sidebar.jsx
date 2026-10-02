import {
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
} from "@mui/material";

import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import Inventory2RoundedIcon from "@mui/icons-material/Inventory2Rounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import ShoppingCartRoundedIcon from "@mui/icons-material/ShoppingCartRounded";
import LocalShippingRoundedIcon from "@mui/icons-material/LocalShippingRounded";
import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import DirectionsCarRoundedIcon from "@mui/icons-material/DirectionsCarRounded";
import ChevronLeftRoundedIcon from "@mui/icons-material/ChevronLeftRounded";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";

const SIDEBAR_WIDTH = 238;
const COLLAPSED_WIDTH = 76;

const DEFAULT_MENU_ITEMS = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: <DashboardRoundedIcon />,
  },
  {
    id: "inventory",
    label: "Inventory",
    icon: <Inventory2RoundedIcon />,
  },
  {
    id: "suppliers",
    label: "Suppliers",
    icon: <GroupsRoundedIcon />,
  },
  {
    id: "procurement",
    label: "Procurement",
    icon: <ShoppingCartRoundedIcon />,
  },
  {
    id: "orders",
    label: "Orders",
    icon: <LocalShippingRoundedIcon />,
  },
  {
    id: "graph-rag",
    label: "AI Assistant",
    icon: <AutoAwesomeRoundedIcon />,
  },
];

function Sidebar({
  menuItems = DEFAULT_MENU_ITEMS,
  activePage = "dashboard",
  setActivePage,
  collapsed = false,
  onToggle,
}) {
  const width = collapsed
    ? COLLAPSED_WIDTH
    : SIDEBAR_WIDTH;

  const handleNavigation = (pageId) => {
    if (typeof setActivePage === "function") {
      setActivePage(pageId);
    }
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,

        "& .MuiDrawer-paper": {
          width,
          boxSizing: "border-box",
          overflowX: "hidden",
          borderRight: "none",
          background:
            "linear-gradient(180deg, #102746 0%, #0B1D36 100%)",
          color: "#FFFFFF",
          transition: "width 0.25s ease",
        },
      }}
    >
      {/* LOGO AND BRAND */}

      <Box
        sx={{
          height: 84,
          minHeight: 84,
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed
            ? "center"
            : "space-between",
          px: collapsed ? 1 : 2,
          borderBottom:
            "1px solid rgba(255,255,255,0.09)",
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1.3,
            minWidth: 0,
          }}
        >
          <Box
            sx={{
              width: 42,
              height: 42,
              minWidth: 42,
              borderRadius: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background:
                "linear-gradient(135deg, #0875E1, #09B6D5)",
              boxShadow:
                "0 5px 16px rgba(0,0,0,0.15)",
            }}
          >
            <DirectionsCarRoundedIcon
              sx={{
                fontSize: 26,
                color: "#FFFFFF",
              }}
            />
          </Box>

          {!collapsed && (
            <Box sx={{ minWidth: 0 }}>
              <Typography
                sx={{
                  fontSize: 15,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  whiteSpace: "nowrap",
                  letterSpacing: "-0.3px",
                }}
              >
                EV Supply Chain
              </Typography>

              <Typography
                sx={{
                  fontSize: 10,
                  color: "#94AFCB",
                  whiteSpace: "nowrap",
                }}
              >
                Management Platform
              </Typography>
            </Box>
          )}
        </Box>
      </Box>

      {/* NAVIGATION */}

      <Box
        component="nav"
        aria-label="Main navigation"
        sx={{
          flexGrow: 1,
          pt: 2,
          px: collapsed ? 1 : 1.5,
          overflowY: "auto",
          overflowX: "hidden",
        }}
      >
        <List disablePadding>
          {menuItems.map((item) => {
            const selected =
              activePage === item.id;

            return (
              <Tooltip
                key={item.id}
                title={collapsed ? item.label : ""}
                placement="right"
                arrow
              >
                <ListItemButton
                  selected={selected}
                  onClick={() =>
                    handleNavigation(item.id)
                  }
                  sx={{
                    minHeight: 47,
                    mb: 0.65,
                    px: collapsed ? 1 : 1.5,
                    borderRadius: "10px",

                    justifyContent: collapsed
                      ? "center"
                      : "flex-start",

                    color: selected
                      ? "#FFFFFF"
                      : "#AFC1D7",

                    backgroundColor: selected
                      ? "#0865CA"
                      : "transparent",

                    transition:
                      "background-color 0.2s ease",

                    "&.Mui-selected": {
                      backgroundColor: "#0865CA",
                      color: "#FFFFFF",
                    },

                    "&.Mui-selected:hover": {
                      backgroundColor: "#0874DF",
                    },

                    "&:hover": {
                      backgroundColor:
                        "rgba(255,255,255,0.08)",
                      color: "#FFFFFF",
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: collapsed ? 0 : 39,
                      color: "inherit",
                      justifyContent: "center",
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>

                  {!collapsed && (
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: 13,
                        fontWeight: selected
                          ? 800
                          : 600,
                        whiteSpace: "nowrap",
                      }}
                    />
                  )}

                  {!collapsed && selected && (
                    <Box
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        backgroundColor: "#FFFFFF",
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            );
          })}
        </List>
      </Box>

      {/* COLLAPSE CONTROL — NO USER PROFILE */}

      <Box
        sx={{
          borderTop:
            "1px solid rgba(255,255,255,0.09)",
          p: 1.5,
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed
            ? "center"
            : "flex-end",
        }}
      >
        <Tooltip
          title={
            collapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
          placement="right"
        >
          <IconButton
            aria-label={
              collapsed
                ? "Expand sidebar"
                : "Collapse sidebar"
            }
            onClick={() => {
              if (typeof onToggle === "function") {
                onToggle();
              }
            }}
            sx={{
              width: 36,
              height: 36,
              color: "#B7C8DB",
              bgcolor:
                "rgba(255,255,255,0.07)",

              "&:hover": {
                bgcolor:
                  "rgba(255,255,255,0.14)",
                color: "#FFFFFF",
              },
            }}
          >
            {collapsed ? (
              <ChevronRightRoundedIcon />
            ) : (
              <ChevronLeftRoundedIcon />
            )}
          </IconButton>
        </Tooltip>
      </Box>
    </Drawer>
  );
}

export default Sidebar;