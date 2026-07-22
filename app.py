import streamlit as st

st.set_page_config(page_title="Dankowa Data & Airtime Hub", page_icon="📱", layout="centered")

st.title("📱 Dankowa Data & Airtime Hub")
st.write("Welcome! Buy cheap SME data and airtime instantly for MTN, Airtel, Glo, and 9mobile.")

network = st.selectbox("Select Network", ["MTN", "Airtel", "Glo", "9mobile"])
service_type = st.radio("Select Service", ["Data Bundle", "Airtime Top-up"])

if service_type == "Data Bundle":
    plan = st.selectbox("Select Data Plan", ["500MB - ₦130", "1GB - ₦250", "2GB - ₦500", "5GB - ₦1,200"])
else:
    amount = st.number_input("Enter Airtime Amount (₦)", min_value=50, max_value=10000, step=50)

phone_number = st.text_input("Enter Phone Number", max_chars=11)

if st.button("Proceed with Transaction"):
    if len(phone_number) == 11:
        st.success(f"Transaction successful! {service_type} sent to {phone_number}.")
    else:
        st.error("Please enter a valid 11-digit phone number.")

