import requests

# API endpoint
url = "http://localhost:5000/predict"

# Sample input data
data = {
    "avg_daily_usage": 12,
    "total_usage": 240,
    "current_stock": 8
}

# Send POST request
response = requests.post(url, json=data)

# Print response
if response.status_code == 200:
    result = response.json()
    print("✅ Prediction Result:")
    print(f"  → Prediction: {result['prediction']}")
    print(f"  → Message: {result['message']}")
else:
    print("❌ Error:")
    print(response.status_code, response.text)
