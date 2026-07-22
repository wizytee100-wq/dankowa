import streamlit as st
import datetime
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
import streamlit as st
import datetime

# --- 1. HIDE STREAMLIT STYLING ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 2. LOGIN CHECK ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone_number = ""

if not st.session_state.logged_in:
    st.markdown("### Welcome to Dankowa Data")
    st.write("Please enter your phone number to continue.")
    
    phone_input = st.text_input("Phone Number", max_chars=11)
    
    if st.button("Continue to App"):
        if phone_input and len(phone_input) >= 10:
            st.session_state.logged_in = True
            st.session_state.phone_number = phone_input
            st.rerun()
        else:
            st.error("Please enter a valid phone number.")
            
else:
    # --- 3. YOUR MAIN APP CODE GOES HERE ---
    # Everything your app does (wallet, data bundles, airtime) goes inside this 'else' section!
    st.success(f"Logged in as: {st.session_state.phone_number}")
    
    # Put your existing dashboard code here...

# Page Configuration
st.set_page_config(page_title="Dankowa Data & Airtime Hub", page_icon="📱", layout="centered")
# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone_number = ""

if not st.session_state.logged_in:
    st.markdown("### Welcome to Dankowa Data")
    st.write("Please enter your phone number to continue.")
    
    phone_input = st.text_input("Phone Number", max_chars=11)
    
    if st.button("Continue to App"):
        if phone_input and len(phone_input) >= 10:
            st.session_state.logged_in = True
            st.session_state.phone_number = phone_input
            st.rerun()
        else:
            st.error("Please enter a valid phone number.")
    st.stop()  # Stops the rest of the app from showing until logged in

# Initialize Session State for Wallet and History
if "wallet_balance" not in st.session_state:
    st.session_state.wallet_balance = 5000.00  # Starting balance in ₦

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# Sidebar for Wallet Management & Bank Funding
st.sidebar.title("💰 Wallet Hub")
st.sidebar.metric(label="Current Balance", value=f"₦{st.session_state.wallet_balance:,.2f}")

st.sidebar.subheader("Fund Wallet via Bank Transfer")
funding_amount = st.sidebar.number_input("Enter Amount to Fund (₦)", min_value=500, max_value=50000, step=500)
user_email = st.sidebar.text_input("Your Email (for receipt)")

# Option 1: Automated Payment Gateway Link (Paystack)
if st.sidebar.button("Generate Transfer Checkout"):
    if user_email:
        # Note: Replace 'pk_test_your_key_here' with your actual Paystack Public Key when ready
        # For testing, users can complete a simulated transfer via Paystack's secure checkout page.
        paystack_checkout_url = f"https://checkout.paystack.com/pay?amount={funding_amount * 100}&email={user_email}"
        st.sidebar.markdown(f"[ 👉 Click Here to Complete Bank Transfer]({paystack_checkout_url})", unsafe_allow_html=True)
        st.sidebar.info("After successful payment, use the simulation button below to credit your wallet.")
    else:
        st.sidebar.error("Please enter your email address first.")

# Simulation helper for testing instantly in your app
if st.sidebar.button("Simulate Successful Transfer"):
    st.session_state.wallet_balance += funding_amount
    st.sidebar.success(f"Wallet credited with ₦{funding_amount:,.2f}!")
    st.rerun()

# Main App Interface
st.title("📱 Dankowa Data & Airtime Hub")
st.write("Welcome back! Buy cheap SME data and airtime instantly with automated delivery.")

# Network Selection including additional providers
network = st.selectbox("Select Network Provider", ["MTN", "Airtel", "Glo", "9mobile", "Smile 4G", "Spectranet"])
service_type = st.radio("Select Service", ["Data Bundle", "Airtime Top-up"])

# Pricing Mapping
prices = {
    "500MB - ₦130": 130,
    "1GB - ₦250": 250,
    "2GB - ₦500": 500,
    "5GB - ₦1,200": 1200
}

cost = 0
plan = ""

if service_type == "Data Bundle":
    plan = st.selectbox("Select Data Plan", list(prices.keys()))
    cost = prices[plan]
    st.info(f"Price: ₦{cost}")
else:
    cost = st.number_input("Enter Airtime Amount (₦)", min_value=50, max_value=10000, step=50)

phone_number = st.text_input("Enter Phone Number", max_chars=11)

if st.button("Proceed with Transaction"):
    if len(phone_number) == 11:
        if st.session_state.wallet_balance >= cost:
            # Deduct from wallet
            st.session_state.wallet_balance -= cost
            
            # Record Transaction
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            details = f"{plan}" if service_type == "Data Bundle" else f"₦{cost} Airtime"
            transaction_record = {
                "time": current_time,
                "network": network,
                "type": service_type,
                "details": details,
                "phone": phone_number,
                "cost": cost
            }
            st.session_state.transactions.insert(0, transaction_record)
            
            st.success(f"Transaction successful! {service_type} sent to {phone_number}.")
        else:
            st.error("Insufficient wallet funds! Please fund your wallet via bank transfer from the sidebar.")
    else:
        st.error("Please enter a valid 11-digit phone number.")

# Transaction History Section
st.markdown("---")
st.subheader("📜 Recent Transaction History")

if len(st.session_state.transactions) > 0:
    for idx, tx in enumerate(st.session_state.transactions):
        with st.container():
            st.write(f"**{idx+1}. [{tx['time']}] {tx['network']} - {tx['type']}**")
            st.text(f"Details: {tx['details']} | Phone: {tx['phone']} | Cost: ₦{tx['cost']}")
            st.markdown("---")
else:
    st.write("No transactions recorded yet.")

