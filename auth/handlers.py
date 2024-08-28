import streamlit as st
from utils.supabase_client import supabase

def handle_confirmation():
    token = st.query_params.get("confirmation_token")
    
    if token:
        try:
            res = supabase.auth.verify_otp({"token": token[0], "type": "signup"})
            st.success("Email confirmed successfully! You can now log in.")
        except Exception as e:
            st.error(f"Confirmation failed: {str(e)}")
    else:
        st.warning("No confirmation token found in the URL.")

def logout():
    if st.sidebar.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.success("Logged out successfully!")
        st.rerun()
