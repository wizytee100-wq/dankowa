import random
from datetime import datetime, timedelta
import streamlit as st

st.subheader("Account Recovery")

# Step 1: Request username/phone to trigger reset
reset_identity = st.text_input(
    "Enter your registered Username or Phone Number"
)

if st.button("Generate Recovery Code"):
  if reset_identity:
    # Check if user exists in your database
    user = get_user_from_db(reset_identity)  

    if user:
      # Generate a secure 6-digit code
      token = str(random.randint(100000, 999999))
      # Set expiry time to 10 minutes from now
      expiry = datetime.now() + timedelta(minutes=10)

      # Save token and expiry into the database for this specific user
      save_reset_token_to_db(reset_identity, token, expiry)

      # Store state so the app knows the token was generated
      st.session_state["reset_identity"] = reset_identity
      st.session_state["token_generated"] = True

      # For a seamless live experience without SMS costs or restrictions, 
      # display the secure code directly on-screen for the user to copy:
      st.success(
          "Recovery code generated! (For testing/live display):"
          f" **{token}**"
      )
    else:
      st.error("Account not found.")
  else:
    st.warning("Please enter your username or phone number.")

# Step 2: Input code and update password
if st.session_state.get("token_generated"):
  st.markdown("---")
  entered_token = st.text_input("Enter 6-digit Recovery Code")
  new_password = st.text_input("Enter New Password", type="password")

  if st.button("Reset Password"):
    # Fetch user details from database
    user_record = get_user_from_db(st.session_state["reset_identity"])

    if user_record:
      stored_token = user_record.get("reset_token")
      token_expiry = user_record.get("token_expiry")

      # Validate token match and check if it has expired (10 min limit)
      if (
          entered_token == stored_token
          and datetime.now() < datetime.fromisoformat(token_expiry)
      ):
        # Update the password in your database and clear the token
        update_password_in_db(st.session_state["reset_identity"], new_password)
        clear_reset_token_in_db(st.session_state["reset_identity"])

        st.success(
            "Password updated successfully! You can now log in with your new"
            " password."
        )
        # Reset session state
        st.session_state["token_generated"] = False
      else:
        st.error("Invalid or expired recovery code. Please try again.")
    else:
      st.error("An error occurred. Please restart the reset process.")
