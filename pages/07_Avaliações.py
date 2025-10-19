# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from auth import get_auth_state
from components.forms import evaluation_form
from data import list_avaliacoes, list_criterios, list_fichas
from rbac import can


st.title("Avaliações")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

auth_state = get_auth_state()

if not can(role, "manage_evaluations"):
    st.error("Somente coordenadores e professores podem lançar avaliações.")
else:
    fichas = list_fichas(ppg_id)
    if not fichas:
        st.info("Cadastre fichas na área de administração do PPG antes de lançar avaliações.")
    else:
        ficha_options = {ficha["nome"]: ficha for ficha in fichas}
        ficha_nome = st.selectbox("Ficha de avaliação", list(ficha_options.keys()))
        ficha = ficha_options[ficha_nome]
        criterios = list_criterios(ficha["id"])
        if criterios:
            evaluation_form(ppg_id, ficha["id"], auth_state.user_id, criterios)
        else:
            st.warning("Cadastre critérios para esta ficha.")

st.divider()

st.subheader("Histórico de avaliações")
avaliacoes = list_avaliacoes(ppg_id)
if avaliacoes:
    df = pd.DataFrame(avaliacoes)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhuma avaliação registrada até o momento.")
