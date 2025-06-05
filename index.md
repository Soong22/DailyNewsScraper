---
layout: default
title: "Daily IT News Summary"
---
# Daily IT News Summary

이곳은 자동으로 스크랩된 IT 뉴스 요약이 올라가는 블로그입니다.

아래 링크에서 최신 뉴스 목록을 확인하세요:
- [홈페이지](https://<YourUsername>.github.io/DailyNewsScraper/)

### 최신 포스트
{% for post in site.posts %}
- [{{ post.title }}]({{ post.url }}) ({{ post.date | date: "%Y-%m-%d" }})
{% endfor %}
