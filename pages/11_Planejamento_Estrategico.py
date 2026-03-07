# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_evidence_items, list_planning_goals, upsert_planning_goal
from demo_context import current_ppg
from demo_seed import ensure_demo_db
from layout import configure_page, render_sidebar
from rbac import can

ensure_demo_db()

configure_page("Planejamento Estratégico")
render_sidebar()

st.title("Planejamento Estratégico")
st.info(
    "Registre objetivos estratégicos, ações e indicadores do ciclo CAPES 2025-2028. "
    "Cada meta pode ser associada a uma evidência do repositório."
)

ppg_id = current_ppg()
if not ppg_id:
    st.stop()

rows = list_planning_goals(ppg_id)
evidence_items = list_evidence_items(ppg_id)
evidence_map = {item.get("id"): item.get("title") for item in evidence_items}

if rows:
    display = []
    for row in rows:
        display.append(
            {
                "Objetivo estratégico": row.get("strategic_objective"),
                "Ação": row.get("action"),
                "Indicador": row.get("indicator"),
                "Meta": row.get("target"),
                "Prazo": row.get("deadline"),
                "Responsável": row.get("responsible"),
                "Status": row.get("status"),
                "Evidência associada": evidence_map.get(row.get("related_evidence_id"), row.get("related_evidence_id") or "-"),
            }
        )
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhuma meta estratégica cadastrada.")

if can("editar"):
    st.divider()
    st.subheader("Cadastrar meta estratégica")
    with st.form("planning_goal_form", clear_on_submit=True):
        strategic_objective = st.text_area("Objetivo estratégico")
        action = st.text_area("Ação")
        indicator = st.text_input("Indicador")
        target = st.text_input("Meta")
        deadline = st.date_input("Prazo")
        responsible = st.text_input("Responsável")
        status = st.selectbox("Status", ["planejado", "em_andamento", "concluido"])
        related_evidence_id = st.selectbox(
            "Evidência associada",
            [None] + [item.get("id") for item in evidence_items],
            format_func=lambda eid: evidence_map.get(eid, "Sem evidência associada") if eid else "Sem evidência associada",
        )

        submitted = st.form_submit_button("Salvar")

    if submitted:
        if not strategic_objective.strip() or not action.strip():
            st.warning("Informe pelo menos o objetivo estratégico e a ação.")
        else:
            upsert_planning_goal(
                {
                    "ppg_id": ppg_id,
                    "strategic_objective": strategic_objective.strip(),
                    "action": action.strip(),
                    "indicator": indicator.strip(),
                    "target": target.strip(),
                    "deadline": str(deadline),
                    "responsible": responsible.strip(),
                    "status": status,
                    "related_evidence_id": related_evidence_id,
                }
            )
            st.success("Meta estratégica salva.")
            st.rerun()
