from __future__ import annotations

from typing import Dict

from demo_seed import ensure_demo_db

ensure_demo_db()

import streamlit as st

from demo_context import current_person, current_ppg, current_profile
from data import (
    add_evaluation_record,
    calculate_weighted_score,
    get_admin_evaluation_forms,
    get_admin_form,
    list_articles,
    list_ppg_members,
    list_ptts,
    list_target_evaluations,
)

st.title("Avaliações")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

forms = get_admin_evaluation_forms()
if not forms:
    st.info("Nenhuma ficha de avaliação configurada. Cadastre uma ficha para continuar.")
    st.stop()

articles = list_articles(ppg_id)
ptts = list_ptts(ppg_id)
members = list_ppg_members(ppg_id)
people_labels = {m["user_id"]: m.get("display_name") or m.get("label") or m["user_id"] for m in members}


def _current_evaluator_id() -> str | None:
    if role != "coordenador":
        return current_person()
    coord = next((m["user_id"] for m in members if m.get("role") == "coordenador"), None)
    return coord or current_person() or (members[0]["user_id"] if members else None)


targets = {
    "article": {
        "label": "Artigos",
        "items": articles,
        "form_type": "articles",
        "title_field": "title",
    },
    "ptt": {
        "label": "PTTs",
        "items": ptts,
        "form_type": "ptts",
        "title_field": "title",
    },
}

target_type = st.selectbox("Tipo de avaliação", options=list(targets.keys()), format_func=lambda k: targets[k]["label"])
target_cfg = targets[target_type]
form = get_admin_form(target_cfg["form_type"])
if not form:
    st.warning("Ficha de avaliação não encontrada para este tipo.")
    form = {"criteria": []}

if not target_cfg["items"]:
    st.info(f"Nenhum {target_cfg['label'].lower()} cadastrado para avaliar.")
    st.stop()

options = {item["id"]: item.get(target_cfg["title_field"], item["id"]) for item in target_cfg["items"]}
selected_id = st.selectbox(
    f"Selecione o {target_cfg['label'][:-1].lower()} a ser avaliado",
    options=list(options.keys()),
    format_func=lambda oid: options.get(oid, oid),
)

current_target_key = f"{target_type}:{selected_id}"
if st.session_state.get("_current_eval_target") != current_target_key:
    st.session_state["_current_eval_target"] = current_target_key
    st.session_state.pop("_show_eval_form", None)

existing = list_target_evaluations(target_type, selected_id)

st.subheader("Avaliações registradas")
if existing:
    for ev in sorted(existing, key=lambda item: item.get("created_at", ""), reverse=True):
        with st.container():
            st.markdown(f"**Nota final:** {ev.get('final_score')} | Criado em: {ev.get('created_at', 'N/A')}")
            evaluator_name = people_labels.get(ev.get("evaluator_id"), ev.get("evaluator_id", "-"))
            st.markdown(f"Avaliador: {evaluator_name}")
            if ev.get("notes"):
                st.write(ev.get("notes"))
else:
    st.info("Nenhuma avaliação registrada para este item.")

can_submit = role in ("coordenador", "orientador")
if not can_submit:
    st.info("Seu perfil permite apenas visualizar as avaliações.")
else:
    if st.button("Nova avaliação", type="primary"):
        st.session_state["_show_eval_form"] = True

    if st.session_state.get("_show_eval_form"):
        st.subheader("Registrar nova avaliação")
        st.caption("Itens do tipo 'Sim/Não' valem 5 para 'Sim' e 0 para 'Não'.")
        with st.form("evaluation_form"):
            scores: Dict[str, object] = {}
            for criterion in form.get("criteria", []):
                ctype = criterion.get("response_type")
                label = f"{criterion.get('name')} ({criterion.get('weight')})"
                help_text = criterion.get("description")
                if ctype == "yes_no":
                    scores[criterion["id"]] = st.checkbox(label, help=help_text, value=True)
                else:
                    scores[criterion["id"]] = st.slider(
                        label,
                        min_value=1,
                        max_value=5,
                        step=1,
                        value=4,
                        help=help_text,
                    )
            notes = st.text_area("Comentários", placeholder="Observações gerais da banca")
            submitted = st.form_submit_button("Salvar avaliação", type="primary")
        if submitted:
            payload = {
                "ppg_id": ppg_id,
                "target_type": target_type,
                "target_id": selected_id,
                "form_type": target_cfg["form_type"],
                "scores": scores,
                "notes": notes,
                "evaluator_id": _current_evaluator_id(),
            }
            saved = add_evaluation_record(payload)
            final_score = saved.get("final_score") or calculate_weighted_score(form, scores)
            st.success(f"Avaliação registrada. Nota final: {final_score}")
            st.session_state.pop("_show_eval_form", None)
            st.rerun()
