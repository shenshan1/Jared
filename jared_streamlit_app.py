import streamlit as st

st.title("Jared: Basic Tech Analysis Companion")

ticker = st.text_input("Enter a ticker symbol (e.g., TSLA):")

if ticker:
    # Dummy response, since no data fetching is possible without external libs
    st.write(f"Analyzing {ticker}...")
    st.write("Sorry, no live data or charts available without extra packages.")
    st.write("Please run this locally with required packages for full features.")
else:
    st.write("Enter a ticker to get started.")

