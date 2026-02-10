from fastapi import FastAPI, Query
import mysql.connector
from mysql.connector import Error

app = FastAPI()

# DB config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ott_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to DB: {e}")
        return None

@app.get("/")
def health():
    return {"status": "OK", "message": "OTT BI Tool is running"}

@app.get("/metrics")
def metrics(
    metric: str = Query(..., description="metric name: dau, mau, total_watch_time"),
    country: str = Query(None, description="Country filter, optional"),
    plan: str = Query(None, description="Subscription plan filter, optional")
):
    conn = get_db_connection()
    if not conn:
        return {"error": "DB connection failed"}
    cursor = conn.cursor()

    # Build WHERE clause dynamically
    where_clauses = []
    if country:
        where_clauses.append(f"u.country = '{country}'")
    if plan:
        where_clauses.append(f"s.plan = '{plan}'")
    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = " AND " + where_sql

    result = None

    if metric.lower() == "dau":
        query = f"""
            SELECT COUNT(DISTINCT wl.user_id) 
            FROM watch_logs wl
            JOIN users u ON wl.user_id = u.id
            JOIN subscriptions s ON wl.user_id = s.user_id
            WHERE wl.watch_date = CURDATE() {where_sql};
        """
    elif metric.lower() == "mau":
        query = f"""
            SELECT COUNT(DISTINCT wl.user_id)
            FROM watch_logs wl
            JOIN users u ON wl.user_id = u.id
            JOIN subscriptions s ON wl.user_id = s.user_id
            WHERE wl.watch_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) {where_sql};
        """
    elif metric.lower() == "total_watch_time":
        query = f"""
            SELECT SUM(wl.watch_time_minutes)
            FROM watch_logs wl
            JOIN users u ON wl.user_id = u.id
            JOIN subscriptions s ON wl.user_id = s.user_id
            WHERE 1=1 {where_sql};
        """
    else:
        return {"error": "Unknown metric"}

    cursor.execute(query)
    value = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return {"metric": metric.lower(), "value": value if value else 0}
