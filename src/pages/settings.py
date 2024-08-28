import streamlit as st
from supabase import create_client
from utils.supabase_client import supabase

def show_settings(user):
    st.subheader("Settings")

    # Fetch current user settings
    try:
        response = supabase.from_("profiles").select("*").eq("user_id", user.id).execute()
        if response.data:
            current_settings = response.data[0]
        else:
            st.warning("No profile found. Please create a profile first.")
            return
    except Exception as e:
        st.error(f"Failed to load user settings: {str(e)}")
        return

    # Settings form
    with st.form("user_settings"):
        full_name = st.text_input("Full Name", value=current_settings.get("full_name", ""))
        email = st.text_input("Email", value=current_settings.get("email", user.email))
        bio = st.text_area("Bio", value=current_settings.get("bio", ""))
        age = st.number_input("Age", value=current_settings.get("age", 0), min_value=0, max_value=120)
        theme = st.selectbox("Theme", ["light", "dark"], index=0 if current_settings.get("theme", "light") == "light" else 1)
        notifications = st.checkbox("Enable Notifications", value=current_settings.get("notifications", True))
        language = st.selectbox("Language", ["en", "es", "fr", "de"], index=["en", "es", "fr", "de"].index(current_settings.get("language", "en")))

        submit_button = st.form_submit_button("Update Settings")

    if submit_button:
        try:
            # Update user settings in Supabase
            supabase.table("profiles").update({
                "full_name": full_name,
                "email": email,
                "bio": bio,
                "age": age,
                "theme": theme,
                "notifications": notifications,
                "language": language
            }).eq("user_id", user.id).execute()

            st.success("Settings updated successfully!")
        except Exception as e:
            st.error(f"Failed to update settings: {str(e)}")

    # Display current settings
    st.subheader("Current Settings")
    st.json(current_settings)

# This function should be called from your main.py or wherever you handle the user's session
def handle_settings(user):
    if user:
        show_settings(user)
    else:
        st.warning("Please log in to view and edit your settings.")