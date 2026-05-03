"""
Macro Router - US Macro Economic Data for XAU/USD Trading
=========================================================
Endpoints:
  GET /api/macro/snapshot     - All macro indicators in one call
  GET /api/macro/history/:key - Historical data for a specific indicator
  GET /api/macro/fed-probability - CME FedWatch rate probability
"""

from fastapi import APIRouter, HTTPException
from app.services.fred_service import fred_service
from app.services.cache_service import cache
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/snapshot")
async def get_macro_snapshot():
    """
    Get complete macro snapshot for XAU/USD trading decisions.
    Includes: DXY, Gold, Treasury Yields, Real Yields, Yield Curve, Signals.
    """
    cache_key = "macro:snapshot"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    try:
        data = await fred_service.get_macro_snapshot()
        await cache.set(cache_key, data, ttl=300)  # 5 min cache
        return {"data": data, "source": "fred"}
    except Exception as e:
        logger.error(f"Macro snapshot error: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch macro data: {str(e)}")


@router.get("/history/{series_key}")
async def get_macro_history(
    series_key: str,
    period: str = "3mo"
):
    """
    Get historical data for a specific macro indicator.
    series_key: dxy, gold, yield_10y, yield_2y, real_yield_10y, yield_curve, breakeven_inflation
    period: 1mo, 3mo, 6mo, 1y, 2y
    """
    valid_keys = ["dxy", "gold", "yield_10y", "yield_2y", "real_yield_10y", "yield_curve", "breakeven_inflation"]
    if series_key not in valid_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid series key. Valid: {valid_keys}"
        )

    cache_key = f"macro:history:{series_key}:{period}"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "series": series_key, "source": "cache"}

    try:
        data = await fred_service.get_history(series_key, period=period)
        await cache.set(cache_key, data, ttl=3600)  # 1 hour cache
        return {"data": data, "series": series_key, "source": "fred"}
    except Exception as e:
        logger.error(f"Macro history error for {series_key}: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/fed-probability")
async def get_fed_probability():
    """
    Get CME FedWatch Fed rate cut probability.
    Scraped from CME Group.
    """
    cache_key = "macro:fed_probability"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    try:
        # CME FedWatch typically publishes probabilities as JSON/HTML
        # We'll do a simple scrape or return a static fallback
        # The actual data changes with market conditions
        import httpx
        url = "https://www.cmegroup.com/CBT200/content/dam/cmegroup/market-data/market-data-api/fedwatch/ff.json"

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                await cache.set(cache_key, data, ttl=3600)
                return {"data": data, "source": "cme"}

    except Exception as e:
        logger.warning(f"CME FedWatch fetch error (using fallback): {e}")

    # Fallback: return a placeholder with explanation
    fallback = {
        "note": "CME FedWatch API unavailable. Check cmegroup.com for live data.",
        "current_meeting": "FOMC",
        "probability_note": "Rate decisions based on Fed Funds Futures pricing.",
    }
    return {"data": fallback, "source": "fallback"}
