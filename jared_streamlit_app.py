import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Jared - Stock Analysis Agent", layout="wide")
st.title("📈 Jared: Your Technical Analysis Companion")

ticker_input = st.text_input("Enter a stock, ETF, or BDC symbol (e.g., TSLA, PLTR, O, MAIN, VTI):", "PLTR")
timeframes = {"1 Hour": ("60m", "7d"), "Daily": ("1d", "6mo"), "Weekly": ("1wk", "2y")}

def fetch_data(ticker, interval, period):
    try:
        df = yf.download(ticker, interval=interval, period=period)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def analyze(df):
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    signals = []

    # Change of Character
    if previous['Close'] < previous['EMA50'] and latest['Close'] > latest['EMA50']:
        signals.append("🟢 Bullish reversal: price crossed above EMA50.")
    elif previous['Close'] > previous['EMA50'] and latest['Close'] < latest['EMA50']:
        signals.append("🔴 Bearish reversal: price crossed below EMA50.")

    # Continuation trend
    if latest['EMA20'] > latest['EMA50'] and latest['RSI'] > 50:
        signals.append("📈 Uptrend continuation confirmed.")
    elif latest['EMA20'] < latest['EMA50'] and latest['RSI'] < 50:
        signals.append("📉 Downtrend continuation confirmed.")

    # Buy suggestion
    if latest['EMA20'] > latest['EMA50'] and latest['RSI'] < 45:
        signals.append("✅ Potential BUY zone: Uptrend with temporary RSI pullback.")
    elif latest['EMA20'] < latest['EMA50'] and latest['RSI'] > 60:
        signals.append("⚠️ Overbought in downtrend: wait before buying.")

    return signals

def plot_chart(df, timeframe_label, ticker):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Candles"))

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange', width=1), name='EMA50'))

    fig.update_layout(
        title=f"{ticker.upper()} -

