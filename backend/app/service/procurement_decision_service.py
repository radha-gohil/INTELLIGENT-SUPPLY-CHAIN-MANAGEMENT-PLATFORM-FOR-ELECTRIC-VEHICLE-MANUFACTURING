from typing import List, Dict


class ProcurementDecisionService:

    # ============================================================
    # PROCUREMENT DECISION WEIGHTS
    # ============================================================
    #
    # Availability = 15%
    # Fulfillment  = 20%
    # Reliability  = 25%
    # Quality      = 10%
    # AI Risk      = 15%
    # Price        = 10%
    # Lead Time    = 5%
    #
    # Total = 100%
    # ============================================================

    WEIGHTS = {

        "availability": 0.15,

        "fulfillment": 0.20,

        "reliability": 0.25,

        "quality": 0.10,

        "ai_risk": 0.15,

        "price": 0.10,

        "lead_time": 0.05

    }


    # ============================================================
    # CALCULATE AI RISK SCORE
    # ============================================================

    @staticmethod
    def calculate_risk_score(
        supplier: Dict
    ) -> float:

        risk_level = str(
            supplier.get(
                "risk_level",
                "UNKNOWN"
            )
        ).upper()


        # --------------------------------------------------------
        # Risk score
        #
        # LOW     = 100
        # MEDIUM  = 60
        # HIGH    = 20
        # UNKNOWN = 50
        # --------------------------------------------------------

        risk_scores = {

            "LOW": 100.0,

            "MEDIUM": 60.0,

            "HIGH": 20.0,

            "UNKNOWN": 50.0

        }


        base_score = risk_scores.get(
            risk_level,
            50.0
        )


        # --------------------------------------------------------
        # Risk confidence
        # --------------------------------------------------------

        confidence = float(
            supplier.get(
                "risk_confidence",
                0.0
            ) or 0.0
        )


        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )


        # --------------------------------------------------------
        # Unknown risk
        # --------------------------------------------------------

        if risk_level == "UNKNOWN":

            return 50.0


        # --------------------------------------------------------
        # Confidence-adjusted risk score
        # --------------------------------------------------------

        risk_score = (

            (
                base_score
                *
                confidence
            )

            +

            (
                50.0
                *
                (1.0 - confidence)
            )

        )


        return round(

            max(
                0.0,
                min(
                    risk_score,
                    100.0
                )
            ),

            2

        )


    # ============================================================
    # CALCULATE PROCUREMENT SCORE
    # ============================================================

    @staticmethod
    def calculate_score(
        supplier: Dict,
        required_quantity: int,
        price_score: float = 0.0,
        lead_time_score: float = 0.0
    ) -> Dict:

        # --------------------------------------------------------
        # Availability
        # --------------------------------------------------------

        available_to_promise = float(
            supplier.get(
                "available_to_promise",
                0
            ) or 0
        )


        if required_quantity > 0:

            availability_score = min(

                (
                    available_to_promise
                    /
                    required_quantity
                )
                * 100,

                100

            )

        else:

            availability_score = 100.0


        # --------------------------------------------------------
        # Fulfillment
        # --------------------------------------------------------

        if supplier.get(
            "can_fulfill",
            False
        ):

            fulfillment_score = 100.0

        else:

            fulfillment_score = (
                availability_score
            )


        # --------------------------------------------------------
        # Reliability
        # --------------------------------------------------------

        reliability_score = float(
            supplier.get(
                "reliability_score",
                0
            ) or 0
        )


        reliability_score = max(
            0.0,
            min(
                reliability_score,
                100.0
            )
        )


        # --------------------------------------------------------
        # Quality
        # --------------------------------------------------------

        defect_rate = float(
            supplier.get(
                "defect_rate",
                0
            ) or 0
        )


        defect_rate = max(
            0.0,
            defect_rate
        )


        quality_score = max(

            0.0,

            100.0 - defect_rate

        )


        quality_score = min(
            quality_score,
            100.0
        )


        # --------------------------------------------------------
        # AI Risk
        # --------------------------------------------------------

        ai_risk_score = (

            ProcurementDecisionService
            .calculate_risk_score(
                supplier
            )

        )


        # --------------------------------------------------------
        # Final Procurement Score
        # --------------------------------------------------------

        procurement_score = (

            (
                availability_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "availability"
                ]
            )

            +

            (
                fulfillment_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "fulfillment"
                ]
            )

            +

            (
                reliability_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "reliability"
                ]
            )

            +

            (
                quality_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "quality"
                ]
            )

            +

            (
                ai_risk_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "ai_risk"
                ]
            )

            +

            (
                price_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "price"
                ]
            )

            +

            (
                lead_time_score
                *
                ProcurementDecisionService
                .WEIGHTS[
                    "lead_time"
                ]
            )

        )


        return {

            "availability_score":
                round(
                    availability_score,
                    2
                ),

            "fulfillment_score":
                round(
                    fulfillment_score,
                    2
                ),

            "reliability_score":
                round(
                    reliability_score,
                    2
                ),

            "quality_score":
                round(
                    quality_score,
                    2
                ),

            "ai_risk_score":
                round(
                    ai_risk_score,
                    2
                ),

            "price_score":
                round(
                    price_score,
                    2
                ),

            "lead_time_score":
                round(
                    lead_time_score,
                    2
                ),

            "procurement_score":
                round(
                    procurement_score,
                    2
                )

        }


    # ============================================================
    # CALCULATE PRICE SCORES
    # ============================================================

    @staticmethod
    def calculate_price_scores(
        suppliers: List[Dict]
    ) -> Dict[int, float]:

        valid_prices = []


        for supplier in suppliers:

            price = supplier.get(
                "unit_price"
            )


            if price is None:

                continue


            try:

                price = float(price)

            except (
                TypeError,
                ValueError
            ):

                continue


            if price > 0:

                valid_prices.append(
                    price
                )


        if not valid_prices:

            return {

                supplier["supplier_id"]:
                    0.0

                for supplier in suppliers

            }


        minimum_price = min(
            valid_prices
        )


        price_scores = {}


        for supplier in suppliers:

            supplier_id = (
                supplier["supplier_id"]
            )


            price = supplier.get(
                "unit_price"
            )


            if price is None:

                price_scores[
                    supplier_id
                ] = 0.0

                continue


            try:

                price = float(price)

            except (
                TypeError,
                ValueError
            ):

                price_scores[
                    supplier_id
                ] = 0.0

                continue


            if price <= 0:

                price_scores[
                    supplier_id
                ] = 0.0

                continue


            score = (

                minimum_price
                /
                price

            ) * 100


            price_scores[
                supplier_id
            ] = round(

                min(
                    score,
                    100.0
                ),

                2

            )


        return price_scores


    # ============================================================
    # CALCULATE LEAD TIME SCORES
    # ============================================================

    @staticmethod
    def calculate_lead_time_scores(
        suppliers: List[Dict]
    ) -> Dict[int, float]:

        valid_lead_times = []


        for supplier in suppliers:

            lead_time = supplier.get(
                "standard_lead_time_days"
            )


            if lead_time is None:

                continue


            try:

                lead_time = int(
                    lead_time
                )

            except (
                TypeError,
                ValueError
            ):

                continue


            if lead_time >= 0:

                valid_lead_times.append(
                    lead_time
                )


        if not valid_lead_times:

            return {

                supplier["supplier_id"]:
                    0.0

                for supplier in suppliers

            }


        minimum_lead_time = min(
            valid_lead_times
        )


        lead_time_scores = {}


        for supplier in suppliers:

            supplier_id = (
                supplier["supplier_id"]
            )


            lead_time = supplier.get(
                "standard_lead_time_days"
            )


            if lead_time is None:

                lead_time_scores[
                    supplier_id
                ] = 0.0

                continue


            try:

                lead_time = int(
                    lead_time
                )

            except (
                TypeError,
                ValueError
            ):

                lead_time_scores[
                    supplier_id
                ] = 0.0

                continue


            if lead_time < 0:

                lead_time_scores[
                    supplier_id
                ] = 0.0

                continue


            if lead_time == 0:

                score = 100.0

            elif minimum_lead_time == 0:

                score = 0.0

            else:

                score = (

                    minimum_lead_time
                    /
                    lead_time

                ) * 100


            lead_time_scores[
                supplier_id
            ] = round(

                min(
                    score,
                    100.0
                ),

                2

            )


        return lead_time_scores


    # ============================================================
    # BUILD DECISION FACTORS
    # ============================================================

    @staticmethod
    def build_decision_factors(
        supplier: Dict,
        scores: Dict
    ) -> List[str]:

        factors = []


        # --------------------------------------------------------
        # Fulfillment
        # --------------------------------------------------------

        if supplier.get(
            "can_fulfill",
            False
        ):

            factors.append(
                "Can fulfill the required quantity"
            )

        else:

            factors.append(
                "Cannot fully fulfill the required quantity"
            )


        # --------------------------------------------------------
        # Reliability
        # --------------------------------------------------------

        if scores[
            "reliability_score"
        ] >= 90:

            factors.append(
                "High supplier reliability"
            )

        elif scores[
            "reliability_score"
        ] >= 75:

            factors.append(
                "Good supplier reliability"
            )

        else:

            factors.append(
                "Supplier reliability needs attention"
            )


        # --------------------------------------------------------
        # Quality
        # --------------------------------------------------------

        if scores[
            "quality_score"
        ] >= 98:

            factors.append(
                "Excellent quality performance"
            )

        elif scores[
            "quality_score"
        ] >= 95:

            factors.append(
                "Good quality performance"
            )

        else:

            factors.append(
                "Quality performance needs attention"
            )


        # --------------------------------------------------------
        # AI Risk
        # --------------------------------------------------------

        risk_level = str(
            supplier.get(
                "risk_level",
                "UNKNOWN"
            )
        ).upper()


        if risk_level == "LOW":

            factors.append(
                "AI predicts low supplier risk"
            )

        elif risk_level == "MEDIUM":

            factors.append(
                "AI predicts medium supplier risk"
            )

        elif risk_level == "HIGH":

            factors.append(
                "AI predicts high supplier risk"
            )

        else:

            factors.append(
                "AI risk prediction unavailable"
            )


        # --------------------------------------------------------
        # Price
        # --------------------------------------------------------

        if scores[
            "price_score"
        ] >= 90:

            factors.append(
                "Competitive unit price"
            )

        elif scores[
            "price_score"
        ] >= 70:

            factors.append(
                "Reasonable unit price"
            )

        else:

            factors.append(
                "Unit price is relatively high"
            )


        # --------------------------------------------------------
        # Lead Time
        # --------------------------------------------------------

        if scores[
            "lead_time_score"
        ] >= 90:

            factors.append(
                "Short lead time"
            )

        elif scores[
            "lead_time_score"
        ] >= 70:

            factors.append(
                "Acceptable lead time"
            )

        else:

            factors.append(
                "Longer lead time"
            )


        # --------------------------------------------------------
        # Approval
        # --------------------------------------------------------

        if not supplier.get(
            "is_approved",
            False
        ):

            factors.append(
                "Supplier is not approved"
            )


        return factors


    # ============================================================
    # RANK SUPPLIERS
    # ============================================================

    @staticmethod
    def rank_suppliers(
        suppliers: List[Dict],
        required_quantity: int
    ) -> List[Dict]:

        if not suppliers:

            return []


        # --------------------------------------------------------
        # Calculate comparison scores
        # --------------------------------------------------------

        price_scores = (

            ProcurementDecisionService
            .calculate_price_scores(
                suppliers
            )

        )


        lead_time_scores = (

            ProcurementDecisionService
            .calculate_lead_time_scores(
                suppliers
            )

        )


        ranked_suppliers = []


        for supplier in suppliers:

            supplier_id = (
                supplier["supplier_id"]
            )


            price_score = (
                price_scores.get(
                    supplier_id,
                    0.0
                )
            )


            lead_time_score = (
                lead_time_scores.get(
                    supplier_id,
                    0.0
                )
            )


            # ----------------------------------------------------
            # Calculate all scores
            # ----------------------------------------------------

            scores = (

                ProcurementDecisionService
                .calculate_score(

                    supplier,

                    required_quantity,

                    price_score,

                    lead_time_score

                )

            )


            # ----------------------------------------------------
            # Decision factors
            # ----------------------------------------------------

            decision_factors = (

                ProcurementDecisionService
                .build_decision_factors(

                    supplier,

                    scores

                )

            )


            # ----------------------------------------------------
            # Enriched supplier
            # ----------------------------------------------------

            enriched_supplier = {

                **supplier,

                "availability_score":
                    scores[
                        "availability_score"
                    ],

                "fulfillment_score":
                    scores[
                        "fulfillment_score"
                    ],

                "reliability_score":
                    scores[
                        "reliability_score"
                    ],

                "quality_score":
                    scores[
                        "quality_score"
                    ],

                "ai_risk_score":
                    scores[
                        "ai_risk_score"
                    ],

                "price_score":
                    scores[
                        "price_score"
                    ],

                "lead_time_score":
                    scores[
                        "lead_time_score"
                    ],

                "procurement_score":
                    scores[
                        "procurement_score"
                    ],

                "decision_factors":
                    decision_factors

            }


            ranked_suppliers.append(
                enriched_supplier
            )


        # --------------------------------------------------------
        # Rank suppliers
        #
        # 1. Approved suppliers
        # 2. Suppliers that can fulfill
        # 3. Highest procurement score
        # --------------------------------------------------------

        ranked_suppliers.sort(

            key=lambda supplier: (

                not supplier.get(
                    "is_approved",
                    False
                ),

                not supplier.get(
                    "can_fulfill",
                    False
                ),

                -supplier.get(
                    "procurement_score",
                    0
                )

            )

        )


        # --------------------------------------------------------
        # Assign ranking
        # --------------------------------------------------------

        for index, supplier in enumerate(

            ranked_suppliers,

            start=1

        ):

            supplier[
                "procurement_rank"
            ] = index


        return ranked_suppliers


    # ============================================================
    # GET RECOMMENDATION
    # ============================================================

    @staticmethod
    def get_recommendation(
        suppliers: List[Dict],
        required_quantity: int
    ) -> Dict:

        ranked_suppliers = (

            ProcurementDecisionService
            .rank_suppliers(

                suppliers,

                required_quantity

            )

        )


        if not ranked_suppliers:

            return {

                "recommended_supplier":
                    None,

                "suppliers":
                    []

            }


        recommended_supplier = (
            ranked_suppliers[0]
        )


        return {

            "recommended_supplier":
                recommended_supplier,

            "suppliers":
                ranked_suppliers,

            "decision_weights":
                ProcurementDecisionService
                .WEIGHTS

        }