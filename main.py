import sys
import os
import streamlit as st

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Set page config at the very top of the main script
st.set_page_config(
    page_title="Supabase Authentication",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)

from auth.handlers import handle_confirmation, logout
from auth.forms import login_form, registration_form, password_reset_form
from pages.home import show_home
from pages.profile import show_profile
from pages.settings import show_settings
from pages.chat import show_chat
from utils.supabase_client import supabase, ensure_profile_exists

# Hide the Streamlit style and About menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QSob {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def check_user_session():
    session = supabase.auth.get_session()
    if session:
        st.session_state.user = session.user
        return True
    return False

def main():
    st.title("Supabase Authentication")
    
    # Check for existing session on app load
    if 'user' not in st.session_state:
        if check_user_session():
            st.success("Welcome back!")
        else:
            st.session_state.user = None
    
    user = st.session_state.get('user')
    
    # Ensure profile exists for the user
    if user:
        ensure_profile_exists(user)
    
    # Check if we're on the confirmation page
    if "confirmation" in st.query_params:
        handle_confirmation()
    else:
        with st.sidebar:
            if user:
                # Logged-in user menu
                st.write(f"Welcome, {user.email}")
                choice = st.selectbox("Menu", ["Home", "Profile", "Settings", "Chat"])
                
                if st.button("Logout"):
                    logout()
            else:
                # Restricted menu for non-logged-in users
                choice = st.selectbox("Menu", ["Home", "Login", "Register", "Reset Password"])
        
        # Load the selected page based on menu choice and authentication status
        if choice == "Home":
            show_home(user)
        elif choice == "Login" and not user:
            login_form()
        elif choice == "Register" and not user:
            registration_form()
        elif choice == "Reset Password" and not user:
            password_reset_form()
        elif choice == "Profile" and user:
            show_profile(user)
        elif choice == "Settings" and user:
            show_settings(user)
        elif choice == "Chat" and user:
            show_chat(user)

if __name__ == "__main__":
    main()