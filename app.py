from supabase import create_client
import streamlit as st

# Initialize Supabase Connection using Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- DATABASE LOGIN CHECK ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone_number = ""

if not st.session_state.logged_in:
    st.markdown("### Welcome to Dankowa Data")
    st.write("Enter your phone number to sign in or register instantly.")
    
    phone_input = st.text_input("Phone Number", max_chars=11)
    
    if st.button("Continue"):
        if phone_input and len(phone_input) >= 10:
            # Check if user exists in Supabase users table
            response = supabase.table("users").select("*").eq("phone", phone_input).execute()
            
            if len(response.data) > 0:
                st.success("Welcome back! Logging you in...")
            else:
                # Register new user automatically with 0 balance
                supabase.table("users").insert({"phone": phone_input, "wallet_balance": 0.0}).execute()
                st.success("Account created successfully!")
                
            st.session_state.logged_in = True
            st.session_state.phone_number = phone_input
            st.rerun()
        else:
            st.error("Please enter a valid phone number.")
    st.stop()
else:
    # --- YOUR MAIN APP CODE GOES UNDER HERE ---
    st.success(f"Logged in as: {st.session_state.phone_number}")


