from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.yahoo_service import yahoo_service
from app.services.cache_service import cache
from app.utils.ticker_map import IDX_TICKERS
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def screener(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    min_market_cap: Optional[float] = Query(None, description="Minimum market cap in IDR"),
    max_pe: Optional[float] = Query(None, description="Maximum P/E ratio"),
    min_roe: Optional[float] = Query(None, description="Minimum ROE"),
    sort_by: str = Query("market_cap", description="Sort by: market_cap, pe, roe, change_pct"),
    order: str = Query("desc", description="Sort order: asc, desc"),
    limit: int = Query(20, le=100, description="Max results")
):
    """
    Stock screener - filter saham berdasarkan kriteria fundamental.
    Data dari Yahoo Finance (delayed ~15 menit).
    """
    cache_key = f"screener:{sector}:{min_market_cap}:{max_pe}:{min_roe}:{sort_by}:{order}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    try:
        # Ambil semua ticker
        ticker_list = list(IDX_TICKERS.keys())

        # Ambil info fundamental untuk semua ticker
        results = []
        for ticker in ticker_list:
            try:
                info = await yahoo_service.get_stock_info(ticker)

                # Apply filters
                if sector and info.get("sector", "").lower() != sector.lower():
                    continue

                market_cap = info.get("market_cap") or 0
                if min_market_cap and market_cap < min_market_cap:
                    continue

                pe = info.get("pe_ratio") or 0
                if max_pe and (pe == 0 or pe > max_pe):
                    continue

                roe = info.get("roe") or 0
                if min_roe and roe < min_roe:
                    continue

                results.append({
                    "ticker": ticker,
                    "name": info.get("name", ticker),
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                    "market_cap": market_cap,
                    "pe_ratio": pe,
                    "pb_ratio": info.get("pb_ratio"),
                    "roe": roe,
                    "revenue": info.get("revenue"),
                    "dividend_yield": info.get("dividend_yield"),
                    "beta": info.get("beta"),
                    "52w_high": info.get("52w_high"),
                    "52w_low": info.get("52w_low"),
                })
            except Exception as e:
                logger.warning(f"Skip {ticker} in screener: {e}")
                continue

        # Sort
        reverse = order == "desc"
        if sort_by == "market_cap":
            results.sort(key=lambda x: x.get("market_cap") or 0, reverse=reverse)
        elif sort_by == "pe":
            results.sort(key=lambda x: x.get("pe_ratio") or 0, reverse=reverse)
        elif sort_by == "roe":
            results.sort(key=lambda x: x.get("roe") or 0, reverse=reverse)

        results = results[:limit]

        data = {"results": results, "total": len(results)}
        await cache.set(cache_key, data, ttl=300)
        return {**data, "source": "yahoo"}

    except Exception as e:
        logger.error(f"Screener error: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/sectors")
async def get_sectors():
    """Daftar sektor yang tersedia"""
    return {"sectors": [
        "Financial Services",
        "Communication Services",
        "Energy",
        "Consumer Cyclical",
        "Consumer Defensive",
        "Industrials",
        "Real Estate",
        "Technology",
        "Healthcare",
        "Basic Materials",
    ]}
