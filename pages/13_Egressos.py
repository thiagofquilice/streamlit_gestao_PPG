# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_alumni, upsert_alumnus
from demo_context import current_ppg
from demo_seed import ensure_demo_db
from layout import configure_page, render_sidebar
from rbac import can

ensure_demo_db()

configure_page("Egressos")
render_sidebar()

st.title("Egressos")
st.info("Registre trajetória profissional e contribuição percebida do PPG para fortalecer o eixo de impacto e inserção.")

ppg_id = current_ppg()
if not ppg_id:
    st.stop()

rows = list_alumni(ppg_id)

if rows:
    display = []
    for row in rows:
        display.append(
            {
                "Nome": row.get("name"),
                "Turma/Ano": row.get("cohort_year"),
                "Vínculo com dissertação/projeto/PTT": row.get("dissertation_project_ptt_link"),
                "Atuação profissional": row.get("professional_activity"),
                "Setor": row.get("sector"),
                "Cargo/Função": row.get("position_role"),
                "Progressão": row.get("progression"),
                "Evidências/Depoimentos": row.get("evidence_testimonials"),
                "Contribuição percebida do PPG": row.get("perceived_ppg_contribution"),
            }
        )
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum egresso cadastrado.")

if can("editar"):
    st.divider()
    with st.form("alumni_form", clear_on_submit=True):
        name = st.text_input("Nome")
        cohort_year = st.number_input("Turma/Ano", min_value=1990, max_value=2100, value=2024, step=1)
        dissertation_project_ptt_link = st.text_input("Vínculo com dissertação/projeto/PTT")
        professional_activity = st.text_input("Atuação profissional")
        sector = st.selectbox("Setor", ["Setor público", "Setor privado", "Terceiro setor", "Acadêmico", "Outro"])
        position_role = st.text_input("Cargo/Função")
        progression = st.text_area("Progressão")
        evidence_testimonials = st.text_area("Evidências/Depoimentos")
        perceived_ppg_contribution = st.text_area("Contribuição percebida do PPG")
        submitted = st.form_submit_button("Salvar")

    if submitted:
        if not name.strip():
            st.warning("Informe o nome do egresso.")
        else:
            upsert_alumnus(
                {
                    "ppg_id": ppg_id,
                    "name": name.strip(),
                    "cohort_year": int(cohort_year),
                    "dissertation_project_ptt_link": dissertation_project_ptt_link.strip(),
                    "professional_activity": professional_activity.strip(),
                    "sector": sector,
                    "position_role": position_role.strip(),
                    "progression": progression.strip(),
                    "evidence_testimonials": evidence_testimonials.strip(),
                    "perceived_ppg_contribution": perceived_ppg_contribution.strip(),
                }
            )
            st.success("Registro de egresso salvo.")
            st.rerun()
