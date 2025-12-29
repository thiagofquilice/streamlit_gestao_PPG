# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

st.title("Dissertações")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

st.info("Módulo em construção. Cadastros poderão ser integrados ao Supabase seguindo o mesmo padrão de RLS.")
