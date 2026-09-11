# 실습 코드 부록: 데이터 생성·공통 규칙·ETL·API·테스트

이 부록은 ZIP의 핵심 파일을 그대로 수록합니다. 코드만 읽는 경우에도 원천 생성 방식과 검증 규칙을 확인할 수 있습니다. 실행은 ZIP 안의 파일을 사용하는 편이 편리합니다. 본문 강의별 예제 60개는 각 교재에 이미 포함되어 있어 여기서는 공통 모듈을 수록합니다.

**안전 범위:** bootstrap은 고정된 학습 DB와 생성 CSV를 다시 만듭니다. API는 로컬 데모 키 기반 읽기 전용입니다. PostgreSQL과 Foundry 실행 검증은 별개입니다. 실제 데이터나 비밀을 넣지 마세요.

## lab/bootstrap.py

```python
"""Create deterministic, wholly fictional training data; never connect to a production database."""
from __future__ import annotations
import csv
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB = DATA / "carelink.db"

SCHEMA = """
CREATE TABLE branches (
 branch_id INTEGER PRIMARY KEY,
 branch_name TEXT NOT NULL UNIQUE
);
CREATE TABLE workers (
 worker_id INTEGER PRIMARY KEY,
 branch_id INTEGER NOT NULL REFERENCES branches(branch_id),
 worker_name TEXT NOT NULL,
 skill_level INTEGER NOT NULL CHECK (skill_level BETWEEN 1 AND 3)
);
CREATE TABLE clients (
 client_id INTEGER PRIMARY KEY,
 branch_id INTEGER NOT NULL REFERENCES branches(branch_id),
 joined_on TEXT NOT NULL
);
CREATE TABLE visits (
 visit_id INTEGER PRIMARY KEY,
 client_id INTEGER NOT NULL REFERENCES clients(client_id),
 worker_id INTEGER REFERENCES workers(worker_id),
 branch_id INTEGER NOT NULL REFERENCES branches(branch_id),
 scheduled_start TEXT NOT NULL,
 actual_start TEXT,
 status TEXT NOT NULL CHECK (status IN ('completed','cancelled','planned')),
 duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
 fee_cents INTEGER NOT NULL CHECK (fee_cents >= 0)
);
CREATE TABLE invoices (
 invoice_id INTEGER PRIMARY KEY,
 client_id INTEGER NOT NULL REFERENCES clients(client_id),
 amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
 issued_on TEXT NOT NULL
);
CREATE TABLE payments (
 payment_id INTEGER PRIMARY KEY,
 invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id),
 amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
 paid_on TEXT NOT NULL
);
"""

def rows_by_table() -> dict[str, list[tuple]]:
    branches = [(1,'Branch-A'),(2,'Branch-B'),(3,'Branch-C'),(4,'Branch-D')]
    workers = [(i, (i-1)//2+1, f'Worker-{i:02d}', (i-1)%3+1) for i in range(1,9)]
    clients = [(i,(i-1)//3+1,'2026-07-01' if i%2 else '2026-08-01') for i in range(1,13)]
    # Same statuses in three days; deliberately include completed visits with missing timestamps.
    statuses = ['completed','completed','cancelled','completed','completed','completed','planned','completed']
    delays = [0,15,None,30,5,None,None,10]
    visits = []
    for day in range(3):
        for j in range(8):
            client_id = j+1
            branch_id = (client_id-1)//3+1
            visit_id = day*8+j+1
            scheduled = datetime(2026,8,1+day,0,0,tzinfo=timezone.utc)+timedelta(hours=j)
            actual = None if delays[j] is None else scheduled+timedelta(minutes=delays[j])
            worker_id = None if statuses[j]=='planned' else (branch_id-1)*2+(j%2)+1
            visits.append((visit_id,client_id,worker_id,branch_id,
                           scheduled.isoformat(),actual.isoformat() if actual else None,
                           statuses[j],60,10000+j*1000))
    invoices=[(1,1,10000,'2026-08-01'),(2,2,20000,'2026-08-01'),
              (3,4,15000,'2026-08-02'),(4,5,12000,'2026-08-02'),
              (5,7,18000,'2026-08-03'),(6,8,25000,'2026-08-03')]
    payments=[(1,1,4000,'2026-08-01'),(2,1,6000,'2026-08-02'),
              (3,2,5000,'2026-08-02'),(4,3,15000,'2026-08-03'),
              (5,4,12000,'2026-08-03'),(6,6,10000,'2026-08-03'),
              (7,6,5000,'2026-08-04')]
    return dict(branches=branches,workers=workers,clients=clients,visits=visits,
                invoices=invoices,payments=payments)

def seed_connection(conn: sqlite3.Connection) -> None:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.executescript(SCHEMA)
    for table, rows in rows_by_table().items():
        placeholders=','.join('?' for _ in rows[0])
        conn.executemany(f'INSERT INTO {table} VALUES ({placeholders})',rows)
    conn.commit()

def sql_literal(value: object) -> str:
    if value is None:
        return 'NULL'
    if isinstance(value,int):
        return str(value)
    return "'"+str(value).replace("'","''")+"'"

def main() -> None:
    DATA.mkdir(exist_ok=True)
    # Fixed allowlisted training path, not an arbitrary user database.
    if DB.exists():
        DB.unlink()
    with sqlite3.connect(DB) as conn:
        seed_connection(conn)
        for table in rows_by_table():
            cur=conn.execute(f'SELECT * FROM {table}')
            with (DATA/f'{table}.csv').open('w',encoding='utf-8',newline='') as f:
                writer=csv.writer(f); writer.writerow([d[0] for d in cur.description]);writer.writerows(cur)
    raw = [
      {'event_id':'e1','visit_id':'101','status':' COMPLETED ','updated_at':'2026-08-04T01:00:00+00:00'},
      {'event_id':'e2','visit_id':'102','status':'planned','updated_at':'2026-08-04T01:00:00+00:00'},
      {'event_id':'e3','visit_id':'101','status':'completed','updated_at':'2026-08-04T02:00:00+00:00'},
      {'event_id':'e4','visit_id':'bad','status':'completed','updated_at':'2026-08-04T01:00:00+00:00'},
      {'event_id':'e5','visit_id':'103','status':'unknown','updated_at':'2026-08-04T01:00:00+00:00'},
      {'event_id':'e6','visit_id':'104','status':'planned','updated_at':'not-a-date'},
    ]
    with (DATA/'raw_events.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(raw[0]));writer.writeheader();writer.writerows(raw)
    pg_schema=SCHEMA.replace('joined_on TEXT','joined_on DATE').replace('issued_on TEXT','issued_on DATE').replace('paid_on TEXT','paid_on DATE').replace('scheduled_start TEXT','scheduled_start TIMESTAMPTZ').replace('actual_start TEXT','actual_start TIMESTAMPTZ')
    pg='-- Only for the empty, disposable course database. No DROP statements.\nBEGIN;\n'+pg_schema
    for table,rows in rows_by_table().items():
        pg += f'INSERT INTO {table} VALUES\n'+',\n'.join('('+','.join(map(sql_literal,r))+')' for r in rows)+';\n'
    pg+='COMMIT;\n'
    (ROOT/'sql'/'00_postgres_seed.sql').write_text(pg,encoding='utf-8')
    counts={k:len(v) for k,v in rows_by_table().items()}
    (DATA/'expected_counts.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
    print(f'Created {DB.name}: '+json.dumps(counts))

if __name__=='__main__':
    main()
```

## lab/course_lib.py

```python
"""Small, explicit training functions. Synthetic operations data only."""
from __future__ import annotations
import csv
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'carelink.db'

def read_csv(name: str) -> list[dict[str,str]]:
    # Deliberately fixed set of course files, not an arbitrary path endpoint.
    allowed={'branches','workers','clients','visits','invoices','payments','raw_events'}
    if name not in allowed:
        raise ValueError('unknown course dataset')
    with (ROOT/'data'/f'{name}.csv').open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def delay_minutes(scheduled: str, actual: str | None) -> float | None:
    if not actual:
        return None
    start=datetime.fromisoformat(scheduled)
    finish=datetime.fromisoformat(actual)
    if start.tzinfo is None or finish.tzinfo is None:
        raise ValueError('timezone-aware timestamps required')
    return (finish-start).total_seconds()/60

def classify_visit(status: str, delay: float | None, threshold: float=10) -> str:
    if status not in {'completed','cancelled','planned'}:
        raise ValueError('unknown status')
    if status!='completed':
        return 'excluded'
    if delay is None:
        return 'unknown'
    return 'late' if delay>threshold else 'on_time'

def kpi(rows: list[dict[str,str]]) -> dict[str,int|float|None]:
    counts={'total':len(rows),'completed':0,'eligible':0,'late':0,'unknown':0}
    for row in rows:
        status=row['status']
        # Only completed rows need actual-start parsing for this particular KPI.
        delay=delay_minutes(row['scheduled_start'],row.get('actual_start')) if status=='completed' else None
        label=classify_visit(status,delay)
        if status=='completed':
            counts['completed']+=1
        if label=='unknown':
            counts['unknown']+=1
        elif label in {'late','on_time'}:
            counts['eligible']+=1
            counts['late']+=int(label=='late')
    result:dict[str,int|float|None]=dict(counts)
    result['late_rate']=counts['late']/counts['eligible'] if counts['eligible'] else None
    return result

def query(sql: str, params: tuple=()) -> list[dict]:
    if not DB.exists():
        raise FileNotFoundError('Run python bootstrap.py first')
    # Read-only connection prevents accidental mutations through this helper.
    with closing(sqlite3.connect(DB.as_uri()+'?mode=ro',uri=True)) as conn:
        conn.row_factory=sqlite3.Row
        return [dict(row) for row in conn.execute(sql,params)]
```

## lab/run_sql.py

```python
"""Execute a course SELECT/WITH query in a read-only SQLite connection."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from course_lib import query

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('file',type=Path)
    args=parser.parse_args()
    sql=args.file.read_text(encoding='utf-8')
    try:
        print(json.dumps(query(sql),ensure_ascii=False,indent=2))
    except Exception as exc:
        raise SystemExit(f'{type(exc).__name__}: {exc}') from exc

if __name__=='__main__':
    main()
```

## lab/run_sql_demo.py

```python
"""Execute SQL in a newly seeded in-memory database, never the on-disk dataset."""
from pathlib import Path
from contextlib import closing
import argparse, json, sqlite3
from bootstrap import seed_connection

def execute_demo(sql: str) -> list[list[dict]]:
    results = []
    with closing(sqlite3.connect(":memory:")) as conn:
        seed_connection(conn)
        conn.isolation_level = None  # each statement commits unless BEGIN is explicit
        conn.row_factory = sqlite3.Row
        pending = ""
        for line in sql.splitlines(keepends=True):
            pending += line
            if sqlite3.complete_statement(pending):
                cursor = conn.execute(pending)
                if cursor.description:
                    results.append([dict(row) for row in cursor.fetchall()])
                pending = ""
        if pending.strip():
            cursor = conn.execute(pending)
            if cursor.description:
                results.append([dict(row) for row in cursor.fetchall()])
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql_file", type=Path)
    args = parser.parse_args()
    print(json.dumps(execute_demo(args.sql_file.read_text(encoding="utf-8")), ensure_ascii=False, indent=2))
```

## lab/etl.py

```python
"""Toy event-state ingestion with validation, quarantine and transactional idempotence.
Single-process batch only. Not a general exactly-once streaming system.
"""
from __future__ import annotations
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ALLOWED={'completed','cancelled','planned'}

def normalize(row: dict[str,str]) -> dict:
    event_id=row['event_id'].strip()
    if not event_id:
        raise ValueError('empty event_id')
    visit_id=int(row['visit_id'])
    if visit_id<=0:
        raise ValueError('visit_id must be positive')
    status=row['status'].strip().lower()
    if status not in ALLOWED:
        raise ValueError('invalid status')
    updated=datetime.fromisoformat(row['updated_at'])
    if updated.tzinfo is None:
        raise ValueError('timezone missing')
    return {'event_id':event_id,'visit_id':visit_id,'status':status,
            'updated_at':updated.astimezone(timezone.utc).isoformat()}

def load_events(csv_path: Path, db_path: Path) -> dict[str,int]:
    valid=[];bad=[]
    with csv_path.open(encoding='utf-8',newline='') as f:
        for line,row in enumerate(csv.DictReader(f),2):
            try:
                valid.append(normalize(row))
            except (ValueError,KeyError,TypeError) as exc:
                bad.append({'line':line,'reason':str(exc),'row':row})
    conn=sqlite3.connect(db_path)
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS event_state(
          visit_id INTEGER PRIMARY KEY, status TEXT NOT NULL,
          updated_at TEXT NOT NULL, event_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS quarantine(
          source_file TEXT NOT NULL, source_line INTEGER NOT NULL,
          reason TEXT NOT NULL, raw_json TEXT NOT NULL,
          PRIMARY KEY(source_file,source_line));
        """)
        # A complete batch either commits or rolls back.
        with conn:
            # Refresh this source's quarantine, so reruns do not duplicate failures.
            conn.execute('DELETE FROM quarantine WHERE source_file=?',(str(csv_path.resolve()),))
            for row in sorted(valid,key=lambda x:(x['updated_at'],x['event_id'])):
                conn.execute("""
                INSERT INTO event_state(visit_id,status,updated_at,event_id)
                VALUES (:visit_id,:status,:updated_at,:event_id)
                ON CONFLICT(visit_id) DO UPDATE SET
                  status=excluded.status,updated_at=excluded.updated_at,event_id=excluded.event_id
                WHERE excluded.updated_at > event_state.updated_at
                   OR (excluded.updated_at=event_state.updated_at
                       AND excluded.event_id > event_state.event_id)
                """,row)
            conn.executemany('INSERT INTO quarantine VALUES (?,?,?,?)',
                [(str(csv_path.resolve()),r['line'],r['reason'],json.dumps(r['row'])) for r in bad])
        return {'valid_input':len(valid),'invalid_input':len(bad),
                'state_rows':conn.execute('SELECT COUNT(*) FROM event_state').fetchone()[0]}
    finally:
        conn.close()

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    print(load_events(root/'data'/'raw_events.csv',root/'data'/'events.db'))
```

## lab/api.py

```python
"""Local-only, read-only teaching API; demo keys are NOT production authentication."""
from __future__ import annotations
from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from course_lib import query

app=FastAPI(title='CareLink Synthetic Training API')
# Fixed demo keys intentionally checked into a training repository. No real credentials.
DEMO_ACCESS={'demo-branch-a':{1},'demo-branch-b':{2},'demo-reviewer':{1,2,3,4}}

class VisitOut(BaseModel):
    visit_id:int
    branch_id:int
    status:str
    scheduled_start:str

@app.get('/health')
def health() -> dict[str,str]:
    return {'status':'ok'}

@app.get('/visits',response_model=list[VisitOut])
def visits(
    branch_id:Annotated[int,Query(ge=1,le=4)],
    after_id:Annotated[int,Query(ge=0)]=0,
    limit:Annotated[int,Query(ge=1,le=100)]=20,
    x_demo_key:Annotated[str|None,Header()]=None,
) -> list[dict]:
    permissions=DEMO_ACCESS.get(x_demo_key or '')
    if permissions is None:
        raise HTTPException(status_code=401,detail='Unknown demo key')
    if branch_id not in permissions:
        raise HTTPException(status_code=403,detail='Branch not allowed')
    # Values are parameters; authorization is separate from SQL injection protection.
    return query("""
      SELECT visit_id,branch_id,status,scheduled_start FROM visits
      WHERE branch_id=? AND visit_id>? ORDER BY visit_id LIMIT ?
    """,(branch_id,after_id,limit))
```

## lab/tests/test_core.py

```python
from pathlib import Path
import sqlite3
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap import seed_connection
from course_lib import classify_visit,delay_minutes,kpi,read_csv,query
from etl import normalize,load_events
ROOT=Path(__file__).resolve().parents[1]

class CoreTests(unittest.TestCase):
    def test_boundary_10_is_on_time(self): self.assertEqual(classify_visit('completed',10),'on_time')
    def test_above_10_is_late(self): self.assertEqual(classify_visit('completed',10.1),'late')
    def test_missing_is_unknown(self): self.assertEqual(classify_visit('completed',None),'unknown')
    def test_cancelled_is_excluded(self): self.assertEqual(classify_visit('cancelled',None),'excluded')
    def test_planned_is_excluded(self): self.assertEqual(classify_visit('planned',None),'excluded')
    def test_invalid_status_raises(self):
        with self.assertRaises(ValueError): classify_visit('typo',0)
    def test_empty_rate_is_none(self): self.assertIsNone(kpi([])['late_rate'])
    def test_seed_kpi(self):
        self.assertEqual(kpi(read_csv('visits')),dict(total=24,completed=18,eligible=15,late=6,unknown=3,late_rate=.4))
    def test_timezone_equivalence(self):
        self.assertEqual(delay_minutes('2026-08-01T00:00:00+00:00','2026-08-01T09:15:00+09:00'),15)
    def test_naive_timezone_rejected(self):
        with self.assertRaises(ValueError): delay_minutes('2026-08-01T00:00:00','2026-08-01T00:01:00')
    def test_parameter_value_not_code(self):
        self.assertEqual(query('SELECT visit_id FROM visits WHERE status=?',("completed' OR 1=1 --",)),[])
    def test_fk_enforced(self):
        conn=sqlite3.connect(':memory:');seed_connection(conn)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO clients VALUES(99,999,'2026-08-01')")
        conn.close()
    def test_transaction_rolls_back(self):
        conn=sqlite3.connect(':memory:');seed_connection(conn)
        with self.assertRaises(RuntimeError):
            with conn:
                conn.execute('UPDATE invoices SET amount_cents=0')
                raise RuntimeError('simulated failure')
        self.assertEqual(conn.execute('SELECT SUM(amount_cents) FROM invoices').fetchone()[0],100000)
        conn.close()
    def test_normalize(self):
        row={'event_id':'e1','visit_id':'1','status':' COMPLETED ','updated_at':'2026-08-04T10:00:00+09:00'}
        self.assertEqual(normalize(row)['updated_at'],'2026-08-04T01:00:00+00:00')
    def test_etl_rerun(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.db'
            first=load_events(ROOT/'data'/'raw_events.csv',path)
            second=load_events(ROOT/'data'/'raw_events.csv',path)
            self.assertEqual(first,second)
            self.assertEqual(second,dict(valid_input=3,invalid_input=3,state_rows=2))
            with sqlite3.connect(path) as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM quarantine').fetchone()[0],3)
                self.assertEqual(conn.execute('SELECT event_id FROM event_state WHERE visit_id=101').fetchone()[0],'e3')

if __name__=='__main__': unittest.main()
```

## lab/tests/test_api.py

```python
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from api import app
client=TestClient(app)

def test_health(): assert client.get('/health').json()=={'status':'ok'}
def test_missing_auth(): assert client.get('/visits?branch_id=1').status_code==401
def test_other_branch():
    assert client.get('/visits?branch_id=2',headers={'X-Demo-Key':'demo-branch-a'}).status_code==403

def test_validation():
    assert client.get('/visits?branch_id=1&limit=101',headers={'X-Demo-Key':'demo-branch-a'}).status_code==422

def test_rows_and_pagination():
    headers={'X-Demo-Key':'demo-branch-a'}
    first=client.get('/visits?branch_id=1&limit=2',headers=headers)
    assert first.status_code==200
    assert [r['visit_id'] for r in first.json()]==[1,2]
    next_page=client.get('/visits?branch_id=1&limit=2&after_id=2',headers=headers)
    assert [r['visit_id'] for r in next_page.json()]==[3,9]
    assert all(r['branch_id']==1 for r in next_page.json())
```

## lab/tests/test_cross_validation.py

```python
"""Independent numeric checks and SQL/Python reconciliation on fixed synthetic data."""
from pathlib import Path
import pytest
from course_lib import kpi, read_csv, query
ROOT=Path(__file__).resolve().parents[1]

def sql_file(stem):
    return query((ROOT/'sql'/f'{stem}.sql').read_text(encoding='utf-8'))

@pytest.mark.parametrize('branch_id,counts,rate',[
    (1,(6,6,3,0),.5),(2,(9,6,3,3),.5),
    (3,(3,3,0,0),0.0),(4,(0,0,0,0),None),
])
def test_branch_metric_agrees_with_independent_expected(branch_id,counts,rate):
    s=next(r for r in sql_file('SQL_I10') if r['branch_id']==branch_id)
    p=kpi([r for r in read_csv('visits') if int(r['branch_id'])==branch_id])
    names=('completed','eligible','late','unknown')
    assert tuple(s[k] for k in names)==counts
    assert tuple(p[k] for k in names)==counts
    assert s['late_rate']==p['late_rate']==rate

def test_financial_control_totals():
    assert query('SELECT SUM(amount_cents) AS n FROM invoices')[0]['n']==100000
    assert query('SELECT SUM(amount_cents) AS n FROM payments')[0]['n']==57000
    assert query('SELECT SUM(i.amount_cents) AS n FROM invoices i LEFT JOIN payments p USING(invoice_id)')[0]['n']==135000

def test_clients_without_any_visit():
    rows=query('SELECT client_id FROM clients c WHERE NOT EXISTS (SELECT 1 FROM visits v WHERE v.client_id=c.client_id) ORDER BY client_id')
    assert [r['client_id'] for r in rows]==[9,10,11,12]

def test_quality_gate_expected_warning():
    assert {r['check_name']:r['violation_count'] for r in sql_file('SQL_A10')}=={
        'duplicate_visit_key':0,'orphan_payment':0,
        'completed_missing_start':3,'invoice_arithmetic_mismatch':0}

def test_latest_visit_per_client():
    rows=query('WITH x AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY scheduled_start DESC,visit_id DESC) AS rn FROM visits) SELECT visit_id FROM x WHERE rn=1 ORDER BY client_id')
    assert [r['visit_id'] for r in rows]==list(range(17,25))
```

## lab/verify.py

```python
"""Run the complete local teaching-lab verification. Does not run PostgreSQL."""
from pathlib import Path
import json,subprocess,sys
from run_sql_demo import execute_demo
ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'example_manifest.json'

def main() -> int:
    subprocess.run([sys.executable,'-m','pytest','tests','examples/PY_I09.py','-q'],cwd=ROOT,check=True)
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    executed=0;skipped=[]
    for item in manifest:
        if item['mode']=='postgres':
            skipped.append(item['id']);continue
        if item['mode']=='pytest':
            continue  # counted in the test command above
        if item['mode']=='python':
            p=subprocess.run([sys.executable,'-m','examples.'+item['stem']],cwd=ROOT,text=True,capture_output=True,timeout=30)
            if p.returncode:
                print(p.stdout,p.stderr,file=sys.stderr);return p.returncode
        else:
            execute_demo((ROOT/'sql'/(item['stem']+'.sql')).read_text(encoding='utf-8'))
        executed+=1
    print(f'Executed {executed} standalone examples; the pytest lesson is included in the test suite.')
    print('PostgreSQL not executed: '+', '.join(skipped))
    print('Execution success does not prove production readiness or replace PostgreSQL testing.')
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as err:
        print(str(err),file=sys.stderr);raise SystemExit(1)
```

## lab/compose.yaml

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: course
      POSTGRES_PASSWORD: local-training-only
      POSTGRES_DB: carelink
    ports:
      - "127.0.0.1:55432:5432"
    volumes:
      - course_pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U course -d carelink"]
      interval: 5s
      timeout: 3s
      retries: 20
volumes:
  course_pg_data:
```

## lab/requirements-tested.txt

```text
# Versions in the build/validation environment; not a claim of latest releases.
pandas==2.2.3
pytest==9.0.2
fastapi==0.128.2
pydantic==2.13.4
httpx==0.28.1
uvicorn==0.48.0
```
