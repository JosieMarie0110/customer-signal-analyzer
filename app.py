import streamlit as st
from analyzer import analyze_customer_message

st.title("Customer Psychology Analyzer")

st.write("Paste a customer email and detect psychological signals.")

customer_message = st.text_area("Customer message")

if st.button("Analyze"):

    if customer_message.strip() == "":
        st.warning("Please paste a message")
    else:

        result = analyze_customer_message(customer_message)

        st.subheader("Analysis")

        st.write(result)
