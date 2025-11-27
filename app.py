import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image;
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from ultralytics import YOLO
import sqlite3

# Import database functions
from database import init_db, insert_detection, get_detections

# Flask setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['RESULT_FOLDER'] = 'static/results/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# ✅ YOLO model
model = YOLO("runs/detect/train27/weights/best.pt")

# ✅ Initialize the database at startup
init_db()


# ✅ Extract GPS metadata
def extract_gps(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return None, None, None, False  # Added boolean for 'is_real'

        gps_data = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag)
            if tag_name == "GPSInfo":
                for t in value:
                    sub_tag = GPSTAGS.get(t)
                    gps_data[sub_tag] = value[t]

        if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
            lat = gps_data["GPSLatitude"]
            lon = gps_data["GPSLongitude"]

            def convert_to_degrees(value):
                d = float(value[0][0]) / float(value[0][1])
                m = float(value[1][0]) / float(value[1][1])
                s = float(value[2][0]) / float(value[2][1])
                return d + (m / 60.0) + (s / 3600.0)

            latitude = convert_to_degrees(lat)
            longitude = convert_to_degrees(lon)

            if gps_data.get("GPSLatitudeRef") == "S":
                latitude = -latitude
            if gps_data.get("GPSLongitudeRef") == "W":
                longitude = -longitude

            timestamp = exif_data.get(36867, "Unknown")
            return latitude, longitude, timestamp, True  # Return True for real GPS

        return None, None, None, False
    except Exception as e:
        print("GPS extraction error:", e)
        return None, None, None, False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        results = model(filepath)
        output_path = os.path.join(app.config["RESULT_FOLDER"], filename)
        results[0].save(filename=output_path)

        detections = []
        for r in results[0].boxes:
            conf = round(float(r.conf[0]) * 100, 2)
            label = model.names[int(r.cls[0])]
            detections.append({"label": label, "conf": conf})

        # ✅ Extract GPS metadata and determine if it's real
        lat, lon, timestamp, is_real_gps = extract_gps(filepath)
        is_dummy_flag = 1 if not is_real_gps else 0

        # ✅ Handle missing GPS → set dummy location
        if not lat or not lon:
            lat, lon = 18.5204, 73.8567
            timestamp = "No GPS metadata – using dummy location"

        # ✅ Insert detection into the database
        if detections:  # Only log if potholes are detected
            insert_detection(filepath, lat, lon, is_dummy_flag)

        return render_template(
            "result.html",
            filename=filename,
            detections=detections,
            latitude=lat,
            longitude=lon,
            timestamp=timestamp
        )

    return render_template("index.html")


# ✅ New route for viewing history
@app.route("/history")
def history():
    records = get_detections()
    return render_template("history.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)