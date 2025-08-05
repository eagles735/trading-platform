import yfinance as yf
import pandas as pd
import time


from config import ALPACA_API_KEY, ALPACA_SECRET_KEY
from alpaca_trade_api.rest import REST

# List of tickers (you can expand this later)
tickers = [
    "AAPL", "TSLA", "AMD", "MSFT", "GOOGL", "META", "NFLX",
    "NVDA", "PYPL", "CRM", "UBER", "SNOW", "INTC", "PINS"
]

# RSI calculation function
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Main screener
oversold = []

for ticker in tickers:
    print(f"\n🔍 Checking {ticker}...")
    try:
        time.sleep(2)  # Prevent Yahoo Finance rate limiting
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)

        if data.empty or len(data) < 15:
            print(f"⚠️ Skipping {ticker} — Not enough data.")
            continue

        data['RSI'] = calculate_rsi(data)
        latest_rsi = data['RSI'].iloc[-1]

        if pd.notna(latest_rsi) and latest_rsi < 30:
            oversold.append((ticker, round(latest_rsi, 2)))

    except Exception as e:
        print(f"❌ Skipping {ticker} — Error: {e}")

# Print results
print("\n📉 Oversold Stocks (RSI < 30):")
for ticker, rsi in oversold:
    print(f"{ticker}: RSI = {rsi}")
    
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY
from alpaca_trade_api.rest import REST

def test_alpaca_connection():
    api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url="https://paper-api.alpaca.markets")
    account = api.get_account()
    print("✅ Connected to Alpaca! Account status:", account.status)

test_alpaca_connection()
