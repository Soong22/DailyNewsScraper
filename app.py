# app.py

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Modules.RssParser import load_processed_links, get_unprocessed_candidates, save_processed_links
from Modules.ArticleScraper import fetch_article_contents
from Modules.Summarizer import generate_three_line_summary
from Modules.BlogGenerator import create_markdown_file, git_commit_and_push

from datetime import datetime
import os

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
    processed_links = load_processed_links()
    candidates = get_unprocessed_candidates(
        rss_urls=RSS_FEEDS,
        days=days,
        processed_links=processed_links
    )

    if item_index < 1 or item_index > len(candidates):
        raise HTTPException(status_code=404, detail="해당 기사를 찾을 수 없습니다.")
    selected = candidates[item_index - 1]

    body_text, image_url, image_credit = fetch_article_contents(selected["link"])
    summary = generate_three_line_summary(body_text)

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


@app.post("/article/{item_index}/post")
def post_article(item_index: int, days: int = 3, summary: str = Form(...)):
    processed_links = load_processed_links()
    candidates = get_unprocessed_candidates(
        rss_urls=RSS_FEEDS,
        days=days,
        processed_links=processed_links
    )
    if item_index < 1 or item_index > len(candidates):
        raise HTTPException(status_code=404, detail="해당 기사를 찾을 수 없습니다.")
    selected = candidates[item_index - 1]

    filepath = create_markdown_file(
        title=selected["title"],
        published=selected["published"],
        image_url=selected.get("image_url", None),
        image_credit=selected.get("image_credit", None),
        summary=summary,
        link=selected["link"]
    )

    commit_msg = f"Add post: {selected['title']}"
    git_commit_and_push([filepath], commit_msg)

    processed = processed_links + [selected["link"]]
    last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_processed_links(processed, last_run)

    return RedirectResponse(url=f"/result?file={os.path.basename(filepath)}", status_code=302)


@app.get("/result")
def result(request: Request, file: str):
    return templates.TemplateResponse(
        "Result.html",
        {
            "request": request,
            "file": file
        }
    )
