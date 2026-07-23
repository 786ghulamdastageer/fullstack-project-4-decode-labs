import sqlite3

DB_NAME = "ems.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin', 'organizer', 'participant')) DEFAULT 'participant'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS venue (
        venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        capacity INTEGER NOT NULL CHECK (capacity > 0)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS event (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        event_date TEXT NOT NULL,
        organizer_id INTEGER NOT NULL,
        venue_id INTEGER,
        FOREIGN KEY (organizer_id) REFERENCES user(user_id),
        FOREIGN KEY (venue_id) REFERENCES venue(venue_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS registration (
        event_id INTEGER NOT NULL,
        participant_id INTEGER NOT NULL,
        registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (event_id, participant_id),
        FOREIGN KEY (event_id) REFERENCES event(event_id),
        FOREIGN KEY (participant_id) REFERENCES user(user_id)
    )
    """)

    conn.commit()
    conn.close()
