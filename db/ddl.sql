-- Schema for PPG Manager (Supabase)
-- Basic multi-tenant structure with RLS policies.

create extension if not exists "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Roles enum (v2) to support coordenador, orientador e mestrando.
-- If an older enum existed (e.g., member_role with value 'professor'), we
-- create the new type and migrate the column using a safe cast.
-- ---------------------------------------------------------------------------
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'member_role_v2') THEN
    CREATE TYPE public.member_role_v2 AS ENUM ('coordenador', 'orientador', 'mestrando');
  END IF;
END$$;

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
    role public.member_role_v2 not null,
    created_at timestamptz default now()
);

-- Normalize legacy roles if present
update public.memberships set role = 'orientador'::member_role_v2 where role::text = 'professor';

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

create table if not exists public.projects (
    id uuid primary key default uuid_generate_v4(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    title text not null,
    description text,
    start_date date,
    end_date date,
    status text,
    created_at timestamptz default now()
);

create table if not exists public.project_orientadores (
    project_id uuid not null references public.projects(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    created_at timestamptz default now(),
    primary key (project_id, user_id)
);

create table if not exists public.project_mestrandos (
    project_id uuid not null references public.projects(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    created_at timestamptz default now(),
    primary key (project_id, user_id)
);

create table if not exists public.articles (
    id uuid primary key default uuid_generate_v4(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    title text not null,
    authors text,
    year integer,
    status text,
    project_id uuid references public.projects(id),
    orientador_user_id uuid references auth.users(id),
    mestrando_user_id uuid references auth.users(id),
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

create or replace function public.user_role(target_ppg uuid)
returns public.member_role_v2
security definer
language sql
as $$
  select role from public.memberships
  where ppg_id = target_ppg and user_id = auth.uid()
  limit 1;
$$;

create or replace function public.is_project_member(target_project uuid)
returns boolean
security definer
language sql
as $$
  select exists (
    select 1
    from public.projects p
    where p.id = target_project and is_member(p.ppg_id)
  );
$$;

create or replace function public.is_project_orientador(target_project uuid)
returns boolean
security definer
language sql
as $$
  select exists (
    select 1
    from public.project_orientadores po
    join public.projects p on p.id = po.project_id
    where po.project_id = target_project and po.user_id = auth.uid() and is_member(p.ppg_id)
  );
$$;

create or replace function public.is_project_mestrando(target_project uuid)
returns boolean
security definer
language sql
as $$
  select exists (
    select 1
    from public.project_mestrandos pm
    join public.projects p on p.id = pm.project_id
    where pm.project_id = target_project and pm.user_id = auth.uid() and is_member(p.ppg_id)
  );
$$;

-- Enable RLS ---------------------------------------------------------------
alter table public.ppgs enable row level security;
alter table public.memberships enable row level security;
alter table public.research_lines enable row level security;
alter table public.swot_items enable row level security;
alter table public.projects enable row level security;
alter table public.project_orientadores enable row level security;
alter table public.project_mestrandos enable row level security;
alter table public.articles enable row level security;

-- Policies -----------------------------------------------------------------
create policy if not exists ppg_select on public.ppgs
for select using (is_member(id));

create policy if not exists memberships_select_self on public.memberships
for select using (auth.uid() = user_id);

create policy if not exists memberships_select_ppg on public.memberships
for select using (is_member(ppg_id));

create policy if not exists memberships_insert_self on public.memberships
for insert with check (auth.uid() = user_id);

create policy if not exists research_lines_select on public.research_lines
for select using (is_member(ppg_id));

create policy if not exists research_lines_write on public.research_lines
for insert with check (is_coordinator(ppg_id));

create policy if not exists research_lines_update on public.research_lines
for update using (is_coordinator(ppg_id));

create policy if not exists swot_items_select on public.swot_items
for select using (is_member(ppg_id));

create policy if not exists swot_items_write on public.swot_items
for insert with check (is_coordinator(ppg_id));

create policy if not exists swot_items_update on public.swot_items
for update using (is_coordinator(ppg_id));

create policy if not exists projects_select on public.projects
for select using (is_project_member(id));

create policy if not exists projects_insert on public.projects
for insert with check (
  is_member(ppg_id) and user_role(ppg_id) in ('coordenador','orientador','mestrando')
);

create policy if not exists projects_update on public.projects
for update using (
  is_coordinator(ppg_id)
  or is_project_orientador(id)
  or is_project_mestrando(id)
);

create policy if not exists projects_delete on public.projects
for delete using (is_coordinator(ppg_id));

create policy if not exists project_orientadores_select on public.project_orientadores
for select using (is_member(ppg_id));

create policy if not exists project_orientadores_insert on public.project_orientadores
for insert with check (
  is_member(ppg_id)
  and (
    user_role(ppg_id) = 'coordenador'
    or (user_role(ppg_id) = 'orientador' and auth.uid() = user_id)
  )
);

create policy if not exists project_orientadores_delete on public.project_orientadores
for delete using (
  is_member(ppg_id)
  and (
    user_role(ppg_id) = 'coordenador'
    or auth.uid() = user_id
  )
);

create policy if not exists project_mestrandos_select on public.project_mestrandos
for select using (
  exists (select 1 from public.projects p where p.id = project_id and is_member(p.ppg_id))
);

create policy if not exists project_mestrandos_insert on public.project_mestrandos
for insert with check (
  exists (select 1 from public.projects p where p.id = project_id and is_member(p.ppg_id))
  and (
    auth.uid() = user_id
    or exists (
      select 1 from public.projects p2
      where p2.id = project_id and user_role(p2.ppg_id) in ('coordenador','orientador')
    )
  )
);

create policy if not exists project_mestrandos_delete on public.project_mestrandos
for delete using (
  exists (select 1 from public.projects p where p.id = project_id and is_member(p.ppg_id))
  and (
    auth.uid() = user_id
    or exists (
      select 1 from public.projects p2
      where p2.id = project_id and user_role(p2.ppg_id) = 'coordenador'
    )
  )
);

create policy if not exists articles_select on public.articles
for select using (is_member(ppg_id));

create policy if not exists articles_write on public.articles
for insert with check (is_member(ppg_id));

create policy if not exists articles_update on public.articles
for update using (
  is_member(ppg_id)
);
