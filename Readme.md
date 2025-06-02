# 🦊 Ethereum Wallet Tracker with Streamlit & Etherscan API

**Track, Analyze & Visualize Ethereum Wallets** in real-time. This project combines on-chain data inspection with modern data visualization and optional blockchain analytics.

---

## 📝 Description

This app is a full-fledged Ethereum wallet dashboard built using **Streamlit**, enabling users to:

- Analyze Ethereum wallet balances, tokens, and NFTs  
- Filter and download transactions  
- Visualize gas usage  
- Understand wallet activity patterns  
- Get wallet analytics like average txn size, active day, and more  

It fetches real-time data via **public blockchain APIs** (like Etherscan or Covalent) and presents them through clean, interactive UI powered by Streamlit.

---

## 📌 Domain

- Web3 / Blockchain Analytics  
- Data Visualization & Dashboards  
- Crypto Portfolio Intelligence  

---

## ⚙️ Technology

| Category              | Tools & APIs                                         |
|----------------------|------------------------------------------------------|
| **Frontend**         | Streamlit                                            |
| **Backend**          | Python 3.10+                                         |
| **Data APIs**        | Etherscan API, CoinGecko API                         |
| **Visualization**    | Altair, Matplotlib                                   |
| **NFT/IPFS Support** | IPFS Image Gateways                                  |
| **Wallet Analytics** | Pandas-based time series + transaction analysis      |

---

## 💻 Languages

- Python (3.10+)

---

## 🧰 Framework & Libraries

- `streamlit`, `pandas`, `requests`, `altair`, `matplotlib`  
- `web3`, `python-dotenv`  
- `aiohttp`, `beautifulsoup4` (for news scraping extensions, optional)

---

## 🗂️ Project Directory Structure

```

crypto-wallet-tracker/
│
├── app/
│   ├── dashboard.py            # Streamlit app logic
│   ├── utils.py                # API handlers & processing functions
│
├── assets/
│   └── Placeholder.png         # Fallback NFT image
│
├── data/
│   └── wallets.json            # Bookmark storage (optional)
│
|__ output
├── streamlit\_app.py            # App entry point
├── requirements.txt            # Pip dependencies
└── README.md                   # This file

```

---

## 🔁 Dashboard Workflow

### 1. Wallet Lookup  
User enters an Ethereum address or ENS → fetches ETH balance & tokens.

### 2. Token Balances  
Shows ERC-20 tokens with current USD value via CoinGecko.

### 3. NFT Holdings  
Card-style layout for NFTs, fallback image used if preview fails.

### 4. Filtered Transactions  
Date/amount/address filters + top 10 largest txns.

### 5. Gas Usage  
Line chart for gas used over time, with summary stats.

### 6. Wallet Analytics  
- Most active day  
- Average transaction size  
- Most transacted ERC-20 token  
- ETH balance over time (approximate)

### 7. CSV Export  
Download filtered transactions as `.csv`.
