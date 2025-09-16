# -*- coding: utf-8 -*-
"""cilent_query.ipynb (Modified for login flexibility + Streamlit rerun fix)"""

import pandas as pd
import mysql.connector
from datetime import datetime
import streamlit as st
import hashlib

# ----------------- UTILS -----------------
def hash_password(password):
    """Return SHA-256 hashed password"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    """Database connection"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="VISHAL$26498",   # change to your MySQL root password
        database="client_query_db"
    )

# ----------------- LOGIN -----------------
def login():
    st.title("Login")

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None

    if not st.session_state.logged_in:   # Show login form
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Client", "Support"])

        if st.button("Login"):
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Try match with hashed password
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND hashed_password=%s AND role=%s",
                (username, hash_password(password), role)
            )
            user = cursor.fetchone()

            # If not found, try plain-text password match (fallback)
            if not user:
                cursor.execute(
                    "SELECT * FROM users WHERE username=%s AND hashed_password=%s AND role=%s",
                    (username, password, role)
                )
                user = cursor.fetchone()

            conn.close()

            if user:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        # Sidebar with user info + logout
        st.sidebar.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.username = None
            st.rerun()

        # Redirect to role-specific page
        if st.session_state.role == "Client":
            client_page(st.session_state.username)
        else:
            support_page()

# ----------------- CLIENT PAGE -----------------
def client_page(username):
    st.subheader("Submit a New Query")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ You are not logged in. Please login again.")
        st.stop()

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

        st.success("✅ Query submitted successfully!")

# ----------------- SUPPORT PAGE -----------------
def support_page():
    st.subheader("Manage Client Queries")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM client_queries ORDER BY query_created_time DESC")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        st.write(f"ID: {row['query_id']} | {row['heading']} | Status: {row['status']} | Created: {row['query_created_time']}")
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
                st.success(f"✅ Query {row['query_id']} closed.")
                st.rerun()

# ----------------- MAIN -----------------
def main():
    login()

if __name__ == "__main__":
    main()