# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from provider import (
    add_objective,
    add_research_line,
    add_swot_item,
    delete_generic,
    list_criteria,
    list_forms,
    list_objectives,
    list_ppg_memberships,
    list_research_lines,
    list_swot,
    remove_criterion,
    remove_objective,
    remove_research_line,
    remove_swot_item,
    upsert_criterion,
    upsert_form,
)
from rbac import can
from components.forms import user_creation_form


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


if can(role, "manage_users"):
    st.subheader("Usuários do PPG")
    memberships = list_ppg_memberships(ppg_id)
    if memberships:
        for membership in memberships:
            cols = st.columns([3, 2, 1])
            email = membership.get("email") or membership.get("user_id")
            cols[0].markdown(f"**{email or 'Usuário'}**\n\n`{membership.get('created_at', '')}`")
            cols[1].write(membership.get("role", "-").capitalize())
            if cols[2].button("Remover", key=f"del_membership_{membership['id']}"):
                delete_generic("ppg_memberships", membership["id"])
                _refresh()
    else:
        st.info("Nenhum usuário vinculado a este PPG.")

    if user_creation_form(ppg_id):
        _refresh()

    st.divider()

st.subheader("Linhas de pesquisa")
linhas = list_research_lines(ppg_id)
if linhas:
    for linha in linhas:
        cols = st.columns([3, 1])
        cols[0].write(f"**{linha.get('nome', 'Sem nome')}**\n\n{linha.get('descricao', '')}")
        if cols[1].button("Remover", key=f"del_linha_{linha['id']}"):
            remove_research_line(linha["id"])
            _refresh()
else:
    st.info("Nenhuma linha cadastrada.")

with st.form("form_linha"):
    nome = st.text_input("Nome da linha")
    descricao = st.text_area("Descrição")
    submitted = st.form_submit_button("Adicionar linha")
if submitted and nome:
    add_research_line(ppg_id, nome, descricao)
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
                remove_swot_item(item["id"])
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
    add_swot_item(ppg_id, categoria, descricao)
    _refresh()

st.divider()

st.subheader("Objetivos estratégicos")
objetivos = list_objectives(ppg_id)
if objetivos:
    for obj in objetivos:
        cols = st.columns([4, 1])
        cols[0].write(f"{obj.get('ordem', '-')}. {obj.get('descricao', '')}")
        if cols[1].button("Remover", key=f"del_obj_{obj['id']}"):
            remove_objective(obj["id"])
            _refresh()
else:
    st.info("Nenhum objetivo cadastrado.")

with st.form("form_objetivo"):
    ordem = st.number_input("Ordem", min_value=1, value=len(objetivos) + 1)
    descricao_obj = st.text_area("Descrição do objetivo")
    submitted_obj = st.form_submit_button("Adicionar objetivo")
if submitted_obj and descricao_obj:
    add_objective(ppg_id, int(ordem), descricao_obj)
    _refresh()

st.divider()

st.subheader("Fichas de avaliação e critérios")
fichas = list_forms(ppg_id, kind=None)
if fichas:
    ficha_options = {ficha["nome"]: ficha for ficha in fichas}
    ficha_nome = st.selectbox("Ficha", list(ficha_options.keys()))
    ficha = ficha_options[ficha_nome]
    criterios = list_criteria(ficha["id"])
    if criterios:
        st.table({"Critério": [c.get("descricao") for c in criterios], "Peso": [c.get("peso") for c in criterios]})
        for criterio in criterios:
            if st.button("Remover critério", key=f"del_criterio_{criterio['id']}"):
                remove_criterion(criterio["id"])
                _refresh()
    else:
        st.info("Nenhum critério para esta ficha.")

    with st.form("form_criterio"):
        descricao = st.text_input("Descrição do critério")
        peso = st.number_input("Peso", min_value=0.0, value=1.0)
        ordem = st.number_input("Ordem", min_value=1, value=len(criterios) + 1)
        submitted_criterio = st.form_submit_button("Adicionar critério")
    if submitted_criterio and descricao:
        upsert_criterion(ficha["id"], descricao, peso, int(ordem))
        _refresh()
else:
    st.info("Cadastre a primeira ficha para liberar os critérios.")

with st.form("form_ficha"):
    nome_ficha = st.text_input("Nome da ficha")
    submitted_ficha = st.form_submit_button("Criar ficha")
if submitted_ficha and nome_ficha:
    upsert_form(ppg_id, nome_ficha)
    _refresh()
