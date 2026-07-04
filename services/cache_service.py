import sqlite3


def get_cache_connection():
    conn = sqlite3.connect("database/submissions.db")
    conn.row_factory = sqlite3.Row
    return conn


def cache_submission(sheet_data):
    conn = get_cache_connection()
    try:
        conn.execute("""
        INSERT INTO submissions (
            faculty,
            program_name,
            program_type,
            organizer,
            venue,
            start_date,
            end_date,
            timestamp,
            drive_link
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     sheet_data
                     )
        conn.commit()
    finally:
        conn.close()


def get_dashboard_stats():

    conn = get_cache_connection()
    try:
        stats = {
            "total_faculty": conn.execute(
                "SELECT COUNT(DISTINCT faculty) FROM submissions"
            ).fetchone()[0],

            "total_submissions": conn.execute(
                "SELECT COUNT(*) FROM submissions"
            ).fetchone()[0]
        }
    finally:
        conn.close()

    return stats


def build_filters(search=None, program_type=None):
    conditions = []
    params = []

    if search:
        search = search.strip()

        if search:
            conditions.append("""
                (
                    faculty LIKE ?
                    OR program_name LIKE ?
                    OR organizer LIKE ?
                )
            """)

            keyword = f"%{search}%"
            params.extend([keyword, keyword, keyword])

    if program_type:
        conditions.append("program_type = ?")
        params.append(program_type)

    return conditions, params


def get_all_faculty():
    conn = get_cache_connection()
    try:
        return conn.execute("""
            SELECT DISTINCT faculty
            FROM submissions
            ORDER BY faculty ASC
        """).fetchall()
    finally:
        conn.close()


def get_submission_count(
    search=None,
    program_type=None
):
    conn = get_cache_connection()
    try:
        query = """
            SELECT COUNT(*)
            FROM submissions
        """
        conditions, params = build_filters(search, program_type)
        if conditions:
            query += " WHERE "
            query += " AND ".join(conditions)
        return conn.execute(query, params).fetchone()[0]
    finally:
        conn.close()


def get_all_submissions(search=None,
                        program_type=None,
                        sort="newest",
                        limit=None,
                        offset=None):

    conn = get_cache_connection()
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM submissions
    """

    conditions, params = build_filters(search, program_type)

    if conditions:
        query += " WHERE "
        query += " AND ".join(conditions)

    sort_options = {
        "newest": "timestamp DESC",
        "oldest": "timestamp ASC",
        "faculty_asc": "faculty ASC",
        "faculty_desc": "faculty DESC"
    }

    query += (
        " ORDER BY "
        + sort_options.get(
            sort,
            "timestamp DESC"
        )
    )

    if limit is not None and offset is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    try:
        rows = cursor.execute(
            query,
            params
        ).fetchall()
    finally:
        conn.close()

    return rows
