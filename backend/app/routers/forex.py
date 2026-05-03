from fastapi import APIRouter, HTTPException, Query
from app.services.yahoo_service import yahoo_service
from app.services.fallback_service import fallback_service
from app.services.cache_service import cache
from app.utils.ticker_map import FOREX_PAIRS
from app.utils.technical_indicators import add_technical_indicators
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/pairs")
async def get_forex_pairs():
    """Daftar pasangan forex yang tersedia"""
    return {"pairs": list(FOREX_PAIRS.keys())}


@router.get("/rates")
async def get_all_forex_rates():
    """Kurs semua pasangan forex USD"""
    cache_key = "forex:all_rates"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    results = []
    for pair in FOREX_PAIRS.keys():
        try:
            rate = await yahoo_service.get_forex_rate(pair)
            results.append(rate)
        except Exception as e:
            logger.warning(f"Failed to get {pair}: {e}")
            # Coba fallback Twelve Data
            parts = pair.split("/")
            if len(parts) == 2:
                fallback = await fallback_service.get_forex_twelve_data(parts[0], parts[1])
                if fallback:
                    results.append({"pair": pair, **fallback})

    await cache.set(cache_key, results, ttl=60)
    return {"data": results, "source": "yahoo+fallback"}


@router.get("/history")
async def get_forex_history(
    pair: str = Query(..., description="Forex pair, e.g. XAU/USD, EUR/USD"),
    period: str = Query("1y"),
    interval: str = Query("1d")
):
    """Data historis pasangan forex"""
    pair_formatted = pair.upper().replace("-", "/")
    yahoo_sym = FOREX_PAIRS.get(pair_formatted, f"{pair.replace('-', '')}=X")

    cache_key = f"forex:history:{pair}:{period}:{interval}"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "pair": pair_formatted, "source": "cache"}

    try:
        import yfinance as yf
        ticker = yf.Ticker(yahoo_sym)
        df = ticker.history(period=period, interval=interval)

        records = []
        for idx, row in df.iterrows():
            records.append({
                "time": int(idx.timestamp()),
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
            })

        enriched = add_technical_indicators(records)
        await cache.set(cache_key, enriched, ttl=300)
        return {"data": enriched, "pair": pair_formatted, "source": "yahoo"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
