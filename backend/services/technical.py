"""
services/technical.py
Pure pandas/numpy implementation of all technical indicators.
No pandas-ta dependency.
"""
import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> dict:
    if df is None or len(df) < 20:
        return {"error": "Insufficient data"}

    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    volume = df["Volume"].squeeze()

    # ── RSI ──────────────────────────────────────────────────────────────────
    def rsi(series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    # ── MACD ─────────────────────────────────────────────────────────────────
    def macd(series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    def bollinger(series, period=20, std=2):
        mid = series.rolling(period).mean()
        sigma = series.rolling(period).std()
        return mid + std * sigma, mid, mid - std * sigma

    # ── Stochastic ────────────────────────────────────────────────────────────
    def stochastic(high, low, close, k=14, d=3):
        lowest_low = low.rolling(k).min()
        highest_high = high.rolling(k).max()
        k_line = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
        d_line = k_line.rolling(d).mean()
        return k_line, d_line

    # ── ATR ───────────────────────────────────────────────────────────────────
    def atr(high, low, close, period=14):
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    # Calculate all
    rsi_val = rsi(close)
    macd_line, signal_line, histogram = macd(close)
    bb_upper, bb_mid, bb_lower = bollinger(close)
    stoch_k, stoch_d = stochastic(high, low, close)
    atr_val = atr(high, low, close)

    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    vol_ma20 = volume.rolling(20).mean()

    def safe(series):
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if pd.isna(val):
            return None
        return round(float(val), 4)

    current_price = safe(close)
    current_volume = safe(volume)
    avg_volume = safe(vol_ma20)

    # ── Signals ───────────────────────────────────────────────────────────────
    rsi_now = safe(rsi_val)
    macd_now = safe(macd_line)
    signal_now = safe(signal_line)
    hist_now = safe(histogram)
    stoch_k_now = safe(stoch_k)
    bb_upper_now = safe(bb_upper)
    bb_lower_now = safe(bb_lower)
    ema20_now = safe(ema20)
    ema50_now = safe(ema50)
    ema200_now = safe(ema200)

    signals = []
    score = 0

    if rsi_now:
        if rsi_now < 30:
            signals.append("RSI oversold — potential buy zone")
            score += 2
        elif rsi_now > 70:
            signals.append("RSI overbought — caution advised")
            score -= 2
        else:
            signals.append(f"RSI neutral at {rsi_now}")
            score += 1

    if macd_now and signal_now:
        if macd_now > signal_now:
            signals.append("MACD bullish crossover")
            score += 2
        else:
            signals.append("MACD bearish — momentum weakening")
            score -= 1

    if current_price and ema20_now and ema50_now:
        if current_price > ema20_now > ema50_now:
            signals.append("Price above EMA20 & EMA50 — uptrend")
            score += 2
        elif current_price < ema20_now:
            signals.append("Price below EMA20 — short-term weakness")
            score -= 1

    if current_price and ema200_now:
        if current_price > ema200_now:
            signals.append("Above EMA200 — long-term bullish")
            score += 1
        else:
            signals.append("Below EMA200 — long-term bearish")
            score -= 1

    if current_price and bb_lower_now and bb_upper_now:
        if current_price < bb_lower_now:
            signals.append("Near Bollinger lower band — oversold")
            score += 1
        elif current_price > bb_upper_now:
            signals.append("Near Bollinger upper band — overbought")
            score -= 1

    if current_volume and avg_volume:
        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        if vol_ratio > 1.5:
            signals.append(f"High volume ({round(vol_ratio,1)}x avg) — strong conviction")
            score += 1

    # Technical score 0-10
    tech_score = max(0, min(10, score + 5))

    return {
        "currentPrice": current_price,
        "rsi": rsi_now,
        "macd": macd_now,
        "macdSignal": signal_now,
        "macdHistogram": hist_now,
        "ema20": ema20_now,
        "ema50": ema50_now,
        "ema200": ema200_now,
        "bbUpper": bb_upper_now,
        "bbMid": safe(bb_mid),
        "bbLower": bb_lower_now,
        "stochK": stoch_k_now,
        "stochD": safe(stoch_d),
        "atr": safe(atr_val),
        "volume": current_volume,
        "avgVolume": avg_volume,
        "signals": signals,
        "technicalScore": tech_score,
    }
