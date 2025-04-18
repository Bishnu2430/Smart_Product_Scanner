# query_all.py
import sqlite3

DB_NAME = "products_demo.db"

def fetch_all_records():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    records = fetch_all_records()
    for record in records:
        print(record)
