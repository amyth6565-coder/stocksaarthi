"""
routers/ipo.py
IPO endpoints: open, upcoming, closed, listed, sme, gmp, verdict
"""

from fastapi import APIRouter, HTTPException
from nse import NSE
from pathlib import Path
import os
from groq import Groq
from services.gmp_service import fetch_gmp_data, get_gmp_for_ipo
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ipo", tags=["ipo"])

GROQ_MODEL = "llama-3.3-70b-versatile"

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

# ── NSE helper ────────────────────────────────────────────────────────────────

def get_nse():
    return NSE(download_folder=Path("."))


# ── GMP endpoint ──────────────────────────────────────────────────────────────

@router.get("/gmp")
async def get_gmp():
    """
    Returns live GMP data for Mainboard + SME IPOs from ipowatch.in.
    Cached for 15 minutes.
    """
    data = await fetch_gmp_data()
    return data


# ── Open IPOs ─────────────────────────────────────────────────────────────────

@router.get("/open")
async def get_open_ipos():
    nse = get_nse()
    try:
        raw = nse.listCurrentIPO()
        gmp_data = await fetch_gmp_data()

        result = []
        for ipo in raw:
            entry = {
                "symbol": ipo.get("symbol", ""),
                "companyName": ipo.get("companyName", ""),
                "series": ipo.get("series", ""),
                "issueStartDate": ipo.get("issueStartDate", ""),
                "issueEndDate": ipo.get("issueEndDate", ""),
                "issuePrice": ipo.get("issuePrice", ""),
                "issueSize": ipo.get("issueSize", ""),
                "status": ipo.get("status", ""),
                "noOfSharesBid": ipo.get("noOfSharesBid", 0),
                "noOfSharesOffered": ipo.get("noOfSharesOffered", 0),
                "subscriptionTimes": _calc_subscription(ipo),
                "type": _ipo_type(ipo),
                "gmp": get_gmp_for_ipo(ipo.get("companyName", ""), gmp_data),
            }
            result.append(entry)
        return {"ipos": result, "count": len(result)}
    except Exception as e:
        logger.error(f"Open IPOs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        nse.exit()


# ── Upcoming IPOs ─────────────────────────────────────────────────────────────

@router.get("/upcoming")
async def get_upcoming_ipos():
    nse = get_nse()
    try:
        raw = nse.listUpcomingIPO()
        gmp_data = await fetch_gmp_data()

        result = []
        for ipo in raw:
            entry = {
                "symbol": ipo.get("symbol", ""),
                "companyName": ipo.get("companyName", ""),
                "series": ipo.get("series", ""),
                "issueStartDate": ipo.get("issueStartDate", ""),
                "issueEndDate": ipo.get("issueEndDate", ""),
                "issuePrice": ipo.get("issuePrice", ""),
                "issueSize": ipo.get("issueSize", ""),
                "status": ipo.get("status", ""),
                "type": _ipo_type(ipo),
                "gmp": get_gmp_for_ipo(ipo.get("companyName", ""), gmp_data),
            }
            result.append(entry)
        return {"ipos": result, "count": len(result)}
    except Exception as e:
        logger.error(f"Upcoming IPOs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        nse.exit()


# ── Closed IPOs ───────────────────────────────────────────────────────────────

@router.get("/closed")
async def get_closed_ipos():
    nse = get_nse()
    try:
        raw = nse.listPastIPO()
        gmp_data = await fetch_gmp_data()

        result = []
        for ipo in raw[:30]:  # last 30
            name = ipo.get("company", ipo.get("companyName", ""))
            entry = {
                "symbol": ipo.get("symbol", ""),
                "companyName": name,
                "ipoStartDate": ipo.get("ipoStartDate", ""),
                "ipoEndDate": ipo.get("ipoEndDate", ""),
                "issuePrice": ipo.get("issuePrice", ""),
                "priceRange": ipo.get("priceRange", ""),
                "listingDate": ipo.get("listingDate", ""),
                "securityType": ipo.get("securityType", ""),
                "type": "SME" if _is_sme_by_security_type(ipo) else "Mainboard",
                "gmp": get_gmp_for_ipo(name, gmp_data),
            }
            result.append(entry)
        return {"ipos": result, "count": len(result)}
    except Exception as e:
        logger.error(f"Closed IPOs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        nse.exit()


# ── Listed IPOs ───────────────────────────────────────────────────────────────

@router.get("/listed")
async def get_listed_ipos():
    """Recently listed IPOs from past IPO list filtered to those with listing date."""
    nse = get_nse()
    try:
        raw = nse.listPastIPO()
        result = []
        for ipo in raw[:20]:
            if ipo.get("listingDate"):
                name = ipo.get("company", ipo.get("companyName", ""))
                result.append({
                    "symbol": ipo.get("symbol", ""),
                    "companyName": name,
                    "issuePrice": ipo.get("issuePrice", ""),
                    "listingDate": ipo.get("listingDate", ""),
                    "priceRange": ipo.get("priceRange", ""),
                    "type": "SME" if _is_sme_by_security_type(ipo) else "Mainboard",
                })
        return {"ipos": result, "count": len(result)}
    except Exception as e:
        logger.error(f"Listed IPOs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        nse.exit()


# ── SME IPOs (from GMP data) ──────────────────────────────────────────────────

@router.get("/sme")
async def get_sme_ipos():
    """
    SME IPO data sourced from ipowatch.in GMP page.
    NSE library has no dedicated SME IPO listing method.
    """
    gmp_data = await fetch_gmp_data()
    sme_ipos = gmp_data.get("sme", [])

    return {
        "ipos": sme_ipos,
        "count": len(sme_ipos),
        "source": gmp_data.get("source", "ipowatch.in"),
        "updated_at": gmp_data.get("updated_at", ""),
        "note": "SME IPO data sourced from grey market tracker. Includes current, upcoming & recently closed SME IPOs.",
    }


# ── IPO Verdict (AI) ──────────────────────────────────────────────────────────

@router.get("/verdict/{company_name}")
async def get_ipo_verdict(company_name: str):
    """AI verdict for an IPO using Groq."""
    client = get_groq_client()
    if not client:
        return {
            "verdict": "AI verdict unavailable. Add GROQ_API_KEY to .env to enable AI analysis.",
            "company": company_name,
        }

    # Also try to get GMP data for this IPO
    gmp_data = await fetch_gmp_data()
    gmp_entry = get_gmp_for_ipo(company_name, gmp_data)
    gmp_context = ""
    if gmp_entry:
        gmp_context = (
            f"\nGrey Market Premium (GMP): ₹{gmp_entry['gmp']} "
            f"({gmp_entry['listing_gain_pct']}% estimated listing gain). "
            f"Sentiment: {gmp_entry['sentiment']}."
        )

    prompt = f"""You are StockSaarthi, an honest Indian IPO advisor. Give a clear, practical verdict on this IPO.

IPO: {company_name}{gmp_context}

Provide:
1. **Overall Verdict**: SUBSCRIBE / AVOID / NEUTRAL (with 1-line reason)
2. **Risk Level**: Low / Medium / High
3. **Who should apply**: (e.g., "Only aggressive investors willing to take short-term risk")
4. **Key concern**: One main risk to watch
5. **Listing expectation**: Based on available data

Keep it under 150 words. Be honest — don't be overly optimistic.
End with: ⚠️ *This is not SEBI-registered advice. Do your own research.*"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )
        verdict_text = response.choices[0].message.content
    except Exception as e:
        logger.error(f"IPO verdict AI error: {e}")
        verdict_text = "AI analysis temporarily unavailable. Please try again later."

    return {
        "company": company_name,
        "verdict": verdict_text,
        "gmp": gmp_entry,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _calc_subscription(ipo: dict) -> float:
    """Calculate subscription times from bid vs offered shares."""
    try:
        bid = float(ipo.get("noOfSharesBid", 0) or 0)
        offered = float(ipo.get("noOfSharesOffered", 1) or 1)
        if offered > 0 and bid > 0:
            return round(bid / offered, 2)
    except Exception:
        pass
    return 0.0


def _ipo_type(ipo: dict) -> str:
    """Determine Mainboard vs SME from series field."""
    series = (ipo.get("series", "") or "").upper()
    if series in ["SM", "ST", "SZ", "SE"]:
        return "SME"
    return "Mainboard"


def _is_sme_by_security_type(ipo: dict) -> bool:
    """Check security type field in past IPO data."""
    sec_type = (ipo.get("securityType", "") or "").upper()
    return "SME" in sec_type or sec_type in ["SM", "ST"]