# app.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Modules.RssParser import load_processed_links, get_unprocessed_candidates

app = FastAPI()
templates = Jinja2Templates(directory="Templates")
app.mount("/static", StaticFiles(directory="Static"), name="static")

# (4) RSS 피드 URL 목록 (keys는 parse_rss_feeds의 RSS_FEED_SITES와 일치해야 함)
RSS_FEEDS = [
    "https://www.itworld.co.kr/feed/",
    "https://yozm.wishket.com/magazine/feed/",
    "https://bloter.net/rss/news",
]

@app.get("/")
def index(request: Request, days: int = 3):
    processed_links = load_processed_links()
    candidates = get_unprocessed_candidates(
        rss_urls=RSS_FEEDS,
        days=days,
        processed_links=processed_links
    )
    return templates.TemplateResponse(
        "Index.html",
        {
            "request": request,
            "candidates": candidates,
            "days": days
        }
    )
