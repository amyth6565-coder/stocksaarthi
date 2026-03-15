from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
import json
from groq import Groq
from services.data_service import fetch_price_history, fetch_fundamentals
from services.technical import calculate_indicators
from services.fundamental import score_fundamentals
from services.ai_service import get_ai_verdict

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    history: Optional[list] = []

SYSTEM_PROMPT = """You are StockSaarthi AI — an expert Indian stock market advisor.

CRITICAL RULES — NEVER BREAK THESE:
1. NEVER write code, function calls, or markdown code blocks like ```python
2. NEVER show tool names or function syntax to the user ever
3. When user asks about a stock, silently call the tool and present ONLY the results in plain text
4. Always respond in plain conversational text with ** for bold headers
5. Use ₹ for prices, % for percentages
6. End every stock analysis with: ⚠️ Educational purposes only. Not financial advice.

FORMAT your stock analysis like this:
**Company (SYMBOL)**
Price: ₹X | Change: X%

**Verdict: BUY/HOLD/AVOID** (X% confidence)
2-3 sentence reasoning here.

**Technical Score: X/10**
- RSI: value — signal
- MACD: signal
- EMA Trend: signal

**Fundamental Score: X/10**
- PE: value | ROE: value
- Revenue Growth: value
- Debt/Equity: value

**Entry Strategy:** advice here

**Key Risks:**
- risk 1
- risk 2

⚠️ Educational purposes only. Not financial advice."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyse_stock",
            "description": "Full technical + fundamental analysis of an Indian stock with BUY/HOLD/AVOID verdict",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "NSE stock symbol e.g. RELIANCE, TCS, INFY"},
                    "exchange": {"type": "string", "description": "Exchange NSE or BSE", "default": "NSE"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_technicals",
            "description": "Get technical indicators RSI MACD EMA Bollinger Bands for a stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "exchange": {"type": "string", "default": "NSE"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fundamentals",
            "description": "Get fundamental data PE ratio ROE debt equity revenue growth for a stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "exchange": {"type": "string", "default": "NSE"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": "Compare multiple Indian stocks side by side",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "exchange": {"type": "string", "default": "NSE"}
                },
                "required": ["symbols"]
            }
        }
    }
]

def call_tool(name: str, args: dict) -> str:
    try:
        if name == "analyse_stock":
            symbol = args["symbol"].upper()
            exchange = args.get("exchange", "NSE")
            hist = fetch_price_history(symbol, period="1y", exchange=exchange)
            if hist.empty:
                return json.dumps({"error": f"No data found for {symbol}"})
            fund_raw = fetch_fundamentals(symbol, exchange)
            tech = calculate_indicators(hist)
            fund_score = score_fundamentals(fund_raw)
            ai = get_ai_verdict(symbol, fund_raw, tech, fund_score)
            return json.dumps({
                "symbol": symbol,
                "company": fund_raw.get("company_name", symbol),
                "sector": fund_raw.get("sector", "N/A"),
                "price": tech.get("close"),
                "day_change_pct": fund_raw.get("day_change_pct"),
                "technical_score": tech.get("technical_score"),
                "technical_summary": tech.get("technical_summary"),
                "rsi": tech.get("rsi", {}).get("value"),
                "rsi_signal": tech.get("rsi", {}).get("signal"),
                "macd_signal": tech.get("macd", {}).get("signal"),
                "ema_signal": tech.get("ema", {}).get("signal"),
                "fundamental_score": fund_score.get("fundamental_score"),
                "fundamental_summary": fund_score.get("fundamental_summary"),
                "pe_ratio": fund_raw.get("pe_ratio"),
                "roe": fund_raw.get("roe"),
                "revenue_growth": fund_raw.get("revenue_growth"),
                "debt_to_equity": fund_raw.get("debt_to_equity"),
                "profit_margin": fund_raw.get("profit_margin"),
                "verdict": ai.get("verdict"),
                "confidence": ai.get("confidence"),
                "reasoning": ai.get("reasoning"),
                "key_positives": ai.get("key_positives"),
                "key_risks": ai.get("key_risks"),
                "entry_strategy": ai.get("entry_strategy"),
                "time_horizon": ai.get("time_horizon"),
            })

        elif name == "get_technicals":
            symbol = args["symbol"].upper()
            hist = fetch_price_history(symbol, period="6mo", exchange=args.get("exchange", "NSE"))
            if hist.empty:
                return json.dumps({"error": f"No data for {symbol}"})
            tech = calculate_indicators(hist)
            return json.dumps({
                "symbol": symbol,
                "price": tech.get("close"),
                "rsi_value": tech.get("rsi", {}).get("value"),
                "rsi_signal": tech.get("rsi", {}).get("signal"),
                "macd_signal": tech.get("macd", {}).get("signal"),
                "macd_value": tech.get("macd", {}).get("value"),
                "ema_signal": tech.get("ema", {}).get("signal"),
                "above_ema200": tech.get("ema", {}).get("above_ema200"),
                "bollinger_signal": tech.get("bollinger", {}).get("signal"),
                "volume_signal": tech.get("volume", {}).get("signal"),
                "technical_score": tech.get("technical_score"),
                "technical_summary": tech.get("technical_summary"),
            })

        elif name == "get_fundamentals":
            symbol = args["symbol"].upper()
            fund_raw = fetch_fundamentals(symbol, args.get("exchange", "NSE"))
            fund_score = score_fundamentals(fund_raw)
            return json.dumps({
                "symbol": symbol,
                "company": fund_raw.get("company_name", symbol),
                "pe_ratio": fund_raw.get("pe_ratio"),
                "pb_ratio": fund_raw.get("pb_ratio"),
                "roe": fund_raw.get("roe"),
                "profit_margin": fund_raw.get("profit_margin"),
                "revenue_growth": fund_raw.get("revenue_growth"),
                "debt_to_equity": fund_raw.get("debt_to_equity"),
                "current_ratio": fund_raw.get("current_ratio"),
                "dividend_yield": fund_raw.get("dividend_yield"),
                "fundamental_score": fund_score.get("fundamental_score"),
                "fundamental_summary": fund_score.get("fundamental_summary"),
            })

        elif name == "compare_stocks":
            symbols = [s.upper() for s in args["symbols"][:4]]
            results = []
            for sym in symbols:
                hist = fetch_price_history(sym, period="6mo", exchange=args.get("exchange", "NSE"))
                fund_raw = fetch_fundamentals(sym, args.get("exchange", "NSE"))
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
            return json.dumps({"comparison": results})

    except Exception as e:
        return json.dumps({"error": str(e)})


@router.post("/chat")
async def chat(req: ChatMessage):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return {
            "reply": "⚠️ Please add your GROQ_API_KEY to the .env file to enable the AI chatbot. Get a free key at console.groq.com",
            "tool_used": None
        }

    client = Groq(api_key=api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in (req.history or []):
        messages.append(h)
    messages.append({"role": "user", "content": req.message})

    tool_used = None

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1200,
            temperature=0.2,
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_used = tool_name

            tool_result = call_tool(tool_name, tool_args)

            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": tool_call.function.arguments
                    }
                }]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

            final = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1200,
                temperature=0.2,
            )
            reply = final.choices[0].message.content

        else:
            reply = msg.content

        return {"reply": reply, "tool_used": tool_used}

    except Exception as e:
        return {"reply": f"Sorry, something went wrong: {str(e)}", "tool_used": None}
