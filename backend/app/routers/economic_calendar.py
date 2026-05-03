"""
Economic Calendar Router - NFP, CPI, FOMC, PMI Events
=======================================================
Data sources:
  - BLS API v2: CPI, NFP, Unemployment Rate
  - Manual calendar: Known recurring events with typical impact

BLS API: https://api.bls.gov/publicAPI
Free: 25 requests/day without API key, 50 with key
"""

from fastapi import APIRouter, HTTPException
from app.services.cache_service import cache
from app.config import settings
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

router = APIRouter()
logger = logging.getLogger(__name__)


def _nan_to_none(value: float) -> Optional[float]:
    if value is None:
        return None
    try:
        if value != value:
            return None
    except (TypeError, ValueError):
        pass
    return value


# Pre-defined economic calendar (recurring high-impact events)
# Format: (event_name, typical_release_date, period_type, impact, description)
ECONOMIC_CALENDAR = [
    {
        "name": "Non-Farm Payrolls (NFP)",
        "series_id": "CES7000000001",  # Employment situation
        "frequency": "Monthly",
        "typical_date": "First Friday of month",
        "impact": "HIGH",
        "description": "Change in number of employed people (excl. farming). "
                       "Gold: NFP↓ = USD↓ = Gold↑ (safe haven). Gold: NFP↑ = USD↑ = Gold↓.",
        "category": "Employment",
    },
    {
        "name": "CPI (Consumer Price Index)",
        "series_id": "CPIAUCSL",  # CPI All Urban Consumers
        "frequency": "Monthly",
        "typical_date": "Mid-month",
        "impact": "HIGH",
        "description": "Inflation measure. Gold: CPI↑ = Real yields↓ = Gold↑. "
                       "CPI↓ = Real yields↑ = Gold↓.",
        "category": "Inflation",
    },
    {
        "name": "Core CPI (ex Food & Energy)",
        "series_id": "CPILFESL",
        "frequency": "Monthly",
        "typical_date": "Mid-month",
        "impact": "HIGH",
        "description": "Core inflation (ex volatile food/energy). Fed watches this closely.",
        "category": "Inflation",
    },
    {
        "name": "FOMC Rate Decision",
        "series_id": None,
        "frequency": "8x per year (approx. every 6 weeks)",
        "typical_date": "Based on schedule (cmegroup.com/governance/interest-rates)",
        "impact": "HIGH",
        "description": "Fed rate decision. Gold: Rate↓ = USD↓ = Gold↑. "
                       "Rate↑ = USD↑ = Gold↓.",
        "category": "Central Bank",
    },
    {
        "name": "Federal Funds Rate",
        "series_id": "FEDFUNDS",
        "frequency": "Effective overnight rate",
        "typical_date": "Daily (published monthly)",
        "impact": "MEDIUM",
        "description": "Current Fed policy rate. Controls all other interest rates.",
        "category": "Central Bank",
    },
    {
        "name": "Unemployment Rate",
        "series_id": "UNRATE",
        "frequency": "Monthly",
        "typical_date": "First Friday (with NFP)",
        "impact": "HIGH",
        "description": "U3 unemployment. Gold: Unemployment↑ = USD weakness = Gold↑.",
        "category": "Employment",
    },
    {
        "name": "ISM Manufacturing PMI",
        "series_id": "MANEMP",
        "frequency": "Monthly",
        "typical_date": "First business day of month",
        "impact": "MEDIUM",
        "description": "Manufacturing health indicator. >50 = expansion, <50 = contraction.",
        "category": "PMI",
    },
    {
        "name": "ISM Services PMI",
        "series_id": "NMEMP",
        "frequency": "Monthly",
        "typical_date": "Third business day of month",
        "impact": "MEDIUM",
        "description": "Services sector health. Largest part of US economy (~80%).",
        "category": "PMI",
    },
    {
        "name": "GDP (Gross Domestic Product)",
        "series_id": "GDP",
        "frequency": "Quarterly",
        "typical_date": "End of month (advance/second/third estimate)",
        "impact": "HIGH",
        "description": "Economic growth measure. Gold: GDP↓ = USD↓ = Gold↑.",
        "category": "GDP",
    },
    {
        "name": "Retail Sales",
        "series_id": "RRSFS",
        "frequency": "Monthly",
        "typical_date": "Mid-month",
        "impact": "MEDIUM",
        "description": "Consumer spending. Largest driver of US GDP.",
        "category": "Consumer",
    },
    {
        "name": "PPI (Producer Price Index)",
        "series_id": "PPIFID",
        "frequency": "Monthly",
        "typical_date": "Around 10th of month",
        "impact": "MEDIUM",
        "description": "Wholesale inflation. Leads CPI by 1-2 months.",
        "category": "Inflation",
    },
    {
        "name": "Consumer Confidence Index",
        "series_id": "CONCCI",
        "frequency": "Monthly",
        "typical_date": "Last week of month",
        "impact": "MEDIUM",
        "description": "Consumer sentiment. Gold: Confidence↓ = USD weakness = Gold↑.",
        "category": "Consumer",
    },
]


async def fetch_bls_series(series_id: str, start_year: int, end_year: int) -> List[Dict]:
    """Fetch data from BLS API v2."""
    url = f"{settings.BLS_BASE_URL}/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if settings.BLS_API_KEY:
        payload["registrationkey"] = settings.BLS_API_KEY

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "REQUEST_SUCCEEDED":
                logger.warning(f"BLS API error: {data.get('status')}")
                return []

            results = data.get("Results", {}).get("series", [])
            if not results:
                return []

            observations = results[0].get("data", [])
            return [
                {
                    "year": obs.get("year"),
                    "period": obs.get("period"),
                    "value": float(obs.get("value", 0)),
                    "date": f"{obs.get('year')}-{obs.get('period', '').replace('M', '').zfill(2)}-01",
                }
                for obs in observations
            ]
    except Exception as e:
        logger.error(f"BLS API error for {series_id}: {e}")
        return []


@router.get("/calendar")
async def get_economic_calendar():
    """
    Get upcoming economic events calendar.
    Returns the predefined calendar with next occurrence dates.
    """
    cache_key = "economic:calendar"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    now = datetime.now()

    # Calculate next occurrence for each event
    enriched_calendar = []
    for event in ECONOMIC_CALENDAR:
        next_date = _get_next_event_date(event["name"], now)
        enriched = {**event, "next_release": next_date}

        # Add impact color for frontend
        impact_colors = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
        enriched["impact_color"] = impact_colors.get(event["impact"], "gray")
        enriched_calendar.append(enriched)

    await cache.set(cache_key, enriched_calendar, ttl=86400)  # 24h cache
    return {"data": enriched_calendar, "source": "calendar"}


@router.get("/latest")
async def get_latest_economic_data():
    """
    Get latest values of key economic indicators (from BLS + FRED).
    Includes: NFP, Unemployment, CPI, Core CPI.
    """
    cache_key = "economic:latest"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    current_year = datetime.now().year
    year_2_ago = current_year - 2

    # Fetch all key series in parallel
    import asyncio

    nfp_data = await fetch_bls_series("CES7000000001", year_2_ago, current_year)
    cpi_data = await fetch_bls_series("CPIAUCSL", year_2_ago, current_year)
    core_cpi_data = await fetch_bls_series("CPILFESL", year_2_ago, current_year)
    unemployment_data = await fetch_bls_series("UNRATE", year_2_ago, current_year)

    def latest_entry(data: List[Dict]) -> Optional[Dict]:
        if not data:
            return None
        valid = [d for d in data if d.get("value") is not None]
        return valid[-1] if valid else None

    def prev_entry(data: List[Dict]) -> Optional[Dict]:
        if not data or len(data) < 2:
            return None
        valid = [d for d in data if d.get("value") is not None]
        return valid[-2] if len(valid) >= 2 else None

    nfp_latest = latest_entry(nfp_data)
    nfp_prev = prev_entry(nfp_data)
    cpi_latest = latest_entry(cpi_data)
    cpi_prev = prev_entry(core_cpi_data)  # Use same month for YoY calc
    unemp_latest = latest_entry(unemployment_data)
    unemp_prev = prev_entry(unemployment_data)

    # YoY CPI change (approximate - need 12 months ago)
    def yoy_change(data: List[Dict]) -> Optional[float]:
        if not data or len(data) < 13:
            return None
        latest = data[-1].get("value")
        year_ago = data[-13].get("value") if len(data) >= 13 else None
        if latest and year_ago and year_ago != 0:
            return round(((latest - year_ago) / year_ago) * 100, 2)
        return None

    result = {
        "timestamp": datetime.now().isoformat(),
        "nfp": {
            "value": _nan_to_none(nfp_latest.get("value")) if nfp_latest else None,
            "period": nfp_latest.get("period") if nfp_latest else None,
            "year": nfp_latest.get("year") if nfp_latest else None,
            "previous": _nan_to_none(nfp_prev.get("value")) if nfp_prev else None,
            "description": "Non-Farm Payrolls (thousands)",
        },
        "unemployment": {
            "value": _nan_to_none(unemp_latest.get("value")) if unemp_latest else None,
            "period": unemp_latest.get("period") if unemp_latest else None,
            "year": unemp_latest.get("year") if unemp_latest else None,
            "previous": _nan_to_none(unemp_prev.get("value")) if unemp_prev else None,
            "description": "U3 Unemployment Rate (%)",
        },
        "cpi": {
            "value": _nan_to_none(cpi_latest.get("value")) if cpi_latest else None,
            "period": cpi_latest.get("period") if cpi_latest else None,
            "year": cpi_latest.get("year") if cpi_latest else None,
            "yoy_change": yoy_change(cpi_data),
            "description": "CPI All Urban Consumers (Index, 1982-84=100)",
        },
        "impact_signals": {
            "nfp_signal": _interpret_nfp(nfp_latest, nfp_prev) if nfp_latest else "no_data",
            "unemployment_signal": _interpret_unemployment(unemp_latest, unemp_prev) if unemp_latest else "no_data",
        }
    }

    await cache.set(cache_key, result, ttl=3600)  # 1 hour cache
    return {"data": result, "source": "bls"}


def _interpret_nfp(latest: Optional[Dict], previous: Optional[Dict]) -> str:
    if not latest or not previous:
        return "no_data"
    curr = latest.get("value", 0)
    prev = previous.get("value", 0)
    if curr > 200 and prev < 100:
        return "bullish_gold"  # Weak USD
    if curr < 50 or curr < 0:
        return "bearish_gold"  # Strong USD
    if curr > prev + 100:
        return "mildly_bullish_gold"
    return "neutral"


def _interpret_unemployment(latest: Optional[Dict], previous: Optional[Dict]) -> str:
    if not latest or not previous:
        return "no_data"
    curr = latest.get("value", 0)
    prev = previous.get("value", 0)
    if curr > prev + 0.2:
        return "bullish_gold"  # Rising unemployment = USD weakness
    if curr < prev - 0.2:
        return "bearish_gold"  # Falling unemployment = USD strength
    return "neutral"


def _get_next_event_date(event_name: str, from_date: datetime) -> str:
    """Calculate next occurrence for recurring events."""
    from datetime import date as _date
    year = from_date.year
    month = from_date.month

    if "NFP" in event_name or "Unemployment" in event_name:
        # First Friday of month
        first = _date(year, month, 1)
        # Find first Friday (weekday 4)
        days_ahead = (4 - first.weekday()) % 7
        first_friday = first + timedelta(days=days_ahead)
        if first_friday <= from_date.date():
            first = _date(year, month + 1 if month < 12 else 1, 1)
            days_ahead = (4 - first.weekday()) % 7
            first_friday = first + timedelta(days=days_ahead)
        return first_friday.strftime("%Y-%m-%d")

    if "CPI" in event_name:
        # Typically mid-month (around 10-15)
        mid = _date(year, month, 12)
        if mid <= from_date.date():
            if month == 12:
                mid = _date(year + 1, 1, 12)
            else:
                mid = _date(year, month + 1, 12)
        return mid.strftime("%Y-%m-%d")

    if "FOMC" in event_name:
        # FOMC meetings are scheduled roughly every 6 weeks
        # Approximate: Jan 30, Mar 20, May 1, Jun 18, Jul 31, Sep 18, Nov 7, Dec 18
        fomc_dates = [
            _date(year, 1, 30), _date(year, 3, 20), _date(year, 5, 1), _date(year, 6, 18),
            _date(year, 7, 31), _date(year, 9, 18), _date(year, 11, 7), _date(year, 12, 18),
        ]
        for d in fomc_dates:
            if d > from_date.date():
                return d.strftime("%Y-%m-%d")
        # Next year
        return _date(year + 1, 1, 30).strftime("%Y-%m-%d")

    if "PMI" in event_name:
        # First business day of month
        first = _date(year, month, 1)
        days_ahead = (0 - first.weekday() + 7) % 7  # Monday
        if days_ahead == 0:
            days_ahead = 7
        first_biz = first + timedelta(days=days_ahead)
        if first_biz <= from_date.date():
            if month == 12:
                first = _date(year + 1, 1, 1)
            else:
                first = _date(year, month + 1, 1)
            days_ahead = (0 - first.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            first_biz = first + timedelta(days=days_ahead)
        return first_biz.strftime("%Y-%m-%d")

    return "TBD"
