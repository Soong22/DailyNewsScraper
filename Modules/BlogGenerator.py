# Modules/BlogGenerator.py

import os
import subprocess
import re
from datetime import datetime

def slugify(text: str) -> str:
    """
    제목(text)을 받아, 파일명용 슬러그(영문·숫자+하이픈)로 변환.
    """
    text = text.lower().strip()
    # 한글이나 특수문자 제거하고, 공백은 하이픈으로 바꾸기
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text

def create_markdown_file(title: str, published: datetime.date, image_url: str, image_credit: str, summary: str, link: str) -> str:
    """
    주어진 정보로 Jekyll 스타일 Markdown 파일을 _posts/ 디렉토리에 생성하고,
    파일 경로를 반환.
    - 파일명: YYYY-MM-DD-{slug}.md
    - front matter: title, date, image, credit, original_link
    - body에는 summary(수정 가능) + 원문 링크
    """
    date_str = published.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    posts_dir = "_posts"
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)

    filepath = os.path.join(posts_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"date: {date_str}\n")
        if image_url:
            f.write(f"image: \"{image_url}\"\n")
        if image_credit:
            f.write(f"credit: \"{image_credit}\"\n")
        f.write(f"original_link: \"{link}\"\n")
        f.write("---\n\n")
        f.write(summary + "\n\n")
        f.write(f"> [원문 보기]({link})\n")

    return filepath

def git_commit_and_push(filepaths: list, commit_message: str):
    """
    주어진 파일들을 git add → commit → push
    """
    try:
        # git add
        subprocess.run(["git", "add"] + filepaths, check=True)
        # git commit
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        # git push
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print("Git 오류:", e)
