import os
import joblib

import pandas as pd

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = (
    "data/ml/supplier_risk_training_dataset.csv"
)

MODEL_DIR = "backend/app/ml/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "supplier_risk_xgboost.pkl"
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "supplier_risk_label_encoder.pkl"
)


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("\nLoading supplier risk dataset...")

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    return df


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_data(df):

    print("\nPreparing features...")


    # --------------------------------------------------------
    # Features used by XGBoost
    # --------------------------------------------------------

    feature_columns = [

        "total_orders",

        "on_time_orders",

        "late_orders",

        "ordered_quantity",

        "received_quantity",

        "defective_quantity",

        "on_time_delivery_rate",

        "fill_rate",

        "defect_rate",

        "average_delay_days"

    ]


    X = df[
        feature_columns
    ].copy()


    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    y = df[
        "risk_level"
    ].copy()


    # --------------------------------------------------------
    # Encode target
    #
    # LOW / MEDIUM / HIGH
    # --------------------------------------------------------

    label_encoder = LabelEncoder()

    y_encoded = label_encoder.fit_transform(
        y
    )


    print("\nRisk label encoding:")

    for index, label in enumerate(
        label_encoder.classes_
    ):

        print(
            f"{label} -> {index}"
        )


    return (
        X,
        y_encoded,
        label_encoder,
        feature_columns
    )


# ============================================================
# CALCULATE SAMPLE WEIGHTS
# ============================================================

def calculate_sample_weights(
    y_train
):

    print(
        "\nCalculating class weights..."
    )


    # --------------------------------------------------------
    # Count each class
    # --------------------------------------------------------

    class_counts = pd.Series(
        y_train
    ).value_counts()


    total_samples = len(
        y_train
    )


    number_of_classes = len(
        class_counts
    )


    class_weights = {}


    # --------------------------------------------------------
    # Balanced class weight formula
    # --------------------------------------------------------

    for class_id, count in class_counts.items():

        class_weights[class_id] = (

            total_samples
            /
            (
                number_of_classes
                * count
            )

        )


    print(
        "Class weights:"
    )

    for class_id, weight in class_weights.items():

        print(
            f"Class {class_id}: "
            f"{weight:.4f}"
        )


    # --------------------------------------------------------
    # Convert class weights into sample weights
    # --------------------------------------------------------

    sample_weights = pd.Series(
        y_train
    ).map(
        class_weights
    ).values


    return sample_weights


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(
    X_train,
    y_train,
    sample_weights
):

    print(
        "\nTraining XGBoost model..."
    )


    model = XGBClassifier(

        objective="multi:softprob",

        num_class=3,

        n_estimators=250,

        max_depth=5,

        learning_rate=0.05,

        subsample=0.85,

        colsample_bytree=0.85,

        min_child_weight=2,

        reg_alpha=0.1,

        reg_lambda=1.0,

        eval_metric="mlogloss",

        random_state=42,

        n_jobs=-1

    )


    model.fit(

        X_train,

        y_train,

        sample_weight=sample_weights

    )


    print(
        "XGBoost training completed."
    )


    return model


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(
    model,
    X_test,
    y_test,
    label_encoder
):

    print(
        "\nEvaluating model..."
    )


    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    y_pred = model.predict(
        X_test
    )


    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )


    print(
        f"\nAccuracy: "
        f"{accuracy:.4f}"
    )


    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    print(
        "\nClassification Report:"
    )


    print(
        classification_report(

            y_test,

            y_pred,

            labels=list(
                range(
                    len(
                        label_encoder.classes_
                    )
                )
            ),

            target_names=(
                label_encoder.classes_
            ),

            zero_division=0

        )
    )


    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(

        y_test,

        y_pred,

        labels=list(
            range(
                len(
                    label_encoder.classes_
                )
            )
        )

    )


    print(
        "\nConfusion Matrix:"
    )

    print(
        cm
    )


    return accuracy


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def show_feature_importance(
    model,
    feature_columns
):

    print(
        "\nFeature Importance:"
    )


    importance_df = pd.DataFrame({

        "feature":
            feature_columns,

        "importance":
            model.feature_importances_

    })


    importance_df = (
        importance_df
        .sort_values(
            by="importance",
            ascending=False
        )
    )


    print(
        importance_df
        .to_string(
            index=False
        )
    )


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model,
    label_encoder
):

    print(
        "\nSaving trained model..."
    )


    joblib.dump(

        model,

        MODEL_PATH

    )


    joblib.dump(

        label_encoder,

        ENCODER_PATH

    )


    print(
        f"Model saved to:\n"
        f"{MODEL_PATH}"
    )


    print(
        f"Label encoder saved to:\n"
        f"{ENCODER_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "SUPPLIER RISK XGBOOST TRAINING"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_dataset()


    # --------------------------------------------------------
    # Display target distribution
    # --------------------------------------------------------

    print(
        "\nOriginal risk distribution:"
    )

    print(
        df["risk_level"]
        .value_counts()
    )


    # --------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------

    (
        X,
        y,
        label_encoder,
        feature_columns

    ) = prepare_data(
        df
    )


    # --------------------------------------------------------
    # Train/test split
    #
    # Stratify maintains class proportions.
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test

    ) = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y

    )


    print(
        "\nTraining samples:",
        len(X_train)
    )

    print(
        "Testing samples:",
        len(X_test)
    )


    # --------------------------------------------------------
    # Calculate sample weights
    # --------------------------------------------------------

    sample_weights = (
        calculate_sample_weights(
            y_train
        )
    )


    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model = train_model(

        X_train,

        y_train,

        sample_weights

    )


    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    accuracy = evaluate_model(

        model,

        X_test,

        y_test,

        label_encoder

    )


    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    show_feature_importance(

        model,

        feature_columns

    )


    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    save_model(

        model,

        label_encoder

    )


    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "MODEL TRAINING COMPLETED"
    )

    print("=" * 70)

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print(
        f"Features used: {len(feature_columns)}"
    )

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()