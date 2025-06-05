# app.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from Modules.RssParser import load_processed_links, get_unprocessed_candidates
from Modules.ArticleScraper import fetch_article_contents
from Modules.Summarizer import generate_three_line_summary

app = FastAPI()
templates = Jinja2Templates(directory="Templates")
app.mount("/static", StaticFiles(directory="Static"), name="static")

RSS_FEEDS = [
    "https://www.itworld.co.kr/feed/",
    "https://yozm.wishket.com/magazine/feed/",
    "https://cdn.bloter.net/rss/gns_allArticle.xml",
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

@app.get("/article/{item_index}")
def article_detail(request: Request, item_index: int, days: int = 3):
    # 1) 미처리 후보 목록을 다시 가져옴
    processed_links = load_processed_links()
    candidates = get_unprocessed_candidates(
        rss_urls=RSS_FEEDS,
        days=days,
        processed_links=processed_links
    )

    # 2) 인덱스 범위 체크
    if item_index < 1 or item_index > len(candidates):
        raise HTTPException(status_code=404, detail="해당 기사를 찾을 수 없습니다.")
    selected = candidates[item_index - 1]  # 인덱스는 1-based

    # 3) URL에서 본문·이미지·이미지 출처 가져오기
    body_text, image_url, image_credit = fetch_article_contents(selected["link"])

    # 4) 3줄 요약 생성
    summary = generate_three_line_summary(body_text)

    # 5) 템플릿 렌더링 (ArticleDetail.html)
    return templates.TemplateResponse(
        "ArticleDetail.html",
        {
            "request": request,
            "item": selected,
            "body_text": body_text,
            "image_url": image_url,
            "image_credit": image_credit,
            "summary": summary
        }
    )
