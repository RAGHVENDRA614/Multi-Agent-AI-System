import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import json
load_dotenv()

# ---------------- Connection Settings ----------------
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "researchmind"),
}


def get_connection():
    """Create and return a new MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None


def init_db():
    """
    Create the database (if not exists) and the reports table.
    Run this once when the app starts.
    """
    try:
        # Step 1: Connect WITHOUT specifying database (so we can create it)
        temp_config = DB_CONFIG.copy()
        temp_config.pop("database")

        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        conn.close()

        # Step 2: Connect to the actual database and create table
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic VARCHAR(255) NOT NULL,
                search_results LONGTEXT,
                scraped_content LONGTEXT,
                report LONGTEXT,
                feedback LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database and table ready.")

    except Error as e:
        print(f"❌ init_db failed: {e}")


def save_report(topic: str, search_results: str, scraped_content: str, report: str, feedback: str) -> int:
    """
    Save a completed research report into the database.
    Returns the inserted row's id.
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO reports (topic, search_results, scraped_content, report, feedback)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
    topic,
    json.dumps(search_results, ensure_ascii=False) if isinstance(search_results, (list, dict)) else search_results,
    json.dumps(scraped_content, ensure_ascii=False) if isinstance(scraped_content, (list, dict)) else scraped_content,
    json.dumps(report, ensure_ascii=False) if isinstance(report, (list, dict)) else report,
    json.dumps(feedback, ensure_ascii=False) if isinstance(feedback, (list, dict)) else feedback,
)
        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return new_id

    except Error as e:
        print(f"❌ save_report failed: {e}")
        return None


def get_history(limit: int = 20) -> list:
    """
    Fetch the most recent reports (id, topic, created_at only —
    lightweight for listing on a history page).
    """
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, topic, created_at
            FROM reports
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    except Error as e:
        print(f"❌ get_history failed: {e}")
        return []


def get_report_by_id(report_id: int) -> dict:
    """
    Fetch a single full report by its id (used when user clicks
    on a history item to view the full report).
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    except Error as e:
        print(f"❌ get_report_by_id failed: {e}")
        return None


def check_existing_report(topic: str) -> dict:
    """
    Check if a report already exists for this exact topic
    (used for simple caching — avoid re-running the whole pipeline).
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM reports
            WHERE topic = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (topic,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    except Error as e:
        print(f"❌ check_existing_report failed: {e}")
        return None


if __name__ == "__main__":
    # Run this file directly to set up the database:  python database.py
    init_db()