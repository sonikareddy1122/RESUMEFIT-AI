import sqlite3
import os
import json
import pandas as pd
from datetime import datetime


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "resume_screening.db"
)

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# ============================================================
# CREATE TABLE
# ============================================================

def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY,
            candidate_name TEXT,
            resume_file TEXT,
            education TEXT,
            location TEXT,
            experience INTEGER,
            experience_level TEXT,
            skills_count INTEGER,
            resume_score REAL,
            jd_match REAL,
            recommendation TEXT,
            top_job_role TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            screening_date TEXT
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# DATABASE SCHEMA MIGRATION
# ============================================================

def migrate_database():
    """
    Makes the existing database compatible with the current
    application.

    Handles:
    - Old ai_probability column
    - Old INTEGER matched_skills / missing_skills columns
    - Missing location column
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(candidates)")
    columns_info = cursor.fetchall()

    existing_columns = {
        row[1]: row[2]
        for row in columns_info
    }

    required_columns = {
        "candidate_name": "TEXT",
        "resume_file": "TEXT",
        "education": "TEXT",
        "location": "TEXT",
        "experience": "INTEGER",
        "experience_level": "TEXT",
        "skills_count": "INTEGER",
        "resume_score": "REAL",
        "jd_match": "REAL",
        "recommendation": "TEXT",
        "top_job_role": "TEXT",
        "matched_skills": "TEXT",
        "missing_skills": "TEXT",
        "screening_date": "TEXT",
    }

    # --------------------------------------------------------
    # Empty database / table did not exist properly
    # --------------------------------------------------------

    if not existing_columns:
        connection.close()
        create_table()
        return

    # --------------------------------------------------------
    # Add missing columns
    # --------------------------------------------------------

    for column, column_type in required_columns.items():

        if column not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE candidates
                ADD COLUMN {column} {column_type}
                """
            )

    connection.commit()

    # --------------------------------------------------------
    # Convert old matched/missing values to TEXT where needed
    #
    # SQLite does not require an ALTER COLUMN operation for
    # storing text in an INTEGER-declared column, but we need
    # to preserve the actual skill names. A migration through
    # a temporary table gives us a clean schema.
    # --------------------------------------------------------

    matched_type = existing_columns.get("matched_skills", "").upper()
    missing_type = existing_columns.get("missing_skills", "").upper()

    if (
        "INTEGER" in matched_type
        or "INTEGER" in missing_type
    ):
        cursor.execute(
            """
            SELECT
                id,
                candidate_name,
                resume_file,
                education,
                location,
                experience,
                experience_level,
                skills_count,
                resume_score,
                jd_match,
                recommendation,
                top_job_role,
                matched_skills,
                missing_skills,
                screening_date
            FROM candidates
            """
        )

        old_rows = cursor.fetchall()

        cursor.execute(
            """
            DROP TABLE IF EXISTS candidates_new
            """
        )

        cursor.execute(
            """
            CREATE TABLE candidates_new (
                id INTEGER PRIMARY KEY,
                candidate_name TEXT,
                resume_file TEXT,
                education TEXT,
                location TEXT,
                experience INTEGER,
                experience_level TEXT,
                skills_count INTEGER,
                resume_score REAL,
                jd_match REAL,
                recommendation TEXT,
                top_job_role TEXT,
                matched_skills TEXT,
                missing_skills TEXT,
                screening_date TEXT
            )
            """
        )

        for row in old_rows:

            (
                candidate_id,
                candidate_name,
                resume_file,
                education,
                location,
                experience,
                experience_level,
                skills_count,
                resume_score,
                jd_match,
                recommendation,
                top_job_role,
                matched_skills,
                missing_skills,
                screening_date,
            ) = row

            # Old database may only contain numeric counts.
            # Preserve those values as text instead of losing them.
            if isinstance(matched_skills, (list, tuple, dict)):
                matched_skills = json.dumps(
                    matched_skills,
                    ensure_ascii=False
                )
            elif matched_skills is None:
                matched_skills = json.dumps([])
            else:
                matched_skills = str(matched_skills)

            if isinstance(missing_skills, (list, tuple, dict)):
                missing_skills = json.dumps(
                    missing_skills,
                    ensure_ascii=False
                )
            elif missing_skills is None:
                missing_skills = json.dumps([])
            else:
                missing_skills = str(missing_skills)

            cursor.execute(
                """
                INSERT INTO candidates_new (
                    id,
                    candidate_name,
                    resume_file,
                    education,
                    location,
                    experience,
                    experience_level,
                    skills_count,
                    resume_score,
                    jd_match,
                    recommendation,
                    top_job_role,
                    matched_skills,
                    missing_skills,
                    screening_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id,
                    candidate_name,
                    resume_file,
                    education,
                    location,
                    experience,
                    experience_level,
                    skills_count,
                    resume_score,
                    jd_match,
                    recommendation,
                    top_job_role,
                    matched_skills,
                    missing_skills,
                    screening_date,
                )
            )

        cursor.execute(
            """
            DROP TABLE candidates
            """
        )

        cursor.execute(
            """
            ALTER TABLE candidates_new
            RENAME TO candidates
            """
        )

    connection.commit()
    connection.close()


# ============================================================
# ADD / ENSURE LOCATION COLUMN
# ============================================================

def add_missing_columns():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        PRAGMA table_info(candidates)
        """
    )

    existing_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "location" not in existing_columns:

        cursor.execute(
            """
            ALTER TABLE candidates
            ADD COLUMN location TEXT
            """
        )

    connection.commit()
    connection.close()


# ============================================================
# VALUE CONVERSION HELPERS
# ============================================================

def serialize_list(value):
    """
    Converts Python lists/tuples/dicts into JSON text that
    SQLite can safely store.
    """

    if value is None:
        return json.dumps([])

    if isinstance(value, (list, tuple, dict, set)):

        if isinstance(value, set):
            value = list(value)

        return json.dumps(
            value,
            ensure_ascii=False
        )

    # If the value is already a string, preserve it.
    if isinstance(value, str):
        return value

    return str(value)


def deserialize_list(value):
    """
    Converts JSON text stored in SQLite back into a Python list
    when possible.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        return [value]

    value = value.strip()

    if not value:
        return []

    try:
        decoded = json.loads(value)

        if isinstance(decoded, list):
            return decoded

        return [decoded]

    except (json.JSONDecodeError, TypeError):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]


def prepare_candidate(candidate):
    """
    Converts a candidate dictionary into SQLite-safe values.
    """

    return (
        candidate.get(
            "Candidate",
            "Unknown"
        ),

        candidate.get(
            "Resume File",
            ""
        ),

        candidate.get(
            "Education",
            "Not Specified"
        ),

        candidate.get(
            "Location",
            "Not Specified"
        ),

        candidate.get(
            "Experience",
            0
        ),

        candidate.get(
            "Experience Level",
            "Fresher"
        ),

        candidate.get(
            "Skills",
            0
        ),

        candidate.get(
            "Resume Score",
            0
        ),

        candidate.get(
            "JD Match",
            0
        ),

        candidate.get(
            "Recommendation",
            "Not Recommended"
        ),

        candidate.get(
            "Top Job Role",
            "Not Specified"
        ),

        serialize_list(
            candidate.get(
                "Matched Skills",
                []
            )
        ),

        serialize_list(
            candidate.get(
                "Missing Skills",
                []
            )
        ),

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )


# ============================================================
# INSERT ONE CANDIDATE
# ============================================================

def insert_candidate(candidate):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        candidate_data = prepare_candidate(candidate)

        cursor.execute(
            """
            INSERT INTO candidates (
                candidate_name,
                resume_file,
                education,
                location,
                experience,
                experience_level,
                skills_count,
                resume_score,
                jd_match,
                recommendation,
                top_job_role,
                matched_skills,
                missing_skills,
                screening_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            candidate_data
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# FIND LOWEST AVAILABLE ID
# ============================================================

def get_next_available_id(cursor):
    """
    Returns the lowest available positive candidate ID.

    Example:

    Existing IDs:
    1, 3, 4

    Returned ID:
    2
    """

    cursor.execute(
        """
        SELECT id
        FROM candidates
        ORDER BY id ASC
        """
    )

    rows = cursor.fetchall()

    expected_id = 1

    for row in rows:

        current_id = row[0]

        if current_id == expected_id:
            expected_id += 1

        elif current_id > expected_id:
            break

    return expected_id


# ============================================================
# INSERT MULTIPLE CANDIDATES
# ============================================================

def insert_candidates(candidates):

    if not candidates:
        return

    connection = get_connection()

    try:

        cursor = connection.cursor()

        for candidate in candidates:

            candidate_data = prepare_candidate(candidate)

            candidate_id = get_next_available_id(cursor)

            cursor.execute(
                """
                INSERT INTO candidates (
                    id,
                    candidate_name,
                    resume_file,
                    education,
                    location,
                    experience,
                    experience_level,
                    skills_count,
                    resume_score,
                    jd_match,
                    recommendation,
                    top_job_role,
                    matched_skills,
                    missing_skills,
                    screening_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id,
                    *candidate_data,
                )
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# GET ALL CANDIDATES
# ============================================================

def get_all_candidates():

    connection = get_connection()

    try:

        query = """
            SELECT
                id,
                candidate_name,
                resume_file,
                education,
                location,
                experience,
                experience_level,
                skills_count,
                resume_score,
                jd_match,
                recommendation,
                top_job_role,
                matched_skills,
                missing_skills,
                screening_date
            FROM candidates
            ORDER BY id DESC
        """

        dataframe = pd.read_sql_query(
            query,
            connection
        )

        # Convert JSON strings back into readable skill names.
        if "matched_skills" in dataframe.columns:
            dataframe["matched_skills"] = dataframe[
                "matched_skills"
            ].apply(
                lambda value: ", ".join(
                    map(
                        str,
                        deserialize_list(value)
                    )
                )
            )

        if "missing_skills" in dataframe.columns:
            dataframe["missing_skills"] = dataframe[
                "missing_skills"
            ].apply(
                lambda value: ", ".join(
                    map(
                        str,
                        deserialize_list(value)
                    )
                )
            )

        return dataframe

    finally:
        connection.close()


# ============================================================
# SEARCH CANDIDATES
# ============================================================

def search_candidates(search_text):

    connection = get_connection()

    try:

        query = """
            SELECT
                id,
                candidate_name,
                resume_file,
                education,
                location,
                experience,
                experience_level,
                skills_count,
                resume_score,
                jd_match,
                recommendation,
                top_job_role,
                matched_skills,
                missing_skills,
                screening_date
            FROM candidates
            WHERE candidate_name LIKE ?
            OR resume_file LIKE ?
            OR recommendation LIKE ?
            OR top_job_role LIKE ?
            OR location LIKE ?
            OR education LIKE ?
            OR matched_skills LIKE ?
            OR missing_skills LIKE ?
            ORDER BY id DESC
        """

        pattern = f"%{search_text}%"

        dataframe = pd.read_sql_query(
            query,
            connection,
            params=(
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
            )
        )

        if "matched_skills" in dataframe.columns:
            dataframe["matched_skills"] = dataframe[
                "matched_skills"
            ].apply(
                lambda value: ", ".join(
                    map(
                        str,
                        deserialize_list(value)
                    )
                )
            )

        if "missing_skills" in dataframe.columns:
            dataframe["missing_skills"] = dataframe[
                "missing_skills"
            ].apply(
                lambda value: ", ".join(
                    map(
                        str,
                        deserialize_list(value)
                    )
                )
            )

        return dataframe

    finally:
        connection.close()


# ============================================================
# DELETE ONE CANDIDATE
# ============================================================

def delete_candidate(candidate_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM candidates
            WHERE id = ?
            """,
            (candidate_id,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# DELETE ALL CANDIDATES
# ============================================================

def delete_all_candidates():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM candidates
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# INITIALIZE / MIGRATE DATABASE
# ============================================================

create_table()
migrate_database()
add_missing_columns()
