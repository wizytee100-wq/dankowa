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
            phone = phone_input.strip()
            try:
                # Check if user exists in the 'users' table, if not create them
                response = supabase.table("users").select("*").eq("phone", phone).execute()
                if not response.data:
                    supabase.table("users").insert({"phone": phone, "wallet_balance": 0.00}).execute()
                
                st.session_state.logged_in = True
                st.session_state.phone = phone
                st.rerun()
            except Exception as e:
                st.error(f"Database error: {e}")
        else:
            st.warning("Please enter a valid phone number.")
else:
    phone = st.session_state.phone
    st.success(f"Logged in as: {phone}")
    
    # Fetch wallet balance from Supabase 'users' table
    try:
        user_data = supabase.table("users").select("wallet_balance").eq("phone", phone).execute()
        balance = user_data.data[0]["wallet_balance"] if user_data.data else 0.00
    except:
        balance = 0.00

    # Wallet / Balance Card
    st.markdown("### Wallet Balance")
    st.info(f"₦{balance:,.2f}")
    
    if st.button("Fund Wallet (Test Demo)"):
        new_balance = float(balance) + 1000.00
        supabase.table("users").update({"wallet_balance": new_balance}).eq("phone", phone).execute()
        st.success("Successfully added ₦1,000.00 test funds!")
        st.rerun()

    st.markdown("---")
    st.markdown("### Buy Data & Airtime")
    
    choice = st.selectbox("Select Service", ["Data Bundle", "Airtime Top-up"])
    network = st.selectbox("Select Network", ["MTN", "Glo", "Airtel", "9mobile"])
    
    if choice == "Data Bundle":
        plan_options = {
            "50MB - 1 Day (₦30)": 30,
            "100MB - 1 Day (₦50)": 50,
            "200MB - 2 Days (₦80)": 80,
            "500MB - 7 Days (₦150)": 150,
            "750MB - 7 Days (₦200)": 200,
            "1GB - 30 Days (₦250)": 250,
            "1.5GB - 30 Days (₦380)": 380,
            "2GB - 30 Days (₦500)": 500,
            "3GB - 30 Days (₦750)": 750,
            "5GB - 30 Days (₦1,200)": 1200,
            "10GB - 30 Days (₦2,300)": 2300,
            "15GB - 30 Days (₦3,400)": 3400,
            "20GB - 30 Days (₦4,500)": 4500,
            "30GB - 30 Days (₦6,700)": 6700,
            "40GB - 30 Days (₦8,900)": 8900,
            "50GB - 30 Days (₦11,000)": 11000,
            "75GB - 30 Days (₦16,000)": 16000,
            "100GB - 30 Days (₦21,000)": 21000,
            "150GB - 30 Days (₦31,000)": 31000,
            "200GB - 30 Days (₦40,000)": 40000,
            "300GB - 30 Days (₦58,000)": 58000,
            "500GB - 30 Days (₦95,000)": 95000,
            "1TB (1000GB) - 30 Days (₦180,000)": 180000,
            "2TB - 30 Days (₦340,000)": 340000,
            "5TB - 30 Days (₦800,000)": 800000,
            "UNLIMITED Data - 30 Days (Standard Speed) (₦25,000)": 25000,
            "UNLIMITED Data - 30 Days (High Speed / 5G) (₦50,000)": 50000
        }
        
        selected_plan = st.selectbox("Select Data Plan", list(plan_options.keys()))
        cost = plan_options[selected_plan]
        
        recipient = st.text_input("Recipient Phone Number", value=phone)
        st.write(f"Price: **₦{cost:,}**")
        
        if st.button("Purchase Data"):
            if float(balance) >= cost:
                new_balance = float(balance) - cost
                supabase.table("users").update({"wallet_balance": new_balance}).eq("phone", phone).execute()
                
                supabase.table("transactions").insert({
                    "phone": phone,
                    "service_type": "Data",
                    "network": network,
                    "details": selected_plan,
                    "amount": cost
                }).execute()
                
                st.success(f"Successfully ordered {selected_plan} for {recipient} on {network}!")
                st.rerun()
            else:
                st.error("Insufficient wallet balance. Please fund your wallet.")
            
    else:
        amount = st.number_input("Enter Amount (₦)", min_value=50, step=50)
        recipient = st.text_input("Recipient Phone Number", value=phone)
        
        if st.button("Purchase Airtime"):
            if float(balance) >= amount:
                new_balance = float(balance) - float(amount)
                supabase.table("users").update({"wallet_balance": new_balance}).eq("phone", phone).execute()
                
                supabase.table("transactions").insert({
                    "phone": phone,
                    "service_type": "Airtime",
                    "network": network,
                    "details": f"₦{amount} Airtime",
                    "amount": amount
                }).execute()
                
                st.success(f"Successfully sent ₦{amount} airtime to {recipient} on {network}!")
                st.rerun()
            else:
                st.error("Insufficient wallet balance. Please fund your wallet.")

    # --- TRANSACTION HISTORY SECTION ---
    st.markdown("---")
    st.markdown("### Recent Transactions")
    try:
        tx_response = supabase.table("transactions").select("*").eq("phone", phone).order("created_at", desc=True).limit(10).execute()
        if tx_response.data:
            for tx in tx_response.data:
                st.markdown(f"- **{tx['service_type']}** | {tx['network']} - {tx['details']} | **₦{tx['amount']:,.2f}** | *{tx['status']}*")
        else:
            st.info("No transaction history yet.")
    except Exception as e:
        st.write("Could not load transaction history.")

    st.markdown("---")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.phone = ""
        st.rerun()
