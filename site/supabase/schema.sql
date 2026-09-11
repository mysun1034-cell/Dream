-- 학습 보드 스키마 — Supabase SQL Editor에서 한 번 실행한다.
-- 모든 행에 user_id를 두고 행 단위 보안(RLS)으로 본인 행만 읽고 쓰게 한다.
-- 지금은 본인 한 명만 쓰지만, 나중에 다른 사람이 가입해도 서로의 데이터가 섞이지 않는다.

-- 사용자마다 계획 한 개: 목표, 1주차 시작일, 매니저 메모
create table if not exists public.plans (
  user_id uuid primary key default auth.uid() references auth.users (id) on delete cascade,
  goal text not null,
  start_date date not null,
  manager_note text,
  manager_note_at date,
  updated_at timestamptz not null default now()
);

-- 학습 트랙: 무엇을 몇 주차부터 몇 주차까지 하는지
create table if not exists public.tracks (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  id text not null,
  sort int not null,
  name text not null,
  category text not null check (category in ('skill', 'interview', 'apply')),
  start_week int not null check (start_week between 1 and 52),
  end_week int not null,
  cadence text,
  primary key (user_id, id),
  check (end_week >= start_week)
);

-- 체크포인트: 다음 단계로 넘어가도 되는지 확인하는 시험
create table if not exists public.checkpoints (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  id text not null,
  sort int not null,
  week int check (week between 1 and 52),
  due_date date,
  when_label text,
  title text not null,
  criteria text not null,
  if_fail text,
  status text not null default 'pending' check (status in ('pending', 'passed', 'extended')),
  primary key (user_id, id)
);

-- 주차별 할 일
create table if not exists public.tasks (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  id text not null,
  week_key text not null check (week_key in ('1', '2', '3', '4', '5-6', '7-10', '11+')),
  seq int not null,
  track_id text not null,
  checkpoint_id text,
  title text not null,
  detail text,
  done boolean not null default false,
  done_at date,
  primary key (user_id, id),
  foreign key (user_id, track_id) references public.tracks (user_id, id) on delete cascade,
  foreign key (user_id, checkpoint_id) references public.checkpoints (user_id, id) on delete set null (checkpoint_id)
);

-- 하루 루틴 체크: practice = SQL·Python 연습
create table if not exists public.daily_logs (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  day date not null,
  practice boolean not null default false,
  english boolean not null default false,
  review boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, day)
);

-- 매니저 질문과 답
create table if not exists public.questions (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  id text not null,
  sort int not null,
  prompt text not null,
  answer text,
  answered_at date,
  primary key (user_id, id)
);

-- 행 단위 보안: 로그인한 사용자는 자기 user_id 행만 보고 고칠 수 있다.
alter table public.plans enable row level security;
alter table public.tracks enable row level security;
alter table public.checkpoints enable row level security;
alter table public.tasks enable row level security;
alter table public.daily_logs enable row level security;
alter table public.questions enable row level security;

drop policy if exists "own rows" on public.plans;
create policy "own rows" on public.plans
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

drop policy if exists "own rows" on public.tracks;
create policy "own rows" on public.tracks
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

drop policy if exists "own rows" on public.checkpoints;
create policy "own rows" on public.checkpoints
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

drop policy if exists "own rows" on public.tasks;
create policy "own rows" on public.tasks
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

drop policy if exists "own rows" on public.daily_logs;
create policy "own rows" on public.daily_logs
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

drop policy if exists "own rows" on public.questions;
create policy "own rows" on public.questions
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

-- 공부방 자료: Dream 저장소의 개념 설명 문서를 옮겨 담는다.
-- 원문은 공개 레포에 올리지 않고(개인 학습 메모라서) 여기 DB에만 둔다.
create table if not exists public.study_docs (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  id text not null,
  category text not null,
  sort int not null,
  title text not null,
  source_path text,
  body text not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, id)
);

alter table public.study_docs enable row level security;

drop policy if exists "own rows" on public.study_docs;
create policy "own rows" on public.study_docs
  for all to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

grant select, insert, update, delete
  on public.plans, public.tracks, public.checkpoints, public.tasks, public.daily_logs, public.questions, public.study_docs
  to authenticated;
