import os
import pandas as pd
import qrcode

# Load CSV data
csv_file = 'qr_training_data.csv'  
output_folder = 'QR_Dump'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Read CSV
df = pd.read_csv(csv_file)

# Generate QR for each row
for index, row in df.iterrows():
    # Create a metadata string
    metadata = (
        f"Product ID: {row['product_id']}\n"
        f"Name: {row['product_name']}\n"
        f"Category: {row['category']}\n"
        f"Price: ₹{row['price']}\n"
        f"MFG: {row['mfg_date']}\n"
        f"EXP: {row['expiry_date']}"
    )
    
    # Ensure the metadata string is encoded in UTF-8 to handle special characters properly
    metadata = metadata.encode('utf-8')
    
    # Generate QR code
    qr = qrcode.QRCode(version=2, box_size=10, border=4)
    qr.add_data(metadata)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Save QR code image
    filename = f"{row['product_id']}.png"
    img.save(os.path.join(output_folder, filename))

print(f"✅ QR codes generated and saved in '{output_folder}' folder.")
