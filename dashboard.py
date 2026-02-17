import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["fraud_detection_db"]
collection = db["transactions"]

st.title("💳 Fraud Detection Dashboard")

# Load data from MongoDB
data = list(collection.find())

if len(data) == 0:
    st.warning("No transactions found.")
else:
    df = pd.DataFrame(data)

    # Remove MongoDB ID column
    df = df.drop(columns=["_id"])

    st.subheader("📋 Transaction History")
    st.dataframe(df)

    # Show fraud alerts only
    st.subheader("🚨 Fraud Alerts")
    fraud_df = df[df["prediction"] == "Fraud"]

    if len(fraud_df) == 0:
        st.success("No fraud detected 🎉")
    else:
        st.dataframe(fraud_df)

    # Statistics
    st.subheader("📊 Statistics")

    total = len(df)
    fraud_count = len(fraud_df)

    st.write(f"Total Transactions: {total}")
    st.write(f"Fraudulent Transactions: {fraud_count}")
    st.write(f"Fraud Rate: {round((fraud_count/total)*100, 2)}%")
