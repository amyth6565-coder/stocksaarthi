import yfinance as yf
import pandas as pd
import requests
import json
from typing import Optional
from datetime import datetime, timedelta

# NSE direct API headers - works on cloud
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

def _nse_session():
    s = requests.Session()
    s.headers.update(NSE_HEADERS)
    # Get cookies first
    try:
        s.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass
    return s

def fetch_price_history(symbol: str, period: str = "6mo", exchange: str = "NSE") -> pd.DataFrame:
    # Try yfinance first
    try:
        suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
        ticker = yf.Ticker(f"{symbol.upper()}{suffix}")
        hist = ticker.history(period=period)
        if not hist.empty:
            return hist
    except Exception:
        pass

    # Fallback: NSE direct API
    try:
        session = _nse_session()
        end = datetime.now()
        start = end - timedelta(days=180)
        url = (
            f"https://www.nseindia.com/api/historical/cm/equity"
            f"?symbol={symbol.upper()}"
            f"&series=[%22EQ%22]"
            f"&from={start.strftime('%d-%m-%Y')}"
            f"&to={end.strftime('%d-%m-%Y')}"
        )
        resp = session.get(url, timeout=15)
        data = resp.json().get("data", [])
        if data:
            rows = []
            for d in data:
                rows.append({
                    "Date": pd.to_datetime(d["CH_TIMESTAMP"]),
                    "Open": float(d.get("CH_OPENING_PRICE", 0)),
                    "High": float(d.get("CH_TRADE_HIGH_PRICE", 0)),
                    "Low": float(d.get("CH_TRADE_LOW_PRICE", 0)),
                    "Close": float(d.get("CH_CLOSING_PRICE", 0)),
                    "Volume": float(d.get("CH_TOT_TRADED_QTY", 0)),
                })
            df = pd.DataFrame(rows).set_index("Date").sort_index()
            return df
    except Exception:
        pass

    return pd.DataFrame()

def fetch_fundamentals(symbol: str, exchange: str = "NSE") -> dict:
    # Try yfinance first
    try:
        suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
        info = yf.Ticker(f"{symbol.upper()}{suffix}").info
        if info.get("regularMarketPrice") or info.get("currentPrice"):
            return _parse_info(info, symbol)
    except Exception:
        pass

    # Fallback: NSE direct quote API
    try:
        session = _nse_session()
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}"
        resp = session.get(url, timeout=15)
        data = resp.json()
        price_info = data.get("priceInfo", {})
        meta = data.get("metadata", {})
        info_obj = data.get("industryInfo", {})
        current = price_info.get("lastPrice", 0)
        prev = price_info.get("previousClose", 0)
        change_pct = round(((current - prev) / prev) * 100, 2) if prev else None
        return {
            "company_name": meta.get("companyName", symbol),
            "sector": info_obj.get("macro", "N/A"),
            "industry": info_obj.get("industry", "N/A"),
            "market_cap": None,
            "current_price": current,
            "prev_close": prev,
            "day_change_pct": change_pct,
            "week_52_high": price_info.get("weekHighLow", {}).get("max"),
            "week_52_low": price_info.get("weekHighLow", {}).get("min"),
            "pe_ratio": None,
            "forward_pe": None,
            "pb_ratio": None,
            "roe": None,
            "roa": None,
            "profit_margin": None,
            "operating_margin": None,
            "revenue_growth": None,
            "earnings_growth": None,
            "debt_to_equity": None,
            "current_ratio": None,
            "dividend_yield": None,
            "analyst_recommendation": None,
            "target_mean_price": None,
            "number_of_analysts": None,
        }
    except Exception as e:
        return {"error": str(e)}

def _parse_info(info: dict, symbol: str) -> dict:
    return {
        "company_name": info.get("longName") or info.get("shortName", symbol),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "prev_close": info.get("previousClose"),
        "day_change_pct": _calc_change(info),
        "week_52_high": info.get("fiftyTwoWeekHigh"),
        "week_52_low": info.get("fiftyTwoWeekLow"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "profit_margin": info.get("profitMargins"),
        "operating_margin": info.get("operatingMargins"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "dividend_yield": info.get("dividendYield"),
        "analyst_recommendation": info.get("recommendationKey"),
        "target_mean_price": info.get("targetMeanPrice"),
        "number_of_analysts": info.get("numberOfAnalystOpinions"),
    }

def fetch_financial_statements(symbol: str, exchange: str = "NSE") -> dict:
    try:
        suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
        ticker = yf.Ticker(f"{symbol.upper()}{suffix}")
        income = ticker.financials
        cashflow = ticker.cashflow
        result = {}
        if not income.empty:
            latest = income.iloc[:, 0]
            result["revenue"] = float(latest.get("Total Revenue", 0) or 0)
            result["net_income"] = float(latest.get("Net Income", 0) or 0)
        if not cashflow.empty:
            latest = cashflow.iloc[:, 0]
            result["free_cash_flow"] = float(latest.get("Free Cash Flow", 0) or 0)
        return result
    except Exception:
        return {}

def _calc_change(info: dict) -> Optional[float]:
    current = info.get("currentPrice") or info.get("regularMarketPrice")
    prev = info.get("previousClose")
    if current and prev and prev != 0:
        return round(((current - prev) / prev) * 100, 2)
    return None
