import yfinance as yf
import pandas as pd
from typing import Optional

def get_ticker(symbol: str, exchange: str = "NSE") -> yf.Ticker:
    suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
    return yf.Ticker(f"{symbol.upper()}{suffix}")

def fetch_price_history(symbol: str, period: str = "6mo", exchange: str = "NSE") -> pd.DataFrame:
    try:
        ticker = get_ticker(symbol, exchange)
        hist = ticker.history(period=period)
        if hist.empty:
            ticker = get_ticker(symbol, "BSE")
            hist = ticker.history(period=period)
        return hist
    except Exception:
        return pd.DataFrame()

def fetch_fundamentals(symbol: str, exchange: str = "NSE") -> dict:
    try:
        info = get_ticker(symbol, exchange).info
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
    except Exception as e:
        return {"error": str(e)}

def fetch_financial_statements(symbol: str, exchange: str = "NSE") -> dict:
    try:
        ticker = get_ticker(symbol, exchange)
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
