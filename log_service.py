def log_entry(cur, client_id, area):
    cur.execute("""
        INSERT INTO logs (client_id, area_code, entry_time, exit_time)
        VALUES (?, ?, time('now'), NULL)
    """, (client_id, area))

def log_exit(cur, client_id, area):
    cur.execute("""
        UPDATE logs
        SET exit_time=time('now')
        WHERE client_id=? AND area_code=? AND exit_time IS NULL
    """, (client_id, area))