import csv
import os
from datetime import datetime, timezone
from typing import List, Optional
import strawberry
from strawberry.types import Info

from backend.startup.database_logistics import get_connection


# ── Helpers ───────────────────────────────────────────────────────────────────

_CSV_FIELDS = ["measured_at", "value", "quality", "notes"]

def _sparse_dir(rawdata_root: str, subject_id: str) -> str:
    return os.path.join(rawdata_root, subject_id, "measurements", "sparse_data")

def _csv_path(rawdata_root: str, subject_id: str, marker_id: str) -> str:
    return os.path.join(_sparse_dir(rawdata_root, subject_id), f"{marker_id}.csv")

def _row_to_measurement(row) -> "Measurement":
    return Measurement(
        subject_id  = row["subject_id"],
        marker_id   = row["marker_id"],
        measured_at = row["measured_at"],
        value       = row["value"],
        quality     = row["quality"],
        notes       = row["notes"] or "",
        created_at  = row["created_at"],
    )


# ── GraphQL types ─────────────────────────────────────────────────────────────

@strawberry.type
class Measurement:
    subject_id:  str
    marker_id:   str
    measured_at: str           # UTC ISO-8601 timestamp
    value:       str
    quality:     str           # 'good' | 'suspect' | 'bad'
    notes:       str
    created_at:  str           # UTC ISO-8601 timestamp


# ── Queries ───────────────────────────────────────────────────────────────────

@strawberry.type
class MeasurementQuery:
    @strawberry.field
    def measurements_by_subject(
        self,
        info: Info,
        subject_id: str,
        marker_id: Optional[str] = None,
    ) -> List[Measurement]:
        """Return all measurements for a subject, optionally filtered to a single marker."""
        db_path = info.context["db_path"]
        with get_connection(db_path) as conn:
            if marker_id:
                rows = conn.execute(
                    """SELECT * FROM measurements
                       WHERE subject_id = ? AND marker_id = ?
                       ORDER BY measured_at""",
                    (subject_id, marker_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM measurements
                       WHERE subject_id = ?
                       ORDER BY marker_id, measured_at""",
                    (subject_id,),
                ).fetchall()
        return [_row_to_measurement(r) for r in rows]

    @strawberry.field
    def measurements_by_marker(
        self,
        info: Info,
        marker_id: str,
        subject_id: Optional[str] = None,
    ) -> List[Measurement]:
        """Return all measurements for a marker across subjects (admin/research view)."""
        db_path = info.context["db_path"]
        with get_connection(db_path) as conn:
            if subject_id:
                rows = conn.execute(
                    """SELECT * FROM measurements
                       WHERE marker_id = ? AND subject_id = ?
                       ORDER BY measured_at""",
                    (marker_id, subject_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM measurements
                       WHERE marker_id = ?
                       ORDER BY subject_id, measured_at""",
                    (marker_id,),
                ).fetchall()
        return [_row_to_measurement(r) for r in rows]


# ── Mutations ─────────────────────────────────────────────────────────────────

@strawberry.type
class MeasurementMutation:
    @strawberry.mutation
    def add_measurement(
        self,
        info: Info,
        subject_id:  str,
        marker_id:   str,
        measured_at: str,
        value:       str,
        quality:     Optional[str] = "good",
        notes:       Optional[str] = "",
    ) -> Measurement:
        """
        Record a new measurement.

        Steps:
          1. Verify subject and marker exist in DB.
          2. Verify marker storage_type is 'sparse'.
          3. Append a row to the subject's sparse_data CSV for this marker
             (creating the file with a header if it doesn't exist yet).
          4. Upsert into the measurements table.
          5. Return the new Measurement.
        """
        db_path      = info.context["db_path"]
        rawdata_root = info.context["rawdata_root"]
        quality      = quality or "good"
        notes        = notes or ""

        with get_connection(db_path) as conn:
            subj_row = conn.execute(
                "SELECT subject_id FROM subjects WHERE subject_id = ?", (subject_id,)
            ).fetchone()
            if not subj_row:
                raise Exception(f"Subject '{subject_id}' not found.")

            marker_row = conn.execute(
                "SELECT marker_id, storage_type FROM markers WHERE marker_id = ?", (marker_id,)
            ).fetchone()
            if not marker_row:
                raise Exception(f"Marker '{marker_id}' not found.")
            if marker_row["storage_type"] != "sparse":
                raise Exception(
                    f"Marker '{marker_id}' has storage_type '{marker_row['storage_type']}'. "
                    "Only sparse markers support this mutation."
                )

        # Write to CSV
        sparse_dir = _sparse_dir(rawdata_root, subject_id)
        os.makedirs(sparse_dir, exist_ok=True)
        csv_file = _csv_path(rawdata_root, subject_id, marker_id)
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "measured_at": measured_at,
                "value":       value,
                "quality":     quality,
                "notes":       notes,
            })

        # Upsert into DB
        created_at = datetime.now(timezone.utc).isoformat()
        with get_connection(db_path) as conn:
            conn.execute(
                """
                INSERT INTO measurements (subject_id, marker_id, measured_at, value, quality, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject_id, marker_id, measured_at) DO UPDATE SET
                    value      = excluded.value,
                    quality    = excluded.quality,
                    notes      = excluded.notes
                """,
                (subject_id, marker_id, measured_at, value, quality, notes, created_at),
            )
            conn.commit()
            row = conn.execute(
                """SELECT * FROM measurements
                   WHERE subject_id = ? AND marker_id = ? AND measured_at = ?""",
                (subject_id, marker_id, measured_at),
            ).fetchone()
        return _row_to_measurement(row)

    @strawberry.mutation
    def delete_measurement(
        self,
        info: Info,
        subject_id:  str,
        marker_id:   str,
        measured_at: str,
    ) -> bool:
        """
        Delete a single measurement identified by (subject_id, marker_id, measured_at).

        Removes the row from the CSV file (rewriting it) and from the DB.
        Returns True on success; raises if the measurement is not found.
        """
        db_path      = info.context["db_path"]
        rawdata_root = info.context["rawdata_root"]

        # Remove from CSV
        csv_file = _csv_path(rawdata_root, subject_id, marker_id)
        if not os.path.isfile(csv_file):
            raise Exception(f"No measurements found for {subject_id}/{marker_id}.")

        with open(csv_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        original_count = len(rows)
        rows = [r for r in rows if r.get("measured_at") != measured_at]
        if len(rows) == original_count:
            raise Exception(f"Measurement at '{measured_at}' not found for {subject_id}/{marker_id}.")

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        # Remove from DB
        with get_connection(db_path) as conn:
            conn.execute(
                """DELETE FROM measurements
                   WHERE subject_id = ? AND marker_id = ? AND measured_at = ?""",
                (subject_id, marker_id, measured_at),
            )
            conn.commit()

        return True
