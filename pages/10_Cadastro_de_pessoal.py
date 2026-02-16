# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st

from demo_context import current_ppg, current_profile
from demo_seed import ensure_demo_db
from data import (
    list_articles,
    list_dissertations,
    list_ppg_members,
    list_projects,
    list_ptts,
    list_research_lines,
    upsert_person,
)
from layout import configure_page, render_sidebar
from navigation_utils import consume_nav_target

ensure_demo_db()

configure_page()
render_sidebar()

st.title("Cadastro de pessoal")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

members = list_ppg_members(ppg_id)
projects = list_projects(ppg_id)
dissertations = list_dissertations(ppg_id)
articles = list_articles(ppg_id)
ptts = list_ptts(ppg_id)
lines = {line["id"]: line.get("name") for line in list_research_lines(ppg_id)}

role_labels = {
    "coordenador": "Coordenador",
    "orientador": "Orientadores",
    "mestrando": "Mestrandos",
}
label_to_role = {v: k for k, v in role_labels.items()}
options = ["Coordenador", "Orientadores", "Mestrandos"]
segmented = getattr(st, "segmented_control", None)
if segmented:
    selected_label = segmented("Perfis", options, default=options[0])
else:
    selected_label = st.radio("Perfis", options, horizontal=True, index=0)
selected_role = label_to_role[selected_label]
selected_person_id = consume_nav_target("person")
if selected_person_id:
    selected_label = "Mestrandos"
    selected_role = "mestrando"

st.divider()

if "show_new_person_form" not in st.session_state:
    st.session_state.show_new_person_form = False

can_register = role == "coordenador"
button_label = f"Incluir {selected_label[:-1] if selected_label.endswith('s') else selected_label}"
if st.button(button_label, use_container_width=True, disabled=not can_register):
    st.session_state.show_new_person_form = True

if not can_register:
    st.caption("Apenas o coordenador pode cadastrar pessoas.")

if st.session_state.show_new_person_form:
    with st.form("form-new-person", clear_on_submit=True):
        name = st.text_input("Nome")
        entry_year = st.number_input("Ano de ingresso", min_value=1900, max_value=2100, value=2026, step=1)
        email = st.text_input("E-mail")
        save_col, cancel_col = st.columns(2)
        with save_col:
            submitted = st.form_submit_button("Salvar", use_container_width=True, disabled=not can_register)
        with cancel_col:
            canceled = st.form_submit_button("Cancelar", use_container_width=True)

    if canceled:
        st.session_state.show_new_person_form = False
        st.rerun()

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Informe nome e e-mail.")
        else:
            upsert_person(
                {
                    "ppg_id": ppg_id,
                    "name": name.strip(),
                    "email": email.strip(),
                    "entry_year": int(entry_year),
                    "role": selected_role,
                }
            )
            st.success("Pessoa cadastrada com sucesso.")
            st.session_state.show_new_person_form = False
            st.rerun()

visible_members = [m for m in members if m.get("role") == selected_role]
if not visible_members:
    st.info("Nenhuma pessoa cadastrada neste perfil.")

for person in visible_members:
    person_id = person.get("id")
    person_name = person.get("name") or "Sem nome"
    subtitle = f"{person.get('email') or '-'} | Ingresso: {person.get('entry_year') or '-'}"

    related_projects = [p for p in projects if person_id in (p.get("orientadores_ids") or []) or person_id in (p.get("mestrandos_ids") or [])]
    related_dissertations = [d for d in dissertations if d.get("orientador_id") == person_id or d.get("mestrando_id") == person_id]
    related_articles = [a for a in articles if person_id in (a.get("authors_ids") or [])]
    related_ptts = [p for p in ptts if person_id in (p.get("authors_ids") or [])]

    line_ids = person.get("linhas_ids") or []
    if person.get("line_id"):
        line_ids = [person.get("line_id")] + list(line_ids)

    with st.expander(person_name, expanded=(selected_person_id == person_id)):
        with st.container(border=True):
            st.caption(subtitle)
            if line_ids:
                linked_lines = [lines.get(line_id, line_id) for line_id in dict.fromkeys(line_ids)]
                st.write("**Linhas de pesquisa:**")
                for line_name in linked_lines:
                    st.markdown(f"- {line_name}")

            st.write("**Projetos vinculados:**")
            if related_projects:
                for proj in related_projects:
                    st.markdown(f"- {proj.get('name')}")
            else:
                st.caption("Nenhum projeto vinculado.")

            st.write("**Dissertações vinculadas:**")
            if related_dissertations:
                for diss in related_dissertations:
                    st.markdown(f"- {diss.get('title')}")
            else:
                st.caption("Nenhuma dissertação vinculada.")

            st.write("**Artigos vinculados:**")
            if related_articles:
                for article in related_articles:
                    st.markdown(f"- {article.get('title')}")
            else:
                st.caption("Nenhum artigo vinculado.")

            st.write("**PTTs vinculados:**")
            if related_ptts:
                for ptt in related_ptts:
                    st.markdown(f"- {ptt.get('title')}")
            else:
                st.caption("Nenhum PTT vinculado.")
