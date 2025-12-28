# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from provider import list_articles, list_dissertations, list_evaluations, list_projects, list_ptts
from rbac import can


st.title("Visão Geral")

ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Nenhum PPG selecionado. Volte à página inicial para escolher um programa.")
    st.stop()

st.caption(f"PPG ativo: {ppg_id} | Perfil: {role}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Projetos", len(list_projects(ppg_id)))
col2.metric("Dissertações", len(list_dissertations(ppg_id)))
col3.metric("Artigos", len(list_articles(ppg_id)))
col4.metric("PTTs", len(list_ptts(ppg_id)))

st.divider()

st.subheader("Avaliações recentes")
if can(role, "manage_evaluations"):
    avaliacoes = list_evaluations(ppg_id)
    if avaliacoes:
        df = pd.DataFrame(avaliacoes)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhuma avaliação registrada até o momento.")
else:
    st.info("Você não possui permissão para visualizar avaliações.")
