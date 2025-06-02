import streamlit as st
from app import utils
import altair as alt
from datetime import date

placeholder_path = "assets/Placeholder.png"

SYMBOL_TO_COINGECKO_ID = {
    "ETH": "ethereum", "USDT": "tether", "USDC": "usd-coin", "DAI": "dai",
    "UNI": "uniswap", "LINK": "chainlink", "WBTC": "wrapped-bitcoin",
    "MATIC": "matic-network", "SHIB": "shiba-inu", "APE": "apecoin"
}

wallets = utils.load_wallets()

def show():
    st.set_page_config(page_title="Crypto Wallet Tracker", layout="wide")
    st.title("Ethereum Wallet Dashboard")

    address = st.text_input("🔑 Enter an Ethereum Address", placeholder="e.g. vitalik.eth or 0x...")
    if not address:
        st.info("Enter a wallet address to begin.")
        return

    with st.spinner("Fetching wallet data..."):
        balance = utils.get_eth_balance(address)
        prices = utils.get_token_prices_by_ids(["ethereum"])
        eth_usd = prices.get("ethereum", {}).get("usd", 0)
        eth_value_usd = balance * eth_usd if eth_usd else 0

    st.markdown("### 💼 Wallet Overview")
    col1, col2 = st.columns(2)
    col1.metric("ETH Balance", f"{balance:.4f} ETH")
    col2.metric("ETH Value (USD)", f"${eth_value_usd:,.2f}")

    section = st.radio("Navigate", ["ERC-20 Tokens", "NFT Holdings", "Filtered Transactions", "Gas Usage", "Wallet Analytics"], horizontal=True)

    # ----------- ERC-20 TOKENS -----------
    if section == "ERC-20 Tokens":
        token_df = utils.get_token_balances(address)
        st.subheader("ERC-20 Token Balances")

        if not token_df.empty:
            st.dataframe(token_df)
            st.markdown("<br><br>", unsafe_allow_html=True)  # Spacing before chart

            token_prices_needed = [
                SYMBOL_TO_COINGECKO_ID[symbol.upper()]
                for symbol in token_df["symbol"]
                if symbol.upper() in SYMBOL_TO_COINGECKO_ID
            ]
            token_prices = utils.get_token_prices_by_ids(token_prices_needed)

            token_df["usd_value"] = 0.0
            for i, row in token_df.iterrows():
                symbol = row["symbol"].upper()
                if symbol in SYMBOL_TO_COINGECKO_ID:
                    cg_id = SYMBOL_TO_COINGECKO_ID[symbol]
                    price = token_prices.get(cg_id, {}).get("usd", 0)
                    token_df.at[i, "usd_value"] = row["balance"] * price

            token_df_sorted = token_df[token_df["usd_value"] > 0].sort_values(by="usd_value", ascending=False)
            st.bar_chart(token_df_sorted.set_index("symbol")["usd_value"])

            total_token_usd = token_df_sorted["usd_value"].sum()
            st.metric("Token Value (USD)", f"${total_token_usd:,.2f}")
            st.metric("Total Portfolio Value", f"${eth_value_usd + total_token_usd:,.2f}")
        else:
            st.warning("No ERC-20 tokens found.")

    # ----------- NFT HOLDINGS -----------
    elif section == "NFT Holdings":
        nft_list = utils.get_nfts(address)
        st.subheader("NFT Holdings")

        if nft_list:
            cols = st.columns(3)
            for i, nft in enumerate(nft_list):
                image = nft.get("image", "")
                name = nft.get("name", "Unnamed NFT")
                symbol = nft.get("symbol", "")

                if image.startswith("ipfs://"):
                    image = image.replace("ipfs://", "https://ipfs.io/ipfs/")
                if not image or not image.startswith("http"):
                    image = placeholder_path

                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div style="border:1px solid #444;padding:10px;border-radius:8px;margin-bottom:12px;text-align:center">
                            <img src="{image}" width="150" onerror="this.onerror=null;this.src='{placeholder_path}'"/><br>
                            <strong>{name}</strong><br>
                            <small>{symbol}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No NFTs found or failed to load.")

    # ----------- TRANSACTIONS -----------
    elif section == "Filtered Transactions":
        txns = utils.get_txns(address)
        txn_df = utils.format_txns(txns)

        if not txn_df.empty:
            st.subheader("Filtered Transactions")
            full_range = st.checkbox("Show All", value=True)

            if full_range:
                start_date = txn_df["timeStamp"].min().date()
                end_date = txn_df["timeStamp"].max().date()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("From", txn_df["timeStamp"].min().date())
                with col2:
                    end_date = st.date_input("To", txn_df["timeStamp"].max().date())

            col3, col4, col5 = st.columns(3)
            with col3:
                min_value = st.number_input("Min ETH", 0.0, step=0.1)
            with col4:
                from_filter = st.text_input("From Address Contains", "")
            with col5:
                to_filter = st.text_input("To Address Contains", "")

            filtered = txn_df.copy()
            filtered = filtered[
                (filtered["timeStamp"].dt.date >= start_date) &
                (filtered["timeStamp"].dt.date <= end_date) &
                (filtered["value"] >= min_value)
            ]
            if from_filter:
                filtered = filtered[filtered["from"].str.contains(from_filter, case=False)]
            if to_filter:
                filtered = filtered[filtered["to"].str.contains(to_filter, case=False)]

            filtered_display = filtered.reset_index(drop=True)
            st.dataframe(filtered_display)

            # 📁 Download as CSV
            csv = filtered_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📁 Download Filtered Transactions as CSV",
                data=csv,
                file_name="filtered_transactions.csv",
                mime="text/csv",
            )

            st.markdown("**Top 10 Largest Transactions**")
            top_txns = txn_df.sort_values(by="value", ascending=False).head(10)
            st.dataframe(top_txns.reset_index(drop=True))
        else:
            st.warning("No transactions found.")

    # ----------- GAS USAGE -----------
    elif section == "Gas Usage":
        txns = utils.get_txns(address)
        txn_df = utils.format_txns(txns)

        if not txn_df.empty:
            st.subheader("Gas Usage")

            full_range = st.checkbox("Show All", value=True, key="gas_range")
            if full_range:
                start_date = txn_df["timeStamp"].min().date()
                end_date = txn_df["timeStamp"].max().date()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("From Date", txn_df["timeStamp"].min().date(), key="gas_from")
                with col2:
                    end_date = st.date_input("To Date", txn_df["timeStamp"].max().date(), key="gas_to")

            gas_df = txn_df[
                (txn_df["timeStamp"].dt.date >= start_date) &
                (txn_df["timeStamp"].dt.date <= end_date)
            ]

            if not gas_df.empty:
                st.line_chart(gas_df.set_index("timeStamp")["gasUsed"])

                total_gas = gas_df["gasUsed"].sum()
                avg_gas = gas_df["gasUsed"].mean()
                max_gas = gas_df["gasUsed"].max()
                gas_eth = total_gas * 1e-9

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Gas Used", f"{total_gas:,.0f}")
                col2.metric("Avg Gas per Txn", f"{avg_gas:,.0f}")
                col3.metric("Est. ETH Spent on Gas", f"{gas_eth:.6f} ETH")
            else:
                st.warning("No gas data found for selected range.")
        else:
            st.warning("No transactions found to compute gas usage.")

        # ----------- WALLET ANALYTICS ------------
    elif section == "Wallet Analytics":
        st.subheader("📊 Wallet Analytics")

        txns = utils.get_txns(address)
        txn_df = utils.format_txns(txns)

        if txn_df.empty:
            st.warning("No transaction data found for analytics.")
        else:
            # ✅ Most Active Day
            active_day = txn_df["timeStamp"].dt.date.value_counts().idxmax()
            txn_count = txn_df["timeStamp"].dt.date.value_counts().max()

            # ✅ Average Transaction Size (non-zero)
            nonzero_txns = txn_df[txn_df["value"] > 0]
            avg_txn_size = nonzero_txns["value"].mean() if not nonzero_txns.empty else 0

            # ✅ Historical ETH Balance (approximation)
            txn_df_sorted = txn_df.sort_values(by="timeStamp")
            balance_series = txn_df_sorted["value"].cumsum()
            balance_series.index = txn_df_sorted["timeStamp"]

            # ✅ Most Transacted Token (ERC-20)
            token_transfers = utils.get_token_transfers(address)
            if token_transfers:
                token_counts = {}
                for transfer in token_transfers:
                    symbol = transfer.get("tokenSymbol", "UNKNOWN")
                    token_counts[symbol] = token_counts.get(symbol, 0) + 1
                most_transacted_token = max(token_counts, key=token_counts.get)
                token_txn_count = token_counts[most_transacted_token]
            else:
                most_transacted_token = "N/A"
                token_txn_count = 0

            # 📋 Display Insights
            st.markdown("### Key Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Most Active Day", str(active_day), f"{txn_count} txns")
            col2.metric("Avg Txn Size (ETH)", f"{avg_txn_size:.4f}")
            col3.metric("Most Transacted Token", most_transacted_token, f"{token_txn_count} transfers")

            # 📈 Historical ETH Balance Chart
            st.markdown("### Historical ETH Balance (Approximate)")
            st.line_chart(balance_series)

