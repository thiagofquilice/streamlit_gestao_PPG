# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import streamlit as st

from data import list_dissertations, list_ppg_members, list_projects, list_research_lines, upsert_dissertation
from demo_context import current_ppg, current_profile
from rbac import can
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

st.title("Dissertações")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

can_create = can("criar")
can_edit = can("editar")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}

lines = list_research_lines(ppg_id)
line_options = {line["id"]: line.get("name") for line in lines}

members = list_ppg_members(ppg_id)
orientadores = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "orientador"}
mestrandos = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "mestrando"}

items = list_dissertations(ppg_id)
if items:
    st.subheader("Dissertações cadastradas")
    for diss in items:
        with st.expander(diss.get("title") or "(Sem título)", expanded=False):
            st.write(diss.get("summary") or "Sem resumo")
            st.caption(f"Projeto: {project_options.get(diss.get('project_id')) or 'Sem projeto'}")
            st.caption(f"Linha: {line_options.get(diss.get('line_id')) or 'Sem linha'} | Ano: {diss.get('year') or 'N/A'}")
            st.caption(f"Status: {diss.get('status') or 'planejado'}")
            st.write("Orientador:", orientadores.get(diss.get("orientador_id")) or "Não definido")
            st.write("Mestrando:", mestrandos.get(diss.get("mestrando_id")) or "Não definido")

            if can_edit:
                with st.form(f"edit-diss-{diss['id']}"):
                    title = st.text_input("Título", value=diss.get("title", ""))
                    summary = st.text_area("Resumo", value=diss.get("summary") or "")
                    year = st.number_input("Ano", min_value=1900, max_value=2100, value=int(diss.get("year") or 2024), step=1)
                    project_id = st.selectbox(
                        "Projeto (opcional)",
                        [None] + list(project_options.keys()),
                        format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
                        index=([None] + list(project_options.keys())).index(diss.get("project_id"))
                        if diss.get("project_id") in project_options
                        else 0,
                    )
                    line_id = st.selectbox(
                        "Linha (opcional)",
                        [None] + list(line_options.keys()),
                        format_func=lambda lid: line_options.get(lid, "Sem linha") if lid else "Sem linha",
                        index=([None] + list(line_options.keys())).index(diss.get("line_id"))
                        if diss.get("line_id") in line_options
                        else 0,
                    )
                    orientador_id = st.selectbox(
                        "Orientador (opcional)",
                        [None] + list(orientadores.keys()),
                        format_func=lambda uid: orientadores.get(uid, "Sem orientador") if uid else "Sem orientador",
                        index=([None] + list(orientadores.keys())).index(diss.get("orientador_id"))
                        if diss.get("orientador_id") in orientadores
                        else 0,
                    )
                    mestrando_id = st.selectbox(
                        "Mestrando (opcional)",
                        [None] + list(mestrandos.keys()),
                        format_func=lambda uid: mestrandos.get(uid, "Sem mestrando") if uid else "Sem mestrando",
                        index=([None] + list(mestrandos.keys())).index(diss.get("mestrando_id"))
                        if diss.get("mestrando_id") in mestrandos
                        else 0,
                    )
                    status = status_selector("Status", diss.get("status"), key=f"status-{diss['id']}")
                    submitted = st.form_submit_button("Salvar", use_container_width=True)
                if submitted and title:
                    upsert_dissertation(
                        {
                            "id": diss["id"],
                            "ppg_id": ppg_id,
                            "title": title,
                            "summary": summary,
                            "year": int(year),
                            "project_id": project_id,
                            "line_id": line_id,
                            "orientador_id": orientador_id,
                            "mestrando_id": mestrando_id,
                            "status": status,
                            "artigos_ids": diss.get("artigos_ids", []),
                            "ptts_ids": diss.get("ptts_ids", []),
                        }
                    )
                    st.success("Dissertação atualizada.")
                    st.rerun()
else:
    st.info("Nenhuma dissertação cadastrada para este PPG.")

if can_create:
    st.divider()
    st.subheader("Cadastrar nova dissertação")
    with st.form("form-diss"):
        title = st.text_input("Título")
        summary = st.text_area("Resumo")
        year = st.number_input("Ano", min_value=1900, max_value=2100, value=2024, step=1)
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
        status = status_selector("Status", None, key="status-new")
        submitted = st.form_submit_button("Salvar", use_container_width=True)
    if submitted and title:
        upsert_dissertation(
            {
                "ppg_id": ppg_id,
                "title": title,
                "summary": summary,
                "year": int(year),
                "project_id": project_id,
                "line_id": line_id,
                "orientador_id": orientador_id,
                "mestrando_id": mestrando_id,
                "status": status,
                "artigos_ids": [],
                "ptts_ids": [],
            }
        )
        st.success("Dissertação salva.")
        st.rerun()
else:
    st.info("Seu perfil não permite cadastrar dissertações.")
