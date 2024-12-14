import streamlit as st
import pandas as pd
import sqlite3

# Initialize SQLite database
conn = sqlite3.connect('hairstylist_app.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS hairstylists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    styles TEXT,
    salon_price REAL,
    home_price REAL,
    style_image BLOB
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    stylist_name TEXT,
    service_type TEXT,
    price REAL
)''')
conn.commit()

# Function to add a hairstylist
def add_hairstylist(name, styles, salon_price, home_price, style_image):
    cursor.execute('''INSERT INTO hairstylists (name, styles, salon_price, home_price, style_image)
                      VALUES (?, ?, ?, ?, ?)''', (name, styles, salon_price, home_price, style_image))
    conn.commit()

# Function to fetch all hairstylists
def get_hairstylists():
    cursor.execute('''SELECT * FROM hairstylists''')
    return cursor.fetchall()

# Function to add a booking
def add_booking(client_name, stylist_name, service_type, price):
    cursor.execute('''INSERT INTO bookings (client_name, stylist_name, service_type, price)
                      VALUES (?, ?, ?, ?)''', (client_name, stylist_name, service_type, price))
    conn.commit()

# Function to fetch all bookings
def get_bookings():
    cursor.execute('''SELECT * FROM bookings''')
    return cursor.fetchall()

# Function to display hairstylists with styles
def display_hairstylists():
    hairstylists = get_hairstylists()
    if hairstylists:
        st.subheader("Available Hairstylists")
        for stylist in hairstylists:
            st.markdown(f"### {stylist[1]}")
            st.image(stylist[5], use_column_width=True, caption=f"Styles: {stylist[2]}")
            st.markdown(f"**Salon Price:** ${stylist[3]} USD")
            st.markdown(f"**Home Service Price:** ${stylist[4]} USD")
            st.markdown("---")
    else:
        st.write("No hairstylists available yet.")

# App Layout
st.set_page_config(page_title="Hairstylist Booking App", layout="wide")
st.title("💇‍♀️ Hairstylist Booking App")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Hairstylist Dashboard", "Client Booking"])

if page == "Home":
    st.header("Welcome to the Hairstylist Booking App!")
    st.image("https://images.unsplash.com/photo-1516646255117-8a3b9ef9cc2a", use_column_width=True)
    st.write("This app connects hairstylists and clients. Hairstylists can showcase their services, and clients can book them for salon or home services.")
    st.write("\n**Features:**")
    st.markdown("- 🧑‍🎨 Hairstylists can create profiles and upload their styles.")
    st.markdown("- 👩‍💻 Clients can browse and book hairstylists.")
    st.markdown("- 💸 Dynamic pricing for home and salon services.")

elif page == "Hairstylist Dashboard":
    st.header("Hairstylist Dashboard")
    with st.form("hairstylist_form"):
        name = st.text_input("Enter your name")
        styles = st.text_area("Describe the styles you offer")
        salon_price = st.number_input("Set your salon price (USD)", min_value=0.0, step=1.0)
        home_price = st.number_input("Set your home service price (USD)", min_value=0.0, step=1.0)
        style_image = st.file_uploader("Upload an image of your hairstyle", type=["jpg", "png", "jpeg"])
        submit = st.form_submit_button("Add Hairstylist")

        if submit:
            if style_image:
                image_bytes = style_image.read()
                add_hairstylist(name, styles, salon_price, home_price, image_bytes)
                st.success("Hairstylist profile added successfully!")
            else:
                st.error("Please upload an image of your hairstyle.")

    display_hairstylists()

elif page == "Client Booking":
    st.header("Client Booking")
    hairstylists = get_hairstylists()
    if not hairstylists:
        st.write("No hairstylists available for booking yet.")
    else:
        with st.form("booking_form"):
            stylist_name = st.selectbox("Select a hairstylist", [stylist[1] for stylist in hairstylists])
            service_type = st.radio("Choose service type", ["Salon", "Home Service"])
            client_name = st.text_input("Enter your name")
            submit_booking = st.form_submit_button("Book Appointment")

            if submit_booking:
                selected_stylist = next(stylist for stylist in hairstylists if stylist[1] == stylist_name)
                price = selected_stylist[3] if service_type == "Salon" else selected_stylist[4]

                add_booking(client_name, stylist_name, service_type, price)
                st.success(f"Appointment booked with {stylist_name} for a {service_type.lower()} at ${price:.2f}!")

        # Display bookings
        bookings = get_bookings()
        if bookings:
            st.subheader("Bookings")
            for booking in bookings:
                st.markdown(f"**Client:** {booking[1]} | **Stylist:** {booking[2]} | **Service:** {booking[3]} | **Price:** ${booking[4]}")
