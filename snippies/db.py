import sqlite3
from datetime import datetime
from snippies import app_log

def init_db(database_path):
    app_log.message("debug", "Initializing backup schedules database")
    with sqlite3.connect(database_path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                date TEXT NOT NULL,
                action TEXT NOT NULL
            );
        """)

def get_records():
    app_log.message("debug", "Getting backup records")
    with sqlite3.connect('schedules.sqlite') as database:
        rows = database.execute(
            "SELECT id, username, date, action FROM schedules").fetchall()
        return rows

def add_record(username, date, action):
    app_log.message("debug", "Formatting datetime object to string")
    date = datetime.strftime(date, "%Y-%m-%dT%H:%M:%S.000Z")
    app_log.message("debug", f"Adding record ({username}, {date}, {action}) into database")
    with sqlite3.connect('schedules.sqlite') as database:
        cur = database.execute("INSERT INTO schedules (username, date, action) VALUES (?, ?, ?)",
            (username, date, action))
        return cur.lastrowid
    
def delete_record(row_id):
    app_log.message("debug", f"Attempting to delete record {row_id}")
    with sqlite3.connect('schedules.sqlite') as database:
        database.execute("DELETE from schedules WHERE id = ?", (row_id,))