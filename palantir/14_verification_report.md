# 출처·버전·검증 보고서

## 1. 작성 기준과 출처 원칙

작성 및 주요 공식 자료 확인 기준일은 **2026-09-11**입니다. 업무 설명은 Palantir가 게시한 공식 채용 공고, 기술 설명은 Python·PostgreSQL·pandas·FastAPI·HTTPX·pytest·Spark 등 공식 문서를 우선 참고했습니다. 각 본문 강의 끝에 상세 링크가 있습니다.

채용 공고는 지역·경력 수준·시기에 따라 바뀝니다. 서울 신입 공고의 학력·졸업 시점 등 조건을 모든 DS/FDSE 지원자에게 일반화하지 않습니다. 지원할 때는 본인이 지원하는 정확한 공고를 다시 확인해야 합니다. 이 문서는 공식 채용 가이드나 합격 보장 자료가 아닙니다.

교재의 업무 사례·코드·과제·모의 질문은 학습 목적으로 작성한 것입니다. 공식 문서의 문장을 대량 복제한 자료, 내부 기밀, 실제 면접 기출 모음이 아닙니다. 플랫폼 기능 설명과 이 교재가 제안한 로컬 대응 설계를 구분합니다.

## 2. 역할과 플랫폼의 공식 출발점

- [서울 Deployment Strategist](https://jobs.lever.co/palantir/2e193bdf-e668-49c1-ba32-66cc1aa131a4)
- [서울 Forward Deployed Software Engineer](https://jobs.lever.co/palantir/1bb19522-3936-4adc-9ced-c3df8b5900b9)
- [서울 신입 FDSE Commercial](https://jobs.lever.co/palantir/341d5cae-a473-4813-9a6c-0f67fcc1b253)
- [Palantir Ontology 개요](https://www.palantir.com/docs/foundry/ontology/overview/)
- [Palantir Python transforms](https://www.palantir.com/docs/foundry/transforms-python/overview/)
- [scikit-learn 누수·전처리](https://scikit-learn.org/stable/common_pitfalls.html)

## 3. 확인한 실행 환경

| 항목 | 제작 검증 환경 / 상태 |
|---|---|
| Python | 3.13.5 |
| SQLite | 3.46.1 |
| pandas | 2.2.3 |
| pytest | 9.0.2 |
| fastapi | 0.128.2 |
| pydantic | 2.13.4 |
| httpx | 0.28.1 |
| uvicorn | 0.48.0 |
| PostgreSQL | 16을 교육 대상으로 작성; 서버/클라이언트 미설치로 미실행 |
| Docker Compose | 구성 파일 제공; 미실행 |
| WSL | 사용자용 경로 안내 제공; 이 환경에서 WSL 자체를 검증하지 않음 |
| Foundry | 계정/런타임 제공·실행 없음 |

위 Python 패키지 버전은 `lab/requirements-tested.txt`에 기록했습니다. 최신 버전이나 모든 환경의 설치 성공을 보장하는 목록이 아닙니다. 패키지 설치, 운영 보안·지원 정책 검토는 독자의 환경에서 필요합니다.

## 4. 실제 실행한 것과 수치의 의미

| 항목 | 결과 | 의미 |
|---|---:|---|
| 본문 강의 | 60 | Python 30, SQL 30 |
| 본문 연습문제 | 120 | 강의마다 2개, 해설집 연결 |
| Python 일반 예제 | 29개 실행 성공 | 각 강의의 완전한 예제 프로그램 |
| pytest 본문 예제 | 1개 강의, 6개 테스트 통과 | 전체 테스트 34개에 포함 |
| SQLite SQL 예제 | 22개 실행 성공 | 조회 20개와 격리된 쓰기/트랜잭션 데모 2개 |
| 본문 실행 확인 합계 | 52개 | 29 Python + 1 pytest 강의 + 22 SQL |
| PostgreSQL 전용 본문 | 8개 미실행 | 기대 결과·독자 실행 명령 제공 |
| 자동 테스트 | 34개 통과 | 핵심 15 + API 5 + SQL/Python 대사 등 8 + pytest 강의 6 |

`lab/verify.py`는 테스트 34개를 실행한 뒤 독립 Python/SQL 예제 51개를 실행합니다. pytest 강의를 독립 예제와 테스트 양쪽에 다시 더해 58개라고 계산하지 않습니다. 기본 테스트를 unittest와 pytest로 각각 실행해도 같은 테스트를 새로운 사례로 중복 집계하지 않습니다.

테스트의 주요 대상은 10분 경계·누락·취소·빈 분모·UTC 동등성·잘못된 입력·파라미터 바인딩·외래키·롤백·ETL 재실행·API 권한·페이지 경계·지점별 수치 대사입니다. 본문 실행 출력은 `validation_results.json`, 요약은 `verification_summary.json`에 들어 있습니다.

API 검증은 FastAPI TestClient를 통해 로컬 요청 경로를 검사한 것입니다. 실제 인터넷 배포·TLS·운영 인증·부하·복구 전체를 시험한 것이 아닙니다. 예제의 실행 성공과 독립 테스트 통과는 구분합니다. 출력만 확인한 예제가 모든 가능한 입력에서 맞는다고 증명된 것은 아닙니다.

## 5. PostgreSQL 미실행 항목

- SQL-I06: 시간대·날짜 달력·빈 구간: 0건과 미수집을 구별하기
- SQL-A01: EXPLAIN·실행 계획·측정: 느린 이유를 증거로 찾기
- SQL-A02: 복합·부분 인덱스와 검색 가능한 조건
- SQL-A03: 트랜잭션 격리·동시 수정·낙관적 잠금
- SQL-A04: 업무 Action·조건부 갱신·감사 기록을 하나로 묶기
- SQL-A05: 증분 적재·UPSERT·늦게 도착하는 데이터
- SQL-A08: 행 수준 보안·최소 권한·테넌트 격리
- SQL-A09: 파티셔닝·JSONB·물리 설계의 선택

시드 `00_postgres_seed.sql`과 지표 대응판 `SQL_I10_postgres.sql`도 PostgreSQL에서 실행하지 못했습니다. SQLite에서 실행된 공통 SQL도 PostgreSQL 호환을 의도했지만 실제 엔진 간 완전한 동등성을 검증한 것은 아닙니다. 데이터 타입·시간·NULL·정렬·동시성·실행 계획은 실제 PostgreSQL에서 확인해야 합니다.

SQL-A03의 낙관적 잠금 예제는 단일 세션 모사입니다. SQL-A08의 역할·RLS 예제는 관리자 권한이 있는 독립 학습 DB를 전제로 합니다. EXPLAIN의 실행 시간·스캔 방식은 측정하지 않아 고정 수치를 제시하지 않았습니다.

## 6. 검증하지 않았거나 프로젝트로 남긴 부분

연습문제 답안의 모든 부분 코드, 프로젝트의 모든 확장 기능, 실제 Foundry 변환·Action, 대규모 분산 처리, 실제 사용자 채택 효과, 머신러닝 성능은 독립 실행 검증한 대상이 아닙니다. 본문과 프로젝트 문서에서 구현 범위와 설계 과제를 분리했습니다.

실습 API의 공개 데모 키는 운영 인증이 아닙니다. ETL은 원본 정상 이벤트를 모두 감사 원장으로 보존하거나 전역 exactly-once를 보장하지 않습니다. 합성 데이터는 실제 환자·고객·기업의 상황을 대표하지 않습니다.

## 7. 기술 참고 링크 전체 색인

각 URL은 해당 강의에서 사용하는 구문이나 개념을 확인하기 위한 공식 참고자료입니다. 동적으로 갱신되는 문서는 본문 검증 버전과 표시 버전이 다를 수 있습니다. 관련 절을 실제 구현 버전과 함께 확인하세요.

1. [공식 기술 문서 1](https://docs.python.org/3.12/tutorial/introduction.html)
2. [공식 기술 문서 2](https://docs.python.org/3.12/library/stdtypes.html#string-methods)
3. [공식 기술 문서 3](https://docs.python.org/3.12/library/decimal.html)
4. [공식 기술 문서 4](https://docs.python.org/3.12/tutorial/controlflow.html)
5. [공식 기술 문서 5](https://docs.python.org/3.12/library/stdtypes.html#truth-value-testing)
6. [공식 기술 문서 6](https://docs.python.org/3.12/tutorial/datastructures.html)
7. [공식 기술 문서 7](https://docs.python.org/3.12/library/copy.html)
8. [공식 기술 문서 8](https://docs.python.org/3.12/tutorial/datastructures.html#dictionaries)
9. [공식 기술 문서 9](https://docs.python.org/3.12/tutorial/controlflow.html#for-statements)
10. [공식 기술 문서 10](https://docs.python.org/3.12/tutorial/datastructures.html#list-comprehensions)
11. [공식 기술 문서 11](https://docs.python.org/3.12/tutorial/controlflow.html#defining-functions)
12. [공식 기술 문서 12](https://docs.python.org/3.12/library/typing.html)
13. [공식 기술 문서 13](https://docs.python.org/3.12/library/csv.html)
14. [공식 기술 문서 14](https://docs.python.org/3.12/library/json.html)
15. [공식 기술 문서 15](https://docs.python.org/3.12/tutorial/inputoutput.html#reading-and-writing-files)
16. [공식 기술 문서 16](https://docs.python.org/3.12/tutorial/errors.html)
17. [공식 기술 문서 17](https://docs.python.org/3.12/tutorial/modules.html)
18. [공식 기술 문서 18](https://docs.python.org/3.12/library/venv.html)
19. [공식 기술 문서 19](https://www.postgresql.org/docs/16/tutorial-select.html)
20. [공식 기술 문서 20](https://www.postgresql.org/docs/16/queries-table-expressions.html#QUERIES-WHERE)
21. [공식 기술 문서 21](https://www.postgresql.org/docs/16/functions-comparison.html)
22. [공식 기술 문서 22](https://www.postgresql.org/docs/16/functions-aggregate.html)
23. [공식 기술 문서 23](https://www.postgresql.org/docs/16/queries-order.html)
24. [공식 기술 문서 24](https://www.postgresql.org/docs/16/queries-limit.html)
25. [공식 기술 문서 25](https://www.postgresql.org/docs/16/queries-select-lists.html)
26. [공식 기술 문서 26](https://www.postgresql.org/docs/16/tutorial-agg.html)
27. [공식 기술 문서 27](https://www.postgresql.org/docs/16/functions-conditional.html)
28. [공식 기술 문서 28](https://www.postgresql.org/docs/16/tutorial-join.html)
29. [공식 기술 문서 29](https://www.postgresql.org/docs/16/ddl-constraints.html)
30. [공식 기술 문서 30](https://www.postgresql.org/docs/16/queries-table-expressions.html#QUERIES-JOIN)
31. [공식 기술 문서 31](https://www.postgresql.org/docs/16/tutorial-transactions.html)
32. [공식 기술 문서 32](https://www.postgresql.org/docs/16/dml.html)
33. [공식 기술 문서 33](https://docs.python.org/3.12/tutorial/controlflow.html#more-on-defining-functions)
34. [공식 기술 문서 34](https://docs.python.org/3.12/tutorial/classes.html)
35. [공식 기술 문서 35](https://docs.python.org/3.12/library/dataclasses.html)
36. [공식 기술 문서 36](https://docs.python.org/3.12/tutorial/classes.html#generators)
37. [공식 기술 문서 37](https://docs.python.org/3.12/library/itertools.html)
38. [공식 기술 문서 38](https://pandas.pydata.org/docs/user_guide/10min.html)
39. [공식 기술 문서 39](https://pandas.pydata.org/docs/user_guide/groupby.html)
40. [공식 기술 문서 40](https://pandas.pydata.org/docs/user_guide/merging.html)
41. [공식 기술 문서 41](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)
42. [공식 기술 문서 42](https://docs.python.org/3.12/library/datetime.html)
43. [공식 기술 문서 43](https://docs.python.org/3.12/library/zoneinfo.html)
44. [공식 기술 문서 44](https://docs.python.org/3.12/library/sqlite3.html)
45. [공식 기술 문서 45](https://www.psycopg.org/psycopg3/docs/basic/params.html)
46. [공식 기술 문서 46](https://www.python-httpx.org/advanced/transports/)
47. [공식 기술 문서 47](https://www.python-httpx.org/advanced/timeouts/)
48. [공식 기술 문서 48](https://docs.pytest.org/en/stable/how-to/parametrize.html)
49. [공식 기술 문서 49](https://docs.pytest.org/en/stable/how-to/assert.html)
50. [공식 기술 문서 50](https://pandas.pydata.org/docs/user_guide/missing_data.html)
51. [공식 기술 문서 51](https://www.postgresql.org/docs/16/queries-with.html)
52. [공식 기술 문서 52](https://www.postgresql.org/docs/16/queries-overview.html)
53. [공식 기술 문서 53](https://www.postgresql.org/docs/16/functions-subquery.html)
54. [공식 기술 문서 54](https://www.postgresql.org/docs/16/queries-table-expressions.html)
55. [공식 기술 문서 55](https://www.postgresql.org/docs/16/tutorial-window.html)
56. [공식 기술 문서 56](https://www.postgresql.org/docs/16/functions-window.html)
57. [공식 기술 문서 57](https://www.postgresql.org/docs/16/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS)
58. [공식 기술 문서 58](https://www.postgresql.org/docs/16/datatype-datetime.html)
59. [공식 기술 문서 59](https://www.postgresql.org/docs/16/functions-datetime.html)
60. [공식 기술 문서 60](https://www.postgresql.org/docs/16/functions-srf.html)
61. [공식 기술 문서 61](https://www.postgresql.org/docs/16/rangetypes.html)
62. [공식 기술 문서 62](https://www.sqlite.org/lang_datefunc.html)
63. [공식 기술 문서 63](https://docs.python.org/3.12/library/stdtypes.html#mapping-types-dict)
64. [공식 기술 문서 64](https://docs.python.org/3.12/library/collections.html#collections.deque)
65. [공식 기술 문서 65](https://docs.python.org/3.12/library/heapq.html)
66. [공식 기술 문서 66](https://docs.python.org/3.12/library/asyncio-task.html)
67. [공식 기술 문서 67](https://docs.python.org/3.12/library/asyncio-sync.html)
68. [공식 기술 문서 68](https://fastapi.tiangolo.com/async/)
69. [공식 기술 문서 69](https://www.postgresql.org/docs/16/sql-insert.html)
70. [공식 기술 문서 70](https://fastapi.tiangolo.com/tutorial/testing/)
71. [공식 기술 문서 71](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
72. [공식 기술 문서 72](https://docs.python.org/3.12/library/typing.html#typing.Protocol)
73. [공식 기술 문서 73](https://docs.python.org/3.12/library/profile.html)
74. [공식 기술 문서 74](https://docs.python.org/3.12/library/concurrent.futures.html)
75. [공식 기술 문서 75](https://docs.python.org/3.12/library/threading.html)
76. [공식 기술 문서 76](https://docs.python.org/3.12/library/logging.html)
77. [공식 기술 문서 77](https://www.postgresql.org/docs/16/user-manag.html)
78. [공식 기술 문서 78](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
79. [공식 기술 문서 79](https://www.palantir.com/docs/foundry/ontology/overview/)
80. [공식 기술 문서 80](https://www.palantir.com/docs/foundry/transforms-python/overview/)
81. [공식 기술 문서 81](https://www.postgresql.org/docs/16/using-explain.html)
82. [공식 기술 문서 82](https://www.postgresql.org/docs/16/sql-analyze.html)
83. [공식 기술 문서 83](https://www.postgresql.org/docs/16/indexes-multicolumn.html)
84. [공식 기술 문서 84](https://www.postgresql.org/docs/16/indexes-partial.html)
85. [공식 기술 문서 85](https://www.postgresql.org/docs/16/indexes-expressional.html)
86. [공식 기술 문서 86](https://www.postgresql.org/docs/16/transaction-iso.html)
87. [공식 기술 문서 87](https://www.postgresql.org/docs/16/explicit-locking.html)
88. [공식 기술 문서 88](https://www.postgresql.org/docs/16/dml-returning.html)
89. [공식 기술 문서 89](https://www.postgresql.org/docs/16/ddl-rowsecurity.html)
90. [공식 기술 문서 90](https://www.postgresql.org/docs/16/sql-createrole.html)
91. [공식 기술 문서 91](https://www.postgresql.org/docs/16/ddl-partitioning.html)
92. [공식 기술 문서 92](https://www.postgresql.org/docs/16/datatype-json.html)
93. [공식 기술 문서 93](https://www.postgresql.org/docs/16/functions-json.html)
94. [공식 기술 문서 94](https://www.postgresql.org/docs/16/rules-materializedviews.html)



---
