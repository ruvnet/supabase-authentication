import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase URL and API key must be set in environment variables or Streamlit secrets.")
        st.stop()
    
    return create_client(url, key)

supabase: Client = init_supabase()

# Function to check if the profile exists for a user
def check_profile_exists(user_id):
    try:
        response = supabase.from_("profiles").select("*").eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Failed to check profile existence: {str(e)}")
        return False

# Function to insert initial profile data
def insert_initial_profile(user_id, full_name="New User", bio="This is your bio."):
    try:
        supabase.from_("profiles").insert({
            "user_id": user_id,
            "full_name": full_name,
            "bio": bio
        }).execute()
        st.success("Initial profile created successfully!")
    except Exception as e:
        st.error(f"Failed to insert initial profile data: {str(e)}")

# Main function to check and create profile if necessary
def ensure_profile_exists(user):
    if not check_profile_exists(user.id):
        insert_initial_profile(user.id)