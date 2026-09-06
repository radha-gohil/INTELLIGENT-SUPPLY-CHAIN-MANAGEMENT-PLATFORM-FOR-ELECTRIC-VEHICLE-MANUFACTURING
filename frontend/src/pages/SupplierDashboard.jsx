import React, { useEffect, useState } from "react";

import {
    Box,
    Typography,
    Grid,
    Card,
    CardContent,
    CircularProgress,
    Alert,
    Chip,
    Divider
} from "@mui/material";

import {
    getSuppliers,
    getAllSupplierMetrics,
    getSupplierRisk
} from "../services/api";


// ============================================================
// SUPPLIER DASHBOARD
// ============================================================

function SupplierDashboard() {

    const [suppliers, setSuppliers] = useState([]);

    const [metrics, setMetrics] = useState([]);

    const [risks, setRisks] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    // ========================================================
    // LOAD DASHBOARD DATA
    // ========================================================

    useEffect(() => {

        loadDashboard();

    }, []);


    async function loadDashboard() {

        try {

            setLoading(true);

            setError("");


            // ------------------------------------------------
            // Get suppliers
            // ------------------------------------------------

            const supplierData =
                await getSuppliers();

            setSuppliers(
                supplierData
            );


            // ------------------------------------------------
            // Get supplier metrics
            // ------------------------------------------------

            const metricsData =
                await getAllSupplierMetrics();

            setMetrics(
                metricsData
            );


            // ------------------------------------------------
            // Get supplier risks
            // ------------------------------------------------

            const riskResults = [];

            for (
                const supplier
                of supplierData
            ) {

                try {

                    const risk =
                        await getSupplierRisk(
                            supplier.id
                        );

                    riskResults.push(
                        risk
                    );

                } catch (riskError) {

                    console.error(
                        `Risk prediction failed for supplier ${supplier.id}`,
                        riskError
                    );

                }

            }


            setRisks(
                riskResults
            );

        } catch (err) {

            console.error(
                "Dashboard loading error:",
                err
            );

            setError(
                err.message ||
                "Unable to load supplier dashboard."
            );

        } finally {

            setLoading(false);

        }

    }


    // ========================================================
    // LOADING
    // ========================================================

    if (loading) {

        return (

            <Box
                sx={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    minHeight: "70vh"
                }}
            >

                <CircularProgress />

            </Box>

        );

    }


    // ========================================================
    // ERROR
    // ========================================================

    if (error) {

        return (

            <Box sx={{ p: 4 }}>

                <Alert severity="error">

                    {error}

                </Alert>

            </Box>

        );

    }


    // ========================================================
    // DASHBOARD CALCULATIONS
    // ========================================================

    const totalSuppliers =
        suppliers.length;


    const activeSuppliers =
        suppliers.filter(
            supplier =>
                supplier.is_active === true
        ).length;


    const highRiskSuppliers =
        risks.filter(
            risk =>
                risk.risk_level === "HIGH"
        ).length;


    const mediumRiskSuppliers =
        risks.filter(
            risk =>
                risk.risk_level === "MEDIUM"
        ).length;


    const lowRiskSuppliers =
        risks.filter(
            risk =>
                risk.risk_level === "LOW"
        ).length;


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <Box sx={{ p: 4 }}>

            {/* =================================================
                HEADER
            ================================================= */}

            <Typography
                variant="h4"
                fontWeight="bold"
                gutterBottom
            >
                Supplier Intelligence Dashboard
            </Typography>


            <Typography
                variant="body1"
                color="text.secondary"
                sx={{ mb: 4 }}
            >
                AI-powered supplier monitoring,
                performance analysis and risk assessment.
            </Typography>


            {/* =================================================
                ERROR WARNING
            ================================================= */}

            {risks.length === 0 && (

                <Alert
                    severity="warning"
                    sx={{ mb: 3 }}
                >
                    Supplier risk predictions are
                    currently unavailable.
                </Alert>

            )}


            {/* =================================================
                SUMMARY CARDS
            ================================================= */}

            <Grid
                container
                spacing={3}
                sx={{ mb: 4 }}
            >

                {/* TOTAL SUPPLIERS */}

                <Grid
                    size={{
                        xs: 12,
                        sm: 6,
                        md: 3
                    }}
                >

                    <Card>

                        <CardContent>

                            <Typography
                                color="text.secondary"
                            >
                                Total Suppliers
                            </Typography>

                            <Typography
                                variant="h3"
                                fontWeight="bold"
                            >
                                {totalSuppliers}
                            </Typography>

                        </CardContent>

                    </Card>

                </Grid>


                {/* ACTIVE SUPPLIERS */}

                <Grid
                    size={{
                        xs: 12,
                        sm: 6,
                        md: 3
                    }}
                >

                    <Card>

                        <CardContent>

                            <Typography
                                color="text.secondary"
                            >
                                Active Suppliers
                            </Typography>

                            <Typography
                                variant="h3"
                                fontWeight="bold"
                            >
                                {activeSuppliers}
                            </Typography>

                        </CardContent>

                    </Card>

                </Grid>


                {/* HIGH RISK */}

                <Grid
                    size={{
                        xs: 12,
                        sm: 6,
                        md: 3
                    }}
                >

                    <Card>

                        <CardContent>

                            <Typography
                                color="text.secondary"
                            >
                                High Risk
                            </Typography>

                            <Typography
                                variant="h3"
                                fontWeight="bold"
                            >
                                {highRiskSuppliers}
                            </Typography>

                        </CardContent>

                    </Card>

                </Grid>


                {/* MEDIUM RISK */}

                <Grid
                    size={{
                        xs: 12,
                        sm: 6,
                        md: 3
                    }}
                >

                    <Card>

                        <CardContent>

                            <Typography
                                color="text.secondary"
                            >
                                Medium Risk
                            </Typography>

                            <Typography
                                variant="h3"
                                fontWeight="bold"
                            >
                                {mediumRiskSuppliers}
                            </Typography>

                        </CardContent>

                    </Card>

                </Grid>

            </Grid>


            {/* =================================================
                RISK SUMMARY
            ================================================= */}

            <Card sx={{ mb: 4 }}>

                <CardContent>

                    <Typography
                        variant="h6"
                        fontWeight="bold"
                        gutterBottom
                    >
                        AI Supplier Risk Overview
                    </Typography>


                    <Divider sx={{ mb: 3 }} />


                    <Box
                        sx={{
                            display: "flex",
                            gap: 2,
                            flexWrap: "wrap"
                        }}
                    >

                        <Chip
                            label={`HIGH: ${highRiskSuppliers}`}
                            color="error"
                        />


                        <Chip
                            label={`MEDIUM: ${mediumRiskSuppliers}`}
                            color="warning"
                        />


                        <Chip
                            label={`LOW: ${lowRiskSuppliers}`}
                            color="success"
                        />

                    </Box>

                </CardContent>

            </Card>


            {/* =================================================
                SUPPLIER LIST
            ================================================= */}

            <Typography
                variant="h5"
                fontWeight="bold"
                sx={{ mb: 2 }}
            >
                Supplier Overview
            </Typography>


            <Grid
                container
                spacing={3}
            >

                {suppliers.map(
                    supplier => {

                        const metric =
                            metrics.find(
                                item =>
                                    item.supplier_id
                                    === supplier.id
                            );


                        const risk =
                            risks.find(
                                item =>
                                    item.supplier_id
                                    === supplier.id
                            );


                        return (

                            <Grid
                                size={{
                                    xs: 12,
                                    md: 6,
                                    lg: 4
                                }}
                                key={supplier.id}
                            >

                                <Card>

                                    <CardContent>

                                        {/* SUPPLIER NAME */}

                                        <Typography
                                            variant="h6"
                                            fontWeight="bold"
                                        >
                                            {supplier.supplier_name}
                                        </Typography>


                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{
                                                mb: 2
                                            }}
                                        >
                                            {supplier.supplier_code}
                                        </Typography>


                                        {/* STATUS */}

                                        <Chip
                                            label={
                                                supplier.status
                                            }
                                            size="small"
                                            sx={{
                                                mb: 2
                                            }}
                                        />


                                        <Divider
                                            sx={{
                                                mb: 2
                                            }}
                                        />


                                        {/* PERFORMANCE */}

                                        <Typography
                                            variant="body2"
                                        >
                                            Reliability Score:{" "}

                                            <strong>
                                                {metric
                                                    ? `${metric.reliability_score}%`
                                                    : "N/A"}
                                            </strong>
                                        </Typography>


                                        <Typography
                                            variant="body2"
                                        >
                                            On-Time Delivery:{" "}

                                            <strong>
                                                {metric
                                                    ? `${metric.on_time_delivery_rate}%`
                                                    : "N/A"}
                                            </strong>
                                        </Typography>


                                        <Typography
                                            variant="body2"
                                        >
                                            Fill Rate:{" "}

                                            <strong>
                                                {metric
                                                    ? `${metric.fill_rate}%`
                                                    : "N/A"}
                                            </strong>
                                        </Typography>


                                        <Typography
                                            variant="body2"
                                        >
                                            Defect Rate:{" "}

                                            <strong>
                                                {metric
                                                    ? `${metric.defect_rate}%`
                                                    : "N/A"}
                                            </strong>
                                        </Typography>


                                        {/* RISK */}

                                        <Box
                                            sx={{
                                                mt: 2
                                            }}
                                        >

                                            {risk && (

                                                <Chip
                                                    label={
                                                        `AI Risk: ${risk.risk_level}`
                                                    }
                                                    color={
                                                        risk.risk_level
                                                        === "HIGH"
                                                            ? "error"
                                                            : risk.risk_level
                                                            === "MEDIUM"
                                                            ? "warning"
                                                            : "success"
                                                    }
                                                />

                                            )}

                                        </Box>

                                    </CardContent>

                                </Card>

                            </Grid>

                        );

                    }
                )}

            </Grid>

        </Box>

    );

}


export default SupplierDashboard;