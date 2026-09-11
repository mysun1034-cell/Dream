"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import type { Session, SupabaseClient } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/supabase";
import {
  addDays,
  dayKey,
  today,
  type Checkpoint,
  type CheckpointStatus,
  type DailyLog,
  type Plan,
  type Question,
  type Task,
  type Track,
} from "@/lib/plan";
import BoardView, { type DailyField } from "./BoardView";
import LoginForm from "./LoginForm";

type BoardData = {
  plan: Plan | null;
  tracks: Track[];
  tasks: Task[];
  checkpoints: Checkpoint[];
  daily: DailyLog[];
  questions: Question[];
};

type WriteResult = { error: { message: string } | null };

// 로그인이나 토큰 갱신 직후 잠깐 동안 Supabase가 새 토큰을 "JWT issued at future"로 거절한다.
// 서버끼리의 시계 차이 때문이라 기다리면 풀리므로, 이 오류일 때만 잠시 뒤 다시 시도한다.
const SKEW_RETRY_MS = 5000;
const SKEW_RETRY_LIMIT = 30;

function isClockSkew(message: string) {
  return /issued at future/i.test(message);
}

function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function Shell({ children }: { children: ReactNode }) {
  return <main className="wrap narrow">{children}</main>;
}

export default function BoardPage() {
  const [supabase, setSupabase] = useState<SupabaseClient | null | undefined>(undefined);
  const [session, setSession] = useState<Session | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [data, setData] = useState<BoardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [waiting, setWaiting] = useState(false);
  const userId = session?.user.id ?? null;
  const activeUser = useRef<string | null>(null);

  useEffect(() => {
    activeUser.current = userId;
  }, [userId]);

  useEffect(() => {
    const client = getSupabase();
    setSupabase(client);
    if (!client) return;
    // 구독하자마자 저장된 로그인 상태가 한 번 들어온다.
    const { data: listener } = client.auth.onAuthStateChange((_event, next) => {
      setSession(next);
      setAuthReady(true);
      if (!next) setData(null);
    });
    return () => listener.subscription.unsubscribe();
  }, []);

  const load = useCallback(async () => {
    if (!supabase || !userId) return;
    const since = dayKey(addDays(today(), -180));
    for (let attempt = 0; ; attempt += 1) {
      const [plan, tracks, tasks, checkpoints, daily, questions] = await Promise.all([
        supabase.from("plans").select("goal, start_date, manager_note, manager_note_at").maybeSingle(),
        supabase.from("tracks").select("id, sort, name, category, start_week, end_week, cadence").order("sort"),
        supabase
          .from("tasks")
          .select("id, week_key, seq, track_id, checkpoint_id, title, detail, done, done_at")
          .order("seq"),
        supabase
          .from("checkpoints")
          .select("id, sort, week, due_date, when_label, title, criteria, if_fail, status")
          .order("sort"),
        supabase.from("daily_logs").select("day, practice, english, review").gte("day", since),
        supabase.from("questions").select("id, sort, prompt, answer, answered_at").order("sort"),
      ]);
      if (activeUser.current !== userId) return;
      const failed = [plan, tracks, tasks, checkpoints, daily, questions].find((r) => r.error);
      if (failed?.error && isClockSkew(failed.error.message) && attempt < SKEW_RETRY_LIMIT) {
        setWaiting(true);
        await wait(SKEW_RETRY_MS);
        continue;
      }
      setWaiting(false);
      if (failed?.error) {
        setError(`불러오지 못했습니다: ${failed.error.message}`);
        return;
      }
      setError(null);
      setData({
        plan: (plan.data as Plan | null) ?? null,
        tracks: (tracks.data ?? []) as Track[],
        tasks: (tasks.data ?? []) as Task[],
        checkpoints: (checkpoints.data ?? []) as Checkpoint[],
        daily: (daily.data ?? []) as DailyLog[],
        questions: (questions.data ?? []) as Question[],
      });
      return;
    }
  }, [supabase, userId]);

  useEffect(() => {
    void load();
  }, [load]);

  const save = useCallback(
    async (send: () => PromiseLike<WriteResult>): Promise<boolean> => {
      for (let attempt = 0; ; attempt += 1) {
        const { error: failure } = await send();
        if (!failure) {
          setError(null);
          return true;
        }
        if (isClockSkew(failure.message) && attempt < SKEW_RETRY_LIMIT) {
          await wait(SKEW_RETRY_MS);
          continue;
        }
        setError(`저장하지 못했습니다: ${failure.message}`);
        await load();
        return false;
      }
    },
    [load],
  );

  if (supabase === undefined) {
    return (
      <Shell>
        <p className="muted">불러오는 중…</p>
      </Shell>
    );
  }

  if (supabase === null) {
    return (
      <Shell>
        <section className="card">
          <p className="eyebrow">학습 보드</p>
          <h1>아직 연결 전입니다</h1>
          <p>
            Supabase 주소와 키가 설정되지 않았습니다. <code>site/README.md</code>의 연결 순서를 따라 하면 보드가
            열립니다.
          </p>
        </section>
      </Shell>
    );
  }

  if (!authReady) {
    return (
      <Shell>
        <p className="muted">로그인 상태를 확인하는 중…</p>
      </Shell>
    );
  }

  if (!session) return <LoginForm supabase={supabase} />;

  const client = supabase;

  if (!data) {
    return (
      <Shell>
        {error ? (
          <p className="banner" role="alert">
            {error}
          </p>
        ) : (
          <p className="muted">{waiting ? "로그인을 확인하는 중입니다. 잠시만 기다려 주세요." : "계획을 불러오는 중…"}</p>
        )}
      </Shell>
    );
  }

  if (!data.plan) {
    return (
      <Shell>
        <section className="card">
          <p className="eyebrow">{session.user.email}</p>
          <h1>계획이 비어 있습니다</h1>
          <p>
            Supabase SQL Editor에서 <code>supabase/seed.local.sql</code>을 한 번 실행하면 12주 계획이 채워집니다.
          </p>
          <button type="button" className="ghost" onClick={() => void client.auth.signOut()}>
            로그아웃
          </button>
        </section>
      </Shell>
    );
  }

  const board = data;
  const plan = data.plan;
  const uid = session.user.id;

  function toggleTask(id: string, done: boolean) {
    const doneAt = done ? dayKey(today()) : null;
    setData((d) => d && { ...d, tasks: d.tasks.map((t) => (t.id === id ? { ...t, done, done_at: doneAt } : t)) });
    void save(() => client.from("tasks").update({ done, done_at: doneAt }).eq("id", id));
  }

  function toggleDaily(field: DailyField, value: boolean) {
    const day = dayKey(today());
    const next: DailyLog = {
      ...(board.daily.find((l) => l.day === day) ?? { day, practice: false, english: false, review: false }),
    };
    next[field] = value;
    setData((d) => d && { ...d, daily: [...d.daily.filter((l) => l.day !== day), next] });
    void save(() =>
      client.from("daily_logs").upsert({ user_id: uid, ...next, updated_at: new Date().toISOString() }),
    );
  }

  function setCheckpoint(id: string, status: CheckpointStatus) {
    setData((d) => d && { ...d, checkpoints: d.checkpoints.map((c) => (c.id === id ? { ...c, status } : c)) });
    void save(() => client.from("checkpoints").update({ status }).eq("id", id));
  }

  async function answer(id: string, text: string): Promise<boolean> {
    const value = text || null;
    const answeredAt = text ? dayKey(today()) : null;
    const ok = await save(() =>
      client.from("questions").update({ answer: value, answered_at: answeredAt }).eq("id", id),
    );
    if (ok) {
      setData(
        (d) =>
          d && {
            ...d,
            questions: d.questions.map((q) => (q.id === id ? { ...q, answer: value, answered_at: answeredAt } : q)),
          },
      );
    }
    return ok;
  }

  return (
    <BoardView
      plan={plan}
      tracks={board.tracks}
      tasks={board.tasks}
      checkpoints={board.checkpoints}
      daily={board.daily}
      questions={board.questions}
      email={session.user.email ?? null}
      error={error}
      onToggleTask={toggleTask}
      onToggleDaily={toggleDaily}
      onCheckpoint={setCheckpoint}
      onAnswer={answer}
      onSignOut={() => void client.auth.signOut()}
    />
  );
}
