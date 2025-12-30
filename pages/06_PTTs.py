# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db

ensure_demo_db()

import streamlit as st

from demo_context import current_ppg, current_profile
from data import (
    evaluation_stats,
    list_dissertations,
    list_ppg_members,
    list_projects,
    list_ptts,
    list_research_lines,
    list_target_evaluations,
)

st.title("PTTs")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id:
    st.stop()

can_create_eval = role in ("coordenador", "orientador")

projects = {p["id"]: p.get("name") for p in list_projects(ppg_id)}
lines = {line["id"]: line.get("name") for line in list_research_lines(ppg_id)}
disserts = {d["id"]: d.get("title") for d in list_dissertations(ppg_id)}
people = {m["user_id"]: m.get("display_name") or m.get("label") or m["user_id"] for m in list_ppg_members(ppg_id)}

ptts = list_ptts(ppg_id)
if not ptts:
    st.info("Nenhum PTT cadastrado para este PPG.")
    st.stop()

for ptt in ptts:
    with st.expander(ptt.get("title") or "(Sem título)", expanded=False):
        st.write(ptt.get("summary") or "Sem resumo")
        st.caption(
            f"Projeto: {projects.get(ptt.get('project_id')) or 'Sem projeto'} | "
            f"Linha: {lines.get(ptt.get('line_id')) or 'Sem linha'} | Ano: {ptt.get('year') or 'N/A'}"
        )
        st.caption(
            f"Status: {ptt.get('status', 'N/A')} | Tipo: {ptt.get('tipo_ptt') or 'N/A'} | Dissertação: {disserts.get(ptt.get('dissertation_id')) or 'Sem vínculo'}"
        )

        count, avg, last_score, last_date = evaluation_stats("ptt", ptt["id"])
        st.markdown(
            f"**Avaliações vinculadas:** {count}" + (f" | média: {avg}" if avg is not None else "")
            + (f" | última: {last_score} ({last_date})" if last_score is not None else "")
        )

        st.markdown("**Avaliações**")
        evaluations = sorted(
            list_target_evaluations("ptt", ptt["id"]), key=lambda ev: ev.get("created_at", ""), reverse=True
        )
        for ev in evaluations:
            st.write(
                f"Nota final: {ev.get('final_score')} | Data: {ev.get('created_at', 'N/A')} | "
                f"Avaliador: {people.get(ev.get('evaluator_id'), ev.get('evaluator_id', '-'))}"
            )
            if ev.get("notes"):
                st.caption(ev.get("notes"))

        if can_create_eval:
            st.page_link("pages/07_Avaliações.py", label="Criar avaliação", icon="✏️")
        else:
            st.info("Perfil atual permite apenas visualizar avaliações.")
