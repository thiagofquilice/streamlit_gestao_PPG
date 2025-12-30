# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

import streamlit as st

from data import (
    create_project,
    delete_project,
    get_project_mestrandos,
    get_project_orientadores,
    list_ppg_members,
    list_project_articles,
    list_project_dissertations,
    list_project_ptts,
    list_projects,
    set_project_mestrandos,
    set_project_orientadores,
    update_project,
)
from rbac import can

st.title("Projetos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

try:
    members = list_ppg_members(ppg_id)
except Exception:
    st.error(
        "Falha ao carregar membros do PPG. Verifique se rodou a migração db/ddl.sql e se as policies RLS permitem acesso."
    )
    members = []
orientadores = [m for m in members if m.get("role") == "orientador"]
mestrandos = [m for m in members if m.get("role") == "mestrando"]
member_labels = {m["user_id"]: m.get("label") or m.get("display_name") or m["user_id"] for m in members}

can_manage_projects = role in ("coordenador", "orientador")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}

if can_manage_projects:
    st.subheader("Cadastrar projeto")
    with st.form("form_new_project"):
        name = st.text_input("Nome do projeto")
        description = st.text_area("Descrição")
        parent_project_id = st.selectbox(
            "Vínculo a um projeto (opcional)",
            [None] + list(project_options.keys()),
            format_func=lambda pid: project_options.get(pid, "Sem vínculo") if pid else "Sem vínculo",
        )
        submitted = st.form_submit_button("Salvar projeto")
    if submitted:
        if not name:
            st.error("Nome é obrigatório.")
        else:
            create_project(ppg_id, name, description or None, parent_project_id)
            st.success("Projeto criado com sucesso.")
            st.experimental_rerun()
else:
    st.info("Seu perfil não permite criar ou editar projetos. Visualização somente de leitura.")

st.divider()
if projects:
    st.subheader("Projetos do PPG")
    for project in projects:
        orientadores_atual = [o["user_id"] for o in get_project_orientadores(project["id"])]
        mestrandos_atual = [m["user_id"] for m in get_project_mestrandos(project["id"])]
        parent_name = project_options.get(project.get("parent_project_id"))
        with st.expander(project.get("name") or "(Sem nome)", expanded=False):
            st.write(project.get("description") or "Sem descrição.")
            st.caption(f"Projeto relacionado: {parent_name or 'Nenhum'}")

            if can_manage_projects:
                with st.form(f"manage-{project['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name_edit = st.text_input("Nome", value=project.get("name") or "")
                        parent_edit = st.selectbox(
                            "Projeto pai (opcional)",
                            [None] + [pid for pid in project_options.keys() if pid != project["id"]],
                            format_func=lambda pid: project_options.get(pid, "Sem vínculo") if pid else "Sem vínculo",
                            index=(
                                [None] + [pid for pid in project_options.keys() if pid != project["id"]]
                            ).index(project.get("parent_project_id"))
                            if project.get("parent_project_id") in project_options
                            else 0,
                        )
                    with col2:
                        description_edit = st.text_area(
                            "Descrição", value=project.get("description") or "", height=120
                        )
                    orientador_selected = st.multiselect(
                        "Orientadores", options=[m["user_id"] for m in orientadores], default=orientadores_atual,
                        format_func=lambda uid: member_labels.get(uid, uid),
                    )
                    mestrando_selected = st.multiselect(
                        "Mestrandos", options=[m["user_id"] for m in mestrandos], default=mestrandos_atual,
                        format_func=lambda uid: member_labels.get(uid, uid),
                    )
                    submitted_edit = st.form_submit_button("Salvar alterações")
                if submitted_edit:
                    update_project(
                        project["id"],
                        {
                            "name": name_edit,
                            "description": description_edit,
                            "parent_project_id": parent_edit,
                        },
                    )
                    set_project_orientadores(project["id"], orientador_selected)
                    set_project_mestrandos(project["id"], mestrando_selected)
                    st.success("Projeto atualizado.")
                    st.experimental_rerun()
            else:
                st.write(
                    "Orientadores:",
                    ", ".join([member_labels.get(uid, uid) for uid in orientadores_atual])
                    or "Nenhum orientador vinculado",
                )
                st.write(
                    "Mestrandos:",
                    ", ".join([member_labels.get(uid, uid) for uid in mestrandos_atual])
                    or "Nenhum mestrando vinculado",
                )

            st.markdown("**Associados**")
            diss = list_project_dissertations(project["id"])
            arts = list_project_articles(project["id"])
            ptts = list_project_ptts(project["id"])
            st.write("Dissertações:", ", ".join([d.get("title", "") for d in diss]) or "Nenhuma")
            st.write("Artigos:", ", ".join([a.get("title", "") for a in arts]) or "Nenhum")
            st.write("PTTs:", ", ".join([p.get("title", "") for p in ptts]) or "Nenhum")

            if can("apagar"):
                if st.button(
                    "Excluir projeto", key=f"delete-{project['id']}", type="primary", use_container_width=True
                ):
                    delete_project(project["id"])
                    st.success("Projeto removido.")
                    st.experimental_rerun()
else:
    st.info("Nenhum projeto cadastrado para este PPG.")
