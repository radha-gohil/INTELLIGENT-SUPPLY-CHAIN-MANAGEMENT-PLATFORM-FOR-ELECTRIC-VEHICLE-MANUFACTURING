import {
  Avatar,
  Box,
  Button,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Typography
} from "@mui/material";

import LogoutIcon from "@mui/icons-material/Logout";
import PersonIcon from "@mui/icons-material/Person";

import {
  useAuth
} from "../context/AuthContext";


const drawerWidth =
  250;


function Sidebar({
  menuItems,
  activePage,
  setActivePage
}) {

  const {
    user,
    logout
  } = useAuth();


  return (

    <Drawer
      variant="permanent"
      sx={{

        width:
          drawerWidth,

        flexShrink: 0,

        "& .MuiDrawer-paper": {

          width:
            drawerWidth,

          boxSizing:
            "border-box",

          borderRight:
            "1px solid #e5e7eb",

          backgroundColor:
            "#ffffff",

          display:
            "flex",

          flexDirection:
            "column"

        }

      }}
    >

      {/* LOGO */}

      <Box
        sx={{
          height: 70,

          display:
            "flex",

          alignItems:
            "center",

          px: 3,

          borderBottom:
            "1px solid #e5e7eb"
        }}
      >

        <Typography
          variant="h6"
          fontWeight={700}
          color="primary"
        >
          EV Supply Chain
        </Typography>

      </Box>


      {/* MENU */}

      <List
        sx={{
          px: 1.5,
          py: 2,
          flexGrow: 1
        }}
      >

        {menuItems.map(
          item => (

            <ListItemButton
              key={
                item.id
              }
              selected={
                activePage ===
                item.id
              }
              onClick={() =>
                setActivePage(
                  item.id
                )
              }
              sx={{

                borderRadius: 2,

                mb: 0.5,

                "&.Mui-selected": {

                  backgroundColor:
                    "rgba(25,118,210,0.10)",

                  color:
                    "primary.main"

                }

              }}
            >

              <ListItemIcon
                sx={{
                  minWidth: 42,

                  color:
                    activePage ===
                    item.id

                      ? "primary.main"

                      : "inherit"
                }}
              >

                {item.icon}

              </ListItemIcon>


              <ListItemText
                primary={
                  item.label
                }
              />

            </ListItemButton>

          )
        )}

      </List>


      <Divider />


      {/* USER */}

      <Box
        sx={{
          p: 2
        }}
      >

        <Stack
          direction="row"
          spacing={1.5}
          alignItems="center"
          sx={{
            mb: 2
          }}
        >

          <Avatar
            sx={{
              bgcolor:
                "primary.main"
            }}
          >

            <PersonIcon />

          </Avatar>


          <Box
            sx={{
              minWidth: 0
            }}
          >

            <Typography
              variant="body2"
              fontWeight={700}
              noWrap
            >
              {
                user?.full_name ||
                user?.username
              }
            </Typography>


            <Typography
              variant="caption"
              color="text.secondary"
              noWrap
              sx={{
                display:
                  "block"
              }}
            >
              {
                user?.role
                  ?.replaceAll(
                    "_",
                    " "
                  )
              }
            </Typography>

          </Box>

        </Stack>


        <Button
          fullWidth
          variant="outlined"
          color="error"
          startIcon={
            <LogoutIcon />
          }
          onClick={
            logout
          }
          sx={{
            textTransform:
              "none"
          }}
        >
          Logout
        </Button>

      </Box>

    </Drawer>

  );

}


export default Sidebar;