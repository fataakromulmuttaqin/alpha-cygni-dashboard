"""
FRED API Service - US Macro Economic Data
==========================================
Data: DXY, Treasury Yields (2Y, 10Y), Real Yields, Gold Price

FRED API Docs: https://fred.stlouisfed.org/docs/api/fred/
Free tier: 120 requests/day, 1200 requests/month
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


def _nan_to_none(value: float) -> Optional[float]:
    """NaN → None for JSON serialization."""
    if value is None:
        return None
    try:
        if value != value:  # NaN check
            return None
    except (TypeError, ValueError):
        pass
    return value


class FredService:

    BASE_URL = settings.FRED_BASE_URL

    # FRED Series IDs (yields, inflation, rates)
    FRED_SERIES = {
        "yield_10y": "DGS10",            # 10-Year Treasury Constant Maturity Rate
        "yield_2y": "DGS2",              # 2-Year Treasury Constant Maturity Rate
        "breakeven_inflation": "T10YIE", # 10-Year Breakeven Inflation Rate
        "yield_curve": "T10Y2Y",         # 10-Year Treasury Minus 2-Year Treasury
        "fed_funds_rate": "FEDFUNDS",    # Effective Federal Funds Rate
    }

    # Yahoo Finance tickers (DXY and Gold from YF)
    YAHOO_TICKERS = {
        "dxy": "DX-Y.NYB",   # ICE US Dollar Index (DXY)
        "gold": "GC=F",      # Gold Futures (CME)
    }

    def __init__(self):
        self.api_key = settings.FRED_API_KEY
        self.timeout = 30.0

    async def _fetch_series_observations(
        self,
        series_id: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict]:
        """Fetch time series observations from FRED."""
        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                observations = data.get("observations", [])
                return [
                    {
                        "date": obs["date"],
                        "value": float(obs["value"]) if obs["value"] != "." else None,
                    }
                    for obs in observations
                ]
        except Exception as e:
            logger.error(f"FRED API error for {series_id}: {e}")
            return []

    async def get_latest_value(self, series_id: str) -> Optional[float]:
        """Get the most recent value for a series."""
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        obs = await self._fetch_series_observations(series_id, start, end)

        # Return last non-None value
        for item in reversed(obs):
            if item["value"] is not None:
                return item["value"]
        return None

    async def get_macro_snapshot(self) -> Dict[str, Any]:
        """
        Get complete macro snapshot for XAU/USD trading decisions.
        Returns: DXY (YF), Gold (YF), Yields (FRED), Real Yields, Yield Curve, Signals.
        """
        import asyncio
        import yfinance as yf

        end = datetime.now().strftime("%Y-%m-%d")
        start_3m = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Fetch FRED series (yields, inflation)
        async def fetch_fred_obs(series_id: str) -> List[Dict]:
            url = f"{self.BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start_3m,
                "observation_end": end,
            }
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    return [
                        {"date": obs["date"],
                         "value": float(obs["value"]) if obs["value"] != "." else None}
                        for obs in data.get("observations", [])
                    ]
            except Exception as e:
                logger.error(f"FRED fetch error {series_id}: {e}")
                return []

        # Fetch Yahoo Finance (DXY, Gold)
        def fetch_yahoo(ticker: str) -> List[Dict]:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="3mo", interval="1d")
                records = []
                for idx, row in df.iterrows():
                    records.append({
                        "date": idx.strftime("%Y-%m-%d"),
                        "value": round(float(row["Close"]), 4),
                    })
                return records
            except Exception as e:
                logger.error(f"Yahoo Finance error {ticker}: {e}")
                return []

        # Parallel fetch all
        fred_keys = list(self.FRED_SERIES.values())
        yahoo_tasks = {k: fetch_yahoo(v) for k, v in self.YAHOO_TICKERS.items()}

        fred_results = await asyncio.gather(
            *[fetch_fred_obs(sid) for sid in fred_keys],
            return_exceptions=True
        )

        fred_map = dict(zip(fred_keys, fred_results))
        yahoo_map = {k: fetch_yahoo(v) for k, v in self.YAHOO_TICKERS.items()}

        def latest(obs_list: List[Dict]) -> Optional[float]:
            if not isinstance(obs_list, list):
                return None
            for item in reversed(obs_list):
                if isinstance(item, dict) and item.get("value") is not None:
                    return item["value"]
            return None

        def prev(obs_list: List[Dict]) -> Optional[float]:
            if not isinstance(obs_list, list) or len(obs_list) < 2:
                return None
            found_current = False
            for item in reversed(obs_list):
                if isinstance(item, dict) and item.get("value") is not None:
                    if found_current:
                        return item["value"]
                    found_current = True
            return None

        # Extract values
        dxy_list = yahoo_map.get("dxy", [])
        gold_list = yahoo_map.get("gold", [])
        y10_list = fred_map.get("DGS10", [])
        y2_list = fred_map.get("DGS2", [])
        bei_list = fred_map.get("T10YIE", [])

        dxy_val = latest(dxy_list)
        gold_val = latest(gold_list)
        yield_10y_val = latest(y10_list)
        yield_2y_val = latest(y2_list)
        breakeven_val = latest(bei_list)

        dxy_prev_val = prev(dxy_list)
        yield_10y_prev_val = prev(y10_list)
        gold_prev_val = prev(gold_list)

        # Derived
        real_yield_10y = _nan_to_none(yield_10y_val - breakeven_val) if yield_10y_val and breakeven_val else None
        yield_curve = _nan_to_none(yield_10y_val - yield_2y_val) if yield_10y_val and yield_2y_val else None

        dxy_change = _nan_to_none(dxy_val - dxy_prev_val) if dxy_val and dxy_prev_val else None
        yield_10y_change = _nan_to_none(yield_10y_val - yield_10y_prev_val) if yield_10y_val and yield_10y_prev_val else None
        gold_change_pct = _nan_to_none(((gold_val - gold_prev_val) / gold_prev_val * 100) if gold_val and gold_prev_val else None)

        # Signals
        dxy_signal = "strong_bullish" if (dxy_change is not None and gold_change_pct is not None and dxy_change < 0 and gold_change_pct > 0) else \
                     "strong_bearish" if (dxy_change is not None and gold_change_pct is not None and dxy_change > 0 and gold_change_pct < 0) else \
                     "neutral"

        return {
            "timestamp": datetime.now().isoformat(),
            "dxy": {
                "value": _nan_to_none(dxy_val),
                "change": _nan_to_none(dxy_change),
                "change_pct": _nan_to_none((dxy_change / dxy_prev_val * 100) if dxy_change and dxy_prev_val else None),
            },
            "gold": {
                "value": _nan_to_none(gold_val),
                "change_pct": gold_change_pct,
            },
            "yield_10y": {
                "value": _nan_to_none(yield_10y_val),
                "change": yield_10y_change,
            },
            "yield_2y": {
                "value": _nan_to_none(yield_2y_val),
            },
            "real_yield_10y": {
                "value": _nan_to_none(real_yield_10y),
                "description": "10Y Treasury - Breakeven Inflation",
            },
            "yield_curve": {
                "value": _nan_to_none(yield_curve),
                "description": "10Y - 2Y Spread",
            },
            "breakeven_inflation": {
                "value": _nan_to_none(breakeven_val),
            },
            "signals": {
                "gold_dxy_correlation": dxy_signal,
            },
        }

    async def _parallel_fetch(self, client: httpx.AsyncClient, tasks: Dict[str, tuple]) -> Dict:
        """Run multiple fetch tasks in parallel."""
        async def fetch_task(key: str, url: str, params: dict):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return key, data.get("observations", [])
            except Exception as e:
                logger.error(f"FRED parallel fetch error for {key}: {e}")
                return key, []

        async def fetch_series(key: str, series_id: str, start: str, end: str):
            url = f"{self.BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start,
                "observation_end": end,
            }
            return await fetch_task(key, url, params)

        import asyncio
        coros = [fetch_series(k, v[0], v[1], v[2]) for k, v in tasks.items()]
        results_array = await asyncio.gather(*coros, return_exceptions=True)

        results = {}
        for item in results_array:
            if isinstance(item, tuple) and len(item) == 2:
                key, val = item
                results[key] = val
        return results

    async def get_history(
        self,
        series_key: str,
        period: str = "3mo",
        interval: str = "daily"
    ) -> List[Dict]:
        """
        Get historical data for a specific macro indicator.
        series_key: dxy, gold, yield_10y, yield_2y, real_yield_10y, yield_curve, breakeven_inflation
        period: 1mo, 3mo, 6mo, 1y, 2y
        """
        import yfinance as yf

        end = datetime.now().strftime("%Y-%m-%d")
        days_map = {
            "1mo": 30, "3mo": 90, "6mo": 180,
            "1y": 365, "2y": 730, "5y": 1825
        }
        days = days_map.get(period, 90)
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # FRED series
        fred_series = {
            "yield_10y": "DGS10",
            "yield_2y": "DGS2",
            "breakeven_inflation": "T10YIE",
            "yield_curve": "T10Y2Y",
        }

        # Yahoo Finance series
        yahoo_series = {
            "dxy": "DX-Y.NYB",
            "gold": "GC=F",
        }

        series_id = fred_series.get(series_key) or yahoo_series.get(series_key)
        if not series_id:
            return []

        # Fetch from FRED
        if series_key in fred_series:
            url = f"{self.BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start,
                "observation_end": end,
            }
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    records = []
                    for obs in data.get("observations", []):
                        if obs["value"] != ".":
                            dt = datetime.strptime(obs["date"], "%Y-%m-%d")
                            records.append({
                                "time": int(dt.timestamp()),
                                "date": obs["date"],
                                "value": round(float(obs["value"]), 4),
                            })
                    return records
            except Exception as e:
                logger.error(f"FRED history error {series_key}: {e}")
                return []

        # Fetch from Yahoo Finance
        if series_key in yahoo_series:
            try:
                stock = yf.Ticker(series_id)
                df = stock.history(period=period, interval="1d")
                records = []
                for idx, row in df.iterrows():
                    dt_utc = idx.tz_convert("UTC") if idx.tz else idx
                    records.append({
                        "time": int(dt_utc.timestamp()),
                        "date": idx.strftime("%Y-%m-%d"),
                        "value": round(float(row["Close"]), 4),
                    })
                return records
            except Exception as e:
                logger.error(f"Yahoo Finance history error {series_key}: {e}")
                return []

        return []


# Singleton instance
fred_service = FredService()
