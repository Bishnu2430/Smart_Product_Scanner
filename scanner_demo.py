# scanner_demo.py
from pyzbar.pyzbar import decode
from paddleocr import PaddleOCR
import cv2
from PIL import Image
import numpy as np
import re

# Initialize OCR model once
ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

# Utility function to extract structured fields from QR data
def parse_qr_data(data):
    """
    Parses structured QR data into fields: product_id, name, category, price, mfg, expiry.
    Accepts data in key:value format separated by commas or newlines.
    """
    fields = {
        "product_id": "",
        "name": "",
        "category": "",
        "price": "",
        "mfg_date": "",
        "expiry_date": ""
    }

    # Remove currency symbols from price field
    data = re.sub(r'[₹$€£¥]', '', data)

    # Normalize and split
    data_lines = re.split(r'[\n,]+', data)
    for line in data_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            if "id" in key:
                fields["product_id"] = value
            elif "name" in key:
                fields["name"] = value
            elif "category" in key:
                fields["category"] = value
            elif "price" in key:
                fields["price"] = value
            elif "mfg" in key:
                fields["mfg_date"] = value
            elif "exp" in key:
                fields["expiry_date"] = value

    return fields

def decode_barcode(frame):
    pil_image = Image.fromarray(frame)
    barcodes = decode(pil_image)
    barcode_data = []

    for barcode in barcodes:
        raw_data = barcode.data.decode("utf-8")
        cleaned_fields = parse_qr_data(raw_data)
        barcode_type = barcode.type
        polygon = [(point.x, point.y) for point in barcode.polygon]

        barcode_data.append({
            "raw": raw_data,
            "type": barcode_type,
            "rect": polygon,
            **cleaned_fields
        })

    return barcode_data

def extract_text_from_frame(frame):
    result = ocr_model.ocr(frame, cls=True)
    ocr_text = []

    for line in result[0]:
        text, confidence = line[1]
        if confidence > 0.6:
            ocr_text.append(text)

    return "\n".join(ocr_text)

def process_frame(frame, mode="Auto"):
    results = {"QR Codes": [], "OCR Text": ""}

    qr_data = []
    if mode in ["Auto", "QR Only"]:
        qr_data = decode_barcode(frame)
        if qr_data:
            results["QR Codes"] = qr_data

    if mode in ["Auto", "Text Only"] and not qr_data:
        try:
            results["OCR Text"] = extract_text_from_frame(frame)
        except Exception as e:
            print(f"[OCR Error] {e}")
            results["OCR Text"] = "[OCR Error]"

    return results
