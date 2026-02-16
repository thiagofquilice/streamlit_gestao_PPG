from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

from data import calculate_weighted_score, get_admin_form, list_target_evaluations, save_evaluation, upsert_evaluation


def _state_key(prefix: str, target_type: str, target_id: str) -> str:
    return f"{prefix}_{target_type}_{target_id}"


def _scale_levels(form: Dict[str, Any]) -> List[Dict[str, Any]]:
    levels = form.get("scale", {}).get("levels", [])
    if levels:
        return levels
    return [
        {"label": "Insuficiente", "value": 1},
        {"label": "Regular", "value": 2},
        {"label": "Bom", "value": 3},
        {"label": "Muito bom", "value": 4},
        {"label": "Excelente", "value": 5},
    ]


def _level_options(levels: List[Dict[str, Any]]) -> List[str]:
    return [f"{float(level.get('value', 0)):.0f} — {str(level.get('label', ''))}" for level in levels]


def render_evaluation_section(
    *,
    ppg_id: str,
    target_type: str,
    target_id: str,
    form_key: str,
    can_manage: bool,
    people: Optional[Dict[str, str]] = None,
    evaluator_id: Optional[str] = None,
) -> None:
    form = get_admin_form(form_key)
    evaluations = sorted(
        list_target_evaluations(target_type, target_id), key=lambda ev: ev.get("created_at", ""), reverse=True
    )
    latest = evaluations[0] if evaluations else None

    show_key = _state_key("show_eval", target_type, target_id)
    edit_key = _state_key("edit_eval", target_type, target_id)

    if show_key not in st.session_state:
        st.session_state[show_key] = False
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    st.markdown("**Avaliação**")

    if latest:
        st.markdown(f"**Nota final da avaliação:** {float(latest.get('final_score') or 0):.2f}")
        st.caption(
            f"Última atualização: {latest.get('created_at', 'N/A')} | "
            f"Avaliador: {(people or {}).get(latest.get('evaluator_id'), latest.get('evaluator_id', '-'))}"
        )

    if can_manage:
        button_cols = st.columns([1, 1, 3])
        with button_cols[0]:
            if st.button("Avaliar", key=_state_key("btn_open", target_type, target_id), use_container_width=True):
                st.session_state[show_key] = True
                st.session_state[edit_key] = False
        with button_cols[1]:
            if st.button(
                "Editar avaliação",
                key=_state_key("btn_edit", target_type, target_id),
                disabled=latest is None,
                use_container_width=True,
            ):
                st.session_state[show_key] = True
                st.session_state[edit_key] = True

    if not st.session_state.get(show_key):
        return

    if not form or not form.get("criteria"):
        st.warning("Não há modelo de avaliação cadastrado para este tipo.")
        return

    levels = _scale_levels(form)
    option_labels = _level_options(levels)
    option_value_by_label = {
        option_label: float(level.get("value", 0)) for option_label, level in zip(option_labels, levels)
    }
    option_index_by_value = {
        float(level.get("value", 0)): idx for idx, level in enumerate(levels)
    }

    initial_scores = latest.get("scores", {}) if latest else {}

    with st.form(_state_key("form_eval", target_type, target_id)):
        st.caption("Preencha cada critério escolhendo o nível de desempenho correspondente (de menor para maior).")

        scores: Dict[str, Any] = {}
        for idx, criterion in enumerate(form.get("criteria", [])):
            criterion_id = criterion.get("id") or f"criterion_{idx + 1}"
            name = criterion.get("name") or f"Critério {idx + 1}"
            description = criterion.get("description") or ""
            weight = float(criterion.get("weight") or 1)

            default_value = float(initial_scores.get(criterion_id, levels[0].get("value", 0)))
            default_index = option_index_by_value.get(default_value, 0)
            st.markdown(f"**Critério: {name}**")
            st.caption(f"Peso: {weight}")
            selected_option = st.radio(
                "Nível atribuído",
                options=option_labels,
                index=default_index,
                horizontal=True,
                help=description or None,
                key=_state_key(f"criterion_{criterion_id}", target_type, target_id),
            )
            scores[criterion_id] = option_value_by_label[selected_option]
            st.caption(f"Descrição do critério: {description}" if description else "Sem descrição complementar.")

        comments = st.text_area(
            "Observações da avaliação",
            value=(latest.get("notes") if st.session_state.get(edit_key) and latest else ""),
            key=_state_key("comments", target_type, target_id),
        )

        col_save, col_cancel = st.columns([1, 1])
        with col_save:
            submitted = st.form_submit_button(
                "Salvar avaliação",
                type="primary",
                use_container_width=True,
                disabled=not can_manage,
            )
        with col_cancel:
            hide = st.form_submit_button("Recolher campos", use_container_width=True)

    if hide:
        st.session_state[show_key] = False
        st.session_state[edit_key] = False
        st.rerun()

    if submitted:
        if st.session_state.get(edit_key) and latest:
            updated = {
                **latest,
                "scores": scores,
                "notes": comments,
                "evaluator_id": evaluator_id or latest.get("evaluator_id"),
                "final_score": calculate_weighted_score(form, scores),
                "created_at": datetime.utcnow().isoformat(),
            }
            upsert_evaluation(updated)
        else:
            save_evaluation(
                ppg_id=ppg_id,
                target_type=target_type,
                target_id=target_id,
                form_key=form_key,
                scores=scores,
                comments=comments,
                evaluator_id=evaluator_id,
            )
        st.session_state[show_key] = False
        st.session_state[edit_key] = False
        st.success("Avaliação salva com sucesso.")
        st.rerun()
