import os
import joblib

import numpy as np
import pandas as pd

from xgboost import XGBClassifier

from sklearn.model_selection import (
    train_test_split
)

from sklearn.preprocessing import (
    LabelEncoder
)

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


MODEL_DIR = (
    "backend/app/ml/models"
)


MODEL_PATH = os.path.join(
    MODEL_DIR,
    "supplier_risk_xgboost.pkl"
)


ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "supplier_risk_label_encoder.pkl"
)


# ============================================================
# AUTHORITATIVE FEATURES
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

    print(
        "\nLoading supplier risk dataset..."
    )


    if not os.path.exists(
        DATASET_PATH
    ):

        raise FileNotFoundError(

            "Supplier risk training dataset "
            "not found: "
            +
            DATASET_PATH

        )


    df = pd.read_csv(
        DATASET_PATH
    )


    print(
        f"Dataset shape: {df.shape}"
    )


    return df


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(
    df
):

    print(
        "\nPreparing features..."
    )


    required_columns = (

        FEATURE_COLUMNS

        +

        [
            "risk_level"
        ]

    )


    # --------------------------------------------------------
    # Validate required columns
    # --------------------------------------------------------

    missing_columns = [

        column

        for column
        in required_columns

        if column
        not in df.columns

    ]


    if missing_columns:

        raise ValueError(

            "Training dataset is missing "
            "required columns: "
            +
            ", ".join(
                missing_columns
            )

        )


    # ========================================================
    # FEATURES
    # ========================================================

    X = df[
        FEATURE_COLUMNS
    ].copy()


    for column in FEATURE_COLUMNS:

        X[
            column
        ] = pd.to_numeric(

            X[
                column
            ],

            errors="coerce"

        )


    # ========================================================
    # TARGET
    # ========================================================

    y = (

        df[
            "risk_level"
        ]

        .astype(
            str
        )

        .str
        .strip()

        .str
        .upper()

    )


    # ========================================================
    # REMOVE INVALID ROWS
    # ========================================================

    valid_mask = (

        X.notna()
        .all(
            axis=1
        )

        &

        y.notna()

        &

        (
            y != ""
        )

    )


    X = (

        X.loc[
            valid_mask
        ]

        .reset_index(
            drop=True
        )

    )


    y = (

        y.loc[
            valid_mask
        ]

        .reset_index(
            drop=True
        )

    )


    if X.empty:

        raise ValueError(
            "No valid training rows available."
        )


    # ========================================================
    # LABEL ENCODER
    # ========================================================

    label_encoder = (
        LabelEncoder()
    )


    y_encoded = (

        label_encoder
        .fit_transform(
            y
        )

    )


    print(
        "\nRisk label encoding:"
    )


    for (
        index,
        label
    ) in enumerate(

        label_encoder.classes_

    ):

        print(
            f"{label} -> {index}"
        )


    number_of_classes = len(
        label_encoder.classes_
    )


    if number_of_classes < 2:

        raise ValueError(

            "At least two risk classes "
            "are required for training."

        )


    if number_of_classes == 2:

        print(
            "\nBinary risk classification detected."
        )

    else:

        print(

            "\nMulticlass risk classification detected: "
            f"{number_of_classes} classes."

        )


    return (

        X,

        y_encoded,

        label_encoder

    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_dataset(
    X,
    y_encoded
):

    class_counts = (

        pd.Series(
            y_encoded
        )

        .value_counts()

    )


    print(
        "\nEncoded class distribution:"
    )


    print(
        class_counts
    )


    can_stratify = bool(

        (
            class_counts
            >=
            2
        )

        .all()

    )


    if can_stratify:

        stratify_value = (
            y_encoded
        )

    else:

        stratify_value = None


        print(

            "\nWARNING: Stratified split disabled "
            "because one or more classes contain "
            "fewer than two records."

        )


    return train_test_split(

        X,

        y_encoded,

        test_size=0.20,

        random_state=42,

        stratify=(
            stratify_value
        )

    )


# ============================================================
# SAMPLE WEIGHTS
# ============================================================

def calculate_sample_weights(
    y_train
):

    print(
        "\nCalculating class weights..."
    )


    class_counts = (

        pd.Series(
            y_train
        )

        .value_counts()

    )


    total_samples = len(
        y_train
    )


    number_of_classes = len(
        class_counts
    )


    class_weights = {}


    for (
        class_id,
        count
    ) in class_counts.items():

        class_weights[
            class_id
        ] = (

            total_samples

            /

            (
                number_of_classes
                *
                count
            )

        )


    for (
        class_id,
        weight
    ) in class_weights.items():

        print(

            f"Class {class_id}: "
            f"{weight:.4f}"

        )


    sample_weights = (

        pd.Series(
            y_train
        )

        .map(
            class_weights
        )

        .values

    )


    return sample_weights


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(

    X_train,

    y_train,

    sample_weights,

    number_of_classes

):

    print(
        "\nTraining XGBoost model..."
    )


    # ========================================================
    # BINARY CLASSIFICATION
    # ========================================================

    if number_of_classes == 2:

        print(
            "Using objective: binary:logistic"
        )


        model = XGBClassifier(

            objective="binary:logistic",

            n_estimators=250,

            max_depth=5,

            learning_rate=0.05,

            subsample=0.85,

            colsample_bytree=0.85,

            min_child_weight=2,

            reg_alpha=0.1,

            reg_lambda=1.0,

            eval_metric="logloss",

            random_state=42,

            n_jobs=-1

        )


    # ========================================================
    # MULTICLASS CLASSIFICATION
    # ========================================================

    else:

        print(
            "Using objective: multi:softprob"
        )


        model = XGBClassifier(

            objective="multi:softprob",

            num_class=(
                number_of_classes
            ),

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


    # ========================================================
    # FIT
    # ========================================================

    model.fit(

        X_train,

        y_train,

        sample_weight=(
            sample_weights
        )

    )


    print(
        "XGBoost training completed."
    )


    return model


# ============================================================
# NORMALIZE PREDICTIONS
# ============================================================

def normalize_predictions(
    predictions
):

    predictions = np.asarray(
        predictions
    )


    # --------------------------------------------------------
    # Correct expected case:
    #
    # [0, 1, 0, 1, ...]
    # --------------------------------------------------------

    if predictions.ndim == 1:

        return predictions.astype(
            int
        )


    # --------------------------------------------------------
    # Defensive fallback if model returns probabilities /
    # indicator matrix.
    # --------------------------------------------------------

    if predictions.ndim == 2:

        if predictions.shape[1] == 1:

            return (

                predictions
                .reshape(
                    -1
                )

                >=
                0.5

            ).astype(
                int
            )


        return np.argmax(

            predictions,

            axis=1

        ).astype(
            int
        )


    raise ValueError(

        "Unexpected XGBoost prediction "
        f"shape: {predictions.shape}"

    )


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


    # ========================================================
    # PREDICTIONS
    # ========================================================

    raw_predictions = model.predict(
        X_test
    )


    print(

        "Raw prediction shape:",
        np.asarray(
            raw_predictions
        ).shape

    )


    y_pred = normalize_predictions(
        raw_predictions
    )


    y_test = np.asarray(
        y_test
    ).astype(
        int
    )


    print(
        "y_test shape:",
        y_test.shape
    )


    print(
        "y_pred shape:",
        y_pred.shape
    )


    # ========================================================
    # ACCURACY
    # ========================================================

    accuracy = accuracy_score(

        y_test,

        y_pred

    )


    print(

        f"\nAccuracy: "
        f"{accuracy:.4f}"

    )


    labels = list(

        range(

            len(
                label_encoder.classes_
            )

        )

    )


    # ========================================================
    # CLASSIFICATION REPORT
    # ========================================================

    print(
        "\nClassification Report:"
    )


    print(

        classification_report(

            y_test,

            y_pred,

            labels=labels,

            target_names=(
                label_encoder.classes_
            ),

            zero_division=0

        )

    )


    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    print(
        "\nConfusion Matrix:"
    )


    cm = confusion_matrix(

        y_test,

        y_pred,

        labels=labels

    )


    print(
        cm
    )


    return accuracy


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def show_feature_importance(
    model
):

    importance_df = pd.DataFrame({

        "feature":
            FEATURE_COLUMNS,

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
        "\nFeature Importance:"
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

    print(
        "=" * 70
    )


    print(
        "SUPPLIER RISK XGBOOST TRAINING"
    )


    print(
        "=" * 70
    )


    # ========================================================
    # LOAD
    # ========================================================

    df = load_dataset()


    print(
        "\nRisk distribution:"
    )


    print(

        df[
            "risk_level"
        ]

        .value_counts()

    )


    # ========================================================
    # PREPARE
    # ========================================================

    (
        X,

        y_encoded,

        label_encoder

    ) = prepare_data(
        df
    )


    number_of_classes = len(
        label_encoder.classes_
    )


    # ========================================================
    # SPLIT
    # ========================================================

    (
        X_train,

        X_test,

        y_train,

        y_test

    ) = split_dataset(

        X,

        y_encoded

    )


    print(

        f"\nTraining samples: "
        f"{len(X_train)}"

    )


    print(

        f"Testing samples: "
        f"{len(X_test)}"

    )


    # ========================================================
    # WEIGHTS
    # ========================================================

    sample_weights = (

        calculate_sample_weights(
            y_train
        )

    )


    # ========================================================
    # TRAIN
    # ========================================================

    model = train_model(

        X_train,

        y_train,

        sample_weights,

        number_of_classes

    )


    # ========================================================
    # EVALUATE
    # ========================================================

    accuracy = evaluate_model(

        model,

        X_test,

        y_test,

        label_encoder

    )


    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    show_feature_importance(
        model
    )


    # ========================================================
    # SAVE
    # ========================================================

    save_model(

        model,

        label_encoder

    )


    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )


    print(
        "MODEL TRAINING COMPLETED"
    )


    print(
        "=" * 70
    )


    print(

        f"Accuracy: "
        f"{accuracy:.4f}"

    )


    print(

        f"Number of classes: "
        f"{number_of_classes}"

    )


    print(

        "Classes: "

        +

        ", ".join(
            label_encoder.classes_
        )

    )


    print(

        f"Features used: "
        f"{len(FEATURE_COLUMNS)}"

    )


    print(

        "Feature names: "

        +

        ", ".join(
            FEATURE_COLUMNS
        )

    )


    if (
        "LOW"
        not in
        label_encoder.classes_
    ):

        print(
            "\nWARNING:"
        )

        print(

            "No LOW-risk samples exist in "
            "the current training dataset."

        )

        print(

            "The trained model will therefore "
            "predict only the risk classes "
            "present in the data."

        )


    print(
        "=" * 70
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()