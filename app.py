import streamlit as st
from supabase import create_client
import requests

# Initialize Supabase connection using Streamlit secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
PAYSTACK_SECRET_KEY = st.secrets.get("PAYSTACK_SECRET_KEY", "")

st.title("Welcome to Dankowa Data")

# Session state initialization for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.identifier = ""
    st.session_state.login_type = "Phone"

# Authentication Section
if not st.session_state.logged_in:
    st.write("Sign in or register instantly to access cheap data & airtime.")
    
    auth_choice = st.radio("Choose Login Method", ["Phone Number", "Google (Gmail)"])
    
    if auth_choice == "Phone Number":
        phone_input = st.text_input("Phone Number")
        if st.button("Continue with Phone"):
            if phone_input.strip():
                phone = phone_input.strip()
                try:
                    response = supabase.table("users").select("*").eq("phone", phone).execute()
                    if not response.data:
                        supabase.table("users").insert({
                            "phone": phone, 
                            "wallet_balance": 0.00,
                            "referral_bonus": 0.00
                        }).execute()
                    
                    st.session_state.logged_in = True
                    st.session_state.identifier = phone
                    st.session_state.login_type = "Phone"
                    st.rerun()
                except Exception as e:
                    st.error(f"Database error: {e}")
            else:
                st.warning("Please enter a valid phone number.")
                
    else:
        gmail_input = st.text_input("Enter your Gmail Address")
        if st.button("Sign in with Google"):
            if gmail_input.strip() and "@" in gmail_input:
                email = gmail_input.strip()
                try:
                    response = supabase.table("users").select("*").eq("phone", email).execute()
                    if not response.data:
                        supabase.table("users").insert({
                            "phone": email, 
                            "wallet_balance": 0.00,
                            "referral_bonus": 0.00
                        }).execute()
                    
                    st.session_state.logged_in = True
                    st.session_state.identifier = email
                    st.session_state.login_type = "Google"
                    st.rerun()
                except Exception as e:
                    st.error(f"Database error: {e}")
            else:
                st.warning("Please enter a valid Gmail address.")
else:
    identifier = st.session_state.identifier
    st.success(f"Logged in as: {identifier}")
    
    # --- FLASH SALE / LUCKY HOUR BANNER ---
    st.warning("⚡ **FLASH SALE ACTIVE!** Get massive discounts on all 1GB and 2GB plans for the next 2 hours only! Hurry and buy now!")

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

    # Wallet & Rewards Cards
    st.markdown("### Wallet Balance")
    st.info(f"₦{balance:,.2f}")
    
    # --- FUNDING METHODS (PAYSTACK + MANUAL BANK TRANSFER) ---
    st.markdown("### Fund Your Wallet")
    funding_method = st.selectbox("Choose Funding Method", ["Paystack (ATM Card / Online)", "Bank Transfer (OPay / Direct Transfer)"])
    
    if funding_method == "Paystack (ATM Card / Online)":
        fund_amount = st.number_input("Enter Amount to Fund (₦)", min_value=100, step=100, value=1000)
        user_email = st.text_input("Enter Email for Receipt", value=identifier if "@" in identifier else f"{identifier}@dankowa.com")
        
        if st.button("Proceed to Pay with Paystack"):
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
    else:
        st.info("💡 **Instructions:** Make a transfer to the account details below, then click the confirmation button once sent.")
        st.markdown("""
        * **Bank Name:** OPay (or Moniepoint)
        * **Account Number:** `1234567890` *(Replace with your actual account number)*
        * **Account Name:** Dankowa Data Services
        """)
        
        transfer_amount = st.number_input("Enter Amount Transferred (₦)", min_value=100, step=100, value=1000)
        if st.button("I Have Made the Transfer"):
            # Logs a pending transaction or notifies you
            supabase.table("transactions").insert({
                "phone": identifier,
                "service_type": "Wallet Funding",
                "network": "Bank Transfer",
                "details": f"Manual Transfer of ₦{transfer_amount} (Pending Confirmation)",
                "amount": transfer_amount
            }).execute()
            st.success("Transfer notification submitted! Your wallet will be credited shortly after confirmation.")

    if ref_bonus > 0:
        if st.button("Claim Referral Bonus"):
            new_balance = float(balance) + float(ref_bonus)
            supabase.table("users").update({"wallet_balance": new_balance, "referral_bonus": 0.00}).eq("phone", identifier).execute()
            st.success(f"Moved ₦{ref_bonus:,.2f} bonus to your main wallet!")
            st.rerun()

    # --- REFERRAL REWARDS SECTION ---
    st.markdown("---")
    st.markdown("### 🎁 Referral Rewards Program")
    st.write("Earn **₦100** free reward bonus for every friend who signs up using your account ID as their referral code!")
    st.info(f"Share your account ID (**{identifier}**) with friends when they sign up!")
    st.write(f"Your Current Unclaimed Rewards: **₦{ref_bonus:,.2f}**")

    st.markdown("---")
    st.markdown("### Buy Data & Airtime")
    
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
        
        if st.button("Purchase Data"):
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
        
        if st.button("Purchase Airtime"):
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
    st.markdown("### Recent Transactions")
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
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.identifier = ""
        st.rerun()
