import streamlit as st
import yfinance as yf
import requests
import time
from datetime import datetime, timedelta

# --- 🟢 PAGE CONFIG ---
st.set_page_config(page_title="AI Trading Advisor V3", page_icon="📈", layout="wide")

st.title("🌟 AI Trading Advisor V3.0")
st.write(f"**Live Market Intelligence** | {datetime.now().strftime('%B %d, %Y')}")

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
        from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}&to={to_date}&token={API_KEY}"
        news_data = requests.get(news_url).json()

        if not news_data:
            return "No recent news found.", "🟡 HOLD", 0, "No data available."

        headline = news_data[0].get('headline', "No Headline")
        
        # 2. Get Price Data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")
        
        if hist.empty:
            price_change = 0.0
        else:
            price_change = ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100

        # 3. AI Sentiment Logic (The "Explainer")
        score = 0
        pos_words = ["growth", "buy", "target", "soar", "deal", "ai", "beats", "record", "bullish"]
        neg_words = ["war", "plunge", "hit", "drop", "fire", "attack", "outage", "misses", "bearish"]
        
        found_pos = [w for w in pos_words if w in headline.lower()]
        found_neg = [w for w in neg_words if w in headline.lower()]
        
        score = len(found_pos) - len(found_neg)
        
        # Build the explanation string
        explanation = f"Logic: +{len(found_pos)} pos, -{len(found_neg)} neg. Price: {price_change:.2f}%"

        # 4. Final Decision
        if score >= 1 and price_change > 0.2:
            advice = "🟢 RECOMMEND: BUY"
        elif score <= -1 or price_change < -1.0:
            advice = "🔴 RECOMMEND: SELL"
        else:
            advice = "🟡 RECOMMEND: HOLD"

        return headline, advice, score, explanation

    except Exception as e:
        return f"Error: {e}", "❌ ERROR", 0, "System failure."

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

        headline, advice, score, logic = get_market_signal(ticker)

        with alert_container:
            with st.expander(f"**{ticker}** - {advice}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📰 **Latest:** {headline}")
                with col2:
                    st.metric("AI Score", score)
                
                st.caption(f"⚙️ {logic}")
        
        time.sleep(0.5) # Faster but safe

    st.balloons()
    st.success("Full Scan Complete!")
else:
    st.info("Click the button above to analyze 100 stocks.")
