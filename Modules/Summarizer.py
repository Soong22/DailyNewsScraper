# Modules/Summarizer.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# 1) 모델·토크나이저 로드: 한 번만 로드하도록 전역 변수로 선언
MODEL_NAME = "hyunwoongko/kobart-summary"  # 예시 한국어 요약 모델
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generate_three_line_summary(text: str) -> str:
    """
    긴 본문(text)을 받아, 3문장 정도의 간략 요약을 반환.
    - max_length/min_length는 모델·하기 원하는 길이에 맞춰 조정
    """
    inputs = tokenizer.encode(
        text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )
    # 디코딩 설정: 비슷한 단어 반복 억제, 생성 길이 제한
    summary_ids = model.generate(
        inputs,
        num_beams=4,
        max_length=150,
        min_length=60,
        length_penalty=2.0,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
