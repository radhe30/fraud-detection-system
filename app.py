from flask import Flask, request, jsonify
from model.predict import predict_transaction
from utils.feature_builder import build_feature_vector
from utils.db import transactions_collection

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return "Fraud Detection API is running!"

# Fraud check route
@app.route("/check_transaction", methods=["POST"])
def check_transaction():

    data = request.json

    # Convert user input → model format
    features = build_feature_vector(data)

    # Get prediction + risk score
    prediction, risk_score = predict_transaction(features)

    # Save transaction to MongoDB
    record = data.copy()
    record["prediction"] = prediction
    record["risk_score"] = risk_score

    transactions_collection.insert_one(record)

    return jsonify({
        "prediction": prediction,
        "risk_score": risk_score
    })


if __name__ == "__main__":
    app.run(debug=True)
