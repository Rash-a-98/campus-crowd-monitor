import sqlite3

def get_db():
    conn = sqlite3.connect("campus.db")
    conn.row_factory = sqlite3.Row   # optional but useful
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # ---------------- LOGIN USERS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users_login(
        phone TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        dept TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # ---------------- ACTIVE USERS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        client_id TEXT PRIMARY KEY,
        area_code TEXT,
        last_seen REAL
    )
    """)

    # ---------------- AREAS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS areas(
        area_code TEXT PRIMARY KEY,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        radius REAL NOT NULL,
        count INTEGER DEFAULT 0
    )
    """)

    # ---------------- LOGS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        area_code TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT
    )
    """)

    # ---------------- DEFAULT AREA ----------------
    cur.execute("SELECT COUNT(*) FROM areas")

    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO areas (area_code, lat, lon, radius, count)
        VALUES (?, ?, ?, ?, ?)
        """, [
            ("Canteen",12.407, 75.095, 50, 0),
            ("Auditorium",12.408, 75.096, 80, 0),
            ("Library",12.406, 75.094,50,0)


        ])

    conn.commit()
    conn.close()