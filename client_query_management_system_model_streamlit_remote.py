# client_query_management_system_model_streamlit_remote.py

import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import hashlib

# Database connection (using Streamlit Secrets)
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database (create tables and insert default users + client_queries)
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role ENUM('Client', 'Support') NOT NULL
        )
    """)

    # Create client_queries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_queries (
            query_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) NOT NULL,
            mobile VARCHAR(20) NOT NULL,
            heading VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            status ENUM('Open', 'Closed') DEFAULT 'Open',
            query_created_time DATETIME NOT NULL,
            query_closed_time DATETIME
        )
    """)

    # Insert default users
    default_users = [
        ("vishal", "password", "Client"),
        ("support1", "password", "Support")
    ]
    for username, password, role in default_users:
        h = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT IGNORE INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
            (username, h, role)
        )

    conn.commit()
    conn.close()

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
    init_db()
    login()

if __name__ == "__main__":
    main()
