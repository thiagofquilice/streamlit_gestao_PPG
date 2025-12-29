# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import list_dissertations, list_projects, upsert_dissertation
from rbac import can

st.title("Dissertações")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

can_create = can("criar")
can_edit = can("editar")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}

items = list_dissertations(ppg_id)
if items:
    st.subheader("Dissertações cadastradas")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Título": i.get("title"),
                    "Projeto": project_options.get(i.get("project_id"), ""),
                    "Resumo": (i.get("summary") or "")[:120],
                }
                for i in items
            ]
        ),
        use_container_width=True,
    )

    if can_edit:
        st.divider()
        st.subheader("Editar dissertações")
        for i in items:
            with st.form(f"edit-diss-{i['id']}"):
                st.caption(f"Editar: {i.get('title')}")
                title = st.text_input("Título", value=i.get("title", ""))
                summary = st.text_area("Resumo", value=i.get("summary") or "")
                project_id = st.selectbox(
                    "Projeto (opcional)",
                    [None] + list(project_options.keys()),
                    format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
                    index=([None] + list(project_options.keys())).index(i.get("project_id"))
                    if i.get("project_id") in project_options
                    else 0,
                )
                submitted = st.form_submit_button("Salvar")
            if submitted and title:
                upsert_dissertation(
                    {
                        "id": i["id"],
                        "ppg_id": ppg_id,
                        "title": title,
                        "summary": summary,
                        "project_id": project_id,
                    }
                )
                st.success("Dissertação atualizada.")
                st.experimental_rerun()
else:
    st.info("Nenhuma dissertação cadastrada para este PPG.")

if can_create:
    st.divider()
    st.subheader("Cadastrar nova dissertação")
    with st.form("form-diss"):
        title = st.text_input("Título")
        summary = st.text_area("Resumo")
        project_id = st.selectbox(
            "Projeto (opcional)",
            [None] + list(project_options.keys()),
            format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
        )
        submitted = st.form_submit_button("Salvar")
    if submitted and title:
        upsert_dissertation(
            {
                "ppg_id": ppg_id,
                "title": title,
                "summary": summary,
                "project_id": project_id,
            }
        )
        st.success("Dissertação salva.")
        st.experimental_rerun()
else:
    st.info("Seu perfil não permite cadastrar dissertações.")
