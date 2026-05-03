from fastapi import APIRouter, Query
from app.services.cache_service import cache
import feedparser
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "investing_commodities": "https://www.investing.com/rss/commodities.rss",
    "investing_forex": "https://www.investing.com/rss/forex.rss",
    "reuters_business": "https://feeds.reuters.com/reuters/businessNews",
}

# Keywords for gold/precious metals focus
GOLD_KEYWORDS = [
    "gold", "xau", "silver", "platinum", "palladium",
    "precious metals", "gold price", "gold market",
    "fed rate", "federal reserve", "treasury yield",
    "inflation", "deflation", "dollar index", "dxy",
    "safe haven", "central bank gold", "gold standard",
    "spot gold", "gold futures", "comex gold",
    "usd", "dollar", "currency", "forex",
    "geopoliti", "recession", "crisis",
]


def _matches_gold_keywords(text: str) -> bool:
    """Check if text contains any gold-related keyword (case-insensitive)."""
    if not text:
        return False
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in GOLD_KEYWORDS)


@router.get("/")
async def get_market_news(
    source: str = Query("all", description="all, kitco, reuters_commodities, mining, investing"),
    limit: int = Query(20, le=50),
    gold_focus: bool = Query(True, description="Filter to gold/precious metals related news"),
):
    """Berita pasar dari RSS feed — default fokus gold/XAU/USD/commodities."""
    cache_key = f"news:{source}:{limit}:gold{int(gold_focus)}"
    cached = await cache.get(cache_key)
    if cached:
        return {"data": cached, "source": "cache"}

    feeds_to_fetch = RSS_FEEDS if source == "all" else {source: RSS_FEEDS.get(source, "")}

    all_news = []
    for source_name, url in feeds_to_fetch.items():
        if not url:
            continue
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit // len(feeds_to_fetch) + 2]:
                title = entry.get("title", "")
                # Always include if gold_focus=False, else filter by keywords
                if gold_focus and not _matches_gold_keywords(title):
                    continue
                all_news.append({
                    "title": title,
                    "summary": entry.get("summary", "")[:300],
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": source_name,
                })
        except Exception as e:
            logger.warning(f"RSS failed for {source_name}: {e}")

    # Sort by published (terbaru dulu) — strip timezone for safe parse
    import email.utils
    def parse_date(s):
        try:
            return email.utils.parsedate_to_datetime(s)
        except Exception:
            return datetime.min

    all_news.sort(key=lambda x: parse_date(x["published"]), reverse=True)
    all_news = all_news[:limit]

    await cache.set(cache_key, all_news, ttl=600)
    return {"data": all_news, "count": len(all_news)}
