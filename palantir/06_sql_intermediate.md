# SQL 중급: 복잡한 데이터에서 믿을 수 있는 지표 만들기

**구성:** 10강 · 연습문제 20개 · DS/FDSE 역할별 적용 과제

SQL 기본 10강과 Python의 자료형·함수 개념이 선행입니다. JOIN의 행 수 변화, 시간의 의미, 지표의 분모를 설명할 수 있는 것이 핵심입니다.

**사용 방법:** 모든 명령은 압축을 푼 폴더의 `lab/`에서 실행합니다. 아직 환경을 만들지 않았다면 [환경과 데이터 사전](#book-02)을 먼저 읽으세요. 각 강의의 설명형 해설은 본문에, 연습문제 정답은 [해설집](#book-09)에 있습니다.

## 강의 지도

- [SQL-I01 서브쿼리·CTE·논리적 실행 순서: 긴 질문을 단계로 나누기](#sql-i01)
- [SQL-I02 EXISTS·NOT EXISTS·안티 조인: “한 번도 없는 고객” 찾기](#sql-i02)
- [SQL-I03 JOIN 부풀림·사전 집계·금액 대사: 합계가 커지는 이유](#sql-i03)
- [SQL-I04 윈도 함수·ROW_NUMBER·RANK: 행을 유지하며 순위 만들기](#sql-i04)
- [SQL-I05 LAG·LEAD·누적 합·프레임: 시간에 따른 변화 읽기](#sql-i05)
- [SQL-I06 시간대·날짜 달력·빈 구간: 0건과 미수집을 구별하기](#sql-i06)
- [SQL-I07 중복 제거·최신 이벤트·품질 쿼리: 좋은 행과 나쁜 행을 나누기](#sql-i07)
- [SQL-I08 코호트·활성·리텐션: 고객 집단을 올바르게 비교하기](#sql-i08)
- [SQL-I09 정규화·스타 스키마·이력: 현재 지점과 당시 지점](#sql-i09)
- [SQL-I10 지표 마트·교차 검증: 지연율을 설명 가능한 결과로](#sql-i10)

---

<a id="sql-i01"></a>
## SQL-I01 · 서브쿼리·CTE·논리적 실행 순서: 긴 질문을 단계로 나누기

**학습 목표:** 복잡한 질문을 이름 있는 중간 결과로 분해한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

서브쿼리는 다른 쿼리 안에 들어가는 쿼리다. CTE(Common Table Expression)는 WITH로 이름 붙인 중간 쿼리다. 논리적 실행 순서는 결과 의미를 이해하기 위한 순서이며 실제 실행 계획과는 다를 수 있다.

### 2. 비유로 잡는 그림

한 번에 긴 보고서를 쓰지 않고 “대상 방문 → 지점 요약 → 기준 충족 지점”의 중간 표를 만든다.

### 3. 원리와 업무에서의 의미

복잡한 SQL을 한 줄로 줄이는 것이 실력이 아니다. 단계마다 입력 grain과 출력 grain을 정하면 논리가 드러난다. 첫 CTE는 완료 방문만 고르고, 두 번째는 지점별 요약으로 바꾸고, 마지막 SELECT는 의사결정 기준에 맞는 지점을 고른다.

개념적으로 FROM/JOIN, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT를 따라가면 조건의 위치를 이해하기 쉽다. 실제 DB는 같은 의미를 유지하면서 실행 순서를 바꿀 수 있으므로 이것을 물리적인 처리 순서라고 단정하지 않는다.

CTE를 쓴다고 무조건 임시 표가 물리적으로 저장되거나 더 빨라지는 것은 아니다. PostgreSQL은 조건에 따라 CTE를 인라인하거나 물질화할 수 있다. 우선 가독성과 검증을 위해 사용하고, 성능은 EXPLAIN으로 확인한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I01.sql
```

```sql
WITH completed AS (
    SELECT visit_id, branch_id, fee_cents
    FROM visits
    WHERE status='completed'
), branch_totals AS (
    SELECT branch_id, COUNT(*) AS n, SUM(fee_cents) AS fee_cents
    FROM completed
    GROUP BY branch_id
)
SELECT branch_id, n, fee_cents
FROM branch_totals
WHERE n >= 5
ORDER BY branch_id;
```

### 5. 결과와 코드 해설

| branch_id | n | fee_cents |
| --- | --- | --- |
| 1 | 6 | 63000 |
| 2 | 9 | 126000 |

completed의 grain은 방문, branch_totals의 grain은 지점이다. 마지막 WHERE의 n은 이미 만들어진 집계 결과 열이므로 사용할 수 있다. 같은 SELECT 단계에서 만든 별칭을 어디서 쓸 수 있는지는 엔진과 문맥에 따라 다르므로 중간 CTE로 분리하면 명확하다.

### 6. 자주 하는 실수

CTE 이름만 바꿔도 설계가 좋아지는 것은 아니다. 각 단계의 의미와 grain, 예상 행 수를 설명해야 한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 문제를 작은 검증 가능한 질문으로 분해한다.

**FDSE 관점:** 중간 단계별 테스트와 실행 계획 검토를 수행한다.

### 8. 직접 풀어 보기

**SQL-I01-1. 완료 방문 비용 합계가 60000 cents 이상인 지점을 조회하도록 바꿔라.**

힌트: 최종 조건을 비용 합계에 적용한다.

[풀이 확인](#sql-i01-1)

**SQL-I01-2. CTE가 항상 성능을 높인다는 주장에 답하라.**

힌트: 논리 구조와 실행 계획을 분리한다.

[풀이 확인](#sql-i01-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-with.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/queries-overview.html)

---

<a id="sql-i02"></a>
## SQL-I02 · EXISTS·NOT EXISTS·안티 조인: “한 번도 없는 고객” 찾기

**학습 목표:** 존재 여부만 묻는 질문을 중복 없이 표현한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

EXISTS는 하위 쿼리에 행이 있는지 검사한다. NOT EXISTS는 없는지 검사한다. 안티 조인(anti join)은 상대 표에 대응 행이 없는 대상을 찾는 논리 패턴이다.

### 2. 비유로 잡는 그림

고객별 방문 횟수를 모두 펼치기보다 “이 고객의 완료 기록이 한 장이라도 있는가?”만 확인한다.

### 3. 원리와 업무에서의 의미

고객 목록을 방문 표와 JOIN한 뒤 DISTINCT로 다시 줄일 수도 있지만, 존재 여부만 필요하면 EXISTS가 질문의 뜻을 직접 드러낸다. 하위 쿼리 안에서 바깥 고객 ID를 참조하는 것을 상관 서브쿼리라고 한다.

NOT IN에는 NULL 함정이 있다. 하위 결과에 NULL이 포함되면 비교가 unknown이 되어 예상한 미방문 고객이 나오지 않을 수 있다. 관련 키가 NULL일 수 있는지 확실하지 않다면 NOT EXISTS로 존재하지 않음을 표현하는 편이 명확하다.

“한 번도 방문하지 않음”과 “완료 방문이 없음”은 다르다. 이 자료의 3번 고객은 취소만 있고, 7번 고객은 예정만 있다. 두 고객 모두 방문 기록 자체는 있지만 완료 경험은 없다. 분석 목적에 맞는 상태를 하위 쿼리에서 제한한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I02.sql
```

```sql
SELECT c.client_id, c.branch_id
FROM clients c
WHERE NOT EXISTS (
    SELECT 1
    FROM visits v
    WHERE v.client_id = c.client_id
      AND v.status = 'completed'
)
ORDER BY c.client_id;
```

### 5. 결과와 코드 해설

| client_id | branch_id |
| --- | --- |
| 3 | 1 |
| 7 | 3 |
| 9 | 3 |
| 10 | 4 |
| 11 | 4 |
| 12 | 4 |

SELECT 1의 숫자는 존재 여부를 확인하기 위한 관례적인 값이다. 고객별 하위 조건에 맞는 완료 방문이 없을 때만 바깥 고객을 남긴다. 결과는 3,7,9,10,11,12번 고객이다. 같은 고객에게 방문이 여러 건 있어도 고객은 한 행이다.

### 6. 자주 하는 실수

고객이 계약 만료·휴면·신규인지 확인하지 않고 “완료가 없다”는 이유로 모두 영업 연락 대상으로 만들지 않는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 활성·이탈·미사용 고객의 업무 정의를 구분한다.

**FDSE 관점:** NULL 키·다중 방문·상태 필터를 포함하는 존재성 테스트를 만든다.

### 8. 직접 풀어 보기

**SQL-I02-1. 상태와 무관하게 방문 기록이 전혀 없는 고객을 구하라.**

힌트: 하위 쿼리에서 상태 조건만 제거한다.

[풀이 확인](#sql-i02-1)

**SQL-I02-2. EXISTS 대신 JOIN을 쓰면 어떤 추가 처리가 필요할 수 있는가?**

힌트: 고객 한 명이 여러 방문과 연결되는 경우를 생각한다.

[풀이 확인](#sql-i02-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-subquery.html)

---

<a id="sql-i03"></a>
## SQL-I03 · JOIN 부풀림·사전 집계·금액 대사: 합계가 커지는 이유

**학습 목표:** 1:N 연결에서 금액이 중복되는 문제를 발견하고 수정한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

팬아웃(fan-out)은 하나의 행이 JOIN 후 여러 행으로 늘어나는 현상이다. 사전 집계는 연결 전에 목적 grain으로 줄이는 작업이다. 대사(reconciliation)는 서로 다른 계산의 수치가 일치하는지 확인하는 작업이다.

### 2. 비유로 잡는 그림

청구서 한 장에 입금 영수증이 두 장 있다고 청구 금액을 두 번 더하면 안 된다.

### 3. 원리와 업무에서의 의미

invoices는 청구서 한 장, payments는 입금 한 건이 한 행이다. 1번 청구서는 4000과 6000으로 나눠 입금되었다. 그대로 연결하면 청구액 10000이 두 행에 반복된다. 6번 청구서도 두 번 반복되어 잘못된 청구 총액이 만들어진다.

해결은 입금을 invoice_id별 합계로 먼저 줄인 뒤 청구서와 1:1 또는 1:0 관계로 연결하는 것이다. 미입금 청구서는 왼쪽에 남기고 입금 합계의 NULL은 업무적으로 “입금 없음”이므로 0으로 대체한다.

SUM(DISTINCT invoice_amount)는 해결책이 아니다. 서로 다른 청구서의 금액이 같으면 실제 청구액까지 하나로 합쳐 버린다. 행의 정체성은 금액이 아니라 invoice_id다. 합계 보존을 검증하는 테스트를 만들어 두자.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I03.sql
```

```sql
WITH paid AS (
    SELECT invoice_id, SUM(amount_cents) AS paid_cents
    FROM payments
    GROUP BY invoice_id
)
SELECT COUNT(*) AS invoice_count,
       SUM(i.amount_cents) AS invoiced_cents,
       SUM(COALESCE(p.paid_cents, 0)) AS paid_cents,
       SUM(i.amount_cents - COALESCE(p.paid_cents, 0)) AS balance_cents
FROM invoices i
LEFT JOIN paid p ON i.invoice_id=p.invoice_id;
```

### 5. 결과와 코드 해설

| invoice_count | invoiced_cents | paid_cents | balance_cents |
| --- | --- | --- | --- |
| 6 | 100000 | 57000 | 43000 |

paid는 청구서당 한 행으로 바뀐다. 최종 결과는 청구서 6장, 청구 100000, 입금 57000, 미수 43000 cents다. 100000=57000+43000의 보존 관계를 확인한다. 과입금·환불·취소 청구는 이 소형 모델에 없으며 실제 설계에서는 별도 규칙이 필요하다.

### 6. 자주 하는 실수

일대다 표를 여러 개 동시에 붙이면 곱셈처럼 행이 늘 수 있다. 각 자식 표를 먼저 목적 키로 집계하거나 서로 다른 분석으로 분리한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** “왜 지난 보고서와 청구액이 다른가?”를 데이터 grain으로 설명한다.

**FDSE 관점:** 금액 보존 불변식과 JOIN 카디널리티 테스트를 구현한다.

### 8. 직접 풀어 보기

**SQL-I03-1. 청구서를 입금에 바로 LEFT JOIN하고 청구액을 합치면 얼마가 나오는가?**

힌트: 1번과 6번 청구액이 추가로 한 번씩 반복된다.

[풀이 확인](#sql-i03-1)

**SQL-I03-2. 미입금 청구서만 찾는 완성 쿼리를 작성하라.**

힌트: 입금 행이 전혀 없는지를 물어본다.

[풀이 확인](#sql-i03-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-table-expressions.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-aggregate.html)

---

<a id="sql-i04"></a>
## SQL-I04 · 윈도 함수·ROW_NUMBER·RANK: 행을 유지하며 순위 만들기

**학습 목표:** 고객별 최신 방문 한 건을 안정적으로 선택한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

윈도 함수(window function)는 행을 합쳐 없애지 않고 관련 행 집합을 참조해 계산한다. PARTITION BY는 계산 그룹, OVER는 윈도 정의다. ROW_NUMBER는 행별 번호, RANK는 동점에 같은 순위를 준다.

### 2. 비유로 잡는 그림

고객별 서류 묶음 안에서 최신 날짜 순으로 번호표를 붙이되 서류 자체는 그대로 둔다.

### 3. 원리와 업무에서의 의미

GROUP BY는 여러 방문을 고객 한 행으로 줄인다. 윈도 함수는 각 방문을 유지한 채 그 고객 안의 순서를 추가한다. 최신 상태의 나머지 열도 함께 가져오려면 MAX(날짜)만 계산하는 것보다 ROW_NUMBER로 행 전체를 선택하는 방식이 명확하다.

같은 시각의 방문이 있을 수 있으므로 scheduled_start만으로 정렬하면 최신 한 행이 불안정할 수 있다. visit_id를 추가해 동률 기준을 정한다. 실제 원천 이벤트에서는 source_sequence나 업데이트 버전이 더 적절할 수 있다.

ROW_NUMBER, RANK, DENSE_RANK는 다르다. 값이 100,100,90이면 row_number는 정렬 동률 기준에 따라 1,2,3, rank는 1,1,3, dense_rank는 1,1,2가 된다. “두 행”과 “상위 두 등급”은 다른 요구다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I04.sql
```

```sql
WITH ranked AS (
    SELECT visit_id, client_id, scheduled_start, status,
           ROW_NUMBER() OVER (
               PARTITION BY client_id
               ORDER BY scheduled_start DESC, visit_id DESC
           ) AS rn
    FROM visits
)
SELECT visit_id, client_id, status
FROM ranked
WHERE rn=1
ORDER BY client_id;
```

### 5. 결과와 코드 해설

| visit_id | client_id | status |
| --- | --- | --- |
| 17 | 1 | completed |
| 18 | 2 | completed |
| 19 | 3 | cancelled |
| 20 | 4 | completed |
| 21 | 5 | completed |
| 22 | 6 | completed |
| 23 | 7 | planned |
| 24 | 8 | completed |

각 고객의 세 방문에 1,2,3 번호를 붙인 뒤 rn=1만 남긴다. 결과 visit_id는 17~24다. 예정이나 취소도 포함한 최신 기록이다. “최신 완료 방문”을 원하면 완료 필터를 랭킹 전에 넣어야 한다.

### 6. 자주 하는 실수

최신 방문을 고른 뒤 완료만 남기는 것과, 완료 방문 중 최신을 고르는 것은 다르다. 필터 위치가 질문을 바꾼다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** “최신”이 발생 시각·수정 시각·수신 시각 중 무엇인지 정의한다.

**FDSE 관점:** 동률·상태 필터·늦게 도착한 수정 이벤트를 테스트한다.

### 8. 직접 풀어 보기

**SQL-I04-1. 고객별 최신 완료 방문을 조회하라.**

힌트: ranked CTE의 FROM 다음에 완료 WHERE를 넣는다.

[풀이 확인](#sql-i04-1)

**SQL-I04-2. 동점 포함 상위 2개 비용 등급을 고르려면 ROW_NUMBER와 DENSE_RANK 중 무엇을 쓰는가?**

힌트: 정확히 두 행인지 두 등급인지 확인한다.

[풀이 확인](#sql-i04-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/tutorial-window.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-window.html)

---

<a id="sql-i05"></a>
## SQL-I05 · LAG·LEAD·누적 합·프레임: 시간에 따른 변화 읽기

**학습 목표:** 이전 값과 누적값을 계산하고 윈도 프레임을 명시한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

LAG는 앞선 행, LEAD는 뒤의 행 값을 참조한다. 윈도 프레임(frame)은 현재 행의 계산에 실제 포함할 행 범위다. ROWS는 행 위치를 기준으로 범위를 잡는다.

### 2. 비유로 잡는 그림

날짜순 장부에서 바로 앞 청구액을 참고하고, 첫 장부터 현재 장까지 누적 금액을 적는다.

### 3. 원리와 업무에서의 의미

같은 날짜의 청구서가 여러 장 있으므로 날짜와 invoice_id를 함께 정렬한다. LAG는 이전 청구서와의 비교를 만들고, SUM OVER는 누적 청구액을 만든다. GROUP BY와 달리 청구서 여섯 장은 그대로 남는다.

ORDER BY만 쓰고 프레임을 생략하면 기본 프레임의 동점 처리 때문에 기대와 다른 누적값이 나올 수 있다. 행별 누적이 목적이라면 `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`를 명시한다.

“최근 7행 평균”은 “최근 7일 평균”이 아니다. 데이터 없는 날이 빠져 있으면 7행이 몇 주에 걸칠 수 있다. 날짜 달력에 0건 또는 미관측을 구분해 채운 뒤 일별 분석을 한다. LAG 역시 단순히 직전 행이지 자동으로 어제 값을 뜻하지 않는다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I05.sql
```

```sql
SELECT invoice_id, issued_on, amount_cents,
       LAG(amount_cents) OVER (ORDER BY issued_on, invoice_id) AS previous_amount,
       SUM(amount_cents) OVER (
           ORDER BY issued_on, invoice_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM invoices
ORDER BY issued_on, invoice_id;
```

### 5. 결과와 코드 해설

| invoice_id | issued_on | amount_cents | previous_amount | running_total |
| --- | --- | --- | --- | --- |
| 1 | 2026-08-01 | 10000 | NULL | 10000 |
| 2 | 2026-08-01 | 20000 | 10000 | 30000 |
| 3 | 2026-08-02 | 15000 | 20000 | 45000 |
| 4 | 2026-08-02 | 12000 | 15000 | 57000 |
| 5 | 2026-08-03 | 18000 | 12000 | 75000 |
| 6 | 2026-08-03 | 25000 | 18000 | 100000 |

첫 행의 previous_amount는 앞선 행이 없어 NULL이다. 누적합은 10000,30000,45000,57000,75000,100000이다. 누적합 마지막 값과 전체 SUM이 일치하는지도 검증한다. 순서를 명시했으므로 동일 입력에서 재현 가능하다.

### 6. 자주 하는 실수

LAST_VALUE는 기본 프레임 때문에 전체 파티션의 마지막 값이 아닌 현재 프레임의 마지막 값을 줄 수 있다. 필요한 프레임을 명시한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 전일 대비·직전 이벤트 대비·최근 일주일의 의미를 분리한다.

**FDSE 관점:** 동점 시각·빈 날짜·프레임 경계를 테스트한다.

### 8. 직접 풀어 보기

**SQL-I05-1. 각 청구액과 이전 청구액의 차이를 계산하라.**

힌트: 현재 값에서 LAG를 뺀다.

[풀이 확인](#sql-i05-1)

**SQL-I05-2. 8월 1일과 8월 3일만 있는 표에서 LAG가 8월 3일 행에 반환하는 값은 어제 값인가?**

힌트: 행의 인접성과 날짜의 인접성을 구분한다.

[풀이 확인](#sql-i05-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-window.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS)

---

<a id="sql-i06"></a>
## SQL-I06 · 시간대·날짜 달력·빈 구간: 0건과 미수집을 구별하기

**학습 목표:** 업무 시간대별 일별 집계를 만들고 비어 있는 날을 표시한다.

**실행 구분:** PostgreSQL 16 전용. 제작 환경에서 미실행; 로컬 PostgreSQL에서 확인해야 함

### 1. 용어부터 이해하기

TIMESTAMPTZ는 시간대 인식 시점을 다루는 PostgreSQL 자료형이다. AT TIME ZONE은 시각의 시간대 해석·표현을 변환한다. 날짜 스파인(date spine)은 빠짐없는 날짜 목록이다.

### 2. 비유로 잡는 그림

데이터가 있는 날만 칠하는 달력이 아니라, 날짜를 먼저 모두 그린 뒤 기록을 채운다.

### 3. 원리와 업무에서의 의미

PostgreSQL의 TIMESTAMPTZ는 순간을 저장하며 입력한 원래 지역 이름까지 그대로 보존하는 자료형은 아니다. 출력은 세션 시간대에 영향을 받는다. 서울 영업일별 방문 수는 `scheduled_start AT TIME ZONE 'Asia/Seoul'`을 날짜로 바꿔 묶는다.

날짜 달력이 없으면 8월 4일처럼 기록이 없는 날이 결과에서 사라진다. 날짜 목록에 일별 집계를 LEFT JOIN하면 0건을 표시할 수 있다. 다만 데이터 수집이 실패한 날을 0건으로 보여 주면 안 되므로 운영 시스템에서는 수집 성공 상태도 함께 연결한다.

아래는 PostgreSQL 전용이다. generate_series로 0~3을 만들고 시작 DATE에 더해 4일 달력을 만든다. SQLite의 TEXT 시각에 같은 문법을 그대로 붙일 수 없다. 기본 실습의 자동 검증은 SQLite 공통 SQL이고, 이 강의는 제공한 PostgreSQL 컨테이너에서 별도로 실행한다.

### 4. 따라 하는 예제

```bash
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_I06.sql
```

```sql
WITH calendar AS (
    SELECT DATE '2026-08-01' + n AS day
    FROM generate_series(0, 3) AS g(n)
), daily AS (
    SELECT (scheduled_start AT TIME ZONE 'Asia/Seoul')::date AS day,
           COUNT(*) AS visits
    FROM visits
    WHERE scheduled_start >= TIMESTAMPTZ '2026-08-01 00:00:00+09'
      AND scheduled_start < TIMESTAMPTZ '2026-08-05 00:00:00+09'
    GROUP BY 1
)
SELECT c.day, COALESCE(d.visits, 0) AS visits
FROM calendar c LEFT JOIN daily d USING (day)
ORDER BY c.day;
```

### 5. 결과와 코드 해설

> 이 코드의 PostgreSQL 실행 결과는 여기서 확인하지 못했습니다. 아래 “코드 해설”의 기대 결과와 독자의 실행 결과를 비교하세요. 실행 계획의 시간·스캔 방식은 고정값이 아닙니다.

calendar는 8월 1~4일을 만든다. daily는 서울 날짜별 방문 수를 집계한다. 이 합성 자료의 예상 결과는 8,8,8,0이다. `GROUP BY 1`은 첫 SELECT 표현식을 뜻하지만 팀 가독성 규칙에 따라 표현식이나 별도 CTE를 사용할 수 있다.

### 6. 자주 하는 실수

조건에서 타임스탬프 열을 함수로 감싸면 일반 인덱스 이용이 불리해질 수 있다. 조회 범위는 원래 열의 시각 구간으로 필터하고 표시·집계에 시간대 변환을 사용하는 방식을 검토한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** “0건”과 “수집 여부 미확인”을 화면에서 다르게 표현한다.

**FDSE 관점:** 지역별 날짜 경계·DST·인덱스 친화적인 시간 범위 필터를 설계한다.

### 8. 직접 풀어 보기

**SQL-I06-1. 서울 8월 전체를 겹치지 않는 시각 범위로 표현하라.**

힌트: 시작 포함, 9월 시작 제외다.

[풀이 확인](#sql-i06-1)

**SQL-I06-2. 8월 4일의 집계 결과가 0이면 실제 방문이 없었다고 단정할 수 있는가?**

힌트: 데이터 수집 성공 기록이 있는지 묻는다.

[풀이 확인](#sql-i06-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/datatype-datetime.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-datetime.html)
- [공식 문서 3](https://www.postgresql.org/docs/16/functions-srf.html)

---

<a id="sql-i07"></a>
## SQL-I07 · 중복 제거·최신 이벤트·품질 쿼리: 좋은 행과 나쁜 행을 나누기

**학습 목표:** 중복 키를 확인하고 안정적인 최신 행 선택 규칙을 작성한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

업무 키(business key)는 현실의 같은 대상을 묶는 키다. 이벤트 ID는 개별 변경 기록 식별자다. 결정적 처리(deterministic processing)는 같은 입력에 같은 출력을 만드는 처리다.

### 2. 비유로 잡는 그림

같은 신청서의 수정본이 세 번 도착하면 접수 순서가 아니라 합의된 수정 버전으로 최종본을 고른다.

### 3. 원리와 업무에서의 의미

중복은 모두 같은 종류가 아니다. 네트워크 재전송된 동일 이벤트, 같은 방문의 새 수정본, 서로 다른 원천 시스템의 충돌은 다르게 처리한다. 먼저 업무 키와 이벤트 키를 구분하고 어떤 변경이 우선하는지 정한다.

최신 updated_at만으로는 동률이 남을 수 있다. 아래는 교육용으로 event_id 문자열을 동률 기준으로 사용하지만 실제 이벤트 ID의 사전순이 업무 우선순위를 뜻한다는 보장은 없다. 가능하면 원천의 증가하는 버전·시퀀스를 계약에 넣는다.

품질 검사는 고유성·필수값·참조 무결성·허용값·시간 순서·신선도로 나누면 빠뜨리기 어렵다. 실패 행을 삭제하지 말고 원본과 사유를 격리해 재처리 가능하게 만든다. 최신 행 선택 전에 잘못된 시각을 정제하는 순서도 필요하다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I07.sql
```

```sql
WITH raw(event_id, visit_id, status, updated_at) AS (
    VALUES ('e1', 101, 'planned',   '2026-08-04T01:00:00+00:00'),
           ('e2', 101, 'completed', '2026-08-04T02:00:00+00:00'),
           ('e3', 102, 'planned',   '2026-08-04T01:00:00+00:00')
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY visit_id ORDER BY updated_at DESC, event_id DESC
    ) AS rn FROM raw
)
SELECT visit_id, status, event_id
FROM ranked WHERE rn=1
ORDER BY visit_id;
```

### 5. 결과와 코드 해설

| visit_id | status | event_id |
| --- | --- | --- |
| 101 | completed | e2 |
| 102 | planned | e3 |

visit_id=101은 e2 완료 상태, 102는 e3 예정 상태가 남는다. 예제의 시각 문자열은 같은 UTC 오프셋과 같은 길이로 정규화되어 있어 정렬할 수 있다. 일반 데이터에서는 문자 정렬을 믿지 말고 실제 타임스탬프로 파싱한다.

### 6. 자주 하는 실수

중복 제거 후 행 수가 줄었다고 품질이 좋아졌다고 단정하지 않는다. 유효한 이력까지 삭제했을 수 있다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 현재 상태와 변경 이력 중 사용자에게 필요한 것이 무엇인지 정한다.

**FDSE 관점:** 원본·정제·현재 상태를 분리하고 재현 가능한 충돌 규칙을 만든다.

### 8. 직접 풀어 보기

**SQL-I07-1. visits에서 방문 키 중복을 찾는 품질 쿼리를 작성하라.**

힌트: 키별 COUNT가 1을 넘는지 검사한다.

[풀이 확인](#sql-i07-1)

**SQL-I07-2. 중복 판단을 SELECT DISTINCT *로 끝내면 무엇을 놓치는가?**

힌트: 같은 방문의 서로 다른 상태 행을 생각한다.

[풀이 확인](#sql-i07-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-window.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/ddl-constraints.html)

---

<a id="sql-i08"></a>
## SQL-I08 · 코호트·활성·리텐션: 고객 집단을 올바르게 비교하기

**학습 목표:** 가입 집단의 크기와 관측 기간의 활동을 분리한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

코호트(cohort)는 같은 기준으로 묶은 집단이다. 활성(active)은 정해진 행동을 한 상태다. 리텐션(retention)은 기준 집단이 후속 기간에 활동을 이어가는 비율이다.

### 2. 비유로 잡는 그림

같은 달에 입학한 학생 집단을 기준으로 다음 달 수업 참여를 비교하는 방식이다.

### 3. 원리와 업무에서의 의미

가입 월별 고객을 묶고 8월에 완료 방문이 있는 고객 비율을 계산한다. 이 실습에서는 이를 “8월 완료 활동률”이라 부른다. 모든 코호트에서 동일한 “가입 후 한 달 리텐션”이 아니기 때문이다. 7월 가입자와 8월 가입자는 서비스 노출 기간도 다르다.

분모는 visits가 아니라 clients에서 만들어야 미사용 고객도 포함된다. 가입 고객 중 활동한 고객을 EXISTS로 표시하면 한 고객이 여러 번 방문해도 분자는 한 번만 올라간다.

실무 리텐션에는 기준 사건, 후속 기간, 달력 월/경과 30일의 차이, 관측 종료, 아직 후속 기간을 다 채우지 못한 고객의 처리까지 필요하다. 최신 가입자를 단순히 이탈로 분류하면 관측 부족을 성과 저하로 오해한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I08.sql
```

```sql
WITH client_activity AS (
    SELECT c.client_id, c.joined_on,
           CASE WHEN EXISTS (
               SELECT 1 FROM visits v
               WHERE v.client_id=c.client_id
                 AND v.status='completed'
                 AND v.scheduled_start >= '2026-08-01T00:00:00+00:00'
                 AND v.scheduled_start <  '2026-09-01T00:00:00+00:00'
           ) THEN 1 ELSE 0 END AS active_in_august
    FROM clients c
)
SELECT joined_on, COUNT(*) AS cohort_clients,
       SUM(active_in_august) AS active_clients,
       1.0*SUM(active_in_august)/NULLIF(COUNT(*),0) AS activity_rate
FROM client_activity
GROUP BY joined_on
ORDER BY joined_on;
```

### 5. 결과와 코드 해설

| joined_on | cohort_clients | active_clients | activity_rate |
| --- | --- | --- | --- |
| 2026-07-01 | 6 | 2 | 0.3333333333333333 |
| 2026-08-01 | 6 | 4 | 0.6666666666666666 |

자료에서 가입 날짜는 각 달의 1일뿐이므로 joined_on으로 묶어도 월 코호트와 같다. 일반 자료에는 월 변환이 필요하다. 7월 집단은 6명 중 2명, 8월 집단은 6명 중 4명이 활동했다. 이 차이만으로 가입 정책의 효과를 추정할 수는 없다.

### 6. 자주 하는 실수

관측 가능한 기간이 다른 집단을 같은 리텐션 단계로 비교하지 않는다. cohort_month와 period_index, eligible_population을 명시한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 활성 정의와 관측 기회를 공정하게 맞춘다.

**FDSE 관점:** 코호트 분모를 차원 테이블에서 유지하고 반복 활동 중복을 제거한다.

### 8. 직접 풀어 보기

**SQL-I08-1. 가입일을 무시한 전체 8월 완료 활동 고객 수와 비율은?**

힌트: 두 코호트의 분자와 분모를 합친다.

[풀이 확인](#sql-i08-1)

**SQL-I08-2. 9월 30일에 9월 가입자의 가입 후 30일 리텐션을 모두 계산해도 되는가?**

힌트: 가입 후 30일이 아직 지나지 않은 사람을 찾는다.

[풀이 확인](#sql-i08-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-subquery.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-datetime.html)

---

<a id="sql-i09"></a>
## SQL-I09 · 정규화·스타 스키마·이력: 현재 지점과 당시 지점

**학습 목표:** 현재 속성과 사건 당시 속성의 차이를 모델에 반영한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

사실 테이블(fact)은 방문·결제 같은 사건을 저장한다. 차원 테이블(dimension)은 고객·지점 같은 설명 속성을 저장한다. 유효 기간은 속성이 실제 업무에서 적용되는 시간 범위다.

### 2. 비유로 잡는 그림

고객이 지점을 옮겨도 지난달 방문 실적까지 새 지점으로 옮겨 적지 않도록 당시 배정을 기록한다.

### 3. 원리와 업무에서의 의미

clients.branch_id는 현재 고객 소속을 나타내는 모델로 사용할 수 있다. visits.branch_id는 사건 당시 서비스 지점을 나타내도록 정의했다. 모든 과거 방문을 현재 고객 지점으로 다시 묶으면 지점 이동만으로 과거 실적이 바뀔 수 있다.

분석용 스타 스키마는 사건 표를 중심으로 설명 표를 연결한다. 중요한 것은 표 모양보다 사건의 grain과 시간 의미다. 한 방문의 청구가 여러 건이면 fact_visit와 fact_invoice를 같은 행 단위로 섞지 않는다.

유효 기간 이력은 `[valid_from,valid_to)`로 표현하면 경계 시점에 두 버전이 동시에 매칭되는 것을 피할 수 있다. 아래는 같은 고객이 8월 2일에 지점 1에서 2로 이동한 가상의 예제다. 기간이 겹치거나 끊기는 문제는 별도 품질 검사로 찾아야 한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I09.sql
```

```sql
WITH history(client_id, branch_id, valid_from, valid_to) AS (
    VALUES (1, 1, '2026-07-01', '2026-08-02'),
           (1, 2, '2026-08-02', '2026-09-01')
), events(event_id, client_id, event_day) AS (
    VALUES (1, 1, '2026-08-01'), (2, 1, '2026-08-02')
)
SELECT e.event_id, e.event_day, h.branch_id
FROM events e JOIN history h
  ON e.client_id=h.client_id
 AND e.event_day >= h.valid_from
 AND e.event_day < h.valid_to
ORDER BY e.event_id;
```

### 5. 결과와 코드 해설

| event_id | event_day | branch_id |
| --- | --- | --- |
| 1 | 2026-08-01 | 1 |
| 2 | 2026-08-02 | 2 |

8월 1일 사건은 지점 1, 8월 2일 사건은 지점 2와 연결된다. 끝 경계를 `<`로 두어 8월 2일이 이전 버전과 겹치지 않는다. 이 예제는 날짜 단위 문자열이 정규화된 소형 설명용이며 PostgreSQL 실제 표에서는 DATE/TIMESTAMPTZ를 사용한다.

### 6. 자주 하는 실수

현재 속성으로 과거 분석을 재작성할지 당시 속성을 유지할지는 업무 결정이다. 두 방식의 보고서가 다른 이유를 숨기지 않는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** “누가 지금 담당하는가?”와 “그때 누가 담당했는가?”를 구분한다.

**FDSE 관점:** 유효 기간·버전 키·동시 갱신·이력 겹침 검사를 설계한다.

### 8. 직접 풀어 보기

**SQL-I09-1. valid_to 조건을 <=로 바꾸면 경계 사건은 몇 행과 연결되는가?**

힌트: 8월 2일은 양쪽 기간에 들어갈 수 있다.

[풀이 확인](#sql-i09-1)

**SQL-I09-2. visits에 client_id와 branch_id가 함께 있는 것은 항상 나쁜 중복인가?**

힌트: 두 속성의 시간 의미를 확인한다.

[풀이 확인](#sql-i09-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/ddl-constraints.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/rangetypes.html)

---

<a id="sql-i10"></a>
## SQL-I10 · 지표 마트·교차 검증: 지연율을 설명 가능한 결과로

**학습 목표:** 분자·분모·결측 건수·빈 지점을 함께 제공한다.

**실행 구분:** SQLite 전용 날짜 계산. PostgreSQL 대응 파일은 lab/sql/SQL_I10_postgres.sql이며 미실행

### 1. 용어부터 이해하기

데이터 마트(data mart)는 특정 업무 질문을 위해 정리한 데이터 집합이다. 지표 계약(metric contract)은 공식·대상·기간·제외·단위·갱신 규칙의 약속이다. 불변식(invariant)은 항상 성립해야 하는 관계다.

### 2. 비유로 잡는 그림

보고서의 백분율 옆에 계산에 사용한 장부의 장수와 제외한 장수를 함께 적는 것이다.

### 3. 원리와 업무에서의 의미

한 숫자만 저장하면 이후 규칙 검증이 어렵다. 지점별 완료 건수, 측정 가능한 건수, 지연 건수, 미측정 완료 건수를 함께 계산한다. 전체 지연율은 late 합/eligible 합으로 재구성한다.

아래 SQLite 쿼리는 julianday로 두 시각 차이를 분으로 바꾸고, 부동소수점 표현에서 생길 수 있는 미세 오차를 막기 위해 반올림한다. 이 실습의 원천 시각 정밀도는 분 단위다. 실제 초·밀리초 단위 계약이라면 반올림 정책을 별도로 정해야 한다. PostgreSQL에서는 `EXTRACT(EPOCH FROM actual_start-scheduled_start)/60.0`을 사용한다.

분자<=분모<=완료<=전체가 성립해야 한다. 지연+정시=측정 가능, 측정 가능+완료 미측정=완료도 확인한다. 이러한 관계가 깨지면 보고서를 예쁘게 만들기 전에 계산 또는 데이터 품질 문제를 찾는다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_I10.sql
```

```sql
WITH labeled AS (
    SELECT *,
           CASE WHEN status='completed' AND actual_start IS NOT NULL
                THEN ROUND((julianday(actual_start)-julianday(scheduled_start))*1440, 6)
                ELSE NULL END AS delay_minutes
    FROM visits
), aggregated AS (
    SELECT branch_id,
           SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed,
           COUNT(delay_minutes) AS eligible,
           SUM(CASE WHEN delay_minutes>10 THEN 1 ELSE 0 END) AS late,
           SUM(CASE WHEN status='completed' AND actual_start IS NULL THEN 1 ELSE 0 END) AS unknown
    FROM labeled GROUP BY branch_id
)
SELECT b.branch_id, COALESCE(a.completed,0) AS completed,
       COALESCE(a.eligible,0) AS eligible, COALESCE(a.late,0) AS late,
       COALESCE(a.unknown,0) AS unknown,
       1.0*a.late/NULLIF(a.eligible,0) AS late_rate
FROM branches b LEFT JOIN aggregated a USING (branch_id)
ORDER BY b.branch_id;
```

### 5. 결과와 코드 해설

| branch_id | completed | eligible | late | unknown | late_rate |
| --- | --- | --- | --- | --- | --- |
| 1 | 6 | 6 | 3 | 0 | 0.5 |
| 2 | 9 | 6 | 3 | 3 | 0.5 |
| 3 | 3 | 3 | 0 | 0 | 0.0 |
| 4 | 0 | 0 | 0 | 0 | NULL |

결과는 지점1=(완료6,측정6,지연3,미측정0,50%), 지점2=(9,6,3,3,50%), 지점3=(3,3,0,0,0%), 지점4=(0,0,0,0,NULL)이다. 전체 지연율은 6/15=40%다. 지점 비율 50%,50%,0%의 단순 평균 33.3%와 구분한다.

### 6. 자주 하는 실수

빈 지점의 NULL 지연율을 COALESCE(...,0)로 바꾸면 0% 지연인 우수 지점처럼 보일 수 있다. 건수의 0과 비율의 미정의를 구분한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 지표를 보고 어떤 사람이 어떤 행동을 해야 하는지 메모로 연결한다.

**FDSE 관점:** Python 결과와 SQL 결과의 분자·분모를 비교하는 자동 대사를 만든다.

### 8. 직접 풀어 보기

**SQL-I10-1. 전체 지연율을 지점 집계에서 다시 계산하는 공식을 쓰고 값을 구하라.**

힌트: 지점 비율의 평균이 아니라 합계를 나눈다.

[풀이 확인](#sql-i10-1)

**SQL-I10-2. 지점2와 지점1 모두 50%이니 상황이 같다고 말할 수 있는가?**

힌트: 측정 누락을 비교한다.

[풀이 확인](#sql-i10-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.sqlite.org/lang_datefunc.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-datetime.html)
- [공식 문서 3](https://www.postgresql.org/docs/16/functions-conditional.html)



---
