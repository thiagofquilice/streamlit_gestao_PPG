# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import streamlit as st
from ui_style import apply_modern_white_theme

ensure_demo_db()
apply_modern_white_theme()

st.title("Relatórios")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

st.info("Módulo em construção. Use os dados já disponíveis (linhas de pesquisa, SWOT, artigos) para validar o fluxo multi-PPG.")
