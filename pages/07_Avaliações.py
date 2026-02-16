from __future__ import annotations

from typing import Any, Dict, List

from demo_seed import ensure_demo_db
import streamlit as st

from layout import configure_page, render_sidebar

from data import get_admin_evaluation_forms, upsert_admin_form
from demo_context import current_ppg, current_profile

ensure_demo_db()

configure_page()
render_sidebar()

st.title("Avaliações")
st.caption("Crie e ajuste os modelos de avaliação para Dissertação, Artigo e PTT.")

ppg_id = current_ppg()
role = current_profile()
if not ppg_id or not role:
    st.warning("Faça login e selecione um PPG para continuar.")
    st.stop()

if role != "coordenador":
    st.info("Somente coordenação pode alterar os modelos. Você pode apenas visualizar.")

forms = get_admin_evaluation_forms()


def _default_scale() -> Dict[str, Any]:
    return {
        "metric_name": "Qualidade",
        "levels": [
            {"label": "Insuficiente", "value": 1},
            {"label": "Regular", "value": 2},
            {"label": "Bom", "value": 3},
            {"label": "Muito bom", "value": 4},
            {"label": "Excelente", "value": 5},
        ],
    }


def _default_form(key: str, kind: str, title: str) -> Dict[str, Any]:
    return {
        "id": f"f_{key}",
        "name": title,
        "kind": kind,
        "scale": _default_scale(),
        "criteria": [
            {
                "id": f"c_{key}_1",
                "name": "Critério 1",
                "description": "",
                "weight": 1.0,
                "response_type": "scale_custom",
            }
        ],
    }


def _normalize_form(form_key: str, kind: str, title: str) -> Dict[str, Any]:
    form = forms.get(form_key) or _default_form(form_key, kind, title)
    if "scale" not in form:
        form["scale"] = _default_scale()
    if not form["scale"].get("levels"):
        form["scale"]["levels"] = _default_scale()["levels"]
    if "metric_name" not in form["scale"]:
        form["scale"]["metric_name"] = "Qualidade"
    return form


def _render_model_editor(form_key: str, label: str, kind: str) -> None:
    form = _normalize_form(form_key, kind, f"Modelo de avaliação — {label}")

    with st.expander(f"Modelo: {label}", expanded=True):
        model_name = st.text_input("Nome do modelo", value=form.get("name", ""), key=f"name_{form_key}")

        st.markdown("**Escala de avaliação**")
        metric_name = st.text_input(
            "Nome da métrica da escala",
            value=form.get("scale", {}).get("metric_name", "Qualidade"),
            key=f"metric_{form_key}",
            help="Exemplo: Qualidade, Aderência, Maturidade.",
        )

        levels = form.get("scale", {}).get("levels", [])
        level_count = st.number_input(
            "Quantidade de níveis",
            min_value=2,
            max_value=10,
            value=len(levels) if levels else 5,
            step=1,
            key=f"level_count_{form_key}",
        )

        level_rows: List[Dict[str, Any]] = []
        for idx in range(int(level_count)):
            current = levels[idx] if idx < len(levels) else {"label": f"Nível {idx + 1}", "value": idx + 1}
            col1, col2 = st.columns([2, 1])
            with col1:
                level_label = st.text_input(
                    f"Rótulo do nível {idx + 1}",
                    value=str(current.get("label", f"Nível {idx + 1}")),
                    key=f"level_label_{form_key}_{idx}",
                )
            with col2:
                level_value = st.number_input(
                    f"Valor {idx + 1}",
                    value=float(current.get("value", idx + 1)),
                    step=1.0,
                    key=f"level_value_{form_key}_{idx}",
                )
            level_rows.append({"label": level_label, "value": float(level_value)})

        st.markdown("**Itens de avaliação (critérios)**")
        criteria = form.get("criteria", [])
        criteria_count = st.number_input(
            "Quantidade de itens de avaliação",
            min_value=1,
            max_value=30,
            value=len(criteria) if criteria else 1,
            step=1,
            key=f"criteria_count_{form_key}",
        )

        criteria_rows: List[Dict[str, Any]] = []
        for idx in range(int(criteria_count)):
            current = criteria[idx] if idx < len(criteria) else {}
            st.markdown(f"**Item {idx + 1}**")
            c_name = st.text_input(
                "Nome do item",
                value=str(current.get("name", f"Critério {idx + 1}")),
                key=f"criterion_name_{form_key}_{idx}",
            )
            c_description = st.text_area(
                "Descrição do item",
                value=str(current.get("description", "")),
                key=f"criterion_desc_{form_key}_{idx}",
            )
            c_weight = st.number_input(
                "Peso",
                min_value=0.0,
                max_value=100.0,
                value=float(current.get("weight", 1.0)),
                step=0.5,
                key=f"criterion_weight_{form_key}_{idx}",
            )
            criteria_rows.append(
                {
                    "id": current.get("id", f"c_{form_key}_{idx + 1}"),
                    "name": c_name,
                    "description": c_description,
                    "weight": float(c_weight),
                    "response_type": "scale_custom",
                }
            )
            st.divider()

        if st.button(f"Salvar modelo {label}", type="primary", key=f"save_{form_key}", disabled=role != "coordenador"):
            payload = {
                "id": form.get("id") or f"f_{form_key}",
                "name": model_name.strip() or f"Modelo de avaliação — {label}",
                "kind": kind,
                "scale": {
                    "metric_name": metric_name.strip() or "Qualidade",
                    "levels": level_rows,
                },
                "criteria": criteria_rows,
            }
            if form_key == "ptts":
                payload["ptt_types"] = form.get("ptt_types", [])
            upsert_admin_form(form_key, payload)
            st.success(f"Modelo {label} salvo com sucesso.")
            st.rerun()

        st.caption(
            "Os critérios e a escala definidos aqui serão usados como referência para as avaliações desse tipo."
        )


_render_model_editor("dissertations", "Dissertação", "dissertacao")
_render_model_editor("articles", "Artigo", "artigo")
_render_model_editor("ptts", "PTT", "ptt")
