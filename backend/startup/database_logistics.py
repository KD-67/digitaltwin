# Checks if the SQLite database exists and has all required tables. If yes - move on, if no - create it. 

import sqlite3
import os
import json

def init_db (db_path: str) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True) # safe to call even if dir already exists
    with get_connection(db_path) as conn: # connect to (or create) db file
       # Table 1: Subjects
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id          INTEGER PRIMARY KEY,
                subject_id  TEXT UNIQUE,
                last_name   TEXT,
                first_name  TEXT,
                sex         TEXT,
                dob         TEXT,
                email       TEXT,
                phone       TEXT,
                notes       TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Table 2: Markers
        conn.execute("""
            CREATE TABLE IF NOT EXISTS markers (
                id               INTEGER PRIMARY KEY,
                marker_id        TEXT UNIQUE,
                marker_name      TEXT,
                description      TEXT,
                unit             TEXT,
                volatility_class TEXT,
                created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
# Opens connection to the SQLite db defined at db_path. sqlite.row makes columns accessible by name, not just by index position
def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Scans all subject directories and upserts individual profile data into the subjects table of asHDT.db
def sync_subjects(db_path: str, rawdata_root: str):
    import logging
    os.makedirs(rawdata_root, exist_ok=True)
    live_ids = set()

    with get_connection(db_path) as conn:
        for entry in os.listdir(rawdata_root):
            if entry == "deleted_subjects":
                continue
            profile_path = os.path.join(rawdata_root, entry, "profile.json")
            if not os.path.isfile(profile_path):
                logging.warning(f"sync_subjects: no profile.json in {entry}, skipping")
                continue
            with open(profile_path, "r") as f:
                p = json.load(f)
            subject_id = p.get("subject_id")
            if subject_id:
                live_ids.add(subject_id)
            conn.execute(
                """
                INSERT INTO subjects (subject_id, first_name, last_name, sex, dob, email, phone, notes, created_at)
                VALUES (:subject_id, :first_name, :last_name, :sex, :dob, :email, :phone, :notes, :created_at)
                ON CONFLICT(subject_id) DO UPDATE SET
                    first_name = excluded.first_name,
                    last_name  = excluded.last_name,
                    sex        = excluded.sex,
                    dob        = excluded.dob,
                    email      = excluded.email,
                    phone      = excluded.phone,
                    notes      = excluded.notes
                """,
                {
                    "subject_id": subject_id,
                    "first_name": p.get("first_name"),
                    "last_name":  p.get("last_name"),
                    "sex":        p.get("sex"),
                    "dob":        p.get("dob"),
                    "email":      p.get("email"),
                    "phone":      p.get("phone"),
                    "notes":      p.get("notes"),
                    "created_at": p.get("created_at", ""),
                },
            )

        # Remove rows whose folders no longer exist
        rows = conn.execute("SELECT subject_id FROM subjects").fetchall()
        for row in rows:
            if row["subject_id"] not in live_ids:
                conn.execute("DELETE FROM subjects WHERE subject_id = ?", (row["subject_id"],))

        conn.commit()


# Reads marker_list.json and upserts each marker into the markers table
def sync_markers(db_path: str, utilities_root: str):
    os.makedirs(utilities_root, exist_ok=True)
    marker_list_path = os.path.join(utilities_root, "marker_list.json")
    if not os.path.isfile(marker_list_path):
        return

    with open(marker_list_path, "r") as f:
        markers = json.load(f)

    live_ids = set()
    with get_connection(db_path) as conn:
        for p in markers:
            marker_id = p.get("marker_id")
            if not marker_id:
                continue
            live_ids.add(marker_id)
            conn.execute(
                """
                INSERT INTO markers (marker_id, marker_name, description, unit, volatility_class, created_at)
                VALUES (:marker_id, :marker_name, :description, :unit, :volatility_class, :created_at)
                ON CONFLICT(marker_id) DO UPDATE SET
                    marker_name      = excluded.marker_name,
                    description      = excluded.description,
                    unit             = excluded.unit,
                    volatility_class = excluded.volatility_class
                """,
                {
                    "marker_id":        marker_id,
                    "marker_name":      p.get("marker_name"),
                    "description":      p.get("description"),
                    "unit":             p.get("unit"),
                    "volatility_class": p.get("volatility_class"),
                    "created_at":       p.get("created_at", ""),
                },
            )

        # Remove rows no longer present in marker_list.json
        rows = conn.execute("SELECT marker_id FROM markers").fetchall()
        for row in rows:
            if row["marker_id"] not in live_ids:
                conn.execute("DELETE FROM markers WHERE marker_id = ?", (row["marker_id"],))

        conn.commit()