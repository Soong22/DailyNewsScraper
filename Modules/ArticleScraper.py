# Modules/ArticleScraper.py

from newspaper import Article
from bs4 import BeautifulSoup
import requests
from typing import Tuple, Optional

def fetch_article_contents(url: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    주어진 URL의 기사를 파싱해서,
    - 본문 텍스트(body_text)
    - 대표 이미지 URL(image_url) 
    - 이미지 출처(image_credit) 
    이렇게 세 가지를 반환.
    필요 시, image_credit을 None으로 두어도 무방합니다.
    """
    # 1) newspaper3k로 기본 정보 크롤링
    article = Article(url, language="ko")
    article.download()
    article.parse()

    body_text = article.text      # 본문 전체 텍스트
    image_url = article.top_image or None  # 맨 위 대표 이미지가 있을 경우, 없으면 None

    # 2) 추가적으로 이미지 출처(credit)를 추출하고 싶으면 BeautifulSoup 활용
    image_credit = None
    if image_url:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.content, "html.parser")
            # 예) <figcaption class="credit"> 같은 태그를 찾아보거나
            caption = soup.find("figcaption")
            if caption and caption.text.strip():
                image_credit = caption.text.strip()
        except:
            pass

    return body_text, image_url, image_credit
