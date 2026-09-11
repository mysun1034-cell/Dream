"use client";

import { useState, type FormEvent } from "react";
import type { SupabaseClient } from "@supabase/supabase-js";

// Supabase가 돌려주는 영어 오류를 원인이 드러나는 한국어 문장으로 바꾼다.
function explain(message: string) {
  if (/invalid login credentials/i.test(message)) return "이메일 또는 비밀번호가 맞지 않습니다.";
  if (/email not confirmed/i.test(message)) return "이메일 인증이 끝나지 않은 계정입니다.";
  if (/invalid api key|no api key/i.test(message)) {
    return "사이트에 넣은 Supabase 키가 잘못됐습니다. Vercel 환경 변수를 확인해 주세요.";
  }
  if (/failed to fetch|network/i.test(message)) return "서버에 연결하지 못했습니다. 인터넷 연결을 확인해 주세요.";
  return `로그인하지 못했습니다: ${message}`;
}

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
    if (error) setMessage(explain(error.message));
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
