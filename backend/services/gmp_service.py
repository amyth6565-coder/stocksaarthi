"""
services/gmp_service.py
Scrapes ipowatch.in for live GMP data (Mainboard + SME).
Static HTML — no JS rendering needed.
"""

import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

GMP_URL = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"

# Simple in-memory cache: {data, fetched_at}
_cache = {"data": None, "fetched_at": None}
CACHE_TTL_MINUTES = 15  # refresh GMP every 15 minutes


def _parse_gmp_rupee(text: str) -> int:
    """Extract integer rupee value from strings like '₹18', '₹0', '₹3.50'"""
    text = text.strip().replace("₹", "").replace(",", "").strip()
    try:
        return int(float(text))
    except Exception:
        return 0


def _parse_listing_gain(text: str) -> float:
    """Extract float % from strings like '16.36%', '-%', '-'"""
    text = text.strip().replace("%", "").strip()
    if text in ["-", "", "-%"]:
        return 0.0
    try:
        return round(float(text), 2)
    except Exception:
        return 0.0


def _parse_tables(soup: BeautifulSoup) -> dict:
    """
    ipowatch.in has two tables on the GMP page:
    1. Mainboard IPO GMP
    2. SME IPO GMP
    Both have columns: IPO | GMP | Price Band | Listing Gain | Date
    """
    tables = soup.find_all("table")
    mainboard = []
    sme = []

    for i, table in enumerate(tables[:2]):  # only first 2 tables
        rows = table.find_all("tr")
        for row in rows[1:]:  # skip header
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) < 5:
                continue

            name = cols[0]
            gmp_rupee = _parse_gmp_rupee(cols[1])
            price_band = cols[2].replace("₹", "").strip()
            listing_gain = _parse_listing_gain(cols[3])
            date_range = cols[4]

            entry = {
                "name": name,
                "gmp": gmp_rupee,
                "price_band": price_band,
                "listing_gain_pct": listing_gain,
                "dates": date_range,
                "sentiment": _gmp_sentiment(gmp_rupee, listing_gain),
            }

            if i == 0:
                mainboard.append(entry)
            else:
                sme.append(entry)

    return {"mainboard": mainboard, "sme": sme}


def _gmp_sentiment(gmp: int, gain_pct: float) -> str:
    """Simple sentiment label based on GMP"""
    if gmp > 20 or gain_pct > 15:
        return "🔥 Strong"
    elif gmp > 0 or gain_pct > 0:
        return "✅ Positive"
    elif gmp == 0 and gain_pct == 0:
        return "⚪ Neutral"
    else:
        return "🔴 Weak"


async def fetch_gmp_data() -> dict:
    """
    Returns cached GMP data or fetches fresh from ipowatch.in.
    Cache TTL = 15 minutes.
    """
    global _cache

    now = datetime.now()
    if (
        _cache["data"] is not None
        and _cache["fetched_at"] is not None
        and (now - _cache["fetched_at"]) < timedelta(minutes=CACHE_TTL_MINUTES)
    ):
        logger.info("GMP cache hit")
        return _cache["data"]

    logger.info("Fetching fresh GMP data from ipowatch.in")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-IN,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(timeout=15, headers=headers, follow_redirects=True) as client:
            resp = await client.get(GMP_URL)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        data = _parse_tables(soup)
        data["source"] = "ipowatch.in"
        data["updated_at"] = now.strftime("%d %b %Y %H:%M")
        data["disclaimer"] = (
            "GMP is unofficial grey market data for informational purposes only. "
            "Do not invest solely based on GMP. Consult a SEBI-registered advisor."
        )

        _cache["data"] = data
        _cache["fetched_at"] = now
        logger.info(f"GMP fetched: {len(data['mainboard'])} mainboard, {len(data['sme'])} SME")
        return data

    except Exception as e:
        logger.error(f"GMP fetch error: {e}")
        # Return stale cache if available
        if _cache["data"]:
            logger.warning("Returning stale GMP cache due to fetch error")
            return _cache["data"]
        # Return empty fallback
        return {
            "mainboard": [],
            "sme": [],
            "source": "unavailable",
            "updated_at": now.strftime("%d %b %Y %H:%M"),
            "disclaimer": "GMP data temporarily unavailable.",
            "error": str(e),
        }


def get_gmp_for_ipo(ipo_name: str, gmp_data: dict) -> dict | None:
    """
    Fuzzy match an IPO name against GMP data.
    Used to enrich NSE IPO listings with GMP.
    Returns the matched GMP entry or None.
    """
    if not gmp_data:
        return None

    search = ipo_name.lower().strip()
    all_entries = gmp_data.get("mainboard", []) + gmp_data.get("sme", [])

    # Try exact match first
    for entry in all_entries:
        if entry["name"].lower() == search:
            return entry

    # Try contains match (both directions)
    for entry in all_entries:
        entry_name = entry["name"].lower()
        words = search.split()
        if any(w in entry_name for w in words if len(w) > 3):
            return entry

    return None