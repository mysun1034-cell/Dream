"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import AuthGate from "../../AuthGate";

type Problem = { id: string; week: string; text: string };

// 보드의 SQL 트랙(1~4주차)과 같은 순서로 두었다. 정답은 여기 없다 — 직접 풀어야 하는 연습장이다.
const PROBLEMS: Problem[] = [
  { id: "p1", week: "1주", text: "visits 테이블에서 visit_id와 minutes만 조회하세요." },
  { id: "p2", week: "1주", text: "beneficiary_id가 'B02'인 방문 기록만 조회하세요." },
  { id: "p3", week: "1주", text: "minutes가 60 이상인 방문을 visit_date 순으로 정렬해서 조회하세요." },
  { id: "p4", week: "2주", text: "2026년 9월 중 minutes가 60 이상인 방문이 몇 건인지 세어보세요." },
  { id: "p5", week: "2주", text: "직원(staff_id)별 방문 횟수를 구하세요." },
  { id: "p6", week: "2주", text: "방문을 3회 이상 받은 수급자(beneficiary_id)를 구하세요." },
  { id: "p7", week: "3주", text: "visits에 staff 이름을 붙여서 조회하세요." },
  { id: "p8", week: "3주", text: "visits에 beneficiaries 이름과 등급을 붙여서 조회하세요." },
  { id: "p9", week: "4주", text: "minutes가 비어있는(NULL) 방문 기록을 찾으세요." },
  { id: "p10", week: "4주", text: "2026년 9월에 있었던 방문만 조회하세요." },
];

const SEED_SQL = `
create table staff (staff_id text primary key, name text not null);
create table beneficiaries (beneficiary_id text primary key, name text not null, grade text not null);
create table visits (
  visit_id int primary key,
  staff_id text references staff (staff_id),
  beneficiary_id text references beneficiaries (beneficiary_id),
  visit_date date not null,
  minutes int
);

insert into staff (staff_id, name) values
  ('S01', '김민지'), ('S02', '박서준'), ('S03', '이하늘');

insert into beneficiaries (beneficiary_id, name, grade) values
  ('B01', '최여사님', '3등급'), ('B02', '정어르신', '2등급'),
  ('B03', '한할머니', '4등급'), ('B04', '오할아버지', '3등급');

insert into visits (visit_id, staff_id, beneficiary_id, visit_date, minutes) values
  (1, 'S01', 'B01', '2026-08-20', 45),
  (2, 'S01', 'B02', '2026-09-02', 60),
  (3, 'S01', 'B02', '2026-09-09', 75),
  (4, 'S02', 'B01', '2026-09-03', 50),
  (5, 'S02', 'B03', '2026-09-05', 90),
  (6, 'S02', 'B03', '2026-09-12', 60),
  (7, 'S03', 'B04', '2026-09-01', 40),
  (8, 'S03', 'B04', '2026-09-08', 65),
  (9, 'S03', 'B02', '2026-09-15', 55),
  (10, 'S01', 'B03', '2026-09-16', 60),
  (11, 'S02', 'B02', '2026-09-20', 80),
  (12, 'S01', 'B04', '2026-09-22', 45),
  (14, 'S02', 'B04', '2026-08-28', 60),
  (15, 'S01', 'B02', '2026-07-30', 60),
  (16, 'S03', 'B03', '2026-09-29', null);
`;

type Row = Record<string, unknown>;
type PgliteDb = {
  query: (sql: string) => Promise<{ rows: Row[]; affectedRows?: number }>;
  exec: (sql: string) => Promise<unknown>;
};

// pglite는 date 열을 JS Date 객체로 돌려준다 — 그대로 String()하면 "Thu Aug 20 2026 09:00:00 GMT+0900…"처럼
// 나온다. 화면에는 날짜만 짧게 보여준다.
function cell(value: unknown): string {
  if (value === null || value === undefined) return "NULL";
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  return String(value);
}

function SqlPractice() {
  const dbRef = useRef<PgliteDb | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [query, setQuery] = useState("select * from visits\norder by visit_id;\n");
  const [rows, setRows] = useState<Row[] | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  async function boot() {
    setStatus("loading");
    setMessage(null);
    try {
      const { PGlite } = await import("@electric-sql/pglite");
      const db = new PGlite() as unknown as PgliteDb;
      await db.exec(SEED_SQL);
      dbRef.current = db;
      setStatus("ready");
    } catch (e) {
      setStatus("error");
      setMessage(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    void boot();
  }, []);

  async function run() {
    if (!dbRef.current) return;
    setRunning(true);
    setMessage(null);
    try {
      const result = await dbRef.current.query(query);
      setRows(result.rows);
      if (!result.rows.length) setMessage("실행됐습니다. 반환된 행이 없습니다.");
    } catch (e) {
      setRows(null);
      setMessage(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  const columns = rows && rows.length ? Object.keys(rows[0]) : [];

  return (
    <div className="wrap narrow">
      <header className="top">
        <div>
          <p className="eyebrow">
            <Link href="/study">공부방</Link>
          </p>
          <h1>SQL 연습장</h1>
          <p className="goal">
            브라우저 안에서 돌아가는 실제 Postgres입니다. 연습을 위해 단순화한 스키마이고, 실제 EdenCare DB와는
            다릅니다.
          </p>
        </div>
      </header>

      <section className="card">
        <div className="card-head">
          <h2>문제</h2>
          <span className="muted">AI 없이 직접 풀어보세요</span>
        </div>
        <ul className="problem-list">
          {PROBLEMS.map((p) => (
            <li key={p.id} className="problem-item">
              <span className="pi-week">{p.week}</span>
              <span className="pi-title">{p.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <div className="card-head">
          <h2>표 구조</h2>
        </div>
        <div className="md-scroll">
          <table className="result-table">
            <thead>
              <tr>
                <th>테이블</th>
                <th>열</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>staff</td>
                <td>staff_id, name</td>
              </tr>
              <tr>
                <td>beneficiaries</td>
                <td>beneficiary_id, name, grade</td>
              </tr>
              <tr>
                <td>visits</td>
                <td>visit_id, staff_id, beneficiary_id, visit_date, minutes</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="card practice">
        <div className="card-head">
          <h2>쿼리 실행</h2>
          <span className="practice-status">
            {status === "loading" ? "데이터베이스 준비 중…" : status === "error" ? "준비하지 못했습니다" : "준비됨"}
          </span>
        </div>
        <textarea className="practice-editor" spellCheck={false} value={query} onChange={(e) => setQuery(e.target.value)} />
        <div className="practice-bar">
          <button type="button" onClick={run} disabled={status !== "ready" || running}>
            {running ? "실행 중…" : "실행"}
          </button>
          <button type="button" className="ghost" onClick={boot} disabled={status === "loading"}>
            데이터 다시 채우기
          </button>
        </div>
        {message && <p className="practice-output">{message}</p>}
        {rows && rows.length > 0 && (
          <div className="result-table-wrap">
            <table className="result-table">
              <thead>
                <tr>
                  {columns.map((c) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i}>
                    {columns.map((c) => (
                      <td key={c}>{cell(r[c])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default function SqlPracticePage() {
  return <AuthGate>{() => <SqlPractice />}</AuthGate>;
}
