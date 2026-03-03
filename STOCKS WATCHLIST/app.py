import streamlit as st
import yfinance as yf
import time

st.set_page_config(page_title="AI Stock Advisor V3", page_icon="📈")

st.title("🌟 AI Trading Advisor V3.0")
st.caption("Live Market Intelligence | March 2026")

# List of stocks to analyze (Add your 100 stocks here!)
tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "LLY", "AVGO", "V"]

if st.button("🚀 Start Full Market Scan"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        # Update progress
        percent_complete = (i + 1) / len(tickers)
        progress_bar.progress(percent_complete)
        status_text.text(f"Analyzing {ticker} ({i+1}/{len(tickers)})...")
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news[:3] # Get latest 3 stories
            
            with st.expander(f"🔍 Analysis for {ticker}"):
                score = 0
                if not news:
                    st.write("No recent news found.")
                else:
                    for item in news:
                        title = item['title']
                        st.write(f"📰 {title}")
                        
                        # Logic: Simple Sentiment Score
                        title_lower = title.lower()
                        pos = ["buy", "upside", "growth", "profit", "surge", "bullish", "beats"]
                        neg = ["fall", "drop", "risk", "sell", "loss", "bearish", "misses"]
                        
                        for word in pos:
                            if word in title_lower: score += 1
                        for word in neg:
                            if word in title_lower: score -= 1
                
                # The Explainer Logic
                st.write(f"**AI Logic Score:** {score}")
                
                if score >= 1:
                    st.success("🟢 RECOMMEND: BUY (Positive News Bias)")
                elif score <= -1:
                    st.error("🔴 RECOMMEND: SELL (Negative News Bias)")
                else:
                    st.warning("🟡 RECOMMEND: HOLD (Neutral/Mixed Signals)")
                    
            # Tiny pause so Yahoo doesn't block us for being too fast
            time.sleep(0.5) 
            
        except Exception as e:
            st.error(f"Error analyzing {ticker}: {e}")

    status_text.text("✅ Analysis Complete!")
    st.balloons()

st.divider()
st.info("Note: This AI analyzes headlines. It does not see hidden financial data.")
