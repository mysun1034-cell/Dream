# 실습 환경과 공통 데이터 사전

## 1. 두 실행 환경을 구분하기

**Python + SQLite:** DB 서버 설치 없이 파일 하나로 표와 SQL을 연습합니다. 본문에 SQLite 실행 확인 표시가 있는 예제는 제작 환경에서 실제 실행했습니다.

**PostgreSQL 16:** 실행 계획·RLS·파티션·일부 시각 처리는 PostgreSQL 문법입니다. Docker Compose 구성을 제공하지만 제작 환경에는 PostgreSQL 서버/클라이언트와 Docker가 없어 실행 검증하지 않았습니다. SQLite에서 PostgreSQL 전용 코드를 실행하지 마세요.

버전은 재현을 위한 교육 기준이며 최신이라는 주장이 아닙니다. 제작 검증은 Python 3.13.5에서 했고 본문은 Python 3.12 이상을 대상으로 작성했습니다. 모든 OS·모든 3.12+ 조합을 시험한 것은 아닙니다.

## 2. 압축을 풀고 시작하기

압축을 풀면 `Palantir_SQL_Python_Course/` 안에 `docs/`와 `lab/`이 있습니다. 아래 명령은 현재 위치가 압축을 푼 폴더의 상위 폴더일 때의 예입니다. 그 외에는 실제 `lab/` 경로로 먼저 이동합니다.

```bash
cd Palantir_SQL_Python_Course/lab
pwd
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python --version
python bootstrap.py
python -m unittest discover -s tests -p test_core.py -v
python -m examples.PY_B01
python run_sql.py sql/SQL_B01.sql
```

**주의:** `bootstrap.py`는 이 교재의 `lab/data/carelink.db`를 삭제하고 합성 데이터로 다시 만듭니다. 생성 CSV와 PostgreSQL 시드 SQL도 다시 작성합니다. 자신의 결과를 그 고정 파일에 덮어 저장하지 말고 별도 폴더에 보관하세요. 외부 DB에는 접속하지 않습니다.

WSL에서 Windows D 드라이브는 `/mnt/d/…` 형태로 접근합니다. 예를 들어 `D:\Dream\Palantir_SQL_Python_Course`에 압축을 풀었다면 다음과 같습니다. 실제 위치가 다르면 경로를 바꿉니다.

```bash
cd /mnt/d/Dream/Palantir_SQL_Python_Course/lab
```

가상환경은 학습 폴더의 Python 패키지를 분리하는 공간입니다. 활성화는 현재 터미널에 적용되므로 새 터미널에서는 다시 `source .venv/bin/activate`를 실행합니다. Ubuntu에 venv 패키지가 없으면 시스템 정책을 확인한 뒤 `sudo apt update`와 `sudo apt install python3-venv`로 준비할 수 있습니다. 시스템 변경 권한이 없으면 관리자에게 확인합니다.

## 3. 중급·심화 패키지와 전체 검증

```bash
# lab/에서 가상환경을 활성화한 상태
python -m pip install -r requirements-tested.txt
python -m pytest tests examples/PY_I09.py -q
python verify.py
```

검증 환경의 패키지는 pandas 2.2.3, pytest 9.0.2, FastAPI 0.128.2, Pydantic 2.13.4, HTTPX 0.28.1, Uvicorn 0.48.0입니다. 설치에는 네트워크·패키지 저장소 접근이 필요합니다. 운영에서는 지원 버전·취약점·조직 정책을 별도로 검토해야 합니다.

전체 검증은 **34개 테스트**와 **51개 독립 예제**를 실행합니다. pytest 강의의 6개 테스트가 34개에 포함됩니다. 따라서 본문 예제 60개 중 52개를 실행 확인했고 PostgreSQL 전용 8개는 미실행입니다. 예제 실행 성공은 모든 입력에서의 정확성이나 운영 준비 완료를 뜻하지 않습니다.

`run_sql.py`는 학습 SQLite DB를 읽기 전용으로 엽니다. 쓰기·트랜잭션 강의 SQL-B09와 B10은 새 메모리 DB에서 다음과 같이 실행합니다.

```bash
python run_sql_demo.py sql/SQL_B09.sql
python run_sql_demo.py sql/SQL_B10.sql
```

## 4. 별도 로컬 PostgreSQL 16 실습 DB

Docker와 Compose 사용이 이미 가능한 환경을 전제로 합니다. 설치는 환경별 공식 지침과 조직 정책을 따릅니다. 제공 설정은 `127.0.0.1:55432`에만 포트를 바인딩합니다. `local-training-only`는 공개된 학습용 비밀번호이지 실제 비밀이 아닙니다. 운영에 재사용하지 마세요.

```bash
# lab/에서 실행. 전용 학습 컨테이너를 준비.
docker compose up -d db
docker compose ps

# db 정상 상태를 확인한 뒤 빈 DB에 최초 1회 적재.
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/00_postgres_seed.sql

# PostgreSQL 전용 예제
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_I06.sql
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_A01.sql

# SQLite 전용 지표 쿼리의 PostgreSQL 대응판
docker compose exec -T db psql -U course -d carelink -v ON_ERROR_STOP=1 < sql/SQL_I10_postgres.sql
```

시드 스크립트는 기존 표를 삭제하지 않습니다. 같은 DB에 다시 실행하면 표가 존재한다는 오류가 나도록 설계했습니다. 이를 무시하고 중복 적재하지 마세요. 최초 실행이 실패하면 원인을 확인하고 독립적인 빈 학습 DB에서 다시 시작합니다.

```bash
# 대화형 접속; 종료는 \q
docker compose exec db psql -U course -d carelink

# 컨테이너 중지·제거. named volume의 학습 데이터는 남음.
docker compose down
```

볼륨까지 삭제하는 명령은 실습 변경을 잃을 수 있어 기본 절차에서 제외했습니다. 리셋 전에 대상이 이 교재 전용인지 확인하고 필요한 데이터를 보관합니다. 운영 DB에서 예제 DDL·역할 생성문을 실행하지 마세요.

SQL-A03은 단일 세션에서 버전 충돌을 모사합니다. 진짜 동시성 검증에는 두 연결이 필요합니다. SQL-A08에는 역할 생성 권한이 필요하며, 없으면 미검증으로 기록하고 관리자 준비 없이 우회하지 않습니다.

## 5. 로컬 학습 API

```bash
# lab/에서 실행
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

별도 터미널에서 확인합니다.

```bash
curl http://127.0.0.1:8000/health
curl -H 'X-Demo-Key: demo-branch-a' 'http://127.0.0.1:8000/visits?branch_id=1&limit=2'
curl -H 'X-Demo-Key: demo-branch-a' 'http://127.0.0.1:8000/visits?branch_id=2'
```

두 번째 응답에는 방문 1·2가 포함되고 세 번째는 403입니다. `demo-branch-a`는 지점 1, `demo-branch-b`는 지점 2, `demo-reviewer`는 지점 1~4 조회용 **공개 테스트 토큰**입니다. 누구나 값을 알 수 있으므로 실제 인증이 아닙니다. 외부에 공개하지 마세요.

현재 API는 읽기 전용입니다. 운영 OIDC/OAuth 인증, 비밀 관리, TLS, 레이트 제한, 완전한 감사·배포·백업, 방문 변경 API는 포함되지 않았습니다. 프로젝트 확장 과제와 이미 구현된 기능을 구분합니다.

## 6. 단위·시점·데이터 계약

모든 데이터는 생성된 합성 데이터입니다. 날짜는 2026년 8월이며 현재 운영 상황을 뜻하지 않습니다. 세 날의 패턴이 반복되므로 실제 예측 성능이나 정책 효과를 증명할 수 있는 표본이 아닙니다.

SQLite 날짜/시각은 정규화된 ISO 문자열, PostgreSQL 시드는 DATE 또는 TIMESTAMPTZ를 사용합니다. 원천 시각은 UTC 오프셋을 포함합니다. 서울 업무 날짜로 묶으려면 변환이 필요합니다. 문자열 시간 비교는 형식·오프셋이 같다는 제한이 명시된 예제에만 적용합니다.

`fee_cents`, `amount_cents`는 **가상 화폐 최소 단위의 정수**입니다. 실제 원화·달러 가격이나 환율이 아닙니다. 100으로 나눠 주단위로 표시하는 코드는 계산 연습입니다.

## 7. 전체 데이터 사전

### branches — 한 행은 지점 하나 / 4행

| 열 | 타입 | NULL | 의미·제약 |
|---|---|---|---|
| branch_id | INTEGER | 불가 | 기본키 1~4 |
| branch_name | TEXT | 불가 | Branch-A~D, UNIQUE |

### workers — 한 행은 담당자 하나 / 8행

| 열 | 타입 | NULL | 의미·제약 |
|---|---|---|---|
| worker_id | INTEGER | 불가 | 기본키 1~8 |
| branch_id | INTEGER | 불가 | branches 외래키 |
| worker_name | TEXT | 불가 | 합성 담당자 이름 |
| skill_level | INTEGER | 불가 | 학습용 수준 1~3 CHECK |

지점마다 2명입니다. skill_level은 실제 법적·의료적 자격을 뜻하지 않습니다.

### clients — 한 행은 고객 하나 / 12행

| 열 | 타입 | NULL | 의미·제약 |
|---|---|---|---|
| client_id | INTEGER | 불가 | 기본키 1~12 |
| branch_id | INTEGER | 불가 | 현재 소속 지점 외래키 |
| joined_on | SQLite TEXT / PG DATE | 불가 | 홀수 ID 7월 1일, 짝수 ID 8월 1일 |

지점마다 고객 3명입니다. 과거 소속 이력은 기본 표에 없고 SQL-I09에서 별도 예제로 다룹니다.

### visits — 한 행은 방문 하나 / 24행

| 열 | 타입 | NULL | 의미·제약 |
|---|---|---|---|
| visit_id | INTEGER | 불가 | 기본키 1~24 |
| client_id | INTEGER | 불가 | clients 외래키 |
| worker_id | INTEGER | 가능 | workers 외래키, 미배정은 NULL |
| branch_id | INTEGER | 불가 | 방문 지점 외래키 |
| scheduled_start | SQLite TEXT / PG TIMESTAMPTZ | 불가 | 예정 시작 UTC |
| actual_start | SQLite TEXT / PG TIMESTAMPTZ | 가능 | 실제 시작 UTC |
| status | TEXT | 불가 | completed / cancelled / planned CHECK |
| duration_minutes | INTEGER | 불가 | 양의 정수, 기본 60 |
| fee_cents | INTEGER | 불가 | 가상 금액, 0 이상 |

외래키만으로 담당자 지점과 방문 지점의 일치 같은 모든 업무 규칙이 보장되는 것은 아닙니다. 필요한 규칙은 추가 검증합니다.

### invoices — 한 행은 청구 하나 / 6행

| 열 | 타입 | NULL | 의미·제약 |
|---|---|---|---|
| invoice_id | INTEGER | 불가 | 기본키 |
| client_id | INTEGER | 불가 | clients 외래키 |
| amount_cents | INTEGER | 불가 | 청구 가상 금액, 0 이상 |
| issued_on | SQLite TEXT / PG DATE | 불가 | 청구 일자 |

visit_id가 없으므로 이 데이터만으로 방문별 청구 배분을 알 수 없습니다. 필요하면 청구 항목 연결 표를 설계합니다.

### payments — 한 행은 입금 하나 / 7행

| 열 | 타입 | NULL | 의미·제약 |
|---|---|---|---|
| payment_id | INTEGER | 불가 | 기본키 |
| invoice_id | INTEGER | 불가 | invoices 외래키, 청구당 여러 입금 가능 |
| amount_cents | INTEGER | 불가 | 입금 가상 금액, 0보다 큼 |
| paid_on | SQLite TEXT / PG DATE | 불가 | 입금 일자 |

환불·수수료·환율은 모델링하지 않습니다. 잔액=청구-입금의 단순 계약입니다.

### raw_events.csv — 한 행은 원천 이벤트 하나 / 6행

| 열 | 의미 | 의도한 오류 |
|---|---|---|
| event_id | 이벤트 ID | 업무 대상 ID와 구분 |
| visit_id | 원천 방문 ID | bad 같은 잘못된 정수 |
| status | 원천 상태 | 공백·대문자·허용되지 않은 상태 |
| updated_at | 원천 갱신 시각 | not-a-date 같은 잘못된 날짜 |

원천 방문 ID 101~104는 기본 visits의 1~24와 **다른 증분 적재 실습 공간**입니다. API DB에 자동 합쳐지지 않습니다. ETL은 별도 DB의 event_state와 quarantine을 만듭니다. 완전한 원본 이벤트 원장이나 전역 exactly-once 시스템은 아닙니다.

## 8. 손으로 검산하는 기준값

| 지점 | 전체 | 완료 | 평가 가능 | 지연 | 완료 시각 누락 | 지연율 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 9 | 6 | 6 | 3 | 0 | 50% |
| 2 | 9 | 9 | 6 | 3 | 3 | 50% |
| 3 | 6 | 3 | 3 | 0 | 0 | 0% |
| 4 | 0 | 0 | 0 | 0 | 0 | NULL |
| 전체 | 24 | 18 | 15 | 6 | 3 | 40% |

완료 시각 누락 방문은 6·14·22입니다. 방문 자체가 없는 고객은 9·10·11·12, 완료 방문이 한 번도 없는 고객은 3·7·9·10·11·12입니다.

청구 합계 100,000, 입금 57,000, 잔액 43,000입니다. 청구와 입금을 직접 LEFT JOIN한 뒤 청구 합계를 더하면 135,000으로 부풀어집니다. 청구 1번과 6번에 입금 두 건이 있기 때문입니다.

전체 방문 금액은 324,000, 완료 방문 금액은 240,000입니다. 방문 금액과 invoices 청구 합계가 일치해야 한다는 계약은 없습니다. 서로 다른 장부를 의미 확인 없이 대사하지 않습니다.

## 9. 자주 막히는 실행 문제

| 증상 | 먼저 확인 | 해결 방향 |
|---|---|---|
| No such file or directory | pwd, ls, 대소문자, 중첩 압축 폴더 | 실제 lab 위치로 이동 |
| No module named course_lib | 파일 경로로 예제를 직접 실행했는가 | lab에서 python -m examples.PY_B10 |
| No module named pandas | 활성 Python과 가상환경 | python -m pip로 설치 |
| no such table | bootstrap 여부, DB 경로 | 원본 보관 확인 후 생성 |
| TIMESTAMPTZ 문법 오류 | SQLite에서 PostgreSQL 예제를 실행했는가 | 엔진 표시 확인 |
| readonly database | 조회 도구에 쓰기를 넣었는가 | 쓰기 데모는 run_sql_demo |
| port already allocated | 55432/8000 사용 중인가 | 충돌 프로세스 확인 |
| 기대값과 다른 KPI | 합성 원본을 수정했는가 | 원본·수정 데이터와 기대값 분리 |

`bootstrap.py`는 데이터 생성, `course_lib.py`는 공통 규칙, `etl.py`는 정제·재실행, `api.py`는 조회·권한 계약을 보여 줍니다. 처음부터 전부 외우지 말고 등장하는 강의와 함께 읽습니다.

공식 참고: [Python venv](https://docs.python.org/3.12/library/venv.html), [Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html), [PostgreSQL 16](https://www.postgresql.org/docs/16/), [FastAPI](https://fastapi.tiangolo.com/).



---
