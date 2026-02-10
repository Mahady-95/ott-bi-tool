from fastapi import FastAPI
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

# Phase 1: Metrics API
@app.get("/metrics/dau")
def dau():
    conn = get_db_connection()
    if not conn:
        return {"error": "DB connection failed"}
    cursor = conn.cursor()
    #query = "SELECT COUNT(DISTINCT user_id) as dau FROM watch_logs WHERE watch_date = CURDATE();"
    query = "SELECT COUNT(DISTINCT user_id) as dau FROM watch_logs;"

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"metric": "DAU", "value": result[0]}
