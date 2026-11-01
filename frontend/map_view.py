import streamlit as st
import folium
from streamlit_folium import st_folium


def show_donation_map(donations):

    st.subheader("Food Donations Near You")

    valid_donations = [
        donation for donation in donations
        if donation.get("latitude") is not None
        and donation.get("longitude") is not None
    ]

    if not valid_donations:
        st.info("No donation locations available yet.")
        return

    # Center map around the first donation
    first = valid_donations[0]

    map_object = folium.Map(
        location=[
            first["latitude"],
            first["longitude"]
        ],
        zoom_start=12
    )

    for donation in valid_donations:

        latitude = donation["latitude"]
        longitude = donation["longitude"]

        popup_html = f"""
        <b>{donation.get('food_name', 'Food Donation')}</b><br>
        Quantity: {donation.get('quantity')} {donation.get('quantity_unit')}<br>
        Address: {donation.get('pickup_address')}
        """

        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=donation.get("food_name", "Food Donation"),
            icon=folium.Icon(
                color="green",
                icon="cutlery",
                prefix="fa"
            )
        ).add_to(map_object)

    st_folium(
        map_object,
        width=None,
        height=500,
        use_container_width=True
    )

    st.caption(
        f"Showing {len(valid_donations)} donation locations."
    )