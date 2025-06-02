import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
MORALIS_API_KEY = os.getenv("MORALIS_API_KEY")

# --- Base URLs ---
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"
MORALIS_BASE_URL = "https://deep-index.moralis.io/api/v2"
WALLET_FILE = "data/wallets.json"

# --- ETH Balance ---
def get_eth_balance(address):
    try:
        url = f"{ETHERSCAN_BASE_URL}?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data['status'] == '1':
            return int(data['result']) / 1e18
    except requests.exceptions.RequestException as e:
        print("ETH Balance API error:", e)
    return 0

# --- Transactions ---
def get_txns(address):
    try:
        url = f"{ETHERSCAN_BASE_URL}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={ETHERSCAN_API_KEY}"
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
        if data['status'] == '1':
            return data['result']
        else:
            print("Etherscan returned error:", data.get("message"))
    except requests.exceptions.RequestException as e:
        print("Transaction API error:", e)
    return []

# --- Format Transactions ---
def format_txns(txns):
    df = pd.DataFrame(txns)
    if df.empty:
        return pd.DataFrame()
    df['value'] = df['value'].astype(float) / 1e18
    df['gasUsed'] = df['gasUsed'].astype(float)
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    return df[['hash', 'from', 'to', 'value', 'gasUsed', 'timeStamp']]

# --- ERC-20 Token Balances ---
def get_token_balances(address):
    try:
        url = f"{MORALIS_BASE_URL}/{address}/erc20"
        headers = {
            "accept": "application/json",
            "X-API-Key": MORALIS_API_KEY
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        tokens = res.json()
        df = pd.DataFrame(tokens)
        if df.empty:
            return pd.DataFrame()
        df['balance'] = df['balance'].astype(float) / (10 ** df['decimals'].astype(float))
        df = df[['name', 'symbol', 'balance']]
        df = df[df['balance'] > 0.0001]
        return df
    except requests.exceptions.RequestException as e:
        print("❌ Moralis Token API error:", e)
        return pd.DataFrame()

# --- NFT Holdings Viewer ---
def get_nfts(address):
    try:
        url = f"{MORALIS_BASE_URL}/{address}/nft?chain=eth&format=decimal"
        headers = {
            "accept": "application/json",
            "X-API-Key": MORALIS_API_KEY
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        items = res.json().get('result', [])
        output = []
        for item in items:
            metadata = item.get("metadata")
            if metadata:
                try:
                    meta = eval(metadata) if isinstance(metadata, str) else metadata
                    image = meta.get("image") or ""
                    name = meta.get("name") or item.get("token_id")
                    symbol = item.get("name") or "NFT"
                    if image.startswith("ipfs://"):
                        image = image.replace("ipfs://", "https://ipfs.io/ipfs/")
                    output.append({"image": image, "name": name, "symbol": symbol})
                except:
                    continue
        return output
    except requests.exceptions.RequestException as e:
        print("❌ Moralis NFT API error:", e)
        return []

# --- CoinGecko Token Prices ---
def get_token_prices_by_ids(token_ids):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(token_ids),
            "vs_currencies": "usd"
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print("CoinGecko API error:", e)
        return {}

# --- Token Transfer History ---
def get_token_transfers(address):
    try:
        url = f"{ETHERSCAN_BASE_URL}?module=account&action=tokentx&address={address}&sort=asc&apikey={ETHERSCAN_API_KEY}"
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
        if data["status"] == "1":
            return data["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching token transfers: {e}")
    return []

# --- Wallet Save/Load ---
def load_wallets():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return {"bookmarked": [], "recent": []}

def save_wallets(data):
    with open(WALLET_FILE, "w") as f:
        json.dump(data, f, indent=4)
