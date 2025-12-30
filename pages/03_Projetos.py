# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db

ensure_demo_db()

import streamlit as st

from demo_context import current_ppg, current_profile
from data import (
    list_ppg_members,
    list_project_articles,
    list_project_dissertations,
    list_project_ptts,
    list_projects,
    list_research_lines,
)

st.title("Projetos")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

lines = {line["id"]: line.get("name") for line in list_research_lines(ppg_id)}
members = list_ppg_members(ppg_id)
member_labels = {m["user_id"]: m.get("label") or m.get("display_name") or m.get("name") or m["user_id"] for m in members}

projects = list_projects(ppg_id)
if not projects:
    st.info("Nenhum projeto cadastrado para este PPG.")
    st.stop()

st.caption(
    "Visualização somente leitura no DEMO. Cada projeto mostra vínculos com orientadores, mestrandos, dissertações, artigos e PTTs."
)

for project in projects:
    with st.expander(project.get("name") or "(Sem nome)", expanded=False):
        st.write(project.get("description") or "Sem descrição.")
        st.caption(f"Linha de pesquisa: {lines.get(project.get('line_id')) or 'Sem linha'} | Status: {project.get('status')}")

        orientadores_ids = project.get("orientadores_ids", [])
        mestrandos_ids = project.get("mestrandos_ids", [])
        st.write(
            "Orientadores:",
            ", ".join([member_labels.get(oid, oid) for oid in orientadores_ids]) or "Nenhum orientador vinculado",
        )
        st.write(
            "Mestrandos:",
            ", ".join([member_labels.get(mid, mid) for mid in mestrandos_ids]) or "Nenhum mestrando vinculado",
        )

        st.markdown("**Associados**")
        diss = list_project_dissertations(project["id"])
        arts = list_project_articles(project["id"])
        ptts = list_project_ptts(project["id"])
        st.write("Dissertações:", ", ".join([d.get("title", "") for d in diss]) or "Nenhuma")
        st.write("Artigos:", ", ".join([a.get("title", "") for a in arts]) or "Nenhum")
        st.write("PTTs:", ", ".join([p.get("title", "") for p in ptts]) or "Nenhum")

if role not in ("coordenador", "orientador"):
    st.info("Seu perfil atual permite apenas consulta.")
