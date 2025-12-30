# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from data import (
    calculate_weighted_score,
    get_admin_evaluation_forms,
    get_admin_form,
    list_articles,
    list_ppg_evaluations,
    list_ptts,
    save_evaluation,
)
from demo_context import current_ppg, current_profile

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

targets = {
    "article": {
        "label": "Artigos",
        "items": articles,
        "form_key": "articles",
        "title_field": "title",
    },
    "ptt": {
        "label": "PTTs",
        "items": ptts,
        "form_key": "ptts",
        "title_field": "title",
    },
}

target_type = st.selectbox("Tipo de avaliação", options=list(targets.keys()), format_func=lambda k: targets[k]["label"])
target_cfg = targets[target_type]
form = get_admin_form(target_cfg["form_key"])

if not target_cfg["items"]:
    st.info(f"Nenhum {target_cfg['label'].lower()} cadastrado para avaliar.")
    st.stop()

options = {item["id"]: item.get(target_cfg["title_field"], item["id"]) for item in target_cfg["items"]}
selected_id = st.selectbox(
    f"Selecione o {target_cfg['label'][:-1].lower()} a ser avaliado",
    options=list(options.keys()),
    format_func=lambda oid: options.get(oid, oid),
)

with st.expander(form.get("name", "Ficha"), expanded=True):
    st.caption("Preencha os critérios abaixo. Itens do tipo 'yes_no' valem 5 para 'Sim' e 0 para 'Não'.")
    with st.form("evaluation_form"):
        scores = {}
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
        comments = st.text_area("Comentários", placeholder="Observações gerais da banca")
        submitted = st.form_submit_button("Salvar avaliação", type="primary")

    if submitted:
        saved = save_evaluation(ppg_id, target_type, selected_id, target_cfg["form_key"], scores, comments)
        final_score = saved.get("final_score") or calculate_weighted_score(form, scores)
        st.success(f"Avaliação registrada. Nota final: {final_score}")
        st.experimental_rerun()

st.divider()
st.subheader("Avaliações registradas")
existing = list_ppg_evaluations(ppg_id, target_type)
if existing:
    df_rows = []
    for ev in existing:
        df_rows.append(
            {
                "Alvo": options.get(ev.get("target_id"), ev.get("target_id")),
                "Nota": ev.get("final_score"),
                "Comentários": ev.get("comments"),
            }
        )
    st.dataframe(pd.DataFrame(df_rows), use_container_width=True)
else:
    st.info("Nenhuma avaliação registrada para este tipo.")
