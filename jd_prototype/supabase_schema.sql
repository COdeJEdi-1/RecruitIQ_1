-- ════════════════════════════════════════════════════════════════════════════
-- Arvind JD Generator — Sample JD Library database schema
-- Run this once in the Supabase SQL Editor (Dashboard → SQL Editor → New query)
-- ════════════════════════════════════════════════════════════════════════════

-- Role taxonomy: one row per unique (department, role_family, yoe_band)
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

-- Sample JDs: the actual JD text, linked to its taxonomy row
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

-- ── Row Level Security ───────────────────────────────────────────────────────
-- Any signed-in Arvind employee can read the library; only the backend
-- (using the service_role key, which bypasses RLS) can write.

alter table role_taxonomy enable row level security;
alter table sample_jds enable row level security;

create policy "Authenticated users can read role_taxonomy"
  on role_taxonomy for select
  using (auth.role() = 'authenticated');

create policy "Authenticated users can read sample_jds"
  on sample_jds for select
  using (auth.role() = 'authenticated');

-- No insert/update/delete policies are defined for the anon/authenticated
-- roles on purpose — all writes go through the backend's service_role key
-- (supabase_kb.py), which bypasses RLS entirely. This keeps the Sample JD
-- Library read-only from the client side, matching its "zero-LLM-cost,
-- curated content" design.
