import { useState } from "react";

import {
  AppBar,
  Avatar,
  Box,
  Chip,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Stack,
  Toolbar,
  Tooltip,
  Typography
} from "@mui/material";

// ============================================================
// ICONS
// ============================================================

import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import KeyboardArrowDownRoundedIcon from "@mui/icons-material/KeyboardArrowDownRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import PersonOutlineRoundedIcon from "@mui/icons-material/PersonOutlineRounded";

// ============================================================
// AUTHENTICATION
// ============================================================

import { useAuth } from "../context/AuthContext";

// ============================================================
// TOPBAR COMPONENT
// ============================================================

function TopBar() {
  const { user, logout } = useAuth();

  const [notificationAnchor, setNotificationAnchor] =
    useState(null);

  const [accountAnchor, setAccountAnchor] =
    useState(null);

  // ==========================================================
  // USER INFORMATION
  // ==========================================================

  const userName =
    user?.full_name ||
    user?.username ||
    user?.email ||
    "User";

  const userRole = String(
    user?.role || "USER"
  )
    .replaceAll("_", " ")
    .toUpperCase();

  const userInitial = String(userName)
    .charAt(0)
    .toUpperCase();

  // ==========================================================
  // DATE
  // ==========================================================

  const today = new Date().toLocaleDateString(
    "en-IN",
    {
      day: "numeric",
      month: "short",
      year: "numeric"
    }
  );

  // ==========================================================
  // CLOSE MENUS
  // ==========================================================

  const closeNotificationMenu = () => {
    setNotificationAnchor(null);
  };

  const closeAccountMenu = () => {
    setAccountAnchor(null);
  };

  // ==========================================================
  // LOGOUT
  // ==========================================================

  const handleLogout = () => {
    closeAccountMenu();
    logout();
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: "#FFFFFF",
        color: "#14263D",
        borderBottom: "1px solid #E5EAF1",
        zIndex: 10,
        width: "100%"
      }}
    >
      <Toolbar
        sx={{
          minHeight: "72px !important",
          px: {
            xs: 2,
            md: 3
          },
          gap: 2
        }}
      >
        {/* ====================================================
            LEFT EMPTY SPACE
        ==================================================== */}

        <Box sx={{ flexGrow: 1 }} />

        {/* ====================================================
            DATE
        ==================================================== */}

        <Chip
          icon={
            <CalendarTodayOutlinedIcon
              sx={{
                fontSize: 16
              }}
            />
          }
          label={today}
          variant="outlined"
          sx={{
            display: {
              xs: "none",
              sm: "flex"
            },

            borderColor: "#E2E8F0",
            color: "#475569",
            bgcolor: "#F8FAFC",
            fontWeight: 600,
            height: 35
          }}
        />

        {/* ====================================================
            NOTIFICATIONS
        ==================================================== */}

        <Tooltip title="Notifications">
          <IconButton
            aria-label="Notifications"
            onClick={(event) => {
              setNotificationAnchor(
                event.currentTarget
              );
            }}
            sx={{
              bgcolor: "#F3F6FA",
              borderRadius: 2,
              width: 40,
              height: 40,
              color: "#334155",

              "&:hover": {
                bgcolor: "#E7F1FF",
                color: "#0865CA"
              }
            }}
          >
            <NotificationsNoneOutlinedIcon />
          </IconButton>
        </Tooltip>

        {/* NOTIFICATION MENU */}

        <Menu
          anchorEl={notificationAnchor}
          open={Boolean(notificationAnchor)}
          onClose={closeNotificationMenu}
          PaperProps={{
            sx: {
              width: 310,
              maxWidth: "calc(100vw - 24px)",
              mt: 1,
              borderRadius: 3,
              boxShadow:
                "0 12px 40px rgba(15,23,42,0.12)"
            }
          }}
        >
          <Box
            sx={{
              px: 2,
              py: 1.5
            }}
          >
            <Typography
              sx={{
                fontSize: 14,
                fontWeight: 800
              }}
            >
              Notifications
            </Typography>

            <Typography
              sx={{
                fontSize: 11,
                color: "#64748B",
                mt: 0.5
              }}
            >
              Live notifications are not connected yet.
            </Typography>
          </Box>

          <Divider />

          <MenuItem onClick={closeNotificationMenu}>
            <Typography
              sx={{
                fontSize: 12,
                color: "#64748B"
              }}
            >
              No notifications to display
            </Typography>
          </MenuItem>
        </Menu>

        {/* ====================================================
            DIVIDER
        ==================================================== */}

        <Divider
          orientation="vertical"
          flexItem
          sx={{
            mx: 0.5,
            my: 2,
            borderColor: "#E5EAF1"
          }}
        />

        {/* ====================================================
            USER PROFILE
        ==================================================== */}

        <Box
          onClick={(event) => {
            setAccountAnchor(
              event.currentTarget
            );
          }}
          role="button"
          tabIndex={0}
          aria-label="Open user profile menu"
          onKeyDown={(event) => {
            if (
              event.key === "Enter" ||
              event.key === " "
            ) {
              event.preventDefault();
              setAccountAnchor(
                event.currentTarget
              );
            }
          }}
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1.2,

            px: 1,
            py: 0.6,

            borderRadius: "10px",
            cursor: "pointer",

            transition: "0.2s",

            "&:hover": {
              bgcolor: "#F3F6FA"
            }
          }}
        >
          {/* AVATAR */}

          <Avatar
            sx={{
              width: 39,
              height: 39,
              bgcolor: "#DBEAFE",
              color: "#1D4ED8",
              fontWeight: 800,
              fontSize: 15
            }}
          >
            {userInitial}
          </Avatar>

          {/* NAME AND ROLE */}

          <Box
            sx={{
              display: {
                xs: "none",
                sm: "block"
              },
              minWidth: 0
            }}
          >
            <Typography
              noWrap
              sx={{
                fontSize: 12,
                fontWeight: 800,
                color: "#14263D",
                maxWidth: 160
              }}
            >
              {userName}
            </Typography>

            <Typography
              sx={{
                fontSize: 10,
                color: "#64748B",
                fontWeight: 600
              }}
            >
              {userRole}
            </Typography>
          </Box>

          {/* DROPDOWN ARROW */}

          <KeyboardArrowDownRoundedIcon
            sx={{
              fontSize: 18,
              color: "#64748B"
            }}
          />
        </Box>

        {/* ====================================================
            PROFILE DROPDOWN MENU
        ==================================================== */}

        <Menu
          anchorEl={accountAnchor}
          open={Boolean(accountAnchor)}
          onClose={closeAccountMenu}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "right"
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "right"
          }}
          PaperProps={{
            sx: {
              minWidth: 220,
              mt: 1,
              borderRadius: 3,
              boxShadow:
                "0 12px 40px rgba(15,23,42,0.12)"
            }
          }}
        >
          {/* PROFILE DETAILS */}

          <Box
            sx={{
              px: 2,
              py: 1.5
            }}
          >
            <Stack
              direction="row"
              spacing={1.5}
              alignItems="center"
            >
              <Avatar
                sx={{
                  width: 42,
                  height: 42,
                  bgcolor: "#DBEAFE",
                  color: "#1D4ED8",
                  fontWeight: 800
                }}
              >
                {userInitial}
              </Avatar>

              <Box sx={{ minWidth: 0 }}>
                <Typography
                  noWrap
                  sx={{
                    fontSize: 13,
                    fontWeight: 800,
                    color: "#14263D"
                  }}
                >
                  {userName}
                </Typography>

                <Typography
                  sx={{
                    fontSize: 11,
                    color: "#64748B"
                  }}
                >
                  {userRole}
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Divider sx={{ my: 0.5 }} />

          {/* SIGN OUT */}

          <MenuItem
            onClick={handleLogout}
            sx={{
              py: 1.3,
              px: 2,
              gap: 1.2,

              "&:hover": {
                bgcolor: "#FFF1F2"
              }
            }}
          >
            <LogoutRoundedIcon
              sx={{
                fontSize: 19,
                color: "#DC2626"
              }}
            />

            <Typography
              sx={{
                fontSize: 13,
                fontWeight: 700,
                color: "#DC2626"
              }}
            >
              Sign out
            </Typography>
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;