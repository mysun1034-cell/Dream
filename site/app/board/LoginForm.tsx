"use client";

import { useState, type FormEvent } from "react";
import type { SupabaseClient } from "@supabase/supabase-js";

export default function LoginForm({ supabase }: { supabase: SupabaseClient }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage(null);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setBusy(false);
    if (error) setMessage("로그인하지 못했습니다. 이메일과 비밀번호를 확인해 주세요.");
  }

  return (
    <main className="wrap narrow">
      <section className="card">
        <p className="eyebrow">학습 보드</p>
        <h1>로그인</h1>
        <p className="muted">등록된 본인 계정으로만 들어갈 수 있습니다.</p>
        <form className="form" onSubmit={submit}>
          <label>
            이메일
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label>
            비밀번호
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {message && (
            <p className="banner" role="alert">
              {message}
            </p>
          )}
          <button type="submit" disabled={busy}>
            {busy ? "확인 중…" : "로그인"}
          </button>
        </form>
      </section>
    </main>
  );
}
