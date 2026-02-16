# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import pandas as pd
import streamlit as st

from demo_context import current_person, current_ppg, current_profile
from data import list_articles, list_dissertations, list_projects, list_ptts, list_research_lines, list_ppg_members, list_project_articles, list_project_dissertations, list_project_ptts

ensure_demo_db()

st.title("Visão Geral")
ppg_id = current_ppg()
profile = current_profile()
if not ppg_id:
    st.stop()

st.caption(f"PPG ativo: {ppg_id} | Perfil: {profile} | Pessoa atual: {current_person() or 'Coordenação'}")

lines = list_research_lines(ppg_id)
projects = list_projects(ppg_id)
dissertations = list_dissertations(ppg_id)
articles = list_articles(ppg_id)
ptts = list_ptts(ppg_id)
people = list_ppg_members(ppg_id)

col1, col2, col3 = st.columns(3)
col1.metric("Pessoas", len(people))
col1.metric("Linhas de Pesquisa", len(lines))
col2.metric("Projetos", len(projects))
col2.metric("Dissertações", len(dissertations))
col3.metric("Artigos", len(articles))
col3.metric("PTTs", len(ptts))

st.subheader("Produção por Linha de Pesquisa")
line_map = {line.get("id"): line.get("name") for line in lines}
rows_by_line: dict[str, dict[str, int | str]] = {}

for proj in projects:
    line_id = proj.get("line_id")
    line_name = line_map.get(line_id) or "Sem linha"
    if line_name not in rows_by_line:
        rows_by_line[line_name] = {
            "Linha de Pesquisa": line_name,
            "#Dissertações": 0,
            "#Artigos": 0,
            "#PTTs": 0,
        }
    rows_by_line[line_name]["#Dissertações"] += len(list_project_dissertations(proj.get("id")))
    rows_by_line[line_name]["#Artigos"] += len(list_project_articles(proj.get("id")))
    rows_by_line[line_name]["#PTTs"] += len(list_project_ptts(proj.get("id")))

if rows_by_line:
    st.dataframe(pd.DataFrame(rows_by_line.values()).sort_values("Linha de Pesquisa"), use_container_width=True)
else:
    st.info("Nenhum projeto cadastrado.")
