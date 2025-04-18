import os
from pyzbar.pyzbar import decode
from PIL import Image

# Folder containing QR code images
qr_folder = 'Dynamic_QR_Generation\QR_Dump'

# Iterate over all PNG images in the folder
for filename in os.listdir(qr_folder):
    if filename.endswith('.png'):
        img_path = os.path.join(qr_folder, filename)
        img = Image.open(img_path)

        decoded_objects = decode(img)
        if decoded_objects:
            print(f"\n🔍 Decoded from {filename}:")
            for obj in decoded_objects:
                decoded_data = obj.data.decode('utf-8')
                print(f"Decoded Data: {decoded_data}")
        else:
            print(f"\n⚠️ No QR code found in {filename}")
