from fastapi import FastAPI, Query, Body
import mysql.connector
from mysql.connector import Error
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "ott_db"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print("DB Error:", e)
        return None


@app.get("/")
def health():
    return {"status": "OK", "message": "OTT BI Tool is running"}


@app.get("/metrics")
def metrics(
    metric: str = Query(...),
    country: str = Query(None),
    plan: str = Query(None)
):
    conn = get_db_connection()
    if not conn:
        return {"error": "DB connection failed"}

    cursor = conn.cursor()

    where = []
    if country:
        where.append(f"u.country='{country}'")
    if plan:
        where.append(f"s.plan='{plan}'")

    where_sql = " AND ".join(where)
    if where_sql:
        where_sql = " AND " + where_sql

    if metric == "dau":
        query = f"""
        SELECT COUNT(DISTINCT wl.user_id)
        FROM watch_logs wl
        JOIN users u ON wl.user_id=u.id
        JOIN subscriptions s ON wl.user_id=s.user_id
        WHERE wl.watch_date=CURDATE() {where_sql}
        """
    elif metric == "mau":
        query = f"""
        SELECT COUNT(DISTINCT wl.user_id)
        FROM watch_logs wl
        JOIN users u ON wl.user_id=u.id
        JOIN subscriptions s ON wl.user_id=s.user_id
        WHERE wl.watch_date>=DATE_SUB(CURDATE(), INTERVAL 30 DAY) {where_sql}
        """
    elif metric == "total_watch_time":
        query = f"""
        SELECT SUM(wl.watch_time_minutes)
        FROM watch_logs wl
        JOIN users u ON wl.user_id=u.id
        JOIN subscriptions s ON wl.user_id=s.user_id
        WHERE 1=1 {where_sql}
        """
    else:
        return {"error": "Unknown metric"}

    cursor.execute(query)
    value = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    return {"metric": metric, "value": value}


# ---------------- DASHBOARD SAVE / LOAD ----------------

DASHBOARD_DIR = "dashboards"
os.makedirs(DASHBOARD_DIR, exist_ok=True)


@app.post("/dashboard/save")
def save_dashboard(payload: dict = Body(...)):
    name = payload.get("name")
    charts = payload.get("charts")

    if not name or not charts:
        return {"error": "Invalid payload"}

    path = f"{DASHBOARD_DIR}/{name}.json"
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    return {"status": "saved", "dashboard": name}


@app.get("/dashboard/load")
def load_dashboard(name: str):
    path = f"{DASHBOARD_DIR}/{name}.json"
    if not os.path.exists(path):
        return {"error": "Dashboard not found"}

    with open(path) as f:
        return json.load(f)
