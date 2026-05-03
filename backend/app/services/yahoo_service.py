import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from app.utils.ticker_map import get_yahoo_ticker, FOREX_PAIRS, IDX_INDICES
import logging

logger = logging.getLogger(__name__)


class YahooFinanceService:

    async def get_stock_quote(self, ticker: str) -> Dict[str, Any]:
        """Ambil quote real-time (delayed ~15 menit) untuk satu saham"""
        try:
            yahoo_ticker = get_yahoo_ticker(ticker)
            stock = yf.Ticker(yahoo_ticker)
            info = stock.info

            # Fast quote: gunakan fast_info untuk lebih cepat
            fast = stock.fast_info

            return {
                "ticker": ticker,
                "yahoo_symbol": yahoo_ticker,
                "name": info.get("longName", ticker),
                "price": fast.last_price,
                "open": fast.open,
                "high": fast.day_high,
                "low": fast.day_low,
                "prev_close": fast.previous_close,
                "volume": fast.three_month_average_volume,
                "market_cap": fast.market_cap,
                "change": fast.last_price - fast.previous_close if fast.previous_close else 0,
                "change_pct": ((fast.last_price - fast.previous_close) / fast.previous_close * 100)
                               if fast.previous_close else 0,
                "currency": "IDR",
                "exchange": "IDX",
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            raise

    async def get_historical_data(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> List[Dict]:
        """Ambil data OHLCV historis"""
        try:
            yahoo_ticker = get_yahoo_ticker(ticker)
            stock = yf.Ticker(yahoo_ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                return []

            # Konversi ke format yang bisa dipakai chart
            records = []
            for idx, row in df.iterrows():
                records.append({
                    "time": int(idx.timestamp()),        # Unix timestamp (untuk Lightweight Charts)
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                })
            return records
        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {e}")
            raise

    async def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Ambil informasi fundamental saham"""
        try:
            yahoo_ticker = get_yahoo_ticker(ticker)
            stock = yf.Ticker(yahoo_ticker)
            info = stock.info

            return {
                "ticker": ticker,
                "name": info.get("longName", ""),
                "description": info.get("longBusinessSummary", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "employees": info.get("fullTimeEmployees", 0),
                "website": info.get("website", ""),
                # Fundamental metrics
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "peg_ratio": info.get("pegRatio"),
                "debt_to_equity": info.get("debtToEquity"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "profit_margin": info.get("profitMargins"),
                "gross_margin": info.get("grossMargins"),
                "operating_margin": info.get("operatingMargins"),
                "revenue": info.get("totalRevenue"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "dividend_yield": info.get("dividendYield"),
                "dividend_rate": info.get("dividendRate"),
                "beta": info.get("beta"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "avg_volume_3m": info.get("averageVolume"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "book_value": info.get("bookValue"),
                "earnings_per_share": info.get("trailingEps"),
            }
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            raise

    async def get_multiple_quotes(self, tickers: List[str]) -> List[Dict]:
        """Ambil quote untuk banyak saham sekaligus (lebih efisien)"""
        try:
            yahoo_tickers = [get_yahoo_ticker(t) for t in tickers]
            symbols_str = " ".join(yahoo_tickers)

            # Download sekaligus
            data = yf.download(
                symbols_str,
                period="2d",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False
            )

            results = []
            for ticker, yahoo_sym in zip(tickers, yahoo_tickers):
                try:
                    if len(tickers) == 1:
                        ticker_data = data
                    else:
                        ticker_data = data[yahoo_sym]

                    if ticker_data.empty:
                        continue

                    latest = ticker_data.iloc[-1]
                    prev = ticker_data.iloc[-2] if len(ticker_data) > 1 else latest

                    price = float(latest["Close"])
                    prev_close = float(prev["Close"])
                    change = price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0

                    results.append({
                        "ticker": ticker,
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                        "volume": int(latest["Volume"]),
                        "high": round(float(latest["High"]), 2),
                        "low": round(float(latest["Low"]), 2),
                    })
                except Exception as inner_e:
                    logger.warning(f"Skip {ticker}: {inner_e}")
                    continue

            return results
        except Exception as e:
            logger.error(f"Error in batch quotes: {e}")
            raise

    async def get_forex_rate(self, pair: str) -> Dict[str, Any]:
        """Ambil kurs forex"""
        try:
            yahoo_sym = FOREX_PAIRS.get(pair, f"{pair.replace('/', '')}=X")
            ticker = yf.Ticker(yahoo_sym)
            fast = ticker.fast_info

            return {
                "pair": pair,
                "rate": fast.last_price,
                "change": fast.last_price - fast.previous_close if fast.previous_close else 0,
                "change_pct": ((fast.last_price - fast.previous_close) / fast.previous_close * 100)
                               if fast.previous_close else 0,
                "high": fast.day_high,
                "low": fast.day_low,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error fetching forex {pair}: {e}")
            raise

    async def get_index_data(self, index_code: str) -> Dict[str, Any]:
        """Ambil data indeks (IHSG, LQ45, dll)"""
        yahoo_sym = IDX_INDICES.get(index_code, index_code)
        return await self.get_stock_quote(yahoo_sym.replace("^", ""))


yahoo_service = YahooFinanceService()
