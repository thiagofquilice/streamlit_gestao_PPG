# Resumo de Merge - CAPES 2025-2028

## 1) Diagnóstico da arquitetura atual

A base do repositório foi mantida: app Streamlit multipágina com `layout.py` para navegação, camada `data.py` como fachada e `demo_store.py`/`demo_seed.py` para modo demo em memória.

## 2) Comparação estrutural (base x versão atualizada)

### Arquivos coincidentes (potencial de conflito)

- `app.py`
- `data.py`
- `demo_seed.py`
- `demo_store.py`
- `layout.py`
- `rbac.py`
- `status_utils.py`
- `requirements.txt`
- `pages/01_*`
- `pages/02_*`

### Arquivos novos na versão atualizada (referência)

- `pages/03_Planejamento.py`
- `pages/04_Autoavaliacao.py`
- `pages/05_Egressos.py`
- `pages/06_Casos_Impacto.py`
- `pages/07_Evidencias.py`
- `pages/08_Projetos.py`
- `pages/09_Producoes.py`
- `pages/10_Pessoas.py`

### Arquivos redundantes na versão atualizada (não incorporados)

- `__pycache__/` e `pages/__pycache__/`
- Estrutura simplificada de páginas base (08/09/10) que duplicava funcionalidades já existentes no repositório atual

## 3) Estratégia de merge aplicada

Merge conservador e incremental:

- Preservação da arquitetura atual e das páginas legadas.
- Inclusão dos novos módulos CAPES como páginas adicionais (`11` a `15`) para evitar breaking changes.
- Extensão da camada de dados/seed sem remover funções existentes.
- Enriquecimento da visão geral e administração do PPG com foco CAPES 2025-2028.

## 4) Arquivos criados, alterados, removidos e renomeados

### Criados

- `pages/11_Planejamento_Estrategico.py`
- `pages/12_Autoavaliacao.py`
- `pages/13_Egressos.py`
- `pages/14_Casos_de_Impacto.py`
- `pages/15_Evidencias.py`

### Alterados

- `README.md`
- `app.py`
- `data.py`
- `demo_seed.py`
- `demo_store.py`
- `layout.py`
- `pages/01_Visão_Geral.py`
- `pages/02_PPG_Admin.py`

### Removidos

- Nenhum.

### Renomeados

- Nenhum.

## 5) Conflitos conceituais e decisões

1. Navegação e organização de páginas
- Conflito: versão atualizada substituía parte das páginas base por versões simplificadas.
- Decisão: manter páginas legadas e adicionar módulos CAPES em páginas novas.

2. Camada de dados
- Conflito: versão atualizada adotava fachada mais enxuta e estrutura de coleções diferente.
- Decisão: manter API atual do repositório e estender `data.py`/`demo_store.py` com coleções CAPES (`planning_goals`, `self_assessments`, `alumni`, `impact_cases`, `evidence_items`).

3. Seed/demo
- Conflito: atualização simplificava entidades existentes.
- Decisão: preservar seed antigo e ampliar com campos institucionais do PPG e novos módulos CAPES.

4. Dependências
- Conflito: versão atualizada removia `supabase` de `requirements.txt`.
- Decisão: manter dependências atuais para evitar quebra de módulos já existentes no repositório.

## 6) Validações executadas

- `python -m compileall app.py data.py demo_seed.py demo_store.py layout.py pages`
- Resultado: compilação bem-sucedida de todos os arquivos alterados/criados.

## 7) Instruções de teste local

1. Criar/ativar ambiente virtual.
2. Instalar dependências.
3. Rodar Streamlit.
4. Validar navegação no menu lateral e os módulos novos:
   - Planejamento Estratégico
   - Autoavaliação
   - Egressos
   - Casos de Impacto
   - Evidências
5. Validar a Visão Geral (painel CAPES) e o PPG Admin (campos institucionais).

Comandos:

```bash
python -m venv .venv
source .venv/bin/activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
