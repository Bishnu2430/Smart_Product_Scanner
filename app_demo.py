import streamlit as st
import time
import cv2
import requests
from scanner_demo import process_frame
from db_demo import (
    init_db,
    insert_product_qr,
    insert_ocr_data,
    get_recent_scans,
    get_inventory,
    update_inventory_stock,
    log_sale,
    suggest_restock
)
import numpy as np
import pandas as pd
import uuid

# Initialize DB
init_db()

# UI Config
st.set_page_config(page_title="Smart Product Scanner", layout="wide", page_icon="📦")
st.title("📦 Smart Product Scanner")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Settings")
    scan_mode = st.radio("Scan Mode", ["Auto", "QR Only", "Text Only"])
    scan_toggle = st.toggle("📷 Start Live Scanning")

# Prevent duplicate QR insertions
if "last_qr" not in st.session_state:
    st.session_state.last_qr = None

# Camera Feed Setup
cap = cv2.VideoCapture("http://192.168.237.124:8080/video")  # Update if needed

# Layout columns
col1, col2 = st.columns([1.1, 1.5])

with col1:
    st.subheader("📷 Live Camera Feed")
    frame_placeholder = st.empty()

with col2:
    results_placeholder = st.container()

def get_demand_prediction(product_id):
    try:
        url = "http://127.0.0.1:5000/predict"
        avg_daily_usage = 10
        total_usage = 100
        current_stock = 20
        data = {
            "avg_daily_usage": avg_daily_usage,
            "total_usage": total_usage,
            "current_stock": current_stock
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Error calling prediction API: {str(e)}")
        return None

if cap.isOpened() and scan_toggle:
    ret, frame = cap.read()
    if ret and frame is not None and frame.size != 0:
        frame_resized = cv2.resize(frame, (640, 480))
        _, img_bytes = cv2.imencode(".jpg", frame_resized)
        frame_placeholder.image(img_bytes.tobytes(), channels="BGR")

        results = process_frame(frame_resized, mode=scan_mode)

        with results_placeholder:
            st.subheader("🔍 Scan Result")
            if results["QR Codes"]:
                for qr in results["QR Codes"]:
                    raw_data = qr.get("raw", "")
                    product_id = qr.get("product_id", "")
                    name = qr.get("name", "")
                    category = qr.get("category", "")
                    price = qr.get("price", "")
                    mfg_date = qr.get("mfg_date", "")
                    expiry_date = qr.get("expiry_date", "")

                    insert_product_qr(product_id, name, category, price, mfg_date, expiry_date)
                    st.session_state.last_qr = raw_data

                    log_sale(product_id, 1)
                    suggest_restock(product_id)

                    prediction_data = get_demand_prediction(product_id)
                    if prediction_data:
                        is_profitable = prediction_data.get("prediction", 0)
                        message = prediction_data.get("message", "")
                        if is_profitable == 1:
                            st.warning(f"⚠️ Product {product_id} is in high demand and is potentially profitable!")
                        else:
                            st.success(f"✅ Product {product_id} is performing well. Message: {message}")

                    st.markdown(f"**Product ID**: {product_id}")
                    st.markdown(f"**Name**: {name}")
                    st.markdown(f"**Category**: {category}")
                    st.markdown(f"**Price**: {price}")
                    st.markdown(f"**MFG**: {mfg_date}")
                    st.markdown(f"**EXP**: {expiry_date}")
            else:
                st.write("No QR code detected.")

            if scan_mode in ["Auto", "Text Only"] and not results["QR Codes"]:
                st.subheader("📝 OCR Text")
                ocr_text = results["OCR Text"]
                if ocr_text.strip() and ocr_text != "[OCR Error]":
                    insert_ocr_data(ocr_text)
                st.text_area("Text", ocr_text, height=150, key=f"ocr_text_{uuid.uuid4()}")

    else:
        st.warning("⚠️ Could not read frame from camera.")
    time.sleep(0.3)

else:
    if not cap.isOpened():
        st.error("🚫 Could not connect to the camera stream.")
    elif not scan_toggle:
        st.info("🔄 Toggle 'Start Live Scanning' to begin.")

st.markdown("---")
st.header("📚 Previous Scans")

recent_scans = get_recent_scans(limit=10)

if recent_scans:
    df = pd.DataFrame(recent_scans)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No scans recorded yet.")

st.markdown("---")
st.header("📦 Inventory Overview")

inventory = get_inventory()

if inventory:
    df_inv = pd.DataFrame(inventory, columns=["Product ID", "Name", "Stock"])

    st.subheader("🔍 Search & Filter")
    col1, col2 = st.columns([2, 1])

    with col1:
        name_filter = st.text_input("Search by Product Name")
    with col2:
        stock_range = st.slider("Stock Range", 0, 100, (0, 100))

    filtered_df = df_inv[
        df_inv["Name"].str.contains(name_filter, case=False, na=False) &
        df_inv["Stock"].between(stock_range[0], stock_range[1])
    ]

    st.subheader("📊 Filtered Inventory")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("No inventory records found.")

st.sidebar.subheader("🔄 Restock Inventory")

with st.sidebar.form("restock_form"):
    restock_id = st.text_input("Product ID to Restock")
    add_stock = st.number_input("Add Stock Quantity", min_value=1, step=1)
    restock_submit = st.form_submit_button("✅ Update Stock")

    if restock_submit:
        if restock_id:
            update_inventory_stock(restock_id, add_stock)
            st.sidebar.success(f"Updated stock for Product ID {restock_id} by +{add_stock}")
        else:
            st.sidebar.warning("Please enter a valid Product ID.")

st.markdown("---")
st.header("🧠 AI Restock Suggestions")

restock_messages = []

for row in inventory:
    product_id = row[0]
    suggestion = suggest_restock(product_id)
    if suggestion and "Restock suggestion" in suggestion:
        restock_messages.append(suggestion)

if restock_messages:
    for msg in restock_messages:
        st.warning(msg)
else:
    st.success("✅ All products have sufficient stock.")