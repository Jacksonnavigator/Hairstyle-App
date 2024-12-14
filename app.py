# app.py
import streamlit as st
from model import *

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_type = None
    st.session_state.booking_in_progress = False
    st.session_state.stylist_id = None

# User Authentication
st.sidebar.header("Log In")
if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Log In")

    if login_btn:
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.user_type = user[3]
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid username or password!")
else:
    st.sidebar.success(f"Logged in as {st.session_state.user_type.capitalize()}")

# Hairstylist Profile Management
if st.session_state.logged_in and st.session_state.user_type == 'hairstylist':
    st.title("Hairstylist Dashboard")
    with st.form("profile_form"):
        name = st.text_input("Name")
        styles = st.text_area("Describe Your Styles")
        salon_price = st.number_input("Salon Price", min_value=0.0)
        home_price = st.number_input("Home Service Price", min_value=0.0)
        availability = st.text_area("Availability (e.g., Mon-Fri 9am-5pm)")
        location = st.text_input("Your Location")
        style_image = st.file_uploader("Upload a Style Image", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Save Profile")

        if submit and style_image:
            if style_image.size > 2 * 1024 * 1024:
                st.error("Image file is too large. Please upload a file smaller than 2 MB.")
            elif not style_image.name.endswith(("jpg", "jpeg", "png")):
                st.error("Invalid file format. Please upload a JPG or PNG image.")
            else:
                image_bytes = style_image.read()
                add_or_edit_hairstylist(st.session_state.user_id, name, styles, salon_price, home_price, availability, location, image_bytes)
                st.success("Profile saved successfully!")

# Client Browsing Hairstylists
if st.session_state.logged_in and st.session_state.user_type == 'client':
    st.title("Browse Hairstylists")
    location_filter = st.text_input("Filter by Location (optional)")
    hairstylists = fetch_hairstylists(location_filter)

    for stylist in hairstylists:
        st.subheader(stylist[2])  # Name
        st.write(f"Styles: {stylist[3]}")
        st.write(f"Salon Price: ${stylist[4]}, Home Price: ${stylist[5]}")
        st.write(f"Location: {stylist[7]}")
        st.image(stylist[8], use_container_width=True)
        if st.button(f"Book {stylist[2]}"):
            st.session_state.stylist_id = stylist[0]
            st.session_state.booking_in_progress = True
            break

# Handle Booking (Booking Form)
if st.session_state.get("booking_in_progress"):
    stylist_id = st.session_state.get("stylist_id")
    stylist = fetch_stylist_by_id(stylist_id)

    st.title(f"Booking with Stylist {stylist[2]}")
    date = st.date_input("Select Booking Date")
    time = st.time_input("Select Time")
    service_type = st.selectbox("Choose Service Type", ["Salon", "Home"])
    price = stylist[4] if service_type == "Salon" else stylist[5]

    if st.button("Confirm Booking"):
        add_booking(st.session_state.user_id, stylist_id, date, time, service_type, price)
        st.success("Booking confirmed!")


# model.py
import sqlite3
import bcrypt

def get_db_connection():
    conn = sqlite3.connect('hairstylist_app.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
cursor = conn.cursor()

# Create Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    user_type TEXT -- 'hairstylist' or 'client'
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS hairstylists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    styles TEXT,
    salon_price REAL,
    home_price REAL,
    availability TEXT,
    location TEXT,
    style_image BLOB,
    rating REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    stylist_id INTEGER,
    date TEXT,
    time TEXT,
    service_type TEXT,
    price REAL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (client_id) REFERENCES users (id),
    FOREIGN KEY (stylist_id) REFERENCES hairstylists (id)
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stylist_id INTEGER,
    client_id INTEGER,
    rating INTEGER,
    comment TEXT,
    FOREIGN KEY (stylist_id) REFERENCES hairstylists (id),
    FOREIGN KEY (client_id) REFERENCES users (id)
)''')
conn.commit()

# User Authentication
def register_user(username, password, user_type):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                   (username, hashed_password, user_type))
    conn.commit()

def login_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

# Add/Edit Hairstylist Profile
def add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, image_bytes):
    cursor.execute('''
        INSERT OR REPLACE INTO hairstylists (user_id, name, styles, salon_price, home_price, availability, location, style_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, name, styles, salon_price, home_price, availability, location, image_bytes))
    conn.commit()

# Fetch Hairstylists
def fetch_hairstylists(location=None):
    query = 'SELECT * FROM hairstylists'
    params = []
    if location:
        query += " WHERE location LIKE ?"
        params.append(f"%{location}%")
    cursor.execute(query, params)
    return cursor.fetchall()

def fetch_stylist_by_id(stylist_id):
    cursor.execute('SELECT * FROM hairstylists WHERE id = ?', (stylist_id,))
    return cursor.fetchone()

# Booking
def add_booking(client_id, stylist_id, date, time, service_type, price):
    cursor.execute('''
        INSERT INTO bookings (client_id, stylist_id, date, time, service_type, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (client_id, stylist_id, date, time, service_type, price, 'pending'))
    conn.commit()
