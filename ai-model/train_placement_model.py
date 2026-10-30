"""
Training script for Placement Readiness Classification Model
Uses base-paper dataset: datasets/base-paper/student_placement_prediction_dataset_2026.csv
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import joblib

DATASET_PATH = "datasets/base-paper/student_placement_prediction_dataset_2026.csv"
MODEL_DIR = "ai-model/models"
MODEL_PATH = os.path.join(MODEL_DIR, "placement_classifier.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

def train_and_evaluate():
    print(f"Loading dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # Define feature set relevant to student profile
    feature_cols = [
        "cgpa",
        "internships_count",
        "projects_count",
        "certifications_count",
        "coding_skill_score",
        "aptitude_score",
        "communication_skill_score",
        "mock_interview_score",
        "backlogs"
    ]

    # Clean and parse numerical features
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Encode target: 'Placed' -> 1, others -> 0
    target_col = "placement_status"
    y = (df[target_col].str.strip().str.lower() == "placed").astype(int)
    X = df[feature_cols]

    print(f"Features: {feature_cols}")
    print(f"Class distribution: Placed = {y.sum()}, Not Placed = {(y == 0).sum()} ({y.mean()*100:.1f}% positive)")

    # 80/20 train/test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training set: {X_train.shape[0]}, Test set: {X_test.shape[0]}")

    # Train Random Forest with balanced settings
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )

    clf.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n================ MODEL EVALUATION ================")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print("Confusion Matrix:")
    print(f"  [TN={cm[0][0]}, FP={cm[0][1]}]")
    print(f"  [FN={cm[1][0]}, TP={cm[1][1]}]")
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=["Not Placed", "Placed"]))

    # Feature importances
    importances = dict(zip(feature_cols, clf.feature_importances_.round(4).tolist()))
    print("Feature Importances:")
    for f, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {f}: {imp * 100:.2f}%")

    # Save model artifact
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"\nModel saved successfully to {MODEL_PATH}")

    # Save metadata
    metadata = {
        "model_name": "RandomForest_Placement_Classifier",
        "version": "1.0-basepaper",
        "dataset_rows": int(df.shape[0]),
        "features": feature_cols,
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "confusion_matrix": cm
        },
        "feature_importances": importances
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata saved to {METADATA_PATH}")

if __name__ == "__main__":
    train_and_evaluate()
