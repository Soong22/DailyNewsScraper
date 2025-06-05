# Modules/RssParser.py

import json
import os
import feedparser
from datetime import datetime, timedelta

PROCESSED_FILE = "processed.json"

# RSS URL → 사이트명 매핑
RSS_FEED_SITES = {
    "https://www.itworld.co.kr/feed/": "ITWorld",
    "https://yozm.wishket.com/magazine/feed/": "요즘IT",
    "https://cdn.bloter.net/rss/gns_allArticle.xml": "블로터",
    # (필요하다면 moji 등 나머지는 주석 처리하거나 추가)
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
        # feedparser로 RSS 불러오기 (User-Agent 지정하면 일부 사이트 안정적)
        feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
        site_name = RSS_FEED_SITES.get(url, "Unknown")

        for entry in feed.entries:
            pub = None

            # ① published_parsed 우선 시도
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6]).date()
            # ② updated_parsed 시도
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub = datetime(*entry.updated_parsed[:6]).date()
            # ③ published 문자열 여러 포맷 파싱 시도
            elif hasattr(entry, "published"):
                for fmt in (
                    "%a, %d %b %Y %H:%M:%S %z",   # e.g. "Tue, 10 Jun 2025 12:34:56 +0900"
                    "%Y-%m-%dT%H:%M:%SZ",         # e.g. "2025-06-10T03:22:10Z"
                    "%Y-%m-%d %H:%M:%S"           # e.g. "2025-06-10 12:34:56"
                ):
                    try:
                        pub = datetime.strptime(entry.published, fmt).date()
                        break
                    except:
                        continue
            # ④ dc_date 형식으로 노출되는 경우 (feedparser가 "dc_date" 키로 제공할 때)
            elif entry.get("dc_date"):
                try:
                    pub = datetime.strptime(entry.get("dc_date"), "%Y-%m-%dT%H:%M:%SZ").date()
                except:
                    pub = None

            # ⑤ 만약 여전히 pub == None인 경우, (특히 Yozm처럼 날짜 필드가 아예 없는 피드)
            #    "오늘 날짜"로 지정해서 필터 통과시키도록 한다.
            if pub is None:
                pub = datetime.now().date()

            entries.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "published": pub,
                "site": site_name
            })

    return entries

def filter_recent_articles(all_entries, days=3):
    today = datetime.now().date()
    cutoff = today - timedelta(days=days)
    # 이제 모든 항목에 published가 None일 리가 없으므로, 날짜 비교로 필터링
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
                "published": entry["published"],
                "site": entry["site"]
            })
            idx += 1
    return candidates
