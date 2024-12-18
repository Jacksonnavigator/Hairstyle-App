import streamlit as st
from model import register_user, login_user, fetch_hairstylists, add_booking, add_or_edit_hairstylist

def main():
    st.title("Hairstylist Booking App")
    page = st.sidebar.selectbox("Choose Page", ["Sign Up", "Login", "View Hairstylists", "Book a Stylist", "Manage Profile"])

    if page == "Sign Up":
        st.header("Sign Up")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        user_type = st.selectbox("User Type", ["hairstylist", "client"])
        if st.button("Sign Up"):
            result = register_user(username, password, user_type)
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(f"Error: {result['message']}")

    elif page == "Login":
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome, {user['username']}! You are logged in as a {user['user_type']}.")
                st.session_state["user"] = user
            else:
                st.error("Invalid username or password.")

    elif page == "View Hairstylists":
        st.header("View Hairstylists")
        location = st.text_input("Search by Location")
        if st.button("Search"):
            stylists = fetch_hairstylists(location)
            if stylists:
                for stylist in stylists:
                    st.write(f"**Name:** {stylist['name']}  ")
                    st.write(f"**Location:** {stylist['location']}  ")
                    st.write(f"**Rating:** {stylist['rating']}  ")
                    st.write("---")
            else:
                st.info("No hairstylists found.")

    elif page == "Book a Stylist":
        st.header("Book a Hairstylist")
        if "user" not in st.session_state or st.session_state["user"]["user_type"] != "client":
            st.warning("You need to log in as a client to book a hairstylist.")
            return

        stylist_id = st.number_input("Enter Stylist ID", min_value=1, step=1)
        date = st.date_input("Select Date")
        time = st.time_input("Select Time")
        service_type = st.text_input("Service Type")
        price = st.number_input("Price", min_value=0.0, step=0.01)
        if st.button("Book Now"):
            add_booking(st.session_state["user"]["id"], stylist_id, date.isoformat(), time.strftime("%H:%M"), service_type, price)
            st.success("Booking request submitted successfully.")

    elif page == "Manage Profile":
        st.header("Manage Hairstylist Profile")
        if "user" not in st.session_state or st.session_state["user"]["user_type"] != "hairstylist":
            st.warning("You need to log in as a hairstylist to manage your profile.")
            return

        name = st.text_input("Name")
        styles = st.text_area("Styles Offered")
        salon_price = st.number_input("Salon Price", min_value=0.0, step=0.01)
        home_price = st.number_input("Home Service Price", min_value=0.0, step=0.01)
        availability = st.text_input("Availability")
        location = st.text_input("Location")
        image_bytes = None  # Add file uploader for image if needed

        if st.button("Save Profile"):
            add_or_edit_hairstylist(
                user_id=st.session_state["user"]["id"],
                name=name,
                styles=styles,
                salon_price=salon_price,
                home_price=home_price,
                availability=availability,
                location=location,
                image_bytes=image_bytes
            )
            st.success("Profile updated successfully.")

if __name__ == "__main__":
    main()
