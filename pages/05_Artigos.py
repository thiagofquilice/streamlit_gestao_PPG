# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_articles, upsert_article
from rbac import can

st.title("Artigos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

can_create = can("criar")

artigos = list_articles(ppg_id)
if artigos:
    st.subheader("Artigos cadastrados")
    df = pd.DataFrame(artigos)
    st.dataframe(df, use_container_width=True)
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
        submitted = st.form_submit_button("Salvar")
    if submitted and titulo:
        upsert_article({"ppg_id": ppg_id, "title": titulo, "authors": autores, "year": int(ano), "status": status})
        st.success("Artigo salvo com sucesso.")
        st.experimental_rerun()
else:
    st.info("Seu perfil não permite cadastrar artigos.")
