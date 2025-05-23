import sqlite3
from datetime import datetime

# Database connection
DB_NAME = "products_demo.db"

# Function to insert example scans
def insert_example_scans():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Example product data (decoded from images)
    example_scans = [
        ("ANTA001", "Antacid", "Medicine", 213.63, "2024-06-07", "2025-08-30"),
        ("ANTA002", "Antacid", "Medicine", 490.87, "2024-09-03", "2027-08-30"),
        ("ANTA003", "Antacid", "Medicine", 887.45, "2025-01-08", "2026-09-13"),
        ("BLUE001", "Bluetooth Speaker", "Electronics", 977.04, "2024-10-06", "2027-08-31"),
        ("BLUE002", "Bluetooth Speaker", "Electronics", 127.11, "2025-02-02", "2026-09-25"),
        ("BLUE003", "Bluetooth Speaker", "Electronics", 800.01, "2025-01-16", "2026-10-01"),
        ("COUG001", "Cough Syrup", "Medicine", 566.05, "2025-02-04", "2026-11-02"),
        ("COUG002", "Cough Syrup", "Medicine", 329.97, "2024-07-12", "2026-01-11"),
        ("FACE001", "Face Wash", "Cosmetics", 390.3, "2024-05-16", "2026-06-15"),
        ("HEAD001", "Headphones", "Electronics", 350.89, "2024-10-31", "2027-10-21"),
        ("LAYS001", "Lays Chips", "Food", 256.03, "2024-12-06", "2025-10-07"),
        ("LAYS002", "Lays Chips", "Food", 751.3, "2024-10-01", "2026-12-11"),
        ("OREO001", "Oreo Cookies", "Food", 467.3, "2025-02-05", "2026-09-26"),
        ("PARA001", "Paracetamol", "Medicine", 409.94, "2024-08-18", "2026-11-01"),
        ("PARA002", "Paracetamol", "Medicine", 475.41, "2024-11-11", "2027-07-03"),
        ("PARA003", "Paracetamol", "Medicine", 602.34, "2025-01-13", "2026-10-30"),
        ("PARA004", "Paracetamol", "Medicine", 474.27, "2025-02-03", "2026-01-05"),
        ("PARA005", "Paracetamol", "Medicine", 74.04, "2024-06-22", "2025-11-28"),
        ("PARA006", "Paracetamol", "Medicine", 509.13, "2025-02-24", "2027-02-12"),
        ("SHAM001", "Shampoo", "Cosmetics", 543.05, "2025-01-30", "2026-05-30"),
        ("SHAM002", "Shampoo", "Cosmetics", 900.23, "2024-07-03", "2026-04-04"),
        ("SHAM003", "Shampoo", "Cosmetics", 373.45, "2024-07-24", "2027-07-02"),
        ("SMAR001", "Smartphone", "Electronics", 963.56, "2024-09-29", "2025-07-13"),
        ("SUNS001", "Sunscreen", "Cosmetics", 585.5, "2024-08-30", "2025-12-11"),
        ("SUNS002", "Sunscreen", "Cosmetics", 815.25, "2025-01-02", "2025-12-21"),
        ("SUNS003", "Sunscreen", "Cosmetics", 748.44, "2024-11-15", "2027-03-19"),
        ("USBD001", "USB Drive", "Electronics", 774.25, "2024-06-03", "2025-07-30")
    ]

    # Insert scan data into the products table
    for product_id, name, category, price, mfg_date, expiry_date in example_scans:
        cursor.execute('''
            INSERT INTO products (product_id, name, category, price, mfg_date, expiry_date, timestamp, is_synced, is_ocr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, name, category, price, mfg_date, expiry_date, datetime.now().isoformat(), 1, 0))

    conn.commit()
    conn.close()
    print("Example scans inserted successfully!")

# Run the function
insert_example_scans()
