import requests
import re

def get_latest_crypto_news(limit=3):
    """Fetch latest crypto news headlines from CoinDesk RSS (free, no API key needed)."""
    try:
        resp = requests.get("https://www.coindesk.com/arc/outboundfeeds/rss/", timeout=10)
        resp.raise_for_status()
        content = resp.text

        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", content)
        titles = [t for t in titles if t.strip() and "CoinDesk" not in t][:limit]

        if titles:
            return titles
        return []
    except Exception as e:
        print(f"News fetch failed: {e}")
        return []
