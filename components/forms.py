"""Reusable Streamlit form helpers."""
from __future__ import annotations

from typing import Dict, Iterable

import streamlit as st

from data import create_article, create_avaliacao, create_ptt


def article_form(ppg_id: str) -> None:
    with st.form("article_form"):
        st.subheader("Cadastrar artigo")
        titulo = st.text_input("Título")
        autores = st.text_input("Autores")
        ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2024)
        status = st.selectbox("Status", ["Em andamento", "Submetido", "Publicado"])
        submitted = st.form_submit_button("Salvar artigo")
    if submitted:
        try:
            create_article(ppg_id, titulo, autores, int(ano), status)
            st.success("Artigo salvo com sucesso.")
        except Exception as exc:
            st.error(f"Erro ao salvar artigo: {exc}")


def ptt_form(ppg_id: str) -> None:
    with st.form("ptt_form"):
        st.subheader("Cadastrar PTT")
        tema = st.text_input("Tema")
        responsavel = st.text_input("Responsável")
        status = st.selectbox("Status", ["Rascunho", "Em revisão", "Aprovado"])
        submitted = st.form_submit_button("Salvar PTT")
    if submitted:
        try:
            create_ptt(ppg_id, tema, responsavel, status)
            st.success("PTT salvo com sucesso.")
        except Exception as exc:
            st.error(f"Erro ao salvar PTT: {exc}")


def evaluation_form(ppg_id: str, ficha_id: str, avaliador_id: str, criterios: Iterable[Dict[str, str]]) -> None:
    with st.form("avaliacao_form"):
        st.subheader("Lançar avaliação")
        avaliavel = st.text_input("Objeto avaliado")
        notas: Dict[str, float] = {}
        for criterio in criterios:
            cid = criterio.get("id")
            descricao = criterio.get("descricao")
            peso = criterio.get("peso", 1)
            notas[cid] = st.slider(
                f"{descricao} (peso {peso})",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
            )
        submitted = st.form_submit_button("Salvar avaliação")
    if submitted:
        try:
            avaliacao = create_avaliacao(ppg_id, ficha_id, avaliador_id, avaliavel, notas)
            st.success(f"Avaliação registrada. Nota total: {avaliacao['total']:.2f}")
        except Exception as exc:
            st.error(f"Erro ao salvar avaliação: {exc}")
