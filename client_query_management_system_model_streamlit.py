# client_query_management_system_model_streamlit.py

import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import hashlib

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="VISHAL$26498",  # ⚠️ Replace with environment variable in production
        database="client_query_db"
    )

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login page
def login():
    st.title("Client Query Management System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Client", "Support"])
    if st.button("Login"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND hashed_password=%s AND role=%s",
            (username, hash_password(password), role)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            st.success(f"Welcome {username}! Logged in as {role}")
            if role == "Client":
                client_page(username)
            else:
                support_page()
        else:
            st.error("Invalid credentials")

# Client page
def client_page(username):
    st.subheader("Submit a New Query")
    email = st.text_input("Email ID")
    mobile = st.text_input("Mobile Number")
    heading = st.text_input("Query Heading")
    description = st.text_area("Query Description")
    if st.button("Submit Query"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO client_queries (email, mobile, heading, description, status, query_created_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, mobile, heading, description, "Open", datetime.now()))
        conn.commit()
        conn.close()
        st.success("Query submitted successfully!")

# Support page
def support_page():
    st.subheader("Manage Client Queries")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM client_queries")
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        st.write(f"ID: {row['query_id']} | {row['heading']} | Status: {row['status']}")
        if row['status'] == "Open":
            if st.button(f"Close Query {row['query_id']}"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE client_queries SET status=%s, query_closed_time=%s WHERE query_id=%s",
                    ("Closed", datetime.now(), row['query_id'])
                )
                conn.commit()
                conn.close()
                st.success(f"Query {row['query_id']} closed.")

# Main function
def main():
    login()

if __name__ == "__main__":
    main()
