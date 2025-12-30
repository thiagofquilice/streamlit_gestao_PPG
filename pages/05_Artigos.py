# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import streamlit as st

from demo_context import current_ppg, current_profile
from data import (
    evaluation_stats,
    list_articles,
    list_dissertations,
    list_ppg_members,
    list_projects,
    list_research_lines,
    list_target_evaluations,
    upsert_article,
)
from ui_style import apply_modern_white_theme

ensure_demo_db()
apply_modern_white_theme()

STATUS_OPTIONS = ["planejado", "em_execucao", "concluido"]


def status_selector(label: str, value: str | None, key: str) -> str:
    default_value = value if value in STATUS_OPTIONS else STATUS_OPTIONS[0]
    segmented = getattr(st, "segmented_control", None)
    if segmented:
        return segmented(label, STATUS_OPTIONS, default=default_value, key=key)
    return st.radio(label, STATUS_OPTIONS, horizontal=True, index=STATUS_OPTIONS.index(default_value), key=key)

st.title("Artigos")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

can_create_eval = role in ("coordenador", "orientador")

projects = {p["id"]: p.get("name") for p in list_projects(ppg_id)}
lines = {line["id"]: line.get("name") for line in list_research_lines(ppg_id)}
disserts = {d["id"]: d.get("title") for d in list_dissertations(ppg_id)}
people = {m["user_id"]: m.get("display_name") or m.get("label") or m["user_id"] for m in list_ppg_members(ppg_id)}

articles = list_articles(ppg_id)
if not articles:
    st.info("Nenhum artigo cadastrado para este PPG.")
    st.stop()

for article in articles:
    with st.expander(article.get("title") or "(Sem título)", expanded=False):
        st.write(article.get("summary") or "Sem resumo")
        st.caption(
            f"Projeto: {projects.get(article.get('project_id')) or 'Sem projeto'} | "
            f"Linha: {lines.get(article.get('line_id')) or 'Sem linha'} | Ano: {article.get('year') or 'N/A'}"
        )
        st.caption(
            f"Status: {article.get('status') or 'planejado'} | Dissertação: {disserts.get(article.get('dissertation_id')) or 'Sem vínculo'}"
        )

        with st.form(f"article-status-{article['id']}"):
            status = status_selector("Status", article.get("status"), key=f"article-status-control-{article['id']}")
            submitted_status = st.form_submit_button("Atualizar status", use_container_width=True)

        if submitted_status:
            upsert_article({**article, "status": status})
            st.success("Status do artigo atualizado.")
            st.rerun()

        count, avg, last_score, last_date = evaluation_stats("article", article["id"])
        st.markdown(
            f"**Avaliações vinculadas:** {count}" + (f" | média: {avg}" if avg is not None else "")
            + (f" | última: {last_score} ({last_date})" if last_score is not None else "")
        )

        st.markdown("**Avaliações**")
        evaluations = sorted(
            list_target_evaluations("article", article["id"]), key=lambda ev: ev.get("created_at", ""), reverse=True
        )
        for ev in evaluations:
            st.write(
                f"Nota final: {ev.get('final_score')} | Data: {ev.get('created_at', 'N/A')} | "
                f"Avaliador: {people.get(ev.get('evaluator_id'), ev.get('evaluator_id', '-'))}"
            )
            if ev.get("notes"):
                st.caption(ev.get("notes"))

        if can_create_eval:
            st.page_link("pages/07_Avaliações.py", label="Criar avaliação", icon="✏️")
        else:
            st.info("Perfil atual permite apenas visualizar avaliações.")
