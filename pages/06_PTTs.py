# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import streamlit as st

from layout import configure_page, render_sidebar
from navigation_utils import consume_nav_target
from components.evaluation_section import render_evaluation_section

from demo_context import current_ppg, current_profile, current_person
from data import (
    list_dissertations,
    list_ppg_members,
    list_projects,
    list_ptts,
    list_research_lines,
    get_admin_form,
    upsert_ptt,
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

st.title("PTTs")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

can_create_eval = role in ("coordenador", "orientador")
can_create = can("criar")
can_edit = can("editar")

project_rows = list_projects(ppg_id)
projects = {p["id"]: p.get("name") for p in project_rows}
projects_by_id = {p["id"]: p for p in project_rows}
lines = {line["id"]: line.get("name") for line in list_research_lines(ppg_id)}
dissertation_rows = list_dissertations(ppg_id)
disserts = {d["id"]: d.get("title") for d in dissertation_rows}
dissertations_by_id = {d["id"]: d for d in dissertation_rows}
people = {m["user_id"]: m.get("display_name") or m.get("label") or m["user_id"] for m in list_ppg_members(ppg_id)}

ptts = list_ptts(ppg_id)
form_ptts = get_admin_form("ptts")
ptt_type_options = form_ptts.get("ptt_types") or []

current_person_id = current_person()


def _can_edit_ptt(ptt: dict) -> bool:
    if role == "coordenador":
        return True
    if role != "orientador" or not current_person_id:
        return False
    if ptt.get("created_by") == current_person_id:
        return True
    project = projects_by_id.get(ptt.get("project_id")) or {}
    if current_person_id in (project.get("orientadores_ids") or []):
        return True
    dissertation = dissertations_by_id.get(ptt.get("dissertation_id")) or {}
    return dissertation.get("orientador_id") == current_person_id


def _mestrando_own_dissertations() -> list[dict]:
    if role != "mestrando" or not current_person_id:
        return []
    return [d for d in dissertation_rows if d.get("mestrando_id") == current_person_id]

if not ptts:
    st.info("Nenhum PTT cadastrado para este PPG.")

status_filter_options = available_filter_labels(ptt.get("status") for ptt in ptts if ptt.get("status"))
status_filter = st.selectbox("Filtrar por status", ["Todos"] + status_filter_options, index=0)
filtered_ptts = ptts
selected_filter_key = filter_label_to_key(status_filter)
if selected_filter_key is not None:
    filtered_ptts = [ptt for ptt in ptts if (ptt.get("status") or "") == selected_filter_key]

selected_target_id = consume_nav_target("ptt")

for ptt in filtered_ptts:
    title_with_status = f"{ptt.get('title') or '(Sem título)'} | Status: {status_label(ptt.get('status'))}"
    with st.expander(title_with_status, expanded=(selected_target_id == ptt.get("id"))):
        st.write(ptt.get("summary") or "Sem resumo")
        st.caption(
            f"Projeto: {projects.get(ptt.get('project_id')) or 'Sem projeto'} | "
            f"Linha: {lines.get(ptt.get('line_id')) or 'Sem linha'} | Ano: {ptt.get('year') or 'N/A'}"
        )
        st.caption(
            f"Status: {status_label(ptt.get('status'))} | Tipo: {ptt.get('tipo_ptt') or 'N/A'} | Dissertação: {disserts.get(ptt.get('dissertation_id')) or 'Sem vínculo'}"
        )

        if can_edit and _can_edit_ptt(ptt):
            with st.form(f"ptt-status-{ptt['id']}"):
                status = status_selector("Status", ptt.get("status"), key=f"ptt-status-control-{ptt['id']}")
                tipo_index = ptt_type_options.index(ptt.get("tipo_ptt")) if ptt.get("tipo_ptt") in ptt_type_options else 0
                tipo_ptt = st.selectbox("Tipo de PTT", ptt_type_options or [""], index=tipo_index, key=f"ptt-type-{ptt['id']}")
                submitted_status = st.form_submit_button("Salvar dados", use_container_width=True)

            if submitted_status:
                upsert_ptt({**ptt, "status": status, "tipo_ptt": tipo_ptt})
                st.success("Dados do PTT atualizados.")
                st.rerun()

        render_evaluation_section(
            ppg_id=ppg_id,
            target_type="ptt",
            target_id=ptt["id"],
            form_key="ptts",
            can_manage=can_create_eval,
            people=people,
            evaluator_id=current_person(),
        )


if can_create:
    st.divider()
    st.subheader("Cadastrar novo PTT")

    add_new_key = "show_new_ptt_form"
    if add_new_key not in st.session_state:
        st.session_state[add_new_key] = False

    if st.button("Adicionar PTT", use_container_width=True):
        st.session_state[add_new_key] = True

    if st.session_state[add_new_key]:
        own_dissertations = _mestrando_own_dissertations()
        mestrando_without_dissertation = role == "mestrando" and not own_dissertations
        with st.form("form-ptt"):
            title = st.text_input("Título")
            summary = st.text_area("Resumo")
            year = st.number_input("Ano", min_value=1900, max_value=2100, value=2024, step=1)
            if role == "mestrando":
                dissertation_id = st.selectbox(
                    "Dissertação (obrigatória)",
                    [d.get("id") for d in own_dissertations],
                    format_func=lambda did: disserts.get(did, "Sem vínculo"),
                    disabled=mestrando_without_dissertation,
                ) if own_dissertations else None
                selected_dissertation = dissertations_by_id.get(dissertation_id) if dissertation_id else {}
                project_id = selected_dissertation.get("project_id")
                line_id = selected_dissertation.get("line_id")
                st.caption(f"Projeto vinculado: {projects.get(project_id) or 'N/A'}")
                st.caption(f"Linha vinculada: {lines.get(line_id) or 'Sem linha'}")
            else:
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
            status = status_selector("Status", None, key="ptt-status-new")
            tipo_ptt = st.selectbox("Tipo de PTT", ptt_type_options or [""], key="ptt-type-new")
            save_col, cancel_col = st.columns(2)
            with save_col:
                submitted = st.form_submit_button("Salvar", use_container_width=True, disabled=mestrando_without_dissertation)
            with cancel_col:
                hide_form = st.form_submit_button("Cancelar", use_container_width=True)

        if hide_form:
            st.session_state[add_new_key] = False
            st.rerun()

        if submitted and title:
            if role == "mestrando" and not dissertation_id:
                st.error("Você só pode cadastrar PTT vinculado à sua dissertação.")
            else:
                upsert_ptt(
                    {
                        "ppg_id": ppg_id,
                        "title": title,
                        "summary": summary,
                        "year": int(year),
                        "project_id": project_id,
                        "line_id": line_id,
                        "dissertation_id": dissertation_id,
                        "status": status,
                        "tipo_ptt": tipo_ptt,
                        "created_by": current_person_id,
                    }
                )
                st.success("PTT salvo.")
                st.session_state[add_new_key] = False
                st.rerun()
elif not ptts:
    st.info("Seu perfil não permite cadastrar PTTs.")
