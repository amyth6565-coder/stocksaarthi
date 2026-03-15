import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def _try_yfinance(symbol: str, exchange: str):
    suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
    return yf.Ticker(f"{symbol.upper()}{suffix}")

def fetch_price_history(symbol: str, period: str = "6mo", exchange: str = "NSE") -> pd.DataFrame:
    # Try yfinance
    try:
        ticker = _try_yfinance(symbol, exchange)
        hist = ticker.history(period=period)
        if not hist.empty:
            return hist
    except Exception as e:
        logger.warning(f"yfinance failed for {symbol}: {e}")

    # Fallback: NSE library
    try:
        from nse import NSE
        nse = NSE(download_folder=Path("/tmp"))
        data = nse.equityHistory(
            symbol=symbol.upper(),
            series="EQ",
            start=pd.Timestamp.now() - pd.Timedelta(days=180),
            end=pd.Timestamp.now()
        )
        nse.exit()
        if data is not None and not data.empty:
            data.index = pd.to_datetime(data.index)
            # Normalize column names
            col_map = {
                "CH_OPENING_PRICE": "Open",
                "CH_TRADE_HIGH_PRICE": "High",
                "CH_TRADE_LOW_PRICE": "Low",
                "CH_CLOSING_PRICE": "Close",
                "CH_TOT_TRADED_QTY": "Volume",
                "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "volume": "Volume",
            }
            data = data.rename(columns=col_map)
            return data.sort_index()
    except Exception as e:
        logger.warning(f"NSE library failed for {symbol}: {e}")

    return pd.DataFrame()

def fetch_fundamentals(symbol: str, exchange: str = "NSE") -> dict:
    # Try yfinance
    try:
        info = _try_yfinance(symbol, exchange).info
        if info.get("regularMarketPrice") or info.get("currentPrice"):
            return _parse_yf_info(info, symbol)
    except Exception as e:
        logger.warning(f"yfinance fundamentals failed for {symbol}: {e}")

    # Fallback: NSE library quote
    try:
        from nse import NSE
        nse = NSE(download_folder=Path("/tmp"))
        quote = nse.equityMetaInfo(symbol=symbol.upper())
        price_data = nse.equity(symbol=symbol.upper(), section="trade_info")
        nse.exit()

        current = None
        prev = None
        if price_data:
            market = price_data.get("marketDeptOrderBook", {})
            trade = price_data.get("tradeInfo", {})
            current = market.get("tradeInfo", {}).get("lastPrice") or trade.get("totalTradedVolume")

        return {
            "company_name": quote.get("companyName", symbol) if quote else symbol,
            "sector": quote.get("industry", "N/A") if quote else "N/A",
            "industry": quote.get("industry", "N/A") if quote else "N/A",
            "market_cap": None,
            "current_price": current,
            "prev_close": prev,
            "day_change_pct": None,
            "week_52_high": None,
            "week_52_low": None,
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
        logger.error(f"NSE fundamentals failed for {symbol}: {e}")
        return {"error": str(e), "company_name": symbol}

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
