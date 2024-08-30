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
from pages.chat import chat  # Changed from show_chat to chat
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
    
    # Handle logout
    if st.session_state.get('logged_out', False):
        st.session_state.clear()
        st.rerun()
    
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
    query_params = st.query_params
    if "confirmation" in query_params:
        handle_confirmation()
    else:
        with st.sidebar:
            if user:
                # Logged-in user menu
                st.write(f"Welcome, {user.email}")
                choice = st.selectbox("Menu", ["Home", "Profile", "Settings", "Chat"], key="menu_selectbox")
                
                # Handle logout
                if st.button("Logout", key="logout_button"):
                    logout()
            else:
                # Restricted menu for non-logged-in users
                choice = st.selectbox("Menu", ["Home", "Login", "Register", "Reset Password"], key="menu_selectbox_guest")
        
        # Load the selected page based on menu choice and authentication status
        if not user:
            if choice == "Home":
                show_home(user)
            elif choice == "Login":
                login_form()
            elif choice == "Register":
                registration_form()
            elif choice == "Reset Password":
                password_reset_form()
        else:
            if choice == "Home":
                show_home(user)
            elif choice == "Profile":
                show_profile(user)
            elif choice == "Settings":
                show_settings(user)
            elif choice == "Chat":
                chat()  # Changed from show_chat(user) to chat()
                
if __name__ == "__main__":
    main()