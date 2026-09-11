"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  TOTAL_WEEKS,
  WEEK_KEYS,
  addDays,
  currentWeek,
  dayKey,
  diffDays,
  keyForWeek,
  localDate,
  md,
  rangeLabel,
  streakDays,
  tabLabel,
  today,
  weekStart,
  type Checkpoint,
  type CheckpointStatus,
  type DailyLog,
  type Plan,
  type Question,
  type Task,
  type Track,
  type WeekKey,
} from "@/lib/plan";

export type DailyField = "practice" | "english" | "review";

type Props = {
  plan: Plan;
  tracks: Track[];
  tasks: Task[];
  checkpoints: Checkpoint[];
  daily: DailyLog[];
  questions: Question[];
  email: string | null;
  error: string | null;
  onToggleTask: (id: string, done: boolean) => void;
  onToggleDaily: (field: DailyField, value: boolean) => void;
  onCheckpoint: (id: string, status: CheckpointStatus) => void;
  onAnswer: (id: string, answer: string) => Promise<boolean>;
  onSignOut: () => void;
};

const ROUTINE: { field: DailyField; label: string; sub: string }[] = [
  { field: "practice", label: "SQL · Python 50분", sub: "푸는 동안 AI 금지 · 시간 재기" },
  { field: "english", label: "영어 10분", sub: "오늘 푼 과정을 영어로 설명하고 녹음" },
  { field: "review", label: "오답 다시 풀기 10분", sub: "3일 전에 틀린 문제" },
];

const LINKS = [
  { href: "https://claude.ai/code/artifact/16ab9a41-5509-407e-a5bf-4c5b0b6d476c", label: "문제 분해 골든 답안" },
  { href: "https://sqlbolt.com", label: "SQLBolt" },
  { href: "https://school.programmers.co.kr", label: "프로그래머스" },
  { href: "https://wikidocs.net/book/1", label: "점프 투 파이썬" },
];

const STATUS_NAME: Record<CheckpointStatus, string> = { pending: "대기", passed: "통과", extended: "연장" };
const WEEKS = Array.from({ length: TOTAL_WEEKS }, (_, i) => i + 1);
const WEEKDAY = "일월화수목금토";
const TAB_STORE = "learningBoard.tab";

function clamp(n: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, n));
}

function dLabel(diff: number) {
  return diff >= 0 ? `D-${diff}` : `지남 ${-diff}일`;
}

function storedTab(fallback: WeekKey): WeekKey {
  try {
    const saved = window.localStorage.getItem(TAB_STORE);
    return WEEK_KEYS.find((k) => k === saved) ?? fallback;
  } catch {
    return fallback;
  }
}

export default function BoardView(props: Props) {
  const { plan, tracks, tasks, checkpoints, daily, questions, email, error } = props;
  const [, setTick] = useState(0);
  const start = localDate(plan.start_date);
  const now = today();
  const week = currentWeek(start);
  const currentKey = keyForWeek(week);
  const [tab, setTab] = useState<WeekKey>(() => storedTab(currentKey));
  const trackMap = useMemo(() => new Map(tracks.map((t) => [t.id, t])), [tracks]);

  useEffect(() => {
    // 자정이 지나면 오늘 할 일과 주차 표시가 바뀌도록 5분마다 다시 그린다.
    const timer = window.setInterval(() => setTick((n) => n + 1), 300_000);
    return () => window.clearInterval(timer);
  }, []);

  function chooseTab(key: WeekKey) {
    setTab(key);
    try {
      window.localStorage.setItem(TAB_STORE, key);
    } catch {
      // 저장하지 못해도 탭은 바뀐다.
    }
  }

  const todayLog = daily.find((l) => l.day === dayKey(now));
  const doneCount = tasks.filter((t) => t.done).length;
  const weekTasks = tasks.filter((t) => t.week_key === currentKey);
  const weekDone = weekTasks.filter((t) => t.done).length;
  const nextCp = checkpoints.find((c) => c.status !== "passed");
  const tabTasks = tasks.filter((t) => t.week_key === tab);

  const nowLabel =
    week < 1
      ? `시작까지 D-${diffDays(start, now)}`
      : `${week}주차 · ${md(weekStart(start, week))} – ${md(addDays(weekStart(start, week), 6))}`;

  const nextCpValue = nextCp
    ? nextCp.due_date
      ? dLabel(diffDays(localDate(nextCp.due_date), now))
      : "예정"
    : checkpoints.length
      ? "모두 통과"
      : "—";

  return (
    <div className="wrap">
      <header className="top">
        <div>
          <p className="eyebrow">{email ?? "학습 매니저 보드"}</p>
          <h1>학습 보드</h1>
          <p className="goal">{plan.goal}</p>
        </div>
        <div className="top-side">
          <span className="now-pill">{nowLabel}</span>
          <Link className="ghost as-button" href="/study">
            공부방
          </Link>
          <button type="button" className="ghost" onClick={props.onSignOut}>
            로그아웃
          </button>
        </div>
      </header>

      {error && (
        <p className="banner" role="alert">
          {error}
        </p>
      )}

      <section className="stats" aria-label="진행 요약">
        <div className="stat">
          <span className="k">전체 진행</span>
          <span className="v">{tasks.length ? `${doneCount} / ${tasks.length}` : "—"}</span>
          <div className="meter">
            <i style={{ width: tasks.length ? `${Math.round((doneCount / tasks.length) * 100)}%` : 0 }} />
          </div>
        </div>
        <div className="stat">
          <span className="k">이번 주 할 일</span>
          <span className="v">{weekTasks.length ? `${weekDone} / ${weekTasks.length}` : "—"}</span>
          <span className="sub">
            {tabLabel(currentKey)} · {rangeLabel(start, currentKey)}
          </span>
        </div>
        <div className="stat">
          <span className="k">연속 학습일</span>
          <span className="v">{streakDays(daily)}일</span>
          <span className="sub">오늘 할 일의 SQL·Python 체크 기준</span>
        </div>
        <div className="stat">
          <span className="k">다음 체크포인트</span>
          <span className="v">{nextCpValue}</span>
          <span className="sub">
            {nextCp ? `${nextCp.title}${nextCp.when_label ? ` · ${nextCp.when_label}` : ""}` : ""}
          </span>
        </div>
      </section>

      {plan.manager_note && (
        <section className="note" aria-label="매니저 메모">
          <span className="tag">매니저</span>
          <p>{plan.manager_note}</p>
          {plan.manager_note_at && <span className="note-date">{plan.manager_note_at}</span>}
        </section>
      )}

      <div className="grid2">
        <section className="card" aria-labelledby="today-h">
          <div className="card-head">
            <h2 id="today-h">오늘 할 일</h2>
            <span className="muted">
              {md(now)} ({WEEKDAY.charAt(now.getDay())})
            </span>
          </div>
          <ul className="routine">
            {ROUTINE.map((r) => {
              const on = Boolean(todayLog?.[r.field]);
              return (
                <li key={r.field} className={`r-item${on ? " is-done" : ""}`}>
                  <label>
                    <input type="checkbox" checked={on} onChange={(e) => props.onToggleDaily(r.field, e.target.checked)} />
                    <span className="r-body">
                      <span className="r-title">{r.label}</span>
                      <span className="r-sub">{r.sub}</span>
                    </span>
                  </label>
                </li>
              );
            })}
          </ul>
          <p className="hint">매일 세 가지를 체크합니다. 날짜가 바뀌면 새로 시작합니다.</p>
        </section>

        <section className="card" aria-labelledby="week-h">
          <div className="card-head">
            <h2 id="week-h">주차별 할 일</h2>
            <span className="muted">{rangeLabel(start, tab)}</span>
          </div>
          <div className="tabs" role="tablist" aria-label="주차">
            {WEEK_KEYS.map((k) => {
              const list = tasks.filter((t) => t.week_key === k);
              const done = list.filter((t) => t.done).length;
              const classes = [
                "tab",
                tab === k ? "on" : "",
                k === currentKey ? "cur" : "",
                list.length && done === list.length ? "full" : "",
              ]
                .filter(Boolean)
                .join(" ");
              return (
                <button key={k} type="button" role="tab" aria-selected={tab === k} className={classes} onClick={() => chooseTab(k)}>
                  {tabLabel(k)}
                  {list.length > 0 && (
                    <small>
                      {done}/{list.length}
                    </small>
                  )}
                </button>
              );
            })}
          </div>
          <ul className="tasks">
            {tabTasks.length === 0 && <li className="empty">이 주차에 등록된 할 일이 없습니다.</li>}
            {tabTasks.map((t: Task) => {
              const track = trackMap.get(t.track_id);
              return (
                <li key={t.id} className={`task${t.done ? " is-done" : ""}`}>
                  <label>
                    <input type="checkbox" checked={t.done} onChange={(e) => props.onToggleTask(t.id, e.target.checked)} />
                    <span className="t-body">
                      <span className="t-title">{t.title}</span>
                      {t.detail && <span className="t-detail">{t.detail}</span>}
                      <span className="t-meta">
                        <span className={`chip g-${track?.category ?? "skill"}`}>{track?.name ?? t.track_id}</span>
                        {t.checkpoint_id && <span className="chip chip-cp">체크포인트</span>}
                      </span>
                    </span>
                  </label>
                </li>
              );
            })}
          </ul>
        </section>
      </div>

      <section className="card" aria-labelledby="tl-h">
        <div className="card-head">
          <h2 id="tl-h">12주 타임라인</h2>
          <div className="legend">
            <span>
              <i className="dot g-skill" />
              실력
            </span>
            <span>
              <i className="dot g-interview" />
              면접 준비
            </span>
            <span>
              <i className="dot g-apply" />
              지원
            </span>
          </div>
        </div>
        <div className="tl-scroll">
          <div className="tl">
            <div className="tl-row">
              <div className="tl-label" style={{ gridColumn: 1, gridRow: 1 }} />
              {WEEKS.map((w) => (
                <div key={w} className={`tl-h${w === week ? " now" : ""}`} style={{ gridColumn: w + 1, gridRow: 1 }}>
                  <b>W{w}</b>
                  <span>{md(weekStart(start, w))}</span>
                </div>
              ))}
            </div>
            {tracks.map((t) => {
              const s = clamp(t.start_week, 1, TOTAL_WEEKS);
              const e = clamp(t.end_week, s, TOTAL_WEEKS);
              return (
                <div key={t.id} className="tl-row">
                  <div className="tl-label" style={{ gridColumn: 1, gridRow: 1 }}>
                    <i className={`dot g-${t.category}`} />
                    {t.name}
                  </div>
                  {WEEKS.map((w) => (
                    <span key={w} className={`tl-cell${w === week ? " now" : ""}`} style={{ gridColumn: w + 1, gridRow: 1 }} />
                  ))}
                  <span
                    className={`tl-bar g-${t.category}`}
                    style={{ gridColumn: `${s + 1} / ${e + 2}`, gridRow: 1 }}
                    title={t.cadence ?? ""}
                  >
                    {t.cadence}
                  </span>
                </div>
              );
            })}
            <div className="tl-row">
              <div className="tl-label" style={{ gridColumn: 1, gridRow: 1 }}>
                체크포인트
              </div>
              {WEEKS.map((w) => (
                <span key={w} className={`tl-cell${w === week ? " now" : ""}`} style={{ gridColumn: w + 1, gridRow: 1 }} />
              ))}
              {checkpoints.map((c, i) =>
                c.week && c.week >= 1 && c.week <= TOTAL_WEEKS ? (
                  <span
                    key={c.id}
                    className={`tl-mark s-${c.status}`}
                    style={{ gridColumn: c.week + 1, gridRow: 1 }}
                    title={c.title}
                  >
                    CP{i + 1}
                  </span>
                ) : null,
              )}
            </div>
          </div>
        </div>
      </section>

      <section aria-labelledby="cp-h">
        <h2 className="sec" id="cp-h">
          체크포인트
        </h2>
        <div className="cps">
          {checkpoints.map((c, i) => (
            <article key={c.id} className={`cp s-${c.status}`}>
              <div className="cp-top">
                <span className="cp-id">CP{i + 1}</span>
                <span className={`pill p-${c.status}`}>{STATUS_NAME[c.status]}</span>
              </div>
              <h3>{c.title}</h3>
              {c.when_label && <p className="cp-when">{c.when_label}</p>}
              <p className="cp-crit">{c.criteria}</p>
              {c.if_fail && <p className="cp-fail">못 넘으면: {c.if_fail}</p>}
              <div className="cp-actions">
                {c.status === "pending" ? (
                  <>
                    <button type="button" onClick={() => props.onCheckpoint(c.id, "passed")}>
                      통과
                    </button>
                    <button type="button" className="ghost" onClick={() => props.onCheckpoint(c.id, "extended")}>
                      연장
                    </button>
                  </>
                ) : (
                  <button type="button" className="ghost" onClick={() => props.onCheckpoint(c.id, "pending")}>
                    되돌리기
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="card" aria-labelledby="q-h">
        <div className="card-head">
          <h2 id="q-h">매니저 질문</h2>
          <span className="muted">답을 적어두면 다음 대화에서 반영합니다</span>
        </div>
        {questions.length === 0 && <p className="empty">지금은 질문이 없습니다.</p>}
        {questions.map((q, i) => (
          <QuestionItem key={q.id} question={q} index={i} onAnswer={props.onAnswer} />
        ))}
      </section>

      <div className="grid-even">
        <section className="card rules" aria-labelledby="rules-h">
          <div className="card-head">
            <h2 id="rules-h">연습 규칙</h2>
          </div>
          <ol>
            <li>푸는 동안 AI 금지 — Claude도 포함입니다. 막히면 힌트만 받습니다.</li>
            <li>문제마다 시간을 잽니다.</li>
            <li>틀린 문제는 3일 뒤에 다시 풉니다.</li>
            <li>푼 과정을 소리 내 설명합니다. 점점 영어로 바꿉니다.</li>
          </ol>
          <div className="links">
            {LINKS.map((l) => (
              <a key={l.href} href={l.href} target="_blank" rel="noopener noreferrer">
                {l.label}
              </a>
            ))}
          </div>
        </section>
        <section className="card" aria-labelledby="rhythm-h">
          <div className="card-head">
            <h2 id="rhythm-h">한 주의 리듬</h2>
          </div>
          <dl className="rhythm">
            <dt>평일</dt>
            <dd>매일 70분 — SQL·Python 50분, 영어 10분, 오답 10분</dd>
            <dt>주말</dt>
            <dd>2~3시간 — 문제 분해 1회(영어로 녹음 후 G1~G8 채점) + 이야기·영상 준비 또는 미니 프로젝트</dd>
            <dt>매니저</dt>
            <dd>대화를 시작하면 이 보드의 체크 상태와 답변을 읽고 다음 할 일을 조정합니다</dd>
          </dl>
        </section>
      </div>
    </div>
  );
}

function QuestionItem({
  question,
  index,
  onAnswer,
}: {
  question: Question;
  index: number;
  onAnswer: (id: string, answer: string) => Promise<boolean>;
}) {
  const [draft, setDraft] = useState(question.answer ?? "");
  const [saving, setSaving] = useState(false);
  const dirty = draft.trim() !== (question.answer ?? "");

  return (
    <div className="q">
      <label className="q-text" htmlFor={`qa-${question.id}`}>
        {index + 1}. {question.prompt}
      </label>
      <textarea
        id={`qa-${question.id}`}
        rows={2}
        value={draft}
        placeholder="여기에 답을 적어주세요"
        onChange={(e) => setDraft(e.target.value)}
      />
      <div className="q-foot">
        <span className="q-state">
          {dirty ? "저장 안 됨" : question.answered_at ? `저장됨 · ${question.answered_at}` : "아직 답하지 않음"}
        </span>
        <button
          type="button"
          disabled={!dirty || saving}
          onClick={async () => {
            setSaving(true);
            await onAnswer(question.id, draft.trim());
            setSaving(false);
          }}
        >
          {saving ? "저장 중…" : "저장"}
        </button>
      </div>
    </div>
  );
}
