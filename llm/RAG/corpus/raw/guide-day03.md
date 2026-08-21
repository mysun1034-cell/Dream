# 학습자 가이드 — Responses API · 상태 · 도구 · 스트리밍

> p3 · 03-llm-api Day 3 (과목 마지막 날)
> 코드: `01_sources/code/day03/` · 붙여넣기 블록: 같은 폴더 `README.md`

---

## 오늘 하는 일

이틀 동안 `messages` 배열을 손으로 쌓고 도구 왕복을 손으로 돌았습니다.
오늘은 **같은 일을 OpenAI 가 파는 방식(Responses API)으로** 다시 합니다.

코드가 짧아집니다. 그런데 이 하루의 목적은 새 API 를 외우는 게 아닙니다.

> **편해졌다. 그래서 무엇이 어디로 갔나?**

이 질문에 오늘 세 번 답하는데, **답이 매번 다릅니다.**

| 무엇이 | 어디로 갔나 |
|---|---|
| 배열 재전송 | **서버로 갔다.** 없어진 게 아니다 |
| 도구 왕복 | **아무 데도 안 갔다. 그대로다** |
| 도구 실행 | **OpenAI 로 갔다.** 대신 토큰을 치른다 |

---

## 이름 대조표 — 옆에 두고 보세요

낯선 이름이 오늘 한꺼번에 쏟아집니다. 외우지 말고 **표를 보면서** 쓰세요.

| 어제까지 (`chat.completions`) | 오늘 (`responses`) |
|---|---|
| `messages=[…]` | `input=…` |
| `{"role": "system"}` | `instructions=` |
| `choices[0].message.content` | `output_text` |
| `finish_reason` | `status` + `incomplete_details` |
| `max_completion_tokens` | `max_output_tokens` |
| `tool_calls` | `output` 안의 `function_call` 아이템 |
| `tool_call_id` | `call_id` |
| `{"role": "tool", …}` | `{"type": "function_call_output", …}` |
| `.parse(response_format=클래스)` → `.parsed` | `.parse(text_format=클래스)` → `.output_parsed` |

---

## 이름 말고 뼈대 — 진짜 차이 셋

위 표는 **표면**입니다. 그 밑에 구조적인 차이가 셋 있습니다.

### ① 응답이 결과냐, 저장된 객체냐

두 응답의 최상위 키를 세어 보면 **9개 vs 39개**입니다.
Responses 쪽에는 **내가 보낸 설정이 되돌아와 담겨 있습니다**(`tools`·`store`·`instructions`·`status`…).

그래서 이런 게 됩니다.

```python
client.responses.retrieve(응답id)   # 나중에 다시 꺼내기
client.responses.delete(응답id)     # 지우기 → 이후 retrieve 는 404
```

`chat.completions` 에는 **둘 다 없습니다.** 응답이 서버에 남는 물건이 아니기 때문입니다.

### ② 답이 담기는 자리 — 칸이냐, 목록이냐

- `chat.completions` : `message` 하나에 칸이 미리 뚫려 있습니다. 안 쓰는 칸은 `None`
- `responses` : `output[]` 에 **타입이 붙은 아이템**이 쌓입니다

```python
[o.type for o in r.output]
# ['reasoning', 'web_search_call', 'message']
```

새 기능이 생기면 Chat 은 **새 칸을 뚫어야** 하고(그래서 옛 `function_call` 이 유물로 남았습니다),
Responses 는 **아이템 종류만 늘어납니다.** 위 코드는 계속 그대로 동작합니다.

### ③ 보내는 쪽도 목록이다

`input="문자열"` 은 **축약형**입니다. 원래 모양은 아이템 목록입니다.
그래서 도구 결과를 `{"type": "function_call_output", …}` 로 넣는 게 특별한 문법이 아니었습니다.

---

## 오늘 실행하는 파일

| 파일 | 실행 | 무엇 |
|---|---|---|
| `01_responses.py` | 셀 단위 | 첫 호출 · `previous_response_id` · 구조 해부 |
| `02_tools_responses.py` | 셀 단위 | 도구 왕복의 Responses 판 |
| `03_stream.py` | 셀 단위 | 스트리밍 이벤트 |
| `stream_app.py` | `streamlit run stream_app.py` | ★ 흘러나오는 챗봇 — **오늘의 산출물** |
| `04_ops.py` | 셀 단위 | 재시도 · 캐시 · 토큰 세기 · **매개변수 지도** |
| `05_catalog.py` | 셀 단위 | 모델 종류 한 바퀴 · 임베딩 |

`.ipynb` 는 `.py` 에서 만들어집니다. 내용을 고칠 때는 `.py` 를 고치세요.

---

## 🔴 Day 1 코드를 복사해 오면 막히는 자리

오늘 쓰는 모델(`gpt-5.6-luna`)은 **이 인자들을 받지 않습니다.** 넣으면 400 입니다.

```
temperature   top_p   logprobs
```

Day 1 에서 `temperature=0.7` 을 쓰던 습관 그대로 붙여넣으면 여기서 멈춥니다. **빼세요.**

---

## 자주 막히는 자리

| 증상 | 확인 |
|---|---|
| `previous_response_id` 가 400 | 앞 호출이 `store=False` 였다. 이어 붙이려면 저장돼 있어야 한다 |
| `output_text` 가 빈 문자열 | 도구 요청서가 온 것. `[o.type for o in r.output]` 부터 본다 |
| `temperature` 가 400 | 위 참조. 오늘 모델은 안 받는다 |
| 도구를 줬는데 안 쓴다 | 모델의 판단이다. `tool_choice` 로 강제할 수 있다 |
| `web_search` 뒤 토큰 급증 | 정상. 검색 결과가 입력에 통째로 들어왔다 |
| 스트리밍이 한 번에 온다 | `print(..., flush=True)` 를 빠뜨렸다 |
| 캐시가 계속 0 | 앞부분 1,024토큰 이상이 **정확히 같아야** 걸린다 |

---

## 오늘 손에 남는 것

- 브라우저에서 **답이 흘러나오는 챗봇** (`stream_app.py`)
- 공식 문서를 혼자 여는 법 — 가이드가 151개입니다. 다 볼 수 없고, **고르는 법**이 남습니다
- 메이킹 타임 두 시간 → `mission-card.md`
