import streamlit as st
from datetime import datetime, date, time
from api import (
    register_user,
    login_user,
    get_current_user,
    create_donation,
    get_my_donations,
    cancel_donation,
    get_available_donations,
    request_donation,
    get_my_requests,
    get_my_pickups,
    confirm_pickup
)
from analytics import show_analytics
from map_view import show_donation_map
st.set_page_config(
    page_title="RePlate | Food Rescue",
    page_icon="🍃",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #F5F8F5;
}

h1, h2, h3 {
    color: #1B4332;
}

[data-testid="stWidgetLabel"] p {
    color: #344E41 !important;
}

input, textarea {
    background-color: white !important;
    color: #1B4332 !important;
}

.stButton button {
    background-color: #238653;
    color: white !important;
    border-radius: 8px;
    border: none;
}

.stButton button:hover {
    background-color: #174D35;
}

[data-testid="stForm"] {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #E1EAE3;
}
</style>
""", unsafe_allow_html=True)


# ---------------- LOGIN ----------------

def login_page():

    st.title("🍃 RePlate")
    st.subheader("Rescue Food. Reduce Waste. Feed Lives.")

    with st.form("login_form"):

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:

            response = login_user(email, password)

            if response is not None and response.status_code == 200:

                token = response.json()["access_token"]
                user_response = get_current_user(token)

                if user_response is not None and user_response.status_code == 200:

                    st.session_state.access_token = token
                    st.session_state.user = user_response.json()
                    st.session_state.logged_in = True
                    st.rerun()

                else:
                    st.error("Unable to retrieve account details.")

            elif response is not None:
                st.error(response.json().get("detail", "Login failed."))


# ---------------- REGISTRATION ----------------

def registration_page():

    st.title("Create Your RePlate Account")

    role = st.selectbox(
        "Register As",
        ["donor", "ngo", "volunteer"]
    )

    with st.form("registration_form"):

        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        organization_name = st.text_input("Organization / Business Name")
        address = st.text_area("Address")

        submitted = st.form_submit_button("Create Account")

        if submitted:

            if not full_name or not email or not password:
                st.warning("Please fill in all required fields.")

            else:

                data = {
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "phone": phone,
                    "organization_name": organization_name,
                    "address": address
                }

                response = register_user(data)

                if response is not None and response.status_code in [200, 201]:
                    st.success("Registration successful! Please login.")

                elif response is not None:
                    st.error(response.json().get("detail", "Registration failed."))


# ---------------- DONOR DASHBOARD ----------------

def donor_dashboard():

    user = st.session_state.user

    st.title("Donor Dashboard")
    st.write(f"Welcome back, {user.get('full_name', 'Donor')}!")
    st.caption("Manage surplus food and help reduce food waste.")

    response = get_my_donations()

    if response is None or response.status_code != 200:
        st.error("Unable to load donations.")
        return

    donations = response.json()

    if not isinstance(donations, list):
        donations = []

    # Statistics

    total = len(donations)
    available = sum(
        1 for d in donations if d.get("status") == "available"
    )
    claimed = sum(
        1 for d in donations if d.get("status") == "claimed"
    )
    completed = sum(
        1 for d in donations if d.get("status") == "completed"
    )

    st.markdown("### Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Donations", total)
    col2.metric("Available", available)
    col3.metric("Claimed", claimed)
    col4.metric("Completed", completed)

    st.divider()

    # Navigation

    tab1, tab2, tab3 = st.tabs([
    "➕ Create Donation",
    "📦 My Donations",
    "📊 Analytics"
    ])

    # CREATE DONATION

    with tab1:

        st.subheader("Share Surplus Food")
        st.write("Provide details about the food you want to donate.")

        with st.form("donation_form"):

            food_name = st.text_input("Food Name")

            food_category = st.selectbox(
                "Food Category",
                [
                    "Cooked Meals",
                    "Bakery Products",
                    "Fruits",
                    "Vegetables",
                    "Packaged Food",
                    "Dairy Products",
                    "Other"
                ]
            )

            description = st.text_area("Food Description")

            c1, c2 = st.columns(2)

            with c1:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=10
                )

            with c2:
                quantity_unit = st.selectbox(
                    "Quantity Unit",
                    ["portions", "kg", "packets", "boxes", "litres"]
                )

            st.markdown("#### Food Timing")

            c1, c2 = st.columns(2)

            with c1:
                preparation_date = st.date_input(
                    "Preparation Date",
                    value=date.today()
                )

                preparation_clock = st.time_input(
                    "Preparation Time",
                    value=time(10, 0)
                )

            with c2:
                safe_date = st.date_input(
                    "Safe Until Date",
                    value=date.today()
                )

                safe_clock = st.time_input(
                    "Safe Until Time",
                    value=time(22, 0)
                )

            pickup_date = st.date_input(
                "Pickup Deadline Date",
                value=date.today()
            )

            pickup_clock = st.time_input(
                "Pickup Deadline Time",
                value=time(20, 0)
            )

            storage_conditions = st.text_input(
                "Storage Conditions",
                placeholder="Example: Refrigerated at 4°C"
            )

            pickup_address = st.text_area(
                "Pickup Address"
            )

            st.markdown("#### Location (Optional)")

            c1, c2 = st.columns(2)

            with c1:
                latitude = st.number_input(
                    "Latitude",
                    value=0.0,
                    format="%.6f"
                )

            with c2:
                longitude = st.number_input(
                    "Longitude",
                    value=0.0,
                    format="%.6f"
                )

            submitted = st.form_submit_button(
                "Publish Food Donation",
                use_container_width=True
            )

            if submitted:

                if not food_name or not pickup_address:
                    st.warning("Food name and pickup address are required.")

                else:

                    preparation_time = datetime.combine(
                        preparation_date,
                        preparation_clock
                    ).astimezone().isoformat()

                    safe_until = datetime.combine(
                        safe_date,
                        safe_clock
                    ).astimezone().isoformat()

                    pickup_deadline = datetime.combine(
                        pickup_date,
                        pickup_clock
                    ).astimezone().isoformat()

                    if not (
                        preparation_time < pickup_deadline <= safe_until
                    ):
                        st.error(
                            "Check the dates and times. "
                            "Pickup deadline must be after preparation "
                            "and no later than the safe-until time."
                        )

                    else:

                        data = {
                            "food_name": food_name,
                            "food_category": food_category,
                            "description": description,
                            "quantity": quantity,
                            "quantity_unit": quantity_unit,
                            "preparation_time": preparation_time,
                            "safe_until": safe_until,
                            "pickup_deadline": pickup_deadline,
                            "storage_conditions": storage_conditions,
                            "pickup_address": pickup_address
                        }

                        if latitude != 0.0:
                            data["latitude"] = latitude

                        if longitude != 0.0:
                            data["longitude"] = longitude

                        result = create_donation(data)

                        if result is not None and result.status_code in [200, 201]:
                            st.success("Food donation published successfully!")
                            st.rerun()

                        elif result is not None:
                            st.error(
                                result.json().get(
                                    "detail",
                                    "Unable to create donation."
                                )
                            )

    # MY DONATIONS

    with tab2:

        st.subheader("Your Donation History")

        if not donations:

            st.info("You haven't published any donations yet.")

        else:

            for donation in donations:

                with st.container(border=True):

                    c1, c2 = st.columns([3, 1])

                    with c1:

                        st.markdown(
                            f"### {donation.get('food_name', 'Food Donation')}"
                        )

                        st.write(
                            donation.get("description", "No description")
                        )

                        st.write(
                            f"**Quantity:** "
                            f"{donation.get('quantity')} "
                            f"{donation.get('quantity_unit')}"
                        )

                        st.write(
                            f"**Pickup Address:** "
                            f"{donation.get('pickup_address')}"
                        )

                        st.write(
                            f"**Pickup Deadline:** "
                            f"{donation.get('pickup_deadline')}"
                        )

                    with c2:

                        status = donation.get("status", "unknown")

                        st.markdown("**Status**")
                        st.write(status.upper())

                        donation_id = donation.get("id")

                        if status == "available":

                            if st.button(
                                "Cancel Donation",
                                key=f"cancel_{donation_id}"
                            ):

                                result = cancel_donation(donation_id)

                                if result is not None and result.status_code in [200, 204]:
                                    st.success("Donation cancelled.")
                                    st.rerun()

                                elif result is not None:
                                    st.error(
                                        result.json().get(
                                            "detail",
                                            "Cancellation failed."
                                        )
                                    )
    with tab3:
        show_analytics(donations)

# ---------------- OTHER DASHBOARDS ----------------

def ngo_dashboard():

    user = st.session_state.user

    st.title("NGO Dashboard")
    st.write(f"Welcome, {user.get('full_name', 'NGO')}!")
    st.caption("Discover surplus food and help feed communities.")

    # Fetch available donations
    response = get_available_donations()

    if response is None or response.status_code != 200:
        st.error("Unable to load available donations.")
        return

    donations = response.json()

    if not isinstance(donations, list):
        donations = []

    # Fetch NGO requests
    request_response = get_my_requests()

    requests_list = []

    if request_response is not None and request_response.status_code == 200:
        requests_list = request_response.json()

        if not isinstance(requests_list, list):
            requests_list = []

    # Statistics
    total_available = len(donations)
    total_requests = len(requests_list)

    accepted = sum(
        1 for r in requests_list
        if r.get("status") == "accepted"
    )

    pending = sum(
        1 for r in requests_list
        if r.get("status") == "pending"
    )

    st.subheader("Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Available Donations", total_available)
    c2.metric("My Requests", total_requests)
    c3.metric("Accepted", accepted)
    c4.metric("Pending", pending)

    st.divider()

    tab1, tab2, tab3 = st.tabs([
    "🍱 Explore Food",
    "📋 My Requests",
    "📍 Food Map"
    ])

    # EXPLORE FOOD

    with tab1:

        st.subheader("Available Food Donations")

        search = st.text_input(
            "Search food",
            placeholder="Search by food name..."
        )

        categories = sorted(set(
            d.get("food_category", "Other")
            for d in donations
        ))

        selected_category = st.selectbox(
            "Filter by Category",
            ["All"] + categories
        )

        filtered = donations

        if search:
            filtered = [
                d for d in filtered
                if search.lower() in d.get("food_name", "").lower()
            ]

        if selected_category != "All":
            filtered = [
                d for d in filtered
                if d.get("food_category") == selected_category
            ]

        if not filtered:
            st.info("No matching food donations available.")

        for donation in filtered:

            with st.container(border=True):

                st.subheader(donation.get("food_name", "Food Donation"))

                c1, c2 = st.columns(2)

                with c1:
                    st.write(
                        f"**Category:** {donation.get('food_category')}"
                    )
                    st.write(
                        f"**Quantity:** {donation.get('quantity')} "
                        f"{donation.get('quantity_unit')}"
                    )
                    st.write(
                        f"**Address:** {donation.get('pickup_address')}"
                    )

                with c2:
                    st.write(
                        f"**Safe Until:** {donation.get('safe_until')}"
                    )
                    st.write(
                        f"**Pickup Deadline:** "
                        f"{donation.get('pickup_deadline')}"
                    )

                st.write(
                    donation.get("description", "No description available.")
                )

                donation_id = donation.get("id")

                with st.expander("Request This Donation"):

                    with st.form(f"claim_{donation_id}"):

                        beneficiaries = st.number_input(
                            "Number of Beneficiaries",
                            min_value=1,
                            value=20
                        )

                        message = st.text_area(
                            "Why do you need this donation?",
                            placeholder="Explain how this food will help your beneficiaries."
                        )

                        submitted = st.form_submit_button(
                            "Submit Request"
                        )

                        if submitted:

                            if not message.strip():
                                st.warning("Please provide a request message.")

                            else:

                                result = request_donation(
                                    donation_id,
                                    {
                                        "beneficiaries": beneficiaries,
                                        "message": message
                                    }
                                )

                                if result is not None and result.status_code in [200, 201]:
                                    st.success("Donation request submitted!")
                                    st.rerun()

                                elif result is not None:
                                    st.error(
                                        result.json().get(
                                            "detail",
                                            "Unable to submit request."
                                        )
                                    )

    # MY REQUESTS

    with tab2:

        st.subheader("My Donation Requests")

        if not requests_list:

            st.info("You haven't requested any donations yet.")

        else:

            for request in requests_list:

                with st.container(border=True):

                    st.write(
                        f"**Request ID:** {request.get('id')}"
                    )

                    st.write(
                        f"**Donation ID:** {request.get('donation_id')}"
                    )

                    st.write(
                        f"**Beneficiaries:** "
                        f"{request.get('beneficiaries')}"
                    )

                    st.write(
                        f"**Message:** {request.get('message')}"
                    )

                    status = request.get("status", "pending")

                    st.write(f"**Status:** {status.upper()}")

    with tab3:
        show_donation_map(donations)


def volunteer_dashboard():

    user = st.session_state.user

    st.title("Volunteer Dashboard")
    st.write(f"Welcome, {user.get('full_name', 'Volunteer')}!")
    st.caption("Help ensure every donated meal reaches someone in need.")

    response = get_my_pickups()

    if response is None or response.status_code != 200:
        st.error("Unable to load assigned pickups.")
        return

    pickups = response.json()

    if not isinstance(pickups, list):
        pickups = []

    scheduled = sum(
        1 for p in pickups if p.get("status") == "scheduled"
    )

    picked_up = sum(
        1 for p in pickups if p.get("status") == "picked_up"
    )

    delivered = sum(
        1 for p in pickups if p.get("status") == "delivered"
    )

    st.subheader("Your Activity")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Assignments", len(pickups))
    c2.metric("Awaiting Pickup", scheduled)
    c3.metric("Delivered", delivered)

    st.divider()

    st.subheader("Assigned Pickups")

    if not pickups:
        st.info("No pickups assigned to you yet.")

    for pickup in pickups:

        with st.container(border=True):

            pickup_id = pickup.get("id")

            st.subheader(f"Pickup #{pickup_id}")

            c1, c2 = st.columns(2)

            with c1:
                st.write(
                    f"**Pickup Address:** "
                    f"{pickup.get('pickup_address')}"
                )

                st.write(
                    f"**Delivery Address:** "
                    f"{pickup.get('delivery_address')}"
                )

            with c2:
                st.write(
                    f"**Scheduled Time:** "
                    f"{pickup.get('pickup_time')}"
                )

                st.write(
                    f"**Status:** "
                    f"{pickup.get('status', 'unknown').upper()}"
                )

            if pickup.get("status") == "scheduled":

                with st.form(f"pickup_form_{pickup_id}"):

                    otp = st.text_input(
                        "Enter pickup verification code",
                        max_chars=6
                    )

                    submitted = st.form_submit_button(
                        "Confirm Food Pickup"
                    )

                    if submitted:

                        if not otp.isdigit() or len(otp) != 6:
                            st.warning("Enter a valid 6-digit code.")

                        else:

                            result = confirm_pickup(
                                pickup_id,
                                otp
                            )

                            if result is not None and result.status_code == 200:
                                st.success("Food pickup confirmed!")
                                st.rerun()

                            elif result is not None:
                                st.error(
                                    result.json().get(
                                        "detail",
                                        "Pickup confirmation failed."
                                    )
                                )

            elif pickup.get("status") == "picked_up":

                st.info("Food picked up successfully. Awaiting NGO delivery confirmation.")

            elif pickup.get("status") == "delivered":

                st.success("Delivery completed successfully!")

# ---------------- MAIN ----------------

def main():

    if not st.session_state.logged_in:

        login_tab, register_tab = st.tabs(
            ["Login", "Create Account"]
        )

        with login_tab:
            login_page()

        with register_tab:
            registration_page()

    else:

        user = st.session_state.user

        with st.sidebar:

            st.title("🍃 RePlate")

            st.write(
                f"Welcome, {user.get('full_name', 'User')}"
            )

            st.caption(
                f"Role: {user.get('role', 'Unknown').upper()}"
            )

            st.divider()

            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

        role = user.get("role")

        if role == "donor":
            donor_dashboard()

        elif role == "ngo":
            ngo_dashboard()

        elif role == "volunteer":
            volunteer_dashboard()

        else:
            st.error("Unknown user role.")


if __name__ == "__main__":
    main()