import streamlit as st
import pandas as pd
import datetime
import time
from alpaca_trade_api.rest import REST

# ✅ Pull API keys from Streamlit Cloud
ALPACA_API_KEY = st.secrets["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]

st.set_page_config(page_title="📈 Wall Street Dashboard", layout="wide")
st.title("📈 Real-Time Trading Dashboard")
st.write("Tracking stocks with RSI, MACD, VWAP, and crossover alerts.")


# 🔁 Optional auto-refresh
st.experimental_rerun = getattr(st, "experimental_rerun", lambda: None)
time.sleep(60)
st.experimental_rerun()

# ✅ Initialize Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url="https://paper-api.alpaca.markets")


#  RSI Function
def get_rsi_from_alpaca(symbol, window=14):
    bars = api.get_bars(symbol, "1D", limit=window + 1).df
    if bars.empty or len(bars) < window + 1:
        return None
    close = bars['close']
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1] if avg_loss.iloc[-1] != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

#  MACD Function
def get_macd_from_alpaca(symbol, short_window=12, long_window=26, signal_window=9):
    bars = api.get_bars(symbol, "1D", limit=long_window + signal_window).df
    if bars.empty:
        return None
    close = bars['close']
    ema_short = close.ewm(span=short_window, adjust=False).mean()
    ema_long = close.ewm(span=long_window, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    hist = macd_line - signal_line
    return round(hist.iloc[-1], 2)

# VWAP Function
def get_vwap_from_alpaca(symbol):
    bars = api.get_bars(symbol, "1D", limit=30).df
    if bars.empty:
        return None
    typical_price = (bars['high'] + bars['low'] + bars['close']) / 3
    vwap = (typical_price * bars['volume']).cumsum() / bars['volume'].cumsum()
    return round(vwap.iloc[-1], 2)

#  SMA Crossover Signal
def get_sma_crossover_signal(symbol, short_window=50, long_window=200):
    bars = api.get_bars(symbol, "1D", limit=long_window + 1).df
    if bars.empty or len(bars) < long_window:
        return "N/A"
    close = bars['close']
    sma_short = close.rolling(window=short_window).mean()
    sma_long = close.rolling(window=long_window).mean()
    if sma_short.iloc[-1] > sma_long.iloc[-1]:
        return "📈 Bullish Crossover"
    elif sma_short.iloc[-1] < sma_long.iloc[-1]:
        return "📉 Bearish Crossover"
    else:
        return "— No Crossover"

# Page Layout
st.set_page_config(page_title="Wall Street Trading Dashboard", layout="wide")
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=30))
end_date = st.sidebar.date_input("End Date", value=datetime.date.today())

st.title("📊 Real-Time Trading Dashboard")
st.markdown(f"Tracking: **{ticker}** from {start_date} to {end_date}")

#  Fetch Indicator Values
rsi_value = get_rsi_from_alpaca(ticker)
macd_value = get_macd_from_alpaca(ticker)
vwap_value = get_vwap_from_alpaca(ticker)
sma_signal = get_sma_crossover_signal(ticker)

#  Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("RSI", rsi_value if rsi_value else "N/A")
col2.metric("MACD", macd_value if macd_value else "N/A")
col3.metric("VWAP", vwap_value if vwap_value else "N/A")

#  Show SMA Crossover
st.subheader("SMA 50/200 Crossover Signal")
st.write(sma_signal)

st.info("📌 This dashboard is under construction. Real-time Alpaca integration coming up next...")
