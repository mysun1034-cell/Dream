"use client";

import { useEffect, useState, type ReactNode } from "react";
import type { Session, SupabaseClient } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/supabase";
import LoginForm from "../board/LoginForm";

type Props = {
  children: (ctx: { supabase: SupabaseClient; session: Session }) => ReactNode;
};

// /study 아래 모든 페이지가 공유하는 로그인 문. 보드와 같은 계정으로만 들어간다.
export default function AuthGate({ children }: Props) {
  const [supabase, setSupabase] = useState<SupabaseClient | null | undefined>(undefined);
  const [session, setSession] = useState<Session | null>(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    const client = getSupabase();
    setSupabase(client);
    if (!client) return;
    const { data: listener } = client.auth.onAuthStateChange((_event, next) => {
      setSession(next);
      setAuthReady(true);
    });
    return () => listener.subscription.unsubscribe();
  }, []);

  if (supabase === undefined) {
    return (
      <main className="wrap narrow">
        <p className="muted">불러오는 중…</p>
      </main>
    );
  }

  if (supabase === null) {
    return (
      <main className="wrap narrow">
        <section className="card">
          <p className="eyebrow">공부방</p>
          <h1>아직 연결 전입니다</h1>
          <p>
            Supabase 주소와 키가 설정되지 않았습니다. <code>site/README.md</code>의 연결 순서를 따라 하면 열립니다.
          </p>
        </section>
      </main>
    );
  }

  if (!authReady) {
    return (
      <main className="wrap narrow">
        <p className="muted">로그인 상태를 확인하는 중…</p>
      </main>
    );
  }

  if (!session) return <LoginForm supabase={supabase} />;

  return <>{children({ supabase, session })}</>;
}
