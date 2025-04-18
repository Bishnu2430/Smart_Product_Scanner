import sqlite3
import json
from datetime import datetime
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

DB_NAME = "products_demo.db"
OFFLINE_FILE = "unsynced_data_demo.json"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create products table with new schema
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            name TEXT,
            category TEXT,
            price REAL,
            mfg_date TEXT,
            expiry_date TEXT,
            timestamp TEXT,
            is_synced INTEGER DEFAULT 1,
            is_ocr INTEGER DEFAULT 0
        )
    ''')

    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            name TEXT,
            stock_quantity INTEGER
        )
    ''')

    # Create sales log table to track product sales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            quantity INTEGER,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()


def insert_product_qr(product_id, name, category, price, mfg_date, expiry_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into products table
    cursor.execute('''
        INSERT INTO products (product_id, name, category, price, mfg_date, expiry_date, timestamp, is_synced, is_ocr)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (product_id, name, category, price, mfg_date, expiry_date, timestamp, 1, 0))

    # Inventory management
    cursor.execute("SELECT stock_quantity FROM inventory WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    if row:
        # Product exists, decrement stock
        new_stock = max(0, row[0] - 1)
        cursor.execute("UPDATE inventory SET stock_quantity = ? WHERE product_id = ?", (new_stock, product_id))
    else:
        # New product, insert with default stock (e.g., 100 units)
        cursor.execute('''
            INSERT INTO inventory (product_id, name, stock_quantity)
            VALUES (?, ?, ?)
        ''', (product_id, name, 100))

    conn.commit()
    conn.close()


def insert_ocr_data(text):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
        INSERT INTO products (product_id, name, timestamp, is_synced, is_ocr)
        VALUES (?, ?, ?, ?, ?)
    ''', ("OCR", text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1))
    conn.commit()
    conn.close()


def get_recent_scans(limit=20):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT * FROM products ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows


def get_inventory():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT * FROM inventory ORDER BY name ASC").fetchall()
    conn.close()
    return rows


def update_inventory_stock(product_id, new_stock):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE inventory SET stock_quantity = ? WHERE product_id = ?", (new_stock, product_id))
    conn.commit()
    conn.close()


def log_sale(product_id, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log sale into sales_log table
    cursor.execute('''
        INSERT INTO sales_log (product_id, quantity, timestamp)
        VALUES (?, ?, ?)
    ''', (product_id, quantity, timestamp))

    conn.commit()
    conn.close()


def get_sales_data(product_id, start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get sales data for a specific product between two dates
    cursor.execute('''
        SELECT SUM(quantity), strftime('%Y-%m', timestamp) AS month
        FROM sales_log
        WHERE product_id = ? AND timestamp BETWEEN ? AND ?
        GROUP BY month
    ''', (product_id, start_date, end_date))

    data = cursor.fetchall()
    conn.close()
    return data



def train_demand_prediction_model(product_id, start_date, end_date):
    # Fetch sales data for the given product and date range
    sales_data = get_sales_data(product_id, start_date, end_date)
    
    # Check if we have enough data to train the model
    if len(sales_data) == 0:
        print(f"No sales data available for {product_id} from {start_date} to {end_date}.")
        return None

    # Prepare the data for training
    sales_data['date'] = pd.to_datetime(sales_data['date'])
    sales_data['day_of_year'] = sales_data['date'].dt.dayofyear
    X = sales_data[['day_of_year']]  # Use day of the year as feature
    y = sales_data['sales_count']  # Sales count as target variable

    # Check if there is enough data for training
    if len(X) < 2:  # We need at least two data points to fit a model
        print(f"Insufficient data for {product_id} to train demand model.")
        return None

    # Initialize and train the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    return model


def predict_demand_for_next_month(model):
    # Predict for the next month (assuming the next month is month 13)
    predicted_demand = model.predict(np.array([[13]]))  # Assuming month 13
    return predicted_demand[0]


def suggest_restock(product_id):
    # Set a reasonable date range for demand prediction
    start_date = '2024-01-01'
    end_date = '2024-12-31'

    # Train the demand prediction model
    model = train_demand_prediction_model(product_id, start_date, end_date)
    
    if model is None:
        print(f"No prediction model for {product_id}, skipping restocking suggestion.")
        return

    # Predict demand for the next period (e.g., the next 7 days)
    future_dates = pd.date_range(start=end_date, periods=7, freq='D')
    future_days = future_dates.dayofyear.values.reshape(-1, 1)
    
    predicted_sales = model.predict(future_days)

    # Calculate the total predicted demand for the next 7 days
    total_predicted_demand = predicted_sales.sum()

    # Get the current stock
    current_stock = get_inventory_stock(product_id)
    
    # Suggest restocking if the predicted demand exceeds current stock
    if total_predicted_demand > current_stock:
        restock_amount = total_predicted_demand - current_stock
        print(f"Restock suggestion for {product_id}: Add {restock_amount:.0f} units.")
        # Optionally, you can add restocking to the inventory
        update_inventory_stock(product_id, restock_amount)
    else:
        print(f"Current stock of {product_id} is sufficient. No restocking needed.")

    conn.close()
