def score_fundamentals(fund: dict) -> dict:
    if "error" in fund:
        return {"error": fund["error"]}
    grades = {}
    total = 0.0
    count = 0

    def add(key, value, score_fn, format_fn, note_fn):
        nonlocal total, count
        if value is not None:
            s = score_fn(value)
            grades[key] = {"value": format_fn(value), "score": s, "grade": _letter(s), "note": note_fn(value)}
            total += s
            count += 1

    add("pe_ratio", fund.get("pe_ratio"), _score_pe, lambda v: f"{round(v,1)}x", _pe_note)
    add("pb_ratio", fund.get("pb_ratio"), _score_pb, lambda v: f"{round(v,2)}x", _pb_note)
    add("roe", fund.get("roe"), lambda v: _score_roe(v*100), lambda v: f"{v*100:.1f}%", lambda v: _roe_note(v*100))
    add("profit_margin", fund.get("profit_margin"), lambda v: _score_margin(v*100), lambda v: f"{v*100:.1f}%", lambda v: _margin_note(v*100))
    add("revenue_growth", fund.get("revenue_growth"), lambda v: _score_growth(v*100), lambda v: f"{v*100:.1f}%", lambda v: _growth_note(v*100))
    add("earnings_growth", fund.get("earnings_growth"), lambda v: _score_growth(v*100), lambda v: f"{v*100:.1f}%", lambda v: _growth_note(v*100))
    add("debt_to_equity", fund.get("debt_to_equity"), _score_de, lambda v: f"{round(v,2)}", _de_note)
    add("current_ratio", fund.get("current_ratio"), _score_cr, lambda v: f"{round(v,2)}", _cr_note)

    final_score = round(total / count, 1) if count > 0 else 5.0
    return {
        "fundamental_score": final_score,
        "fundamental_grade": _letter(final_score),
        "fundamental_summary": _fund_summary(final_score),
        "metrics": grades,
    }

def _score_pe(v):
    if v <= 0: return 3.0
    if v < 10: return 9.0
    if v < 20: return 8.0
    if v < 30: return 6.5
    if v < 40: return 5.0
    return 3.0

def _score_pb(v):
    if v <= 0: return 3.0
    if v < 1: return 9.0
    if v < 2: return 8.0
    if v < 4: return 6.5
    if v < 8: return 5.0
    return 3.5

def _score_roe(v):
    if v >= 25: return 9.5
    if v >= 15: return 8.0
    if v >= 10: return 6.5
    if v >= 5: return 5.0
    return 3.0

def _score_margin(v):
    if v >= 25: return 9.5
    if v >= 15: return 8.0
    if v >= 8: return 6.5
    if v >= 3: return 5.0
    return 3.0

def _score_growth(v):
    if v >= 25: return 9.5
    if v >= 15: return 8.0
    if v >= 8: return 6.5
    if v >= 0: return 5.0
    return 3.0

def _score_de(v):
    if v < 0.1: return 9.5
    if v < 0.5: return 8.0
    if v < 1.0: return 6.5
    if v < 1.5: return 5.0
    return 3.5

def _score_cr(v):
    if v >= 2.5: return 8.5
    if v >= 1.5: return 7.5
    if v >= 1.0: return 5.5
    return 3.0

def _letter(s):
    if s >= 8.5: return "A+"
    if s >= 7.5: return "A"
    if s >= 6.5: return "B+"
    if s >= 5.5: return "B"
    if s >= 4.5: return "C+"
    if s >= 3.5: return "C"
    return "D"

def _fund_summary(s):
    if s >= 8: return "Excellent — top-tier fundamentals"
    if s >= 7: return "Strong business quality"
    if s >= 6: return "Good fundamentals, some concerns"
    if s >= 5: return "Average — mixed quality"
    if s >= 4: return "Below average — caution advised"
    return "Weak fundamentals"

def _pe_note(v): return "Undervalued" if v < 15 else "Fairly valued" if v < 25 else "Premium valuation"
def _pb_note(v): return "Below book value" if v < 1 else "Reasonable" if v < 3 else "High premium"
def _roe_note(v): return "Excellent capital efficiency" if v >= 20 else "Good returns" if v >= 12 else "Below average"
def _margin_note(v): return "Exceptional profitability" if v >= 20 else "Healthy margins" if v >= 10 else "Thin margins"
def _growth_note(v): return "High growth" if v >= 20 else "Solid growth" if v >= 8 else "Slow growth" if v >= 0 else "Declining"
def _de_note(v): return "Near debt-free" if v < 0.3 else "Conservative leverage" if v < 0.7 else "Moderate debt" if v < 1.2 else "High leverage"
def _cr_note(v): return "Strong liquidity" if v >= 2 else "Adequate liquidity" if v >= 1.2 else "Tight liquidity"
