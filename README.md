# Dream

**미래를 위한 학습 저장소** — SQL · Python · CS · ML · Career · Q&A

[혼자 공부하는 머신러닝+딥러닝](https://hongong.hanbit.co.kr) · Palantir FDSE · 시드닝(에덴케어·EDENING)

## 로컬 환경

Windows:

```powershell
cd C:\Users\금정산2-PC02\Desktop\Dream
```

WSL (수업 LLM 실습은 이쪽):

```bash
cd /mnt/c/Users/금정산2-PC02/Desktop/Dream
cd llm-api-playground
source .venv/bin/activate
```

## 디렉터리

| 경로 | 용도 |
|------|------|
| [`python/`](./python/) | Python 기초·OOP·실습 |
| [`sql/`](./sql/) | SQL · **데이터 모델링** · ERD (에덴케어) |
| [`cs/`](./cs/) | DS&A · 시스템 설계 · OS/네트워크 |
| [`english/`](./english/) | **기술·면접 영어** (TOEIC 985 → FDSE) |
| [`ml/`](./ml/) | ML/DL · 혼공 노트북 · 개념 지도 |
| [`career/`](./career/) | FDSE 로드맵 · 프로필 · SQL 트랙 · **Spring Boot/AI (EDENING)** |
| [`lms/`](./lms/) | **생성형 AI 과정 습득 커리큘럼** · 42수업 전체 지도 |
| [`llm-api-playground/`](./llm-api-playground/) | **P3-LLM 실습** · Day1~3 Responses API · [흐름비교 노트북](./llm-api-playground/day03/흐름비교_day1-2-3.ipynb) · [Day3 슬라이드 정리](./llm-api-playground/day03/내용정리.md) |
| [`qa/`](./qa/) | 질문·답변 일지 (`YYYY-MM-DD.md`) |

## 설치 (한 번)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ipykernel install --user --name=ml-dl-study --display-name="Dream (.venv)"
```

## Chris · 다음 액션

1. [career/SQL_data_modeling_track.md](./career/SQL_data_modeling_track.md) W1 — 에덴케어 ERD  
2. [ml/notebooks/ch01/](./ml/notebooks/ch01/) — 혼공 Ch.1  
3. [career/profile_chris.md](./career/profile_chris.md) — 포지셔닝 한 문장  
4. [career/SpringBoot_SpringAI_EDENING_curriculum.md](./career/SpringBoot_SpringAI_EDENING_curriculum.md) — EDENING Spring 커리큘럼
