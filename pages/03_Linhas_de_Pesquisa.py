# -*- coding: utf-8 -*-
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple

import pandas as pd
import streamlit as st

from demo_context import current_ppg
from demo_seed import ensure_demo_db
from demo_store import get_db
from data import add_research_line
from layout import configure_page, render_sidebar

ensure_demo_db()

configure_page("Linhas de Pesquisa")
render_sidebar()

st.title("Linhas de Pesquisa")
st.info(
    "A associação de Dissertações, Artigos e PTTs às Linhas de Pesquisa e aos Projetos deve ser feita "
    "nos respectivos menus na coluna de navegação."
)

if "show_add_line_form_linhas" not in st.session_state:
    st.session_state.show_add_line_form_linhas = False


@st.cache_data(show_spinner=False)
def _load_ppg_snapshot(ppg_id: str) -> Dict[str, List[Dict[str, Any]]]:
    db = get_db()
    keys = ["research_lines", "people", "projects", "dissertations", "articles", "ptts"]
    return {key: [row.copy() for row in db.get(key, []) if row.get("ppg_id") == ppg_id] for key in keys}


def _person_name(people_map: Dict[str, Dict[str, Any]], person_id: str | None) -> str:
    if not person_id:
        return "-"
    person = people_map.get(person_id)
    return (person or {}).get("name") or person_id


def _build_article_dissertation_links(dissertations: List[Dict[str, Any]], articles: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """Build many-to-many links (artigo_dissertacao) within a project.

    Artigo é entidade única do projeto; os vínculos com dissertação são uma relação N:N.
    Mantemos o artigo sem duplicidade e renderizamos os links por meio desta estrutura.
    """
    diss_ids = {d.get("id") for d in dissertations if d.get("id")}
    article_ids = {a.get("id") for a in articles if a.get("id")}
    links: Set[Tuple[str, str]] = set()

    for dissertation in dissertations:
        diss_id = dissertation.get("id")
        for article_id in dissertation.get("artigos_ids", []) or []:
            if diss_id and article_id in article_ids:
                links.add((article_id, diss_id))

    for article in articles:
        article_id = article.get("id")
        diss_id = article.get("dissertation_id")
        if article_id and diss_id in diss_ids:
            links.add((article_id, diss_id))

    return sorted(links)


def _line_docentes(line: Dict[str, Any], people: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    line_id = line.get("id")
    docentes: List[Dict[str, Any]] = []
    for person in people:
        if person.get("role") != "orientador":
            continue
        line_ids = set((person.get("linhas_ids") or []) + (person.get("linhas_de_pesquisa_ids") or []))
        if line_id and line_id in line_ids:
            docentes.append(person)

    permanentes: List[Dict[str, Any]] = []
    colaboradores: List[Dict[str, Any]] = []
    for docente in docentes:
        tipo = (docente.get("tipo") or docente.get("tipo_docente") or "permanente").lower()
        if tipo == "colaborador":
            colaboradores.append(docente)
        else:
            permanentes.append(docente)

    return permanentes, colaboradores


def _project_tabs(
    project: Dict[str, Any],
    project_mestrandos: List[Dict[str, Any]],
    project_dissertations: List[Dict[str, Any]],
    project_articles: List[Dict[str, Any]],
    project_ptts: List[Dict[str, Any]],
    link_pairs: List[Tuple[str, str]],
    people_map: Dict[str, Dict[str, Any]],
) -> None:
    article_to_dissertations: Dict[str, List[str]] = defaultdict(list)
    dissertation_to_articles: Dict[str, List[str]] = defaultdict(list)
    dissertation_to_article_statuses: Dict[str, List[str]] = defaultdict(list)
    dissertation_to_ptts: Dict[str, List[str]] = defaultdict(list)
    dissertation_to_ptt_statuses: Dict[str, List[str]] = defaultdict(list)

    diss_title_by_id = {d.get("id"): d.get("title") or d.get("id") for d in project_dissertations}
    article_title_by_id = {a.get("id"): a.get("title") or a.get("id") for a in project_articles}

    for article_id, dissertation_id in link_pairs:
        article_label = article_title_by_id.get(article_id, article_id)
        dissertation_label = diss_title_by_id.get(dissertation_id, dissertation_id)
        article_to_dissertations[article_id].append(dissertation_label)
        dissertation_to_articles[dissertation_id].append(article_label)

    article_status_by_id = {a.get("id"): a.get("status") or "planejado" for a in project_articles}
    for article_id, dissertation_id in link_pairs:
        if article_id and dissertation_id:
            dissertation_to_article_statuses[dissertation_id].append(article_status_by_id.get(article_id, "planejado"))

    for ptt in project_ptts:
        dissertation_id = ptt.get("dissertation_id")
        if not dissertation_id:
            continue
        dissertation_to_ptts[dissertation_id].append(ptt.get("title") or ptt.get("id") or "-")
        dissertation_to_ptt_statuses[dissertation_id].append(ptt.get("status") or "planejado")

    shared_articles = {aid for aid, diss_list in article_to_dissertations.items() if len(set(diss_list)) > 1}

    tabs = st.tabs(
        [
            "Mestrandos",
            "Dissertações",
            "Artigos",
            "PTTs",
            "Matriz (Dissertação × Artigo)",
            "Matriz (Dissertação × PTT)",
            "Matriz (Artigo × PTT)",
        ]
    )

    with tabs[0]:
        if project_mestrandos:
            mestrandos_df = pd.DataFrame(
                [
                    {
                        "Nome": m.get("name"),
                        "Situação": m.get("status", "-"),
                        "Orientador": _person_name(people_map, m.get("orientador_id")),
                    }
                    for m in project_mestrandos
                ]
            )
            st.dataframe(mestrandos_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sem mestrandos vinculados ao projeto.")

    with tabs[1]:
        if project_dissertations:
            rows = []
            for diss in project_dissertations:
                diss_id = diss.get("id")
                artigos = dissertation_to_articles.get(diss_id, [])
                rows.append(
                    {
                        "Discente": _person_name(people_map, diss.get("mestrando_id")),
                        "Título": diss.get("title"),
                        "Ano": diss.get("year", "-"),
                        "Status": diss.get("status", "-"),
                        "Artigos associados": ", ".join(artigos) if artigos else "-",
                        "Status dos artigos": ", ".join(dissertation_to_article_statuses.get(diss_id, [])) or "-",
                        "PTTs associados": ", ".join(dissertation_to_ptts.get(diss_id, [])) or "-",
                        "Status dos PTTs": ", ".join(dissertation_to_ptt_statuses.get(diss_id, [])) or "-",
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption("Artigos podem ser compartilhados entre dissertações pela relação N:N artigo_dissertacao.")
        else:
            st.info("Sem dissertações vinculadas ao projeto.")

    with tabs[2]:
        if project_articles:
            article_rows = []
            for article in project_articles:
                article_id = article.get("id")
                diss_list = article_to_dissertations.get(article_id, [])
                article_rows.append(
                    {
                        "Título": article.get("title"),
                        "Periódico": article.get("journal") or article.get("periodico") or "-",
                        "Ano": article.get("year", "-"),
                        "Associado a": ", ".join(diss_list) if diss_list else "-",
                        "Compartilhado": "Sim" if article_id in shared_articles else "Não",
                    }
                )
            st.dataframe(pd.DataFrame(article_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Sem artigos vinculados ao projeto.")

    with tabs[3]:
        if project_ptts:
            ptts_df = pd.DataFrame(
                [
                    {
                        "Título": ptt.get("title"),
                        "Tipo": ptt.get("tipo_ptt") or "-",
                        "Ano": ptt.get("year", "-"),
                        "Status": ptt.get("status", "-"),
                    }
                    for ptt in project_ptts
                ]
            )
            st.dataframe(ptts_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sem PTTs vinculados ao projeto.")

    with tabs[4]:
        if not project_dissertations or not project_articles:
            st.info("Matriz indisponível: é necessário ter ao menos uma dissertação e um artigo.")
        else:
            matrix_rows = []
            article_columns = [f"{a.get('title', a.get('id'))[:30]} ({a.get('year', '-')})" for a in project_articles]
            article_ids = [a.get("id") for a in project_articles]
            for diss in project_dissertations:
                row = {
                    "Dissertação": f"{(diss.get('title') or diss.get('id'))[:40]} — {_person_name(people_map, diss.get('mestrando_id'))}"
                }
                for col_label, art_id in zip(article_columns, article_ids):
                    row[col_label] = "✅" if (art_id, diss.get("id")) in link_pairs else ""
                matrix_rows.append(row)
            st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

    with tabs[5]:
        if not project_dissertations or not project_ptts:
            st.info("Matriz indisponível: é necessário ter ao menos uma dissertação e um PTT.")
        else:
            matrix_rows = []
            ptt_columns = [f"{p.get('title', p.get('id'))[:30]} ({p.get('year', '-')})" for p in project_ptts]
            ptt_dissertation_ids = [p.get("dissertation_id") for p in project_ptts]
            for diss in project_dissertations:
                row = {
                    "Dissertação": f"{(diss.get('title') or diss.get('id'))[:40]} — {_person_name(people_map, diss.get('mestrando_id'))}"
                }
                diss_id = diss.get("id")
                for col_label, ptt_diss_id in zip(ptt_columns, ptt_dissertation_ids):
                    row[col_label] = "✅" if ptt_diss_id and ptt_diss_id == diss_id else ""
                matrix_rows.append(row)
            st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

    with tabs[6]:
        if not project_articles or not project_ptts:
            st.info("Matriz indisponível: é necessário ter ao menos um artigo e um PTT.")
        else:
            article_dissertations = {article_id: set() for article_id in article_title_by_id}
            for article_id, dissertation_id in link_pairs:
                article_dissertations.setdefault(article_id, set()).add(dissertation_id)

            matrix_rows = []
            ptt_columns = [f"{p.get('title', p.get('id'))[:30]} ({p.get('year', '-')})" for p in project_ptts]
            ptt_dissertation_ids = [p.get("dissertation_id") for p in project_ptts]
            for article in project_articles:
                article_id = article.get("id")
                row = {
                    "Artigo": f"{(article.get('title') or article_id)[:50]} ({article.get('year', '-')})"
                }
                linked_dissertations = article_dissertations.get(article_id, set())
                for col_label, ptt_diss_id in zip(ptt_columns, ptt_dissertation_ids):
                    row[col_label] = "✅" if ptt_diss_id and ptt_diss_id in linked_dissertations else ""
                matrix_rows.append(row)
            st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)


ppg_id = current_ppg()
if not ppg_id:
    st.stop()

snapshot = _load_ppg_snapshot(ppg_id)
lines = snapshot["research_lines"]
people = snapshot["people"]
projects = snapshot["projects"]
dissertations = snapshot["dissertations"]
articles = snapshot["articles"]
ptts = snapshot["ptts"]

if not lines:
    st.info("Nenhuma linha de pesquisa cadastrada para este PPG.")
    st.stop()

# Filtros persistentes em sessão
current_year = st.session_state.get("linhas_filter_year", "Todos")
status_options = ["Todos"] + sorted({p.get("status", "-") for p in projects})
current_status = st.session_state.get("linhas_filter_status", "Todos")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    years = sorted({str(p.get("year")) for p in dissertations if p.get("year")})
    year_option = st.selectbox("Filtro por ano de dissertação", ["Todos"] + years, index=(["Todos"] + years).index(current_year) if current_year in (["Todos"] + years) else 0)
with filter_col2:
    status_option = st.selectbox(
        "Filtro por status de projeto",
        status_options,
        index=status_options.index(current_status) if current_status in status_options else 0,
    )

st.session_state["linhas_filter_year"] = year_option
st.session_state["linhas_filter_status"] = status_option

people_map = {p.get("id"): p for p in people}

for line in lines:
    line_id = line.get("id")
    line_projects = [p for p in projects if p.get("line_id") == line_id]

    if status_option != "Todos":
        line_projects = [p for p in line_projects if p.get("status") == status_option]

    line_project_ids = {p.get("id") for p in line_projects}
    line_dissertations = [d for d in dissertations if d.get("project_id") in line_project_ids]
    if year_option != "Todos":
        line_dissertations = [d for d in line_dissertations if str(d.get("year")) == year_option]

    filtered_diss_ids = {d.get("id") for d in line_dissertations}
    line_articles = [a for a in articles if a.get("project_id") in line_project_ids]
    line_ptts = [p for p in ptts if p.get("project_id") in line_project_ids]

    permanentes, colaboradores = _line_docentes(line, people)

    line_links: Set[Tuple[str, str]] = set()
    for project in line_projects:
        project_dissertations = [d for d in line_dissertations if d.get("project_id") == project.get("id")]
        project_articles = [a for a in line_articles if a.get("project_id") == project.get("id")]
        line_links.update(_build_article_dissertation_links(project_dissertations, project_articles))

    unique_articles = {aid for aid, _ in line_links} | {
        a.get("id") for a in line_articles if not filtered_diss_ids or a.get("dissertation_id") in filtered_diss_ids or not a.get("dissertation_id")
    }

    label = (
        f"{line.get('name')} — Projetos: {len(line_projects)} | "
        f"Docentes: {len(permanentes) + len(colaboradores)} | "
        f"Dissertações: {len(line_dissertations)} | Artigos: {len(unique_articles)}"
    )

    with st.expander(label, expanded=False):
        st.subheader("Descrição")
        description = line.get("description") or "Sem descrição."
        if len(description) > 240:
            key = f"show_more_{line_id}"
            show_full = st.session_state.get(key, False)
            st.markdown(description if show_full else f"{description[:240]}...")
            if st.button("Ver mais" if not show_full else "Ver menos", key=f"btn_{line_id}"):
                st.session_state[key] = not show_full
                st.rerun()
        else:
            st.markdown(description)

        st.subheader("Docentes")
        doc_col1, doc_col2 = st.columns(2)
        with doc_col1:
            st.markdown("**Permanentes**")
            if permanentes:
                for docente in permanentes:
                    st.markdown(f"- {docente.get('name')}")
            else:
                st.caption("Nenhum docente permanente vinculado.")
        with doc_col2:
            st.markdown("**Colaboradores**")
            if colaboradores:
                for docente in colaboradores:
                    st.markdown(f"- {docente.get('name')}")
            else:
                st.caption("Nenhum docente colaborador vinculado.")

        st.subheader("Projetos da Linha")
        st.caption(
            f"Artigos (únicos): {len(unique_articles)} | "
            f"Associações artigo–dissertação: {len(line_links)}"
        )

        if not line_projects:
            st.info("Nenhum projeto encontrado para os filtros atuais.")
            continue

        for project in line_projects:
            project_id = project.get("id")
            project_mestrandos = [m for m in people if m.get("role") == "mestrando" and m.get("id") in (project.get("mestrandos_ids") or [])]
            project_dissertations = [d for d in line_dissertations if d.get("project_id") == project_id]
            project_articles = [a for a in line_articles if a.get("project_id") == project_id]
            project_ptts = [p for p in line_ptts if p.get("project_id") == project_id]
            link_pairs = _build_article_dissertation_links(project_dissertations, project_articles)

            docentes_proj = [_person_name(people_map, person_id) for person_id in project.get("orientadores_ids", [])]
            title = project.get("name") or "Projeto sem título"
            period = f"{project.get('start_date', '-')} → {project.get('end_date', '-') }"
            header = (
                f"{title} | Status: {project.get('status', '-')} | Período: {period} | "
                f"Mestrandos: {len(project_mestrandos)} | Dissertações: {len(project_dissertations)} | "
                f"Artigos: {len({a.get('id') for a in project_articles})} | PTTs: {len(project_ptts)}"
            )

            with st.container(border=True):
                st.markdown(f"**{header}**")
                st.caption(f"Docentes do projeto: {', '.join(docentes_proj) if docentes_proj else '-'}")
                _project_tabs(
                    project,
                    project_mestrandos,
                    project_dissertations,
                    project_articles,
                    project_ptts,
                    link_pairs,
                    people_map,
                )

st.divider()
if st.button("Adicionar Linha de Pesquisa", use_container_width=True):
    st.session_state.show_add_line_form_linhas = not st.session_state.show_add_line_form_linhas

if st.session_state.show_add_line_form_linhas:
    with st.form("add_line_form_linhas", clear_on_submit=True):
        line_name = st.text_input("Nome da Linha de Pesquisa")
        line_description = st.text_area("Descrição")
        submit_line = st.form_submit_button("Salvar Linha")

    if submit_line:
        if not line_name.strip():
            st.warning("Informe o nome da linha de pesquisa.")
        else:
            add_research_line(ppg_id, line_name.strip(), line_description.strip())
            _load_ppg_snapshot.clear()
            st.success("Linha de pesquisa adicionada com sucesso.")
            st.session_state.show_add_line_form_linhas = False
            st.rerun()
