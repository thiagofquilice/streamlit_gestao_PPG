# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_evidence_items, list_self_assessments, upsert_self_assessment
from demo_context import current_ppg
from demo_seed import ensure_demo_db
from layout import configure_page, render_sidebar
from rbac import can

ensure_demo_db()

configure_page("Autoavaliação")
render_sidebar()

st.title("Autoavaliação")
st.info("Registre ciclos, instrumentos, achados, fragilidades e encaminhamentos para compor a narrativa CAPES.")

ppg_id = current_ppg()
if not ppg_id:
    st.stop()

rows = list_self_assessments(ppg_id)
evidence_items = list_evidence_items(ppg_id)
evidence_map = {item.get("id"): item.get("title") for item in evidence_items}

if rows:
    display = []
    for row in rows:
        evidence_titles = [evidence_map.get(eid, eid) for eid in row.get("related_evidence_ids", [])]
        display.append(
            {
                "Ciclo/Período": row.get("cycle_period"),
                "Instrumento": row.get("instrument"),
                "Participantes": row.get("participants"),
                "Dimensões avaliadas": row.get("assessed_dimensions"),
                "Principais achados": row.get("key_findings"),
                "Fragilidades": row.get("weaknesses"),
                "Encaminhamentos": row.get("referrals"),
                "Status dos encaminhamentos": row.get("referrals_status"),
                "Evidências associadas": ", ".join(evidence_titles) if evidence_titles else "-",
            }
        )
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum ciclo de autoavaliação registrado.")

if can("editar"):
    st.divider()
    with st.form("self_assessment_form", clear_on_submit=True):
        cycle_period = st.text_input("Ciclo/Período", placeholder="Ex.: 2025")
        instrument = st.text_input("Instrumento")
        participants = st.text_input("Participantes")
        assessed_dimensions = st.text_area("Dimensões avaliadas")
        key_findings = st.text_area("Principais achados")
        weaknesses = st.text_area("Fragilidades")
        referrals = st.text_area("Encaminhamentos")
        referrals_status = st.selectbox("Status dos encaminhamentos", ["rascunho", "em_andamento", "concluido"])
        related_evidence_ids = st.multiselect(
            "Evidências associadas",
            [item.get("id") for item in evidence_items],
            format_func=lambda eid: evidence_map.get(eid, eid),
        )
        submitted = st.form_submit_button("Salvar")

    if submitted:
        if not cycle_period.strip() or not assessed_dimensions.strip():
            st.warning("Informe pelo menos ciclo/período e dimensões avaliadas.")
        else:
            upsert_self_assessment(
                {
                    "ppg_id": ppg_id,
                    "cycle_period": cycle_period.strip(),
                    "instrument": instrument.strip(),
                    "participants": participants.strip(),
                    "assessed_dimensions": assessed_dimensions.strip(),
                    "key_findings": key_findings.strip(),
                    "weaknesses": weaknesses.strip(),
                    "referrals": referrals.strip(),
                    "referrals_status": referrals_status,
                    "related_evidence_ids": related_evidence_ids,
                }
            )
            st.success("Autoavaliação salva.")
            st.rerun()
