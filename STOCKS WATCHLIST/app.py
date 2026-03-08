import streamlit as st
import yfinance as yf
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# --- 🟢 1. PAGE CONFIG & GHOST MODE ---
# This makes it look like a professional standalone website
st.set_page_config(page_title="AI Trading Advisor V3.7", page_icon="📈", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 🟢 2. SIDEBAR TOOLS ---
with st.sidebar:
    st.header("🚀 Quick Tools")
    
    # SHARE SECTION
    st.subheader("📢 Share with Friends")
    # Change the link below to your actual URL once you set your custom one!
    my_url = "https://ai-stock-advisor.streamlit.app" 
    st.text_input("Copy Link:", my_url)
    st.caption("Share this link with other traders!")

    st.divider()

    # REQUEST A STOCK (This goes to your private logs)
    st.subheader("📩 Suggest a Stock")
    user_request = st.text_input("What should I scan next?", placeholder="e.g., PLTR or BTC-USD")
    if user_request:
        st.success(f"Noted! I'll look into {user_request}.")
        print(f"🔥 USER REQUESTED: {user_request}") 

    st.divider()

    # AI SCALE LEGEND
    st.subheader("⚖️ AI Score Legend")
    st.code("+3 or more: Strong Buy\n 0: Neutral / Hold\n-3 or less: Strong Sell")
    st.info("Score = (Good News) - (Bad News)")

    st.divider()
    
    # MARKET LEADER SPOTLIGHT
    st.subheader("🏆 Top Pick Today")
    spotlight = st.empty()
    spotlight.info("Run scan to see leader.")

# --- 🟢 3. HEADER & SEO SECTION (Updated!) ---
st.title("🌟 AI Trading Advisor: Free Stock Sentiment Scanner")

# This paragraph is "SEO Gold" - it tells Google exactly what you do.
st.write("""
### The best AI-powered tool for real-time stock market news analysis.
Our **AI Trading Advisor** scans the top 100 stocks (including NVIDIA, Tesla, and Apple) 
using advanced sentiment analysis to find **Buy and Sell signals** based on live 
market intelligence. Perfect for NASDAQ and NYSE traders looking for an edge in 2026.
""")

st.warning("""
**⚠️ USE AT YOUR OWN RISK:** This AI is for educational purposes only. AI is **not 100% accurate**. 
Always consult a human financial advisor before trading.
""")
st.write(f"**Live Market Intelligence** | {datetime.now().strftime('%B %d, %Y')}")

# --- 🟢 4. THE WATCHLIST (Your 100 Stocks) ---
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
        
        headline = news_data[0].get('headline', "No Recent News") if news_data else "No Recent News"
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        price_change = ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100 if not hist.empty else 0
        
        good_words = ["growth", "buy", "target", "soar", "deal", "ai", "beat", "surge", "win", "partnership", "record", "up"]
        bad_words = ["war", "plunge", "hit", "drop", "fire", "attack", "outage", "miss", "risk", "lawsuit", "slump", "down"]
        
        low_h = headline.lower()
        pos_count = sum(1 for word in good_words if word in low_h)
        neg_count = sum(1 for word in bad_words if word in low_h)
        score = pos_count - neg_count

        if score >= 1 and price_change > 0:
            advice = "BUY"
        elif score <= -1 or price_change < -1.5:
            advice = "SELL"
        else:
            advice = "HOLD"
            
        return headline, advice, score
    except:
        return "N/A", "HOLD", 0

# --- 🚀 5. THE MAIN INTERFACE ---
if st.button('🚀 Start Full Market Analysis'):
    st.write("---")
    
    # Metrics columns
    m1, m2, m3 = st.columns(3)
    buy_m, hold_m, sell_m = m1.metric("🟢 BUYS", "0"), m2.metric("🟡 HOLDS", "0"), m3.metric("🔴 SELLS", "0")

    progress = st.progress(0)
    status_text = st.empty()
    alert_container = st.container()

    summary = {"BUY": 0, "HOLD": 0, "SELL": 0}
    best_score = -99
    best_ticker = ""

    for i, ticker in enumerate(WATCHLIST):
        progress.progress((i + 1) / len(WATCHLIST))
        status_text.text(f"Analyzing {ticker}...")
        
        head, adv, scr = get_market_signal(ticker)
        
        summary[adv] += 1
        if scr > best_score:
            best_score = scr
            best_ticker = ticker
            # Update Spotlight in Sidebar Live
            spotlight.success(f"🌟 **{best_ticker}** (Score: {best_score})")

        buy_m.metric("🟢 BUYS", summary["BUY"])
        hold_m.metric("🟡 HOLDS", summary["HOLD"])
        sell_m.metric("🔴 SELLS", summary["SELL"])

        with alert_container:
            color = "green" if adv == "BUY" else "red" if adv == "SELL" else "orange"
            with st.expander(f"**{ticker}** | :{color}[{adv}] (Score: {scr})"):
                st.write(f"📰 {head}")
                st.link_button(f"View {ticker} Chart", f"https://finance.yahoo.com/quote/{ticker}")

        time.sleep(1.2) # API Protection

    # Summary Chart
    st.divider()
    st.header("📊 Market Sentiment Summary")
    df_chart = pd.DataFrame(list(summary.items()), columns=['Signal', 'Count'])
    st.bar_chart(df_chart.set_index('Signal'))
    
    st.balloons()
    st.success(f"✅ Scan Complete! Top Pick: **{best_ticker}**")
else:
    st.info("Ready for analysis. Click the button to start.")
