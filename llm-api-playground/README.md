# 수업 그래프 · 과목 퀴즈

수업 슬라이드를 마인드맵처럼 펼치고, 칸을 고르면 설명·예제 코드·객관식 퀴즈가 나오는 Streamlit 앱입니다.

오늘 작업:

- 수업 슬라이드 25개를 트리에 넣었다. 전체 **8과목 · 31수업 · 163항목**.
- 그래프는 클릭하면 그 층만 남는다. 노드는 제자리에 고정해서 화면 밖으로 안 나간다.
- 마우스가 잘 안 잡혀서 제목 아래 **큰 과목 단추**와 왼쪽 **큰 라디오**를 같이 두었다.
- 퀴즈는 `chat.completions.parse` + Pydantic `Quiz` 로 문항 모양을 고정한다. 보기는 4개, 정답은 1~4.
- 항목마다 줄마다 한글 주석이 달린 예제 코드가 붙는다.

## 과목

| 과목 | 수업 |
|---|---|
| Streamlit | 5/21 위젯·대시보드, 5/22 session_state·배포 |
| 머신러닝 | k-NN → 회귀·규제 → 분류 지표 → 트리·CV → K-Means·PCA |
| 딥러닝 | 퍼셉트론 → 역전파 → Dropout → CNN → 전이학습·탐지 |
| 미니프로젝트 | Git 협업, EDA·전처리, 충돌·리뷰 |
| Spring AI | ChatClient부터 스트리밍·통합까지 6일 |
| PyTorch NLP | 텐서·루프 → 텍스트를 숫자로 → RNN → LSTM·GRU |
| LLM 핵심기술 | 어텐션, 셀프 어텐션, BERT/GPT, 생성 디코딩 |
| LLM API | 무상태 대화, 구조화 출력, 도구 호출, **Day 3 Responses API** |

## 실행

키는 `.env` 또는 `env`에 둔다. git에 올리지 않는다.

```powershell
cd C:\Users\금정산2-PC02\Desktop\Dream\llm-api-playground
.\.venv-win\Scripts\python.exe -m streamlit run day02/lecture_quiz_app.py
```

WSL이면 같은 파일에서:

```bash
source .venv/bin/activate
streamlit run day02/lecture_quiz_app.py
```

제목 아래 과목 단추 8개가 보여야 한다. 안 보이면 **전체 맵으로**를 누르거나 새로고침한다.

## 쓰는 법

1. 위 단추나 청록 상자에서 과목을 고른다.
2. 그래프에서 수업을 누르면 항목이 펼쳐진다.
3. 항목을 누르면 설명과 예제 코드가 나온다.
4. **퀴즈 3문제 만들기** → 고르고 **채점**.

## 파일

| 파일 | 하는 일 |
|---|---|
| `day02/lecture_quiz_app.py` | 그래프 + 단추 + 라디오 + 퀴즈 |
| `day02/curriculum.py` | LLM 핵심기술 · LLM API |
| `day02/curriculum_more.py` | Streamlit · ML · DL · 미니 · Spring AI · PyTorch NLP |
| `day02/curriculum_code.py` / `curriculum_code_more.py` | 항목마다 줄 주석 예제 |
| `day02/quiz.py` | 터미널 퀴즈 |
| `day02/structured.ipynb` | `json_object` → `json_schema`+`strict` → Pydantic `parse` |
| `day02/tools.ipynb` | 도구 호출 |
| `day02/tool_chat.py` | 날씨·계산 도구 챗 |
| [`day03/내용정리.md`](./day03/내용정리.md) | Day 3 슬라이드 86장 정리 |
| [`day03/흐름비교_day1-2-3.ipynb`](./day03/흐름비교_day1-2-3.ipynb) | Day 1·2·3 같은 질문 비교 + `01`~`04` 수업 셀 |
| `day03/01_response_api.ipynb` | 첫 호출 · 기억 · store · 키 비교 · 날씨 왕복 · 웹검색 · 코드 해석기 |
| `day03/02_stream.ipynb` | `create` vs `stream` · 타입 개수 · 첫 글자 시각 |
| `day03/03_ops.ipynb` | 재시도 · 캐시 · verbosity · reasoning · 방 · llms.txt |
| `day03/04_other_models.ipynb` | 모델 목록 · 검열 · TTS · 이미지 · 임베딩 |
| `day03/hello.mp3` · `war.mp3` · `image.png` | TTS·이미지 시연 산출물 |
| `수업정리/` | 강사 코드와 슬라이드 쉽게 풀이 |

## Day 3 · Responses API

2026-08-19. `chat.completions`와 Responses는 이름만 다른 표기가 아니다. Chat 응답은 결과 봉투, Responses 응답은 설정까지 되돌아오는 서버 저장 객체라서 `retrieve`·`delete`가 있다.

```powershell
cd C:\Users\금정산2-PC02\Desktop\Dream\llm-api-playground
.\.venv-win\Scripts\python.exe -m jupyter notebook day03/흐름비교_day1-2-3.ipynb
```

키는 `.env` 또는 `env`. 노트북 첫 셀이 파일을 읽어 `OPENAI_API_KEY`를 넣는다. `temperature`는 오늘 모델에서 400이다.

퀴즈 핵심:

```python
class Quiz(BaseModel):
    questions: List[Question]

r = client.chat.completions.parse(..., response_format=Quiz)
```
