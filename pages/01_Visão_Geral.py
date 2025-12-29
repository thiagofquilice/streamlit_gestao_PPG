# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from rbac import can

st.title("Visão Geral")

ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

st.caption(f"PPG ativo: {ppg_id} | Perfil: {role}")

st.info(
    "Esta visão geral será preenchida com indicadores quando mais módulos estiverem conectados ao Supabase."
)

if can("admin"):
    st.success("Você é coordenador e pode acessar a administração do PPG no menu lateral.")
else:
    st.write("Use o menu lateral para navegar pelas seções disponíveis.")
