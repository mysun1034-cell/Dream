"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { SupabaseClient } from "@supabase/supabase-js";
import AuthGate from "./AuthGate";
import { CATEGORIES } from "@/lib/study";

const PRACTICE = [
  { href: "/study/practice/sql", tag: "SQL", name: "SQL 연습장", blurb: "브라우저 안 실제 Postgres에 바로 쿼리를 실행합니다." },
  { href: "/study/practice/python", tag: "Python", name: "Python 연습장", blurb: "브라우저 안에서 바로 Python 코드를 실행합니다." },
];

function Hub({ supabase }: { supabase: SupabaseClient }) {
  const [counts, setCounts] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    let alive = true;
    supabase
      .from("study_docs")
      .select("category")
      .then(({ data }) => {
        if (!alive) return;
        const next: Record<string, number> = {};
        for (const row of (data ?? []) as { category: string }[]) {
          next[row.category] = (next[row.category] ?? 0) + 1;
        }
        setCounts(next);
      });
    return () => {
      alive = false;
    };
  }, [supabase]);

  return (
    <div className="wrap">
      <header className="top">
        <div>
          <p className="eyebrow">한정욱</p>
          <h1>공부방</h1>
          <p className="goal">개념 설명과 연습장을 모아뒀습니다. 문제는 직접 풀어보세요.</p>
        </div>
        <Link className="ghost as-button" href="/board">
          학습 보드로
        </Link>
      </header>

      <section aria-labelledby="practice-h">
        <h2 className="sec" id="practice-h">
          연습장
        </h2>
        <div className="study-grid">
          {PRACTICE.map((p) => (
            <Link key={p.href} className="study-card" href={p.href}>
              <span className="sc-count">{p.tag}</span>
              <span className="sc-name">{p.name}</span>
              <span className="sc-blurb">{p.blurb}</span>
            </Link>
          ))}
        </div>
      </section>

      <section aria-labelledby="cat-h">
        <h2 className="sec" id="cat-h">
          개념 설명
        </h2>
        <div className="study-grid">
          {CATEGORIES.map((c) => (
            <Link key={c.slug} className="study-card" href={`/study/${c.slug}`}>
              <span className="sc-count">{counts ? `${counts[c.slug] ?? 0}개 문서` : "…"}</span>
              <span className="sc-name">{c.name}</span>
              <span className="sc-blurb">{c.blurb}</span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default function StudyPage() {
  return <AuthGate>{({ supabase }) => <Hub supabase={supabase} />}</AuthGate>;
}
