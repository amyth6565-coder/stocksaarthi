from mcp.server.fastmcp import FastMCP
from services.data_service import fetch_price_history, fetch_fundamentals, fetch_financial_statements
from services.technical import calculate_indicators
from services.fundamental import score_fundamentals
from services.ai_service import get_ai_verdict

mcp = FastMCP("StockSaarthi")

@mcp.tool()
def analyse_stock(symbol: str, exchange: str = "NSE") -> dict:
    """Analyse an Indian stock technically and fundamentally. Returns BUY/HOLD/AVOID verdict."""
    symbol = symbol.upper().strip()
    hist = fetch_price_history(symbol, period="1y", exchange=exchange)
    if hist.empty:
        return {"error": f"No data found for {symbol}"}
    fund_raw = fetch_fundamentals(symbol, exchange)
    technicals = calculate_indicators(hist)
    fund_score = score_fundamentals(fund_raw)
    ai = get_ai_verdict(symbol, fund_raw, technicals, fund_score)
    return {
        "symbol": symbol,
        "company": fund_raw.get("company_name", symbol),
        "sector": fund_raw.get("sector", "N/A"),
        "price": technicals.get("close"),
        "day_change_pct": fund_raw.get("day_change_pct"),
        "technical_score": technicals.get("technical_score"),
        "technical_summary": technicals.get("technical_summary"),
        "fundamental_score": fund_score.get("fundamental_score"),
        "fundamental_summary": fund_score.get("fundamental_summary"),
        "verdict": ai.get("verdict"),
        "confidence": ai.get("confidence"),
        "reasoning": ai.get("reasoning"),
        "key_positives": ai.get("key_positives"),
        "key_risks": ai.get("key_risks"),
        "entry_strategy": ai.get("entry_strategy"),
        "time_horizon": ai.get("time_horizon"),
    }

@mcp.tool()
def get_technicals(symbol: str, exchange: str = "NSE") -> dict:
    """Get technical indicators for a stock — RSI, MACD, EMA, Bollinger Bands."""
    symbol = symbol.upper().strip()
    hist = fetch_price_history(symbol, period="6mo", exchange=exchange)
    if hist.empty:
        return {"error": f"No data found for {symbol}"}
    tech = calculate_indicators(hist)
    return {
        "symbol": symbol,
        "price": tech.get("close"),
        "rsi": tech.get("rsi"),
        "macd": tech.get("macd"),
        "ema": tech.get("ema"),
        "bollinger": tech.get("bollinger"),
        "volume": tech.get("volume"),
        "technical_score": tech.get("technical_score"),
        "technical_summary": tech.get("technical_summary"),
    }

@mcp.tool()
def get_fundamentals(symbol: str, exchange: str = "NSE") -> dict:
    """Get fundamental data for a stock — PE, ROE, debt, growth, margins."""
    symbol = symbol.upper().strip()
    fund_raw = fetch_fundamentals(symbol, exchange)
    fund_score = score_fundamentals(fund_raw)
    return {
        "symbol": symbol,
        "company": fund_raw.get("company_name", symbol),
        "sector": fund_raw.get("sector", "N/A"),
        "pe_ratio": fund_raw.get("pe_ratio"),
        "pb_ratio": fund_raw.get("pb_ratio"),
        "roe": fund_raw.get("roe"),
        "profit_margin": fund_raw.get("profit_margin"),
        "revenue_growth": fund_raw.get("revenue_growth"),
        "debt_to_equity": fund_raw.get("debt_to_equity"),
        "fundamental_score": fund_score.get("fundamental_score"),
        "fundamental_summary": fund_score.get("fundamental_summary"),
        "metrics": fund_score.get("metrics"),
    }

@mcp.tool()
def compare_stocks(symbols: list[str], exchange: str = "NSE") -> dict:
    """Compare multiple Indian stocks side by side. Pass up to 4 symbols."""
    results = []
    for sym in symbols[:4]:
        sym = sym.upper().strip()
        try:
            hist = fetch_price_history(sym, period="6mo", exchange=exchange)
            fund_raw = fetch_fundamentals(sym, exchange)
            tech = calculate_indicators(hist) if not hist.empty else {}
            fund_score = score_fundamentals(fund_raw)
            ai = get_ai_verdict(sym, fund_raw, tech, fund_score)
            results.append({
                "symbol": sym,
                "name": fund_raw.get("company_name", sym),
                "price": tech.get("close"),
                "verdict": ai.get("verdict"),
                "confidence": ai.get("confidence"),
                "technical_score": tech.get("technical_score"),
                "fundamental_score": fund_score.get("fundamental_score"),
                "pe_ratio": fund_raw.get("pe_ratio"),
                "roe": fund_raw.get("roe"),
                "revenue_growth": fund_raw.get("revenue_growth"),
                "debt_to_equity": fund_raw.get("debt_to_equity"),
            })
        except Exception as e:
            results.append({"symbol": sym, "error": str(e)})
    return {"comparison": results}

if __name__ == "__main__":
    mcp.run(transport="stdio")
