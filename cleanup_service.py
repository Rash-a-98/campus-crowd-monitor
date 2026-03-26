import time
from database import get_db
from modules.crowd_service import exit_area
from modules.log_service import log_exit

def cleanup_inactive_users():
    while True:
        time.sleep(10)
        now = time.time()

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT client_id, area_code, last_seen FROM users")
        users = cur.fetchall()

        for cid, area, last_seen in users:
            if area and (now - last_seen > 60):
                exit_area(cur, area)
                log_exit(cur, cid, area)
                cur.execute("DELETE FROM users WHERE client_id=?", (cid,))

        conn.commit()
        conn.close()