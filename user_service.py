def get_user(cur, client_id):
    cur.execute("SELECT area_code FROM users WHERE client_id=?", (client_id,))
    row = cur.fetchone()
    return row[0] if row else None

def update_user(cur, client_id, area, time):
    cur.execute(
        "INSERT OR REPLACE INTO users VALUES (?,?,?)",
        (client_id, area, time)
    )
