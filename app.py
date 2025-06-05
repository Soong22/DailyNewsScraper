from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from Modules.RssParser import load_processed_links, get_unprocessed_candidates

app = FastAPI()
templates = Jinja2Templates(directory="Templates")

# RSS 피드 URL 리스트
RSS_FEEDS = [
    "https://zdnet.co.kr/rss/",
    "https://www.itworld.co.kr/service/rss/rss.asp",
    "https://www.bloter.net/rss"
]

@app.get("/")
def index(request: Request, days: int = 3):
    """
    메인 페이지: recent N일 범위 내, 아직 처리되지 않은 IT 뉴스 목록을 보여줌
    - days: query parameter로 받으며 default=3일
    """
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
