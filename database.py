import sqlite3
import os

DB_NAME = "potholes.db"


def init_db():
    """Initialize database and create table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            is_dummy INTEGER DEFAULT 1,   -- ✅ 1 = dummy GPS, 0 = real GPS
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # ✅ Ensure "is_dummy" column exists (for old databases)
    cursor.execute("PRAGMA table_info(detections)")
    columns = [col[1] for col in cursor.fetchall()]
    if "is_dummy" not in columns:
        cursor.execute("ALTER TABLE detections ADD COLUMN is_dummy INTEGER DEFAULT 1")
        conn.commit()

    conn.close()


def insert_detection(image_path, latitude, longitude, is_dummy=1):
    """Insert new pothole detection with GPS coordinates and flag."""
    # ✅ Always store only filename (not full path)
    filename_only = os.path.basename(image_path)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO detections (image_path, latitude, longitude, is_dummy) VALUES (?, ?, ?, ?)",
        (filename_only, latitude, longitude, is_dummy)
    )
    conn.commit()
    conn.close()


def get_detections():
    """Fetch all detections as list of dicts (latest first)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # ✅ return rows as dict-like objects
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    # ✅ Convert sqlite Row objects into plain dicts and clean filename
    detections = []
    for row in rows:
        row_dict = dict(row)
        row_dict["image_path"] = os.path.basename(row_dict["image_path"])
        detections.append(row_dict)

    return detections
