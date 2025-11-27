from flask import Flask, render_template
from ultralytics import YOLO
import os

app = Flask(__name__)

# -------------------------------
# 🔹 Run YOLO inference once on startup
# -------------------------------
model = YOLO("runs/detect/train10/weights/best.pt")

# Ensure results folder exists
results_folder = os.path.join("static", "results")
os.makedirs(results_folder, exist_ok=True)

# Run inference on validation/test images
results = model.predict(
    source="dataset/images/val",   # or wherever your pothole test images are
    conf=0.6,
    iou=0.5,
    save=True,
    project="static",              # save inside /static
    name="results",                # save inside /static/results
    exist_ok=True                  # overwrite if folder exists
)

# -------------------------------
# 🔹 Flask routes
# -------------------------------
@app.route('/')
def index():
    # Get all detected images
    image_files = os.listdir("static/results")
    image_files = [f"results/{img}" for img in image_files if img.endswith(('.jpg', '.png'))]
    return render_template("result.html", images=image_files)


if __name__ == "__main__":
    app.run(debug=True)
