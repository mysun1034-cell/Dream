// claude.ai 학습 보드에서 내보낸 JSON 폴더를 Supabase 시드 SQL로 바꾼다. 보드를 옮길 때 한 번 쓴다.
// 사용: node scripts/board-to-seed.mjs <내보내기 폴더> <로그인 이메일>
// 결과는 supabase/seed.local.sql 에 쓴다. 개인 데이터라 .gitignore 에 있다.
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const [exportDir, email] = process.argv.slice(2);
if (!exportDir || !email) {
  console.error("사용: node scripts/board-to-seed.mjs <내보내기 폴더> <로그인 이메일>");
  process.exit(1);
}
const output = join(dirname(fileURLToPath(import.meta.url)), "..", "supabase", "seed.local.sql");

function collection(name) {
  const dir = join(exportDir, name);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => ({ id: f.slice(0, -5), ...JSON.parse(readFileSync(join(dir, f), "utf8")) }));
}

const plan = collection("meta").find((d) => d.id === "plan");
if (!plan) throw new Error("meta/plan 문서가 없습니다");

const plans = [
  {
    goal: plan.goal,
    start_date: plan.startDate,
    manager_note: plan.managerNote || null,
    manager_note_at: plan.managerNoteAt || null,
  },
];

const tracks = collection("tracks")
  .sort((a, b) => a.order - b.order)
  .map((t) => ({
    id: t.id,
    sort: t.order,
    name: t.name,
    category: t.group,
    start_week: t.start,
    end_week: t.end,
    cadence: t.cadence || null,
  }));

const checkpoints = collection("checkpoints")
  .sort((a, b) => a.order - b.order)
  .map((c) => ({
    id: c.id,
    sort: c.order,
    week: c.week ?? null,
    due_date: c.date || null,
    when_label: c.when || null,
    title: c.title,
    criteria: c.criteria,
    if_fail: c.ifFail || null,
    status: c.status || "pending",
  }));

const tasks = collection("tasks")
  .sort((a, b) => a.seq - b.seq)
  .map((t) => ({
    id: t.id,
    week_key: t.weekKey,
    seq: t.seq,
    track_id: t.track,
    checkpoint_id: t.checkpoint || null,
    title: t.title,
    detail: t.detail || null,
    done: Boolean(t.done),
    done_at: t.doneAt || null,
  }));

const dailyLogs = collection("daily")
  .map((d) => ({
    day: d.id,
    practice: Boolean(d.sql),
    english: Boolean(d.english),
    review: Boolean(d.review),
    updated_at: d.updatedAt || null,
  }))
  .filter((d) => d.practice || d.english || d.review)
  .sort((a, b) => a.day.localeCompare(b.day));

const questions = collection("questions")
  .sort((a, b) => a.order - b.order)
  .map((q) => ({
    id: q.id,
    sort: q.order,
    prompt: q.text,
    answer: q.answer || null,
    answered_at: q.answeredAt || null,
  }));

function literal(value) {
  if (value === null || value === undefined) return "null";
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return `'${String(value).replace(/'/g, "''")}'`;
}

function insert(table, rows) {
  if (!rows.length) return `  -- ${table}: 옮길 행 없음\n`;
  const columns = Object.keys(rows[0]);
  const values = rows.map((row) => `    (me, ${columns.map((c) => literal(row[c])).join(", ")})`).join(",\n");
  return `  insert into public.${table} (user_id, ${columns.join(", ")}) values\n${values}\n  on conflict do nothing;\n`;
}

const sql = `-- 학습 보드 초기 데이터 — ${new Date().toISOString().slice(0, 10)} claude.ai 학습 보드에서 내보냄.
-- 개인 데이터라 커밋하지 않는다. schema.sql 실행과 계정 생성이 끝난 뒤 SQL Editor에서 실행한다.
-- 여러 번 실행해도 이미 있는 행은 건드리지 않는다.
do $seed$
declare
  me uuid;
begin
  select id into me from auth.users where email = ${literal(email)};
  if me is null then
    raise exception ${literal(`계정이 없습니다. Authentication > Users에서 ${email} 계정을 먼저 만드세요.`)};
  end if;

${[
  insert("plans", plans),
  insert("tracks", tracks),
  insert("checkpoints", checkpoints),
  insert("tasks", tasks),
  insert("daily_logs", dailyLogs),
  insert("questions", questions),
].join("\n")}end
$seed$;
`;

writeFileSync(output, sql, "utf8");
console.log(
  `seed.local.sql: 계획 1 · 트랙 ${tracks.length} · 체크포인트 ${checkpoints.length} · 할 일 ${tasks.length} · 하루 기록 ${dailyLogs.length} · 질문 ${questions.length}`,
);
