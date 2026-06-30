-- ════════════════════════════════════════════════════════════════════════════
-- Arvind JD Generator — Full production schema (v2)
-- Run in Supabase SQL Editor: Dashboard → SQL Editor → New query
-- This extends the v1 schema (role_taxonomy + sample_jds) — safe to re-run.
-- ════════════════════════════════════════════════════════════════════════════

-- ── Existing tables (kept as-is) ─────────────────────────────────────────────
create table if not exists role_taxonomy (
  id               uuid primary key default gen_random_uuid(),
  department       text not null,
  division         text not null,
  role_family      text not null,
  yoe_band         text not null,
  seniority_label  text,
  created_at       timestamptz default now(),
  unique (department, role_family, yoe_band)
);

create table if not exists sample_jds (
  id            uuid primary key default gen_random_uuid(),
  taxonomy_id   uuid references role_taxonomy(id) on delete cascade,
  jd_text       text not null,
  metadata      jsonb default '{}'::jsonb,
  added_by      text,
  created_at    timestamptz default now()
);

create index if not exists idx_sample_jds_taxonomy_id on sample_jds(taxonomy_id);
create index if not exists idx_role_taxonomy_dept on role_taxonomy(department);

-- ── New: user_profiles ────────────────────────────────────────────────────────
-- One row per Supabase auth user; auto-created by trigger on auth.users insert.
create table if not exists user_profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  email       text unique not null,
  full_name   text,
  role        text not null default 'employee',   -- 'employee' | 'admin'
  avatar_url  text,
  jd_count    int not null default 0,
  last_active timestamptz,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

-- ── New: user_jds ─────────────────────────────────────────────────────────────
-- Every generated JD draft (and its approved final version) for every user.
create table if not exists user_jds (
  id              uuid primary key default gen_random_uuid(),
  generation_id   text unique not null,           -- client-side UUID from /api/jd/generate
  user_email      text not null,
  role_title      text not null,
  department      text not null,
  division        text,
  family          text not null,
  yoe_band        text not null,
  focus_areas     text,
  original_text   text not null,                  -- raw LLM output
  final_text      text,                           -- edited final (null until approved)
  status          text not null default 'draft',  -- 'draft' | 'approved' | 'archived'
  edit_ratio      float,
  jd_ref          text,                           -- short 8-char ref (e.g. "a1b2c3d4")
  approved_at     timestamptz,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

create index if not exists idx_user_jds_user_email on user_jds(user_email);
create index if not exists idx_user_jds_status on user_jds(status);
create index if not exists idx_user_jds_department on user_jds(department);
create index if not exists idx_user_jds_created_at on user_jds(created_at desc);

-- ── New: jd_feedback ─────────────────────────────────────────────────────────
create table if not exists jd_feedback (
  id               uuid primary key default gen_random_uuid(),
  jd_id            text not null,                 -- matches user_jds.jd_ref
  generation_id    text,
  user_email       text not null,
  department       text,
  family           text,
  yoe_band         text,
  role_title       text,
  overall_rating   int not null check (overall_rating between 1 and 5),
  section_ratings  jsonb default '{}'::jsonb,
  positive_tags    text[] default '{}',
  improvement_tags text[] default '{}',
  free_text        text,
  better_than_manual text default 'about_the_same',
  created_at       timestamptz default now()
);

create index if not exists idx_jd_feedback_jd_id on jd_feedback(jd_id);
create index if not exists idx_jd_feedback_dept on jd_feedback(department);

-- ── New: jd_edit_diffs ───────────────────────────────────────────────────────
create table if not exists jd_edit_diffs (
  id              uuid primary key default gen_random_uuid(),
  jd_id           text not null,
  generation_id   text,
  user_email      text not null,
  department      text,
  family          text,
  yoe_band        text,
  role_title      text,
  edit_ratio      float,
  char_added      int,
  char_removed    int,
  original_len    int,
  final_len       int,
  created_at      timestamptz default now()
);

-- ── New: kb_versions ─────────────────────────────────────────────────────────
create table if not exists kb_versions (
  id          uuid primary key default gen_random_uuid(),
  department  text not null,
  family      text not null,
  yoe_band    text not null,
  version     int not null default 1,
  updated_at  timestamptz default now(),
  unique (department, family, yoe_band)
);

-- ── New: share_tokens ────────────────────────────────────────────────────────
create table if not exists share_tokens (
  id          uuid primary key default gen_random_uuid(),
  token       text unique not null,
  jd_id       text not null,
  user_email  text not null,
  expires_at  timestamptz,
  created_at  timestamptz default now()
);

-- ── updated_at triggers ───────────────────────────────────────────────────────
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_user_profiles_updated_at on user_profiles;
create trigger trg_user_profiles_updated_at
  before update on user_profiles
  for each row execute function set_updated_at();

drop trigger if exists trg_user_jds_updated_at on user_jds;
create trigger trg_user_jds_updated_at
  before update on user_jds
  for each row execute function set_updated_at();

-- ── Auto-create user_profile on new Supabase auth signup ─────────────────────
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.user_profiles (id, email, full_name, avatar_url, role)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
    coalesce(new.raw_user_meta_data->>'avatar_url', ''),
    case when new.email = any(string_to_array(current_setting('app.admin_emails', true), ','))
         then 'admin' else 'employee' end
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- ── Row Level Security ────────────────────────────────────────────────────────
alter table role_taxonomy enable row level security;
alter table sample_jds enable row level security;
alter table user_profiles enable row level security;
alter table user_jds enable row level security;
alter table jd_feedback enable row level security;
alter table jd_edit_diffs enable row level security;
alter table kb_versions enable row level security;
alter table share_tokens enable row level security;

-- role_taxonomy + sample_jds: any authenticated user can read
drop policy if exists "Authenticated users can read role_taxonomy" on role_taxonomy;
create policy "Authenticated users can read role_taxonomy"
  on role_taxonomy for select using (auth.role() = 'authenticated');

drop policy if exists "Authenticated users can read sample_jds" on sample_jds;
create policy "Authenticated users can read sample_jds"
  on sample_jds for select using (auth.role() = 'authenticated');

-- user_profiles: users see their own row
drop policy if exists "Users can view own profile" on user_profiles;
create policy "Users can view own profile"
  on user_profiles for select using (auth.uid() = id);

-- user_jds: users see their own JDs
drop policy if exists "Users can view own jds" on user_jds;
create policy "Users can view own jds"
  on user_jds for select using (auth.jwt()->>'email' = user_email);

-- jd_feedback: users see their own
drop policy if exists "Users can view own feedback" on jd_feedback;
create policy "Users can view own feedback"
  on jd_feedback for select using (auth.jwt()->>'email' = user_email);

-- All writes go through the service_role key (bypasses RLS entirely).
-- No client-side insert/update policies are intentionally defined.
