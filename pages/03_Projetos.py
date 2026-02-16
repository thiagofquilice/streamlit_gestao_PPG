# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from demo_context import current_ppg, current_profile, current_person
from demo_seed import ensure_demo_db
from data import (
    create_project,
    update_project,
    list_ppg_members,
    list_project_articles,
    list_project_dissertations,
    list_project_ptts,
    list_projects,
    list_research_lines,
)
from layout import configure_page, render_sidebar
from navigation_utils import navigate_to
from status_utils import (
    available_filter_labels,
    filter_label_to_key,
    selector_label_to_key,
    selector_labels,
    status_label,
)

ensure_demo_db()

configure_page()
render_sidebar()

st.title("Projetos")
st.info(
    "A associação de Dissertações, Artigos e PTTs às Linhas de Pesquisa e aos Projetos deve ser feita "
    "nos respectivos menus na coluna de navegação."
)

if "show_add_project_form" not in st.session_state:
    st.session_state.show_add_project_form = False

ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

lines = list_research_lines(ppg_id)
members = list_ppg_members(ppg_id)
member_labels = {m["user_id"]: m.get("label") or m.get("display_name") or m.get("name") or m["user_id"] for m in members}

projects = list_projects(ppg_id)
if not projects:
    st.info("Nenhum projeto cadastrado para este PPG.")

project_statuses = available_filter_labels(p.get("status") for p in projects if p.get("status"))
project_status_filter = st.selectbox(
    "Filtrar por status",
    options=["Todos"] + project_statuses,
    index=0,
)
filtered_projects = projects
selected_filter_key = filter_label_to_key(project_status_filter)
if selected_filter_key is not None:
    filtered_projects = [p for p in projects if (p.get("status") or "") == selected_filter_key]

st.caption(
    "Visualização no DEMO. Cada projeto mostra vínculos com orientadores, mestrandos, dissertações, artigos e PTTs."
)


current_person_id = current_person()


def _can_edit_project(project: Dict[str, Any]) -> bool:
    if role == "coordenador":
        return True
    if role != "orientador" or not current_person_id:
        return False
    linked_orientador = current_person_id in (project.get("orientadores_ids") or [])
    created_by_me = project.get("created_by") == current_person_id
    return linked_orientador or created_by_me




def _render_entity_links(items: List[Dict[str, Any]], label_key: str, page_path: str, target_type: str, prefix: str) -> None:
    if not items:
        st.caption("Nenhum item vinculado.")
        return
    for idx, item in enumerate(items):
        item_id = item.get("id")
        label = item.get(label_key) or item_id or "(Sem título)"
        if st.button(label, key=f"{prefix}-{item_id or idx}", type="secondary"):
            navigate_to(page_path, target_type, item_id)


def _render_project_tabs(project: Dict[str, Any]) -> None:
    project_mestrandos = [m for m in members if m.get("role") == "mestrando" and m.get("id") in (project.get("mestrandos_ids") or [])]
    project_dissertations = list_project_dissertations(project["id"])
    project_articles = list_project_articles(project["id"])
    project_ptts = list_project_ptts(project["id"])

    tabs = st.tabs(["Mestrandos", "Dissertações", "Artigos", "PTTs"])

    with tabs[0]:
        _render_entity_links(project_mestrandos, "name", "pages/10_Cadastro_de_pessoal.py", "person", f"proj-mestrando-{project.get('id')}")
        if project_mestrandos:
            mestrandos_df = pd.DataFrame(
                [
                    {
                        "Nome": m.get("name"),
                        "Situação": m.get("status", "-"),
                        "Orientador": member_labels.get(m.get("orientador_id"), m.get("orientador_id") or "-"),
                    }
                    for m in project_mestrandos
                ]
            )
            st.dataframe(mestrandos_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sem mestrandos vinculados ao projeto.")

    with tabs[1]:
        _render_entity_links(project_dissertations, "title", "pages/04_Dissertações.py", "dissertation", f"proj-diss-{project.get('id')}")
        if project_dissertations:
            dissertations_df = pd.DataFrame(
                [
                    {
                        "Título": d.get("title"),
                        "Ano": d.get("year", "-"),
                        "Status": status_label(d.get("status")),
                    }
                    for d in project_dissertations
                ]
            )
            st.dataframe(dissertations_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sem dissertações vinculadas ao projeto.")

    with tabs[2]:
        _render_entity_links(project_articles, "title", "pages/05_Artigos.py", "article", f"proj-article-{project.get('id')}")
        if project_articles:
            articles_df = pd.DataFrame(
                [
                    {
                        "Título": a.get("title"),
                        "Ano": a.get("year", "-"),
                        "Status": status_label(a.get("status")),
                    }
                    for a in project_articles
                ]
            )
            st.dataframe(articles_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sem artigos vinculados ao projeto.")

    with tabs[3]:
        _render_entity_links(project_ptts, "title", "pages/06_PTTs.py", "ptt", f"proj-ptt-{project.get('id')}")
        if project_ptts:
            ptts_df = pd.DataFrame(
                [
                    {
                        "Título": p.get("title"),
                        "Tipo": p.get("tipo_ptt") or "-",
                        "Ano": p.get("year", "-"),
                        "Status": status_label(p.get("status")),
                    }
                    for p in project_ptts
                ]
            )
            st.dataframe(ptts_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sem PTTs vinculados ao projeto.")


def _render_project_card(project: Dict[str, Any]) -> None:
    project_mestrandos = [m for m in members if m.get("role") == "mestrando" and m.get("id") in (project.get("mestrandos_ids") or [])]
    project_dissertations = list_project_dissertations(project["id"])
    project_articles = list_project_articles(project["id"])
    project_ptts = list_project_ptts(project["id"])

    docentes_proj = [member_labels.get(person_id, person_id) for person_id in project.get("orientadores_ids", [])]
    title = project.get("name") or "Projeto sem título"
    period = f"{project.get('start_date', '-')} → {project.get('end_date', '-')}"
    header = (
        f"{title} | Status: {status_label(project.get('status'))} | Período: {period} | "
        f"Mestrandos: {len(project_mestrandos)} | Dissertações: {len(project_dissertations)} | "
        f"Artigos: {len({a.get('id') for a in project_articles})} | PTTs: {len(project_ptts)}"
    )

    with st.container(border=True):
        st.markdown(f"**{header}**")
        st.caption(f"Docentes do projeto: {', '.join(docentes_proj) if docentes_proj else '-'}")
        if project.get("description"):
            st.write(project.get("description"))

        if _can_edit_project(project):
            with st.form(f"edit-project-{project['id']}"):
                edit_name = st.text_input("Nome do projeto", value=project.get("name") or "")
                edit_description = st.text_area("Descrição", value=project.get("description") or "")
                status_display = st.selectbox(
                    "Status",
                    selector_labels(),
                    index=selector_labels().index(status_label(project.get("status"))),
                    key=f"project-status-{project['id']}",
                )
                submitted = st.form_submit_button("Salvar alterações", use_container_width=True)
            if submitted and edit_name.strip():
                payload = {
                    **project,
                    "name": edit_name.strip(),
                    "description": edit_description.strip(),
                    "status": selector_label_to_key(status_display),
                }
                update_project(project["id"], payload)
                st.success("Projeto atualizado.")
                st.rerun()

        _render_project_tabs(project)


def _render_project_group(title: str, group_projects: List[Dict[str, Any]]) -> None:
    st.subheader(title)
    if not group_projects:
        st.caption("Nenhum projeto neste agrupamento.")
        return
    for project in group_projects:
        _render_project_card(project)


if projects:
    for line in lines:
        grouped_projects = [p for p in filtered_projects if p.get("line_id") == line.get("id")]
        _render_project_group(line.get("name") or "Linha sem nome", grouped_projects)

    unlinked_projects = [p for p in filtered_projects if not p.get("line_id")]
    _render_project_group("Projetos não vinculados a uma Linha de Pesquisa", unlinked_projects)

st.divider()
if role in ("coordenador", "orientador"):
    if st.button("Adicionar Projeto", use_container_width=True):
        st.session_state.show_add_project_form = not st.session_state.show_add_project_form

    if st.session_state.show_add_project_form:
        with st.form("add_project_form", clear_on_submit=True):
            name = st.text_input("Nome do Projeto")
            description = st.text_area("Descrição")
            status_display = st.selectbox("Status", selector_labels(), index=0)
            status = selector_label_to_key(status_display)
            line_options = {"Sem linha": None}
            for line in lines:
                label = line.get("name") or line.get("id") or "Linha sem nome"
                line_options[label] = line.get("id")
            selected_line = st.selectbox("Linha de Pesquisa", options=list(line_options.keys()))
            submit = st.form_submit_button("Salvar Projeto")

        if submit:
            if not name.strip():
                st.warning("Informe o nome do projeto.")
            else:
                line_id = line_options.get(selected_line)
                create_project(ppg_id, name.strip(), description.strip(), line_id, status, created_by=current_person_id)
                st.success("Projeto adicionado com sucesso.")
                st.session_state.show_add_project_form = False
                st.rerun()
else:
    st.info("Seu perfil atual permite apenas consulta.")
