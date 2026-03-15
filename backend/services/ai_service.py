import os
import json
from groq import Groq

def get_ai_verdict(symbol: str, fundamentals: dict, technicals: dict, fund_score: dict) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return _fallback_verdict(technicals, fund_score)
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior Indian stock market analyst. Respond ONLY with valid JSON, no markdown, no preamble."
                },
                {"role": "user", "content": _build_prompt(symbol, fundamentals, technicals, fund_score)},
            ],
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        return json.loads(raw.strip())
    except Exception:
        return _fallback_verdict(technicals, fund_score)

def _build_prompt(symbol, fund, tech, fund_score):
    m = fund_score.get("metrics", {})
    return f"""Analyse {symbol.upper()} (Sector: {fund.get('sector','N/A')}) and return ONLY this JSON:

TECHNICAL: Price ₹{tech.get('close','N/A')} | RSI {tech.get('rsi',{}).get('value','N/A')} ({tech.get('rsi',{}).get('signal','N/A')}) | MACD {tech.get('macd',{}).get('signal','N/A')} | EMA Trend: {tech.get('ema',{}).get('signal','N/A')} | Tech Score: {tech.get('technical_score','N/A')}/10

FUNDAMENTAL: PE {m.get('pe_ratio',{}).get('value','N/A')} | ROE {m.get('roe',{}).get('value','N/A')} | D/E {m.get('debt_to_equity',{}).get('value','N/A')} | Rev Growth {m.get('revenue_growth',{}).get('value','N/A')} | Fund Score: {fund_score.get('fundamental_score','N/A')}/10

Return exactly:
{{"verdict":"BUY or HOLD or AVOID","confidence":75,"reasoning":"2-3 sentences combining technical and fundamental analysis","key_positives":["point1","point2","point3"],"key_risks":["risk1","risk2"],"time_horizon":"Short-term (days-weeks) or Medium-term (1-3 months) or Long-term (6-12 months)","entry_strategy":"brief entry advice"}}"""

def _fallback_verdict(tech, fund_score):
    tech_score = tech.get("technical_score", 5) if isinstance(tech, dict) else 5
    fund = fund_score.get("fundamental_score", 5) if isinstance(fund_score, dict) else 5
    combined = (tech_score * 0.5) + (fund * 0.5)
    if combined >= 7: verdict, confidence = "BUY", 72
    elif combined >= 5: verdict, confidence = "HOLD", 58
    else: verdict, confidence = "AVOID", 65
    return {
        "verdict": verdict,
        "confidence": confidence,
        "reasoning": f"Rule-based analysis: Technical score {tech_score}/10, Fundamental score {fund}/10. Add GROQ_API_KEY to .env for AI-powered analysis.",
        "key_positives": [tech.get("technical_summary", "See technical panel") if isinstance(tech, dict) else "See technical panel"],
        "key_risks": ["Add GROQ_API_KEY in backend/.env for detailed AI analysis"],
        "time_horizon": "Medium-term (1-3 months)",
        "entry_strategy": "Review technical and fundamental data carefully before investing.",
    }
