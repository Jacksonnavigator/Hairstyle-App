import streamlit as st
from model import register_user, login_user, fetch_hairstylists, add_booking, add_or_edit_hairstylist

def main():
    st.title("Hairstylist Booking App")
    page = st.sidebar.selectbox("Navigate", ["Home", "Browse", "Bookings", "Profile Management"])

    if page == "Home":
        st.header("Welcome to the Hairstylist Booking App")
        choice = st.radio("Please choose an option:", ["Sign Up", "Login"])

        if choice == "Sign Up":
            st.subheader("Sign Up")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            user_type = st.selectbox("User Type", ["hairstylist", "client"])
            if st.button("Register"):
                result = register_user(username, password, user_type)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(f"Error: {result['message']}")

        elif choice == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Log In"):
                user = login_user(username, password)
                if user:
                    st.success(f"Welcome, {user['username']}! You are logged in as a {user['user_type']}.")
                    st.session_state["user"] = user
                else:
                    st.error("Invalid username or password.")

    elif page == "Browse":
        st.header("Browse Hairstylists")
        location = st.text_input("Enter your location for nearby stylists:")
        if st.button("Search"):
            stylists = fetch_hairstylists(location)
            if stylists:
                for stylist in stylists:
                    st.write(f"**Name:** {stylist['name']}  ")
                    st.write(f"**Location:** {stylist['location']}  ")
                    st.write(f"**Rating:** {stylist['rating']}  ")
                    st.write(f"**Styles:** {stylist['styles']}  ")
                    st.write("---")
            else:
                st.info("No hairstylists found in your area.")

    elif page == "Bookings":
        st.header("Manage Bookings")
        if "user" not in st.session_state or st.session_state["user"]["user_type"] != "client":
            st.warning("You need to log in as a client to manage bookings.")
            return

        stylist_id = st.number_input("Enter Stylist ID", min_value=1, step=1)
        date = st.date_input("Choose a Date")
        time = st.time_input("Choose a Time")
        service_type = st.selectbox("Service Type", ["Home", "Salon"])
        price = st.number_input("Enter Price", min_value=0.0, step=0.01)
        if st.button("Book Now"):
            add_booking(
                client_id=st.session_state["user"]["id"],
                stylist_id=stylist_id,
                date=date.isoformat(),
                time=time.strftime("%H:%M"),
                service_type=service_type,
                price=price
            )
            st.success("Booking request submitted successfully.")

    elif page == "Profile Management":
        st.header("Profile Management")
        if "user" not in st.session_state:
            st.warning("You need to log in to manage your profile.")
            return

        user_type = st.session_state["user"]["user_type"]
        if user_type == "hairstylist":
            st.subheader("Manage Hairstylist Profile")
            name = st.text_input("Name")
            location = st.text_input("Location")
            availability = st.text_input("Availability")
            image_bytes = None  # Add file uploader for profile picture if needed

            if st.button("Save Profile"):
                add_or_edit_hairstylist(
                    user_id=st.session_state["user"]["id"],
                    name=name,
                    styles=None,  # This will be handled by individual style uploads
                    salon_price=0,  # Placeholder
                    home_price=0,  # Placeholder
                    availability=availability,
                    location=location,
                    image_bytes=image_bytes
                )
                st.success("Profile updated successfully.")

            st.subheader("Upload Hairstyles")
            style_name = st.text_input("Hairstyle Name")
            style_price = st.number_input("Price", min_value=0.0, step=0.01)
            style_image = st.file_uploader("Upload Hairstyle Image", type=["png", "jpg", "jpeg"])

            if st.button("Add Hairstyle"):
                if style_name and style_price and style_image:
                    image_bytes = style_image.read()
                    add_or_edit_hairstylist(
                        user_id=st.session_state["user"]["id"],
                        name=name,
                        styles=f"{style_name}: {style_price}",
                        salon_price=style_price,
                        home_price=style_price,  # Assuming same price for simplicity
                        availability=availability,
                        location=location,
                        image_bytes=image_bytes
                    )
                    st.success(f"Hairstyle '{style_name}' added successfully.")
                else:
                    st.error("Please provide all hairstyle details and upload an image.")

        elif user_type == "client":
            st.subheader("Manage Client Profile")
            name = st.text_input("Full Name")
            contact_info = st.text_input("Contact Information")
            if st.button("Save Profile"):
                st.success("Client profile updated successfully.")

if __name__ == "__main__":
    main()
