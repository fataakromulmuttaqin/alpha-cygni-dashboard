"""
Technical Indicators: SMA & RSI
Calculated from OHLCV data before sending to frontend.
"""
from typing import List, Dict, Any


def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Simple Moving Average — returns list matching price length (NaN for insufficient data)"""
    if len(prices) < period:
        return [float("nan")] * len(prices)

    sma = []
    for i in range(len(prices)):
        if i < period - 1:
            sma.append(float("nan"))
        else:
            avg = sum(prices[i - period + 1 : i + 1]) / period
            sma.append(round(avg, 4))
    return sma


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """Relative Strength Index — 14-period default"""
    if len(prices) < period + 1:
        return [float("nan")] * len(prices)

    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    rsi = [float("nan")] * period  # pad start

    avg_gain = sum(d for d in deltas[:period] if d > 0) / period
    avg_loss = sum(-d for d in deltas[:period] if d < 0) / period

    for i in range(period, len(deltas)):
        gain = deltas[i] if deltas[i] > 0 else 0
        loss = -deltas[i] if deltas[i] < 0 else 0

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            rsi.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi.append(round(100 - 100 / (1 + rs), 2))

    # Align: rsi[0] corresponds to prices[1], so pad front
    rsi = [float("nan")] + rsi
    return rsi


def _nan_to_none(value: float) -> float | None:
    """Convert NaN to None for JSON serialization, keep finite values as-is."""
    if value is None:
        return None
    try:
        if value != value:  # NaN check
            return None
    except (TypeError, ValueError):
        pass
    return value


def add_technical_indicators(records: List[Dict[str, Any]], period_sma_short: int = 20, period_sma_long: int = 50) -> List[Dict[str, Any]]:
    """
    Inject SMA20, SMA50, RSI14 into each OHLCV record.
    Returns new list with extra keys: sma_20, sma_50, rsi_14
    """
    if not records:
        return records

    closes = [r["close"] for r in records]
    sma20 = calculate_sma(closes, period_sma_short)
    sma50 = calculate_sma(closes, period_sma_long)
    rsi14 = calculate_rsi(closes, 14)

    enriched = []
    for i, rec in enumerate(records):
        enriched_rec = {**rec}
        enriched_rec["sma_20"] = _nan_to_none(sma20[i]) if i < len(sma20) else None
        enriched_rec["sma_50"] = _nan_to_none(sma50[i]) if i < len(sma50) else None
        enriched_rec["rsi_14"] = _nan_to_none(rsi14[i]) if i < len(rsi14) else None
        enriched.append(enriched_rec)

    return enriched
