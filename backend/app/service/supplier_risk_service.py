import os
import joblib
import pandas as pd

from sqlalchemy.orm import Session

from backend.app.models import (
    Supplier,
    SupplierPerformance
)


# ============================================================
# MODEL PATHS
# ============================================================

MODEL_PATH = (
    "backend/app/ml/models/supplier_risk_xgboost.pkl"
)

ENCODER_PATH = (
    "backend/app/ml/models/supplier_risk_label_encoder.pkl"
)


# ============================================================
# SUPPLIER RISK SERVICE
# ============================================================

class SupplierRiskService:

    # ========================================================
    # LOAD MODEL
    # ========================================================

    @staticmethod
    def load_model():

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                "Supplier risk XGBoost model not found."
            )

        if not os.path.exists(ENCODER_PATH):

            raise FileNotFoundError(
                "Supplier risk label encoder not found."
            )

        model = joblib.load(
            MODEL_PATH
        )

        label_encoder = joblib.load(
            ENCODER_PATH
        )

        return model, label_encoder


    # ========================================================
    # GET SUPPLIER
    # ========================================================

    @staticmethod
    def get_supplier(
        db: Session,
        supplier_id: int
    ):

        supplier = (

            db.query(Supplier)

            .filter(
                Supplier.id == supplier_id
            )

            .first()

        )

        if supplier is None:

            raise ValueError(
                "Supplier not found."
            )

        return supplier


    # ========================================================
    # GET SUPPLIER PERFORMANCE
    # ========================================================

    @staticmethod
    def get_supplier_performance(
        db: Session,
        supplier_id: int
    ):

        records = (

            db.query(SupplierPerformance)

            .filter(

                SupplierPerformance.supplier_id
                == supplier_id

            )

            .all()

        )

        if not records:

            raise ValueError(
                "No supplier performance data available."
            )

        return records


    # ========================================================
    # BUILD ML FEATURES
    # ========================================================

    @staticmethod
    def build_features(
        records
    ):

        # ----------------------------------------------------
        # Aggregate historical supplier data
        # ----------------------------------------------------

        total_orders = sum(

            record.total_orders

            for record in records

        )


        on_time_orders = sum(

            record.on_time_orders

            for record in records

        )


        late_orders = sum(

            record.late_orders

            for record in records

        )


        ordered_quantity = sum(

            record.ordered_quantity

            for record in records

        )


        received_quantity = sum(

            record.received_quantity

            for record in records

        )


        defective_quantity = sum(

            record.defective_quantity

            for record in records

        )


        # ----------------------------------------------------
        # Average delay
        # ----------------------------------------------------

        total_delay = sum(

            record.average_delay_days
            * record.late_orders

            for record in records

        )


        if late_orders > 0:

            average_delay_days = (

                total_delay
                /
                late_orders

            )

        else:

            average_delay_days = 0.0


        # ----------------------------------------------------
        # On-time delivery rate
        # ----------------------------------------------------

        if total_orders > 0:

            on_time_delivery_rate = (

                on_time_orders
                /
                total_orders

            ) * 100

        else:

            on_time_delivery_rate = 0.0


        # ----------------------------------------------------
        # Fill rate
        # ----------------------------------------------------

        if ordered_quantity > 0:

            fill_rate = (

                received_quantity
                /
                ordered_quantity

            ) * 100

        else:

            fill_rate = 0.0


        # ----------------------------------------------------
        # Defect rate
        # ----------------------------------------------------

        if received_quantity > 0:

            defect_rate = (

                defective_quantity
                /
                received_quantity

            ) * 100

        else:

            defect_rate = 0.0


        # ----------------------------------------------------
        # Create DataFrame
        #
        # IMPORTANT:
        # Column order must match training.
        # ----------------------------------------------------

        features = pd.DataFrame([{

            "total_orders":
                total_orders,

            "on_time_orders":
                on_time_orders,

            "late_orders":
                late_orders,

            "ordered_quantity":
                ordered_quantity,

            "received_quantity":
                received_quantity,

            "defective_quantity":
                defective_quantity,

            "on_time_delivery_rate":
                on_time_delivery_rate,

            "fill_rate":
                fill_rate,

            "defect_rate":
                defect_rate,

            "average_delay_days":
                average_delay_days

        }])


        return features


    # ========================================================
    # PREDICT SUPPLIER RISK
    # ========================================================

    @staticmethod
    def predict_supplier_risk(
        db: Session,
        supplier_id: int
    ):

        # ----------------------------------------------------
        # Get supplier
        # ----------------------------------------------------

        supplier = (

            SupplierRiskService
            .get_supplier(

                db,

                supplier_id

            )

        )


        # ----------------------------------------------------
        # Get performance
        # ----------------------------------------------------

        records = (

            SupplierRiskService
            .get_supplier_performance(

                db,

                supplier_id

            )

        )


        # ----------------------------------------------------
        # Build features
        # ----------------------------------------------------

        features = (

            SupplierRiskService
            .build_features(

                records

            )

        )


        # ----------------------------------------------------
        # Load trained model
        # ----------------------------------------------------

        model, label_encoder = (

            SupplierRiskService
            .load_model()

        )


        # ----------------------------------------------------
        # Predict class
        # ----------------------------------------------------

        prediction = model.predict(
            features
        )


        predicted_class = int(
            prediction[0]
        )


        risk_level = (

            label_encoder
            .inverse_transform(
                [predicted_class]
            )[0]

        )


        # ----------------------------------------------------
        # Prediction probabilities
        # ----------------------------------------------------

        probabilities = (

            model
            .predict_proba(
                features
            )[0]

        )


        # ----------------------------------------------------
        # Build probability dictionary
        # ----------------------------------------------------

        risk_probabilities = {}


        for index, label in enumerate(

            label_encoder.classes_

        ):

            risk_probabilities[label] = round(

                float(
                    probabilities[index]
                ),

                4

            )


        # ----------------------------------------------------
        # Highest probability
        # ----------------------------------------------------

        confidence = round(

            float(
                max(probabilities)
            ),

            4

        )


        # ----------------------------------------------------
        # Return prediction
        # ----------------------------------------------------

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