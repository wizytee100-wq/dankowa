import streamlit as st
import datetime

# Page Configuration
st.set_page_config(page_title="Dankowa Data & Airtime Hub", page_icon="📱", layout="centered")

# Initialize Session State for Wallet and History
if "wallet_balance" not in st.session_state:
    st.session_state.wallet_balance = 5000.00  # Starting bonus balance in ₦

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# Sidebar for Wallet Management
st.sidebar.title("💰 Wallet Hub")
st.sidebar.metric(label="Current Balance", value=f"₦{st.session_state.wallet_balance:,.2f}")

funding_amount = st.sidebar.number_input("Fund Wallet (₦)", min_value=100, max_value=50000, step=500)
if st.sidebar.button("Add Funds"):
    st.session_state.wallet_balance += funding_amount
    st.sidebar.success(f"Successfully added ₦{funding_amount:,.2f} to wallet!")

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
            st.error("Insufficient wallet funds! Please fund your wallet from the sidebar.")
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
