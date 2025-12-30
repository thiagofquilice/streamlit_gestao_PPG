# PPG Manager (Demo)

Ambiente Streamlit puramente em memória para validar cadastros de PPG, projetos e avaliações de Artigos e PTTs. Não há dependência de Supabase neste modo.

## Como rodar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
O seed é carregado em `st.session_state` na primeira execução. Não é necessário configurar secrets.

## Perfis e seleção de pessoa
- Use a barra lateral para escolher o **perfil** (coordenador, orientador, mestrando).
- Para orientador/mestrando, selecione também a **pessoa** correspondente. O contexto fica em `st.session_state['ctx']` (campos `ppg_id`, `profile`, `person_id`).

## Seed e relações
O arquivo `demo_seed.py` inicializa um PPG com pessoas, linhas, projetos, dissertações, artigos, PTTs, fichas e **uma avaliação para cada artigo e cada PTT**. Cada avaliação é vinculada apenas pelos campos `target_type` (`"article"` ou `"ptt"`) e `target_id` (ID do artigo/PTT), evitando referências duplicadas dentro dos próprios registros.

## Uso das avaliações
- Nas páginas **Artigos** e **PTTs**: mostra contagem, média e última nota, além da lista de avaliações vinculadas e o atalho para criar nova avaliação.
- Na página **Avaliações**: filtre por tipo (Artigo/PTT), escolha o item, visualize avaliações existentes e cadastre uma nova usando a ficha específica (`evaluation_forms['articles']` ou `['ptts']`). A nota final é calculada como soma ponderada das respostas.

## Estabilidade do DEMO
Todas as páginas chamam `ensure_demo_db()` logo no início, antes de importar qualquer função de `data`, garantindo que o banco em memória esteja pronto e evitando crashes durante a navegação.
