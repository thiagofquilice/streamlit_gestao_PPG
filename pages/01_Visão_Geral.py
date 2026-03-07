# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import pandas as pd
import streamlit as st

from layout import configure_page, render_sidebar
from navigation_utils import navigate_to

from demo_context import current_person, current_ppg, current_profile
from data import (
    add_research_line,
    list_articles,
    list_dissertations,
    list_ppg_members,
    list_planning_goals,
    list_project_articles,
    list_project_dissertations,
    list_project_ptts,
    list_projects,
    list_self_assessments,
    list_ptts,
    list_alumni,
    list_impact_cases,
    list_evidence_items,
    list_research_lines,
)

ensure_demo_db()

configure_page()
render_sidebar()

st.title("Visão Geral")
ppg_id = current_ppg()
profile = current_profile()
if not ppg_id:
    st.stop()

st.caption(f"PPG ativo: {ppg_id} | Perfil: {profile} | Pessoa atual: {current_person() or 'Coordenação'}")

if "show_add_line_form" not in st.session_state:
    st.session_state.show_add_line_form = False

if st.button("Adicionar Linha de Pesquisa"):
    st.session_state.show_add_line_form = not st.session_state.show_add_line_form

if st.session_state.show_add_line_form:
    with st.form("add_line_form", clear_on_submit=True):
        line_name = st.text_input("Nome da Linha de Pesquisa")
        line_description = st.text_area("Descrição")
        submit_line = st.form_submit_button("Salvar Linha")
    if submit_line:
        if not line_name.strip():
            st.warning("Informe o nome da linha de pesquisa.")
        else:
            add_research_line(ppg_id, line_name.strip(), line_description.strip())
            st.success("Linha de pesquisa adicionada com sucesso.")
            st.session_state.show_add_line_form = False
            st.rerun()

lines = list_research_lines(ppg_id)
projects = list_projects(ppg_id)
dissertations = list_dissertations(ppg_id)
articles = list_articles(ppg_id)
ptts = list_ptts(ppg_id)
people = list_ppg_members(ppg_id)
goals = list_planning_goals(ppg_id)
self_assessments = list_self_assessments(ppg_id)
alumni = list_alumni(ppg_id)
impact_cases = list_impact_cases(ppg_id)
evidence_items = list_evidence_items(ppg_id)

col1, col2, col3 = st.columns(3)
col1.metric("Pessoas", len(people))
col1.metric("Linhas de Pesquisa", len(lines))
col2.metric("Projetos", len(projects))
col2.metric("Dissertações", len(dissertations))
col3.metric("Artigos", len(articles))
col3.metric("PTTs", len(ptts))


col4, col5, col6, col7 = st.columns(4)
col4.metric("Metas estratégicas", len(goals))
col5.metric("Autoavaliações", len(self_assessments))
col6.metric("Egressos", len(alumni))
col7.metric("Casos de impacto", len(impact_cases))

st.subheader("Painel de aderência CAPES 2025-2028")
validated_evidence = len([item for item in evidence_items if item.get("status") == "validado"])
panel_rows = [
    {
        "Dimensão": "Planejamento Estratégico",
        "Situação": "Estruturado" if goals else "Inexistente",
        "Detalhe": f"{len(goals)} metas cadastradas",
    },
    {
        "Dimensão": "Autoavaliação",
        "Situação": "Estruturado" if self_assessments else "Inexistente",
        "Detalhe": f"{len(self_assessments)} ciclos registrados",
    },
    {
        "Dimensão": "Egressos",
        "Situação": "Estruturado" if alumni else "Inexistente",
        "Detalhe": f"{len(alumni)} egressos acompanhados",
    },
    {
        "Dimensão": "Casos de Impacto",
        "Situação": "Estruturado" if impact_cases else "Inexistente",
        "Detalhe": f"{len(impact_cases)} casos documentados",
    },
    {
        "Dimensão": "Evidências",
        "Situação": "Estruturado" if evidence_items else "Inexistente",
        "Detalhe": f"{validated_evidence} evidências validadas de {len(evidence_items)}",
    },
]
st.dataframe(pd.DataFrame(panel_rows), use_container_width=True, hide_index=True)
st.subheader("Produção por Linha de Pesquisa")
line_map = {line.get("id"): line.get("name") for line in lines}
rows_by_line: dict[str, dict[str, int | str]] = {}
line_id_by_name: dict[str, str] = {}

for proj in projects:
    line_id = proj.get("line_id")
    line_name = line_map.get(line_id) or "Sem linha"
    if line_name not in rows_by_line:
        if line_id:
            line_id_by_name[line_name] = line_id
        rows_by_line[line_name] = {
            "Linha de Pesquisa": line_name,
            "#Projetos": 0,
            "#Dissertações": 0,
            "#Artigos": 0,
            "#PTTs": 0,
        }
    rows_by_line[line_name]["#Projetos"] += 1
    rows_by_line[line_name]["#Dissertações"] += len(list_project_dissertations(proj.get("id")))
    rows_by_line[line_name]["#Artigos"] += len(list_project_articles(proj.get("id")))
    rows_by_line[line_name]["#PTTs"] += len(list_project_ptts(proj.get("id")))

if rows_by_line:
    sorted_rows = pd.DataFrame(rows_by_line.values()).sort_values("Linha de Pesquisa").to_dict(orient="records")
    head = st.columns([3, 1, 1, 1, 1])
    head[0].markdown("**Linha de Pesquisa**")
    head[1].markdown("**#Projetos**")
    head[2].markdown("**#Dissertações**")
    head[3].markdown("**#Artigos**")
    head[4].markdown("**#PTTs**")

    for idx, row in enumerate(sorted_rows):
        line_name = row["Linha de Pesquisa"]
        cols = st.columns([3, 1, 1, 1, 1])
        line_id = line_id_by_name.get(line_name)
        if line_id:
            if cols[0].button(line_name, key=f"overview-line-{idx}", type="secondary"):
                navigate_to("pages/03_Linhas_de_Pesquisa.py", "research_line", line_id)
        else:
            cols[0].write(line_name)
        cols[1].write(row["#Projetos"])
        cols[2].write(row["#Dissertações"])
        cols[3].write(row["#Artigos"])
        cols[4].write(row["#PTTs"])
else:
    st.info("Nenhum projeto cadastrado.")
