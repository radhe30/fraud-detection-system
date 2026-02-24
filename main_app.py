import streamlit as st
import requests
from pymongo import MongoClient
import pandas as pd

# ===== CONFIG =====
st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="💳",
    layout="wide"
)

st.title("💳 AI Fraud Detection System")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["Customer Transaction", "Admin Dashboard"]
)

# ===============================
# 💳 CUSTOMER TRANSACTION PAGE
# ===============================
if page == "Customer Transaction":

    st.header("🧾 Simulate a Payment")

    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Amount (₹)", min_value=0.0)
        hour = st.slider("Transaction Hour", 0, 23, 12)
        age = st.number_input("Cardholder Age", 18, 100, 30)

    with col2:
        foreign = st.selectbox("Foreign Transaction", ["No", "Yes"])
        mismatch = st.selectbox("Location Mismatch", ["No", "Yes"])
        device_score = st.slider("Device Trust Score", 0.0, 1.0, 0.8)

    velocity = st.number_input("Transactions in Last 24h", 0, 50, 1)

    category = st.selectbox(
        "Merchant Category",
        ["Electronics", "Food", "Travel", "Clothing", "Health"]
    )

    foreign_val = 1 if foreign == "Yes" else 0
    mismatch_val = 1 if mismatch == "Yes" else 0

    if st.button("🔍 Analyze Transaction"):

        payload = {
            "amount": amount,
            "transaction_hour": hour,
            "foreign_transaction": foreign_val,
            "location_mismatch": mismatch_val,
            "device_trust_score": device_score,
            "velocity_last_24h": velocity,
            "cardholder_age": age,
            "merchant_category": category
        }

        try:
            response = requests.post(
                "http://127.0.0.1:5000/check_transaction",
                json=payload
            )

            result = response.json()

            st.subheader("📊 Result")

            colA, colB = st.columns(2)

            colA.metric("Prediction", result["prediction"])
            colB.metric("Risk Score", f'{result["risk_score"]}%')

            if result["prediction"] == "Fraud":
                st.error("🚨 High Risk Transaction — BLOCK")
            else:
                st.success("✅ Transaction Approved")

        except:
            st.error("⚠️ Backend API not running")

# ===============================
# 🛡️ ADMIN DASHBOARD PAGE
# ===============================
else:

    st.header("🛡️ Admin Dashboard")

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["fraud_detection_db"]
    collection = db["transactions"]

    data = list(collection.find())

    if len(data) == 0:
        st.warning("No transactions found.")
    else:
        for item in data:
            item["_id"] = str(item["_id"])

        df = pd.DataFrame(data)

        st.subheader("📋 All Transactions")
        st.dataframe(df, use_container_width=True)

        fraud_df = df[df["prediction"] == "Fraud"]

        st.subheader("🚨 Fraud Alerts")
        st.dataframe(fraud_df, use_container_width=True)

        st.subheader("📊 Statistics")

        total = len(df)
        fraud_count = len(fraud_df)

        st.write(f"Total Transactions: {total}")
        st.write(f"Fraudulent Transactions: {fraud_count}")

        if total > 0:
            st.write(
                f"Fraud Rate: {round((fraud_count/total)*100, 2)}%"
            )