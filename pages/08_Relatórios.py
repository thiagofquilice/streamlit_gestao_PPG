# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from provider import list_reports, save_report
from rbac import can


st.title("Relatórios")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

if can(role, "view_reports"):
    relatorios = list_reports(ppg_id)
    if relatorios:
        st.dataframe(pd.DataFrame(relatorios), use_container_width=True)
    else:
        st.info("Nenhum relatório cadastrado.")
else:
    st.error("Você não possui acesso aos relatórios.")

if can(role, "manage_ppg_admin"):
    with st.form("form_relatorio"):
        periodo = st.text_input("Período (ex: 2024-1)")
        resumo = st.text_area("Resumo executivo")
        submitted = st.form_submit_button("Salvar relatório")
    if submitted and periodo:
        save_report(ppg_id, periodo, resumo)
        st.success("Relatório salvo.")
        st.experimental_rerun()
