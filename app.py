import streamlit as st
from supabase import create_client
import requests

# Initialize Supabase connection using Streamlit secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
PAYSTACK_SECRET_KEY = st.secrets.get("PAYSTACK_SECRET_KEY", "")

# Page Configuration for a professional look
st.set_page_config(page_title="Dankowa Data Portal", page_icon="⚡", layout="centered")

# App Header Banner
st.markdown("""
    <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px;'>
        <h1 style='margin: 0; font-size: 28px;'>⚡ Dankowa Data Hub</h1>
        <p style='margin: 5px 0 0 0; font-size: 16px;'>Instant Cheap Data, Airtime & Automated Services</p>
    </div>
""", unsafe_allow_html=True)

# Session state initialization for login & reset mode
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.identifier = ""

if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False

# Authentication Section
if not st.session_state.logged_in:
    
    if not st.session_state.reset_mode:
        st.markdown("### 🔐 Secure Sign In & Registration")
        st.write("Access your wallet and cheap data securely with your PIN.")
        
        auth_choice = st.selectbox("Identifier Type", ["Phone Number", "Google (Gmail)"])
        
        if auth_choice == "Phone Number":
            identifier_input = st.text_input("Phone Number (e.g. 08012345678)")
        else:
            identifier_input = st.text_input("Gmail Address")
            
        pin_input = st.text_input("Enter 4-Digit Security PIN", type="password", max_chars=4)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Login", use_container_width=True):
                if identifier_input.strip() and pin_input.strip():
                    identifier = identifier_input.strip()
                    try:
                        response = supabase.table("users").select("*").eq("phone", identifier).execute()
                        if response.data:
                            user_record = response.data[0]
                            stored_pin = str(user_record.get("pin", ""))
                            
                            if stored_pin == pin_input:
                                st.session_state.logged_in = True
                                st.session_state.identifier = identifier
                                st.rerun()
                            else:
                                st.error("Incorrect 4-Digit PIN. Please try again.")
                        else:
                            st.warning("Account not found! Click 'Register New Account' below to create one instantly.")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    st.warning("Please fill in both your identifier and your 4-digit PIN.")

        with col2:
            if st.button("Register New Account", use_container_width=True):
                if identifier_input.strip() and len(pin_input) == 4:
                    identifier = identifier_input.strip()
                    try:
                        response = supabase.table("users").select("*").eq("phone", identifier).execute()
                        if response.data:
                            st.error("Account already exists! You can log in directly.")
                        else:
                            supabase.table("users").insert({
                                "phone": identifier, 
                                "wallet_balance": 0.00,
                                "referral_bonus": 0.00,
                                "pin": pin_input
                            }).execute()
                            st.success("Account created successfully! Logging you in...")
                            st.session_state.logged_in = True
                            st.session_state.identifier = identifier
                            st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    st.warning("Enter your phone/email and a strict 4-digit PIN to register.")

        st.markdown("---")
        if st.button("Forgot Your PIN? Click Here to Reset"):
            st.session_state.reset_mode = True
            st.rerun()

    else:
        # --- FORGOT / RESET PIN VIEW ---
        st.markdown("### 🔄 Reset Your Security PIN")
        st.write("Enter your registered phone number or Gmail and set a new 4-digit PIN.")
        
        reset_choice = st.selectbox("Identifier Type for Reset", ["Phone Number", "Google (Gmail)"])
        if reset_choice == "Phone Number":
            reset_identifier = st.text_input("Registered Phone Number")
        else:
            reset_identifier = st.text_input("Registered Gmail Address")
            
        new_pin = st.text_input("Enter New 4-Digit PIN", type="password", max_chars=4)
        confirm_pin = st.text_input("Confirm New 4-Digit PIN", type="password", max_chars=4)
        
        if st.button("Update PIN Now", use_container_width=True):
            if reset_identifier.strip() and len(new_pin) == 4:
                if new_pin == confirm_pin:
                    try:
                        response = supabase.table("users").select("*").eq("phone", reset_identifier.strip()).execute()
                        if response.data:
                            supabase.table("users").update({"pin": new_pin}).eq("phone", reset_identifier.strip()).execute()
                            st.success("PIN updated successfully! You can now log in with your new PIN.")
                            st.session_state.reset_mode = False
                            st.rerun()
                        else:
                            st.error("Account not found with this identifier.")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    st.error("New PINs do not match!")
            else:
                st.warning("Please provide a valid account ID and a strict 4-digit PIN.")

        if st.button("Back to Login"):
            st.session_state.reset_mode = False
            st.rerun()

else:
    identifier = st.session_state.identifier
    
    # User Profile Welcome Banner
    st.success(f"👤 Logged in as: **{identifier}**")
    
    # --- FLASH SALE / LUCKY HOUR BANNER ---
    st.markdown("""
        <div style='background-color: #ff4b4b; padding: 12px; border-radius: 8px; color: white; text-align: center; font-weight: bold; margin-bottom: 20px;'>
            🔥 FLASH SALE ACTIVE: Get massive discounts on 1GB and 2GB plans today! 🚀
        </div>
    """, unsafe_allow_html=True)

    # Fetch wallet balance and referral rewards from Supabase
    try:
        user_data = supabase.table("users").select("wallet_balance, referral_bonus").eq("phone", identifier).execute()
        if user_data.data:
            balance = user_data.data[0].get("wallet_balance", 0.00)
            ref_bonus = user_data.data[0].get("referral_bonus", 0.00)
        else:
            balance = 0.00
            ref_bonus = 0.00
    except:
        balance = 0.00
        ref_bonus = 0.00

    # Wallet & Rewards Display Columns
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="💰 Wallet Balance", value=f"₦{balance:,.2f}")
    with col_b:
        st.metric(label="🎁 Unclaimed Rewards", value=f"₦{ref_bonus:,.2f}")
    
    st.markdown("---")

    # --- AUTOMATED PAYSTACK FUNDING SECTION ---
    st.markdown("### 💳 Fund Your Wallet")
    fund_amount = st.number_input("Enter Amount to Fund (₦)", min_value=100, step=100, value=1000)
    user_email = st.text_input("Enter Email for Receipt", value=identifier if "@" in identifier else f"{identifier}@dankowa.com")
    
    if st.button("Proceed to Pay with Paystack", use_container_width=True):
        if PAYSTACK_SECRET_KEY:
            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "email": user_email,
                "amount": int(fund_amount * 100),
                "callback_url": "https://dankowa.streamlit.app"
            }
            try:
                res = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
                res_data = res.json()
                if res_data.get("status"):
                    auth_url = res_data["data"]["authorization_url"]
                    st.markdown(f"👉 **[Click Here to Complete Secure Payment]({auth_url})**", unsafe_allow_html=True)
                else:
                    st.error("Could not initialize payment gateway.")
            except Exception as ex:
                st.error(f"Connection error: {ex}")
        else:
            st.warning("Paystack Secret Key is missing in Streamlit secrets.")

    if ref_bonus > 0:
        if st.button("Claim Referral Bonus to Wallet", use_container_width=True):
            new_balance = float(balance) + float(ref_bonus)
            supabase.table("users").update({"wallet_balance": new_balance, "referral_bonus": 0.00}).eq("phone", identifier).execute()
            st.success(f"Moved ₦{ref_bonus:,.2f} bonus to your main wallet!")
            st.rerun()

    # --- REFERRAL REWARDS SECTION ---
    st.markdown("---")
    st.markdown("### 🎁 Referral Rewards Program")
    st.info(f"Share your account identifier (**{identifier}**) with friends! Earn **₦100** free reward bonus for every friend who joins.")

    st.markdown("---")
    st.markdown("### 🛒 Buy Data & Airtime")
    
    choice = st.selectbox("Select Service", ["Data Bundle", "Airtime Top-up"])
    network = st.selectbox("Select Network", ["MTN", "Glo", "Airtel", "9mobile"])
    
    if choice == "Data Bundle":
        plan_options = {
            "⚡ FLASH DEAL: 1GB - 30 Days (₦200)": 200,
            "⚡ FLASH DEAL: 2GB - 30 Days (₦400)": 400,
            "50MB - 1 Day (₦30)": 30,
            "100MB - 1 Day (₦50)": 50,
            "200MB - 2 Days (₦80)": 80,
            "500MB - 7 Days (₦150)": 150,
            "750MB - 7 Days (₦200)": 200,
            "1.5GB - 30 Days (₦380)": 380,
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
        
        recipient = st.text_input("Recipient Phone Number", value="")
        st.write(f"Price: **₦{cost:,}**")
        
        if st.button("Purchase Data Now", use_container_width=True):
            if float(balance) >= cost and recipient.strip():
                new_balance = float(balance) - cost
                supabase.table("users").update({"wallet_balance": new_balance}).eq("phone", identifier).execute()
                
                supabase.table("transactions").insert({
                    "phone": identifier,
                    "service_type": "Data",
                    "network": network,
                    "details": f"{selected_plan} -> Sent to {recipient}",
                    "amount": cost
                }).execute()
                
                st.success(f"Successfully ordered {selected_plan} for {recipient} on {network}!")
                st.rerun()
            else:
                st.error("Please enter a valid recipient phone number or check your wallet balance.")
            
    else:
        amount = st.number_input("Enter Amount (₦)", min_value=50, step=50)
        recipient = st.text_input("Recipient Phone Number", value="")
        
        if st.button("Purchase Airtime Now", use_container_width=True):
            if float(balance) >= float(amount) and recipient.strip():
                new_balance = float(balance) - float(amount)
                supabase.table("users").update({"wallet_balance": new_balance}).eq("phone", identifier).execute()
                
                supabase.table("transactions").insert({
                    "phone": identifier,
                    "service_type": "Airtime",
                    "network": network,
                    "details": f"₦{amount} Airtime -> Sent to {recipient}",
                    "amount": amount
                }).execute()
                
                st.success(f"Successfully sent ₦{amount} airtime to {recipient} on {network}!")
                st.rerun()
            else:
                st.error("Please enter a valid recipient phone number or check your wallet balance.")

    # --- TRANSACTION HISTORY SECTION ---
    st.markdown("---")
    st.markdown("### 📜 Recent Transactions")
    try:
        tx_response = supabase.table("transactions").select("*").eq("phone", identifier).order("created_at", desc=True).limit(10).execute()
        if tx_response.data:
            for tx in tx_response.data:
                st.markdown(f"- **{tx['service_type']}** | {tx['network']} - {tx['details']} | **₦{tx['amount']:,.2f}**")
        else:
            st.info("No transaction history yet.")
    except Exception as e:
        st.write("Could not load transaction history.")

    st.markdown("---")
    if st.button("Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.identifier = ""
        st.rerun()
