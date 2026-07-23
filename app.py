from datetime import datetime, timedelta
import random
from supabase import create_client
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Dankowa Data & Airtime Hub", page_icon="📱", layout="centered"
)

# Initialize Supabase client (using Streamlit Secrets)
supabase = create_client(
    st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
)

# Initialize Session State
if "wallet_balance" not in st.session_state:
  st.session_state.wallet_balance = 5000.00  # Starting balance in ₦

if "transactions" not in st.session_state:
  st.session_state.transactions = []

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if "auth_mode" not in st.session_state:
  st.session_state.auth_mode = "Log In"


# Database Helper Functions for Users & Recovery
def get_user_from_db(identifier):
  try:
    response = (
        supabase.table("users")
        .select("*")
        .or_(f"username.eq.{identifier},phone.eq.{identifier}")
        .execute()
    )
    if response.data:
      return response.data[0]
  except Exception:
    pass
  return None


# --- SIDEBAR: AUTHENTICATION & WALLET HUB ---
st.sidebar.title("🔐 Account & Wallet")

if not st.session_state["logged_in"]:
  auth_choice = st.sidebar.radio(
      "Account Access", ["Log In", "Sign Up", "Forgot Password"]
  )

  if auth_choice == "Log In":
    st.sidebar.subheader("Log In")
    login_id = st.sidebar.text_input("Username or Phone")
    login_pass = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Sign In"):
      user = get_user_from_db(login_id)
      if user and user.get("password") == login_pass:
        st.session_state["logged_in"] = True
        st.session_state["username"] = user.get("username")
        st.sidebar.success("Logged in successfully!")
        st.rerun()
      else:
        st.sidebar.error("Invalid credentials.")

  elif auth_choice == "Sign Up":
    st.sidebar.subheader("Create Account")
    new_user = st.sidebar.text_input("Choose Username")
    new_phone = st.sidebar.text_input("Phone Number")
    new_pass = st.sidebar.text_input("Choose Password", type="password")

    if st.sidebar.button("Register Account"):
      if new_user and new_phone and new_pass:
        try:
          supabase.table("users").insert({
              "username": new_user,
              "phone": new_phone,
              "password": new_pass,
          }).execute()
          st.sidebar.success(
              "Account created! Please switch to Log In tab."
          )
        except Exception as e:
          st.sidebar.error(f"Error: {e}")
      else:
        st.sidebar.warning("Fill in all fields.")

  elif auth_choice == "Forgot Password":
    st.sidebar.subheader("Password Recovery")
    reset_id = st.sidebar.text_input("Registered Username or Phone")

    if st.sidebar.button("Generate Code"):
      if reset_id:
        user = get_user_from_db(reset_id)
        if user:
          token = str(random.randint(100000, 999999))
          expiry = datetime.now() + timedelta(minutes=10)
          supabase.table("users").update({
              "reset_token": token,
              "token_expiry": expiry.isoformat(),
          }).or_(f"username.eq.{reset_id},phone.eq.{reset_id}").execute()

          st.sidebar.session_state["reset_id"] = reset_id
          st.sidebar.success(f"Recovery Code (Copy): **{token}**")
        else:
          st.sidebar.error("User not found.")
      else:
        st.sidebar.warning("Enter your identifier.")

    if "reset_id" in st.sidebar.session_state:
      entered_token = st.sidebar.text_input("Enter 6-digit Code")
      new_pass_input = st.sidebar.text_input(
          "New Password", type="password", key="new_pass_inp"
      )

      if st.sidebar.button("Reset Password Now"):
        user_rec = get_user_from_db(st.sidebar.session_state["reset_id"])
        if user_rec:
          stored_token = user_rec.get("reset_token")
          token_exp = user_rec.get("token_expiry")
          if (
              entered_token == stored_token
              and token_exp
              and datetime.now() < datetime.fromisoformat(token_exp)
          ):
            supabase.table("users").update({"password": new_pass_input}).or_(
                f"username.eq.{st.sidebar.session_state['reset_id']},phone.eq.{st.sidebar.session_state['reset_id']}"
            ).execute()
            supabase.table("users").update(
                {"reset_token": None, "token_expiry": None}
            ).or_(
                f"username.eq.{st.sidebar.session_state['reset_id']},phone.eq.{st.sidebar.session_state['reset_id']}"
            ).execute()
            st.sidebar.success(
                "Password updated! You can now log in securely."
            )
            del st.sidebar.session_state["reset_id"]
          else:
            st.sidebar.error("Invalid or expired code.")

else:
  st.sidebar.success(
      f"Logged in as: **{st.session_state.get('username', 'User')}**"
  )
  if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.rerun()

  st.sidebar.markdown("---")
  st.sidebar.title("💰 Wallet Hub")
  st.sidebar.metric(
      label="Current Balance", value=f"₦{st.session_state.wallet_balance:,.2f}"
  )

  st.sidebar.subheader("Fund Wallet via Bank Transfer")
  funding_amount = st.sidebar.number_input(
      "Enter Amount to Fund (₦)", min_value=500, max_value=50000, step=500
  )
  user_email = st.sidebar.text_input("Your Email (for receipt)")

  if st.sidebar.button("Generate Transfer Checkout"):
    if user_email:
      paystack_checkout_url = f"https://checkout.paystack.com/pay?amount={funding_amount * 100}&email={user_email}"
      st.sidebar.markdown(
          f"[ 👉 Click Here to Complete Bank Transfer]({paystack_checkout_url})",
          unsafe_allow_html=True,
      )
      st.sidebar.info(
          "After successful payment, use the simulation button below to credit"
          " your wallet."
      )
    else:
      st.sidebar.error("Please enter your email address first.")

  if st.sidebar.button("Simulate Successful Transfer"):
    st.session_state.wallet_balance += funding_amount
    st.sidebar.success(f"Wallet credited with ₦{funding_amount:,.2f}!")
    st.rerun()

# --- MAIN APP INTERFACE ---
st.title("📱 Dankowa Data & Airtime Hub")
st.write(
    "Welcome back! Buy cheap SME data and airtime instantly with automated"
    " delivery."
)

# Network Selection including additional providers
network = st.selectbox(
    "Select Network Provider",
    ["MTN", "Airtel", "Glo", "9mobile", "Smile 4G", "Spectranet"],
)
service_type = st.radio("Select Service", ["Data Bundle", "Airtime Top-up"])

# Pricing Mapping
prices = {
    "500MB - ₦130": 130,
    "1GB - ₦250": 250,
    "2GB - ₦500": 500,
    "5GB - ₦1,200": 1200,
}

cost = 0
plan = ""

if service_type == "Data Bundle":
  plan = st.selectbox("Select Data Plan", list(prices.keys()))
  cost = prices[plan]
  st.info(f"Price: ₦{cost}")
else:
  cost = st.number_input(
      "Enter Airtime Amount (₦)", min_value=50, max_value=10000, step=50
  )

phone_number = st.text_input("Enter Phone Number", max_chars=11)

if st.button("Proceed with Transaction"):
  if len(phone_number) == 11:
    if st.session_state.wallet_balance >= cost:
      # Deduct from wallet
      st.session_state.wallet_balance -= cost

      # Record Transaction
      current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      details = f"{plan}" if service_type == "Data Bundle" else f"₦{cost} Airtime"
      transaction_record = {
          "time": current_time,
          "network": network,
          "type": service_type,
          "details": details,
          "phone": phone_number,
          "cost": cost,
      }
      st.session_state.transactions.insert(0, transaction_record)

      st.success(
          f"Transaction successful! {service_type} sent to {phone_number}."
      )
    else:
      st.error(
          "Insufficient wallet funds! Please fund your wallet via bank transfer"
          " from the sidebar."
      )
  else:
    st.error("Please enter a valid 11-digit phone number.")

# Transaction History Section
st.markdown("---")
st.subheader("📜 Recent Transaction History")

if len(st.session_state.transactions) > 0:
  for idx, tx in enumerate(st.session_state.transactions):
    with st.container():
      st.write(
          f"**{idx+1}. [{tx['time']}] {tx['network']} - {tx['type']}**"
      )
      st.text(
          f"Details: {tx['details']} | Phone: {tx['phone']} | Cost:"
          f" ₦{tx['cost']}"
      )
      st.markdown("---")
else:
  st.write("No transactions recorded yet.")
