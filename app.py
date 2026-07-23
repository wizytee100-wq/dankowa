from datetime import datetime, timedelta
import random
from supabase import create_client
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Dankowa Data & Airtime Hub", page_icon="📱", layout="centered"
)

# Initialize Supabase client
supabase = create_client(
    st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
)

# Initialize Session State
if "wallet_balance" not in st.session_state:
  st.session_state.wallet_balance = 5000.00

if "transactions" not in st.session_state:
  st.session_state.transactions = []

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False


# Database Helper Function
def get_user_from_db(identifier):
  try:
    response = (
        supabase.table("profiles")
        .select("*")
        .or_(f"username.eq.{identifier},phone.eq.{identifier}")
        .execute()
    )
    if response.data:
      return response.data[0]
  except Exception:
    pass
  return None


# --- GATEKEEPER: IF NOT LOGGED IN, SHOW AUTHENTICATION SCREENS ---
if not st.session_state["logged_in"]:
  st.title("📱 Dankowa Data & Airtime Hub")
  st.write("Please log in or create an account to access the platform.")

  auth_tab = st.radio(
      "Choose Action", ["Log In", "Sign Up", "Forgot Password"]
  )
  st.markdown("---")

  if auth_tab == "Log In":
    st.subheader("Log In to Your Account")
    login_id = st.text_input("Username or Phone Number")
    login_pass = st.text_input("Password", type="password")

    if st.button("Log In Now"):
      user = get_user_from_db(login_id)
      if user and user.get("password") == login_pass:
        st.session_state["logged_in"] = True
        st.session_state["username"] = user.get("username")
        st.success("Logged in successfully!")
        st.rerun()
      else:
        st.error("Invalid credentials. Please check your username and password.")

  elif auth_tab == "Sign Up":
    st.subheader("Create a New Account")
    new_user = st.text_input("Choose Username")
    new_phone = st.text_input("Phone Number")
    new_pass = st.text_input("Choose Password", type="password")

    if st.button("Register Account"):
      if new_user and new_phone and new_pass:
        try:
          supabase.table("profiles").insert({
              "username": new_user,
              "phone": new_phone,
              "password": new_pass,
          }).execute()
          st.success("Account created successfully! Please switch to 'Log In'.")
        except Exception as e:
          st.error(f"Error creating account: {e}")
      else:
        st.warning("Please fill in all fields.")

  elif auth_tab == "Forgot Password":
    st.subheader("Account Recovery")
    reset_id = st.text_input("Enter your registered Username or Phone")

    if st.button("Generate Recovery Code"):
      if reset_id:
        user = get_user_from_db(reset_id)
        if user:
          token = str(random.randint(100000, 999999))
          expiry = datetime.now() + timedelta(minutes=10)
          supabase.table("profiles").update({
              "reset_token": token,
              "token_expiry": expiry.isoformat(),
          }).or_(f"username.eq.{reset_id},phone.eq.{reset_id}").execute()

          st.session_state["reset_id"] = reset_id
          st.success(
              "Recovery code generated! Your code is: " f"**{token}**"
          )
        else:
          st.error("Account not found.")
      else:
        st.warning("Please enter your identifier.")

    if "reset_id" in st.session_state:
      entered_token = st.text_input("Enter 6-digit Recovery Code")
      new_pass_input = st.text_input(
          "Enter New Password", type="password", key="new_pass_inp"
      )

      if st.button("Reset Password"):
        user_rec = get_user_from_db(st.session_state["reset_id"])
        if user_rec:
          stored_token = user_rec.get("reset_token")
          token_exp = user_rec.get("token_expiry")
          if (
              entered_token == stored_token
              and token_exp
              and datetime.now() < datetime.fromisoformat(token_exp)
          ):
            supabase.table("profiles").update({"password": new_pass_input}).or_(
                f"username.eq.{st.session_state['reset_id']},phone.eq.{st.session_state['reset_id']}"
            ).execute()
            supabase.table("profiles").update(
                {"reset_token": None, "token_expiry": None}
            ).or_(
                f"username.eq.{st.session_state['reset_id']},phone.eq.{st.session_state['reset_id']}"
            ).execute()
            st.success("Password updated successfully! You can now log in.")
            del st.session_state["reset_id"]
          else:
            st.error("Invalid or expired recovery code.")

# --- MAIN APP INTERFACE (ONLY SHOWN AFTER SUCCESSFUL LOGIN) ---
else:
  # Sidebar for Wallet Management & Logout
  st.sidebar.title("💰 Wallet Hub")
  st.sidebar.success(
      f"Logged in as: **{st.session_state.get('username', 'User')}**"
  )
  if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.rerun()

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

  # Main Dashboard Content
  st.title("📱 Dankowa Data & Airtime Hub")
  st.write(
      "Welcome back! Buy cheap SME data and airtime instantly with automated"
      " delivery."
  )

  # Referral Banner / Invite Feature
  st.info(
      "🎁 **Refer & Earn:** Share your username **"
      f"{st.session_state.get('username', 'User')}** with friends and get ₦100"
      " bonus when they fund their wallet!"
  )

  network = st.selectbox(
      "Select Network Provider",
      ["MTN", "Airtel", "Glo", "9mobile", "Smile 4G", "Spectranet"],
  )
  service_type = st.radio("Select Service", ["Data Bundle", "Airtime Top-up"])

  # Massive Comprehensive Data Plan List (MB -> GB -> TB -> Unlimited)
  prices = {
      "100MB (1 Day) - ₦50": 50,
      "200MB (3 Days) - ₦90": 90,
      "500MB (7 Days) - ₦130": 130,
      "1GB (30 Days) - ₦250": 250,
      "2GB (30 Days) - ₦500": 500,
      "3GB (30 Days) - ₦750": 750,
      "5GB (30 Days) - ₦1,200": 1200,
      "10GB (30 Days) - ₦2,300": 2300,
      "20GB (30 Days) - ₦4,500": 4500,
      "40GB (Monthly Mega) - ₦8,500": 8500,
      "50GB (TB Tier) - ₦10,500": 10500,
      "100GB (TB Tier) - ₦20,000": 20000,
      "200GB (TB Tier) - ₦38,000": 38000,
      "500GB (Heavy Duty TB) - ₦90,000": 90000,
      "1TB (Enterprise Terabyte) - ₦175,000": 175000,
      "Unlimited Plan (1 Month) - ₦45,000": 45000,
  }

  cost = 0
  plan = ""

  if service_type == "Data Bundle":
    plan = st.selectbox("Select Data Plan", list(prices.keys()))
    cost = prices[plan]
    st.info(f"Price: ₦{cost:,}")
  else:
    cost = st.number_input(
        "Enter Airtime Amount (₦)", min_value=50, max_value=10000, step=50
    )

  phone_number = st.text_input("Enter Phone Number", max_chars=11)

  if st.button("Proceed with Transaction"):
    if len(phone_number) == 11:
      if st.session_state.wallet_balance >= cost:
        st.session_state.wallet_balance -= cost

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details = (
            f"{plan}" if service_type == "Data Bundle" else f"₦{cost} Airtime"
        )
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
            "Insufficient wallet funds! Please fund your wallet via bank"
            " transfer from the sidebar."
        )
    else:
      st.error("Please enter a valid 11-digit phone number.")

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
            f" ₦{tx['cost']:,}"
        )
        st.markdown("---")
  else:
    st.write("No transactions recorded yet.")
