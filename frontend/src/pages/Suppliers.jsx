import { useEffect, useState } from "react";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from "@mui/material";


// ============================================================
// API BASE URL
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";


// ============================================================
// SUPPLIERS PAGE
// ============================================================

function Suppliers() {

  const [suppliers, setSuppliers] = useState([]);

  const [selectedSupplier, setSelectedSupplier] =
    useState(null);

  const [supplierDetails, setSupplierDetails] =
    useState(null);

  const [riskData, setRiskData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [detailsLoading, setDetailsLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [detailsError, setDetailsError] =
    useState("");


  // ==========================================================
  // LOAD SUPPLIER METRICS
  // ==========================================================

  useEffect(() => {

    loadSuppliers();

  }, []);


  const loadSuppliers = async () => {

    try {

      setLoading(true);

      setError("");

      const response = await fetch(
        `${API_BASE_URL}/supplier-metrics`
      );


      if (!response.ok) {

        throw new Error(
          `Failed to load suppliers (${response.status})`
        );

      }


      const data = await response.json();

      setSuppliers(data);


    } catch (err) {

      console.error(err);

      setError(
        "Unable to load supplier information. " +
        "Make sure FastAPI is running."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // LOAD SUPPLIER DETAILS
  // ==========================================================

  const loadSupplierDetails = async (
    supplierId
  ) => {

    try {

      setDetailsLoading(true);

      setDetailsError("");

      setSelectedSupplier(supplierId);


      // ------------------------------------------------------
      // Supplier details
      // ------------------------------------------------------

      const detailsResponse = await fetch(

        `${API_BASE_URL}/supplier-details/supplier/${supplierId}`

      );


      if (!detailsResponse.ok) {

        throw new Error(
          "Failed to load supplier details."
        );

      }


      const detailsData =
        await detailsResponse.json();


      setSupplierDetails(detailsData);


      // ------------------------------------------------------
      // Supplier AI risk
      // ------------------------------------------------------

      const riskResponse = await fetch(

        `${API_BASE_URL}/supplier-risk/supplier/${supplierId}`

      );


      if (riskResponse.ok) {

        const riskResult =
          await riskResponse.json();

        setRiskData(riskResult);

      } else {

        setRiskData(null);

      }


    } catch (err) {

      console.error(err);

      setDetailsError(
        "Unable to load supplier details."
      );

      setSupplierDetails(null);

      setRiskData(null);

    } finally {

      setDetailsLoading(false);

    }

  };


  // ==========================================================
  // RISK COLOR
  // ==========================================================

  const getRiskColor = (risk) => {

    switch (risk) {

      case "LOW":
        return "success";

      case "MEDIUM":
        return "warning";

      case "HIGH":
        return "error";

      default:
        return "default";

    }

  };


  // ==========================================================
  // STATUS COLOR
  // ==========================================================

  const getStatusColor = (status) => {

    if (status === "ACTIVE") {

      return "success";

    }

    return "default";

  };


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <Box
        sx={{
          p: 4,
          display: "flex",
          justifyContent: "center"
        }}
      >

        <CircularProgress />

      </Box>

    );

  }


  // ==========================================================
  // MAIN PAGE
  // ==========================================================

  return (

    <Box sx={{ p: 3 }}>

      {/* ====================================================
          PAGE HEADER
      ==================================================== */}

      <Box sx={{ mb: 3 }}>

        <Typography
          variant="h4"
          fontWeight="700"
        >
          Supplier Management
        </Typography>

        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mt: 0.5 }}
        >
          Monitor supplier performance, availability
          and AI-based supplier risk.
        </Typography>

      </Box>


      {/* ====================================================
          ERROR
      ==================================================== */}

      {error && (

        <Alert
          severity="error"
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>

      )}


      {/* ====================================================
          SUPPLIER SUMMARY
      ==================================================== */}

      <Grid
        container
        spacing={2}
        sx={{ mb: 3 }}
      >

        <Grid item xs={12} sm={6} md={3}>

          <Card>

            <CardContent>

              <Typography
                color="text.secondary"
                variant="body2"
              >
                Total Suppliers
              </Typography>

              <Typography
                variant="h4"
                fontWeight="700"
              >
                {suppliers.length}
              </Typography>

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} sm={6} md={3}>

          <Card>

            <CardContent>

              <Typography
                color="text.secondary"
                variant="body2"
              >
                Active Suppliers
              </Typography>

              <Typography
                variant="h4"
                fontWeight="700"
              >
                {suppliers.length}
              </Typography>

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} sm={6} md={3}>

          <Card>

            <CardContent>

              <Typography
                color="text.secondary"
                variant="body2"
              >
                Highest Reliability
              </Typography>

              <Typography
                variant="h4"
                fontWeight="700"
              >
                {suppliers.length > 0
                  ? `${Math.max(
                      ...suppliers.map(
                        s => s.reliability_score
                      )
                    ).toFixed(1)}%`
                  : "0%"
                }
              </Typography>

            </CardContent>

          </Card>

        </Grid>


        <Grid item xs={12} sm={6} md={3}>

          <Card>

            <CardContent>

              <Typography
                color="text.secondary"
                variant="body2"
              >
                Suppliers With Risk Data
              </Typography>

              <Typography
                variant="h4"
                fontWeight="700"
              >
                AI
              </Typography>

            </CardContent>

          </Card>

        </Grid>

      </Grid>


      {/* ====================================================
          SUPPLIER TABLE
      ==================================================== */}

      <Card sx={{ mb: 3 }}>

        <CardContent>

          <Typography
            variant="h6"
            fontWeight="700"
            sx={{ mb: 2 }}
          >
            Supplier Performance
          </Typography>


          <TableContainer
            component={Paper}
            variant="outlined"
          >

            <Table>

              <TableHead>

                <TableRow>

                  <TableCell>
                    Supplier
                  </TableCell>

                  <TableCell>
                    Total Orders
                  </TableCell>

                  <TableCell>
                    On-Time Delivery
                  </TableCell>

                  <TableCell>
                    Fill Rate
                  </TableCell>

                  <TableCell>
                    Defect Rate
                  </TableCell>

                  <TableCell>
                    Reliability
                  </TableCell>

                  <TableCell>
                    Action
                  </TableCell>

                </TableRow>

              </TableHead>


              <TableBody>

                {suppliers.map(
                  (supplier) => (

                    <TableRow
                      key={supplier.supplier_id}
                      hover
                    >

                      <TableCell>

                        <Typography
                          fontWeight="600"
                        >
                          {supplier.supplier_name}
                        </Typography>

                        <Typography
                          variant="caption"
                          color="text.secondary"
                        >
                          {supplier.supplier_code}
                        </Typography>

                      </TableCell>


                      <TableCell>
                        {supplier.total_orders}
                      </TableCell>


                      <TableCell>
                        {supplier.on_time_delivery_rate.toFixed(2)}%
                      </TableCell>


                      <TableCell>
                        {supplier.fill_rate.toFixed(2)}%
                      </TableCell>


                      <TableCell>
                        {supplier.defect_rate.toFixed(2)}%
                      </TableCell>


                      <TableCell>

                        <Typography
                          fontWeight="700"
                        >
                          {supplier.reliability_score.toFixed(2)}%
                        </Typography>

                      </TableCell>


                      <TableCell>

                        <Chip
                          label="View"
                          clickable
                          color="primary"
                          variant="outlined"
                          onClick={() =>
                            loadSupplierDetails(
                              supplier.supplier_id
                            )
                          }
                        />

                      </TableCell>

                    </TableRow>

                  )
                )}

              </TableBody>

            </Table>

          </TableContainer>

        </CardContent>

      </Card>


      {/* ====================================================
          SUPPLIER DETAILS
      ==================================================== */}

      {detailsLoading && (

        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            p: 4
          }}
        >

          <CircularProgress />

        </Box>

      )}


      {detailsError && (

        <Alert
          severity="error"
          sx={{ mb: 3 }}
        >
          {detailsError}
        </Alert>

      )}


      {supplierDetails &&
        !detailsLoading && (

        <Card>

          <CardContent>

            {/* ============================================
                SUPPLIER HEADER
            ============================================ */}

            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2
              }}
            >

              <Box>

                <Typography
                  variant="h5"
                  fontWeight="700"
                >
                  {supplierDetails.supplier_name}
                </Typography>

                <Typography
                  color="text.secondary"
                >
                  {supplierDetails.supplier_code}
                </Typography>

              </Box>


              <Chip
                label={supplierDetails.status}
                color={getStatusColor(
                  supplierDetails.status
                )}
              />

            </Box>


            <Divider sx={{ mb: 3 }} />


            {/* ============================================
                SUPPLIER INFORMATION
            ============================================ */}

            <Grid
              container
              spacing={2}
              sx={{ mb: 3 }}
            >

              <Grid item xs={12} md={4}>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Location
                </Typography>

                <Typography
                  fontWeight="600"
                >
                  {supplierDetails.location ||
                    "Not available"}
                </Typography>

              </Grid>


              <Grid item xs={12} md={4}>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Email
                </Typography>

                <Typography
                  fontWeight="600"
                >
                  {supplierDetails.contact_email ||
                    "Not available"}
                </Typography>

              </Grid>


              <Grid item xs={12} md={4}>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Phone
                </Typography>

                <Typography
                  fontWeight="600"
                >
                  {supplierDetails.contact_phone ||
                    "Not available"}
                </Typography>

              </Grid>

            </Grid>


            {/* ============================================
                AI RISK
            ============================================ */}

            {riskData && (

              <Card
                variant="outlined"
                sx={{ mb: 3 }}
              >

                <CardContent>

                  <Typography
                    variant="h6"
                    fontWeight="700"
                    sx={{ mb: 2 }}
                  >
                    AI Supplier Risk Assessment
                  </Typography>


                  <Grid
                    container
                    spacing={2}
                  >

                    <Grid
                      item
                      xs={12}
                      md={4}
                    >

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        Risk Level
                      </Typography>

                      <Chip
                        label={riskData.risk_level}
                        color={getRiskColor(
                          riskData.risk_level
                        )}
                        sx={{ mt: 1 }}
                      />

                    </Grid>


                    <Grid
                      item
                      xs={12}
                      md={4}
                    >

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        Prediction Confidence
                      </Typography>

                      <Typography
                        variant="h5"
                        fontWeight="700"
                      >
                        {(
                          riskData.confidence * 100
                        ).toFixed(2)}%
                      </Typography>

                    </Grid>


                    <Grid
                      item
                      xs={12}
                      md={4}
                    >

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        Supplier ID
                      </Typography>

                      <Typography
                        variant="h6"
                        fontWeight="700"
                      >
                        {riskData.supplier_id}
                      </Typography>

                    </Grid>

                  </Grid>


                  <Box sx={{ mt: 2 }}>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1 }}
                    >
                      Risk Probabilities
                    </Typography>


                    {Object.entries(
                      riskData.risk_probabilities
                    ).map(
                      ([risk, probability]) => (

                        <Box
                          key={risk}
                          sx={{
                            display: "flex",
                            justifyContent:
                              "space-between",
                            mb: 1
                          }}
                        >

                          <Typography>
                            {risk}
                          </Typography>

                          <Typography
                            fontWeight="600"
                          >
                            {(
                              probability * 100
                            ).toFixed(2)}%
                          </Typography>

                        </Box>

                      )
                    )}

                  </Box>

                </CardContent>

              </Card>

            )}


            {/* ============================================
                COMPONENTS
            ============================================ */}

            <Typography
              variant="h6"
              fontWeight="700"
              sx={{ mb: 2 }}
            >
              Supplied Components
            </Typography>


            {supplierDetails.components.length === 0 ? (

              <Alert severity="info">

                No component information available
                for this supplier.

              </Alert>

            ) : (

              <TableContainer
                component={Paper}
                variant="outlined"
              >

                <Table>

                  <TableHead>

                    <TableRow>

                      <TableCell>
                        Component
                      </TableCell>

                      <TableCell>
                        Criticality
                      </TableCell>

                      <TableCell>
                        Available
                      </TableCell>

                      <TableCell>
                        ATP
                      </TableCell>

                      <TableCell>
                        Lead Time
                      </TableCell>

                      <TableCell>
                        Unit Price
                      </TableCell>

                      <TableCell>
                        MOQ
                      </TableCell>

                      <TableCell>
                        Approval
                      </TableCell>

                    </TableRow>

                  </TableHead>


                  <TableBody>

                    {supplierDetails.components.map(
                      (component) => (

                        <TableRow
                          key={
                            component.component_id
                          }
                        >

                          <TableCell>

                            <Typography
                              fontWeight="600"
                            >
                              {component.part_name}
                            </Typography>

                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {component.part_id}
                            </Typography>

                          </TableCell>


                          <TableCell>

                            <Chip
                              label={
                                component.criticality
                              }
                              size="small"
                            />

                          </TableCell>


                          <TableCell>

                            {component.available_quantity}

                          </TableCell>


                          <TableCell>

                            <Typography
                              fontWeight="700"
                            >
                              {
                                component.available_to_promise
                              }
                            </Typography>

                          </TableCell>


                          <TableCell>

                            {component.standard_lead_time_days
                              ?? "-"}{" "}
                            days

                          </TableCell>


                          <TableCell>

                            {component.unit_price
                              != null
                              ? `₹${component.unit_price}`
                              : "-"}

                          </TableCell>


                          <TableCell>

                            {
                              component.minimum_order_quantity
                            }

                          </TableCell>


                          <TableCell>

                            <Chip
                              label={
                                component.is_approved
                                  ? "Approved"
                                  : "Not Approved"
                              }
                              color={
                                component.is_approved
                                  ? "success"
                                  : "error"
                              }
                              size="small"
                            />

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

      )}

    </Box>

  );

}


export default Suppliers;