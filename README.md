# PPG Manager

Aplicativo Streamlit para gestão de programas de pós-graduação (PPG) com backend Supabase. O objetivo é concentrar indicadores, fluxos administrativos e ferramentas de avaliação em um único painel, respeitando permissões por papel.

## Requisitos

- Python 3.11+
- Conta Supabase (projeto com banco PostgreSQL)
- Docker (opcional)

## Modo Demonstração (sem Supabase)

Use o modo demo para apresentar o app sem depender de credenciais externas. Os dados são simulados, ficam apenas na sessão atual e
podem ser resetados a qualquer momento.

- Ative executando: `DEMO_MODE=true streamlit run app.py`
- No Streamlit Cloud, defina em **Secrets**:

```
DEMO_MODE = "true"
```

Limitações: os registros não persistem entre sessões/redeploys e o isolamento multi-tenant é apenas simulado.

## Configuração do Supabase

1. Crie um novo projeto Supabase e habilite as extensões `pgcrypto` e `uuid-ossp`.
2. Execute o DDL abaixo no SQL Editor do Supabase para criar tabelas, funções e políticas de RLS.

```sql
-- Extensões necessárias
create extension if not exists "pgcrypto";
create extension if not exists "uuid-ossp";

-- Tabelas básicas
create table if not exists public.ppgs (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.ppg_memberships (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    user_id uuid not null,
    role text not null check (role in ('coordenador', 'professor', 'mestrando')),
    created_at timestamptz not null default timezone('utc', now()),
    unique (ppg_id, user_id)
);

create table if not exists public.linhas_pesquisa (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    nome text not null,
    descricao text,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.swot (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    categoria text not null check (categoria in ('forcas', 'fraquezas', 'oportunidades', 'ameacas')),
    descricao text not null,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.objetivos (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    descricao text not null,
    ordem integer not null default 1,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.fichas (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    nome text not null,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.ficha_criterios (
    id uuid primary key default gen_random_uuid(),
    ficha_id uuid not null references public.fichas(id) on delete cascade,
    descricao text not null,
    peso numeric not null default 1,
    ordem integer not null default 1,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.projetos (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    titulo text not null,
    lider text,
    status text not null default 'Planejado',
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.dissertacoes (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    titulo text not null,
    autor text,
    orientador text,
    defesa_prevista date,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.artigos (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    titulo text not null,
    autores text,
    ano integer,
    status text not null default 'Em andamento',
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.ptts (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    tema text not null,
    responsavel text,
    status text not null default 'Rascunho',
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.avaliacoes (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    ficha_id uuid not null references public.fichas(id) on delete cascade,
    avaliador_id uuid not null,
    avaliavel text not null,
    total numeric not null default 0,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.avaliacao_notas (
    id uuid primary key default gen_random_uuid(),
    avaliacao_id uuid not null references public.avaliacoes(id) on delete cascade,
    criterio_id uuid not null references public.ficha_criterios(id) on delete cascade,
    nota numeric not null,
    created_at timestamptz not null default timezone('utc', now()),
    unique (avaliacao_id, criterio_id)
);

create table if not exists public.relatorios (
    id uuid primary key default gen_random_uuid(),
    ppg_id uuid not null references public.ppgs(id) on delete cascade,
    periodo text not null,
    resumo text,
    created_at timestamptz not null default timezone('utc', now())
);

-- Funções utilitárias para RLS
create or replace function public.is_member(target_ppg uuid)
returns boolean
language sql
stable
as $$
    select exists (
        select 1 from public.ppg_memberships m
        where m.ppg_id = target_ppg and m.user_id = auth.uid()
    );
$$;

create or replace function public.has_role(target_ppg uuid, allowed_roles text[])
returns boolean
language sql
stable
as $$
    select coalesce(
        (select role from public.ppg_memberships m
         where m.ppg_id = target_ppg and m.user_id = auth.uid()
         limit 1
        ) = any(allowed_roles),
        false
    );
$$;

-- Habilitar RLS
alter table public.ppg_memberships enable row level security;
alter table public.linhas_pesquisa enable row level security;
alter table public.swot enable row level security;
alter table public.objetivos enable row level security;
alter table public.fichas enable row level security;
alter table public.ficha_criterios enable row level security;
alter table public.projetos enable row level security;
alter table public.dissertacoes enable row level security;
alter table public.artigos enable row level security;
alter table public.ptts enable row level security;
alter table public.avaliacoes enable row level security;
alter table public.avaliacao_notas enable row level security;
alter table public.relatorios enable row level security;

-- Policies
create policy "Ler vínculos do próprio usuário" on public.ppg_memberships
for select
using (auth.uid() = user_id or has_role(ppg_id, array['coordenador']::text[]));

create policy "Coordenadores gerenciam vínculos" on public.ppg_memberships
for all
using (has_role(ppg_id, array['coordenador']::text[]))
with check (has_role(ppg_id, array['coordenador']::text[]));

create policy "Membros visualizam dados" on public.linhas_pesquisa
for select using (is_member(ppg_id));
create policy "Coordenadores editam linhas" on public.linhas_pesquisa
for all using (has_role(ppg_id, array['coordenador']::text[]))
with check (has_role(ppg_id, array['coordenador']::text[]));

create policy "Membros visualizam SWOT" on public.swot
for select using (is_member(ppg_id));
create policy "Coordenadores editam SWOT" on public.swot
for all using (has_role(ppg_id, array['coordenador']::text[]))
with check (has_role(ppg_id, array['coordenador']::text[]));

create policy "Membros visualizam objetivos" on public.objetivos
for select using (is_member(ppg_id));
create policy "Coordenadores editam objetivos" on public.objetivos
for all using (has_role(ppg_id, array['coordenador']::text[]))
with check (has_role(ppg_id, array['coordenador']::text[]));

create policy "Membros visualizam fichas" on public.fichas
for select using (is_member(ppg_id));
create policy "Coordenadores editam fichas" on public.fichas
for all using (has_role(ppg_id, array['coordenador']::text[]))
with check (has_role(ppg_id, array['coordenador']::text[]));

create policy "Membros visualizam critérios" on public.ficha_criterios
for select using (is_member((select ppg_id from public.fichas f where f.id = ficha_id)));
create policy "Coordenadores editam critérios" on public.ficha_criterios
for all using (has_role((select ppg_id from public.fichas f where f.id = ficha_id), array['coordenador']::text[]))
with check (has_role((select ppg_id from public.fichas f where f.id = ficha_id), array['coordenador']::text[]));

create policy "Membros visualizam projetos" on public.projetos
for select using (is_member(ppg_id));
create policy "Equipe gerencia projetos" on public.projetos
for all using (has_role(ppg_id, array['coordenador','professor']::text[]))
with check (has_role(ppg_id, array['coordenador','professor']::text[]));

create policy "Membros visualizam dissertações" on public.dissertacoes
for select using (is_member(ppg_id));
create policy "Equipe gerencia dissertações" on public.dissertacoes
for all using (has_role(ppg_id, array['coordenador','professor']::text[]))
with check (has_role(ppg_id, array['coordenador','professor']::text[]));

create policy "Membros visualizam artigos" on public.artigos
for select using (is_member(ppg_id));
create policy "Membros submetem artigos" on public.artigos
for insert with check (has_role(ppg_id, array['coordenador','professor','mestrando']::text[]));
create policy "Equipe atualiza artigos" on public.artigos
for update, delete using (has_role(ppg_id, array['coordenador','professor']::text[]))
with check (has_role(ppg_id, array['coordenador','professor']::text[]));

create policy "Membros visualizam PTTs" on public.ptts
for select using (is_member(ppg_id));
create policy "Membros submetem PTTs" on public.ptts
for insert with check (has_role(ppg_id, array['coordenador','professor','mestrando']::text[]));
create policy "Equipe atualiza PTTs" on public.ptts
for update, delete using (has_role(ppg_id, array['coordenador','professor']::text[]))
with check (has_role(ppg_id, array['coordenador','professor']::text[]));

create policy "Equipe visualiza avaliações" on public.avaliacoes
for select using (has_role(ppg_id, array['coordenador','professor']::text[]));
create policy "Equipe gerencia avaliações" on public.avaliacoes
for all using (has_role(ppg_id, array['coordenador','professor']::text[]))
with check (has_role(ppg_id, array['coordenador','professor']::text[]));

create policy "Equipe visualiza notas" on public.avaliacao_notas
for select using (
    exists (
        select 1
        from public.avaliacoes a
        where a.id = avaliacao_id
          and has_role(a.ppg_id, array['coordenador','professor']::text[])
    )
);
create policy "Equipe gerencia notas" on public.avaliacao_notas
for all using (
    exists (
        select 1
        from public.avaliacoes a
        where a.id = avaliacao_id
          and has_role(a.ppg_id, array['coordenador','professor']::text[])
    )
)
with check (
    exists (
        select 1
        from public.avaliacoes a
        where a.id = avaliacao_id
          and has_role(a.ppg_id, array['coordenador','professor']::text[])
    )
);

create policy "Membros visualizam relatórios" on public.relatorios
for select using (is_member(ppg_id));
create policy "Coordenadores gerenciam relatórios" on public.relatorios
for all using (has_role(ppg_id, array['coordenador']::text[]))
with check (has_role(ppg_id, array['coordenador']::text[]));
```

3. Crie usuários no Supabase Authentication e associe-os às tabelas de `ppg_memberships` com a role adequada. Para permitir que coordenadores realizem esse cadastro diretamente no aplicativo, defina a variável `SUPABASE_SERVICE_ROLE_KEY` com a chave de service role (mantenha-a fora do repositório).

## Variáveis de ambiente

Configure as seguintes variáveis antes de executar o app (via `.env`, Docker Compose ou painel do serviço):

- `SUPABASE_URL`: URL do projeto Supabase (ex.: `https://xxxx.supabase.co`).
- `SUPABASE_ANON_KEY`: chave pública anônima do projeto.
- `SUPABASE_SERVICE_ROLE_KEY` (opcional): habilita o cadastro de novos usuários pelo coordenador dentro do app.

Opcionalmente, para desenvolvimento local, você pode definir esses valores em `.streamlit/secrets.toml`.

## Execução local (venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Execução com Docker

```bash
docker compose up --build
```

O aplicativo ficará disponível em `http://localhost:8501`.

## Estrutura do projeto

```
app.py
auth.py
rbac.py
data.py
components/
  forms.py
pages/
  01_Visão_Geral.py
  02_PPG_Admin.py
  03_Projetos.py
  04_Dissertações.py
  05_Artigos.py
  06_PTTs.py
  07_Avaliações.py
  08_Relatórios.py
```

## Papéis e permissões

- **Coordenador**: acesso total, incluindo administração do PPG, relatórios e (com `SUPABASE_SERVICE_ROLE_KEY`) cadastro de novos usuários vinculados ao programa.
- **Professor**: pode gerenciar projetos, dissertações, artigos, PTTs e avaliações.
- **Mestrando**: pode cadastrar artigos/PTTs e visualizar indicadores gerais.

As permissões são aplicadas no frontend via `rbac.py` e reforçadas pelas policies de RLS no Supabase.

## Roadmap

- Integração com uploads de arquivos e anexos.
- Dashboards analíticos com gráficos.
- Notificações por e-mail para atualizações de avaliações.
- Testes automatizados e linting específicos para Python.
