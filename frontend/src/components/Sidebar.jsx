import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography
} from "@mui/material";


const drawerWidth = 250;


function Sidebar({
  menuItems,
  activePage,
  setActivePage
}) {

  return (

    <Drawer

      variant="permanent"

      sx={{

        width: drawerWidth,

        flexShrink: 0,

        "& .MuiDrawer-paper": {

          width: drawerWidth,

          boxSizing: "border-box",

          borderRight:
            "1px solid #e5e7eb",

          backgroundColor:
            "#ffffff"

        }

      }}

    >

      <Box
        sx={{
          height: 70,
          display: "flex",
          alignItems: "center",
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


      <List sx={{ px: 1.5, py: 2 }}>

        {menuItems.map((item) => (

          <ListItemButton

            key={item.id}

            selected={
              activePage === item.id
            }

            onClick={() =>
              setActivePage(item.id)
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
                  activePage === item.id
                    ? "primary.main"
                    : "inherit"
              }}
            >

              {item.icon}

            </ListItemIcon>


            <ListItemText
              primary={item.label}
            />

          </ListItemButton>

        ))}

      </List>

    </Drawer>

  );

}


export default Sidebar;