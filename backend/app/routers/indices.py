from fastapi import APIRouter, HTTPException
from app.services.yahoo_service import yahoo_service
from app.services.cache_service import cache
from app.utils.ticker_map import IDX_INDICES
import yfinance as yf
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_all_indices():
    """Semua indeks IDX"""
    cache_key = "indices:all"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    results = []
    for name, symbol in IDX_INDICES.items():
        try:
            ticker = yf.Ticker(symbol)
            fast = ticker.fast_info
            prev = ticker.history(period="2d")

            price = fast.last_price
            prev_close = float(prev["Close"].iloc[-2]) if len(prev) > 1 else price
            change = price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0

            results.append({
                "name": name,
                "symbol": symbol,
                "price": round(price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "high": round(fast.day_high, 2),
                "low": round(fast.day_low, 2),
            })
        except Exception as e:
            logger.warning(f"Error fetching index {name}: {e}")

    await cache.set(cache_key, results, ttl=120)
    return {"data": results, "source": "yahoo"}


@router.get("/{index_code}/history")
async def get_index_history(index_code: str, period: str = "1y", interval: str = "1d"):
    """Historis indeks"""
    symbol = IDX_INDICES.get(index_code.upper())
    if not symbol:
        raise HTTPException(status_code=404, detail=f"Index {index_code} not found")

    cache_key = f"index:history:{index_code}:{period}:{interval}"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        records = [
            {
                "time": int(idx.timestamp()),
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            }
            for idx, row in df.iterrows()
        ]

        await cache.set(cache_key, records, ttl=300)
        return {"data": records, "index": index_code, "source": "yahoo"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
