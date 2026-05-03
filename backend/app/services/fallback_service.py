import httpx
from datetime import datetime, timedelta
from app.config import settings
import logging
import csv
import io

logger = logging.getLogger(__name__)


class FallbackDataService:
    """
    Fallback ketika yfinance gagal.
    Urutan: 1. Stooq → 2. Alpha Vantage → 3. Twelve Data
    """

    async def get_historical_stooq(self, ticker: str, days: int = 365):
        """Ambil data dari stooq.com via CSV endpoint langsung (GRATIS, tanpa API key)"""
        try:
            end = datetime.now()
            start = end - timedelta(days=days)

            # Stooq CSV endpoint - format: https://stooq.com/q/d/l/?s={ticker}&d1={start}&d2={end}
            start_str = start.strftime("%Y%m%d")
            end_str = end.strftime("%Y%m%d")

            url = f"https://stooq.com/q/d/l/?s={ticker.lower()}&d1={start_str}&d2={end_str}"

            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(url)
                r.raise_for_status()

            # Parse CSV
            lines = r.text.strip().split('\n')
            if len(lines) <= 1:
                return []

            reader = csv.reader(io.StringIO(r.text))
            header = next(reader)

            # Find column indices
            date_idx = header.index('Date') if 'Date' in header else 0
            open_idx = header.index('Open') if 'Open' in header else 1
            high_idx = header.index('High') if 'High' in header else 2
            low_idx = header.index('Low') if 'Low' in header else 3
            close_idx = header.index('Close') if 'Close' in header else 4
            volume_idx = header.index('Volume') if 'Volume' in header else 5

            records = []
            for row in reader:
                if len(row) < 6:
                    continue
                try:
                    date = row[date_idx]
                    records.append({
                        "time": int(datetime.strptime(date, "%Y-%m-%d").timestamp()),
                        "date": date,
                        "open": round(float(row[open_idx]), 2),
                        "high": round(float(row[high_idx]), 2),
                        "low": round(float(row[low_idx]), 2),
                        "close": round(float(row[close_idx]), 2),
                        "volume": int(float(row[volume_idx])) if row[volume_idx] else 0,
                    })
                except (ValueError, IndexError):
                    continue

            # Stooq returns newest first, reverse to oldest first
            records.reverse()
            return records

        except Exception as e:
            logger.error(f"Stooq fallback failed for {ticker}: {e}")
            return []

    async def get_quote_alpha_vantage(self, ticker: str) -> dict:
        """Ambil quote dari Alpha Vantage (25 req/hari gratis)"""
        if not settings.ALPHA_VANTAGE_KEY:
            return {}

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": settings.ALPHA_VANTAGE_KEY,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(url, params=params)
                data = r.json()

            quote = data.get("Global Quote", {})
            if not quote:
                return {}

            price = float(quote.get("05. price", 0))
            prev = float(quote.get("08. previous close", 0))

            return {
                "price": price,
                "change": price - prev,
                "change_pct": float(quote.get("10. change percent", "0%").replace("%", "")),
                "volume": int(quote.get("06. volume", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "source": "alphavantage",
            }
        except Exception as e:
            logger.error(f"Alpha Vantage fallback failed: {e}")
            return {}

    async def get_forex_twelve_data(self, from_sym: str, to_sym: str) -> dict:
        """Ambil forex dari Twelve Data (800 req/hari gratis)"""
        if not settings.TWELVE_DATA_KEY:
            return {}

        try:
            url = "https://api.twelvedata.com/price"
            params = {
                "symbol": f"{from_sym}/{to_sym}",
                "apikey": settings.TWELVE_DATA_KEY,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(url, params=params)
                data = r.json()

            return {
                "rate": float(data.get("price", 0)),
                "source": "twelvedata",
            }
        except Exception as e:
            logger.error(f"Twelve Data fallback failed: {e}")
            return {}


fallback_service = FallbackDataService()
