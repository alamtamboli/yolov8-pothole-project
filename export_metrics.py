from ultralytics import YOLO
import pandas as pd
import numpy as np

# Load model - adjust the path to your best.pt
model = YOLO("runs/detect/train10/weights/best.pt")

# Run validation
metrics = model.val()

# --- 1. Extract main metrics ---
results_dict = {
    "precision": metrics.results_dict.get("metrics/precision(B)", None),
    "recall": metrics.results_dict.get("metrics/recall(B)", None),
    "f1_score": metrics.results_dict.get("metrics/f1(B)", None),
    "mAP50": metrics.results_dict.get("metrics/mAP50(B)", None),
    "mAP50-95": metrics.results_dict.get("metrics/mAP50-95(B)", None),
}

df_metrics = pd.DataFrame([results_dict])

# --- 2. Extract confusion matrix ---
# metrics.confusion_matrix.matrix is numpy array (rows=true, cols=pred)
cm = metrics.confusion_matrix.matrix
cm_df = pd.DataFrame(cm)

# Save to Excel with 2 sheets
with pd.ExcelWriter("final_metrics.xlsx") as writer:
    df_metrics.to_excel(writer, sheet_name="Main Metrics", index=False)
    cm_df.to_excel(writer, sheet_name="Confusion Matrix", index=False)

print("✅ Metrics and confusion matrix exported to final_metrics.xlsx")
