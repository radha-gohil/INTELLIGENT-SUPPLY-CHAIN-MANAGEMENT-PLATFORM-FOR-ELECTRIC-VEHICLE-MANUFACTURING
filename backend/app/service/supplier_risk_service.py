from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from sqlalchemy.orm import Session

from backend.app.models import (
    Supplier
)

from backend.app.service.supplier_performance_service import (
    SupplierPerformanceService
)


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = (

    Path(
        __file__
    )

    .resolve()

    .parents[3]

)


# ============================================================
# MODEL PATHS
# ============================================================

MODEL_PATH = (

    PROJECT_ROOT

    /

    "backend"

    /

    "app"

    /

    "ml"

    /

    "models"

    /

    "supplier_risk_xgboost.pkl"

)


ENCODER_PATH = (

    PROJECT_ROOT

    /

    "backend"

    /

    "app"

    /

    "ml"

    /

    "models"

    /

    "supplier_risk_label_encoder.pkl"

)


# ============================================================
# AUTHORITATIVE FEATURE LIST
# ============================================================
#
# IMPORTANT:
#
# This MUST exactly match:
#
# train_supplier_risk_model.py
#
# ============================================================

FEATURE_COLUMNS = [

    "total_orders",

    "late_order_rate",

    "on_time_delivery_rate",

    "fill_rate",

    "average_delay_days",

    "quality_score",

    "baseline_reliability_score"

]


# ============================================================
# SUPPLIER RISK SERVICE
# ============================================================

class SupplierRiskService:


    # ========================================================
    # LOAD MODEL
    # ========================================================

    @staticmethod
    @lru_cache(
        maxsize=1
    )
    def load_model():

        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        if not MODEL_PATH.exists():

            raise FileNotFoundError(

                "Supplier risk XGBoost model "
                "not found: "
                +
                str(
                    MODEL_PATH
                )

            )


        # ----------------------------------------------------
        # Label encoder
        # ----------------------------------------------------

        if not ENCODER_PATH.exists():

            raise FileNotFoundError(

                "Supplier risk label encoder "
                "not found: "
                +
                str(
                    ENCODER_PATH
                )

            )


        model = joblib.load(
            MODEL_PATH
        )


        label_encoder = joblib.load(
            ENCODER_PATH
        )


        return (

            model,

            label_encoder

        )


    # ========================================================
    # GET SUPPLIER
    # ========================================================

    @staticmethod
    def get_supplier(

        db: Session,

        supplier_id: int

    ):

        supplier = (

            db.query(
                Supplier
            )

            .filter(

                Supplier.id
                ==
                supplier_id

            )

            .first()

        )


        if supplier is None:

            raise ValueError(
                "Supplier not found."
            )


        return supplier


    # ========================================================
    # BUILD LIVE XGBOOST FEATURES
    # ========================================================

    @staticmethod
    def build_features(
        performance: dict
    ):

        # ----------------------------------------------------
        # Model needs historical supplier performance.
        # ----------------------------------------------------

        if not performance.get(
            "performance_data_available"
        ):

            raise ValueError(

                "No supplier performance data "
                "available for AI risk prediction."

            )


        # ====================================================
        # TOTAL ORDERS
        # ====================================================

        total_orders = float(

            performance.get(
                "total_orders",
                0
            )

            or

            0

        )


        # ====================================================
        # LATE ORDERS
        # ====================================================

        late_orders = float(

            performance.get(
                "late_orders",
                0
            )

            or

            0

        )


        # ====================================================
        # LATE ORDER RATE
        # ====================================================

        if total_orders > 0:

            late_order_rate = (

                late_orders
                /
                total_orders

            ) * 100

        else:

            late_order_rate = 0.0


        late_order_rate = max(

            0.0,

            min(
                100.0,
                late_order_rate
            )

        )


        # ====================================================
        # BASELINE RELIABILITY
        # ====================================================

        baseline_reliability_score = (

            performance.get(
                "baseline_reliability_score"
            )

        )


        if baseline_reliability_score is None:

            baseline_reliability_score = 50.0


        # ====================================================
        # QUALITY
        # ====================================================

        quality_score = (

            performance.get(
                "quality_score"
            )

        )


        if quality_score is None:

            quality_score = 50.0


        # ====================================================
        # FEATURE ROW
        # ====================================================

        feature_row = {

            "total_orders":

                total_orders,


            "late_order_rate":

                late_order_rate,


            "on_time_delivery_rate":

                float(

                    performance.get(
                        "on_time_delivery_rate",
                        0
                    )

                    or

                    0

                ),


            "fill_rate":

                float(

                    performance.get(
                        "fill_rate",
                        0
                    )

                    or

                    0

                ),


            "average_delay_days":

                max(

                    0.0,

                    float(

                        performance.get(
                            "average_delay_days",
                            0
                        )

                        or

                        0

                    )

                ),


            "quality_score":

                float(
                    quality_score
                ),


            "baseline_reliability_score":

                float(
                    baseline_reliability_score
                )

        }


        # ====================================================
        # DATAFRAME
        #
        # Explicit column order prevents model mismatch.
        # ====================================================

        features = pd.DataFrame(

            [
                feature_row
            ],

            columns=(
                FEATURE_COLUMNS
            )

        )


        return features


    # ========================================================
    # VALIDATE MODEL FEATURES
    # ========================================================

    @staticmethod
    def validate_model_features(
        model
    ):

        # ----------------------------------------------------
        # sklearn-style feature list
        # ----------------------------------------------------

        model_features = getattr(

            model,

            "feature_names_in_",

            None

        )


        # ----------------------------------------------------
        # XGBoost booster feature list fallback
        # ----------------------------------------------------

        if model_features is None:

            try:

                model_features = (

                    model
                    .get_booster()
                    .feature_names

                )

            except Exception:

                model_features = None


        # ----------------------------------------------------
        # Older model formats may not expose feature names.
        # ----------------------------------------------------

        if model_features is None:

            return


        model_features = list(
            model_features
        )


        if (
            model_features
            !=
            FEATURE_COLUMNS
        ):

            raise ValueError(

                "XGBoost model feature mismatch. "

                "Regenerate the supplier risk dataset "
                "and retrain the model. "

                "Expected features: "

                +

                ", ".join(
                    FEATURE_COLUMNS
                )

            )


    # ========================================================
    # PREDICT SUPPLIER RISK
    # ========================================================

    @staticmethod
    def predict_supplier_risk(

        db: Session,

        supplier_id: int

    ):

        # ====================================================
        # SUPPLIER
        # ====================================================

        supplier = (

            SupplierRiskService
            .get_supplier(

                db,

                supplier_id

            )

        )


        # ====================================================
        # SINGLE SOURCE OF PERFORMANCE METRICS
        # ====================================================

        performance = (

            SupplierPerformanceService
            .calculate_supplier_performance(

                db,

                supplier_id

            )

        )


        # ====================================================
        # MODEL FEATURES
        # ====================================================

        features = (

            SupplierRiskService
            .build_features(
                performance
            )

        )


        # ====================================================
        # LOAD MODEL
        # ====================================================

        (
            model,

            label_encoder

        ) = (

            SupplierRiskService
            .load_model()

        )


        # ====================================================
        # FEATURE CONTRACT CHECK
        # ====================================================

        SupplierRiskService \
            .validate_model_features(
                model
            )


        # ====================================================
        # PREDICT CLASS
        # ====================================================

        prediction = model.predict(
            features
        )


        predicted_class = int(
            prediction[0]
        )


        # ====================================================
        # DECODE CLASS
        # ====================================================

        risk_level = str(

            label_encoder
            .inverse_transform(

                [
                    predicted_class
                ]

            )[0]

        )


        # ====================================================
        # CLASS PROBABILITIES
        # ====================================================

        probabilities = (

            model
            .predict_proba(
                features
            )[0]

        )


        risk_probabilities = {}


        for (
            index,
            label
        ) in enumerate(

            label_encoder.classes_

        ):

            risk_probabilities[
                str(
                    label
                )
            ] = round(

                float(

                    probabilities[
                        index
                    ]

                ),

                4

            )


        # ====================================================
        # CONFIDENCE
        # ====================================================

        confidence = round(

            float(

                max(
                    probabilities
                )

            ),

            4

        )


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "supplier_id":
                supplier.id,

            "supplier_code":
                supplier.supplier_code,

            "supplier_name":
                supplier.supplier_name,

            "risk_level":
                risk_level,

            "confidence":
                confidence,

            "risk_probabilities":
                risk_probabilities

        }