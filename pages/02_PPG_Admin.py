# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from data import (
    delete_record,
    list_fichas,
    list_criterios,
    list_linhas,
    list_objetivos,
    list_swot,
    upsert_record,
)
from rbac import can


st.title("Administração do PPG")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

if not can(role, "manage_ppg_admin"):
    st.error("Acesso restrito aos coordenadores do PPG.")
    st.stop()


def _refresh():
    st.experimental_rerun()


st.subheader("Linhas de pesquisa")
linhas = list_linhas(ppg_id)
if linhas:
    for linha in linhas:
        cols = st.columns([3, 1])
        cols[0].write(f"**{linha.get('nome', 'Sem nome')}**\n\n{linha.get('descricao', '')}")
        if cols[1].button("Remover", key=f"del_linha_{linha['id']}"):
            delete_record("linhas_pesquisa", linha["id"])
            _refresh()
else:
    st.info("Nenhuma linha cadastrada.")

with st.form("form_linha"):
    nome = st.text_input("Nome da linha")
    descricao = st.text_area("Descrição")
    submitted = st.form_submit_button("Adicionar linha")
if submitted and nome:
    upsert_record("linhas_pesquisa", {"ppg_id": ppg_id, "nome": nome, "descricao": descricao})
    _refresh()

st.divider()

st.subheader("Análise SWOT")
swot_data = list_swot(ppg_id)
for categoria, titulo in {
    "forcas": "Forças",
    "fraquezas": "Fraquezas",
    "oportunidades": "Oportunidades",
    "ameacas": "Ameaças",
}.items():
    st.markdown(f"### {titulo}")
    itens = swot_data.get(categoria, [])
    if itens:
        for item in itens:
            cols = st.columns([4, 1])
            cols[0].write(item.get("descricao", ""))
            if cols[1].button("Remover", key=f"del_swot_{item['id']}"):
                delete_record("swot", item["id"])
                _refresh()
    else:
        st.write("Sem registros")

with st.form("form_swot"):
    categoria = st.selectbox(
        "Categoria",
        ["forcas", "fraquezas", "oportunidades", "ameacas"],
        format_func=lambda c: c.capitalize(),
    )
    descricao = st.text_area("Descrição da entrada")
    submitted_swot = st.form_submit_button("Adicionar entrada")
if submitted_swot and descricao:
    upsert_record("swot", {"ppg_id": ppg_id, "categoria": categoria, "descricao": descricao})
    _refresh()

st.divider()

st.subheader("Objetivos estratégicos")
objetivos = list_objetivos(ppg_id)
if objetivos:
    for obj in objetivos:
        cols = st.columns([4, 1])
        cols[0].write(f"{obj.get('ordem', '-')}. {obj.get('descricao', '')}")
        if cols[1].button("Remover", key=f"del_obj_{obj['id']}"):
            delete_record("objetivos", obj["id"])
            _refresh()
else:
    st.info("Nenhum objetivo cadastrado.")

with st.form("form_objetivo"):
    ordem = st.number_input("Ordem", min_value=1, value=len(objetivos) + 1)
    descricao_obj = st.text_area("Descrição do objetivo")
    submitted_obj = st.form_submit_button("Adicionar objetivo")
if submitted_obj and descricao_obj:
    upsert_record("objetivos", {"ppg_id": ppg_id, "ordem": int(ordem), "descricao": descricao_obj})
    _refresh()

st.divider()

st.subheader("Fichas de avaliação e critérios")
fichas = list_fichas(ppg_id)
if fichas:
    ficha_options = {ficha["nome"]: ficha for ficha in fichas}
    ficha_nome = st.selectbox("Ficha", list(ficha_options.keys()))
    ficha = ficha_options[ficha_nome]
    criterios = list_criterios(ficha["id"])
    if criterios:
        st.table({"Critério": [c.get("descricao") for c in criterios], "Peso": [c.get("peso") for c in criterios]})
        for criterio in criterios:
            if st.button("Remover critério", key=f"del_criterio_{criterio['id']}"):
                delete_record("ficha_criterios", criterio["id"])
                _refresh()
    else:
        st.info("Nenhum critério para esta ficha.")

    with st.form("form_criterio"):
        descricao = st.text_input("Descrição do critério")
        peso = st.number_input("Peso", min_value=0.0, value=1.0)
        ordem = st.number_input("Ordem", min_value=1, value=len(criterios) + 1)
        submitted_criterio = st.form_submit_button("Adicionar critério")
    if submitted_criterio and descricao:
        upsert_record(
            "ficha_criterios",
            {
                "ficha_id": ficha["id"],
                "descricao": descricao,
                "peso": peso,
                "ordem": int(ordem),
            },
        )
        _refresh()
else:
    st.info("Cadastre a primeira ficha para liberar os critérios.")

with st.form("form_ficha"):
    nome_ficha = st.text_input("Nome da ficha")
    submitted_ficha = st.form_submit_button("Criar ficha")
if submitted_ficha and nome_ficha:
    upsert_record("fichas", {"ppg_id": ppg_id, "nome": nome_ficha})
    _refresh()
