import streamlit as st

def show():
    st.set_page_config(page_title="Crypto Wallet Tracker", layout="centered")

    st.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Ethereum_logo_translucent.svg", width=60)
    st.title("Welcome to Crypto Wallet Tracker")

    st.write("Track your Ethereum wallet's activity, token balances, NFTs, and more — all in one place.")

    st.markdown("""
    ### Key Features
    - View ETH balance and full transaction history  
    - Analyze token holdings and gas fees  
    - Display NFTs in your wallet  
    - Portfolio tracking with live price data  
    """)

    st.caption("Try it later with: `0x742d35Cc6634C0532925a3b844Bc454e4438f44e`")

    if st.button("Track Your Ethereum Wallet"):
        st.session_state.page = "dashboard"

    st.markdown(
        "<hr style='border: 1px solid #444;'>"
        "<div style='text-align:center; font-size:0.9em;'>"
        "</div>",
        unsafe_allow_html=True
    )


