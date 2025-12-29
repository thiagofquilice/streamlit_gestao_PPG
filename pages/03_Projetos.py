# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

st.title("Projetos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

st.info("Módulo em construção. Integração com Supabase poderá ser adicionada futuramente.")
