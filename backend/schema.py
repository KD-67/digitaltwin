import sqlite3
import json
import os
import re
import shutil
from datetime import datetime, timezone
from typing import List, Optional
import strawberry
from strawberry.types import Info

from backend.startup.database_logistics import get_connection


# GraphQL type returned by subject queries and mutations.
# subject_id follows the pattern subj_NNN (e.g. subj_001).
@strawberry.type
class Subject:
    subject_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    sex: Optional[str]
    dob: Optional[str]           # ISO date string, e.g. "1990-05-20"
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    created_at: Optional[str]    # UTC ISO-8601 timestamp


# Input type for create/update mutations.
# All fields are optional so callers only send what they want to set.
@strawberry.input
class SubjectInput:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None
    dob: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


def _row_to_subject(row) -> Subject:
    """Convert a sqlite3.Row from the subjects table into a Subject object."""
    return Subject(
        subject_id = row["subject_id"],
        first_name = row["first_name"],
        last_name  = row["last_name"],
        sex        = row["sex"],
        dob        = row["dob"],
        email      = row["email"],
        phone      = row["phone"],
        notes      = row["notes"],
        created_at = row["created_at"],
    )


@strawberry.type
class Query:
    @strawberry.field
    def subjects(self, info: Info, subject_id: Optional[str] = None) -> List[Subject]:
        """
        Return all subjects, or a single subject if subject_id is provided.
        db_path is injected via the Strawberry context.
        """
        db_path = info.context["db_path"]
        with get_connection(db_path) as conn:
            if subject_id:
                rows = conn.execute(
                    "SELECT * FROM subjects WHERE subject_id = ?", (subject_id,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM subjects").fetchall()
        return [_row_to_subject(r) for r in rows]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_subject(self, info: Info, input: SubjectInput) -> Subject:
        """
        Create a new subject record.

        Steps:
          1. Determine the next available subj_NNN id by inspecting both the
             DB and the rawdata filesystem (so gaps from manual folder creation
             are avoided).
          2. Create the subject's directory under rawdata_root and write a
             profile.json snapshot of all fields.
          3. Insert a row into the subjects table and return the new Subject.
        """
        db_path      = info.context["db_path"]
        rawdata_root = info.context["rawdata_root"]

        # Generate next subj_NNN id
        with get_connection(db_path) as conn:
            rows = conn.execute("SELECT subject_id FROM subjects").fetchall()
        existing_nums = []
        for r in rows:
            m = re.match(r"subj_(\d+)$", r["subject_id"])
            if m:
                existing_nums.append(int(m.group(1)))
        # Also check filesystem for any folders not yet in DB
        if os.path.isdir(rawdata_root):
            for entry in os.listdir(rawdata_root):
                m = re.match(r"subj_(\d+)$", entry)
                if m:
                    existing_nums.append(int(m.group(1)))
        next_n     = max(existing_nums, default=0) + 1
        subject_id = f"subj_{next_n:03d}"

        created_at = datetime.now(timezone.utc).isoformat()

        # Create folder + profile.json
        subject_dir = os.path.join(rawdata_root, subject_id)
        os.makedirs(subject_dir, exist_ok=True)
        profile = {
            "subject_id": subject_id,
            "first_name": input.first_name,
            "last_name":  input.last_name,
            "sex":        input.sex,
            "dob":        input.dob,
            "email":      input.email,
            "phone":      input.phone,
            "notes":      input.notes,
            "created_at": created_at,
        }
        with open(os.path.join(subject_dir, "profile.json"), "w") as f:
            json.dump(profile, f, indent=2)

        # Insert into DB
        with get_connection(db_path) as conn:
            conn.execute(
                """INSERT INTO subjects (subject_id, first_name, last_name, sex, dob, email, phone, notes, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (subject_id, input.first_name, input.last_name, input.sex,
                 input.dob, input.email, input.phone, input.notes, created_at),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM subjects WHERE subject_id = ?", (subject_id,)).fetchone()
        return _row_to_subject(row)

    @strawberry.mutation
    def update_subject(self, info: Info, subject_id: str, input: SubjectInput) -> Subject:
        """
        Update an existing subject's fields.

        Only fields explicitly set in SubjectInput (i.e. not None) are written,
        so callers can do partial updates without overwriting untouched fields.
        The profile.json on disk is rewritten to stay in sync with the DB.
        """
        db_path      = info.context["db_path"]
        rawdata_root = info.context["rawdata_root"]

        # Build SET clause for non-None fields only
        fields = ["first_name", "last_name", "sex", "dob", "email", "phone", "notes"]
        updates = {f: getattr(input, f) for f in fields if getattr(input, f) is not None}

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [subject_id]
            with get_connection(db_path) as conn:
                conn.execute(f"UPDATE subjects SET {set_clause} WHERE subject_id = ?", values)
                conn.commit()

        # Rewrite profile.json
        profile_path = os.path.join(rawdata_root, subject_id, "profile.json")
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        if os.path.isfile(profile_path):
            with open(profile_path, "r") as f:
                profile = json.load(f)
        else:
            profile = {"subject_id": subject_id}
        profile.update(updates)
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)

        with get_connection(db_path) as conn:
            row = conn.execute("SELECT * FROM subjects WHERE subject_id = ?", (subject_id,)).fetchone()
        return _row_to_subject(row)

    @strawberry.mutation
    def delete_subject(self, info: Info, subject_id: str) -> bool:
        """
        Soft-delete a subject by moving their rawdata folder to
        rawdata_root/deleted_subjects/ instead of permanently removing it,
        then remove the DB row.  Returns True on success.
        """
        db_path      = info.context["db_path"]
        rawdata_root = info.context["rawdata_root"]

        # Move folder to deleted_subjects/
        src = os.path.join(rawdata_root, subject_id)
        deleted_dir = os.path.join(rawdata_root, "deleted_subjects")
        os.makedirs(deleted_dir, exist_ok=True)
        if os.path.isdir(src):
            shutil.move(src, os.path.join(deleted_dir, subject_id))

        with get_connection(db_path) as conn:
            conn.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))
            conn.commit()

        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
