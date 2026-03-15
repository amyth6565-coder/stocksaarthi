from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from services.data_service import fetch_price_history, fetch_fundamentals, fetch_financial_statements
from services.technical import calculate_indicators
from services.fundamental import score_fundamentals
from services.ai_service import get_ai_verdict
import yfinance as yf

router = APIRouter()

class CompareRequest(BaseModel):
    symbols: list[str]
    exchange: str = "NSE"

@router.get("/analyse/{symbol}")
def analyse_stock(symbol: str, exchange: str = Query("NSE")):
    symbol = symbol.upper().strip()
    hist = fetch_price_history(symbol, period="1y", exchange=exchange)
    if hist.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}. Check the symbol.")
    fund_raw = fetch_fundamentals(symbol, exchange)
    financials = fetch_financial_statements(symbol, exchange)
    technicals = calculate_indicators(hist)
    fund_score = score_fundamentals(fund_raw)
    ai = get_ai_verdict(symbol, fund_raw, technicals, fund_score)
    return {
        "symbol": symbol,
        "exchange": exchange,
        "company": {
            "name": fund_raw.get("company_name", symbol),
            "sector": fund_raw.get("sector", "N/A"),
            "industry": fund_raw.get("industry", "N/A"),
            "market_cap": fund_raw.get("market_cap"),
        },
        "price": {
            "current": technicals.get("currentPrice"),
            "prev_close": fund_raw.get("prev_close"),
            "day_change_pct": fund_raw.get("day_change_pct"),
            "week_52_high": fund_raw.get("week_52_high"),
            "week_52_low": fund_raw.get("week_52_low"),
        },
        "technicals": technicals,
        "fundamentals": {**fund_raw, **financials},
        "fundamental_score": fund_score,
        "ai_verdict": ai,
    }

@router.get("/search")
def search_stocks(q: str = Query(..., min_length=1)):
    # Large NSE stock list covering Nifty 500
    all_stocks = [
        {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy"},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking"},
        {"symbol": "INFY", "name": "Infosys", "sector": "IT"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Banking"},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "FMCG"},
        {"symbol": "WIPRO", "name": "Wipro", "sector": "IT"},
        {"symbol": "TATASTEEL", "name": "Tata Steel", "sector": "Metals"},
        {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "NBFC"},
        {"symbol": "AXISBANK", "name": "Axis Bank", "sector": "Banking"},
        {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Auto"},
        {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Pharma"},
        {"symbol": "ONGC", "name": "ONGC", "sector": "Oil & Gas"},
        {"symbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Auto"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom"},
        {"symbol": "NTPC", "name": "NTPC", "sector": "Power"},
        {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG"},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Banking"},
        {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Infrastructure"},
        {"symbol": "TITAN", "name": "Titan Company", "sector": "Consumer"},
        {"symbol": "NESTLEIND", "name": "Nestle India", "sector": "FMCG"},
        {"symbol": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Cement"},
        {"symbol": "ADANIPORTS", "name": "Adani Ports", "sector": "Infrastructure"},
        {"symbol": "SBILIFE", "name": "SBI Life Insurance", "sector": "Insurance"},
        {"symbol": "POWERGRID", "name": "Power Grid Corp", "sector": "Power"},
        {"symbol": "SBI", "name": "State Bank of India", "sector": "Banking"},
        {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "NBFC"},
        {"symbol": "HCLTECH", "name": "HCL Technologies", "sector": "IT"},
        {"symbol": "TECHM", "name": "Tech Mahindra", "sector": "IT"},
        {"symbol": "DRREDDY", "name": "Dr Reddy's Laboratories", "sector": "Pharma"},
        {"symbol": "CIPLA", "name": "Cipla", "sector": "Pharma"},
        {"symbol": "DIVISLAB", "name": "Divi's Laboratories", "sector": "Pharma"},
        {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals", "sector": "Healthcare"},
        {"symbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Consumer"},
        {"symbol": "DMART", "name": "Avenue Supermarts (DMart)", "sector": "Retail"},
        {"symbol": "PIDILITIND", "name": "Pidilite Industries", "sector": "Chemicals"},
        {"symbol": "BERGEPAINT", "name": "Berger Paints", "sector": "Consumer"},
        {"symbol": "HAVELLS", "name": "Havells India", "sector": "Electricals"},
        {"symbol": "VOLTAS", "name": "Voltas", "sector": "Electricals"},
        {"symbol": "BRITANNIA", "name": "Britannia Industries", "sector": "FMCG"},
        {"symbol": "DABUR", "name": "Dabur India", "sector": "FMCG"},
        {"symbol": "MARICO", "name": "Marico", "sector": "FMCG"},
        {"symbol": "COLPAL", "name": "Colgate-Palmolive India", "sector": "FMCG"},
        {"symbol": "GODREJCP", "name": "Godrej Consumer Products", "sector": "FMCG"},
        {"symbol": "TATACONSUM", "name": "Tata Consumer Products", "sector": "FMCG"},
        {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance", "sector": "NBFC"},
        {"symbol": "CHOLAFIN", "name": "Cholamandalam Finance", "sector": "NBFC"},
        {"symbol": "LICHSGFIN", "name": "LIC Housing Finance", "sector": "NBFC"},
        {"symbol": "PNBHOUSING", "name": "PNB Housing Finance", "sector": "NBFC"},
        {"symbol": "PNB", "name": "Punjab National Bank", "sector": "Banking"},
        {"symbol": "BANKBARODA", "name": "Bank of Baroda", "sector": "Banking"},
        {"symbol": "CANBK", "name": "Canara Bank", "sector": "Banking"},
        {"symbol": "UNIONBANK", "name": "Union Bank of India", "sector": "Banking"},
        {"symbol": "FEDERALBNK", "name": "Federal Bank", "sector": "Banking"},
        {"symbol": "IDFCFIRSTB", "name": "IDFC First Bank", "sector": "Banking"},
        {"symbol": "BANDHANBNK", "name": "Bandhan Bank", "sector": "Banking"},
        {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Banking"},
        {"symbol": "RBLBANK", "name": "RBL Bank", "sector": "Banking"},
        {"symbol": "YESBANK", "name": "Yes Bank", "sector": "Banking"},
        {"symbol": "TATAPOWER", "name": "Tata Power", "sector": "Power"},
        {"symbol": "ADANIGREEN", "name": "Adani Green Energy", "sector": "Power"},
        {"symbol": "ADANIENT", "name": "Adani Enterprises", "sector": "Conglomerate"},
        {"symbol": "ADANITRANS", "name": "Adani Transmission", "sector": "Power"},
        {"symbol": "JINDALSTEL", "name": "Jindal Steel & Power", "sector": "Metals"},
        {"symbol": "SAIL", "name": "Steel Authority of India", "sector": "Metals"},
        {"symbol": "HINDALCO", "name": "Hindalco Industries", "sector": "Metals"},
        {"symbol": "VEDL", "name": "Vedanta", "sector": "Metals"},
        {"symbol": "COALINDIA", "name": "Coal India", "sector": "Mining"},
        {"symbol": "NMDC", "name": "NMDC", "sector": "Mining"},
        {"symbol": "GRASIM", "name": "Grasim Industries", "sector": "Cement"},
        {"symbol": "AMBUJACEM", "name": "Ambuja Cements", "sector": "Cement"},
        {"symbol": "ACC", "name": "ACC Limited", "sector": "Cement"},
        {"symbol": "SHREECEM", "name": "Shree Cement", "sector": "Cement"},
        {"symbol": "RAMCOCEM", "name": "Ramco Cements", "sector": "Cement"},
        {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp", "sector": "Auto"},
        {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto", "sector": "Auto"},
        {"symbol": "EICHERMOT", "name": "Eicher Motors", "sector": "Auto"},
        {"symbol": "ASHOKLEY", "name": "Ashok Leyland", "sector": "Auto"},
        {"symbol": "MOTHERSON", "name": "Motherson Sumi", "sector": "Auto Ancillary"},
        {"symbol": "BOSCHLTD", "name": "Bosch", "sector": "Auto Ancillary"},
        {"symbol": "MRF", "name": "MRF", "sector": "Auto Ancillary"},
        {"symbol": "APOLLOTYRE", "name": "Apollo Tyres", "sector": "Auto Ancillary"},
        {"symbol": "EXIDEIND", "name": "Exide Industries", "sector": "Auto Ancillary"},
        {"symbol": "ZOMATO", "name": "Zomato", "sector": "Internet"},
        {"symbol": "NYKAA", "name": "Nykaa (FSN E-Commerce)", "sector": "Internet"},
        {"symbol": "PAYTM", "name": "Paytm (One97 Communications)", "sector": "Fintech"},
        {"symbol": "POLICYBZR", "name": "PB Fintech (Policybazaar)", "sector": "Fintech"},
        {"symbol": "IRCTC", "name": "IRCTC", "sector": "Travel"},
        {"symbol": "INDIGO", "name": "IndiGo (InterGlobe Aviation)", "sector": "Aviation"},
        {"symbol": "SPICEJET", "name": "SpiceJet", "sector": "Aviation"},
        {"symbol": "DELHIVERY", "name": "Delhivery", "sector": "Logistics"},
        {"symbol": "TIINDIA", "name": "Tube Investments of India", "sector": "Engineering"},
        {"symbol": "SIEMENS", "name": "Siemens India", "sector": "Engineering"},
        {"symbol": "ABB", "name": "ABB India", "sector": "Engineering"},
        {"symbol": "BEL", "name": "Bharat Electronics", "sector": "Defence"},
        {"symbol": "HAL", "name": "Hindustan Aeronautics", "sector": "Defence"},
        {"symbol": "COCHINSHIP", "name": "Cochin Shipyard", "sector": "Defence"},
        {"symbol": "MAZAGON", "name": "Mazagon Dock", "sector": "Defence"},
        {"symbol": "PERSISTENT", "name": "Persistent Systems", "sector": "IT"},
        {"symbol": "MPHASIS", "name": "Mphasis", "sector": "IT"},
        {"symbol": "LTIM", "name": "LTIMindtree", "sector": "IT"},
        {"symbol": "COFORGE", "name": "Coforge", "sector": "IT"},
        {"symbol": "OFSS", "name": "Oracle Financial Services", "sector": "IT"},
        {"symbol": "KPITTECH", "name": "KPIT Technologies", "sector": "IT"},
        {"symbol": "TATAELXSI", "name": "Tata Elxsi", "sector": "IT"},
        {"symbol": "ZYDUSLIFE", "name": "Zydus Lifesciences", "sector": "Pharma"},
        {"symbol": "TORNTPHARM", "name": "Torrent Pharmaceuticals", "sector": "Pharma"},
        {"symbol": "ALKEM", "name": "Alkem Laboratories", "sector": "Pharma"},
        {"symbol": "AUROPHARMA", "name": "Aurobindo Pharma", "sector": "Pharma"},
        {"symbol": "LUPIN", "name": "Lupin", "sector": "Pharma"},
        {"symbol": "BIOCON", "name": "Biocon", "sector": "Pharma"},
        {"symbol": "GLENMARK", "name": "Glenmark Pharmaceuticals", "sector": "Pharma"},
        {"symbol": "IPCALAB", "name": "IPCA Laboratories", "sector": "Pharma"},
        {"symbol": "PAGEIND", "name": "Page Industries (Jockey)", "sector": "Consumer"},
        {"symbol": "TRENT", "name": "Trent (Zara/Westside)", "sector": "Retail"},
        {"symbol": "ABFRL", "name": "Aditya Birla Fashion", "sector": "Retail"},
        {"symbol": "MANYAVAR", "name": "Vedant Fashions (Manyavar)", "sector": "Retail"},
        {"symbol": "CAMPUS", "name": "Campus Activewear", "sector": "Consumer"},
        {"symbol": "LICI", "name": "LIC of India", "sector": "Insurance"},
        {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance", "sector": "Insurance"},
        {"symbol": "ICICIPRULI", "name": "ICICI Prudential Life", "sector": "Insurance"},
        {"symbol": "ICICIGI", "name": "ICICI Lombard GIC", "sector": "Insurance"},
        {"symbol": "SBICARD", "name": "SBI Cards", "sector": "Fintech"},
        {"symbol": "NAUKRI", "name": "Info Edge (Naukri)", "sector": "Internet"},
        {"symbol": "INDIAMART", "name": "IndiaMART InterMESH", "sector": "Internet"},
        {"symbol": "JUSTDIAL", "name": "Just Dial", "sector": "Internet"},
        {"symbol": "DIXON", "name": "Dixon Technologies", "sector": "Electronics"},
        {"symbol": "AMBER", "name": "Amber Enterprises", "sector": "Electronics"},
        {"symbol": "KAYNES", "name": "Kaynes Technology", "sector": "Electronics"},
        {"symbol": "SOLARINDS", "name": "Solar Industries", "sector": "Defence"},
        {"symbol": "APARINDS", "name": "Apar Industries", "sector": "Cables"},
        {"symbol": "POLYCAB", "name": "Polycab India", "sector": "Cables"},
        {"symbol": "KFINTECH", "name": "KFin Technologies", "sector": "Fintech"},
        {"symbol": "CAMS", "name": "CAMS", "sector": "Fintech"},
        {"symbol": "BSE", "name": "BSE Limited", "sector": "Exchange"},
        {"symbol": "MCX", "name": "Multi Commodity Exchange", "sector": "Exchange"},
        {"symbol": "CDSL", "name": "CDSL", "sector": "Exchange"},
    ]

    # Filter by query
    q = q.upper()
    results = [s for s in all_stocks if q in s["symbol"] or q in s["name"].upper()]

    # If nothing found in list, try yfinance directly as fallback
    if not results:
        try:
            ticker = yf.Ticker(f"{q}.NS")
            info = ticker.info
            name = info.get("longName") or info.get("shortName")
            if name:
                results = [{"symbol": q, "name": name, "sector": info.get("sector", "N/A")}]
        except Exception:
            pass

    return {"results": results[:8]}

@router.post("/compare")
def compare_stocks(request: CompareRequest):
    if len(request.symbols) > 4:
        raise HTTPException(status_code=400, detail="Max 4 stocks")
    results = []
    for sym in request.symbols:
        sym = sym.upper().strip()
        try:
            hist = fetch_price_history(sym, period="6mo", exchange=request.exchange)
            fund_raw = fetch_fundamentals(sym, request.exchange)
            technicals = calculate_indicators(hist) if not hist.empty else {}
            fund_score = score_fundamentals(fund_raw)
            ai = get_ai_verdict(sym, fund_raw, technicals, fund_score)
            results.append({
                "symbol": sym,
                "name": fund_raw.get("company_name", sym),
                "sector": fund_raw.get("sector", "N/A"),
                "price": technicals.get("currentPrice"),
                "day_change_pct": fund_raw.get("day_change_pct"),
                "technical_score": technicals.get("technical_score"),
                "fundamental_score": fund_score.get("fundamental_score"),
                "verdict": ai.get("verdict"),
                "confidence": ai.get("confidence"),
                "pe_ratio": fund_raw.get("pe_ratio"),
                "roe": fund_raw.get("roe"),
                "revenue_growth": fund_raw.get("revenue_growth"),
                "debt_to_equity": fund_raw.get("debt_to_equity"),
            })
        except Exception as e:
            results.append({"symbol": sym, "error": str(e)})
    return {"comparison": results}
