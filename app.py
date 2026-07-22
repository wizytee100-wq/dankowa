import streamlit as st
from supabase import create_client

# Initialize Supabase connection using Streamlit secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("Welcome to Dankowa Data")

# Session state initialization for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone = ""

# Authentication Section
if not st.session_state.logged_in:
    st.write("Enter your phone number to sign in or register instantly.")
    phone_input = st.text_input("Phone Number")
    
    if st.button("Continue"):
        if phone_input.strip():
            st.session_state.logged_in = True
            st.session_state.phone = phone_input.strip()
            st.rerun()
        else:
            st.warning("Please enter a valid phone number.")
else:
    # Dashboard Section after login
    st.success(f"Logged in as: {st.session_state.phone}")
    
    # Wallet / Balance Card mockup
    st.markdown("### Wallet Balance")
    st.info("₦0.00")
    
    if st.button("Fund Wallet"):
        st.write("Payment gateway integration coming soon.")

    st.markdown("---")
    st.markdown("### Buy Data & Airtime")
    
    choice = st.selectbox("Select Service", ["Data Bundle", "Airtime Top-up"])
    
    network = st.selectbox("Select Network", ["MTN", "Glo", "Airtel", "9mobile"])
    
    if choice == "Data Bundle":
        plan = st.selectbox(
            "Select Data Plan", 
            ["1GB - 30 Days (₦300)", "2GB - 30 Days (₦600)", "5GB - 30 Days (₦1,500)"]
        )
        recipient = st.text_input("Recipient Phone Number", value=st.session_state.phone)
        
        if st.button("Purchase Data"):
            st.success(f"Successfully ordered {plan} for {recipient} on {network}!")
            
    else:
        amount = st.number_input("Enter Amount (₦)", min_value=50, step=50)
        recipient = st.text_input("Recipient Phone Number", value=st.session_state.phone)
        
        if st.button("Purchase Airtime"):
            st.success(f"Successfully sent ₦{amount} airtime to {recipient} on {network}!")

    st.markdown("---")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.phone = ""
        st.rerun()
