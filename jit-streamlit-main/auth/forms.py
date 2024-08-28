import streamlit as st
from utils.supabase_client import supabase

def registration_form():
    st.subheader("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password == confirm_password:
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Registration successful! Please check your email to verify your account.")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")
        else:
            st.error("Passwords do not match")

def login_form():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = res.user
            st.success("Login successful!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

def password_reset_form():
    st.subheader("Reset Password")
    email = st.text_input("Email")
    
    if st.button("Send Reset Link"):
        try:
            res = supabase.auth.reset_password_email(email)
            st.success("Password reset link sent to your email!")
        except Exception as e:
            st.error(f"Failed to send reset link: {str(e)}")
