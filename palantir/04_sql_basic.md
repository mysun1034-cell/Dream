# SQL 기본: 표를 읽는 단계에서 정확한 업무 질문을 만드는 단계로

**구성:** 10강 · 연습문제 20개 · DS/FDSE 역할별 적용 과제

표의 한 행이 무엇을 뜻하는지부터 시작합니다. Python 기본과 같은 주차에 병행하되 서로의 문법을 외우는 대신 같은 업무 질문을 두 방식으로 표현하세요.

**사용 방법:** 모든 명령은 압축을 푼 폴더의 `lab/`에서 실행합니다. 아직 환경을 만들지 않았다면 [환경과 데이터 사전](#book-02)을 먼저 읽으세요. 각 강의의 설명형 해설은 본문에, 연습문제 정답은 [해설집](#book-09)에 있습니다.

## 강의 지도

- [SQL-B01 데이터베이스·테이블·행 단위·SELECT](#sql-b01)
- [SQL-B02 WHERE·AND·OR·IN: 업무 대상을 정확히 고르기](#sql-b02)
- [SQL-B03 NULL·3값 논리·COUNT: 모른다는 사실을 계산에 반영하기](#sql-b03)
- [SQL-B04 ORDER BY·LIMIT·DISTINCT: 결과의 순서와 중복 의미](#sql-b04)
- [SQL-B05 집계·GROUP BY·HAVING: 행을 요약으로 바꾸기](#sql-b05)
- [SQL-B06 CASE·조건부 집계·분모: 한 번의 조회로 운영 지표 만들기](#sql-b06)
- [SQL-B07 INNER JOIN·외래키·카디널리티: 분리된 장부 연결하기](#sql-b07)
- [SQL-B08 LEFT JOIN·ON과 WHERE: 0건인 지점도 남기기](#sql-b08)
- [SQL-B09 스키마·제약조건·정규화: 틀린 데이터가 들어오기 어렵게 만들기](#sql-b09)
- [SQL-B10 INSERT·UPDATE·DELETE·트랜잭션: 안전하게 상태 바꾸기](#sql-b10)

---

<a id="sql-b01"></a>
## SQL-B01 · 데이터베이스·테이블·행 단위·SELECT

**학습 목표:** 표의 한 행이 무엇인지 설명하고 필요한 열만 조회한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

데이터베이스(DB)는 데이터를 저장하고 조회·수정하는 체계다. DBMS는 이를 관리하는 소프트웨어다. SQL은 관계형 데이터를 정의·조회·변경하는 언어다. 테이블은 행과 열로 구성되며, grain은 한 행이 나타내는 업무 단위다.

### 2. 비유로 잡는 그림

데이터베이스는 연결된 업무 장부이고 SQL은 그 장부에서 필요한 내용을 요청하는 문장이다.

### 3. 원리와 업무에서의 의미

방문 장부 visits의 한 행은 방문 한 건이다. 고객 장부 clients의 한 행은 고객 한 명이다. 같은 고객이 세 번 방문하면 visits에는 세 행, clients에는 한 행이 존재한다. 이 차이를 확인하지 않고 고객 수를 세면 고객을 여러 번 셀 수 있다.

SELECT는 결과에 어떤 열을 넣을지, FROM은 어느 표에서 읽을지를 나타낸다. 이 단계에서는 데이터가 수정되지 않는다. `SELECT *`는 모든 열을 읽지만, 실제 업무에서는 필요한 열을 명시하면 의미와 노출 범위를 관리하기 쉽다.

기본키(primary key)는 행을 식별하는 값이다. 이름은 중복·변경될 수 있으므로 ID가 필요하다. “행 수=고객 수”가 아니라 “행 수=이 표의 grain 개수”라고 이해한다. SQL은 Excel 셀 좌표보다 열의 의미와 행 집합에 집중한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B01.sql
```

```sql
SELECT visit_id, client_id, status
FROM visits
ORDER BY visit_id
LIMIT 5;
```

### 5. 결과와 코드 해설

| visit_id | client_id | status |
| --- | --- | --- |
| 1 | 1 | completed |
| 2 | 2 | completed |
| 3 | 3 | cancelled |
| 4 | 4 | completed |
| 5 | 5 | completed |

visit_id는 방문 식별자, client_id는 그 방문을 받은 고객 식별자다. ORDER BY는 표시 순서를 정하고 LIMIT 5는 다섯 행만 보여 준다. LIMIT만으로는 어떤 다섯 행인지 보장할 수 없으므로 정렬 기준을 함께 넣었다. 세미콜론은 SQL 문장의 끝이다.

### 6. 자주 하는 실수

visits에서 COUNT(*)를 하면 방문 건수이지 고유 고객 수가 아니다. 쿼리를 작성하기 전에 입력 grain과 출력 grain을 각각 적는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 고객의 “몇 명인가요?”가 사람 수인지 방문 건수인지 확인한다.

**FDSE 관점:** 키와 테이블 관계를 모델로 표현하고 필요한 열만 반환한다.

### 8. 직접 풀어 보기

**SQL-B01-1. 고객 테이블에서 client_id와 branch_id를 ID순으로 첫 네 행 조회하라.**

힌트: 표 이름은 clients다.

[풀이 확인](#sql-b01-1)

**SQL-B01-2. SELECT 결과에서 client_id=1이 여러 번 나오는 것은 무조건 중복 오류인가?**

힌트: 방문과 고객의 grain을 비교한다.

[풀이 확인](#sql-b01-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/tutorial-select.html)

---

<a id="sql-b02"></a>
## SQL-B02 · WHERE·AND·OR·IN: 업무 대상을 정확히 고르기

**학습 목표:** 조건을 조합하고 괄호로 의도를 명확히 표현한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

WHERE는 행 단위 조건이다. AND는 두 조건이 모두 참일 때, OR는 하나라도 참일 때 통과시킨다. IN은 값이 목록에 속하는지 검사한다.

### 2. 비유로 잡는 그림

신청서 묶음에서 “1번 지점이면서 완료된 신청서”만 따로 꺼내는 과정이다.

### 3. 원리와 업무에서의 의미

SQL의 조건은 Python의 조건문과 비슷해 보이지만 여러 행에 한꺼번에 적용된다. `branch_id = 1`은 여기서는 대입이 아니라 비교다. 문자열은 작은따옴표로 감싼다. PostgreSQL에서 큰따옴표는 열 이름 같은 식별자에 쓰일 수 있으므로 혼동하지 않는다.

AND가 OR보다 먼저 묶인다. “1번 또는 2번 지점의 완료 방문”을 원하면 `(branch_id=1 OR branch_id=2) AND status='completed'`처럼 괄호를 쓰거나 IN을 사용한다. 우선순위를 외우는 것보다 의도를 보이게 쓰는 것이 안전하다.

날짜 구간은 시작 포함·끝 제외 `[start,end)`를 기본 습관으로 삼는다. 8월은 8월 1일 이상, 9월 1일 미만이다. 마지막 날의 23:59:59를 직접 지정하면 더 정밀한 시각 데이터가 빠질 수 있다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B02.sql
```

```sql
SELECT visit_id, branch_id, status
FROM visits
WHERE branch_id IN (1, 2)
  AND status = 'completed'
ORDER BY visit_id;
```

### 5. 결과와 코드 해설

| visit_id | branch_id | status |
| --- | --- | --- |
| 1 | 1 | completed |
| 2 | 1 | completed |
| 4 | 2 | completed |
| 5 | 2 | completed |
| 6 | 2 | completed |
| 9 | 1 | completed |
| 10 | 1 | completed |
| 12 | 2 | completed |
| 13 | 2 | completed |
| 14 | 2 | completed |
| 17 | 1 | completed |
| 18 | 1 | completed |
전체 15행 중 앞 12행 표시. 실행하면 전체 결과가 나옵니다.

FROM에서 방문 표를 대상으로 삼고 WHERE로 두 지점의 완료 방문만 통과시킨다. 출력에는 취소·예정이 없다. WHERE에서 쓰는 열은 SELECT에 꼭 포함할 필요는 없지만, 학습 초기에는 조건에 쓰인 값을 함께 출력하면 검증하기 쉽다.

### 6. 자주 하는 실수

`branch_id=1 OR branch_id=2 AND status=...`는 1번 지점의 취소 방문도 포함한다. 논리적으로 비슷해 보이는 표현을 결과 행으로 비교한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 대상 집단·기간·제외 사유를 자연어로 먼저 합의한다.

**FDSE 관점:** 조건 누락이 다른 지점의 데이터 노출로 이어지지 않도록 테스트한다.

### 8. 직접 풀어 보기

**SQL-B02-1. branch_id=3인 방문 중 planned가 아닌 방문 ID를 조회하라.**

힌트: 같지 않다는 SQL 연산자는 <>다.

[풀이 확인](#sql-b02-1)

**SQL-B02-2. `fee_cents BETWEEN 10000 AND 12000`은 12000도 포함하는가?**

힌트: BETWEEN의 양쪽 경계를 확인한다.

[풀이 확인](#sql-b02-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-table-expressions.html#QUERIES-WHERE)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-comparison.html)

---

<a id="sql-b03"></a>
## SQL-B03 · NULL·3값 논리·COUNT: 모른다는 사실을 계산에 반영하기

**학습 목표:** NULL을 0과 구분하고 결측이 집계에 미치는 영향을 설명한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

NULL은 값이 알려지지 않았거나 존재하지 않음을 나타내는 표식이다. SQL 비교에는 참·거짓 외에 unknown이 있다. COUNT(*)는 행 수, COUNT(열)는 그 열이 NULL이 아닌 행 수다.

### 2. 비유로 잡는 그림

도착 시각이 빈 방문 기록은 “0분 지연” 기록이 아니라 “도착 시각을 모름” 기록이다.

### 3. 원리와 업무에서의 의미

`actual_start = NULL`로 결측을 찾을 수 없다. NULL과 일반 비교를 하면 unknown이 되며 WHERE는 참인 행만 남긴다. 결측 여부는 `IS NULL`, `IS NOT NULL`로 검사한다.

전체 24건 중 실제 시작이 있는 것은 15건이다. 하지만 없는 9건의 의미는 같지 않다. 취소 3건, 예정 3건, 완료했지만 시작 시각이 없는 3건이다. 모든 빈칸을 데이터 오류로 보거나 모두 정상 제외로 보면 둘 다 부정확하다.

COALESCE는 NULL일 때 대체값을 고르는 기능이다. 보고서에서 미입금 합계를 0으로 표시하는 데 쓸 수 있지만, 모르는 지연 시간을 0으로 바꾸면 정시 방문처럼 계산된다. 대체값은 업무 의미에 근거해야 한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B03.sql
```

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(actual_start) AS known_start_rows,
    SUM(CASE WHEN status = 'completed' AND actual_start IS NULL
             THEN 1 ELSE 0 END) AS completed_missing
FROM visits;
```

### 5. 결과와 코드 해설

| total_rows | known_start_rows | completed_missing |
| --- | --- | --- |
| 24 | 15 | 3 |

AS는 결과 열에 이름을 붙인다. CASE는 조건에 따라 1 또는 0을 만들며 SUM이 이를 더한다. 결과는 total_rows=24, known_start_rows=15, completed_missing=3이다. 결측 건수와 지연 건수는 다른 지표다.

### 6. 자주 하는 실수

`COUNT(actual_start)`는 완료 여부를 자동 확인하지 않는다. 다른 상태에 시간이 들어갈 수 있는 실데이터에서는 상태 조건도 명시해야 한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 측정 불가능한 방문을 따로 보고하고 지연율 신뢰도를 설명한다.

**FDSE 관점:** NULL 처리 규칙을 SQL·Python·API 응답에서 일관되게 유지한다.

### 8. 직접 풀어 보기

**SQL-B03-1. 완료 방문 중 actual_start가 없는 방문 ID를 조회하라.**

힌트: status 조건과 IS NULL을 함께 쓴다.

[풀이 확인](#sql-b03-1)

**SQL-B03-2. NULL을 모두 0분으로 바꿔 지연율을 계산하면 왜 낮아질 수 있는가?**

힌트: 분자는 그대로인데 분모에 누가 추가되는지 본다.

[풀이 확인](#sql-b03-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-comparison.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/functions-aggregate.html)

---

<a id="sql-b04"></a>
## SQL-B04 · ORDER BY·LIMIT·DISTINCT: 결과의 순서와 중복 의미

**학습 목표:** 안정적인 정렬을 만들고 행 중복 제거와 업무 중복 제거를 구분한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

ORDER BY는 결과 정렬, LIMIT는 결과 행 수 제한, DISTINCT는 선택된 열 조합의 중복 제거다. tie-breaker는 정렬값이 같을 때 순서를 정하는 추가 기준이다.

### 2. 비유로 잡는 그림

방문 요금이 같은 신청서는 접수 ID를 추가 기준으로 삼아 순서를 고정한다.

### 3. 원리와 업무에서의 의미

테이블은 “항상 저장된 순서대로 읽히는 파일”이 아니다. 결과 순서가 중요하면 ORDER BY를 써야 한다. 비용이 높은 다섯 건을 보여줄 때 비용이 같으면 visit_id로 동률을 해소한다.

DISTINCT는 출력 열 전체 조합을 기준으로 행을 합친다. `SELECT DISTINCT client_id`는 고유 고객 목록이고 `SELECT DISTINCT client_id,status`는 고객·상태 조합 목록이다. 열을 하나 추가하는 것만으로 행 수가 달라질 수 있다.

DISTINCT로 JOIN 오류를 덮으면 금액 합계는 이미 잘못됐을 수 있다. 중복이 왜 생겼는지, 원래 어떤 grain의 결과를 원했는지 먼저 확인한다. 고유 고객 수는 `COUNT(DISTINCT client_id)`처럼 질문을 직접 표현한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B04.sql
```

```sql
SELECT visit_id, fee_cents
FROM visits
ORDER BY fee_cents DESC, visit_id ASC
LIMIT 5;
```

### 5. 결과와 코드 해설

| visit_id | fee_cents |
| --- | --- |
| 8 | 17000 |
| 16 | 17000 |
| 24 | 17000 |
| 7 | 16000 |
| 15 | 16000 |

DESC는 내림차순, ASC는 오름차순이다. 먼저 fee_cents가 큰 값을 고른 뒤 같은 요금에서는 visit_id가 작은 순서다. 요금 17000인 8,16,24번 방문이 먼저 나오고 다음으로 16000인 7,15번이 나온다. 이것은 예정·취소도 포함한 요금 필드 순위이지 실제 매출 순위가 아니다.

### 6. 자주 하는 실수

정렬된 상위 다섯 건을 전체 분포처럼 해석하지 않는다. 상위 사례는 문제 탐색에 유용하지만 대표성은 별도로 확인해야 한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 상위 사례의 목적이 원인 탐색인지 전체 KPI 설명인지 구분한다.

**FDSE 관점:** 페이지 조회에서 안정적인 복합 정렬 키를 사용한다.

### 8. 직접 풀어 보기

**SQL-B04-1. 방문한 고객의 고유 ID를 오름차순으로 조회하라.**

힌트: DISTINCT는 client_id 하나에 적용한다.

[풀이 확인](#sql-b04-1)

**SQL-B04-2. 비용 상위 5건을 조회하는데 동일 비용 행의 순서가 바뀌어도 괜찮은가?**

힌트: 재현 가능한 보고서와 페이지 이동을 생각한다.

[풀이 확인](#sql-b04-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-order.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/queries-limit.html)
- [공식 문서 3](https://www.postgresql.org/docs/16/queries-select-lists.html)

---

<a id="sql-b05"></a>
## SQL-B05 · 집계·GROUP BY·HAVING: 행을 요약으로 바꾸기

**학습 목표:** 그룹별 합계를 만들고 집계 전후 필터의 차이를 설명한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

집계(aggregation)는 여러 행을 하나의 요약으로 계산하는 일이다. GROUP BY는 같은 키의 행을 묶고 HAVING은 묶인 결과에 조건을 적용한다.

### 2. 비유로 잡는 그림

방문 신청서를 지점별로 분류한 뒤 지점별 완료 건수를 집계하는 작업이다.

### 3. 원리와 업무에서의 의미

원본 grain이 방문 한 건이라도 GROUP BY branch_id를 실행한 결과 grain은 지점 하나가 된다. 출력할 열은 그룹 키이거나 집계 결과여야 한다. 특정 방문의 client_id를 아무 기준 없이 같이 출력하면 “어느 고객인가?”에 답할 수 없다.

WHERE는 묶기 전에 행을 고른다. HAVING은 묶은 뒤 그룹을 고른다. 완료 방문이 5건 이상인 지점을 찾으려면 먼저 WHERE로 완료 방문을 고르고 GROUP BY 후 HAVING COUNT(*)>=5를 적용한다.

평균을 다시 평균 내는 것은 대부분 원래 행 전체의 평균과 다르다. 지점별 건수가 다르면 가중치가 달라지기 때문이다. 합계와 건수를 함께 저장하면 전체 지표를 정확하게 재계산할 수 있다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B05.sql
```

```sql
SELECT branch_id,
       COUNT(*) AS completed_visits,
       SUM(fee_cents) AS completed_fee_cents
FROM visits
WHERE status = 'completed'
GROUP BY branch_id
HAVING COUNT(*) >= 5
ORDER BY branch_id;
```

### 5. 결과와 코드 해설

| branch_id | completed_visits | completed_fee_cents |
| --- | --- | --- |
| 1 | 6 | 63000 |
| 2 | 9 | 126000 |

1번 지점은 완료 6건·63000 cents, 2번 지점은 완료 9건·126000 cents다. 3번 지점은 완료 3건이라 HAVING에서 제외된다. 실제 지급이나 청구와는 다른, 완료 방문의 학습용 fee 합계라는 점을 열 이름으로 표시했다.

### 6. 자주 하는 실수

집계에 사용한 비용 필드가 예상 요금인지 확정 청구액인지 확인한다. 같은 SUM이라도 어떤 열을 더하느냐에 따라 업무 의미가 달라진다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 요약 단위와 지표 정의를 보고서 제목에 드러낸다.

**FDSE 관점:** 집계 전후의 행 수와 합계 보존 여부를 검증한다.

### 8. 직접 풀어 보기

**SQL-B05-1. 상태별 방문 수를 구하라.**

힌트: status를 GROUP BY에 넣는다.

[풀이 확인](#sql-b05-1)

**SQL-B05-2. 지점 A가 1/2, 지점 B가 9/18 지연이면 전체 지연율은 얼마인가?**

힌트: 분자끼리·분모끼리 합친다.

[풀이 확인](#sql-b05-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/tutorial-agg.html)

---

<a id="sql-b06"></a>
## SQL-B06 · CASE·조건부 집계·분모: 한 번의 조회로 운영 지표 만들기

**학습 목표:** 상태별 건수와 비율을 계산하고 0건 집단을 안전하게 처리한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

CASE는 행마다 조건에 따라 값을 선택한다. 조건부 집계는 특정 조건의 행만 합계·건수에 기여하도록 한다. NULLIF(a,b)는 두 값이 같으면 NULL을 반환한다.

### 2. 비유로 잡는 그림

각 기록에 완료면 1, 아니면 0 스티커를 붙이고 지점별로 스티커를 세는 방식이다.

### 3. 원리와 업무에서의 의미

완료율은 완료 건수/전체 방문 수로 정의할 수 있다. 다만 운영 목적에 따라 미래 예정 방문을 제외해야 할 수도 있으므로 이 정의를 보편적인 정답으로 취급하지 않는다. 이 강의에서는 제공된 24건 스냅샷의 구성비를 계산한다.

`SUM(CASE WHEN ... THEN 1 ELSE 0 END)`는 조건을 충족하는 건수를 만든다. 정수 나눗셈은 엔진과 자료형에 따라 소수 부분을 잃을 수 있으므로 1.0을 곱하거나 명시적으로 소수 자료형으로 변환한다.

NULLIF는 분모가 0이면 나눗셈을 NULL로 만든다. 빈 집단을 0%로 바꾸지 않으면 “아직 측정할 데이터 없음”을 표현할 수 있다. 사용자가 볼 때는 NULL을 '측정 불가'처럼 명시적으로 표시한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B06.sql
```

```sql
SELECT branch_id,
       COUNT(*) AS total_visits,
       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
       ROUND(1.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 3) AS completion_rate
FROM visits
GROUP BY branch_id
ORDER BY branch_id;
```

### 5. 결과와 코드 해설

| branch_id | total_visits | completed | completion_rate |
| --- | --- | --- | --- |
| 1 | 9 | 6 | 0.667 |
| 2 | 9 | 9 | 1.0 |
| 3 | 6 | 3 | 0.5 |

각 지점에 대해 총 방문 수와 완료 건수를 같은 쿼리에서 만든다. 1번은 6/9, 2번은 9/9, 3번은 3/6이다. 4번 지점은 방문 자체가 없어 결과에 나타나지 않는다. 모든 지점을 표시하려면 다음 JOIN 강의를 적용한다.

### 6. 자주 하는 실수

없는 지점이 결과에서 사라진 것과 0건으로 출력된 것은 다르다. 대시보드에 어떤 집단을 반드시 표시할지 정한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 비율 정의의 대안과 선택 이유를 문서화한다.

**FDSE 관점:** 정수 나눗셈·0 분모·빈 그룹·반올림 시점을 테스트한다.

### 8. 직접 풀어 보기

**SQL-B06-1. 전체 취소율을 소수 네 자리까지 계산하라.**

힌트: 취소 건수를 전체 24건으로 나눈다.

[풀이 확인](#sql-b06-1)

**SQL-B06-2. 전체 완료율이 75%인 이유만으로 운영이 나쁘다고 결론 내릴 수 있는가?**

힌트: 예정·취소 상태와 관측 시점을 확인한다.

[풀이 확인](#sql-b06-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-conditional.html)

---

<a id="sql-b07"></a>
## SQL-B07 · INNER JOIN·외래키·카디널리티: 분리된 장부 연결하기

**학습 목표:** 고객과 방문의 관계를 키로 연결하고 결과 행 수를 예측한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

JOIN은 조건에 맞는 행을 두 표에서 연결한다. 외래키(foreign key)는 다른 표의 키를 참조한다. 카디널리티(cardinality)는 여기서 1:1, 1:N 같은 관계의 대응 수를 뜻한다.

### 2. 비유로 잡는 그림

방문 기록의 지점 번호를 지점 이름 장부에 대조해 읽기 쉬운 보고서를 만드는 일이다.

### 3. 원리와 업무에서의 의미

지점 이름을 모든 방문에 반복 저장하면 이름 변경 시 여러 곳을 수정해야 한다. 지점 표에는 이름을 한 번 저장하고 방문 표에는 branch_id를 저장해 연결한다. 이때 branch_id가 지점 표에서 고유해야 방문 한 건이 지점 여러 개와 연결되지 않는다.

INNER JOIN은 양쪽에서 조건을 만족하는 조합만 남긴다. 부모 지점이 없는 방문은 결과에서 빠질 수 있다. 외래키는 이런 잘못된 참조를 막는 장치지만 데이터 유입 경로 전체에서 실제로 강제되는지 확인해야 한다.

항상 “방문 24행과 지점 4행을 연결하면 왜 24행인가?”를 설명해 보자. 지점 키가 고유하고 모든 방문의 지점이 존재한다면 각 방문은 정확히 하나의 지점에 연결되므로 24행을 유지한다. JOIN 종류만 외우는 것보다 이 사고가 중요하다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B07.sql
```

```sql
SELECT v.visit_id, b.branch_name, v.status
FROM visits AS v
JOIN branches AS b ON v.branch_id = b.branch_id
ORDER BY v.visit_id
LIMIT 6;
```

### 5. 결과와 코드 해설

| visit_id | branch_name | status |
| --- | --- | --- |
| 1 | Branch-A | completed |
| 2 | Branch-A | completed |
| 3 | Branch-A | cancelled |
| 4 | Branch-B | completed |
| 5 | Branch-B | completed |
| 6 | Branch-B | completed |

v와 b는 표의 짧은 별칭이다. `v.branch_id`는 visits 쪽의 열임을 밝힌다. ON이 연결 조건이다. 지점 이름을 덧붙였지만 출력 grain은 여전히 방문 한 건이다. 키가 고유하지 않으면 같은 방문이 여러 번 출력될 수 있다.

### 6. 자주 하는 실수

이름으로 JOIN하면 동명이인·표기 차이·이름 변경 문제를 만든다. 업무에서 합의한 안정적 식별자를 사용한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 시스템마다 고객 ID가 다를 때 매핑 규칙과 책임자를 찾는다.

**FDSE 관점:** JOIN 전후 행 수와 오른쪽 키의 고유성을 검증한다.

### 8. 직접 풀어 보기

**SQL-B07-1. 방문 ID와 담당 직원 이름을 연결하라. 담당자가 없는 방문은 이번에는 제외한다.**

힌트: workers.worker_id와 visits.worker_id를 연결한다.

[풀이 확인](#sql-b07-1)

**SQL-B07-2. 오른쪽 지점 표에서 branch_id=1이 두 행이면 어떤 일이 생기는가?**

힌트: 1번 지점 방문 한 행에 연결되는 상대가 몇 개인지 센다.

[풀이 확인](#sql-b07-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/tutorial-join.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/ddl-constraints.html)

---

<a id="sql-b08"></a>
## SQL-B08 · LEFT JOIN·ON과 WHERE: 0건인 지점도 남기기

**학습 목표:** 연결 대상이 없는 행을 보존하고 필터 위치의 영향을 설명한다.

**실행 구분:** SQLite 실행 확인. PostgreSQL 16에서도 사용할 수 있는 구문을 의도했으나 PostgreSQL 실행 검증은 하지 않음

### 1. 용어부터 이해하기

LEFT JOIN은 왼쪽 표의 행을 유지한다. 오른쪽에 대응 행이 없으면 오른쪽 열은 NULL이다. ON은 연결 기준, WHERE는 연결 이후 결과 필터다.

### 2. 비유로 잡는 그림

지점 전체 명부를 기준으로 완료 방문을 붙이면, 완료 방문이 없는 지점도 보고서에 이름이 남는다.

### 3. 원리와 업무에서의 의미

0건 지점을 보여 주려면 기준 표를 visits가 아니라 branches로 삼는다. 지점 목록에 완료 방문만 붙이고 그 개수를 센다. 오른쪽 visit_id는 실제 방문이 연결되었을 때만 값이 있으므로 COUNT(v.visit_id)가 0을 정확히 만든다.

LEFT JOIN 후 COUNT(*)를 하면 방문이 없는 지점에도 왼쪽에서 보존된 행 하나가 있으므로 1이 나온다. “결과 행 수”와 “매칭된 방문 수”의 차이다.

오른쪽 상태 조건을 WHERE v.status='completed'에 두면 연결되지 않은 행은 NULL 비교가 되어 제거된다. 모든 지점을 보존하려면 그 조건을 ON에 넣는다. 결과가 같아 보이는 데이터만으로 SQL이 맞는지 판단하지 말고 0건 지점을 넣어 테스트한다.

### 4. 따라 하는 예제

```bash
python run_sql.py sql/SQL_B08.sql
```

```sql
SELECT b.branch_id, b.branch_name,
       COUNT(v.visit_id) AS completed_visits
FROM branches b
LEFT JOIN visits v
  ON b.branch_id = v.branch_id
 AND v.status = 'completed'
GROUP BY b.branch_id, b.branch_name
ORDER BY b.branch_id;
```

### 5. 결과와 코드 해설

| branch_id | branch_name | completed_visits |
| --- | --- | --- |
| 1 | Branch-A | 6 |
| 2 | Branch-B | 9 |
| 3 | Branch-C | 3 |
| 4 | Branch-D | 0 |

지점 1,2,3,4가 모두 나오며 완료 건수는 6,9,3,0이다. GROUP BY에 ID와 이름을 함께 넣어 엔진 간 호환성과 의도를 명확히 했다. 방문이 없는 지점도 성과 모니터링 대상에 포함할 수 있다.

### 6. 자주 하는 실수

LEFT JOIN을 썼다는 이유만으로 왼쪽 행이 끝까지 보존되는 것은 아니다. 뒤의 WHERE·HAVING이 다시 제거할 수 있다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 영업 중이지만 데이터가 없는 지점과 실제 활동 0건인 지점을 구별한다.

**FDSE 관점:** 빈 지점·누락 참조·필터 조건을 포함하는 JOIN 테스트를 작성한다.

### 8. 직접 풀어 보기

**SQL-B08-1. 모든 지점의 예정 방문 수를 구하라.**

힌트: ON의 상태를 planned로 바꾼다.

[풀이 확인](#sql-b08-1)

**SQL-B08-2. 이 쿼리에서 COUNT(*)와 COUNT(v.visit_id)는 4번 지점에서 각각 얼마인가?**

힌트: 보존된 왼쪽 행과 오른쪽 값의 유무를 구분한다.

[풀이 확인](#sql-b08-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/queries-table-expressions.html#QUERIES-JOIN)

---

<a id="sql-b09"></a>
## SQL-B09 · 스키마·제약조건·정규화: 틀린 데이터가 들어오기 어렵게 만들기

**학습 목표:** 업무 규칙을 자료형·키·제약조건으로 표현한다.

**실행 구분:** 독립적인 메모리 SQLite DB에서 실행 확인. 원본 실습 DB를 수정하지 않음

### 1. 용어부터 이해하기

스키마(schema)는 표·열·자료형·관계의 구조다. 제약조건(constraint)은 저장 가능한 데이터의 규칙이다. 정규화(normalization)는 중복으로 인한 수정 모순을 줄이도록 데이터를 나누는 설계다.

### 2. 비유로 잡는 그림

좋은 입력 양식은 직원이 주의하길 기대하는 대신, 잘못된 값이 들어갈 칸 자체를 줄인다.

### 3. 원리와 업무에서의 의미

ID가 필수라면 PRIMARY KEY, 상태가 필수라면 NOT NULL, 요금이 음수일 수 없다면 CHECK를 적용한다. Python 검증은 친절한 오류 메시지에 유용하고 DB 제약조건은 다른 유입 경로까지 포함하는 마지막 방어선이 된다.

이 강의는 독립된 임시 표에 방문 ID와 요금을 저장한다. 실제 모델에서는 고객·직원·지점의 키를 연결한다. 고객 이름·지점 이름·방문 날짜를 한 표에 모두 반복하면 이름 변경 시 일부 행만 고쳐져 모순이 생길 수 있다.

정규화된 거래 모델과 분석용 넓은 표는 목적이 다르다. 모든 상황에서 표를 최대한 나누거나 모든 것을 합치는 규칙은 없다. 원본의 정합성을 유지하면서 분석용 파생 표를 만드는 방식을 중급에서 배운다. CHECK는 NULL을 반드시 막아 주지 않으므로 NOT NULL도 별도로 둔다.

### 4. 따라 하는 예제

```bash
python run_sql_demo.py sql/SQL_B09.sql
```

```sql
CREATE TEMP TABLE fee_demo (
    visit_id INTEGER PRIMARY KEY,
    fee_cents INTEGER NOT NULL CHECK (fee_cents >= 0),
    status TEXT NOT NULL CHECK (status IN ('planned', 'completed', 'cancelled'))
);
INSERT INTO fee_demo VALUES (1, 10000, 'planned');
SELECT * FROM fee_demo;
```

### 5. 결과와 코드 해설

| visit_id | fee_cents | status |
| --- | --- | --- |
| 1 | 10000 | planned |

TEMP는 현재 연결 동안만 사용하는 임시 표다. 기본키 중복, 음수 요금, 허용 목록 밖의 상태를 넣는 추가 실험은 실패해야 한다. PostgreSQL 실습에서는 오류 후 트랜잭션 상태도 확인한다. 이 예제는 실제 visits 표를 수정하지 않는다.

### 6. 자주 하는 실수

CHECK(fee_cents>=0)만으로는 NULL이 막히지 않는다. “값이 있어야 함”과 “그 값의 범위”는 별도 조건이다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 고객과 허용 상태·필수 필드·예외 업무를 정의한다.

**FDSE 관점:** 자료형과 제약조건을 코드 리뷰 대상으로 삼고 마이그레이션 계획을 만든다.

### 8. 직접 풀어 보기

**SQL-B09-1. fee_demo에 (2,-1,"planned")를 넣으면 어떻게 되어야 하는가?**

힌트: 음수 금액 규칙을 찾는다.

[풀이 확인](#sql-b09-1)

**SQL-B09-2. 고객 이름을 기본키로 쓰지 않는 이유를 세 가지 설명하라.**

힌트: 중복·변경·입력 차이를 생각한다.

[풀이 확인](#sql-b09-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/ddl-constraints.html)

---

<a id="sql-b10"></a>
## SQL-B10 · INSERT·UPDATE·DELETE·트랜잭션: 안전하게 상태 바꾸기

**학습 목표:** 변경 전에 대상을 확인하고 되돌리기까지 한 단위로 이해한다.

**실행 구분:** 독립적인 메모리 SQLite DB에서 실행 확인. 원본 실습 DB를 수정하지 않음

### 1. 용어부터 이해하기

INSERT는 추가, UPDATE는 수정, DELETE는 삭제다. 트랜잭션(transaction)은 여러 작업을 함께 성공시키거나 함께 취소하는 단위다. COMMIT은 확정, ROLLBACK은 취소다.

### 2. 비유로 잡는 그림

장부를 수정할 때 초안에서 검토한 뒤 확정 도장을 찍거나, 잘못되면 수정 전 상태로 돌리는 절차다.

### 3. 원리와 업무에서의 의미

조회와 변경은 위험도가 다르다. WHERE 없는 UPDATE는 모든 행을 바꿀 수 있다. 변경 전 같은 조건으로 SELECT를 실행하고 예상 영향 행 수를 적는다. 학습은 항상 별도의 폐기 가능한 데이터에서 한다.

트랜잭션은 에러가 안 났다는 이유만으로 업무적으로 올바름을 보장하지 않는다. 엉뚱한 고객의 상태를 바꾸는 쿼리도 성공할 수 있다. 올바른 대상 조건과 영향 행 수 확인, 업무 제약조건이 함께 필요하다.

아래 예제는 임시 작업 표를 만들고 예정 방문을 완료로 바꿔 본 뒤 ROLLBACK한다. 마지막 상태는 planned다. 실제 여러 사용자가 동시에 수정하는 문제는 심화의 격리·잠금에서 다룬다. 여기서는 데이터 변경의 경계와 되돌리기를 먼저 익힌다.

### 4. 따라 하는 예제

```bash
python run_sql_demo.py sql/SQL_B10.sql
```

```sql
CREATE TEMP TABLE change_demo (visit_id INTEGER PRIMARY KEY, status TEXT NOT NULL);
INSERT INTO change_demo VALUES (1, 'planned');
BEGIN;
UPDATE change_demo SET status='completed'
WHERE visit_id=1 AND status='planned';
SELECT * FROM change_demo;
ROLLBACK;
SELECT * FROM change_demo;
```

### 5. 결과와 코드 해설

**SELECT 결과 1**
| visit_id | status |
| --- | --- |
| 1 | completed |
**SELECT 결과 2**
| visit_id | status |
| --- | --- |
| 1 | planned |

처음 SELECT에서는 completed가 보인다. ROLLBACK 후 두 번째 SELECT는 planned를 보여 준다. 이미 완료된 행을 다시 수정하지 않도록 기존 상태도 WHERE에 넣었다. 실제 애플리케이션에서는 수정된 행 수가 1인지 확인해야 한다.

### 6. 자주 하는 실수

운영 DB에서 연습하지 않는다. EXPLAIN ANALYZE도 변경 쿼리를 실제 실행하므로 “분석 명령이니까 안전하다”고 생각하면 안 된다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 누가 어떤 조건에서 상태를 변경할 수 있는지 업무 책임을 정한다.

**FDSE 관점:** 트랜잭션·조건부 갱신·감사 기록·롤백을 함께 설계한다.

### 8. 직접 풀어 보기

**SQL-B10-1. 예정 상태인 visit_id=1만 삭제하는 쿼리를 작성하되 실제 데이터에서는 실행하지 마라.**

힌트: ID와 기존 상태를 함께 제한한다.

[풀이 확인](#sql-b10-1)

**SQL-B10-2. 트랜잭션을 쓰면 WHERE 없이 전체 행을 바꿔도 안전한가?**

힌트: 원자성과 업무 정확성은 다르다.

[풀이 확인](#sql-b10-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/tutorial-transactions.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/dml.html)



---
