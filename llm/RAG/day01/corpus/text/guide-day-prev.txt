# 학습자 가이드 — 답의 모양을 약속한다 · 함수를 설명한다: 구조화 출력과 도구 호출

> 2026-08-18 · 생성형 AI 기반 기업솔루션 개발 실무 프로젝트 과정
> LLM 활용·API 연동 Day 2 · 원본: developers.openai.com/api/docs/guides/structured-outputs

---

## 지식 목표

- 모델의 답을 코드가 쓰려면 형식이 먼저 약속돼야 한다는 것, 그 약속을 적는 도구가 JSON 스키마
  하나이며 쓰는 자리가 둘(답의 모양·함수 인자의 모양)이라는 것을 이해한다.
- 구조화 출력의 세 단계가 기능의 계단이 아니라 **같은 약속의 세 표기법**이며, `json_object`는
  유효한 JSON까지만 보장하고 `json_schema`+`strict`부터 모양이 보장된다는 차이를 안다.
- 도구 호출에서 모델은 함수를 실행하지 않고 호출 요청만 반환하며 실제 실행은 내 코드라는 것,
  그래서 결과를 `role:"tool"` 조각으로 다시 보내는 왕복이 구조적으로 필요하다는 것을 안다.
- 400 응답이 신분 문제(401)와 달리 요청서 양식 문제이며 고칠 곳이 응답 문장에 적혀 있다는
  감각을 갖는다.

## 기능 목표

- `response_format`으로 `json_object` · `json_schema`(strict)를 지정하고, Pydantic 클래스를
  `chat.completions.parse`에 넘겨 `.parsed`로 객체를 받을 수 있다.
- `model_json_schema()`로 클래스가 품은 스키마를 꺼내 확인할 수 있다.
- 함수 사용법을 `tools` 스키마로 작성하고, `finish_reason`과 `tool_calls`를 읽어 모델의 호출
  요청을 해석하고, 인자를 파싱해 내 함수를 실행한 뒤 `tool_call_id`로 짝지어 재투입하는 왕복을
  직접 구현할 수 있다.
- 도구가 여럿일 때 `for`로 순회하고, 재호출이 필요할 때 `while`로 감싸며 횟수 상한과 빈 응답
  대비를 둘 수 있다.
- 400이 나면 응답 문장을 읽고 세 함정(json 미언급 · `additionalProperties` 누락 · 최상위 한글
  클래스명) 중 어느 것인지 판별할 수 있다.

## 산출물 목표

- 터미널에서 도는 `tool_chat.py`와 브라우저에서 도는 `tool_app.py` — 질문에 따라 모델이 스스로
  날씨·계산 도구를 골라 부르고, 오늘의 실제 날씨가 말풍선에 나오는 챗봇.
- 메이킹 타임의 결과물 — 구조화 출력 또는 도구 호출 중 하나가 들어 있는, 학습자가 만들고 싶어서
  만든 결과물.

## 도구·환경

Python 3.12(기존 가상환경 `.venv` 그대로) · `openai` 3.0.0 Python SDK
(`chat.completions.create` / `.parse`) · Pydantic(데이터 모양을 파이썬 클래스로 적는 도구) ·
Streamlit(브라우저 챗봇 화면, p1 선이수) · open-meteo 공개 API(키 없이 쓰는 날씨 도구) ·
VSCode + Jupyter 확장(`.py`에서 생성한 `.ipynb` 셀 실행). 외부 데이터셋 없음 — 실습 소재는
수업용 쇼핑몰 리뷰 문장 4건(직접 작성)과 open-meteo가 반환하는 실시간 날씨 값. 호출 모델은
OpenAI `gpt-5.4-nano`.

## 세 단계 표기법 정리

| 단계 | `response_format` | 보장 수준 |
|---|---|---|
| 1. json_object | `{"type": "json_object"}` | 유효한 JSON이라는 것만 보장 — 키 이름·구조는 매번 달라질 수 있음 |
| 2. json_schema + strict | `{"type": "json_schema", "json_schema": {"schema": {...}, "strict": True}}` | 스키마에 적은 모양 그대로 보장 |
| 3. Pydantic 클래스 | `client.chat.completions.parse(..., response_format=MyModel)` | 2와 동일한 보장 + `.parsed`로 바로 파이썬 객체 |

## 메이킹 — 내 결과물 하나 완성

오늘 배운 구조화 출력 또는 도구 호출 중 하나를 넣어, 만들고 싶은 결과물 하나를 완성해 공유한다.
주제·형태·도구는 자유이며 금요일 결과물을 이어 키워도 된다.

- [ ] 첫 걸음이 안 떨어지면 `tool_app.py`를 복사해 도구 함수 하나만 바꿨는가?
- [ ] 400이 났을 때 서버가 준 문장을 읽었는가?
- [ ] 도구를 안 부르면 description부터 확인했는가?

## 둘을 엮기 — 도구가 가져온 값을 구조화해 보이기

도구 호출로 바깥에서 값을 가져오고, 그 값을 구조화 출력으로 정리해 표나 카드 형태로 화면에
보인다. 오늘 배운 두 가지가 한 흐름 안에서 이어지는 것을 직접 만든다.

- [ ] 도구가 여러 개 요청될 때 `for`로 순회하는가?
- [ ] 재투입할 때 모델의 요청서(`msg`)도 배열에 넣었는가?

## 남에게 보여줄 완성도까지

처음 보는 사람이 화면만 보고 용도를 알 수 있는 수준까지 결과물을 다듬는다. 제목·첫인사·입력
안내·오류 안내를 갖춘다.

- [ ] 빈 응답일 때 대체 문구가 준비돼 있는가?
- [ ] 키를 코드에 직접 적지 않았는가?

## 제출 안내

메이킹 타임의 공유물 하나면 됩니다. 내가 만든 결과물의 화면 캡처와 함께, 무엇을 만들었는지 한
줄과 오늘 배운 것 중 어디에 썼는지 한 줄을 적어 주세요. 조건은 하나입니다 — 구조화 출력 또는
도구 호출 중 하나가 결과물 안에 있으면 됩니다. 금요일 결과물을 이어 키운 것도 좋습니다.

## 다음 수업 연결

다음 수업은 오늘 만든 도구 챗봇을 다시 열며 시작한다. 같은 일을 OpenAI의 새 호출 방식
(Responses API)으로 다시 짜 보면 코드가 짧아지는데, 무엇이 짧아지고 무엇이 감춰지는지를 오늘
손으로 다 짜 봤기 때문에 비로소 볼 수 있다. 이어서 답이 한 글자씩 흘러나오게 하고(스트리밍),
호출이 실패하거나 한도에 걸릴 때의 운영을 다룬다. 마지막에 다음 과목으로 넘어가는 질문을 심는다
— 이제 답을 내 문서에서 찾게 하려면 무엇이 필요할까.

## 강의자료

- developers.openai.com · api/docs/guides/structured-outputs —
  https://developers.openai.com/api/docs/guides/structured-outputs
- LLM 활용(OpenAI, Google Gemini) 및 API 연동 · 학습자 가이드 HTML(원본)

## 오늘 만든 것 (우리 실습 — [`llm-api-playground/`](../../llm-api-playground/))

- `structured.ipynb` — `json_object` → `json_schema`+`strict` → Pydantic `.parse()` 세 단계를
  같은 리뷰로 반복 비교, `BadRequestError`(400) 직접 유도해 원인 문장 확인
- `day02/tool_chat.py` — open-meteo 날씨 + 계산기 두 도구를 `tools`로 등록한 터미널 챗봇.
  `finish_reason == "tool_calls"`일 때만 실행 → `tool_call_id`로 재투입 → `MAX_ROUNDS` 상한
- 아직 없음: `tool_app.py`(Streamlit 버전), 메이킹 타임 결과물
