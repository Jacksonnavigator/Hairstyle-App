import streamlit as st
import pandas as pd

# Data Storage (Temporary for Demo)
hairstylists = []
bookings = []

# Function to display hairstylists with styles
def display_hairstylists():
    if hairstylists:
        st.subheader("Available Hairstylists")
        for stylist in hairstylists:
            st.markdown(f"### {stylist['name']}")
            st.image(stylist['style_image'], use_column_width=True, caption=f"Styles: {stylist['styles']}")
            st.markdown(f"**Salon Price:** ${stylist['salon_price']} USD")
            st.markdown(f"**Home Service Price:** ${stylist['home_price']} USD")
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
                hairstylists.append({"name": name, "styles": styles, "salon_price": salon_price, "home_price": home_price, "style_image": style_image})
                st.success("Hairstylist profile added successfully!")
            else:
                st.error("Please upload an image of your hairstyle.")

    display_hairstylists()

elif page == "Client Booking":
    st.header("Client Booking")
    if not hairstylists:
        st.write("No hairstylists available for booking yet.")
    else:
        with st.form("booking_form"):
            stylist_name = st.selectbox("Select a hairstylist", [stylist['name'] for stylist in hairstylists])
            service_type = st.radio("Choose service type", ["Salon", "Home Service"])
            client_name = st.text_input("Enter your name")
            submit_booking = st.form_submit_button("Book Appointment")

            if submit_booking:
                selected_stylist = next(stylist for stylist in hairstylists if stylist['name'] == stylist_name)
                price = selected_stylist['salon_price'] if service_type == "Salon" else selected_stylist['home_price']

                bookings.append({"client": client_name, "stylist": stylist_name, "service": service_type, "price": price})
                st.success(f"Appointment booked with {stylist_name} for a {service_type.lower()} at ${price:.2f}!")

        # Display bookings
        if bookings:
            st.subheader("Bookings")
            for booking in bookings:
                st.markdown(f"**Client:** {booking['client']} | **Stylist:** {booking['stylist']} | **Service:** {booking['service']} | **Price:** ${booking['price']}")
