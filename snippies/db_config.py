import sqlite3


def init_db(database_path):
    with sqlite3.connect(database_path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                username TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL
            );
        """)
