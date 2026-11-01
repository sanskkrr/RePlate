import requests
import streamlit as st
from config import API_BASE_URL


def get_headers():
    token = st.session_state.get("access_token")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# AUTHENTICATION

def register_user(data):
    try:
        return requests.post(
            f"{API_BASE_URL}/auth/register",
            json=data,
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def login_user(email, password):
    try:
        return requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def get_current_user(token):
    try:
        return requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


# DONATION MANAGEMENT

def create_donation(data):
    try:
        return requests.post(
            f"{API_BASE_URL}/donations/",
            json=data,
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def get_my_donations():
    try:
        return requests.get(
            f"{API_BASE_URL}/donations/my-donations",
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def get_available_donations():
    try:
        return requests.get(
            f"{API_BASE_URL}/donations/",
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def cancel_donation(donation_id):
    try:
        return requests.delete(
            f"{API_BASE_URL}/donations/{donation_id}",
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None

# NGO MANAGEMENT

def request_donation(donation_id, data):
    try:
        return requests.post(
            f"{API_BASE_URL}/claims/",
            params={"donation_id": donation_id},
            json=data,
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def get_my_requests():
    try:
        return requests.get(
            f"{API_BASE_URL}/claims/my-requests",
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


# VOLUNTEER MANAGEMENT
def get_my_pickups():
    try:
        return requests.get(
            f"{API_BASE_URL}/pickups/my-pickups",
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None


def confirm_pickup(pickup_id, verification_code):
    try:
        return requests.patch(
            f"{API_BASE_URL}/pickups/{pickup_id}/confirm-pickup",
            json={"verification_code": verification_code},
            headers=get_headers(),
            timeout=10
        )
    except requests.RequestException as e:
        st.error(str(e))
        return None