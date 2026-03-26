from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import time, math, io

from database import init_db, get_db

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib import pagesizes

app = Flask(__name__)
CORS(app)

# Initialize DB
init_db()


# ---------------- DISTANCE FUNCTION ----------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))


# ---------------- PAGES ----------------

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/logs")
def logs_page():
    return render_template("logs.html")


# ---------------- LOGIN API ----------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json

    name = data.get("name", "")
    phone = data.get("phone", "")
    dept = data.get("dept", "")
    role = data.get("role", "")
    staff_code = data.get("staff_code", "")

    if role == "staff":
        if staff_code != "STAFF2026":
            return jsonify({"error": "Invalid staff code"}), 403

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO users_login
        (phone, name, dept, role)
        VALUES (?, ?, ?, ?)
    """, (phone, name, dept, role))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ---------------- GET AREAS ----------------

@app.route('/api/areas')
def areas():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM areas")
    rows = cur.fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


# ---------------- PRESENCE TRACKING ----------------

from datetime import datetime

@app.route("/api/presence", methods=["POST"])
def presence():
    data = request.json

    client_id = data["client_id"]
    lat = float(data["lat"])
    lon = float(data["lon"])
    now = time.time()

    conn = get_db()
    cur = conn.cursor()

    # 🔥 Get current local system time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------- REMOVE INACTIVE USERS ----------------
    TIMEOUT = 15

    cur.execute("SELECT client_id, area_code FROM users WHERE last_seen < ?", (now - TIMEOUT,))
    inactive_users = cur.fetchall()

    for u in inactive_users:
        if u["area_code"]:
            cur.execute(
                "UPDATE areas SET count=count-1 WHERE area_code=? AND count>0",
                (u["area_code"],)
            )

            # ✅ Use system time instead of SQLite UTC
            cur.execute("""
                UPDATE logs
                SET exit_time = ?
                WHERE client_id=? AND area_code=? AND exit_time IS NULL
            """, (current_time, u["client_id"], u["area_code"]))

    cur.execute("DELETE FROM users WHERE last_seen < ?", (now - TIMEOUT,))

    # ---------------- DETECT AREA ----------------
    cur.execute("SELECT area_code, lat, lon, radius FROM areas")
    areas = cur.fetchall()

    new_area = None
    for a in areas:
        if haversine(lat, lon, a["lat"], a["lon"]) <= a["radius"]:
            new_area = a["area_code"]
            break

    # ---------------- CHECK OLD AREA ----------------
    cur.execute("SELECT area_code FROM users WHERE client_id=?", (client_id,))
    row = cur.fetchone()
    old_area = row["area_code"] if row else None

    if old_area != new_area:

        # EXIT OLD AREA
        if old_area:
            cur.execute(
                "UPDATE areas SET count=count-1 WHERE area_code=? AND count>0",
                (old_area,)
            )

            cur.execute("""
                UPDATE logs
                SET exit_time = ?
                WHERE client_id=? AND area_code=? AND exit_time IS NULL
            """, (current_time, client_id, old_area))

        # ENTER NEW AREA
        if new_area:
            cur.execute(
                "UPDATE areas SET count=count+1 WHERE area_code=?",
                (new_area,)
            )

            cur.execute("""
                INSERT INTO logs (client_id, area_code, entry_time)
                VALUES (?, ?, ?)
            """, (client_id, new_area, current_time))

    # ---------------- UPDATE USERS TABLE ----------------
    cur.execute("""
        INSERT OR REPLACE INTO users (client_id, area_code, last_seen)
        VALUES (?, ?, ?)
    """, (client_id, new_area, now))

    conn.commit()
    conn.close()

    return jsonify({"area": new_area})



# ---------------- GET LOGS (DATE FILTER + TIME ONLY) ----------------

@app.route("/api/logs")
def get_logs():
    selected_date = request.args.get("date")
    selected_role = request.args.get("role")

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT 
            u.name,
            u.dept,
            u.role,
            l.area_code,
            TIME(l.entry_time) as entry_time,
            TIME(l.exit_time) as exit_time
        FROM logs l
        LEFT JOIN users_login u
        ON l.client_id = u.phone
    """

    conditions = []
    params = []

    if selected_date:
        conditions.append("DATE(l.entry_time) = ?")
        params.append(selected_date)

    if selected_role and selected_role != "all":
        conditions.append("u.role = ?")
        params.append(selected_role)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY l.entry_time DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])






# ---------------- DOWNLOAD PDF ----------------

@app.route("/download_logs")
def download_logs():

    selected_date = request.args.get("date", "").strip()
    selected_role = request.args.get("role", "").strip()

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT u.name, u.dept, u.role, l.area_code,
               DATE(l.entry_time),
               TIME(l.entry_time),
               TIME(l.exit_time)
        FROM logs l
        LEFT JOIN users_login u
        ON l.client_id = u.phone
    """

    conditions = []
    params = []

    # Date filter
    if selected_date != "":
        conditions.append("DATE(l.entry_time) = ?")
        params.append(selected_date)

    # Role filter
    if selected_role != "" and selected_role != "all":
        conditions.append("u.role = ?")
        params.append(selected_role)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY l.entry_time DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    # ---- PDF ----
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
    elements = []

    data = [["Name", "Dept", "Role", "Area", "Date", "Entry", "Exit"]]

    for r in rows:
        data.append([
            r[0] or "Unknown",
            r[1] or "-",
            r[2] or "-",
            r[3],
            r[4],
            r[5],
            r[6] or "Active"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="filtered_logs.pdf",
                     mimetype='application/pdf')




# ---------------- RUN SERVER ----------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)