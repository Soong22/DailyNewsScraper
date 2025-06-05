# Modules/RssParser.py

import json, os, feedparser
from datetime import datetime, timedelta

PROCESSED_FILE = "processed.json"

# (1) RSS_URL→사이트명 매핑 추가
RSS_FEED_SITES = {
    "https://www.itworld.co.kr/feed/": "ITWorld",
    "https://yozm.wishket.com/magazine/feed/": "요즘IT",
    "https://bloter.net/rss/news": "블로터",
    # "https://moji.or.kr/feed/": "뭐지",  # 필요 시 추가
}

def load_processed_links(path: str = PROCESSED_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("processed_links", [])

def save_processed_links(links, last_run: str, path: str = PROCESSED_FILE):
    data = {"processed_links": links, "last_run": last_run}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_rss_feeds(rss_urls):
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        site_name = RSS_FEED_SITES.get(url, "Unknown")  # 맵핑이 없으면 "Unknown"
        for entry in feed.entries:
            pub = None
            # (a) published_parsed
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6]).date()
            # (b) updated_parsed
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub = datetime(*entry.updated_parsed[:6]).date()
            # (c) published 문자열을 여러 포맷으로 시도
            elif hasattr(entry, "published"):
                for fmt in (
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S"
                ):
                    try:
                        pub = datetime.strptime(entry.published, fmt).date()
                        break
                    except:
                        continue
            entries.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "published": pub,
                "site": site_name  # (2) site 필드 추가
            })
    return entries

def filter_recent_articles(all_entries, days=3):
    today = datetime.now().date()
    cutoff = today - timedelta(days=days)
    return [e for e in all_entries if e["published"] and e["published"] >= cutoff]

def get_unprocessed_candidates(rss_urls, days, processed_links):
    all_entries = parse_rss_feeds(rss_urls)
    recent = filter_recent_articles(all_entries, days)
    candidates = []
    idx = 1
    for entry in recent:
        if entry["link"] not in processed_links:
            candidates.append({
                "index": idx,
                "title": entry["title"],
                "link": entry["link"],
                "published": entry["published"],
                "site": entry["site"]  # (3) site도 넘겨줌
            })
            idx += 1
    return candidates
