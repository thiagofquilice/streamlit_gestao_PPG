# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import streamlit as st

from layout import configure_page, render_sidebar

from demo_context import current_ppg, current_profile
from data import list_ppgs, update_ppg
from rbac import can

ensure_demo_db()

configure_page()
render_sidebar()

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
    area = st.text_input("Área de avaliação", value=ppg.get("area", ""))
    campus = st.text_input("Campus/Unidade", value=ppg.get("campus", ""))
    modalidade = st.text_input("Modalidade/Nível", value=ppg.get("modality", ""))
    missao = st.text_area("Missão", value=ppg.get("mission", ""))
    visao = st.text_area("Visão", value=ppg.get("vision", ""))
    quadrienio = st.text_input("Quadriênio", value=ppg.get("quadriennium", "2025-2028"))
    submitted = st.form_submit_button("Salvar")

if submitted:
    update_ppg(
        ppg_id,
        {
            "name": nome,
            "description": descricao,
            "area": area,
            "campus": campus,
            "modality": modalidade,
            "mission": missao,
            "vision": visao,
            "quadriennium": quadrienio,
        },
    )
    st.success("PPG atualizado.")
    st.rerun()

st.write("Use as demais páginas para gerenciar linhas, projetos, produções e evidências CAPES.")
