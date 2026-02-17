import requests
import pandas as pd
from typing import List, Dict, Optional
from langchain.tools import tool
from datetime import datetime
import os
import yfinance as yf
from exa_py import Exa

SYMBOL_TO_YAHOO = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "ADA": "ADA-USD",
    "DOT": "DOT-USD",
    "MATIC": "MATIC-USD",
    "AVAX": "AVAX-USD",
    "LINK": "LINK-USD",
    "UNI": "UNI-USD",
    "XRP": "XRP-USD",
    "DOGE": "DOGE-USD",
    "SHIB": "SHIB-USD",
    "LTC": "LTC-USD",
    "BCH": "BCH-USD",
    "ATOM": "ATOM-USD",
    "XLM": "XLM-USD",
    "ALGO": "ALGO-USD",
    "VET": "VET-USD",
    "ICP": "ICP-USD",
    "FIL": "FIL-USD",
}


def _get_yahoo_symbol(symbol: str) -> str:
    """Convert crypto symbol to Yahoo Finance format"""
    symbol = symbol.upper()
    # If already in Yahoo format (e.g., BTC-USD), return as is
    if "-USD" in symbol:
        return symbol
    return SYMBOL_TO_YAHOO.get(symbol, f"{symbol}-USD")


@tool
def fetch_crypto_news(cryptocurrency: str, num_results: int = 5) -> str:
    """
    Fetch recent news articles about a cryptocurrency using Exa API.

    Args:
        cryptocurrency: Symbol or name of cryptocurrency (e.g., 'BTC', 'Bitcoin')
        num_results: Number of news articles to fetch (default: 5, max: 10)

    Returns:
        Formatted string containing recent news articles with titles and snippets
    """
    exa_api_key = os.getenv("EXA_API_KEY")

    if not exa_api_key:
        return "Error: EXA_API_KEY not found. Please add the key in .env"

    try:
        exa = Exa(exa_api_key)
        result = exa.search(
            f"{cryptocurrency} cryptocurrency news",
            num_results=min(num_results, 10),
            type="auto",
            contents={
                "highlights": {
                    "max_characters": 4000
                }
            }
        )

        if not result.results:
            return f"No recent news found on {cryptocurrency}"
        
        formatted_news = f"Recent news for {cryptocurrency}:\n\n"
        for i, article in enumerate(result.results, 1):
            formatted_news += f"{i}. {article.title}\n"
            # highlights is a list of strings, join them
            if hasattr(article, 'highlights') and article.highlights:
                formatted_news += f"   {' '.join(article.highlights)}\n"
            formatted_news += f"   URL: {article.url}\n\n"

        return formatted_news

    except Exception as e:
        return f"Error fetching news for {cryptocurrency}: {str(e)}"

    

@tool
def fetch_current_price(cryptocurrency: str) -> str:
    """
    Fetch current price and key market metrics for a cryptocurrency using Yahoo Finance.
    No API key required.

    Args:
        cryptocurrency: Symbol or name of cryptocurrency (e.g., 'BTC', 'ETH', 'Bitcoin')

    Returns:
        Formatted string with current price, market cap, volume, and price changes
    """
    yahoo_symbol = _get_yahoo_symbol(cryptocurrency)

    try:
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info

        if not info or "currentPrice" not in info and "regularMarketPrice" not in info:
            return f"Could not retrieve data for {cryptocurrency}. Please check the symbol."

        # Extract metrics - yfinance uses different keys depending on asset type
        current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
        market_cap = info.get("marketCap", 0)
        volume_24h = info.get("volume24Hr") or info.get("volume", 0)
        day_high = info.get("dayHigh") or info.get("regularMarketDayHigh", 0)
        day_low = info.get("dayLow") or info.get("regularMarketDayLow", 0)
        fifty_two_week_high = info.get("fiftyTwoWeekHigh", 0)
        fifty_two_week_low = info.get("fiftyTwoWeekLow", 0)

        # Calculate 24h change
        change_24h = ((current_price - prev_close) / prev_close * 100) if prev_close else 0

        result = f"""Current Market Data for {cryptocurrency} ({yahoo_symbol}):

Price:          ${current_price:,.4f}
24h Change:     {change_24h:+.2f}%
24h High:       ${day_high:,.4f}
24h Low:        ${day_low:,.4f}

Market Cap:     ${market_cap:,.0f}
24h Volume:     ${volume_24h:,.0f}

52-Week High:   ${fifty_two_week_high:,.4f}
52-Week Low:    ${fifty_two_week_low:,.4f}
"""
        return result

    except Exception as e:
        return f"Error fetching current price for {cryptocurrency}: {str(e)}"


@tool
def fetch_historical_prices(cryptocurrency: str, days: int = 30) -> str:
    """
    Fetch historical OHLCV price data and calculate key metrics for a cryptocurrency.
    Uses Yahoo Finance - no API key required.

    Args:
        cryptocurrency: Symbol or name of cryptocurrency (e.g., 'BTC', 'ETH')
        days: Number of days of historical data to fetch (default: 30, max: 365)

    Returns:
        Formatted string with OHLCV stats, trend analysis, and volatility metrics
    """
    yahoo_symbol = _get_yahoo_symbol(cryptocurrency)
    days = min(days, 365)

    # Convert days to yfinance period format
    if days <= 7:
        period = "7d"
    elif days <= 30:
        period = "1mo"
    elif days <= 90:
        period = "3mo"
    elif days <= 180:
        period = "6mo"
    else:
        period = "1y"

    try:
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(period=period)

        if df.empty:
            return f"No historical data found for {cryptocurrency} ({yahoo_symbol})"

        # Core price metrics
        current_price = df["Close"].iloc[-1]
        start_price = df["Close"].iloc[0]
        price_change = ((current_price - start_price) / start_price) * 100

        high_price = df["High"].max()
        low_price = df["Low"].min()
        avg_close = df["Close"].mean()
        avg_volume = df["Volume"].mean()

        # Dates for high/low
        high_date = df["High"].idxmax().strftime("%Y-%m-%d")
        low_date = df["Low"].idxmin().strftime("%Y-%m-%d")

        # Volatility - annualized standard deviation of daily returns
        daily_returns = df["Close"].pct_change().dropna()
        volatility = daily_returns.std() * 100

        # 7-day momentum
        if len(df) >= 14:
            recent_avg = df["Close"].iloc[-7:].mean()
            previous_avg = df["Close"].iloc[-14:-7].mean()
            momentum = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            momentum = 0

        # Simple moving averages
        sma_7 = df["Close"].tail(7).mean() if len(df) >= 7 else current_price
        sma_30 = df["Close"].tail(30).mean() if len(df) >= 30 else current_price

        # Determine trend
        if price_change > 10:
            trend = "Strong Uptrend 📈"
        elif price_change > 3:
            trend = "Uptrend 📈"
        elif price_change < -10:
            trend = "Strong Downtrend 📉"
        elif price_change < -3:
            trend = "Downtrend 📉"
        else:
            trend = "Sideways / Consolidation ↔️"

        result = f"""Historical Price Analysis for {cryptocurrency} ({days} days):

Price Summary:
- Current Close:    ${current_price:,.4f}
- Period Start:     ${start_price:,.4f} ({df.index[0].strftime('%Y-%m-%d')})
- Period Change:    {price_change:+.2f}%
- Trend:            {trend}

OHLCV Range:
- Period High:      ${high_price:,.4f} (on {high_date})
- Period Low:       ${low_price:,.4f} (on {low_date})
- Average Close:    ${avg_close:,.4f}
- Average Volume:   ${avg_volume:,.0f}

Moving Averages:
- 7-day SMA:        ${sma_7:,.4f}
- 30-day SMA:       ${sma_30:,.4f}

Momentum & Volatility:
- 7-day Momentum:   {momentum:+.2f}%
- Daily Volatility: {volatility:.2f}%
"""
        return result

    except Exception as e:
        return f"Error fetching historical prices for {cryptocurrency}: {str(e)}"


# ============================================================================
# TOOL COLLECTION
# ============================================================================

def get_all_tools():
    """Returns all available cryptocurrency analysis tools for the agent"""
    return [
        fetch_crypto_news,
        fetch_current_price,
        fetch_historical_prices,
    ]