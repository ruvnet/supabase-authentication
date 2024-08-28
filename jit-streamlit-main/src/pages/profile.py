import streamlit as st
from supabase import create_client
from utils.supabase_client import supabase

def fetch_user_profile(user_id):
    try:
        response = supabase.from_("profiles").select("*").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Failed to load profile data: {str(e)}")
        return None

def update_user_profile(user_id, full_name, bio):
    try:
        supabase.from_("profiles").update({
            "full_name": full_name,
            "bio": bio
        }).eq("user_id", user_id).execute()
        st.success("Profile updated successfully!")
    except Exception as e:
        st.error(f"Failed to update profile data: {str(e)}")

def insert_initial_profile(user_id, full_name="New User", bio="This is your bio."):
    try:
        supabase.from_("profiles").insert({
            "user_id": user_id,
            "full_name": full_name,
            "bio": bio
        }).execute()
        st.success("Profile created successfully!")
        return {"full_name": full_name, "bio": bio}
    except Exception as e:
        st.error(f"Failed to insert initial profile data: {str(e)}")
        return None

def show_profile(user):
    st.subheader("Your Profile")
    st.write(f"Email: {user.email}")
    
    profile_data = fetch_user_profile(user.id)
    
    if not profile_data:
        st.warning("No profile found. Let's create one!")
        full_name = st.text_input("Full Name", value="New User")
        bio = st.text_area("Bio", value="This is your bio.")
        if st.button("Create Profile"):
            profile_data = insert_initial_profile(user.id, full_name, bio)
    
    if profile_data:
        full_name = st.text_input("Full Name", value=profile_data.get("full_name", ""))
        bio = st.text_area("Bio", value=profile_data.get("bio", ""))
        
        if st.button("Update Profile"):
            update_user_profile(user.id, full_name, bio)

# This function should be called from your main.py or wherever you handle the user's session
def handle_profile(user):
    if user:
        show_profile(user)
    else:
        st.warning("Please log in to view and edit your profile.")