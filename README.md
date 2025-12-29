# PPG Manager

Aplicação Streamlit multi-PPG com autenticação Supabase (Auth + Postgres + Storage). Mantém PPGs isolados via RLS e utiliza apenas as credenciais públicas (anon key) no app.

## Pré-requisitos
- Conta no [Supabase](https://supabase.com/)
- Conta no [Streamlit Community Cloud](https://streamlit.io/cloud)
- Python 3.11+

## 1. Preparar o Supabase
1. Crie um novo projeto no Supabase.
2. No SQL Editor, execute o conteúdo de `db/ddl.sql` para criar/atualizar tabelas, funções e policies (rode novamente sempre que atualizar o repositório).
3. Em **Auth → Users → Add user**, crie um usuário (e-mail/senha) e marque **Confirm user**.
4. Crie um PPG e vincule o usuário como coordenador (seed inicial):
   ```sql
   WITH new_ppg AS (
     INSERT INTO public.ppgs (name, description) VALUES ('PPG Piloto','Teste') RETURNING id
   ),
   u AS (
     SELECT id AS user_id FROM auth.users WHERE email = 'coordenador@exemplo.br' LIMIT 1
   )
   INSERT INTO public.memberships (user_id, ppg_id, role)
   SELECT u.user_id, p.id, 'coordenador' FROM u, new_ppg p;
   ```
5. Para adicionar orientador/mestrando no mesmo PPG, insira novas linhas em `memberships` com o mesmo `ppg_id` e o `user_id` de cada usuário:
   ```sql
   INSERT INTO public.memberships (user_id, ppg_id, role)
   VALUES
     ('<uuid-orientador>', '<uuid-ppg>', 'orientador'),
     ('<uuid-mestrando>', '<uuid-ppg>', 'mestrando');
   ```

## 2. Configurar secrets no Streamlit
No repositório, o app busca as credenciais primeiro em variáveis de ambiente e depois em `st.secrets`:
```toml
SUPABASE_URL = "https://<project>.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```
No Streamlit Community Cloud, abra **Edit secrets** e cole as chaves acima.

> Use a chave "anon public" do Supabase (JWT iniciado por `eyJ`). **Não** use `service_role` nem chaves `sb_publishable_...`.

## 3. Rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Defina `SUPABASE_URL` e `SUPABASE_ANON_KEY` no ambiente ou em `.streamlit/secrets.toml` (não faça commit do arquivo).

## 4. Deploy no Streamlit Community Cloud
1. Publique o repositório no GitHub.
2. Crie um app em **New app**, apontando para `app.py` na branch desejada.
3. Adicione os *secrets* conforme a seção anterior.
4. Abra o app, faça login com o usuário criado e confirme que `ppg_id` e `role` aparecem no topo.

## 5. Fluxo do app
- Login: formulário de e-mail/senha. Sem sessão, o restante do app fica bloqueado.
- Após login, os vínculos em `memberships` são carregados e o primeiro `ppg_id` encontrado é aplicado em `st.session_state['ppg_id']` e `['role']`. É possível alternar o PPG pela barra lateral.
- Botão **Sair** encerra a sessão.
- RBAC simples via `rbac.can(action)`:
  - coordenador: ver/criar/editar/apagar/admin
- orientador: ver/criar/editar
- mestrando: ver/criar/editar (limitado aos próprios registros via RLS)

### Páginas
- **Admin do PPG (coordenador)**: CRUD de `research_lines` e `swot_items` filtrados por `ppg_id`.
- **Projetos**: lista por PPG, criação/edição pelo coordenador/orientador, vínculos de orientadores/mestrandos e visualização das produções associadas (Dissertações/Artigos/PTTs). O vínculo "Projeto pai" é opcional.
- **Artigos**, **Dissertações** e **PTTs**: criação/edição com seleção opcional de projeto do mesmo PPG para permitir a exibição em "Associados" na aba Projetos. Orientador/mestrando são listados via memberships/profiles do PPG.
- Demais páginas seguem protegidas por login e `ppg_id`.

## 6. Banco de dados e RLS
- Tabelas mínimas: `ppgs`, `memberships`, `profiles` (espelha `auth.users` para exibir nome/email), `research_lines`, `swot_items`, `projects` (colunas `name`, `description`, `parent_project_id`), `project_orientadores`, `project_mestrandos`, `articles`, `dissertations`, `ptts`.
- Enum de roles: `member_role_v2` com `coordenador`, `orientador`, `mestrando` (migrando `professor` -> `orientador`).
- Funções: `is_member(ppg uuid)`, `is_coordinator(ppg uuid)`, `user_role(ppg uuid)` e helpers de projeto.
- Policies principais:
  - `ppg_select`: `ppgs` somente para membros.
  - `memberships`: select do próprio usuário ou de quem pertence ao mesmo PPG (para montar listas de vínculo) e seed manual.
  - `profiles`: select permitido para quem compartilha um PPG via memberships.
  - `projects`: select para membros; insert/update para coordenador ou orientador; delete apenas coordenador.
  - `project_orientadores`/`project_mestrandos`: select para membros do PPG do projeto; insert/delete para coordenador/orientador.
  - `articles`/`dissertations`/`ptts`: select/insert/update para membros dentro do PPG.

## 7. Checklist de testes
- Login com usuário do Supabase (email/senha).
- Confirmar `ppg_id`/`role` no topo e na barra lateral.
- Na página **Admin do PPG**, criar/editar/excluir linhas de pesquisa e SWOT (somente coordenador).
- Na página **Projetos**:
  - Coordenador cria projeto e vincula orientadores/mestrandos.
  - Orientador visualiza e edita vínculos do projeto do PPG.
  - Mestrando visualiza lista e seção de associados.
- Na página **Artigos/Dissertações/PTTs**, criar/editar vinculando `project_id` do mesmo PPG e validar que aparecem em "Associados" na aba Projetos.
