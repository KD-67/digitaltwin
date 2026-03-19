import json
import os
import re
from datetime import datetime, timezone
from typing import List, Optional
import strawberry
from strawberry.types import Info

from backend.startup.database_logistics import get_connection


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_list(path: str) -> list:
    if not os.path.isfile(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def _write_list(path: str, data: list) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _row_to_marker(row) -> "Marker":
    return Marker(
        marker_id        = row["marker_id"],
        marker_name      = row["marker_name"],
        description      = row["description"],
        unit             = row["unit"],
        volatility_class = row["volatility_class"],
        created_at       = row["created_at"],
    )


# MARKERS - what types of measurements are possible

@strawberry.type
class Marker:
    marker_id: str
    marker_name: Optional[str]
    description: Optional[str]
    unit: Optional[str]
    volatility_class: Optional[str]
    created_at: Optional[str]    # UTC ISO-8601 timestamp


@strawberry.input
class MarkerInput:
    marker_name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    volatility_class: Optional[str] = None


@strawberry.type
class MarkerQuery:
    @strawberry.field
    def markers(self, info: Info, marker_id: Optional[str] = None) -> List[Marker]:
        """Return all markers, or a single marker if marker_id is provided."""
        db_path = info.context["db_path"]
        with get_connection(db_path) as conn:
            if marker_id:
                rows = conn.execute(
                    "SELECT * FROM markers WHERE marker_id = ?", (marker_id,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM markers").fetchall()
        return [_row_to_marker(r) for r in rows]


@strawberry.type
class MarkerMutation:
    @strawberry.mutation
    def create_marker(self, info: Info, input: MarkerInput) -> Marker:
        """
        Create a new marker record.

        Steps:
          1. Determine the next available mark_NNN id by inspecting marker_list.json
             and deleted_marker_list.json so ids are never reused.
          2. Append the new marker to marker_list.json.
          3. Insert a row into the markers table and return the new Marker.
        """
        db_path        = info.context["db_path"]
        utilities_root = os.path.join(os.path.dirname(info.context["rawdata_root"]), "utilities")

        list_path    = os.path.join(utilities_root, "marker_list.json")
        deleted_path = os.path.join(utilities_root, "deleted_marker_list.json")

        existing   = _read_list(list_path)
        deleted    = _read_list(deleted_path)
        all_ids    = [p["marker_id"] for p in existing + deleted if "marker_id" in p]
        existing_nums = []
        for mid in all_ids:
            m = re.match(r"mark_(\d+)$", mid)
            if m:
                existing_nums.append(int(m.group(1)))
        next_n    = max(existing_nums, default=0) + 1
        marker_id = f"mark_{next_n:03d}"

        created_at = datetime.now(timezone.utc).isoformat()

        entry = {
            "marker_id":        marker_id,
            "marker_name":      input.marker_name,
            "description":      input.description,
            "unit":             input.unit,
            "volatility_class": input.volatility_class,
            "created_at":       created_at,
        }
        existing.append(entry)
        _write_list(list_path, existing)

        with get_connection(db_path) as conn:
            conn.execute(
                """INSERT INTO markers (marker_id, marker_name, description, unit, volatility_class, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (marker_id, input.marker_name, input.description,
                 input.unit, input.volatility_class, created_at),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM markers WHERE marker_id = ?", (marker_id,)).fetchone()
        return _row_to_marker(row)

    @strawberry.mutation
    def update_marker(self, info: Info, marker_id: str, input: MarkerInput) -> Marker:
        """
        Update an existing marker's fields.

        Only fields explicitly set in MarkerInput (i.e. not None) are written.
        marker_list.json is rewritten to stay in sync with the DB.
        """
        db_path        = info.context["db_path"]
        utilities_root = os.path.join(os.path.dirname(info.context["rawdata_root"]), "utilities")

        fields  = ["marker_name", "description", "unit", "volatility_class"]
        updates = {f: getattr(input, f) for f in fields if getattr(input, f) is not None}

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [marker_id]
            with get_connection(db_path) as conn:
                conn.execute(f"UPDATE markers SET {set_clause} WHERE marker_id = ?", values)
                conn.commit()

        list_path = os.path.join(utilities_root, "marker_list.json")
        markers   = _read_list(list_path)
        for entry in markers:
            if entry.get("marker_id") == marker_id:
                entry.update(updates)
                break
        _write_list(list_path, markers)

        with get_connection(db_path) as conn:
            row = conn.execute("SELECT * FROM markers WHERE marker_id = ?", (marker_id,)).fetchone()
        return _row_to_marker(row)

    @strawberry.mutation
    def delete_marker(self, info: Info, marker_id: str) -> bool:
        """
        Soft-delete a marker by removing it from marker_list.json and appending
        it to deleted_marker_list.json, then removing the DB row.
        Returns True on success.
        """
        db_path        = info.context["db_path"]
        utilities_root = os.path.join(os.path.dirname(info.context["rawdata_root"]), "utilities")

        list_path    = os.path.join(utilities_root, "marker_list.json")
        deleted_path = os.path.join(utilities_root, "deleted_marker_list.json")

        markers = _read_list(list_path)
        to_delete = [m for m in markers if m.get("marker_id") == marker_id]
        remaining = [m for m in markers if m.get("marker_id") != marker_id]
        _write_list(list_path, remaining)

        deleted = _read_list(deleted_path)
        deleted.extend(to_delete)
        _write_list(deleted_path, deleted)

        with get_connection(db_path) as conn:
            conn.execute("DELETE FROM markers WHERE marker_id = ?", (marker_id,))
            conn.commit()

        return True


# MEASUREMENTS - individual measured instances of a marker
@strawberry.type
class Measurement:
    marker_id: str
    marker_name: str
    subject_id: str
    measured_at: str                      # UTC ISO-8601 timestamp
    value: str
    unit: str
    quality: str
    notes: str
    created_at: str                       # UTC ISO-8601 timestamp
    updated_at: Optional[str]             # UTC ISO-8601 timestamp

@strawberry.input
class MeasurementInput:
    marker_id: Optional[str] = None
    marker_name: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[str] = None
    measured_at: Optional[str] = None      # UTC ISO-8601 timestamp
    value: Optional[str] = None
    unit: Optional[str] = None
    quality: Optional[str] = None
    notes: Optional[str] = None
    updated_at: Optional[str] = None       # UTC ISO-8601 timestamp
