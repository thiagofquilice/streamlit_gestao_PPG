# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Tuple

import streamlit as st

from data import (
    list_articles,
    list_dissertations,
    list_ppg_members,
    list_projects,
    list_research_lines,
    list_target_evaluations,
    upsert_article,
)
from demo_context import current_ppg, current_profile
from demo_seed import ensure_demo_db


def _evaluation_summary(target_id: str) -> Tuple[int, float | None, float | None]:
    evaluations = list_target_evaluations("article", target_id)
    if not evaluations:
        return 0, None, None
    scores = [ev.get("final_score", 0) for ev in evaluations]
    avg_score = round(sum(scores) / len(scores), 2)
    latest = sorted(evaluations, key=lambda ev: ev.get("created_at", ""))[-1]
    return len(evaluations), avg_score, latest.get("final_score")


ensure_demo_db()

st.title("Artigos")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

can_create = role in ("coordenador", "orientador", "mestrando")
can_edit = role in ("coordenador", "orientador", "mestrando")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}

lines = list_research_lines(ppg_id)
line_options = {line["id"]: line.get("name") for line in lines}

members = list_ppg_members(ppg_id)
orientadores = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "orientador"}
mestrandos = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "mestrando"}


items = list_articles(ppg_id)

if items:
    st.subheader("Artigos cadastrados")
    for article in items:
        eval_count, avg_score, last_score = _evaluation_summary(article["id"])
        with st.expander(article.get("title") or "(Sem título)", expanded=False):
            st.write(article.get("summary") or "Sem resumo")
            st.caption(f"Projeto: {project_options.get(article.get('project_id')) or 'Sem projeto'}")
            st.caption(f"Linha: {line_options.get(article.get('line_id')) or 'Sem linha'} | Ano: {article.get('year') or 'N/A'}")
            st.caption(
                "Avaliações vinculadas: "
                f"{eval_count}"
                + (f" | média: {avg_score}" if avg_score is not None else "")
                + (f" | última: {last_score}" if last_score is not None else "")
            )
            st.info("Veja detalhes na aba Avaliações.")

            st.write(
                "Orientador:", orientadores.get(article.get("orientador_id")) or "Não definido",
            )
            st.write("Mestrando:", mestrandos.get(article.get("mestrando_id")) or "Não definido")

            if can_edit:
                with st.form(f"edit-article-{article['id']}"):
                    title = st.text_input("Título", value=article.get("title", ""))
                    summary = st.text_area("Resumo", value=article.get("summary") or "")
                    autores = st.text_input("Autores (texto livre)", value=article.get("autores_texto") or "")
                    ano = st.number_input(
                        "Ano", min_value=1900, max_value=2100, value=int(article.get("year") or 2024), step=1
                    )
                    status = st.selectbox(
                        "Status",
                        ["rascunho", "submetido", "publicado"],
                        index=["rascunho", "submetido", "publicado"].index(article.get("status", "rascunho")),
                    )
                    project_id = st.selectbox(
                        "Projeto (opcional)",
                        [None] + list(project_options.keys()),
                        format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
                        index=([None] + list(project_options.keys())).index(article.get("project_id"))
                        if article.get("project_id") in project_options
                        else 0,
                    )
                    line_id = st.selectbox(
                        "Linha (opcional)",
                        [None] + list(line_options.keys()),
                        format_func=lambda lid: line_options.get(lid, "Sem linha") if lid else "Sem linha",
                        index=([None] + list(line_options.keys())).index(article.get("line_id"))
                        if article.get("line_id") in line_options
                        else 0,
                    )
                    orientador_id = st.selectbox(
                        "Orientador (opcional)",
                        [None] + list(orientadores.keys()),
                        format_func=lambda uid: orientadores.get(uid, "Sem orientador") if uid else "Sem orientador",
                        index=([None] + list(orientadores.keys())).index(article.get("orientador_id"))
                        if article.get("orientador_id") in orientadores
                        else 0,
                    )
                    mestrando_id = st.selectbox(
                        "Mestrando (opcional)",
                        [None] + list(mestrandos.keys()),
                        format_func=lambda uid: mestrandos.get(uid, "Sem mestrando") if uid else "Sem mestrando",
                        index=([None] + list(mestrandos.keys())).index(article.get("mestrando_id"))
                        if article.get("mestrando_id") in mestrandos
                        else 0,
                    )
                    dissertações = list_dissertations(ppg_id)
                    diss_options = {d["id"]: d.get("title") for d in dissertações}
                    diss_id = st.selectbox(
                        "Dissertação (opcional)",
                        [None] + list(diss_options.keys()),
                        format_func=lambda did: diss_options.get(did, "Sem dissertação") if did else "Sem dissertação",
                        index=([None] + list(diss_options.keys())).index(article.get("dissertation_id"))
                        if article.get("dissertation_id") in diss_options
                        else 0,
                    )

                    submitted = st.form_submit_button("Salvar alterações")
                if submitted:
                    upsert_article(
                        {
                            "id": article["id"],
                            "ppg_id": ppg_id,
                            "title": title,
                            "summary": summary,
                            "autores_texto": autores,
                            "year": int(ano),
                            "status": status,
                            "project_id": project_id,
                            "line_id": line_id,
                            "orientador_id": orientador_id,
                            "mestrando_id": mestrando_id,
                            "dissertation_id": diss_id,
                        }
                    )
                    st.success("Artigo atualizado.")
                    st.rerun()
else:
    st.info("Nenhum artigo cadastrado para este PPG.")

if can_create:
    st.divider()
    st.subheader("Cadastrar novo artigo")
    with st.form("form_artigo"):
        titulo = st.text_input("Título")
        resumo = st.text_area("Resumo")
        autores = st.text_input("Autores (texto livre)")
        ano = st.number_input("Ano", min_value=1900, max_value=2100, value=2024, step=1)
        status = st.selectbox("Status", ["rascunho", "submetido", "publicado"])
        project_id = st.selectbox(
            "Projeto (opcional)",
            [None] + list(project_options.keys()),
            format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
        )
        line_id = st.selectbox(
            "Linha (opcional)",
            [None] + list(line_options.keys()),
            format_func=lambda lid: line_options.get(lid, "Sem linha") if lid else "Sem linha",
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
        dissertações = list_dissertations(ppg_id)
        diss_options = {d["id"]: d.get("title") for d in dissertações}
        diss_id = st.selectbox(
            "Dissertação (opcional)",
            [None] + list(diss_options.keys()),
            format_func=lambda did: diss_options.get(did, "Sem dissertação") if did else "Sem dissertação",
        )
        submitted = st.form_submit_button("Salvar")
    if submitted and titulo:
        upsert_article(
            {
                "ppg_id": ppg_id,
                "title": titulo,
                "summary": resumo,
                "autores_texto": autores,
                "year": int(ano),
                "status": status,
                "project_id": project_id,
                "line_id": line_id,
                "orientador_id": orientador_id,
                "mestrando_id": mestrando_id,
                "dissertation_id": diss_id,
            }
        )
        st.success("Artigo salvo com sucesso.")
        st.rerun()
else:
    st.info("Seu perfil não permite cadastrar artigos.")
