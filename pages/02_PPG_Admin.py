# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from demo_context import current_ppg, current_profile
from data import list_ppgs, update_ppg
from rbac import can

st.title("Administração do PPG")
ppg_id = current_ppg()
profile = current_profile()
if not ppg_id:
    st.stop()

if not can("admin"):
    st.error("Acesso restrito aos coordenadores do PPG.")
    st.stop()

ppg = next((p for p in list_ppgs() if p.get("id") == ppg_id), None)
if not ppg:
    st.error("PPG não encontrado.")
    st.stop()

with st.form("ppg_form"):
    nome = st.text_input("Nome do PPG", value=ppg.get("name", ""))
    descricao = st.text_area("Descrição", value=ppg.get("description", ""))
    submitted = st.form_submit_button("Salvar")

if submitted:
    update_ppg(ppg_id, {"name": nome, "description": descricao})
    st.success("PPG atualizado.")
    st.rerun()

st.write("Use as demais páginas para gerenciar linhas, projetos e produções.")
