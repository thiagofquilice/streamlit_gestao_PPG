# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from demo_context import current_person, current_ppg, current_profile
from data import list_articles, list_dissertations, list_projects, list_ptts, list_research_lines, list_ppg_members, list_project_articles, list_project_dissertations, list_project_ptts

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

st.subheader("Produção por projeto")
rows = []
for proj in projects:
    rows.append(
        {
            "Projeto": proj.get("name"),
            "#Dissertações": len(list_project_dissertations(proj.get("id"))),
            "#Artigos": len(list_project_articles(proj.get("id"))),
            "#PTTs": len(list_project_ptts(proj.get("id"))),
        }
    )
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
else:
    st.info("Nenhum projeto cadastrado.")
