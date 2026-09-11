export type Category = "skill" | "interview" | "apply";
export type CheckpointStatus = "pending" | "passed" | "extended";

export const WEEK_KEYS = ["1", "2", "3", "4", "5-6", "7-10", "11+"] as const;
export type WeekKey = (typeof WEEK_KEYS)[number];
export const TOTAL_WEEKS = 12;

export type Plan = {
  goal: string;
  start_date: string;
  manager_note: string | null;
  manager_note_at: string | null;
};

export type Track = {
  id: string;
  sort: number;
  name: string;
  category: Category;
  start_week: number;
  end_week: number;
  cadence: string | null;
};

export type Task = {
  id: string;
  week_key: WeekKey;
  seq: number;
  track_id: string;
  checkpoint_id: string | null;
  title: string;
  detail: string | null;
  done: boolean;
  done_at: string | null;
};

export type Checkpoint = {
  id: string;
  sort: number;
  week: number | null;
  due_date: string | null;
  when_label: string | null;
  title: string;
  criteria: string;
  if_fail: string | null;
  status: CheckpointStatus;
};

export type DailyLog = {
  day: string;
  practice: boolean;
  english: boolean;
  review: boolean;
};

export type Question = {
  id: string;
  sort: number;
  prompt: string;
  answer: string | null;
  answered_at: string | null;
};

const KEY_RANGE: Record<WeekKey, [number, number]> = {
  "1": [1, 1],
  "2": [2, 2],
  "3": [3, 3],
  "4": [4, 4],
  "5-6": [5, 6],
  "7-10": [7, 10],
  "11+": [11, 12],
};

const DAY_MS = 86_400_000;

export function today(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

export function localDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function addDays(date: Date, days: number): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}

export function diffDays(a: Date, b: Date): number {
  return Math.round((a.getTime() - b.getTime()) / DAY_MS);
}

export function dayKey(date: Date): string {
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${m}-${d}`;
}

export function md(date: Date): string {
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

export function weekStart(start: Date, week: number): Date {
  return addDays(start, 7 * (week - 1));
}

export function currentWeek(start: Date): number {
  return Math.floor(diffDays(today(), start) / 7) + 1;
}

export function keyForWeek(week: number): WeekKey {
  if (week <= 1) return "1";
  if (week <= 4) return String(week) as WeekKey;
  if (week <= 6) return "5-6";
  if (week <= 10) return "7-10";
  return "11+";
}

export function tabLabel(key: WeekKey): string {
  if (key === "5-6") return "5~6주";
  if (key === "7-10") return "7~10주";
  if (key === "11+") return "11주~";
  return `${key}주`;
}

export function rangeLabel(start: Date, key: WeekKey): string {
  const [from, to] = KEY_RANGE[key];
  const first = weekStart(start, from);
  if (key === "11+") return `${md(first)} ~`;
  return `${md(first)} – ${md(addDays(weekStart(start, to), 6))}`;
}

export function streakDays(logs: DailyLog[]): number {
  const practiced = new Set(logs.filter((l) => l.practice).map((l) => l.day));
  let cursor = today();
  if (!practiced.has(dayKey(cursor))) cursor = addDays(cursor, -1);
  let count = 0;
  while (practiced.has(dayKey(cursor))) {
    count += 1;
    cursor = addDays(cursor, -1);
  }
  return count;
}
