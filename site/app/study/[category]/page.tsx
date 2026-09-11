"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { SupabaseClient } from "@supabase/supabase-js";
import AuthGate from "../AuthGate";
import { categoryOf, type StudyDoc } from "@/lib/study";
import { renderMarkdown } from "@/lib/markdown";

function CategoryView({ supabase, slug }: { supabase: SupabaseClient; slug: string }) {
  const [docs, setDocs] = useState<StudyDoc[] | null>(null);
  const category = categoryOf(slug);

  useEffect(() => {
    let alive = true;
    supabase
      .from("study_docs")
      .select("id, category, sort, title, source_path, body")
      .eq("category", slug)
      .order("sort")
      .then(({ data }) => {
        if (alive) setDocs((data ?? []) as StudyDoc[]);
      });
    return () => {
      alive = false;
    };
  }, [supabase, slug]);

  return (
    <div className="wrap">
      <header className="top">
        <div>
          <p className="eyebrow">
            <Link href="/study">공부방</Link>
          </p>
          <h1>{category?.name ?? slug}</h1>
          {category && <p className="goal">{category.blurb}</p>}
        </div>
      </header>

      {docs === null && <p className="muted">불러오는 중…</p>}
      {docs && docs.length === 0 && (
        <section className="card">
          <p>이 분류에는 아직 옮겨둔 문서가 없습니다.</p>
        </section>
      )}
      {docs?.map((doc) => (
        <section key={doc.id} className="card">
          <div className="card-head">
            <h2>{doc.title}</h2>
            {doc.source_path && <span className="muted">Dream/{doc.source_path}</span>}
          </div>
          <div className="md-scroll">
            <div className="md-body" dangerouslySetInnerHTML={{ __html: renderMarkdown(doc.body) }} />
          </div>
        </section>
      ))}
    </div>
  );
}

export default function CategoryPage() {
  const params = useParams<{ category: string }>();
  return <AuthGate>{({ supabase }) => <CategoryView supabase={supabase} slug={params.category} />}</AuthGate>;
}
