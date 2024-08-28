import streamlit as st

def show_home(user):
    if user:
        st.subheader("Welcome to Your Dashboard")
        st.write("Here's some personalized content for logged-in users.")
        # Add more personalized content or features here
    else:
        st.subheader("Welcome to the Home Page")
        st.write("Please login or register to access more features.")
