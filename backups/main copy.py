import os
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client using environment variables or Streamlit secrets
@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase URL and API key must be set in environment variables or Streamlit secrets.")
        st.stop()
    
    return create_client(url, key)

supabase: Client = init_supabase()

def check_user_session():
    session = supabase.auth.get_session()
    if session:
        st.session_state.user = session.user
        return True
    return False

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

def main():
    st.title("Supabase Authentication")
    
    # Check for existing session on app load
    if 'user' not in st.session_state:
        if check_user_session():
            st.success("Welcome back!")
        else:
            st.session_state.user = None
    
    # Check if we're on the confirmation page
    if "confirmation" in st.query_params:
        handle_confirmation()
    else:
        user = st.session_state.get('user')
        
        if user:
            st.sidebar.write(f"Welcome, {user.email}")
            logout()
            menu = ["Home", "Profile", "Settings"]
        else:
            menu = ["Home", "Login", "Register", "Reset Password"]
        
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Home":
            if user:
                st.subheader("Welcome to Your Dashboard")
                st.write("Here's some personalized content for logged-in users.")
                # Add more personalized content or features here
            else:
                st.subheader("Welcome to the Home Page")
                st.write("Please login or register to access more features.")
        elif choice == "Login" and not user:
            login_form()
        elif choice == "Register" and not user:
            registration_form()
        elif choice == "Reset Password" and not user:
            password_reset_form()
        elif choice == "Profile" and user:
            st.subheader("Your Profile")
            st.write(f"Email: {user.email}")
            # Add more profile information or editing options here
        elif choice == "Settings" and user:
            st.subheader("Settings")
            # Add user settings options here

if __name__ == "__main__":
    main()