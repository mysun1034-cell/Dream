# SQL 심화: 성능·정합성·보안·데이터 시스템 설계

**구성:** 10강 · 연습문제 20개 · DS/FDSE 역할별 적용 과제

SQL 중급을 선행합니다. PostgreSQL 전용 실습은 환경 가이드의 독립 학습 DB에서만 실행하세요. 성능·정합성·보안을 결과 SQL과 함께 설계합니다.

**사용 방법:** 모든 명령은 압축을 푼 폴더의 `lab/`에서 실행합니다. 아직 환경을 만들지 않았다면 [환경과 데이터 사전](#book-02)을 먼저 읽으세요. 각 강의의 설명형 해설은 본문에, 연습문제 정답은 [해설집](#book-09)에 있습니다.

## 강의 지도

- [SQL-A01 EXPLAIN·실행 계획·측정: 느린 이유를 증거로 찾기](#sql-a01)
- [SQL-A02 복합·부분 인덱스와 검색 가능한 조건](#sql-a02)
- [SQL-A03 트랜잭션 격리·동시 수정·낙관적 잠금](#sql-a03)
- [SQL-A04 업무 Action·조건부 갱신·감사 기록을 하나로 묶기](#sql-a04)
- [SQL-A05 증분 적재·UPSERT·늦게 도착하는 데이터](#sql-a05)
- [SQL-A06 시점 일치·지연 도착·데이터 누수 방지](#sql-a06)
- [SQL-A07 재귀 CTE·의존성 탐색·순환 제어](#sql-a07)
- [SQL-A08 행 수준 보안·최소 권한·테넌트 격리](#sql-a08)
- [SQL-A09 파티셔닝·JSONB·물리 설계의 선택](#sql-a09)
- [SQL-A10 배포 전 품질 게이트·대사·운영 지표 계약](#sql-a10)

---

<a id="sql-a01"></a>
## SQL-A01 · EXPLAIN·실행 계획·측정: 느린 이유를 증거로 찾기

**학습 목표:** 예상 비용과 실제 실행을 구분하고 개선 전후를 비교할 계획을 세운다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

실행 계획(plan)은 DB가 행을 찾고 연결하고 집계하는 방법이다. 순차 스캔은 표를 훑는 방식이고 인덱스 스캔은 색인을 이용하는 방식이다. 추정 행 수와 실제 행 수는 각각 계획 당시 예상과 실행 중 관측이다.

### 2. 비유로 잡는 그림

음식이 늦었다고 요리사부터 늘리지 않고 주문 접수·재료 찾기·조리·배달 중 어디에서 시간이 쓰였는지 살펴본다.

### 3. 원리와 업무에서의 의미

SQL은 원하는 결과를 선언하지만 실제 처리 방식은 DB가 정한다. EXPLAIN은 계획을 보여 주고, EXPLAIN ANALYZE는 실제로 실행하면서 관측치를 수집한다. cost는 추상적인 비용 단위이므로 그대로 밀리초로 읽으면 안 된다. 실제 시간도 한 번의 실행 환경에 영향을 받는다.

아래 예제는 PostgreSQL 전용이다. 24행짜리 학습 표에서는 순차 스캔이 합리적일 수 있다. “인덱스가 사용되지 않았으니 실패”가 아니다. 문제를 재현할 때는 실제에 가까운 행 수·분포·선택도·쿼리 조건을 준비하고 출력 행 수가 동일한지도 확인한다.

분석 순서는 실행 시간만 보는 것이 아니라 예상/실제 행 수 차이, 반복 횟수, 많은 데이터를 버리는 필터, 정렬의 메모리·디스크 사용, 버퍼 접근을 함께 보는 것이다. ANALYZE는 데이터를 읽어 통계를 갱신하는 명령이기도 하므로 EXPLAIN ANALYZE의 단어와 문맥을 구분한다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A01.sql
```

```sql
-- PostgreSQL 16, 학습용 데이터베이스에서 실행.
ANALYZE visits;
EXPLAIN (ANALYZE, BUFFERS)
SELECT visit_id, scheduled_start
FROM visits
WHERE branch_id = 1
  AND scheduled_start >= TIMESTAMPTZ '2026-08-01 00:00:00+00'
  AND scheduled_start <  TIMESTAMPTZ '2026-08-04 00:00:00+00'
ORDER BY scheduled_start, visit_id;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

필터를 만족하는 결과는 9행이다. 실제 계획의 모양과 시간은 독자의 환경에서 확인한다. 실행 결과를 “계획 종류, 예상 행, 실제 행, loops, 실행 시간, 버퍼” 열로 기록하고 동일 조건에서 반복 측정한다. 캐시가 찬 실행과 첫 실행을 구분한다.

### 6. 자주 하는 실수

EXPLAIN ANALYZE는 쓰기 쿼리도 실제 실행한다. 운영 UPDATE/DELETE에 무심코 붙이지 않는다. 읽기 쿼리라도 큰 부하가 생길 수 있다. 이 교재는 실행 시간을 꾸며 제시하지 않는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 사용자가 기다리는 시간이 업무에 미치는 영향과 개선 목표를 수치로 합의한다.

**FDSE 관점:** 대표 부하·성능 기준·실행 계획·정합성 회귀 테스트를 함께 기록한다.

### 8. 직접 풀어 보기

**SQL-A01-1. 추정 10행인데 실제 100만 행이면 무엇부터 의심하는가?**

힌트: 통계, 분포, 조건 사이 상관관계를 생각한다.

[풀이 확인](#sql-a01-1)

**SQL-A01-2. 인덱스 생성 뒤 단 한 번 20ms→10ms가 나오면 개선을 확정할 수 있는가?**

힌트: 캐시와 결과 동일성을 분리해 본다.

[풀이 확인](#sql-a01-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/using-explain.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/sql-analyze.html)

---

<a id="sql-a02"></a>
## SQL-A02 · 복합·부분 인덱스와 검색 가능한 조건

**학습 목표:** 자주 쓰는 조회 조건에 맞춰 인덱스를 제안하고 비용을 설명한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

복합 인덱스는 여러 열을 함께 색인한다. 부분 인덱스는 조건을 만족하는 행만 색인한다. 선택도는 조건이 전체 중 얼마나 적은 행을 남기는지와 관련된다. Sargable은 색인을 활용하기 좋은 검색 조건을 뜻하는 실무 표현이다.

### 2. 비유로 잡는 그림

책의 색인을 지점→날짜→방문 번호 순으로 만들면 특정 지점의 날짜 범위를 찾기 쉽지만, 색인 자체를 만들고 유지하는 비용도 생긴다.

### 3. 원리와 업무에서의 의미

PostgreSQL B-tree 복합 인덱스는 선행 열에 대한 조건과 정렬 요구를 함께 고려해 설계한다. 여기서는 지점의 완료 방문을 시간순으로 읽으므로 branch_id, scheduled_start, visit_id 순서를 제안한다. status가 completed인 행만 포함하는 부분 인덱스를 사용한다.

이 인덱스가 모든 쿼리에 유리한 것은 아니다. planned 상태를 찾는 쿼리에는 이 부분 인덱스의 데이터가 없다. 조건이 부분 인덱스의 조건을 충족함을 계획기가 판단할 수 있어야 한다. 바인딩된 매개변수와 일반 계획 등에서는 적용 여부를 실제 계획으로 확인한다.

날짜 열에 함수를 씌워 비교하는 대신 원래 열의 반열린 범위로 표현하면 일반적인 열 인덱스를 활용하기 쉬워진다. 다만 함수를 사용하면 절대 인덱스를 못 쓴다는 뜻은 아니다. 표현식 인덱스 같은 다른 설계가 있다. 아래 생성은 트랜잭션 끝에서 되돌려 실습 상태를 보존한다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A02.sql
```

```sql
-- PostgreSQL 16. 이 데모 인덱스는 ROLLBACK으로 제거된다.
BEGIN;
CREATE INDEX lesson_completed_branch_time
ON visits (branch_id, scheduled_start, visit_id)
WHERE status = 'completed';
EXPLAIN
SELECT visit_id, scheduled_start
FROM visits
WHERE branch_id = 1 AND status = 'completed'
  AND scheduled_start >= TIMESTAMPTZ '2026-08-01 00:00:00+00'
  AND scheduled_start <  TIMESTAMPTZ '2026-08-04 00:00:00+00'
ORDER BY scheduled_start, visit_id;
ROLLBACK;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

branch_id=1인 완료 방문 6행이 목표다. 작은 데이터에서는 새 인덱스가 선택되지 않을 수 있다. 인덱스가 필요한 조회를 먼저 정하고 후보를 만든 다음 실행 계획으로 확인한다. 실제 운영의 CREATE INDEX CONCURRENTLY는 일반 CREATE INDEX와 실행 제약이 다르며 위 트랜잭션 패턴을 그대로 적용하지 않는다.

### 6. 자주 하는 실수

모든 열에 인덱스를 만들면 저장 공간과 INSERT/UPDATE/DELETE 유지 비용이 커진다. INCLUDE를 붙였다고 항상 index-only scan이 되는 것도 아니며 가시성 상태 등 실행 조건이 중요하다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 조회 지연 개선의 가치와 쓰기 지연·운영 복잡성 사이의 우선순위를 정한다.

**FDSE 관점:** 쿼리 패턴별 인덱스 후보와 불필요한 중복 인덱스를 검토한다.

### 8. 직접 풀어 보기

**SQL-A02-1. 한국 날짜 8월 1일만 조회하려면 UTC 경계는?**

힌트: 서울은 UTC+9인 이 실습의 시간 계약을 사용한다.

[풀이 확인](#sql-a02-1)

**SQL-A02-2. planned 조회가 빨라지지 않은 이유를 설명하라.**

힌트: 부분 인덱스 안에 어떤 행이 있는가?

[풀이 확인](#sql-a02-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/indexes-multicolumn.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/indexes-partial.html)
- [공식 문서 3](https://www.postgresql.org/docs/16/indexes-expressional.html)

---

<a id="sql-a03"></a>
## SQL-A03 · 트랜잭션 격리·동시 수정·낙관적 잠금

**학습 목표:** 두 사용자가 같은 업무를 수정할 때 갱신 손실을 방지한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

격리 수준은 동시에 실행되는 트랜잭션이 서로의 변경을 어떻게 보는지 정한다. MVCC는 여러 행 버전을 이용해 동시 접근을 처리하는 방식이다. 낙관적 잠금은 읽은 버전과 수정 시점 버전이 같은지 검사하는 패턴이다.

### 2. 비유로 잡는 그림

같은 예약표를 복사해 간 두 직원이 서로 다른 수정을 할 때, 나중 사람이 먼저 사람의 변경을 모르게 덮어쓰지 않도록 문서 버전 번호를 확인한다.

### 3. 원리와 업무에서의 의미

PostgreSQL의 기본 Read Committed에서는 각 명령이 시작할 때의 적절한 스냅샷을 사용한다. 일반 SELECT를 했다고 다른 사용자의 수정이 자동으로 금지되는 것은 아니다. 애플리케이션이 읽은 값을 오래 보관한 뒤 무조건 덮어쓰면 업무상 갱신 손실이 생길 수 있다.

낙관적 잠금은 `WHERE id=? AND version=읽은_버전`으로 UPDATE하고 성공 시 version을 증가시킨다. 변경 행 수가 0이면 해당 버전의 조건을 충족하지 않았으므로 충돌 또는 대상 없음으로 처리해야 한다. 사용자가 최신 내용을 확인하고 다시 결정하게 할 수 있다.

아래는 같은 세션에서 두 요청을 차례로 재현한 최소 예다. 실제 두 터미널 실습에서는 A와 B가 모두 version=1을 읽은 뒤 A가 먼저 수정하고 커밋하고 B가 이전 버전으로 수정하도록 해 본다. 모든 오류를 무한 재시도하지 말고 직렬화 실패처럼 재시도 가능한 오류는 전체 트랜잭션 범위로 제한된 재시도를 설계한다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A03.sql
```

```sql
-- PostgreSQL 16. 독립적인 임시 표, 실제 visits를 바꾸지 않는다.
BEGIN;
CREATE TEMP TABLE lesson_assignment (
    visit_id INTEGER PRIMARY KEY,
    worker_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 1)
);
INSERT INTO lesson_assignment VALUES (1, 1, 1);
-- 요청 A는 version=1을 읽었다고 가정.
UPDATE lesson_assignment
SET worker_id = 2, version = version + 1
WHERE visit_id = 1 AND version = 1
RETURNING visit_id, worker_id, version;
-- 요청 B도 예전에 읽은 version=1을 제출: 반환 행이 없어야 한다.
UPDATE lesson_assignment
SET worker_id = 3, version = version + 1
WHERE visit_id = 1 AND version = 1
RETURNING visit_id, worker_id, version;
SELECT * FROM lesson_assignment;
ROLLBACK;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

첫 UPDATE는 (1,2,2)를 반환하고 두 번째는 0행을 반환해야 한다. 마지막 상태는 worker_id=2,version=2다. 이 단일 세션 데모는 버전 조건을 보여 줄 뿐 실제 동시성 검증을 대신하지 않는다. 여러 세션 부하 테스트와 오류 처리 테스트가 별도로 필요하다.

### 6. 자주 하는 실수

RLS 때문에 보이지 않는 행, 이미 삭제된 행, 버전 충돌을 무조건 같은 내부 원인이라고 단정하지 않는다. 외부 응답은 정보 노출을 막고 내부 로그는 원인을 진단할 수 있어야 한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 동시 수정 충돌이 났을 때 사용자에게 보여 줄 선택지와 책임자를 정의한다.

**FDSE 관점:** 버전 비교, 변경 행 수 검사, 트랜잭션 경계와 재시도 정책을 구현한다.

### 8. 직접 풀어 보기

**SQL-A03-1. 두 번째 UPDATE가 0행인데 API가 성공을 돌려주면 어떤 문제가 생기는가?**

힌트: 실제 상태와 사용자 믿음이 달라진다.

[풀이 확인](#sql-a03-1)

**SQL-A03-2. SELECT FOR UPDATE는 낙관적 잠금과 무엇이 다른가?**

힌트: 먼저 잠그는 방식과 나중에 버전을 확인하는 방식을 비교한다.

[풀이 확인](#sql-a03-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/transaction-iso.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/explicit-locking.html)

---

<a id="sql-a04"></a>
## SQL-A04 · 업무 Action·조건부 갱신·감사 기록을 하나로 묶기

**학습 목표:** 허용된 상태 전이와 감사 기록을 동일 트랜잭션으로 처리한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

상태 전이는 planned→completed처럼 업무 상태가 바뀌는 규칙이다. 감사 기록(audit)은 누가 무엇을 언제 바꿨는지 남긴 이력이다. 원자성은 관련 변경이 전부 성공하거나 전부 취소되는 성질이다.

### 2. 비유로 잡는 그림

예약 완료 도장을 찍는 일과 담당자의 처리 기록을 남기는 일이 따로 놀면 안 된다. 둘을 한 묶음으로 처리한다.

### 3. 원리와 업무에서의 의미

조회가 정확하다고 운영 시스템이 완성되는 것은 아니다. 사용자가 상태를 변경하는 Action에는 권한, 입력 검증, 허용 상태, 동시 수정, 감사 기록이 필요하다. 이 예제는 planned 상태에 대해서만 completed로 변경하고 실제로 변경된 행만 감사 표에 기록한다.

PostgreSQL의 data-modifying CTE와 RETURNING을 사용해 변경된 행을 다음 INSERT의 입력으로 연결한다. 같은 요청을 두 번 실행하면 첫 번째만 planned 조건을 만족하므로 변경과 감사 행이 한 번씩 생긴다. 이것은 이 상태 전이에서의 재실행 안전성이지 모든 업무에 적용되는 전역 exactly-once 보장은 아니다.

외부 결제나 이메일 전송은 DB 트랜잭션만으로 되돌릴 수 없다. 외부 부작용이 있으면 idempotency key, outbox, 소비자 중복 제거와 재시도 전략을 별도로 설계한다. 아래 actor는 학습용 상수이며 실제 서버는 검증된 로그인 주체에서 가져와야 한다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A04.sql
```

```sql
-- PostgreSQL 16. 임시 표에서만 상태 전이와 감사 기록을 실험.
BEGIN;
CREATE TEMP TABLE lesson_jobs (
  job_id INTEGER PRIMARY KEY,
  status TEXT NOT NULL CHECK (status IN ('planned','completed'))
);
CREATE TEMP TABLE lesson_audit (
  audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  job_id INTEGER NOT NULL,
  actor TEXT NOT NULL,
  new_status TEXT NOT NULL
);
INSERT INTO lesson_jobs VALUES (1,'planned');
WITH changed AS (
  UPDATE lesson_jobs SET status='completed'
  WHERE job_id=1 AND status='planned'
  RETURNING job_id,status
)
INSERT INTO lesson_audit(job_id,actor,new_status)
SELECT job_id,'demo-operator',status FROM changed;
-- 같은 요청을 재실행해도 이미 completed이면 추가 감사 행이 생기지 않는다.
WITH changed AS (
  UPDATE lesson_jobs SET status='completed'
  WHERE job_id=1 AND status='planned'
  RETURNING job_id,status
)
INSERT INTO lesson_audit(job_id,actor,new_status)
SELECT job_id,'demo-operator',status FROM changed;
SELECT COUNT(*) AS audit_rows FROM lesson_audit;
ROLLBACK;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

감사 행은 1개가 기대된다. 변경이 없는 두 번째 요청을 성공한 재요청으로 볼지, 상태 충돌로 볼지는 API 계약에서 정한다. 사용자 재요청에 같은 결과를 돌려줘야 한다면 요청 식별자와 응답 보관도 필요할 수 있다.

### 6. 자주 하는 실수

Action 권한을 버튼 숨김만으로 구현하지 않는다. 서버와 데이터 접근 계층에서 검증해야 한다. 변경 전후 값·사유·요청 ID 등을 무엇까지 보관할지 개인정보·감사 정책과 함께 정한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 누가 어떤 조건에서 변경하며 잘못된 변경을 어떻게 바로잡는지 업무 규칙을 작성한다.

**FDSE 관점:** 상태 전이, 감사 기록, 충돌, 재시도와 외부 부작용의 경계를 테스트한다.

### 8. 직접 풀어 보기

**SQL-A04-1. 감사 INSERT가 실패하면 UPDATE도 취소되어야 하는가?**

힌트: 감사 없는 변경을 허용하는지 요구사항을 생각한다.

[풀이 확인](#sql-a04-1)

**SQL-A04-2. 완료 처리 후 이메일을 보내다가 실패했다면 UPDATE를 다시 하면 되는가?**

힌트: DB 상태와 이메일은 서로 다른 자원이다.

[풀이 확인](#sql-a04-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-with.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/dml-returning.html)

---

<a id="sql-a05"></a>
## SQL-A05 · 증분 적재·UPSERT·늦게 도착하는 데이터

**학습 목표:** 신규·수정 이벤트를 안정적으로 반영하고 진행 위치의 의미를 설명한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

증분 적재는 전체가 아니라 새로 도착하거나 변경된 일부를 처리한다. UPSERT는 키가 없으면 추가하고 있으면 조건에 따라 갱신한다. 워터마크는 어디까지 처리했다고 기록한 진행 위치다.

### 2. 비유로 잡는 그림

일기장 전체를 매번 다시 쓰지 않고 새로 도착한 수정 메모를 반영한다. 늦게 온 오래된 메모가 최신 내용을 덮어쓰지 않도록 버전을 비교한다.

### 3. 원리와 업무에서의 의미

증분 적재에서 “ID가 커진 행만 읽는다”는 규칙은 수정·삭제를 놓칠 수 있다. updated_at 같은 시각만 사용해도 같은 시각의 여러 이벤트, 역순 도착, 시계 오차가 문제가 된다. 원천이 제공하는 단조 증가 순서 번호나 변경 로그의 의미를 먼저 확인한다.

아래는 원천이 visit_id별 source_version을 안정적으로 제공한다고 가정한다. 새 행은 추가하고 기존 행보다 큰 버전일 때만 갱신한다. 같은 배치에 같은 키가 여러 번 있으면 INSERT ... ON CONFLICT 전에 키별 최신 이벤트로 줄여야 한다. 한 명령이 동일 대상 행을 여러 번 수정하려는 상황을 그대로 넘기지 않는다.

타깃 반영 전에 워터마크부터 올리면 장애 때 데이터를 건너뛸 수 있다. 동일 DB 내에서는 타깃 반영과 진행 상태를 같은 트랜잭션으로 묶는 방법을 검토한다. 원천 읽기와 타깃 쓰기가 분산되어 있으면 원자성이 저절로 생기지 않는다. 재처리 가능한 로그·겹친 읽기 구간·멱등 키가 필요하다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A05.sql
```

```sql
-- PostgreSQL 16. 원천 버전이 신뢰 가능하다는 명시적 계약.
BEGIN;
CREATE TEMP TABLE lesson_state (
  visit_id INTEGER PRIMARY KEY,
  status TEXT NOT NULL,
  source_version BIGINT NOT NULL
);
INSERT INTO lesson_state VALUES (101,'planned',1);
INSERT INTO lesson_state AS current(visit_id,status,source_version)
VALUES (101,'completed',3),(102,'planned',1)
ON CONFLICT (visit_id) DO UPDATE
SET status=EXCLUDED.status, source_version=EXCLUDED.source_version
WHERE EXCLUDED.source_version > current.source_version;
-- 늦게 도착한 구버전은 무시한다.
INSERT INTO lesson_state AS current(visit_id,status,source_version)
VALUES (101,'cancelled',2)
ON CONFLICT (visit_id) DO UPDATE
SET status=EXCLUDED.status, source_version=EXCLUDED.source_version
WHERE EXCLUDED.source_version > current.source_version;
SELECT * FROM lesson_state ORDER BY visit_id;
ROLLBACK;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

기대 상태는 101/completed/3, 102/planned/1이다. cancelled/2가 나중에 도착했지만 최신 상태를 덮어쓰지 않는다. 현재 상태 표만으로는 버려진 구버전이나 모든 변경 이력을 추적할 수 없으므로 원본 이벤트 보관과 별개로 생각한다.

### 6. 자주 하는 실수

같은 버전인데 내용이 다른 이벤트를 조용히 무시하면 원천 오류를 숨길 수 있다. 충돌 탐지·격리·원천 계약 확인을 추가한다. 삭제는 tombstone 같은 별도 표현이 필요할 수 있다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 데이터 신선도 목표와 정정 반영 시간을 사용자와 정한다.

**FDSE 관점:** 재실행·역순 도착·같은 버전 충돌·삭제·장애 후 복구를 검증한다.

### 8. 직접 풀어 보기

**SQL-A05-1. 워터마크를 100으로 저장한 뒤 91~100 반영 중 실패하면?**

힌트: 다음 실행이 어디서 시작하는가?

[풀이 확인](#sql-a05-1)

**SQL-A05-2. updated_at만 같은 두 이벤트의 순서를 어떻게 정하는가?**

힌트: 업무 의미가 있는 순서와 임의 순서를 구분한다.

[풀이 확인](#sql-a05-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/sql-insert.html)

---

<a id="sql-a06"></a>
## SQL-A06 · 시점 일치·지연 도착·데이터 누수 방지

**학습 목표:** 사건 발생 시각과 시스템이 알게 된 시각을 분리해 과거 판단을 재현한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

event time은 사건이 일어난 시각이고 available time은 그 정보가 시스템에 사용 가능해진 시각이다. point-in-time correct는 판단 당시 알 수 있던 정보만 사용하는 원칙이다. 데이터 누수는 당시 알 수 없던 정보가 평가에 섞이는 문제다.

### 2. 비유로 잡는 그림

월요일 회의에서 어떤 결정을 할 수 있었는지 평가하면서 수요일에 도착한 정정 보고서를 미리 알고 있었다고 가정하면 안 된다.

### 3. 원리와 업무에서의 의미

과거 고객 상태를 연결할 때 valid_from/valid_to만 맞추면 충분하지 않을 수 있다. 실제 사건은 8월 1일이지만 원천 지연으로 8월 3일에 처음 알게 된 정보라면 8월 2일 의사결정에는 쓸 수 없었다. 업무상 유효한 시각과 기록이 알려진 시각의 두 축이 필요하다.

아래는 각 이벤트의 event_time과 available_at을 보관한 최소 예다. cutoff 이전에 발생했고 cutoff 이전에 알려진 이벤트만 후보로 삼은 뒤 최신 사건을 고른다. 모든 시각은 UTC ISO 문자열의 동일 정규 형식이라 SQLite에서도 문자열 비교가 가능하도록 제한했다. PostgreSQL 실제 표에서는 TIMESTAMPTZ 등 적절한 타입을 사용한다.

실제 정정·취소·버전 이력이 복잡하면 이 예제만으로 완전한 이중 시점 모델이 되는 것은 아니다. “현재 알려진 진실로 과거를 다시 계산”할 것인지 “당시 알려진 정보로 판단을 재현”할 것인지 목적을 구분해야 한다. 머신러닝 특징 생성과 운영 지표 감사 모두 이 구분이 중요하다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_A06.sql
```

```sql
WITH events(client_id,event_time,available_at,status,event_id) AS (
  VALUES
  (1,'2026-08-01T01:00:00+00:00','2026-08-01T02:00:00+00:00','active',1),
  (1,'2026-08-01T03:00:00+00:00','2026-08-03T00:00:00+00:00','paused',2)
), known AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY client_id ORDER BY event_time DESC,event_id DESC
  ) AS rn
  FROM events
  WHERE event_time < '2026-08-02T00:00:00+00:00'
    AND available_at < '2026-08-02T00:00:00+00:00'
)
SELECT client_id,status,event_id FROM known WHERE rn=1;
```

### 5. 결과와 코드 해설

| client_id | status | event_id |
| --- | --- | --- |
| 1 | active | 1 |

8월 2일 시점에서 기대 상태는 active/event_id=1이다. 두 번째 사건은 8월 1일에 발생했지만 8월 3일에야 알려졌으므로 제외된다. available_at 조건을 없애면 당시 몰랐던 paused를 사용하게 된다.

### 6. 자주 하는 실수

학습 시점 이후 정보가 섞이면 모델 성능이나 정책 효과가 실제보다 좋아 보일 수 있다. 현재 표만 저장하면 당시 상태를 재현하지 못할 수 있으므로 이력 보관 요구를 미리 정한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** “당시 알 수 있었는가?”를 결과 설명과 의사결정 평가의 기본 질문으로 삼는다.

**FDSE 관점:** event/ingestion/available 시간 정의, 시점 JOIN과 재현 테스트를 구현한다.

### 8. 직접 풀어 보기

**SQL-A06-1. cutoff를 8월 4일로 바꾸면 어떤 이벤트가 선택되는가?**

힌트: 두 시간 조건을 모두 만족한 후보 중 최신 사건을 고른다.

[풀이 확인](#sql-a06-1)

**SQL-A06-2. 현재 상태 하나만 저장한 표로 8월 2일의 판단을 완벽히 재현할 수 있는가?**

힌트: 과거 정보와 변경 시점을 보관했는가?

[풀이 확인](#sql-a06-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/tutorial-window.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/datatype-datetime.html)

---

<a id="sql-a07"></a>
## SQL-A07 · 재귀 CTE·의존성 탐색·순환 제어

**학습 목표:** 계층과 그래프를 SQL로 탐색하며 무한 반복을 방지한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

재귀 CTE는 초기 결과에 반복 규칙을 적용해 다음 결과를 만든다. anchor는 시작 부분이고 recursive term은 반복 부분이다. 도달 가능성은 연결을 따라 어떤 정점까지 갈 수 있는지 뜻한다.

### 2. 비유로 잡는 그림

어떤 원천 표가 잘못되었을 때 연결된 보고서를 한 단계씩 따라가며 전체 영향 목록을 만든다.

### 3. 원리와 업무에서의 의미

재귀는 같은 구조의 작업을 더 작은 단계로 반복하는 방식이다. SQL 재귀 CTE에서는 시작 정점을 먼저 만들고 현재 결과와 간선을 JOIN해 다음 정점을 찾는다. 조직도·구성 부품·데이터 계보 같은 관계에 사용할 수 있다.

아래는 정점 이름만 출력하고 UNION으로 이미 나온 정점을 중복 제거한다. 순환 간선이 있어도 새로운 정점이 더 나오지 않으면 멈춘다. Python BFS 강의와 동일한 도달 가능성 문제를 SQL로 표현한다. 출력 ORDER BY는 최종 표시 순서이지 탐색 순서의 보장이 아니다.

깊이(depth)나 경로(path)를 함께 행에 넣으면 같은 정점이어도 깊이/경로 값이 달라져 UNION만으로 순환을 제거하지 못할 수 있다. 이런 경우 명시적인 경로 방문 검사나 PostgreSQL CYCLE 기능 등 목적에 맞는 제어가 필요하다. 임의 깊이 제한은 안전장치일 수 있지만 누락을 조용히 정상 결과로 표시하면 안 된다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_A07.sql
```

```sql
WITH RECURSIVE edges(parent,child) AS (
  VALUES ('clients','visits'),('visits','invoices'),
         ('invoices','payments'),('payments','clients'),
         ('workers','visits')
), reachable(node) AS (
  SELECT 'clients'
  UNION
  SELECT edges.child
  FROM edges JOIN reachable ON edges.parent=reachable.node
)
SELECT node FROM reachable ORDER BY node;
```

### 5. 결과와 코드 해설

| node |
| --- |
| clients |
| invoices |
| payments |
| visits |

clients,invoices,payments,visits 네 정점이 나온다. workers는 역방향의 시작점이라 clients에서 따라가는 방향으로 도달하지 않는다. payments→clients 순환이 있어도 node만을 중복 제거하므로 종료한다.

### 6. 자주 하는 실수

UNION ALL로 바꾸면 이 순환 그래프에서 결과가 계속 늘어날 수 있다. 운영에서 무제한 재귀 쿼리를 실행하지 말고 입력·순환 정책·자원 제한을 확인한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 영향 범위를 설명할 때 연결 방향과 누락 가능성을 함께 전달한다.

**FDSE 관점:** 순환·다중 경로·고립 정점과 접근 권한을 테스트한다.

### 8. 직접 풀어 보기

**SQL-A07-1. UNION을 UNION ALL로 바꾸면 무엇이 달라지는가?**

힌트: clients가 다시 발견되었을 때 제거되는가?

[풀이 확인](#sql-a07-1)

**SQL-A07-2. clients에서 workers까지의 영향이 필요하면 간선을 거꾸로 추가하면 되는가?**

힌트: 이 관계가 실제 업무 의존성인지 따져 본다.

[풀이 확인](#sql-a07-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-with.html)

---

<a id="sql-a08"></a>
## SQL-A08 · 행 수준 보안·최소 권한·테넌트 격리

**학습 목표:** 사용자 지점 필터와 실제 데이터 접근 통제를 구분한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

인증은 사용자가 누구인지 확인하고 인가는 무엇을 할 수 있는지 판단한다. RLS는 DB가 행별 접근 정책을 적용하는 기능이다. 테넌트는 데이터를 논리적으로 분리해야 하는 고객 조직 단위다.

### 2. 비유로 잡는 그림

화면에서 다른 지점 메뉴를 숨기는 것과 창고 열쇠가 다른 지점 물건을 실제로 열지 못하게 하는 것은 다르다.

### 3. 원리와 업무에서의 의미

아래 PostgreSQL 데모는 전용 임시 실습 역할을 만들고 branch_id=1에 해당하는 행만 읽게 한다. 역할 생성 권한이 있는 격리된 학습 DB 관리자 세션에서만 실행한다. transaction 끝에 ROLLBACK하여 표·정책·역할을 제거한다. 운영 역할이나 운영 표에는 적용하지 않는다.

일반적인 RLS에서는 수퍼유저나 BYPASSRLS 역할, 표 소유자 등 적용 예외를 고려해야 한다. 이 예제에서는 표를 만든 관리자와 실제 SELECT를 하는 NOLOGIN/NOBYPASSRLS 역할을 분리한다. NOLOGIN은 직접 로그인할 수 없다는 뜻이지 역할 전환이나 권한이 자동으로 사라진다는 뜻은 아니다.

실제 다중 지점 시스템에서는 로그인 주체와 허용 지점의 관계를 검증된 인증 결과에서 결정해야 한다. 사용자가 보낸 branch_id를 그대로 신뢰하면 안 된다. current_setting 기반 정책도 신뢰된 서버만 세션 값을 설정하는 통제 없이 사용하면 우회될 수 있다. 연결 풀에서 사용자별 상태가 남지 않도록 트랜잭션 범위와 초기화도 설계한다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A08.sql
```

```sql
-- PostgreSQL 16 관리자 권한 필요. 전용 로컬 학습 DB에서만 실행.
-- 같은 이름의 기존 역할/표가 있으면 중단하고 이름 충돌을 먼저 확인한다.
BEGIN;
CREATE ROLE lesson_branch_reader NOLOGIN NOBYPASSRLS;
CREATE TABLE lesson_rls_visits(visit_id INTEGER PRIMARY KEY,branch_id INTEGER NOT NULL);
INSERT INTO lesson_rls_visits VALUES (1,1),(2,2);
ALTER TABLE lesson_rls_visits ENABLE ROW LEVEL SECURITY;
CREATE POLICY lesson_branch_one ON lesson_rls_visits
  FOR SELECT TO lesson_branch_reader
  USING (branch_id=1);
GRANT SELECT ON lesson_rls_visits TO lesson_branch_reader;
SET LOCAL ROLE lesson_branch_reader;
SELECT * FROM lesson_rls_visits ORDER BY visit_id;
RESET ROLE;
ROLLBACK;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

독립된 reader 역할의 SELECT는 visit_id=1,branch_id=1만 반환해야 한다. 관리자 역할로 실행한 SELECT가 모두 보인다는 이유로 RLS가 실패했다고 단정하지 않는다. 실제 애플리케이션 역할로 테스트해야 한다. 역할 생성이 허용되지 않는 환경에서는 권한 있는 관리자의 준비가 필요하며 자동으로 우회하지 않는다.

### 6. 자주 하는 실수

RLS만으로 API·파일 내보내기·캐시·로그의 유출이 모두 해결되지는 않는다. 모든 접근 경로를 확인하고 SELECT뿐 아니라 INSERT/UPDATE의 WITH CHECK 정책도 요구에 맞게 설계한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 지점 사용자·본부 분석가·관리자의 권한 표와 승인 과정을 작성한다.

**FDSE 관점:** 실제 서비스 역할로 교차 지점 조회·쓰기·풀 재사용·오류 노출을 검증한다.

### 8. 직접 풀어 보기

**SQL-A08-1. WHERE branch_id=사용자입력만 있으면 지점 격리가 되는가?**

힌트: 그 사용자가 그 지점에 접근해도 되는지 확인했는가?

[풀이 확인](#sql-a08-1)

**SQL-A08-2. 관리자 계정의 RLS 테스트만 통과하면 충분한가?**

힌트: 실제 앱 역할과 예외 적용 여부가 다른가?

[풀이 확인](#sql-a08-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/ddl-rowsecurity.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/sql-createrole.html)

---

<a id="sql-a09"></a>
## SQL-A09 · 파티셔닝·JSONB·물리 설계의 선택

**학습 목표:** 핵심 업무 열과 유연한 부가 정보를 구분하고 데이터 분할의 조건을 설명한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

파티셔닝은 하나의 논리적 표를 규칙에 따라 물리적인 여러 부분으로 나눈다. partition pruning은 조건상 불필요한 부분을 읽지 않는 최적화다. JSONB는 PostgreSQL의 구조화된 JSON 저장 타입이다.

### 2. 비유로 잡는 그림

연도별 서류함으로 보관하되 고객 번호와 처리 상태는 표준 양식에 쓰고, 선택적 비고만 자유 양식에 넣는 방식이다.

### 3. 원리와 업무에서의 의미

월별 방문 이벤트가 크게 늘어나고 시간 범위 조회·보관 기한 관리가 중요하다면 날짜 파티셔닝을 검토할 수 있다. 하지만 작은 표를 나누는 것 자체가 성능 개선을 보장하지 않는다. 파티션 생성·인덱스·백업·삭제·늦게 도착하는 데이터 처리의 운영 비용이 증가한다.

status나 branch_id처럼 자주 검증하고 연결하고 필터하는 핵심 열은 명확한 타입과 제약을 갖춘 일반 열로 두는 편이 적절할 수 있다. 선택적인 원천 부가 정보에는 JSONB를 사용할 수 있다. JSONB가 있다는 이유로 모든 업무 구조를 아무 검증 없이 한 열에 넣지 않는다.

아래는 8월 파티션 하나만 만든 격리된 데모다. 9월 데이터를 넣으면 대응 파티션이 없으므로 실패한다. 이를 알고 파티션을 미리 생성하거나 격리/기본 파티션 정책을 설계해야 한다. 파티션 표의 고유성 제약에는 파티션 키 관련 제약이 있으므로 무조건 전체 event_id 고유성이 보장된다고 가정하지 않는다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A09.sql
```

```sql
-- PostgreSQL 16. ROLLBACK으로 모든 데모 객체 제거.
BEGIN;
CREATE TABLE lesson_events (
  event_id INTEGER NOT NULL,
  event_day DATE NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('planned','completed')),
  metadata JSONB NOT NULL,
  PRIMARY KEY(event_id,event_day)
) PARTITION BY RANGE(event_day);
CREATE TABLE lesson_events_202608 PARTITION OF lesson_events
FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
INSERT INTO lesson_events VALUES
(1,'2026-08-01','completed','{"source":"demo","priority":"normal"}'::jsonb);
SELECT event_id,metadata->>'source' AS source
FROM lesson_events
WHERE event_day >= DATE '2026-08-01' AND event_day < DATE '2026-09-01';
EXPLAIN SELECT event_id FROM lesson_events
WHERE event_day >= DATE '2026-08-01' AND event_day < DATE '2026-09-01';
ROLLBACK;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

SELECT는 event_id=1,source=demo를 반환해야 한다. ->>는 JSON 속성을 텍스트로 꺼낸다. 현재 예제는 한 파티션뿐이므로 여러 파티션을 생략하는 실질적인 성능 효과를 입증하지 않는다. 여러 달의 대표 데이터와 조건으로 pruning 여부를 확인한다.

### 6. 자주 하는 실수

JSON에 개인정보를 몰아 넣으면 접근 통제·삭제·스키마 변화 관리가 어려워질 수 있다. 핵심 필드 계약, 허용 키, 보관 정책을 정한다. 파티션 삭제는 데이터 삭제이므로 운영 승인 없이 수행하지 않는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 데이터 보관 기간, 감사 재현, 조회 패턴을 요구사항으로 만든다.

**FDSE 관점:** 파티션 키·고유성·늦은 데이터·DDL 운영·JSON 검증을 설계한다.

### 8. 직접 풀어 보기

**SQL-A09-1. 2026-09-01 행을 넣으면 어디에 들어가는가?**

힌트: [8월1일,9월1일) 경계를 확인한다.

[풀이 확인](#sql-a09-1)

**SQL-A09-2. PRIMARY KEY(event_id,event_day)는 event_id 단독 고유성을 보장하는가?**

힌트: 같은 ID와 다른 날짜 조합을 생각한다.

[풀이 확인](#sql-a09-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/ddl-partitioning.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/datatype-json.html)
- [공식 문서 3](https://www.postgresql.org/docs/16/functions-json.html)

---

<a id="sql-a10"></a>
## SQL-A10 · 배포 전 품질 게이트·대사·운영 지표 계약

**학습 목표:** 잘못된 데이터를 정상 결과로 배포하지 않도록 검사 쿼리와 운영 기준을 만든다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

품질 게이트는 통과 조건을 만족해야 다음 단계로 진행시키는 검사다. 대사(reconciliation)는 독립적으로 계산한 합계나 상태가 일치하는지 확인하는 일이다. materialized view는 조회 결과를 물리적으로 저장해 재사용하는 구조다.

### 2. 비유로 잡는 그림

보고서를 보내기 전에 영수증 합계와 회계 장부가 맞는지, 빠진 고객이 없는지, 데이터가 오래되지 않았는지 출고 검사를 한다.

### 3. 원리와 업무에서의 의미

좋은 SQL 한 개보다 그 SQL이 계속 맞는다는 증거가 중요하다. 키 중복·외래키 누락 같은 구조 검사, 음수 금액 같은 값 검사, 결측 완료 시각 같은 업무 품질 검사, 원천과 타깃 합계 대사를 구분한다. 결측이 있다고 무조건 전체 업무를 중단할지는 업무 영향에 따라 결정한다.

아래 검사는 여러 결과를 같은 모양인 check_name,violation_count로 묶는다. 청구 합계와 사전 집계한 입금/잔액 합계의 관계도 검사한다. 이 등식은 같은 식에서 유도되므로 혼자서는 독립적인 원천 대사가 아니다. 별도 원천 통제 합계와 행 수, 누락된 키 집합도 함께 확인해야 한다.

대시보드를 빠르게 만들기 위해 materialized view나 집계 표를 도입하면 새로고침 시각과 허용 지연을 계약에 포함한다. “빠른데 하루 전 데이터”가 지금 필요한 의사결정에 부적합할 수 있다. 배포에는 SQL 결과·품질 상태·데이터 기준 시각·변경 이력을 함께 내보내는 설계가 필요하다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_A10.sql
```

```sql
WITH paid AS (
 SELECT invoice_id,SUM(amount_cents) AS paid_cents
 FROM payments GROUP BY invoice_id
), reconciled AS (
 SELECT i.invoice_id,i.amount_cents,COALESCE(p.paid_cents,0) AS paid_cents,
        i.amount_cents-COALESCE(p.paid_cents,0) AS balance_cents
 FROM invoices i LEFT JOIN paid p ON p.invoice_id=i.invoice_id
)
SELECT 'duplicate_visit_key' AS check_name,
       COUNT(*)-COUNT(DISTINCT visit_id) AS violation_count FROM visits
UNION ALL
SELECT 'orphan_payment',COUNT(*)
FROM payments p LEFT JOIN invoices i ON i.invoice_id=p.invoice_id
WHERE i.invoice_id IS NULL
UNION ALL
SELECT 'completed_missing_start',COUNT(*) FROM visits
WHERE status='completed' AND actual_start IS NULL
UNION ALL
SELECT 'invoice_arithmetic_mismatch',COUNT(*) FROM reconciled
WHERE amount_cents <> paid_cents+balance_cents
ORDER BY check_name;
```

### 5. 결과와 코드 해설

| check_name | violation_count |
| --- | --- |
| completed_missing_start | 3 |
| duplicate_visit_key | 0 |
| invoice_arithmetic_mismatch | 0 |
| orphan_payment | 0 |

결과는 completed_missing_start=3이고 나머지 세 검사는 0이다. 3건을 조용히 0분 지연으로 채우지 않는다. 이번 교육 계약에서는 품질 경고와 제외 수를 함께 표시하며 지연율은 6/15=40%로 계산한다. 실제 허용 임계값과 차단 여부는 사용자·운영 책임자가 정한다.

### 6. 자주 하는 실수

제약이 이미 막는 항목의 검사 결과 0만 모아 데이터가 완벽하다고 주장하지 않는다. 아직 수집되지 않은 방문, 잘못된 업무 정의, 오래된 원천은 별도 검사가 필요하다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 지표 정의서·오류 처리 담당자·신선도 경고·복구 후 소통 방식을 승인받는다.

**FDSE 관점:** 검사 자동화, 실패 시 배포 차단, 원천 대사, 모니터링과 롤백을 구현한다.

### 8. 직접 풀어 보기

**SQL-A10-1. 결측 3건을 0분으로 채우면 지연율은 어떻게 달라지는가?**

힌트: 분자와 분모가 바뀌는지 본다.

[풀이 확인](#sql-a10-1)

**SQL-A10-2. 집계 표는 빠르지만 마지막 갱신이 어제다. 어떻게 표시하고 운영하는가?**

힌트: 성능 외에 데이터 기준 시각과 의사결정 적합성을 생각한다.

[풀이 확인](#sql-a10-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/ddl-constraints.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/rules-materializedviews.html)



---
