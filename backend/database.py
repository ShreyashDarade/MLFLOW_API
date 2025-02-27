import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "ml_dashboard"
}

def get_db_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn
