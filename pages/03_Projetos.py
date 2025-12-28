# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from provider import list_projects, remove_project, upsert_project
from rbac import can


st.title("Projetos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

if not (can(role, "manage_projects") or can(role, "view_projects")):
    st.error("Você não possui acesso a esta página.")
    st.stop()

projetos = list_projects(ppg_id)
if projetos:
    for projeto in projetos:
        cols = st.columns([3, 1])
        cols[0].write(f"**{projeto.get('titulo', '')}**\n\nLíder: {projeto.get('lider', 'N/D')}\n\nStatus: {projeto.get('status', 'N/D')}")
        if can(role, "manage_projects") and cols[1].button("Excluir", key=f"del_proj_{projeto['id']}"):
            remove_project(projeto["id"])
            st.experimental_rerun()
else:
    st.info("Nenhum projeto cadastrado.")

if can(role, "manage_projects"):
    with st.form("form_projeto"):
        titulo = st.text_input("Título do projeto")
        lider = st.text_input("Líder")
        status = st.selectbox("Status", ["Planejado", "Em andamento", "Concluído"])
        submitted = st.form_submit_button("Salvar projeto")
    if submitted and titulo:
        upsert_project(ppg_id, titulo, lider, status)
        st.success("Projeto cadastrado com sucesso.")
        st.experimental_rerun()
