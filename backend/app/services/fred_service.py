"""
FRED API Service - US Macro Economic Data
==========================================
Data: DXY (Alpha Vantage), Gold (TwelveData), Treasury Yields (FRED), Real Yields

Data Sources:
- Gold: TwelveData XAU/USD (https://api.twelvedata.com/price?symbol=XAU/USD)
- DXY: Alpha Vantage EUR/USD exchange rate → DXY estimate
- Yields: FRED (DGS10, DGS2)
- Inflation: FRED (T10YIE)
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
        if value != value:
            return None
    except (TypeError, ValueError):
        pass
    return value


class FredService:

    BASE_URL = settings.FRED_BASE_URL
    TWELVE_DATA_URL = "https://api.twelvedata.com"
    ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

    # FRED Series IDs
    FRED_SERIES = {
        "yield_10y": "DGS10",
        "yield_2y": "DGS2",
        "breakeven_inflation": "T10YIE",
        "yield_curve": "T10Y2Y",
    }

    def __init__(self):
        self.fred_api_key = settings.FRED_API_KEY
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_KEY
        self.twelve_data_key = settings.TWELVE_DATA_KEY
        self.timeout = 30.0

    async def _fetch_fred_series(
        self,
        series_id: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict]:
        """Fetch time series observations from FRED."""
        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.fred_api_key,
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
            logger.error(f"FRED fetch error {series_id}: {e}")
            return []

    async def _fetch_twelve_data_price(self, symbol: str) -> Optional[float]:
        """Fetch price from TwelveData."""
        url = f"{self.TWELVE_DATA_URL}/price"
        params = {"symbol": symbol, "apikey": self.twelve_data_key}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                price = data.get("price")
                if price:
                    return float(price)
        except Exception as e:
            logger.error(f"TwelveData error {symbol}: {e}")
        return None

    async def _fetch_alpha_vantage_eurusd(self) -> Optional[float]:
        """Fetch EUR/USD exchange rate from Alpha Vantage."""
        url = self.ALPHA_VANTAGE_URL
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "USD",
            "to_currency": "EUR",
            "apikey": self.alpha_vantage_key,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                rate_data = data.get("Realtime Currency Exchange Rate", {})
                rate = rate_data.get("5. Exchange Rate")
                if rate:
                    return float(rate)
        except Exception as e:
            logger.error(f"Alpha Vantage EUR/USD error: {e}")
        return None

    def _eurusd_to_dxy(self, eurusd: float) -> float:
        """
        Estimate DXY from EUR/USD.
        DXY components (approximate weights):
        - EUR: 57.6%
        - JPY: 13.6%
        - GBP: 11.9%
        - CAD: 9.1%
        - SEK: 4.2%
        - CHF: 3.6%
        Simplified: DXY ≈ 50.14348112 × (EUR/USD)^-0.576 × (USD/JPY)^0.136 × ...
        We use simplified correlation: DXY ≈ 1 / EUR_USD × adjustment_factor
        Historical correlation: DXY ≈ (1/EURUSD) × ~115 (approximation)
        """
        if eurusd is None or eurusd == 0:
            return None
        # Simple linear regression approximation
        # Historical: when EUR/USD = 0.85, DXY ≈ 104; when EUR/USD = 1.20, DXY ≈ 95
        # DXY ≈ -50.5 * EUR/USD + 146.9 (r² ≈ 0.95)
        return -50.5 * eurusd + 146.9

    async def get_macro_snapshot(self) -> Dict[str, Any]:
        """
        Get complete macro snapshot for XAU/USD trading.
        """
        import asyncio

        end = datetime.now().strftime("%Y-%m-%d")
        start_3m = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Parallel fetch
        async def fetch_fred_obs(series_id: str) -> List[Dict]:
            return await self._fetch_fred_series(series_id, start_3m, end)

        gold_task = self._fetch_twelve_data_price("XAU/USD")
        eurusd_task = self._fetch_alpha_vantage_eurusd()

        fred_tasks = {k: v for k, v in self.FRED_SERIES.items()}
        fred_results = await asyncio.gather(
            *[fetch_fred_obs(sid) for sid in fred_tasks.values()],
            return_exceptions=True
        )
        fred_map = dict(zip(fred_tasks.keys(), fred_results))

        gold_price = await gold_task
        eurusd = await eurusd_task
        dxy_price = self._eurusd_to_dxy(eurusd)

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

        def prev_if_only_two(obs_list: List[Dict]) -> Optional[float]:
            """Get the value before the last one."""
            if not isinstance(obs_list, list) or len(obs_list) < 2:
                return None
            valid = [item for item in obs_list if isinstance(item, dict) and item.get("value") is not None]
            if len(valid) < 2:
                return None
            return valid[-2]["value"]

        yield_10y_val = latest(fred_map.get("yield_10y", []))
        yield_2y_val = latest(fred_map.get("yield_2y", []))
        breakeven_val = latest(fred_map.get("breakeven_inflation", []))

        yield_10y_prev = prev_if_only_two(fred_map.get("yield_10y", []))
        yield_2y_prev = prev_if_only_two(fred_map.get("yield_2y", []))

        # DXY from EUR/USD
        dxy_val = dxy_price
        dxy_prev = None  # can't get historical DXY cheaply

        # Gold from TwelveData (no historical in free price endpoint)
        gold_val = gold_price
        gold_prev = None

        # Derived values
        real_yield_10y = _nan_to_none(yield_10y_val - breakeven_val) if yield_10y_val and breakeven_val else None
        yield_curve = _nan_to_none(yield_10y_val - yield_2y_val) if yield_10y_val and yield_2y_val else None

        yield_10y_change = _nan_to_none(yield_10y_val - yield_10y_prev) if yield_10y_val and yield_10y_prev else None

        # Signals
        dxy_signal = "neutral"
        if dxy_val is not None and gold_val is not None:
            # Simplified: strong negative correlation when DXY up + gold down
            if eurusd is not None and eurusd < 0.90:  # Strong EUR weakness = strong DXY = gold pressure
                dxy_signal = "strong_bearish" if gold_val else "neutral"
            elif eurusd is not None and eurusd > 1.10:  # Strong EUR = weak DXY = gold support
                dxy_signal = "strong_bullish" if gold_val else "neutral"

        return {
            "timestamp": datetime.now().isoformat(),
            "dxy": {
                "value": _nan_to_none(dxy_val),
                "change": None,
                "change_pct": None,
                "source": "Alpha Vantage (EUR/USD derived)",
            },
            "gold": {
                "value": _nan_to_none(gold_val),
                "change_pct": None,
                "source": "TwelveData XAU/USD",
            },
            "yield_10y": {
                "value": _nan_to_none(yield_10y_val),
                "change": yield_10y_change,
                "source": "FRED DGS10",
            },
            "yield_2y": {
                "value": _nan_to_none(yield_2y_val),
                "source": "FRED DGS2",
            },
            "real_yield_10y": {
                "value": _nan_to_none(real_yield_10y),
                "description": "10Y Treasury - Breakeven Inflation",
                "source": "FRED (DGS10 - T10YIE)",
            },
            "yield_curve": {
                "value": _nan_to_none(yield_curve),
                "description": "10Y - 2Y Spread",
            },
            "breakeven_inflation": {
                "value": _nan_to_none(breakeven_val),
                "source": "FRED T10YIE",
            },
            "signals": {
                "gold_dxy_correlation": dxy_signal,
            },
        }

    async def get_history(
        self,
        series_key: str,
        period: str = "3mo",
        interval: str = "daily"
    ) -> List[Dict]:
        """
        Get historical data for a specific macro indicator.
        """
        end = datetime.now().strftime("%Y-%m-%d")
        days_map = {
            "1mo": 30, "3mo": 90, "6mo": 180,
            "1y": 365, "2y": 730, "5y": 1825
        }
        days = days_map.get(period, 90)
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        fred_series_map = {
            "yield_10y": "DGS10",
            "yield_2y": "DGS2",
            "breakeven_inflation": "T10YIE",
            "yield_curve": "T10Y2Y",
        }

        if series_key in fred_series_map:
            series_id = fred_series_map[series_key]
            url = f"{self.BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
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

        if series_key == "gold":
            price = await self._fetch_twelve_data_price("XAU/USD")
            if price:
                return [{"time": int(datetime.now().timestamp()), "date": datetime.now().strftime("%Y-%m-%d"), "value": round(price, 2)}]
            return []

        if series_key == "dxy":
            eurusd = await self._fetch_alpha_vantage_eurusd()
            if eurusd:
                dxy = self._eurusd_to_dxy(eurusd)
                return [{"time": int(datetime.now().timestamp()), "date": datetime.now().strftime("%Y-%m-%d"), "value": round(dxy, 2)}]
            return []

        return []


fred_service = FredService()
