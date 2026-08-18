# 장원 강사 — 구조화 출력
# 1) 깨진 스키마 → 400
# 2) json_schema + strict
# 3) Pydantic parse (create 대신 parse)

import json

from openai import BadRequestError, OpenAI
from pydantic import BaseModel

client = OpenAI()
API_MODEL = "gpt-5.4-nano"
review = "배송은 느렸지만 물건은 기대 이상이야. 또 사줄게!"

# ── 1. 400 이 나는 스키마 (properties 오타, required/strict 없음) ──
broken = {
    "type": "object",
    "propeties": {
        "감정": {"type": "string", "description": "긍정/부정/중립 중에서 하나로"},
        "별점": {"type": "integer", "description": "1~5 점 사이 점수. 높은게 긍정"},
        "요약": {"type": "string", "description": "한 문장으로 요약"},
    },
}
try:
    r = client.chat.completions.create(
        model=API_MODEL,
        messages=[{"role": "user", "content": f"이 리뷰를 JSON으로 분석해줘. {review}"}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "review_analysis", "schema": broken},
        },
        max_completion_tokens=300,
    )
    print(json.loads(r.choices[0].message.content))
except BadRequestError as e:
    print(e)

# ── 2. strict 스키마 — 모양이 고정된다 ──────────────────────────
# description 은 장식이 아니다. 각 칸에 무엇을 넣을지 모델이 읽는 설명이다.
strict_schema = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "description": "긍정 / 부정 / 중립 중 하나"},
        "rating": {"type": "integer", "description": "1~5 사이 정수"},
        "summary": {"type": "string", "description": "한 문장 요약"},
    },
    "required": ["sentiment", "rating", "summary"],
    "additionalProperties": False,
}

r = client.chat.completions.create(
    model=API_MODEL,
    messages=[{"role": "user", "content": f"이 리뷰를 분석해 줘: {review}"}],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "review_analysis", "strict": True, "schema": strict_schema},
    },
    max_completion_tokens=400,
)
print(json.loads(r.choices[0].message.content))

# ── 3. Pydantic — 텍스트가 아니라 인스턴스로 받는다 ─────────────


class ReviewAnalysis(BaseModel):
    감정: str
    별점: int
    요약: str


r = client.chat.completions.parse(
    model=API_MODEL,
    messages=[{"role": "user", "content": f"이 리뷰를 분석해 줘: {review}"}],
    response_format=ReviewAnalysis,
    max_completion_tokens=400,
)
print(r.choices[0].message.parsed)
print(type(r.choices[0].message.parsed))
