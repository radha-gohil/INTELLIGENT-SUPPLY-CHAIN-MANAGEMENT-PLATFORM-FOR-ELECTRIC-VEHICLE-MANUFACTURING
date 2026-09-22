import {
  useState
} from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  InputAdornment,
  Stack,
  TextField,
  Typography
} from "@mui/material";

import EmailIcon from "@mui/icons-material/Email";
import LockIcon from "@mui/icons-material/Lock";
import ElectricCarIcon from "@mui/icons-material/ElectricCar";
import LoginIcon from "@mui/icons-material/Login";

import {
  useAuth
} from "../context/AuthContext";


function Login() {

  const {
    login
  } = useAuth();


  const [
    email,
    setEmail
  ] = useState(
    ""
  );


  const [
    password,
    setPassword
  ] = useState(
    ""
  );


  const [
    error,
    setError
  ] = useState(
    ""
  );


  const [
    submitting,
    setSubmitting
  ] = useState(
    false
  );


  // ==========================================================
  // LOGIN
  // ==========================================================

  const handleSubmit =
    async event => {

      event.preventDefault();


      setError(
        ""
      );


      if (
        !email.trim() ||
        !password
      ) {

        setError(
          "Please enter your email and password."
        );

        return;

      }


      try {

        setSubmitting(
          true
        );


        await login(
          email.trim(),
          password
        );

      }
      catch (err) {

        setError(
          err.message ||
          "Unable to sign in."
        );

      }
      finally {

        setSubmitting(
          false
        );

      }

    };


  return (

    <Box
      sx={{
        minHeight:
          "100vh",

        display:
          "flex",

        alignItems:
          "center",

        justifyContent:
          "center",

        px: 2,

        background:
          "linear-gradient(135deg, #eef5ff 0%, #f8fafc 50%, #e8f1ff 100%)"
      }}
    >

      <Card
        elevation={0}
        sx={{
          width:
            "100%",

          maxWidth:
            460,

          borderRadius:
            4,

          border:
            "1px solid #e5e7eb",

          boxShadow:
            "0 24px 70px rgba(15, 23, 42, 0.12)"
        }}
      >

        <CardContent
          sx={{
            p: {
              xs: 3,
              sm: 5
            }
          }}
        >

          <Stack
            spacing={3}
          >

            {/* LOGO */}

            <Box
              sx={{
                textAlign:
                  "center"
              }}
            >

              <Box
                sx={{
                  width: 64,
                  height: 64,

                  mx: "auto",
                  mb: 2,

                  borderRadius: 3,

                  display:
                    "flex",

                  alignItems:
                    "center",

                  justifyContent:
                    "center",

                  backgroundColor:
                    "primary.main",

                  color:
                    "white"
                }}
              >

                <ElectricCarIcon
                  sx={{
                    fontSize: 36
                  }}
                />

              </Box>


              <Typography
                variant="h4"
                fontWeight={800}
              >
                EV Supply Chain
              </Typography>


              <Typography
                color="text.secondary"
                sx={{
                  mt: 1
                }}
              >
                Intelligent Supply Chain Management Platform
              </Typography>

            </Box>


            {/* ERROR */}

            {error && (

              <Alert
                severity="error"
              >
                {error}
              </Alert>

            )}


            {/* FORM */}

            <Box
              component="form"
              onSubmit={
                handleSubmit
              }
            >

              <Stack
                spacing={2.5}
              >

                <TextField
                  label="Email"
                  type="email"
                  value={email}
                  onChange={
                    event =>
                      setEmail(
                        event.target.value
                      )
                  }
                  autoComplete="email"
                  fullWidth
                  disabled={
                    submitting
                  }
                  slotProps={{
                    input: {
                      startAdornment: (

                        <InputAdornment
                          position="start"
                        >

                          <EmailIcon
                            color="action"
                          />

                        </InputAdornment>

                      )
                    }
                  }}
                />


                <TextField
                  label="Password"
                  type="password"
                  value={password}
                  onChange={
                    event =>
                      setPassword(
                        event.target.value
                      )
                  }
                  autoComplete="current-password"
                  fullWidth
                  disabled={
                    submitting
                  }
                  slotProps={{
                    input: {
                      startAdornment: (

                        <InputAdornment
                          position="start"
                        >

                          <LockIcon
                            color="action"
                          />

                        </InputAdornment>

                      )
                    }
                  }}
                />


                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={
                    submitting
                  }
                  startIcon={
                    submitting
                      ? null
                      : <LoginIcon />
                  }
                  sx={{
                    py: 1.4,
                    fontWeight: 700,
                    textTransform:
                      "none"
                  }}
                >

                  {
                    submitting

                      ? (

                        <CircularProgress
                          size={24}
                          color="inherit"
                        />

                      )

                      : "Sign In"
                  }

                </Button>

              </Stack>

            </Box>


            <Typography
              variant="caption"
              color="text.secondary"
              textAlign="center"
            >
              Authorized users only
            </Typography>

          </Stack>

        </CardContent>

      </Card>

    </Box>

  );

}


export default Login;