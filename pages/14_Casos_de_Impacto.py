# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import (
    list_articles,
    list_dissertations,
    list_evidence_items,
    list_impact_cases,
    list_ppg_members,
    list_projects,
    list_ptts,
    list_research_lines,
    upsert_impact_case,
)
from demo_context import current_ppg
from demo_seed import ensure_demo_db
from layout import configure_page, render_sidebar
from rbac import can

ensure_demo_db()

configure_page("Casos de Impacto")
render_sidebar()

st.title("Casos de Impacto")
st.info("Documente evidências de contribuição do PPG para organizações e território, com foco em transferência e resultados.")

ppg_id = current_ppg()
if not ppg_id:
    st.stop()

rows = list_impact_cases(ppg_id)
people = list_ppg_members(ppg_id)
evidence_items = list_evidence_items(ppg_id)
projects = list_projects(ppg_id)
lines = list_research_lines(ppg_id)
dissertations = list_dissertations(ppg_id)
articles = list_articles(ppg_id)
ptts = list_ptts(ppg_id)

people_map = {item.get("id"): item.get("name") for item in people}
evidence_map = {item.get("id"): item.get("title") for item in evidence_items}
project_map = {item.get("id"): item.get("name") for item in projects}
line_map = {item.get("id"): item.get("name") for item in lines}
dissertation_map = {item.get("id"): item.get("title") for item in dissertations}
article_map = {item.get("id"): item.get("title") for item in articles}
ptt_map = {item.get("id"): item.get("title") for item in ptts}

if rows:
    display = []
    for row in rows:
        involved_names = [people_map.get(pid, pid) for pid in row.get("involved_people_ids", [])]
        evidence_titles = [evidence_map.get(eid, eid) for eid in row.get("evidence_ids", [])]

        related_dissertations = [dissertation_map.get(did, did) for did in row.get("related_dissertation_ids", [])]
        related_articles = [article_map.get(aid, aid) for aid in row.get("related_article_ids", [])]
        related_ptts = [ptt_map.get(pid, pid) for pid in row.get("related_ptt_ids", [])]
        related_projects = [project_map.get(pid, pid) for pid in row.get("related_project_ids", [])]
        related_lines = [line_map.get(lid, lid) for lid in row.get("related_line_ids", [])]

        has_links = row.get("has_academic_links") or any(
            [
                related_dissertations,
                related_articles,
                related_ptts,
                related_projects,
                related_lines,
            ]
        )

        display.append(
            {
                "Título do caso": row.get("case_title"),
                "Contexto/Problema": row.get("context_problem"),
                "Contribuição do PPG": row.get("ppg_contribution"),
                "Pessoas envolvidas": ", ".join(involved_names) if involved_names else "-",
                "Parceiros externos": row.get("external_partners"),
                "Produto/Ação gerada": row.get("generated_product_action"),
                "Mecanismo de transferência": row.get("transfer_mechanism"),
                "Resultados": row.get("results"),
                "Relacionado a dissertação/artigo/PTT/projeto/linha": "Sim" if has_links else "Não",
                "Dissertações vinculadas": ", ".join(related_dissertations) if related_dissertations else "-",
                "Artigos vinculados": ", ".join(related_articles) if related_articles else "-",
                "PTTs vinculados": ", ".join(related_ptts) if related_ptts else "-",
                "Projetos vinculados": ", ".join(related_projects) if related_projects else "-",
                "Linhas vinculadas": ", ".join(related_lines) if related_lines else "-",
                "Evidências": ", ".join(evidence_titles) if evidence_titles else "-",
                "Potencial de replicação": row.get("replication_potential"),
                "Status": row.get("status"),
            }
        )
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum caso de impacto cadastrado.")

if can("editar"):
    st.divider()
    with st.form("impact_case_form", clear_on_submit=True):
        case_title = st.text_input("Título do caso")
        context_problem = st.text_area("Contexto/Problema")
        ppg_contribution = st.text_area("Contribuição do PPG")
        involved_people_ids = st.multiselect(
            "Pessoas envolvidas",
            [item.get("id") for item in people],
            format_func=lambda pid: people_map.get(pid, pid),
        )
        external_partners = st.text_input("Parceiros externos")
        generated_product_action = st.text_area("Produto/Ação gerada")
        transfer_mechanism = st.text_area("Mecanismo de transferência")
        results = st.text_area("Resultados")

        st.markdown("**Vínculos acadêmico-produtivos**")
        has_academic_links = st.radio(
            "Este caso está relacionado a dissertação, artigo ou PTT, projeto e/ou linha?",
            ["Não", "Sim"],
            horizontal=True,
            index=1,
        )

        if has_academic_links == "Sim":
            related_dissertation_ids = st.multiselect(
                "Dissertações vinculadas",
                [item.get("id") for item in dissertations],
                format_func=lambda did: dissertation_map.get(did, did),
            )
            related_article_ids = st.multiselect(
                "Artigos vinculados",
                [item.get("id") for item in articles],
                format_func=lambda aid: article_map.get(aid, aid),
            )
            related_ptt_ids = st.multiselect(
                "PTTs vinculados",
                [item.get("id") for item in ptts],
                format_func=lambda pid: ptt_map.get(pid, pid),
            )
            related_project_ids = st.multiselect(
                "Projetos vinculados",
                [item.get("id") for item in projects],
                format_func=lambda pid: project_map.get(pid, pid),
            )
            related_line_ids = st.multiselect(
                "Linhas vinculadas",
                [item.get("id") for item in lines],
                format_func=lambda lid: line_map.get(lid, lid),
            )
        else:
            related_dissertation_ids = []
            related_article_ids = []
            related_ptt_ids = []
            related_project_ids = []
            related_line_ids = []

        evidence_ids = st.multiselect(
            "Evidências",
            [item.get("id") for item in evidence_items],
            format_func=lambda eid: evidence_map.get(eid, eid),
        )
        replication_potential = st.text_area("Potencial de replicação")
        status = st.selectbox("Status", ["rascunho", "em_documentacao", "validado"])
        submitted = st.form_submit_button("Salvar")

    if submitted:
        if not case_title.strip() or not context_problem.strip():
            st.warning("Informe pelo menos o título e o contexto/problema.")
        else:
            upsert_impact_case(
                {
                    "ppg_id": ppg_id,
                    "case_title": case_title.strip(),
                    "context_problem": context_problem.strip(),
                    "ppg_contribution": ppg_contribution.strip(),
                    "involved_people_ids": involved_people_ids,
                    "external_partners": external_partners.strip(),
                    "generated_product_action": generated_product_action.strip(),
                    "transfer_mechanism": transfer_mechanism.strip(),
                    "results": results.strip(),
                    "has_academic_links": has_academic_links == "Sim",
                    "related_dissertation_ids": related_dissertation_ids,
                    "related_article_ids": related_article_ids,
                    "related_ptt_ids": related_ptt_ids,
                    "related_project_ids": related_project_ids,
                    "related_line_ids": related_line_ids,
                    "evidence_ids": evidence_ids,
                    "replication_potential": replication_potential.strip(),
                    "status": status,
                }
            )
            st.success("Caso de impacto salvo.")
            st.rerun()
