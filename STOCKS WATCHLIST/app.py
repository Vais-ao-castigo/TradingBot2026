import streamlit as st
import yfinance as yf
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# --- 🟢 GHOST MODE (Hides GitHub Icon & Streamlit Branding) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 🟢 PAGE CONFIG ---
st.set_page_config(page_title="AI Trading Advisor V3.3", page_icon="📈", layout="wide")

# --- 🟢 HEADER & DISCLAIMER ---
st.title("🌟 AI Trading Advisor V3.3")

st.warning("""
**⚠️ USE AT YOUR OWN RISK:** This AI is for educational purposes only. AI is **not 100% accurate**. 
Always consult a human financial advisor before trading.
""")

st.write(f"**Live Market Intelligence** | {datetime.now().strftime('%B %d, %Y')}")

# --- 🟢 THE SCALE (Sidebar) ---
with st.sidebar:
    st.header("📊 Sentiment Scale")
    st.code("""
 +3 or more: Strong Buy
 +1 to +2:   Speculative Buy
  0:         Neutral / Hold
 -1 to -2:   Caution / Sell
 -3 or less: Strong Sell
    """)
    st.info("The AI scans headlines for 'Trigger Words' and combines them with price action.")

# --- 🟢 SETUP ---
API_KEY = "d6jgtchr01qkvh5prf7gd6jgtchr01qkvh5prf80" 
WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "LLY", "JPM",
    "UNH", "XOM", "V", "MA", "PG", "COST", "HD", "JNJ", "ABBV", "BAC",
    "WMT", "KO", "CRM", "NFLX", "ADBE", "AMD", "ORCL", "PEP", "CVX", "MRK",
    "TMO", "WFC", "CSCO", "ACN", "MCD", "ABT", "LIN", "DHR", "INTC", "INTU",
    "DIS", "TXN", "PM", "VZ", "AMAT", "CAT", "PFE", "UNP", "IBM", "AMGN",
    "NOW", "LOW", "ISRG", "QCOM", "HON", "GE", "AXP", "SPGI", "T", "BA",
    "GS", "NEE", "BKNG", "PLD", "MS", "RTX", "TJX", "VRTX", "ELV", "ADP",
    "MDT", "SYK", "BLK", "ETN", "MMC", "LMT", "SCHW", "ADI", "MDLZ", "CB",
    "AMT", "CI", "C", "GILD", "BMY", "MU", "LRCX", "DE", "REGN", "ZTS",
    "PLTR", "UBER", "SNPS", "PANW", "CDNS", "KLAC", "BSX", "VRSK", "MNST", "ORLY"
]

def get_market_signal(ticker):
    try:
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}&to={to_date}&token={API_KEY}"
        news_data = requests.get(news_url).json()
        
        if not news_data:
            return "No news found.", "🟡 HOLD", 0

        headline = news_data[0].get('headline', "No Headline")
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        price_change = 0.0
        if not hist.empty:
            price_change = ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
        
        bad_words = ["war", "plunge", "hit", "drop", "fire", "attack", "outage", "miss", "risk", "lawsuit", "slump", "down", "bearish"]
        good_words = ["growth", "buy", "target", "soar", "deal", "ai", "beat", "surge", "win", "partnership", "record", "up", "bullish"]
        
        headline_low = headline.lower()
        pos_count = sum(1 for word in good_words if word in headline_low)
        neg_count = sum(1 for word in bad_words if word in headline_low)
        score = pos_count - neg_count

        if score >= 1 and price_change > 0:
            advice = "BUY"
        elif score <= -1 or price_change < -1.5:
            advice = "SELL"
        else:
            advice = "HOLD"
            
        return headline, advice, score

    except Exception as e:
        return f"Error: {e}", "ERROR", 0

# --- 🚀 THE APP INTERFACE ---
if st.button('🚀 Start Full Market Analysis'):
    st.write("---")
    
    # Summary Dashboard Setup
    m1, m2, m3 = st.columns(3)
    buy_metric = m1.metric("🟢 BUY SIGNALS", "0")
    hold_metric = m2.metric("🟡 HOLD SIGNALS", "0")
    sell_metric = m3.metric("🔴 SELL SIGNALS", "0")

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Containers for results
    chart_container = st.empty()
    alert_container = st.container()

    # Data tracking
    summary_data = {"BUY": 0, "HOLD": 0, "SELL": 0}
    top_score = -99
    top_ticker = ""

    for i, ticker in enumerate(WATCHLIST):
        percent_complete = (i + 1) / len(WATCHLIST)
        progress_bar.progress(percent_complete)
        status_text.text(f"Scanning: {ticker} ({i+1}/{len(WATCHLIST)})")
        
        headline, advice, score = get_market_signal(ticker)
        
        # Update Counts
        if advice in summary_data:
            summary_data[advice] += 1
        
        # Track Top Pick
        if score > top_score:
            top_score = score
            top_ticker = ticker

        # Update Live Metrics
        buy_metric.metric("🟢 BUY SIGNALS", summary_data["BUY"])
        hold_metric.metric("🟡 HOLD SIGNALS", summary_data["HOLD"])
        sell_metric.metric("🔴 SELL SIGNALS", summary_data["SELL"])

        with alert_container:
            color = "green" if advice == "BUY" else "red" if advice == "SELL" else "orange"
            with st.expander(f"**{ticker}** | :{color}[{advice}] (Score: {score})"):
                st.write(f"📰 **Latest News:** {headline}")
                st.link_button(f"Analyze {ticker} on Yahoo Finance", f"https://finance.yahoo.com/quote/{ticker}")

        time.sleep(1.5) 

    # Final Summary Visuals
    st.divider()
    st.header("📊 Market Sentiment Summary")
    df_chart = pd.DataFrame(list(summary_data.items()), columns=['Signal', 'Count'])
    st.bar_chart(df_chart.set_index('Signal'))
    
    st.balloons()
    st.success(f"✅ Scan Complete! Top Pick: **{top_ticker}** with a score of **{top_score}**.")
else:
    st.info("Ready for analysis. Click the button above to start the 100-stock scan.")

