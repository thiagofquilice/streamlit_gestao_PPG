# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_articles, list_ppg_members, list_projects, upsert_article
from rbac import can

st.title("Artigos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

can_create = can("criar")
can_edit = can("editar")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}

members = list_ppg_members(ppg_id)
orientadores = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "orientador"}
mestrandos = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "mestrando"}

artigos = list_articles(ppg_id)
if artigos:
    st.subheader("Artigos cadastrados")
    df_rows = []
    for a in artigos:
        df_rows.append(
            {
                "Título": a.get("title"),
                "Projeto": project_options.get(a.get("project_id"), ""),
                "Orientador": orientadores.get(a.get("orientador_user_id"), ""),
                "Mestrando": mestrandos.get(a.get("mestrando_user_id"), ""),
                "Status": a.get("status"),
                "Ano": a.get("year"),
            }
        )
    st.dataframe(pd.DataFrame(df_rows), use_container_width=True)

    if can_edit:
        st.divider()
        st.subheader("Editar artigos")
        status_options = ["rascunho", "submetido", "publicado"]
        for a in artigos:
            with st.form(f"edit_article_{a['id']}"):
                st.caption(f"Editar: {a.get('title')}")
                titulo = st.text_input("Título", value=a.get("title", ""))
                autores = st.text_input("Autores", value=a.get("authors") or "")
                ano = st.number_input(
                    "Ano",
                    min_value=1900,
                    max_value=2100,
                    value=int(a.get("year") or 2024),
                    step=1,
                )
                status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(a.get("status")) if a.get("status") in status_options else 0,
                )
                projeto_id = st.selectbox(
                    "Projeto (opcional)",
                    [None] + list(project_options.keys()),
                    format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
                    index=([None] + list(project_options.keys())).index(a.get("project_id"))
                    if a.get("project_id") in project_options
                    else 0,
                )
                orientador_id = st.selectbox(
                    "Orientador (opcional)",
                    [None] + list(orientadores.keys()),
                    format_func=lambda uid: orientadores.get(uid, "Sem orientador") if uid else "Sem orientador",
                    index=([None] + list(orientadores.keys())).index(a.get("orientador_user_id"))
                    if a.get("orientador_user_id") in orientadores
                    else 0,
                )
                mestrando_id = st.selectbox(
                    "Mestrando (opcional)",
                    [None] + list(mestrandos.keys()),
                    format_func=lambda uid: mestrandos.get(uid, "Sem mestrando") if uid else "Sem mestrando",
                    index=([None] + list(mestrandos.keys())).index(a.get("mestrando_user_id"))
                    if a.get("mestrando_user_id") in mestrandos
                    else 0,
                )
                submitted = st.form_submit_button("Salvar artigo")
            if submitted:
                payload = {
                    "id": a["id"],
                    "ppg_id": ppg_id,
                    "title": titulo,
                    "authors": autores,
                    "year": int(ano),
                    "status": status,
                    "project_id": projeto_id,
                    "orientador_user_id": orientador_id,
                    "mestrando_user_id": mestrando_id,
                }
                upsert_article(payload)
                st.success("Artigo atualizado.")
                st.experimental_rerun()
else:
    st.info("Nenhum artigo cadastrado para este PPG.")

if can_create:
    st.divider()
    st.subheader("Cadastrar novo artigo")
    with st.form("form_artigo"):
        titulo = st.text_input("Título")
        autores = st.text_input("Autores")
        ano = st.number_input("Ano", min_value=1900, max_value=2100, value=2024, step=1)
        status = st.selectbox("Status", ["rascunho", "submetido", "publicado"])
        projeto_id = st.selectbox(
            "Projeto (opcional)",
            [None] + list(project_options.keys()),
            format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
        )
        orientador_id = st.selectbox(
            "Orientador (opcional)",
            [None] + list(orientadores.keys()),
            format_func=lambda uid: orientadores.get(uid, "Sem orientador") if uid else "Sem orientador",
        )
        mestrando_id = st.selectbox(
            "Mestrando (opcional)",
            [None] + list(mestrandos.keys()),
            format_func=lambda uid: mestrandos.get(uid, "Sem mestrando") if uid else "Sem mestrando",
        )
        submitted = st.form_submit_button("Salvar")
    if submitted and titulo:
        upsert_article(
            {
                "ppg_id": ppg_id,
                "title": titulo,
                "authors": autores,
                "year": int(ano),
                "status": status,
                "project_id": projeto_id,
                "orientador_user_id": orientador_id,
                "mestrando_user_id": mestrando_id,
            }
        )
        st.success("Artigo salvo com sucesso.")
        st.experimental_rerun()
else:
    st.info("Seu perfil não permite cadastrar artigos.")
