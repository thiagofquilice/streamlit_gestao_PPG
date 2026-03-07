# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_evidence_items, upsert_evidence_item
from demo_context import current_ppg
from demo_seed import ensure_demo_db
from layout import configure_page, render_sidebar
from rbac import can

ensure_demo_db()

configure_page("Evidências")
render_sidebar()

st.title("Evidências")
st.info("Repositório documental do PPG para sustentar planejamento, autoavaliação, egressos e casos de impacto.")

ppg_id = current_ppg()
if not ppg_id:
    st.stop()

rows = list_evidence_items(ppg_id)

if rows:
    display = []
    for row in rows:
        display.append(
            {
                "Título": row.get("title"),
                "Tipo de evidência": row.get("evidence_type"),
                "Módulo relacionado": row.get("related_module"),
                "Descrição": row.get("description"),
                "Link/Arquivo/Caminho": row.get("link_file_path"),
                "Data": row.get("date"),
                "Observações": row.get("notes"),
                "Status": row.get("status"),
            }
        )
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhuma evidência cadastrada.")

if can("editar"):
    st.divider()
    with st.form("evidence_form", clear_on_submit=True):
        title = st.text_input("Título")
        evidence_type = st.text_input("Tipo de evidência", placeholder="Ex.: relatório, ata, print, vídeo, depoimento")
        related_module = st.selectbox(
            "Módulo relacionado",
            ["Planejamento Estratégico", "Autoavaliação", "Egressos", "Casos de Impacto", "Produções", "PPG/Admin"],
        )
        description = st.text_area("Descrição")
        link_file_path = st.text_input("Link/Arquivo/Caminho")
        date = st.date_input("Data")
        notes = st.text_area("Observações")
        status = st.selectbox("Status", ["rascunho", "validado"])
        submitted = st.form_submit_button("Salvar")

    if submitted:
        if not title.strip() or not evidence_type.strip():
            st.warning("Informe pelo menos título e tipo de evidência.")
        else:
            upsert_evidence_item(
                {
                    "ppg_id": ppg_id,
                    "title": title.strip(),
                    "evidence_type": evidence_type.strip(),
                    "related_module": related_module,
                    "description": description.strip(),
                    "link_file_path": link_file_path.strip(),
                    "date": str(date),
                    "notes": notes.strip(),
                    "status": status,
                }
            )
            st.success("Evidência salva.")
            st.rerun()
