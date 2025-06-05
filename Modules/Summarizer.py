# Modules/Summarizer.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# 한국어 요약용으로 공개된 모델로 변경
MODEL_NAME = "gogamza/kobart-summarization"

# 토크나이저와 모델을 전역에서 한 번만 로드
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generate_three_line_summary(text: str) -> str:
    """
    긴 한국어 본문(text)을 받아, 3문장 정도 분량의 요약을 반환합니다.
    - max_length, min_length 파라미터로 출력 길이를 조절합니다.
    """
    # 1) 입력 텍스트를 토크나이저로 인코딩 (최대 1024 토큰까지 자름)
    inputs = tokenizer.encode(
        text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )

    # 2) 모델에 넘겨서 요약 생성 (빔 서치, 길이 제약 등 설정)
    summary_ids = model.generate(
        inputs,
        num_beams=4,            # 빔 서치 폭
        max_length=150,         # 생성 최대 토큰 길이
        min_length=60,          # 생성 최소 토큰 길이
        length_penalty=2.0,
        no_repeat_ngram_size=3,
        early_stopping=True
    )

    # 3) 토크나이저로 디코딩하여 문자열로 반환
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
