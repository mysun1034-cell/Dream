// Dream 저장소의 개념 설명 문서를 골라 공부방 시드 SQL로 만든다.
// 원문은 사이트 코드가 아니라 이 SQL을 통해 Supabase에만 들어간다 — 공개 레포에는 올라가지 않는다.
// 사용: node scripts/study-to-seed.mjs <로그인 이메일>
// 결과는 supabase/seed.study.local.sql 에 쓴다.
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const email = process.argv[2];
if (!email) {
  console.error("사용: node scripts/study-to-seed.mjs <로그인 이메일>");
  process.exit(1);
}

const siteRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const dreamRoot = join(siteRoot, "..");
const output = join(siteRoot, "supabase", "seed.study.local.sql");

// { category, sort, title, path } — path 는 Dream 레포 루트 기준.
const DOCS = [
  { category: "sql", sort: 1, title: "SQL · 데이터 모델링 트랙", path: "career/SQL_data_modeling_track.md" },
  { category: "sql", sort: 2, title: "sql/ 폴더 안내", path: "sql/README.md" },
  { category: "sql", sort: 3, title: "EdenCare ERD (초안)", path: "sql/models/edencare/erd.md" },

  { category: "python", sort: 1, title: "python/ 폴더 안내", path: "python/README.md" },

  { category: "cs", sort: 1, title: "cs/ 폴더 안내", path: "cs/README.md" },

  { category: "english", sort: 1, title: "english/ 폴더 안내", path: "english/README.md" },
  { category: "english", sort: 2, title: "30초 자기소개 피치", path: "english/speaking/pitch_30s.md" },
  { category: "english", sort: 3, title: "2026년 8월 단어장", path: "english/vocab/2026-08.md" },
  { category: "english", sort: 4, title: "영문 이력서 표현 메모", path: "english/writing/resume_en.md" },

  { category: "ml", sort: 1, title: "ml/ 폴더 안내", path: "ml/README.md" },
  { category: "ml", sort: 2, title: "개념 지도", path: "ml/notes/concept-map.md" },

  { category: "genai", sort: 1, title: "생성형 AI 과정 안내", path: "lms/README.md" },
  { category: "genai", sort: 2, title: "42수업 전체 지도", path: "lms/syllabus_map.md" },

  { category: "llm", sort: 1, title: "LLM API 실습 (Responses API)", path: "llm-api-playground/README.md" },
  { category: "llm", sort: 2, title: "RAG 데이터 엔지니어링", path: "llm/RAG/README.md" },
  { category: "llm", sort: 3, title: "로컬 sLM 추론 실습 보고서", path: "llm/c3-slm/REPORT.md" },
  { category: "llm", sort: 4, title: "vLLM 스터디", path: "llm/c5-slm/README.md" },

  { category: "career", sort: 1, title: "포지셔닝 프로필", path: "career/profile_chris.md" },
  { category: "career", sort: 2, title: "Spring Boot/AI (EDENING) 커리큘럼", path: "career/SpringBoot_SpringAI_EDENING_curriculum.md" },

  { category: "qa", sort: 1, title: "질문·답변 일지 안내", path: "qa/README.md" },
];

function literal(value) {
  if (value === null || value === undefined) return "null";
  return `'${String(value).replace(/'/g, "''")}'`;
}

const rows = [];
const missing = [];
for (const doc of DOCS) {
  const full = join(dreamRoot, doc.path);
  if (!existsSync(full)) {
    missing.push(doc.path);
    continue;
  }
  const body = readFileSync(full, "utf8");
  rows.push({ id: doc.path.replace(/[\\/]/g, "-").replace(/\.md$/, ""), ...doc, body });
}

if (missing.length) {
  console.log("찾지 못해 건너뜀:\n" + missing.map((p) => "  - " + p).join("\n"));
}

const values = rows
  .map(
    (r) =>
      `    (me, ${literal(r.id)}, ${literal(r.category)}, ${r.sort}, ${literal(r.title)}, ${literal(r.path)}, ${literal(r.body)})`,
  )
  .join(",\n");

const totalBytes = rows.reduce((n, r) => n + Buffer.byteLength(r.body, "utf8"), 0);

const sql = `-- 공부방 개념 문서 — Dream 저장소에서 가져옴 (원문은 커밋되지 않고 이 SQL로만 옮겨간다).
-- schema.sql 실행 뒤 SQL Editor에서 실행한다. 다시 실행하면 기존 문서는 최신 내용으로 갱신된다.
do $seed$
declare
  me uuid;
begin
  select id into me from auth.users where email = ${literal(email)};
  if me is null then
    raise exception ${literal(`계정이 없습니다. Authentication > Users에서 ${email} 계정을 먼저 만드세요.`)};
  end if;

  insert into public.study_docs (user_id, id, category, sort, title, source_path, body) values
${values}
  on conflict (user_id, id) do update set
    category = excluded.category,
    sort = excluded.sort,
    title = excluded.title,
    source_path = excluded.source_path,
    body = excluded.body,
    updated_at = now();
end
$seed$;
`;

writeFileSync(output, sql, "utf8");
console.log(
  `seed.study.local.sql: 문서 ${rows.length}개 · 본문 합계 ${(totalBytes / 1024).toFixed(1)}KB · SQL 파일 ${(Buffer.byteLength(sql, "utf8") / 1024).toFixed(1)}KB`,
);
