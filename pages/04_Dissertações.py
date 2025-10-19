# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from data import delete_record, list_dissertacoes, upsert_dissertacao
from rbac import can


st.title("Dissertações")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

if not (can(role, "manage_dissertations") or can(role, "view_dissertations")):
    st.error("Você não possui acesso a esta página.")
    st.stop()

records = list_dissertacoes(ppg_id)
if records:
    for disser in records:
        cols = st.columns([3, 1])
        cols[0].write(
            f"**{disser.get('titulo', '')}**\nAutor(a): {disser.get('autor', 'N/D')}\nOrientador(a): {disser.get('orientador', 'N/D')}\nDefesa prevista: {disser.get('defesa_prevista', 'N/D')}"
        )
        if can(role, "manage_dissertations") and cols[1].button("Excluir", key=f"del_dis_{disser['id']}"):
            delete_record("dissertacoes", disser["id"])
            st.experimental_rerun()
else:
    st.info("Nenhuma dissertação cadastrada.")

if can(role, "manage_dissertations"):
    with st.form("form_dissertacao"):
        titulo = st.text_input("Título")
        autor = st.text_input("Autor(a)")
        orientador = st.text_input("Orientador(a)")
        defesa_prevista = st.date_input("Data prevista de defesa")
        submitted = st.form_submit_button("Salvar")
    if submitted and titulo and autor:
        upsert_dissertacao(ppg_id, titulo, autor, orientador, defesa_prevista.isoformat())
        st.success("Dissertação cadastrada com sucesso.")
        st.experimental_rerun()
