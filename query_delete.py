import sqlite3

DB_NAME = "products_demo.db"

def delete_all_records():
    # Connect to the database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Execute DELETE query to remove all records from the 'products' table
    cursor.execute("DELETE FROM products")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("✅ All records deleted from the 'products' table.")

if __name__ == "__main__":
    delete_all_records()
