# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from rbac import can

st.title("Avaliações")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

if can("admin"):
    st.info("Planeje e registre avaliações aqui. A integração com Supabase pode reaproveitar o padrão de artigos e SWOT.")
else:
    st.info("A visualização de avaliações será habilitada conforme regras de permissão futuras.")
