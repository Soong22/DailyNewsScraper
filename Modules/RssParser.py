# Modules/RssParser.py

import json
import os
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict

# 처리 이력 파일 경로(기본: 프로젝트 루트)
PROCESSED_FILE = "processed.json"

def load_processed_links(path: str = PROCESSED_FILE) -> List[str]:
    """
    processed.json에서 'processed_links' 리스트를 읽어서 반환.
    파일이 없으면 빈 리스트 반환.
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("processed_links", [])

def save_processed_links(links: List[str], last_run: str, path: str = PROCESSED_FILE):
    """
    processed_links와 last_run(날짜 문자열)을 JSON 형태로 저장.
    """
    data = {
        "processed_links": links,
        "last_run": last_run
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_rss_feeds(rss_urls: List[str]) -> List[Dict]:
    """
    feedparser로 RSS URL들을 모두 파싱한 후,
    각 엔트리마다 title, link, published(date 객체) 정보를 딕셔너리로 모아 리스트 반환.
    """
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # published 필드가 문자열로 들어올 수 있음. 파싱 시도
            pub = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6]).date()
            elif hasattr(entry, "published"):
                try:
                    pub = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").date()
                except:
                    pub = None
            entries.append({
                "title": entry.title,
                "link": entry.link,
                "published": pub
            })
    return entries

def filter_recent_articles(all_entries: List[Dict], days: int = 3) -> List[Dict]:
    """
    today = 현재 날짜
    (today - days) 이상 날짜인 엔트리만 필터링해서 반환.
    published가 None이면 제외.
    """
    today = datetime.now().date()
    cutoff = today - timedelta(days=days)
    recent = [e for e in all_entries if e["published"] and e["published"] >= cutoff]
    return recent

def get_unprocessed_candidates(
    rss_urls: List[str],
    days: int,
    processed_links: List[str]
) -> List[Dict]:
    """
    1) parse_rss_feeds(rss_urls) → all_entries
    2) filter_recent_articles(all_entries, days) → recent_entries
    3) recent_entries 중 link가 processed_links에 없으면 후보로 남김
    4) return 후보 리스트에 index, title, link, published 포함
    """
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
