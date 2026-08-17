# SQL · 데이터 모델링 — 경험을 “인정받는 실력”으로 고정

> **왜 SQL부터?** 에덴케어에서 테이블·관계·queue를 **이미 만들었지만**,  
> 채용관은 **「데이터 모델러/엔지니어처럼 원칙으로 설명」** 할 수 있는지 본다.  
> **처음부터 버리는 게 아니라**, 만든 것을 **언어로 고정**하는 트랙.

**대상:** Chris · 에덴케어·EDENING 경험 보유  
**병행:** Dream ML(혼공) 14h/주 · **본 트랙 8~10h/week** (Q1~Q2 집중)

---

## 1. 원칙

| | |
|---|---|
| **하지 않음** | toy DB만 100번 |
| **함** | **에덴케어 실제 모델**을 ER · 정규화 · SQL로 **설명 가능**하게 |
| **산출물** | `sql/models/edencare/` + `sql/notebooks/` |

---

## 2. Phase S0 — 현재 것 “언어화” (4주)

**입력:** 에덴케어 이미 있는 것 (청구·회계·tenant·queue)

| 주 | 할 일 | 산출 |
|----|-------|------|
| W1 | **ERD** — tenant · user · beneficiary · billing | `sql/models/edencare/erd.md` |
| W2 | **정규화 설명** — 왜 이 분리? 3NF 위반 예 1개 **의도적** denorm 있으면 이유 | 1-page |
| W3 | **SQL 20문** — JOIN · aggregate · window | `sql/notebooks/edencare_queries.ipynb` |
| W4 | **Queue 설계 essay** | `sql/models/edencare/durable_queue_design.md` |

**Exit:** 면접에서 **5분** ER + queue 설명 **녹음**.

---

## 3. Phase S1 — SQL 면접·실무 (8주)

| 주차 | 주제 | 리소스 |
|------|------|--------|
| 1~2 | SELECT · JOIN · subquery · CTE | 혼공 Ch.2 + **LeetCode Database** Easy |
| 3~4 | **Window** · ranking · running total | EDENING 리포트 쿼리 1개 |
| 5~6 | Index · EXPLAIN · **slow query** 1개 개선 | 에덴케어 실측 |
| 7~8 | Transaction · isolation · **멱등** · audit table | NHIS 청구 시나리오 |

**목표:** LeetCode Database **Easy 30 + Medium 15**

---

## 4. Phase S2 — 데이터 모델링 (6주)

| | |
|---|---|
| **개념** | 카디널리티 · optional/mandatory · **slowly changing** · audit trail |
| **실습** | EDENING Learning Memory **개념 ER** (측정 헌법 반영) |
| **실습** | 에덴케어 **회계 일반/특별** 분리 — **왜 테이블 나눴는지** |
| **읽기** | 「데이터 모델링 개론」 또는 Kimball **star schema** 2장 |

---

## 5. Phase S3 — CS 면접 관문 (Palantir FDSE, 병행)

| 우선 | 주제 |
|------|------|
| P0 | **DS&A** — LC Easy/Medium 60 (배열·해시·트리·그래프) |
| P1 | **DB internals** — B-tree · WAL · connection pool |
| P1 | **System design** — 멀티테넌트 · queue · auth (에덴케어 **그대로**) |
| P2 | OS · 네트워크 · **분산** (CAP, at-least-once) |

**주 3h** — ML 주말과 **평일 저녁** 분리.

---

## 6. 에덴케어 경험 → 면접 답변 매핑

| 만들 것 | 면접 질문 |
|---------|-----------|
| ERD | “멀티테넌트 어떻게?” |
| Durable queue doc | “비동기 실패하면?” |
| RBAC schema | “권한 모델?” |
| Migration + gate | “배포 안전?” |
| NHIS 검산 rule | “규제를 코드로?” |

---

## 7. 팀 협업 갭 (약점 #4)

| 액션 | 기한 |
|------|------|
| EDENING **PR 1개/월** (코드리뷰 받기) | Q1~ |
| 부산 AI **팀** — PR · 회의록 | 2026-10 |
| Dream **public** — README · ADR 스타일 | 지속 |

---

## 8. 주간 시간 (Q1 예시)

```text
평일 2h × 4  = SQL/모델링/CS (본 트랙)
주말 14h       = Dream ML (혼공)
에덴케어       = ship (기존 리듬)
```

---

## 9. 다음 7일

- [ ] W1: 에덴케어 **ERD 초안** (8 entity)
- [ ] SQL notebook **5문** (tenant별 billing count)
- [ ] profile §9 **포지셔닝** 암기

**관련:** [profile_chris.md](./profile_chris.md) · [FDE_roadmap_2y.md](./FDE_roadmap_2y.md)
