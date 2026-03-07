# PPG Manager (Demo CAPES)

Aplicação Streamlit em modo demo (dados em `st.session_state`) para gestão integrada do PPG com foco em evidências CAPES 2025-2028.

## Módulos principais

- Cadastros-base: PPG, Linhas de Pesquisa, Projetos, Dissertações, Artigos, PTTs e Pessoas
- Planejamento Estratégico
- Autoavaliação
- Egressos
- Casos de Impacto
- Evidências
- Classificações e Avaliações

## Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Modo demo

- O seed é carregado automaticamente por `ensure_demo_db()`.
- O contexto de navegação fica em `st.session_state['ctx']` (`ppg_id`, `profile`, `person_id`).
- O menu lateral permite resetar, exportar e importar o banco demo em JSON.

## Observações de integração

- A arquitetura original do repositório foi preservada.
- Os novos módulos CAPES foram incorporados incrementalmente (sem remover páginas legadas).
- O seed foi ampliado com coleções de planejamento, autoavaliação, egressos, impacto e evidências.
