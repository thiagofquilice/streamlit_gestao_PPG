# -*- coding: utf-8 -*-
from __future__ import annotations

from demo_seed import ensure_demo_db
import pandas as pd
import streamlit as st

from data import get_admin_evaluation_forms
from demo_context import current_ppg, current_profile
from ui_style import apply_modern_white_theme

ensure_demo_db()
apply_modern_white_theme()

st.title("Fichas CAPES / Critérios Administração")
ppg_id = current_ppg()
role = current_profile()
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

forms = get_admin_evaluation_forms()
if not forms:
    st.info("Nenhuma ficha de avaliação configurada para este PPG.")
    st.stop()

st.write("Estas fichas são carregadas automaticamente para Artigos e PTTs.")

order = ["articles", "ptts"]
for key in order:
    form = forms.get(key)
    if not form:
        continue
    with st.expander(form.get("name", key).strip() or key, expanded=True):
        if key == "ptts" and form.get("ptt_types"):
            st.caption("Tipos de PTT contemplados: " + ", ".join(form["ptt_types"]))

        rows = []
        for criterion in form.get("criteria", []):
            rows.append(
                {
                    "Critério": criterion.get("name"),
                    "Descrição": criterion.get("description"),
                    "Peso": criterion.get("weight"),
                    "Tipo de resposta": criterion.get("response_type"),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.success("Fichas carregadas com sucesso para visualização.")
