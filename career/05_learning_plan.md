# 학습 계획

> 마지막 갱신 2026-09-15. 교육 과정 정보는 2026-09-15에 공식 페이지에서 확인했다. 확인하지 못한 가격은 "미확인"으로 적었다.

## 원칙

**배우고, 적용하고, 증명한다.** 중심은 SQL·Python과 두 제품이다. 강의는 **이론 1개와 공식 실습 1개**까지만 같이 듣는다. 수료증보다 프로젝트에 적용한 결과를 남긴다.

2026년 11월에는 시드닝 정규직 입사, 2027년 1학기에는 복학이 겹친다. 그래서 과정을 늘리기보다 하나를 끝내는 쪽을 택한다.

## 지금 하는 것

| 트랙 | 내용 | 상태 |
|---|---|---|
| SQL·Python 재건 | 2026-09-14 시작한 12주 학습 보드. 교재는 공부방의 팔란티어 DS·FDSE 통합교재(`palantir/` 00–15) | 진행 중 |
| 두 제품 | EDENING, 문서자동화 통합관리시스템 | 진행 중 |

## 추가할 과정 (제안)

| 역할 | 과정 | 접근·비용 | 분량 | 선수 조건 | 왜 이것인가 |
|---|---|---|---|---|---|
| **이론 1** | [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) (Stanford Online · DeepLearning.AI, Coursera) | Coursera 구독 약 월 49달러. 무료 청강 없음, 재정 지원 신청 가능 | 약 95시간 (3과목) | 기초 코딩, 고등학교 수학 | ML의 표준 입문. 회귀·분류·기초 신경망 |
| 이론 2 (나중) | [Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning) (DeepLearning.AI) | Coursera 구독. 무료 청강 없음, 재정 지원 신청 가능 | 약 3개월 × 주 10시간 (5과목) | 중급 Python, 선형대수 기초, ML 기초 | ML Specialization을 끝낸 뒤에만 시작 |
| **공식 실습 1** | [AWS Skill Builder](https://skillbuilder.aws) → [AWS Certified Solutions Architect – Associate](https://aws.amazon.com/certification/certified-solutions-architect-associate/) | 과정은 무료 등급 있음(구독 가격은 미확인). 시험 150달러 | 자기 주도 | AWS 경험 약 1년 권장 | 이미 EDENING을 AWS ECS에 배포·운영 중이고, AWS Associate Solutions Architect 채용과 바로 이어진다 |
| 틈틈이 | [Palantir Learn](https://learn.palantir.com) — Ontology·AIP 과정 | 무료 | 과정당 60–90분 | 없음 | DS 면접 준비용으로 훑어보기. 자격시험은 지원팀에 요청해야 응시할 수 있고 비용이 공개돼 있지 않아 주력 실습으로 두지 않는다 |
| 필요할 때 | [Claude Academy](https://academy.claude.com) — Building with the Claude API | 무료 | 약 8–9시간 | Python·JSON 기초 | 제품의 AI 기능을 만들 때만 |

**지금 하지 않는 것:** OpenAI Academy 자격 과정(비용 미확인), DL과 ML 동시 수강, 자격증 여러 개 동시 준비, 같은 AI 입문 내용 중복 수강.

## 순서 (제안)

1. **2026년 9–12월:** SQL·Python 보드를 끝낸다. 새 과정은 추가하지 않는다.
2. **2026년 12월–2027년 2월:** Machine Learning Specialization. 동시에 AWS Skill Builder로 SAA 준비를 시작한다.
3. **2027년 3–6월 (복학, 지원 시기):** SAA 시험. 과정보다 지원 준비와 사례 정리가 우선이다.
4. **2027년 여름 이후:** 필요하면 Deep Learning Specialization.

주당 시간과 시작일은 11월 입사 뒤 실제 근무 시간에 맞춰 다시 정한다.

## 완료 기준

| 영역 | 끝났다고 보는 기준 |
|---|---|
| SQL | JOIN·집계·CASE·CTE·윈도 함수로 업무 질문에 답하고, 숫자가 맞는지 원본과 교차 검산할 수 있다 |
| Python | 파일·API 데이터를 pandas로 정리·분석하고, 잘못된 입력과 결과 검증까지 설명할 수 있다 |
| ML | 기준 모델과 비교해 모델이 실제로 나은지 지표로 말할 수 있다. 데이터 누수와 과적합을 설명할 수 있다 |
| AWS SAA | 시험 합격. 그리고 EDENING 배포 구조를 비용·권한·복구 관점에서 설명할 수 있다 |

## 과정 기록 양식

```text
과정명 · 제공사:
공식 URL · 확인일:
상태: 후보 / 등록 / 수강 중 / 수료 / 프로젝트 적용
비용 · 접근 권한:
배우는 이유와 지금 부딪힌 문제:
실습 결과물:
혼자 설명할 수 있는 내용:
프로젝트에 적용한 결과:
남은 한계 · 다음 결정:
```

## 출처 (2026-09-15 확인)

- [Palantir Learn 과정 목록](https://learn.palantir.com/page/course-catalog)
- [Claude Academy](https://academy.claude.com/)
- [OpenAI Academy](https://academy.openai.com)
- [AWS Certified Cloud Practitioner](https://aws.amazon.com/certification/certified-cloud-practitioner/) (시험 100달러)
- [AWS Certified Solutions Architect – Associate](https://aws.amazon.com/certification/certified-solutions-architect-associate/) (시험 150달러)
- [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction)
- [Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning)
