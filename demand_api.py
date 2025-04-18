from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model
try:
    model = joblib.load("profitable_demand_model.pkl")
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

@app.route("/")
def home():
    return "📦 Demand Prediction API is running!"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Parse input data
        data = request.json
        avg_daily_usage = data.get("avg_daily_usage")
        total_usage = data.get("total_usage")
        current_stock = data.get("current_stock")

        # Validate input
        if None in (avg_daily_usage, total_usage, current_stock):
            return jsonify({"error": "Missing input values"}), 400

        # Prepare input for model
        features = np.array([[avg_daily_usage, total_usage, current_stock]])

        # Predict
        prediction = model.predict(features)[0]
        result = "Profitable (High Demand)" if prediction == 1 else "Not Profitable (Low Demand)"

        # Return prediction result
        return jsonify({
            "prediction": int(prediction),
            "message": result
        })

    except Exception as e:
        # Return error in case of an exception
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Ensure port 5000 is not blocked by any firewall or other service
