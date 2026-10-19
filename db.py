import sqlite3

DB = "ginterships.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT UNIQUE, password_hash TEXT
    );
    CREATE TABLE IF NOT EXISTS interests(
        user_id INTEGER, keyword TEXT
    );
    CREATE TABLE IF NOT EXISTS offers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, company TEXT, location TEXT,
        url TEXT UNIQUE, source TEXT, category TEXT DEFAULT 'stage',
        first_seen TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS sent(
        user_id INTEGER, offer_id INTEGER,
        PRIMARY KEY (user_id, offer_id)
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database ready")
