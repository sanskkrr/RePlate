import streamlit as st
import pandas as pd
import plotly.express as px

def show_analytics(donations):

    st.title("RePlate Analytics")
    st.caption("Measuring our impact on food waste reduction.")

    if not donations:
        st.info("No donation data available yet.")
        return

    df = pd.DataFrame(donations)

    total_donations = len(df)

    completed = len(
        df[df["status"] == "completed"]
    ) if "status" in df else 0

    available = len(
        df[df["status"] == "available"]
    ) if "status" in df else 0

    claimed = len(
        df[df["status"] == "claimed"]
    ) if "status" in df else 0

    total_quantity = (
        df["quantity"].sum()
        if "quantity" in df else 0
    )

    st.subheader("Platform Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Donations", total_donations)
    c2.metric("Completed", completed)
    c3.metric("Available", available)
    c4.metric("Food Quantity", total_quantity)

    st.divider()

    st.subheader("Donation Status Distribution")

    if "status" in df.columns:

        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.5,
            title="Donation Status"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Food Category Distribution")

    if "food_category" in df.columns:

        category_counts = (
            df["food_category"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = ["Category", "Count"]

        fig = px.bar(
            category_counts,
            x="Category",
            y="Count",
            title="Donations by Food Category"
        )

        st.plotly_chart(fig, use_container_width=True)