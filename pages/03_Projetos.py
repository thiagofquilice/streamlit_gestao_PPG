# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

import streamlit as st

from demo_context import current_ppg, current_profile
from demo_seed import ensure_demo_db
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
    list_research_lines,
    set_project_mestrandos,
    set_project_orientadores,
    update_project,
)
from rbac import can

ensure_demo_db()

st.title("Projetos")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

members = list_ppg_members(ppg_id)
orientadores = [m for m in members if m.get("role") == "orientador"]
mestrandos = [m for m in members if m.get("role") == "mestrando"]
member_labels = {m["user_id"]: m.get("label") or m.get("display_name") or m["user_id"] for m in members}

can_manage_projects = role in ("coordenador", "orientador")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}
lines = list_research_lines(ppg_id)
line_options = {l["id"]: l.get("name") for l in lines}

if can_manage_projects:
    st.subheader("Cadastrar projeto")
    with st.form("form_new_project"):
        name = st.text_input("Nome do projeto")
        description = st.text_area("Descrição")
        line_id = st.selectbox(
            "Linha de pesquisa (opcional)",
            [None] + list(line_options.keys()),
            format_func=lambda lid: line_options.get(lid, "Sem linha") if lid else "Sem linha",
        )
        status = st.selectbox("Status", ["planejamento", "em_andamento", "concluido"])
        orientador_selected = st.multiselect(
            "Orientadores", options=[m["user_id"] for m in orientadores], format_func=lambda uid: member_labels.get(uid, uid)
        )
        mestrando_selected = st.multiselect(
            "Mestrandos", options=[m["user_id"] for m in mestrandos], format_func=lambda uid: member_labels.get(uid, uid)
        )
        submitted = st.form_submit_button("Salvar projeto")
    if submitted:
        if not name:
            st.error("Nome é obrigatório.")
        else:
            new_project = create_project(ppg_id, name, description or None, line_id, status)
            set_project_orientadores(new_project["id"], orientador_selected)
            set_project_mestrandos(new_project["id"], mestrando_selected)
            st.success("Projeto criado com sucesso.")
            st.rerun()
else:
    st.info("Seu perfil não permite criar ou editar projetos. Visualização somente de leitura.")

st.divider()
if projects:
    st.subheader("Projetos do PPG")
    for project in projects:
        orientadores_atual = [o["user_id"] for o in get_project_orientadores(project["id"])]
        mestrandos_atual = [m["user_id"] for m in get_project_mestrandos(project["id"])]
        with st.expander(project.get("name") or "(Sem nome)", expanded=False):
            st.write(project.get("description") or "Sem descrição.")
            st.caption(f"Linha de pesquisa: {line_options.get(project.get('line_id')) or 'Sem linha'}")
            st.caption(f"Status: {project.get('status')}")

            if can_manage_projects:
                with st.form(f"manage-{project['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name_edit = st.text_input("Nome", value=project.get("name") or "")
                        line_edit = st.selectbox(
                            "Linha de pesquisa",
                            [None] + list(line_options.keys()),
                            format_func=lambda lid: line_options.get(lid, "Sem linha") if lid else "Sem linha",
                            index=([None] + list(line_options.keys())).index(project.get("line_id"))
                            if project.get("line_id") in line_options
                            else 0,
                        )
                    with col2:
                        description_edit = st.text_area(
                            "Descrição", value=project.get("description") or "", height=120
                        )
                        status_edit = st.selectbox(
                            "Status",
                            ["planejamento", "em_andamento", "concluido"],
                            index=["planejamento", "em_andamento", "concluido"].index(project.get("status", "em_andamento")),
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
                            "line_id": line_edit,
                            "status": status_edit,
                        },
                    )
                    set_project_orientadores(project["id"], orientador_selected)
                    set_project_mestrandos(project["id"], mestrando_selected)
                    st.success("Projeto atualizado.")
                    st.rerun()

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

            if can("apagar") and can_manage_projects:
                if st.button(
                    "Excluir projeto", key=f"delete-{project['id']}", type="primary", use_container_width=True
                ):
                    delete_project(project["id"])
                    st.success("Projeto removido.")
                    st.rerun()
else:
    st.info("Nenhum projeto cadastrado para este PPG.")
