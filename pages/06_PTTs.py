# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Tuple

import streamlit as st

from data import (
    get_admin_evaluation_forms,
    list_ppg_members,
    list_projects,
    list_ptts,
    list_research_lines,
    list_target_evaluations,
    upsert_ptt,
)
from demo_context import current_ppg, current_profile
from demo_seed import ensure_demo_db


def _evaluation_summary(ptt_id: str) -> Tuple[int, float | None, float | None]:
    evaluations = list_target_evaluations("ptt", ptt_id)
    if not evaluations:
        return 0, None, None
    scores = [ev.get("final_score", 0) for ev in evaluations]
    avg_score = round(sum(scores) / len(scores), 2)
    latest = sorted(evaluations, key=lambda ev: ev.get("created_at", ""))[-1]
    return len(evaluations), avg_score, latest.get("final_score")


def _ptt_types() -> list[str]:
    forms = get_admin_evaluation_forms()
    return forms.get("ptts", {}).get("ptt_types", [])


ensure_demo_db()

st.title("PTTs")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

can_create = role in ("coordenador", "orientador", "mestrando")
can_edit = role in ("coordenador", "orientador", "mestrando")

projects = list_projects(ppg_id)
project_options = {p["id"]: p.get("name", "") for p in projects}

lines = list_research_lines(ppg_id)
line_options = {line["id"]: line.get("name") for line in lines}

members = list_ppg_members(ppg_id)
orientadores = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "orientador"}
mestrandos = {m["user_id"]: m.get("display_name") or m["user_id"] for m in members if m.get("role") == "mestrando"}

ptts = list_ptts(ppg_id)
tipo_options = _ptt_types()

if ptts:
    st.subheader("PTTs cadastrados")
    for item in ptts:
        eval_count, avg_score, last_score = _evaluation_summary(item["id"])
        with st.expander(item.get("title") or "(Sem título)", expanded=False):
            st.write(item.get("summary") or "Sem resumo")
            st.caption(f"Projeto: {project_options.get(item.get('project_id')) or 'Sem projeto'}")
            st.caption(
                f"Linha: {line_options.get(item.get('line_id')) or 'Sem linha'} | "
                f"Tipo: {item.get('tipo_ptt') or 'N/A'} | Ano: {item.get('year') or 'N/A'}"
            )
            st.caption(
                "Avaliações vinculadas: "
                f"{eval_count}"
                + (f" | média: {avg_score}" if avg_score is not None else "")
                + (f" | última: {last_score}" if last_score is not None else "")
            )
            st.info("Veja detalhes na aba Avaliações.")

            st.write(
                "Orientador:", orientadores.get(item.get("orientador_id")) or "Não definido",
            )
            st.write("Mestrando:", mestrandos.get(item.get("mestrando_id")) or "Não definido")

            if can_edit:
                with st.form(f"edit-ptt-{item['id']}"):
                    title = st.text_input("Título", value=item.get("title", ""))
                    summary = st.text_area("Resumo", value=item.get("summary") or "")
                    tipo = st.selectbox(
                        "Tipo de PTT",
                        tipo_options or [item.get("tipo_ptt") or "software"],
                        index=(tipo_options or [item.get("tipo_ptt") or "software"]).index(
                            item.get("tipo_ptt") or (tipo_options[0] if tipo_options else "software")
                        ),
                    )
                    ano = st.number_input(
                        "Ano", min_value=1900, max_value=2100, value=int(item.get("year") or 2024), step=1
                    )
                    status = st.selectbox(
                        "Status",
                        ["rascunho", "em_andamento", "entregue"],
                        index=["rascunho", "em_andamento", "entregue"].index(item.get("status", "rascunho")),
                    )
                    project_id = st.selectbox(
                        "Projeto (opcional)",
                        [None] + list(project_options.keys()),
                        format_func=lambda pid: project_options.get(pid, "Sem projeto") if pid else "Sem projeto",
                        index=([None] + list(project_options.keys())).index(item.get("project_id"))
                        if item.get("project_id") in project_options
                        else 0,
                    )
                    line_id = st.selectbox(
                        "Linha (opcional)",
                        [None] + list(line_options.keys()),
                        format_func=lambda lid: line_options.get(lid, "Sem linha") if lid else "Sem linha",
                        index=([None] + list(line_options.keys())).index(item.get("line_id"))
                        if item.get("line_id") in line_options
                        else 0,
                    )
                    orientador_id = st.selectbox(
                        "Orientador (opcional)",
                        [None] + list(orientadores.keys()),
                        format_func=lambda uid: orientadores.get(uid, "Sem orientador") if uid else "Sem orientador",
                        index=([None] + list(orientadores.keys())).index(item.get("orientador_id"))
                        if item.get("orientador_id") in orientadores
                        else 0,
                    )
                    mestrando_id = st.selectbox(
                        "Mestrando (opcional)",
                        [None] + list(mestrandos.keys()),
                        format_func=lambda uid: mestrandos.get(uid, "Sem mestrando") if uid else "Sem mestrando",
                        index=([None] + list(mestrandos.keys())).index(item.get("mestrando_id"))
                        if item.get("mestrando_id") in mestrandos
                        else 0,
                    )
                    submitted = st.form_submit_button("Salvar")
                if submitted and title:
                    upsert_ptt(
                        {
                            "id": item["id"],
                            "ppg_id": ppg_id,
                            "title": title,
                            "summary": summary,
                            "tipo_ptt": tipo,
                            "year": int(ano),
                            "status": status,
                            "project_id": project_id,
                            "line_id": line_id,
                            "orientador_id": orientador_id,
                            "mestrando_id": mestrando_id,
                        }
                    )
                    st.success("PTT atualizado.")
                    st.rerun()
else:
    st.info("Nenhum PTT cadastrado para este PPG.")

if can_create:
    st.divider()
    st.subheader("Cadastrar novo PTT")
    with st.form("form-ptt"):
        title = st.text_input("Título")
        summary = st.text_area("Resumo")
        tipo = st.selectbox("Tipo de PTT", tipo_options or ["software", "processo", "relatorio", "produto", "servico"])
        ano = st.number_input("Ano", min_value=1900, max_value=2100, value=2024, step=1)
        status = st.selectbox("Status", ["rascunho", "em_andamento", "entregue"])
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
        submitted = st.form_submit_button("Salvar")
    if submitted and title:
        upsert_ptt(
            {
                "ppg_id": ppg_id,
                "title": title,
                "summary": summary,
                "tipo_ptt": tipo,
                "year": int(ano),
                "status": status,
                "project_id": project_id,
                "line_id": line_id,
                "orientador_id": orientador_id,
                "mestrando_id": mestrando_id,
            }
        )
        st.success("PTT salvo.")
        st.rerun()
else:
    st.info("Seu perfil não permite cadastrar PTTs.")
