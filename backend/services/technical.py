import pandas as pd
import pandas_ta as ta
from typing import Optional

def calculate_indicators(hist: pd.DataFrame) -> dict:
    if hist.empty or len(hist) < 20:
        return {"error": "Not enough price history"}
    df = hist.copy()
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.ema(length=200, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.stoch(k=14, d=3, append=True)

    rsi = _last(df, "RSI_14")
    macd = _last(df, "MACD_12_26_9")
    macd_signal = _last(df, "MACDs_12_26_9")
    macd_hist = _last(df, "MACDh_12_26_9")
    ema20 = _last(df, "EMA_20")
    ema50 = _last(df, "EMA_50")
    ema200 = _last(df, "EMA_200")
    bb_upper = _last(df, "BBU_20_2.0")
    bb_mid = _last(df, "BBM_20_2.0")
    bb_lower = _last(df, "BBL_20_2.0")
    stoch_k = _last(df, "STOCHk_14_3_3")
    stoch_d = _last(df, "STOCHd_14_3_3")

    avg_vol = float(df["Volume"].tail(20).mean()) if "Volume" in df.columns else None
    last_vol = float(df["Volume"].iloc[-1]) if "Volume" in df.columns else None
    vol_ratio = round(last_vol / avg_vol, 2) if avg_vol and avg_vol > 0 else None
    close = float(df["Close"].iloc[-1])
    high_52w = float(df["High"].tail(252).max()) if len(df) >= 50 else float(df["High"].max())
    low_52w = float(df["Low"].tail(252).min()) if len(df) >= 50 else float(df["Low"].min())

    indicators = {
        "close": round(close, 2),
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "rsi": {"value": round(rsi, 1) if rsi else None, "signal": _rsi_signal(rsi)},
        "macd": {
            "value": round(macd, 2) if macd else None,
            "signal_line": round(macd_signal, 2) if macd_signal else None,
            "histogram": round(macd_hist, 2) if macd_hist else None,
            "signal": _macd_signal(macd, macd_signal),
        },
        "ema": {
            "ema20": round(ema20, 2) if ema20 else None,
            "ema50": round(ema50, 2) if ema50 else None,
            "ema200": round(ema200, 2) if ema200 else None,
            "signal": _ema_signal(close, ema20, ema50, ema200),
            "above_ema20": close > ema20 if ema20 else None,
            "above_ema50": close > ema50 if ema50 else None,
            "above_ema200": close > ema200 if ema200 else None,
        },
        "bollinger": {
            "upper": round(bb_upper, 2) if bb_upper else None,
            "mid": round(bb_mid, 2) if bb_mid else None,
            "lower": round(bb_lower, 2) if bb_lower else None,
            "signal": _bb_signal(close, bb_upper, bb_lower, bb_mid),
        },
        "stochastic": {
            "k": round(stoch_k, 1) if stoch_k else None,
            "d": round(stoch_d, 1) if stoch_d else None,
            "signal": _stoch_signal(stoch_k, stoch_d),
        },
        "volume": {
            "last": int(last_vol) if last_vol else None,
            "avg_20d": int(avg_vol) if avg_vol else None,
            "ratio": vol_ratio,
            "signal": _volume_signal(vol_ratio),
        },
    }
    score, summary = _compute_tech_score(indicators)
    indicators["technical_score"] = score
    indicators["technical_summary"] = summary

    chart_data = []
    for idx, row in df.tail(90).iterrows():
        chart_data.append({
            "date": idx.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]) if "Volume" in row else 0,
        })
    indicators["chart_data"] = chart_data
    return indicators

def _last(df, col):
    if col in df.columns:
        val = df[col].dropna()
        if not val.empty:
            return float(val.iloc[-1])
    return None

def _rsi_signal(rsi):
    if rsi is None: return "N/A"
    if rsi >= 70: return "OVERBOUGHT"
    if rsi <= 30: return "OVERSOLD"
    if rsi >= 55: return "BULLISH"
    if rsi <= 45: return "BEARISH"
    return "NEUTRAL"

def _macd_signal(macd, signal):
    if macd is None or signal is None: return "N/A"
    if macd > signal and macd > 0: return "STRONG BULLISH"
    if macd > signal: return "BULLISH CROSSOVER"
    if macd < signal and macd < 0: return "STRONG BEARISH"
    return "BEARISH CROSSOVER"

def _ema_signal(close, ema20, ema50, ema200):
    above = sum([close > ema20 if ema20 else False, close > ema50 if ema50 else False, close > ema200 if ema200 else False])
    if above == 3: return "STRONG UPTREND"
    if above == 2: return "UPTREND"
    if above == 1: return "MIXED"
    return "DOWNTREND"

def _bb_signal(close, upper, lower, mid):
    if None in (upper, lower, mid): return "N/A"
    if close >= upper: return "OVERBOUGHT"
    if close <= lower: return "OVERSOLD"
    if close > mid: return "ABOVE MID — BULLISH"
    return "BELOW MID — BEARISH"

def _stoch_signal(k, d):
    if k is None or d is None: return "N/A"
    if k > 80 and d > 80: return "OVERBOUGHT"
    if k < 20 and d < 20: return "OVERSOLD"
    if k > d: return "BULLISH"
    return "BEARISH"

def _volume_signal(ratio):
    if ratio is None: return "N/A"
    if ratio >= 2.0: return "VERY HIGH VOLUME"
    if ratio >= 1.3: return "HIGH VOLUME"
    if ratio <= 0.6: return "LOW VOLUME"
    return "AVERAGE"

def _compute_tech_score(ind):
    score = 5.0
    rsi = ind["rsi"]["signal"]
    macd_s = ind["macd"]["signal"]
    ema_s = ind["ema"]["signal"]
    if rsi == "BULLISH": score += 0.5
    elif rsi == "OVERBOUGHT": score -= 0.5
    elif rsi == "OVERSOLD": score += 1.0
    elif rsi == "BEARISH": score -= 0.5
    if "STRONG BULLISH" in macd_s: score += 1.5
    elif "BULLISH" in macd_s: score += 0.8
    elif "STRONG BEARISH" in macd_s: score -= 1.5
    elif "BEARISH" in macd_s: score -= 0.8
    if ema_s == "STRONG UPTREND": score += 1.5
    elif ema_s == "UPTREND": score += 0.8
    elif ema_s == "DOWNTREND": score -= 1.5
    elif ema_s == "MIXED": score -= 0.3
    score = round(max(1.0, min(10.0, score)), 1)
    if score >= 7.5: summary = "Strong bullish setup"
    elif score >= 6.0: summary = "Moderately bullish"
    elif score >= 4.5: summary = "Neutral / mixed signals"
    elif score >= 3.0: summary = "Moderately bearish"
    else: summary = "Strong bearish pressure"
    return score, summary
