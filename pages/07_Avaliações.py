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

st.title("Cadastro de Classificações e Avaliações")
st.caption(
    "Configure os catálogos auxiliares e os modelos de avaliação. "
    "Use os botões abaixo para abrir cada bloco de configuração."
)

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


def _normalize_values(values: List[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for value in values:
        label = str(value or "").strip()
        if not label:
            continue
        lowered = label.lower()
        if lowered in seen:
            continue
        normalized.append(label)
        seen.add(lowered)
    return normalized


def _default_journal_ratings() -> List[str]:
    return ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"]


def _render_ptt_types_editor() -> None:
    ptt_form = forms.get("ptts") or _default_form("ptts", "ptt", "Modelo de avaliação — PTT")
    st.markdown("### Tipos de PTT")
    st.info("Defina os tipos de PTT que aparecerão no cadastro de PTTs. Exemplo: Software, Relatório Técnico, Material Didático.")

    ptt_types = ptt_form.get("ptt_types") or []
    ptt_type_count = st.number_input(
        "Quantidade de tipos de PTT",
        min_value=1,
        max_value=30,
        value=len(ptt_types) if ptt_types else 1,
        step=1,
        key="ptt_type_count",
    )
    ptt_type_rows: List[str] = []
    for idx in range(int(ptt_type_count)):
        current_value = ptt_types[idx] if idx < len(ptt_types) else ""
        typed = st.text_input(
            f"Tipo de PTT {idx + 1}",
            value=str(current_value),
            key=f"ptt_type_{idx}",
        )
        ptt_type_rows.append(typed)

    if st.button("Salvar tipos de PTT", type="primary", key="save_ptt_types", disabled=role != "coordenador"):
        normalized_ptt_types = _normalize_values(ptt_type_rows)
        ptt_payload = {
            **ptt_form,
            "id": ptt_form.get("id") or "f_ptts",
            "name": ptt_form.get("name") or "Modelo de avaliação — PTT",
            "kind": ptt_form.get("kind") or "ptt",
            "scale": ptt_form.get("scale") or _default_scale(),
            "criteria": ptt_form.get("criteria") or _default_form("ptts", "ptt", "Modelo de avaliação — PTT")["criteria"],
            "ptt_types": normalized_ptt_types,
        }
        upsert_admin_form("ptts", ptt_payload)
        st.success("Tipos de PTT salvos com sucesso.")
        st.rerun()


def _render_journal_ratings_editor() -> None:
    article_form = forms.get("articles") or _default_form("articles", "artigo", "Modelo de avaliação — Artigo")
    st.markdown("### Classificação de Revistas")
    st.info("Cadastre classificações para artigos. Exemplo: A1, A2, B1, B2, C.")

    journal_ratings = article_form.get("journal_ratings") or _default_journal_ratings()
    ratings_count = st.number_input(
        "Quantidade de classificações de revista",
        min_value=1,
        max_value=40,
        value=len(journal_ratings) if journal_ratings else len(_default_journal_ratings()),
        step=1,
        key="journal_ratings_count",
    )
    rating_rows: List[str] = []
    for idx in range(int(ratings_count)):
        current_value = journal_ratings[idx] if idx < len(journal_ratings) else ""
        typed = st.text_input(
            f"Classificação da revista {idx + 1}",
            value=str(current_value),
            key=f"journal_rating_{idx}",
        )
        rating_rows.append(typed)

    if st.button("Salvar classificações de revista", type="primary", key="save_journal_ratings", disabled=role != "coordenador"):
        normalized_ratings = _normalize_values(rating_rows)
        article_payload = {
            **article_form,
            "id": article_form.get("id") or "f_articles",
            "name": article_form.get("name") or "Modelo de avaliação — Artigo",
            "kind": article_form.get("kind") or "artigo",
            "scale": article_form.get("scale") or _default_scale(),
            "criteria": article_form.get("criteria") or _default_form("articles", "artigo", "Modelo de avaliação — Artigo")["criteria"],
            "journal_ratings": normalized_ratings or _default_journal_ratings(),
        }
        upsert_admin_form("articles", article_payload)
        st.success("Classificações de revista salvas com sucesso.")
        st.rerun()


def _render_model_editor(form_key: str, label: str, kind: str) -> None:
    form = _normalize_form(form_key, kind, f"Modelo de avaliação — {label}")

    st.markdown(f"### Avaliação de {label}")
    st.info(
        "Configure a escala e os critérios usados no cálculo da nota final. "
        "Exemplo: Escala 'Qualidade' com níveis de 1 a 5; critério 'Originalidade' com peso 2."
    )

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
        if form_key == "articles":
            payload["journal_ratings"] = form.get("journal_ratings", _default_journal_ratings())
        upsert_admin_form(form_key, payload)
        st.success(f"Modelo {label} salvo com sucesso.")
        st.rerun()

    st.caption("Esses critérios serão usados no botão 'Avaliar' dentro dos cards de Dissertação, Artigo e PTT.")


button_labels = [
    ("Tipos de PTT", "section_tipos_ptt"),
    ("Classificação de Revistas", "section_class_revistas"),
    ("Avaliação de Dissertação", "section_eval_dissertacao"),
    ("Avaliação de Artigo", "section_eval_artigo"),
    ("Avaliação de PTT", "section_eval_ptt"),
]

if "active_classification_section" not in st.session_state:
    st.session_state["active_classification_section"] = button_labels[0][1]

cols = st.columns(len(button_labels))
for col, (label, section_key) in zip(cols, button_labels):
    with col:
        if st.button(label, key=f"btn_{section_key}", use_container_width=True):
            st.session_state["active_classification_section"] = section_key

active = st.session_state.get("active_classification_section")
st.divider()

if active == "section_tipos_ptt":
    _render_ptt_types_editor()
elif active == "section_class_revistas":
    _render_journal_ratings_editor()
elif active == "section_eval_dissertacao":
    _render_model_editor("dissertations", "Dissertação", "dissertacao")
elif active == "section_eval_artigo":
    _render_model_editor("articles", "Artigo", "artigo")
elif active == "section_eval_ptt":
    _render_model_editor("ptts", "PTT", "ptt")
