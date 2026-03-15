import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

def _try_yfinance(symbol: str, exchange: str):
    suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
    return yf.Ticker(f"{symbol.upper()}{suffix}")

def fetch_price_history(symbol: str, period: str = "6mo", exchange: str = "NSE") -> pd.DataFrame:
    try:
        ticker = _try_yfinance(symbol, exchange)
        hist = ticker.history(period=period)
        if not hist.empty:
            return hist
    except Exception as e:
        logger.warning(f"yfinance failed for {symbol}: {e}")

    try:
        from nse import NSE
        nse = NSE(download_folder=Path("/tmp"))
        to_date = date.today()
        from_date = to_date - timedelta(days=180)
        data = nse.fetch_equity_historical_data(
            symbol=symbol.upper(),
            from_date=from_date,
            to_date=to_date,
            series="EQ"
        )
        nse.exit()
        if data:
            rows = []
            for d in data:
                rows.append({
                    "Date": pd.to_datetime(d.get("mtimestamp"), dayfirst=True),
                    "Open":   float(d.get("chOpeningPrice") or 0),
                    "High":   float(d.get("chTradeHighPrice") or 0),
                    "Low":    float(d.get("chTradeLowPrice") or 0),
                    "Close":  float(d.get("chClosingPrice") or 0),
                    "Volume": float(d.get("chTotTradedQty") or 0),
                })
            df = pd.DataFrame(rows).set_index("Date").sort_index()
            if not df.empty:
                return df
    except Exception as e:
        logger.warning(f"NSE library price history failed for {symbol}: {e}")

    return pd.DataFrame()

def fetch_fundamentals(symbol: str, exchange: str = "NSE") -> dict:
    try:
        info = _try_yfinance(symbol, exchange).info
        if info.get("regularMarketPrice") or info.get("currentPrice"):
            return _parse_yf_info(info, symbol)
    except Exception as e:
        logger.warning(f"yfinance fundamentals failed for {symbol}: {e}")

    try:
        from nse import NSE
        nse = NSE(download_folder=Path("/tmp"))
        quote = nse.equityQuote(symbol.upper())
        nse.exit()
        if quote:
            current = float(quote.get("lastPrice") or quote.get("chLastTradedPrice") or 0)
            prev = float(quote.get("previousClose") or quote.get("chPreviousClsPrice") or 0)
            change_pct = round(((current - prev) / prev) * 100, 2) if prev else None
            return {
                "company_name": quote.get("companyName") or symbol,
                "sector": quote.get("industry", "N/A"),
                "industry": quote.get("industry", "N/A"),
                "market_cap": quote.get("totalMarketCap"),
                "current_price": current,
                "prev_close": prev,
                "day_change_pct": change_pct,
                "week_52_high": float(quote.get("ch52WeekHighPrice") or 0) or None,
                "week_52_low": float(quote.get("ch52WeekLowPrice") or 0) or None,
                "pe_ratio": quote.get("pe"),
                "forward_pe": None,
                "pb_ratio": quote.get("pb"),
                "roe": None, "roa": None,
                "profit_margin": None, "operating_margin": None,
                "revenue_growth": None, "earnings_growth": None,
                "debt_to_equity": None, "current_ratio": None,
                "dividend_yield": None, "analyst_recommendation": None,
                "target_mean_price": None, "number_of_analysts": None,
            }
    except Exception as e:
        logger.error(f"NSE fundamentals failed for {symbol}: {e}")

    return {"error": f"No data found for {symbol}", "company_name": symbol}

def _parse_yf_info(info: dict, symbol: str) -> dict:
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
        ticker = _try_yfinance(symbol, exchange)
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
