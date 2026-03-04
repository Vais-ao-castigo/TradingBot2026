import streamlit as st
import yfinance as yf
import requests
import time
from datetime import datetime, timedelta

# --- 🟢 PAGE CONFIG ---
st.set_page_config(page_title="AI Trading Advisor V3.2", page_icon="📈", layout="wide")

# --- 🟢 HEADER & DISCLAIMER ---
st.title("🌟 AI Trading Advisor V3.2")

# 🚩 LEGAL DISCLAIMER
st.warning("""
**⚠️ USE AT YOUR OWN RISK:** This AI is for educational purposes only. It analyzes news headlines using 
basic sentiment logic and does not account for complex market factors. AI is **not 100% accurate**. 
Always consult a human financial advisor before trading.
""")

st.write(f"**Live Market Intelligence** | {datetime.now().strftime('%B %d, %Y')}")

# --- 🟢 THE SCALE (Legend) ---
with st.sidebar:
    st.header("📊 Sentiment Scale")
    st.write("The AI scans headlines for 'Trigger Words'.")
    st.code("""
 +3 or more: Strong Buy
 +1 to +2:   Speculative Buy
  0:         Neutral / Hold
 -1 to -2:   Caution / Sell
 -3 or less: Strong Sell
    """)
    st.info("Score = (Pos Words) - (Neg Words)")

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
        # 1. Get News from Finnhub
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}&to={to_date}&token={API_KEY}"
        news_data = requests.get(news_url).json()
        
        if not news_data:
            return "No news found.", "🟡 HOLD", 0

        headline = news_data[0].get('headline', "No Headline")
        
        # 2. Get Price Data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        price_change = 0.0
        if not hist.empty:
            price_change = ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
        
        # 3. Decision Logic (Advanced Sentiment Scoring)
        bad_words = ["war", "plunge", "hit", "drop", "fire", "attack", "outage", "miss", "risk", "lawsuit", "slump"]
        good_words = ["growth", "buy", "target", "soar", "deal", "ai", "beat", "surge", "win", "partnership", "record"]
        
        headline_low = headline.lower()
        pos_count = sum(1 for word in good_words if word in headline_low)
        neg_count = sum(1 for word in bad_words if word in headline_low)
        
        score = pos_count - neg_count

        # Combining Score + Price Change for Advice
        if score >= 1 and price_change > 0:
            advice = f"🟢 RECOMMEND: BUY (Score: {score})"
        elif score <= -1 or price_change < -1.5:
            advice = f"🔴 RECOMMEND: SELL (Score: {score})"
        else:
            advice = f"🟡 RECOMMEND: HOLD (Score: {score})"
            
        return headline, advice, score

    except Exception as e:
        return f"Error: {e}", "❌ ERROR", 0

# --- 🚀 THE APP INTERFACE ---
if st.button('🔍 Start Real-Time Scan'):
    st.write("---")
    progress_bar = st.progress(0)
    status_text = st.empty()
    alert_container = st.container()

    for i, ticker in enumerate(WATCHLIST):
        percent_complete = (i + 1) / len(WATCHLIST)
        progress_bar.progress(percent_complete)
        status_text.text(f"Analyzing {ticker} ({i+1}/{len(WATCHLIST)})...")
        
        headline, advice, score = get_market_signal(ticker)
        
        with alert_container:
            # Expander keeps the 100 stocks looking clean
            with st.expander(f"**{ticker}** | {advice}"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📰 **Latest News:** {headline}")
                with col2:
                    st.metric("AI Score", score)
        
        # Keep 1.5s to avoid Finnhub "Rate Limit" errors
        time.sleep(1.5) 

    st.balloons()
    st.success("Full Scan Complete!")
else:
    st.info("Click the button above to analyze 100 stocks.")
