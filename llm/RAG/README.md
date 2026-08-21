# LLM 데이터 엔지니어링 — RAG

2026-08-21 수업. 코퍼스 다섯 문서를 잘라 임베딩하고 Chroma에 넣는다.

## 폴더

| 경로 | 내용 |
|---|---|
| `corpus/` | day02 노트북의 `../corpus` — raw·text·manifest |
| `day01/` | PDF/HTML/표 추출, 코퍼스 장부 |
| `day02/01_whole.ipynb` | 문서를 통째로 넣기 (비용·지연) |
| `day02/02_chunk.ipynb` | Document, 헤더 자르기, 토큰 400/겹침 80, `chunks.jsonl` |
| `day02/03_embed.ipynb` | 코사인 유사도, 히트맵, `vectors.npy`, numpy 검색 |
| `day02/04_chroma.ipynb` | 벡터를 Chroma에 넣고 `doc_id`로 필터 |

`.env`와 `chroma/`는 git에 올리지 않는다. 노트북은 `day02`에서 연다.

```bash
cd llm/RAG/day02
# 커널: 기존 .venv (Python 3.12)
```
