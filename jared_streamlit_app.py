import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Jared - Your Tech Analysis Companion", layout="wide")

st.title("Jared: Technical Analysis Companion")

# User input for tickers - comma separated
ticker_input = st.text_input(
    "Enter ticker symbols separated by commas (e.g. TSLA, PLTR, AAPL):",
    value="PLTR, TSLA, O, MAIN, MSTY, COIN, HOOD"
)

tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

timeframes = {
    '1h': '60m',
    'Daily': '1d',
    'Weekly': '1wk'
}

def fetch_data(ticker, interval, period):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        data.dropna(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker} {interval}: {e}")
        return None

def analyze_data(df):
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    alerts = []
    
    if len(df) > 2:
        if df['Close'].iloc[-2] < df['EMA50'].iloc[-2] and df['Close'].iloc[-1] > df['EMA50'].iloc[-1]:
            alerts.append("Bullish Change of Character detected: Price crossed above EMA50.")
        if df['Close'].iloc[-2] > df['EMA50'].iloc[-2] and df['Close'].iloc[-1] < df['EMA50'].iloc[-1]:
            alerts.append("Bearish Change of Character detected: Price crossed below EMA50.")
    
    if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] and df['RSI'].iloc[-1] > 50:
        alerts.append("Continuation trend confirmed: EMA20 > EMA50 and RSI > 50.")
    elif df['EMA20'].iloc[-1] < df['EMA50'].iloc[-1] and df['RSI'].iloc[-1] < 50:
        alerts.append("Continuation trend confirmed: EMA20 < EMA50 and RSI < 50 (downtrend).")
    
    recent_high = df['High'].rolling(window=10).max().iloc[-1]
    recent_low = df['Low'].rolling(window=10).min().iloc[-1]
    last_close = df['Close'].iloc[-1]

    if abs(last_close - recent_high)/recent_high < 0.02:
        alerts.append(f"Price near recent swing high (POI): {recent_high:.2f}")
    elif abs(last_close - recent_low)/recent_low < 0.02:
        alerts.append(f"Price near recent swing low (POI): {recent_low:.2f}")

    return alerts

def plot_candles_with_ema(df, ticker, timeframe):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Candles')])
    
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange', width=1), name='EMA50'))
    
    fig.update_layout(
        title=f"{ticker} {timeframe} Chart with EMA20 & EMA50",
        xaxis_title="Date",
        yaxis_title="Price",
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        template="plotly_dark"
    )
    return fig

if not tickers:
    st.warning("Please enter at least one ticker symbol.")
else:
    for ticker in tickers:
        st.header(f"Analysis for {ticker}")
        for tf_name, tf_interval in timeframes.items():
            period = '30d' if tf_interval == '60m' else '6mo'
            df = fetch_data(ticker, tf_interval, period)
            if df is None or df.empty:
                st.write(f"No data available for {ticker} on {tf_name} timeframe.")
                continue

            alerts = analyze_data(df)

            st.subheader(f"{tf_name} timeframe")
            for alert in alerts:
                st.info(alert)

            fig = plot_candles_with_ema(df, ticker, tf_name)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
