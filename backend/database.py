import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "researchmind.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            search_results TEXT,
            scraped_content TEXT,
            report TEXT,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("✅ SQLite Database Ready.")


def save_report(topic, search_results, scraped_content, report, feedback):
    conn = get_connection()
    cursor = conn.cursor()

    search_results = (
        json.dumps(search_results, ensure_ascii=False)
        if isinstance(search_results, (list, dict))
        else search_results
    )

    scraped_content = (
        json.dumps(scraped_content, ensure_ascii=False)
        if isinstance(scraped_content, (list, dict))
        else scraped_content
    )

    report = (
        json.dumps(report, ensure_ascii=False)
        if isinstance(report, (list, dict))
        else report
    )

    feedback = (
        json.dumps(feedback, ensure_ascii=False)
        if isinstance(feedback, (list, dict))
        else feedback
    )

    cursor.execute(
        """
        INSERT INTO reports
        (topic, search_results, scraped_content, report, feedback)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            topic,
            search_results,
            scraped_content,
            report,
            feedback,
        ),
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return new_id


def get_history(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, topic, created_at
        FROM reports
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


def get_report_by_id(report_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def check_existing_report(topic):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM reports
        WHERE topic = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (topic,),
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


if __name__ == "__main__":
    init_db()