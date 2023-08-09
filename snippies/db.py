import sqlite3

def init_db(database_path):
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
    with sqlite3.connect('schedules.sqlite') as database:
        rows = database.execute(
            "SELECT id, username, date, action FROM schedules").fetchall()
        return rows

def add_record(username, date, action):
    with sqlite3.connect('schedules.sqlite') as database:
        cur = database.execute("INSERT INTO schedules (username, date, action) VALUES (?, ?, ?)",
            (username, date, action))
        return cur.lastrowid
    
def delete_record(row_id):
    with sqlite3.connect('schedules.sqlite') as database:
        database.execute("DELETE from schedules WHERE id = ?", (row_id,))