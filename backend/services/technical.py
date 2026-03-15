import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> dict:
    if df is None or len(df) < 20:
        return {"error": "Insufficient data"}

    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    volume = df["Volume"].squeeze()

    def rsi(series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def macd(series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line

    def bollinger(series, period=20, std=2):
        mid = series.rolling(period).mean()
        sigma = series.rolling(period).std()
        return mid + std * sigma, mid, mid - std * sigma

    def stochastic(high, low, close, k=14, d=3):
        lowest = low.rolling(k).min()
        highest = high.rolling(k).max()
        k_line = 100 * (close - lowest) / (highest - lowest).replace(0, np.nan)
        d_line = k_line.rolling(d).mean()
        return k_line, d_line

    def safe(series):
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if pd.isna(val): return None
        return round(float(val), 2)

    rsi_val = safe(rsi(close))
    macd_line, signal_line = macd(close)
    macd_val = safe(macd_line)
    signal_val = safe(signal_line)
    bb_upper, bb_mid, bb_lower = bollinger(close)
    stoch_k, stoch_d = stochastic(high, low, close)

    ema20 = safe(close.ewm(span=20, adjust=False).mean())
    ema50 = safe(close.ewm(span=50, adjust=False).mean())
    ema200 = safe(close.ewm(span=200, adjust=False).mean())
    vol_ma20 = safe(close.rolling(20).count() * 0 + volume.rolling(20).mean())
    current_vol = safe(volume)
    current_price = safe(close)

    # RSI signal
    rsi_signal = "NEUTRAL"
    if rsi_val:
        if rsi_val < 30: rsi_signal = "OVERSOLD"
        elif rsi_val > 70: rsi_signal = "OVERBOUGHT"
        elif rsi_val > 55: rsi_signal = "BULLISH"
        elif rsi_val < 45: rsi_signal = "BEARISH"

    # MACD signal
    macd_signal = "NEUTRAL"
    if macd_val and signal_val:
        if macd_val > signal_val: macd_signal = "BULLISH CROSSOVER"
        else: macd_signal = "BEARISH CROSSOVER"

    # EMA signal
    ema_signal = "NEUTRAL"
    if current_price and ema20 and ema50:
        if current_price > ema20 > ema50: ema_signal = "STRONG UPTREND"
        elif current_price > ema20: ema_signal = "UPTREND"
        elif current_price < ema20 < ema50: ema_signal = "DOWNTREND"
        else: ema_signal = "MIXED"

    # Bollinger signal
    bb_upper_val = safe(bb_upper)
    bb_lower_val = safe(bb_lower)
    bb_signal = "NEUTRAL"
    if current_price and bb_upper_val and bb_lower_val:
        mid = (bb_upper_val + bb_lower_val) / 2
        if current_price > mid: bb_signal = "ABOVE MID — BULLISH"
        else: bb_signal = "BELOW MID — BEARISH"

    # Stochastic signal
    stoch_k_val = safe(stoch_k)
    stoch_d_val = safe(stoch_d)
    stoch_signal = "NEUTRAL"
    if stoch_k_val:
        if stoch_k_val < 20: stoch_signal = "OVERSOLD"
        elif stoch_k_val > 80: stoch_signal = "OVERBOUGHT"
        elif stoch_k_val > 50: stoch_signal = "BULLISH"
        else: stoch_signal = "BEARISH"

    # Volume signal
    vol_ratio = round(current_vol / vol_ma20, 2) if (current_vol and vol_ma20 and vol_ma20 > 0) else None
    vol_signal = "AVERAGE"
    if vol_ratio:
        if vol_ratio > 2: vol_signal = "VERY HIGH VOLUME"
        elif vol_ratio > 1.3: vol_signal = "HIGH VOLUME"
        elif vol_ratio < 0.7: vol_signal = "LOW VOLUME"

    # Score
    score = 5
    if rsi_val:
        if rsi_val < 35: score += 1
        elif rsi_val > 65: score -= 1
    if macd_val and signal_val:
        if macd_val > signal_val: score += 1
        else: score -= 1
    if current_price and ema20 and ema50:
        if current_price > ema20 > ema50: score += 2
        elif current_price < ema20: score -= 1
    if current_price and ema200:
        if current_price > ema200: score += 1
        else: score -= 1
    tech_score = max(0, min(10, score))

    summary_map = {
        (8, 10): "Strong bullish momentum",
        (6, 7): "Moderately bullish",
        (5, 5): "Neutral — wait for confirmation",
        (3, 4): "Moderately bearish",
        (0, 2): "Strong bearish — caution advised",
    }
    technical_summary = next(
        (v for (lo, hi), v in summary_map.items() if lo <= tech_score <= hi),
        "Neutral"
    )

    # 52w from data
    high_52w = round(float(high.max()), 2) if not high.empty else None
    low_52w = round(float(low.min()), 2) if not low.empty else None

    return {
        "currentPrice": current_price,
        "current_price": current_price,
        "close": current_price,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "technical_score": tech_score,
        "technicalScore": tech_score,
        "technical_summary": technical_summary,
        "rsi": {"value": rsi_val, "signal": rsi_signal},
        "macd": {"value": macd_val, "signal_line": signal_val, "signal": macd_signal},
        "ema": {"ema20": ema20, "ema50": ema50, "ema200": ema200, "signal": ema_signal},
        "bollinger": {"upper": bb_upper_val, "lower": bb_lower_val, "signal": bb_signal},
        "stochastic": {"k": stoch_k_val, "d": stoch_d_val, "signal": stoch_signal},
        "volume": {"ratio": vol_ratio, "signal": vol_signal},
        "signals": [],
    }
