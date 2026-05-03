from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.yahoo_service import yahoo_service
from app.services.fallback_service import fallback_service
from app.services.cache_service import cache
from app.utils.ticker_map import IDX_TICKERS, get_all_idx_tickers
from app.utils.technical_indicators import add_technical_indicators
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/list")
async def get_stock_list():
    """Daftar semua saham IDX yang tersedia di dashboard ini"""
    return {"tickers": list(IDX_TICKERS.keys()), "total": len(IDX_TICKERS)}


@router.get("/quotes")
async def get_all_quotes(
    tickers: Optional[str] = Query(None, description="Comma-separated tickers, e.g. BBCA,BBRI,TLKM")
):
    """Ambil quote untuk semua saham atau subset tertentu"""
    cache_key = f"quotes:{tickers or 'all'}"

    # Cek cache dulu
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    ticker_list = tickers.split(",") if tickers else list(IDX_TICKERS.keys())

    try:
        data = await yahoo_service.get_multiple_quotes(ticker_list)
        await cache.set(cache_key, data, ttl=60)  # Cache 1 menit untuk quotes
        return {"data": data, "source": "yahoo"}
    except Exception as e:
        logger.error(f"Failed to get quotes: {e}")
        raise HTTPException(status_code=503, detail=f"Data unavailable: {str(e)}")


@router.get("/{ticker}/quote")
async def get_stock_quote(ticker: str):
    """Quote untuk satu saham"""
    cache_key = f"quote:{ticker.upper()}"
    cached = await cache.get(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    try:
        data = await yahoo_service.get_stock_quote(ticker)
        await cache.set(cache_key, data, ttl=60)
        return {**data, "source": "yahoo"}
    except Exception as e:
        # Coba fallback Alpha Vantage
        from app.utils.ticker_map import get_yahoo_ticker
        yahoo_sym = get_yahoo_ticker(ticker)
        fallback = await fallback_service.get_quote_alpha_vantage(yahoo_sym)
        if fallback:
            return {**fallback, "ticker": ticker}
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{ticker}/history")
async def get_stock_history(
    ticker: str,
    period: str = Query("1y", description="1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"),
    interval: str = Query("1d", description="1d, 1wk, 1mo")
):
    """Data historis OHLCV untuk charting"""
    cache_key = f"history:{ticker.upper()}:{period}:{interval}"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "ticker": ticker, "source": "cache"}

    try:
        data = await yahoo_service.get_historical_data(ticker, period, interval)
        enriched = add_technical_indicators(data)
        await cache.set(cache_key, enriched, ttl=300)  # Cache 5 menit
        return {"data": enriched, "ticker": ticker, "source": "yahoo"}
    except Exception as e:
        # Fallback ke stooq
        logger.warning(f"yfinance failed for {ticker}, trying stooq...")
        from app.utils.ticker_map import get_yahoo_ticker
        data = await fallback_service.get_historical_stooq(get_yahoo_ticker(ticker))
        if data:
            enriched = add_technical_indicators(data)
            return {"data": enriched, "ticker": ticker, "source": "stooq"}
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{ticker}/info")
async def get_stock_info(ticker: str):
    """Informasi fundamental saham"""
    cache_key = f"info:{ticker.upper()}"
    cached = await cache.get(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    try:
        data = await yahoo_service.get_stock_info(ticker)
        await cache.set(cache_key, data, ttl=3600)  # Cache 1 jam (fundamental jarang berubah)
        return {**data, "source": "yahoo"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{ticker}/financials")
async def get_stock_financials(ticker: str):
    """Laporan keuangan: income statement, balance sheet, cash flow"""
    cache_key = f"financials:{ticker.upper()}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    try:
        from app.utils.ticker_map import get_yahoo_ticker
        import yfinance as yf
        stock = yf.Ticker(get_yahoo_ticker(ticker))

        income_stmt = stock.financials.to_dict() if stock.financials is not None else {}
        balance_sheet = stock.balance_sheet.to_dict() if stock.balance_sheet is not None else {}
        cash_flow = stock.cashflow.to_dict() if stock.cashflow is not None else {}

        data = {
            "ticker": ticker,
            "income_statement": {str(k): v for k, v in income_stmt.items()},
            "balance_sheet": {str(k): v for k, v in balance_sheet.items()},
            "cash_flow": {str(k): v for k, v in cash_flow.items()},
        }
        await cache.set(cache_key, data, ttl=86400)  # Cache 24 jam
        return data
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
