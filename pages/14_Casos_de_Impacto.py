# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_evidence_items, list_impact_cases, list_ppg_members, upsert_impact_case
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
people_map = {item.get("id"): item.get("name") for item in people}
evidence_map = {item.get("id"): item.get("title") for item in evidence_items}

if rows:
    display = []
    for row in rows:
        involved_names = [people_map.get(pid, pid) for pid in row.get("involved_people_ids", [])]
        evidence_titles = [evidence_map.get(eid, eid) for eid in row.get("evidence_ids", [])]
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
                    "evidence_ids": evidence_ids,
                    "replication_potential": replication_potential.strip(),
                    "status": status,
                }
            )
            st.success("Caso de impacto salvo.")
            st.rerun()
