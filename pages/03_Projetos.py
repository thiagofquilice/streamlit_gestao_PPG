# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt
from typing import List

import pandas as pd
import streamlit as st

from data import (
    add_project,
    delete_project,
    list_ppg_members,
    list_project_mestrandos,
    list_project_orientadores,
    list_projects,
    set_project_mestrandos,
    set_project_orientadores,
    update_project,
)
from rbac import can

st.title("Projetos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
user_id = st.session_state.get("auth", {}).get("user_id")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

members = list_ppg_members(ppg_id)
orientadores = [m for m in members if m.get("role") == "orientador"]
mestrandos = [m for m in members if m.get("role") == "mestrando"]


def _options_dict(filtered_members: List[dict]) -> dict:
    return {m["user_id"]: f"{m['user_id']} ({m['role']})" for m in filtered_members}


def _date_input(label: str, value: str | None, key: str):
    parsed = dt.date.fromisoformat(value) if value else None
    return st.date_input(label, value=parsed, key=key)


can_create = can("criar")
can_edit = can("editar")
can_delete = can("apagar")

projects = list_projects(ppg_id)
if projects:
    st.subheader("Projetos cadastrados")
    summary_rows = []
    orientador_map = {p["id"]: list_project_orientadores(p["id"]) for p in projects}
    mestrando_map = {p["id"]: list_project_mestrandos(p["id"]) for p in projects}
    for p in projects:
        summary_rows.append(
            {
                "Título": p.get("title"),
                "Status": p.get("status") or "-",
                "Orientadores": len(orientador_map.get(p["id"], [])),
                "Mestrandos": len(mestrando_map.get(p["id"], [])),
                "Início": p.get("start_date"),
                "Fim": p.get("end_date"),
            }
        )
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

    for p in projects:
        with st.expander(p.get("title", "(sem título)"), expanded=False):
            st.write(p.get("description") or "Sem descrição.")
            st.caption(f"Status: {p.get('status') or 'não informado'}")
            project_orientadores = orientador_map.get(p["id"], [])
            project_mestrandos = mestrando_map.get(p["id"], [])
            st.write(
                "Orientadores:",
                ", ".join(project_orientadores) if project_orientadores else "Nenhum vinculado",
            )
            st.write(
                "Mestrandos:",
                ", ".join(project_mestrandos) if project_mestrandos else "Nenhum vinculado",
            )

            if role == "orientador" and user_id and user_id not in project_orientadores:
                if st.button(
                    "Aderir como orientador", key=f"join-{p['id']}", use_container_width=True
                ):
                    combined = list(dict.fromkeys(project_orientadores + [user_id]))
                    set_project_orientadores(p["id"], ppg_id, combined)
                    st.success("Vínculo adicionado ao projeto.")
                    st.experimental_rerun()

            if can_edit:
                with st.form(f"edit_project_{p['id']}"):
                    title = st.text_input("Título", value=p.get("title", ""))
                    description = st.text_area("Descrição", value=p.get("description") or "")
                    status = st.selectbox(
                        "Status",
                        ["em_andamento", "concluido", "planejado"],
                        index=["em_andamento", "concluido", "planejado"].index(
                            p.get("status") or "em_andamento"
                        ),
                    )
                    start_date = _date_input("Data de início", p.get("start_date"), key=f"start-{p['id']}")
                    end_date = _date_input("Data de término", p.get("end_date"), key=f"end-{p['id']}")
                    orientador_options = _options_dict(orientadores)
                    mestrando_options = _options_dict(mestrandos)
                    orientadores_selected = st.multiselect(
                        "Orientadores vinculados",
                        options=list(orientador_options.keys()),
                        default=project_orientadores,
                        format_func=lambda uid: orientador_options.get(uid, uid),
                        help="Inclua pelo menos um orientador responsável pelo projeto.",
                    )
                    mestrandos_selected = st.multiselect(
                        "Mestrandos vinculados",
                        options=list(mestrando_options.keys()),
                        default=project_mestrandos,
                        format_func=lambda uid: mestrando_options.get(uid, uid),
                    )
                    submitted = st.form_submit_button("Salvar alterações")
                if submitted:
                    payload = {
                        "title": title,
                        "description": description,
                        "status": status,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    }
                    update_project(p["id"], payload)
                    set_project_orientadores(p["id"], ppg_id, orientadores_selected)
                    set_project_mestrandos(p["id"], mestrandos_selected)
                    st.success("Projeto atualizado.")
                    st.experimental_rerun()

            if can_delete:
                if st.button(
                    "Excluir projeto",
                    key=f"delete-{p['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    delete_project(p["id"])
                    st.success("Projeto removido.")
                    st.experimental_rerun()
else:
    st.info("Nenhum projeto cadastrado para este PPG.")

if can_create:
    st.divider()
    st.subheader("Cadastrar novo projeto")
    with st.form("form_new_project"):
        title = st.text_input("Título do projeto")
        description = st.text_area("Descrição")
        status = st.selectbox("Status", ["em_andamento", "concluido", "planejado"], index=0)
        start_date = st.date_input("Data de início", value=None)
        end_date = st.date_input("Data de término", value=None)
        orientador_options = _options_dict(orientadores)
        mestrando_options = _options_dict(mestrandos)
        orientadores_selected = st.multiselect(
            "Orientadores",
            options=list(orientador_options.keys()),
            format_func=lambda uid: orientador_options.get(uid, uid),
        )
        mestrandos_selected = st.multiselect(
            "Mestrandos",
            options=list(mestrando_options.keys()),
            format_func=lambda uid: mestrando_options.get(uid, uid),
        )
        submitted = st.form_submit_button("Criar projeto")

    if submitted:
        if not title:
            st.error("Título é obrigatório.")
        else:
            payload = {
                "ppg_id": ppg_id,
                "title": title,
                "description": description,
                "status": status,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            }
            project = add_project(payload)
            if project.get("id"):
                set_project_orientadores(project["id"], ppg_id, orientadores_selected)
                set_project_mestrandos(project["id"], mestrandos_selected)
            st.success("Projeto criado com sucesso.")
            st.experimental_rerun()
else:
    st.info("Seu perfil não permite criar novos projetos.")
