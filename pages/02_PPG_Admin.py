# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from data import add_research_line, add_swot_item, delete_research_line, delete_swot_item, list_research_lines, list_swot_items
from rbac import can

st.title("Administração do PPG")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

if not can("admin"):
    st.error("Acesso restrito aos coordenadores do PPG.")
    st.stop()


st.subheader("Linhas de pesquisa")
linhas = list_research_lines(ppg_id)
if linhas:
    for linha in linhas:
        cols = st.columns([3, 1])
        cols[0].write(f"**{linha.get('name', 'Sem nome')}**\n\n{linha.get('description', '')}")
        if cols[1].button("Remover", key=f"del_linha_{linha['id']}"):
            delete_research_line(linha["id"])
            st.rerun()
else:
    st.info("Nenhuma linha cadastrada.")

with st.form("form_linha"):
    nome = st.text_input("Nome da linha")
    descricao = st.text_area("Descrição")
    submitted = st.form_submit_button("Adicionar linha")
if submitted and nome:
    add_research_line(ppg_id, nome, descricao)
    st.rerun()

st.divider()

st.subheader("Análise SWOT")
swot_data = list_swot_items(ppg_id)
for categoria, titulo in {
    "strength": "Forças",
    "weakness": "Fraquezas",
    "opportunity": "Oportunidades",
    "threat": "Ameaças",
}.items():
    st.markdown(f"### {titulo}")
    itens = [item for item in swot_data if item.get("category") == categoria]
    if itens:
        for item in itens:
            cols = st.columns([4, 1])
            cols[0].write(item.get("description", ""))
            if cols[1].button("Remover", key=f"del_swot_{item['id']}"):
                delete_swot_item(item["id"])
                st.rerun()
    else:
        st.write("Sem registros")

with st.form("form_swot"):
    categoria = st.selectbox(
        "Categoria",
        ["strength", "weakness", "opportunity", "threat"],
        format_func=lambda c: {
            "strength": "Forças",
            "weakness": "Fraquezas",
            "opportunity": "Oportunidades",
            "threat": "Ameaças",
        }.get(c, c),
    )
    descricao = st.text_area("Descrição da entrada")
    submitted_swot = st.form_submit_button("Adicionar entrada")
if submitted_swot and descricao:
    add_swot_item(ppg_id, categoria, descricao)
    st.rerun()
