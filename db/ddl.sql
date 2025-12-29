-- Schema for PPG Manager (Supabase)
-- Basic multi-tenant structure with RLS policies.

create extension if not exists "uuid-ossp";

create table if not exists public.ppgs (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    description text,
    created_at timestamptz default now()
);

create table if not exists public.memberships (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null,
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    role text not null check (role in ('coordenador', 'professor', 'mestrando')),
    created_at timestamptz default now()
);

create table if not exists public.research_lines (
    id uuid primary key default uuid_generate_v4(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    name text not null,
    description text,
    created_at timestamptz default now()
);

create table if not exists public.swot_items (
    id uuid primary key default uuid_generate_v4(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    category text not null check (category in ('strength','weakness','opportunity','threat')),
    description text not null,
    created_at timestamptz default now()
);

create table if not exists public.articles (
    id uuid primary key default uuid_generate_v4(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    title text not null,
    authors text,
    year integer,
    status text,
    created_at timestamptz default now()
);

-- Helper functions for RLS --------------------------------------------------
create or replace function public.is_member(target_ppg uuid)
returns boolean
security definer
language sql
as $$
  select exists(
    select 1 from public.memberships m
    where m.ppg_id = target_ppg and m.user_id = auth.uid()
  );
$$;
create or replace function public.is_coordinator(target_ppg uuid)
returns boolean
security definer
language sql
as $$
  select exists(
    select 1 from public.memberships m
    where m.ppg_id = target_ppg and m.user_id = auth.uid() and m.role = 'coordenador'
  );
$$;

-- Enable RLS ---------------------------------------------------------------
alter table public.ppgs enable row level security;
alter table public.memberships enable row level security;
alter table public.research_lines enable row level security;
alter table public.swot_items enable row level security;
alter table public.articles enable row level security;

-- Policies -----------------------------------------------------------------
create policy ppg_select on public.ppgs
for select using (is_member(id));

create policy memberships_select_self on public.memberships
for select using (auth.uid() = user_id);

create policy memberships_insert_self on public.memberships
for insert with check (auth.uid() = user_id);

create policy research_lines_select on public.research_lines
for select using (is_member(ppg_id));

create policy research_lines_write on public.research_lines
for insert with check (is_coordinator(ppg_id));

create policy research_lines_update on public.research_lines
for update using (is_coordinator(ppg_id));

create policy swot_items_select on public.swot_items
for select using (is_member(ppg_id));

create policy swot_items_write on public.swot_items
for insert with check (is_coordinator(ppg_id));

create policy swot_items_update on public.swot_items
for update using (is_coordinator(ppg_id));

create policy articles_select on public.articles
for select using (is_member(ppg_id));

create policy articles_write on public.articles
for insert with check (is_member(ppg_id));

create policy articles_update on public.articles
for update using (is_member(ppg_id));
