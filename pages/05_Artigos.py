# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import streamlit as st

from layout import configure_page, render_sidebar
from components.evaluation_section import render_evaluation_section

from demo_context import current_ppg, current_profile, current_person
from data import (
    list_articles,
    list_dissertations,
    list_ppg_members,
    list_projects,
    list_research_lines,
    get_admin_form,
    upsert_article,
)

from rbac import can
from status_utils import (
    available_filter_labels,
    filter_label_to_key,
    selector_default_label,
    selector_label_to_key,
    selector_labels,
    status_label,
)

ensure_demo_db()

configure_page()
render_sidebar()

def status_selector(label: str, value: str | None, key: str) -> str:
    options = selector_labels()
    default_value = selector_default_label(value)
    segmented = getattr(st, "segmented_control", None)
    if segmented:
        selected = segmented(label, options, default=default_value, key=key)
    else:
        selected = st.radio(label, options, horizontal=True, index=options.index(default_value), key=key)
    return selector_label_to_key(selected)

st.title("Artigos")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

can_create_eval = role in ("coordenador", "orientador")
can_create = can("criar")
can_edit = can("editar")

projects = {p["id"]: p.get("name") for p in list_projects(ppg_id)}
lines = {line["id"]: line.get("name") for line in list_research_lines(ppg_id)}
disserts = {d["id"]: d.get("title") for d in list_dissertations(ppg_id)}
people = {m["user_id"]: m.get("display_name") or m.get("label") or m["user_id"] for m in list_ppg_members(ppg_id)}

articles = list_articles(ppg_id)
form_articles = get_admin_form("articles")
journal_rating_options = form_articles.get("journal_ratings") or ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"]

if not articles:
    st.info("Nenhum artigo cadastrado para este PPG.")

status_filter_options = available_filter_labels(article.get("status") for article in articles if article.get("status"))
status_filter = st.selectbox("Filtrar por status", ["Todos"] + status_filter_options, index=0)
filtered_articles = articles
selected_filter_key = filter_label_to_key(status_filter)
if selected_filter_key is not None:
    filtered_articles = [article for article in articles if (article.get("status") or "") == selected_filter_key]

for article in filtered_articles:
    title_with_status = f"{article.get('title') or '(Sem título)'} | Status: {status_label(article.get('status'))}"
    with st.expander(title_with_status, expanded=False):
        st.write(article.get("summary") or "Sem resumo")
        st.caption(
            f"Projeto: {projects.get(article.get('project_id')) or 'Sem projeto'} | "
            f"Linha: {lines.get(article.get('line_id')) or 'Sem linha'} | Ano: {article.get('year') or 'N/A'}"
        )
        st.caption(
            f"Status: {status_label(article.get('status'))} | Dissertação: {disserts.get(article.get('dissertation_id')) or 'Sem vínculo'}"
        )
        st.caption(
            f"Classificação para submissão: {article.get('journal_target_rating') or 'N/A'} | "
            f"Classificação da revista publicada: {article.get('journal_published_rating') or 'N/A'}"
        )

        if can_edit:
            with st.form(f"article-edit-{article['id']}"):
                status = status_selector("Status", article.get("status"), key=f"article-status-control-{article['id']}")
                target_index = journal_rating_options.index(article.get("journal_target_rating")) if article.get("journal_target_rating") in journal_rating_options else 0
                journal_target_rating = st.selectbox(
                    "Classificação da revista (execução/planejamento)",
                    journal_rating_options,
                    index=target_index,
                    key=f"article-target-rating-{article['id']}",
                )
                published_index = journal_rating_options.index(article.get("journal_published_rating")) if article.get("journal_published_rating") in journal_rating_options else 0
                journal_published_rating = st.selectbox(
                    "Classificação da revista publicada (conclusão)",
                    journal_rating_options,
                    index=published_index,
                    key=f"article-published-rating-{article['id']}",
                )
                submitted_status = st.form_submit_button("Salvar dados", use_container_width=True)

            if submitted_status:
                updated = {
                    **article,
                    "status": status,
                    "journal_target_rating": journal_target_rating,
                    "journal_published_rating": journal_published_rating if status == "concluido" else None,
                }
                if status == "concluido" and not journal_published_rating:
                    st.error("Informe a classificação da revista publicada para concluir o artigo.")
                else:
                    try:
                        upsert_article(updated)
                        st.success("Dados do artigo atualizados.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

        render_evaluation_section(
            ppg_id=ppg_id,
            target_type="article",
            target_id=article["id"],
            form_key="articles",
            can_manage=can_create_eval,
            people=people,
            evaluator_id=current_person(),
        )


if can_create:
    st.divider()
    st.subheader("Cadastrar novo artigo")
    with st.form("form-article"):
        title = st.text_input("Título")
        summary = st.text_area("Resumo")
        year = st.number_input("Ano", min_value=1900, max_value=2100, value=2024, step=1)
        project_id = st.selectbox(
            "Projeto",
            list(projects.keys()),
            format_func=lambda pid: projects.get(pid, "Projeto inválido"),
        )
        line_id = st.selectbox(
            "Linha (opcional)",
            [None] + list(lines.keys()),
            format_func=lambda lid: lines.get(lid, "Sem linha") if lid else "Sem linha",
        )
        dissertation_id = st.selectbox(
            "Dissertação (opcional)",
            [None] + list(disserts.keys()),
            format_func=lambda did: disserts.get(did, "Sem vínculo") if did else "Sem vínculo",
        )
        status = status_selector("Status", None, key="article-status-new")
        journal_target_rating = st.selectbox("Classificação da revista (execução/planejamento)", journal_rating_options, key="article-target-rating-new")
        journal_published_rating = st.selectbox("Classificação da revista publicada (conclusão)", journal_rating_options, key="article-published-rating-new")
        submitted = st.form_submit_button("Salvar", use_container_width=True)

    if submitted and title:
        if status == "concluido" and not journal_published_rating:
            st.error("Um artigo só pode ser concluído quando publicado. Informe a classificação da revista publicada.")
        else:
            try:
                upsert_article(
                    {
                        "ppg_id": ppg_id,
                        "title": title,
                        "summary": summary,
                        "year": int(year),
                        "project_id": project_id,
                        "line_id": line_id,
                        "dissertation_id": dissertation_id,
                        "status": status,
                        "journal_target_rating": journal_target_rating,
                        "journal_published_rating": journal_published_rating if status == "concluido" else None,
                    }
                )
                st.success("Artigo salvo.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
elif not articles:
    st.info("Seu perfil não permite cadastrar artigos.")
