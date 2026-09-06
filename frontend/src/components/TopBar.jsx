import {
  AppBar,
  Box,
  Toolbar,
  Typography
} from "@mui/material";


function TopBar() {

  return (

    <AppBar

      position="static"

      elevation={0}

      sx={{

        backgroundColor:
          "#ffffff",

        color:
          "#1f2937",

        borderBottom:
          "1px solid #e5e7eb"

      }}

    >

      <Toolbar>

        <Box sx={{ flexGrow: 1 }}>

          <Typography
            variant="h6"
            fontWeight={600}
          >
            Supply Chain Intelligence
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
          >
            Intelligent procurement and
            supplier management
          </Typography>

        </Box>

      </Toolbar>

    </AppBar>

  );

}


export default TopBar;