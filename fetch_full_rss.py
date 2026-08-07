import feedparser
import requests
import trafilatura
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import time
import hashlib
import os

SOURCE_FEED = "https://rss.app/feeds/8PpPUNyYwHkYhkvV.xml"
OUTPUT_PATH = "docs/feed.xml"
MAX_ITEMS = 30
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

def fetch_full_text(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        text = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
        return text
    except Exception as e:
        print(f"extract failed for {url}: {e}")
        return None

def main():
    os.makedirs("docs", exist_ok=True)
    parsed = feedparser.parse(SOURCE_FEED)

    fg = FeedGenerator()
    fg.title("KBS 뉴스 전체기사 (전문)")
    fg.link(href="https://news.kbs.co.kr/news/pc/main/main.html", rel="alternate")
    fg.description("KBS 뉴스 전체기사 - 전문 추출 피드")
    fg.language("ko")

    for entry in parsed.entries[:MAX_ITEMS]:
        link = entry.get("link")
        title = entry.get("title", "")
        summary = entry.get("summary", "")

        full_text = fetch_full_text(link) if link else None
        content = full_text if full_text else summary

        fe = fg.add_entry()
        fe.title(title)
        fe.link(href=link)
        fe.description(content)
        guid = hashlib.md5((link or title).encode()).hexdigest()
        fe.guid(guid, permalink=False)

        if entry.get("published_parsed"):
            pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            fe.pubDate(pub_dt)

        time.sleep(1)

    fg.rss_file(OUTPUT_PATH)

if __name__ == "__main__":
    main()
