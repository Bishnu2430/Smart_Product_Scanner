# 🏭 QR Code-Based Product Metadata Tracker

This project simulates a production line system where every product (e.g., biscuit packets, medicines, electronics) has a **unique QR code** containing detailed metadata. Each QR code is dynamically generated and linked to a specific product unit. The system can both generate and decode QR codes, enabling efficient product identification and tracking.

---

## 📦 Features

- 🔗 **Unique Product IDs** assigned to each record
- 📄 **QR Code Generation** for each product with metadata embedded
- 🖼️ **QR Code Image Saving** in a designated folder
- 🔍 **QR Code Decoding** to extract and display product metadata
- 🧠 Ready for integration with **ML models** for predictions
- 📀 Can be linked to a **database** for production-level use

---

## 🗓️ Data Fields

Each QR code contains the following product metadata:
- Product ID
- Product Name
- Category (e.g., Medicine, Food, Electronics)
- Price
- Manufacturing Date
- Expiry Date

---

## 💪 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

> Make sure you also have `zbar` installed on your system (needed by `pyzbar`).

---


This will:
- Load each QR image
- Decode the embedded product metadata
- Display the metadata in a readable format

---

## 📌 Example Output

**Decoded from `ANTA003.png`:**
```
Product ID: ANTA003
Name: Antacid
Category: Medicine
Price: ₹887.45
MFG: 2025-01-08
EXP: 2026-09-13
```

---

