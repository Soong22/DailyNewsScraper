# Modules/RssParser.py

import json, os, feedparser
from datetime import datetime, timedelta

PROCESSED_FILE = "processed.json"

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
        for entry in feed.entries:
            pub = None
            # (1) published_parsed 우선 시도
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6]).date()
            # (2) updated_parsed 시도
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub = datetime(*entry.updated_parsed[:6]).date()
            # (3) published 문자열을 다양한 포맷으로 파싱 시도
            elif hasattr(entry, "published"):
                for fmt in (
                    "%a, %d %b %Y %H:%M:%S %z",   # ex. Tue, 10 Jun 2025 12:34:56 +0900
                    "%Y-%m-%dT%H:%M:%SZ",        # ex. 2025-06-10T03:22:10Z
                    "%Y-%m-%d %H:%M:%S"          # ex. 2025-06-10 12:34:56
                ):
                    try:
                        pub = datetime.strptime(entry.published, fmt).date()
                        break
                    except:
                        continue
            entries.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "published": pub
            })
    return entries

def filter_recent_articles(all_entries, days=3):
    today = datetime.now().date()
    cutoff = today - timedelta(days=days)
    # published가 None인 항목은 제외
    recent = [e for e in all_entries if e["published"] and e["published"] >= cutoff]
    return recent

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
                "published": entry["published"]
            })
            idx += 1
    return candidates
