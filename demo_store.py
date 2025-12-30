"""In-memory data store helpers backed by ``st.session_state['db']``."""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

import streamlit as st

from demo_context import current_ppg
from demo_seed import ensure_demo_db, init_demo_db

STANDARD_STATUSES = {"planejado", "em_execucao", "concluido"}
STATUS_SYNONYMS = {
    "em_andamento": "em_execucao",
    "em andamento": "em_execucao",
    "andamento": "em_execucao",
    "em_curso": "em_execucao",
    "em curso": "em_execucao",
    "submetido": "em_execucao",
    "em_revisao": "em_execucao",
    "planejamento": "planejado",
    "rascunho": "planejado",
    "aceito": "concluido",
    "publicado": "concluido",
    "finalizado": "concluido",
}


def get_db() -> Dict[str, List[dict]]:
    ensure_demo_db()
    return st.session_state["db"]


def reset_db() -> None:
    st.session_state["db"] = init_demo_db()


def export_db_json() -> str:
    return json.dumps(get_db(), indent=2, ensure_ascii=False)


def import_db_json(file) -> None:
    if not file:
        return
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    st.session_state["db"] = json.loads(content)


def next_id(prefix: str) -> str:
    ensure_demo_db()
    counters = st.session_state.setdefault("id_counters", {})
    counters[prefix] = counters.get(prefix, 0) + 1
    return f"{prefix}-{counters[prefix]}"


def _filter_by_ppg(items: Iterable[dict], ppg_id: str) -> List[dict]:
    return [item for item in items if item.get("ppg_id") == ppg_id]


def list_people(ppg_id: str, role: Optional[str] = None) -> List[dict]:
    people = _filter_by_ppg(get_db().get("people", []), ppg_id)
    if role:
        return [p for p in people if p.get("role") == role]
    return people


def list_lines(ppg_id: str) -> List[dict]:
    return _filter_by_ppg(get_db().get("research_lines", []), ppg_id)


def list_projects(ppg_id: str) -> List[dict]:
    return _filter_by_ppg(get_db().get("projects", []), ppg_id)


def list_dissertations(ppg_id: str) -> List[dict]:
    return [
        _ensure_standard_status(row, "dissertations")
        for row in _filter_by_ppg(get_db().get("dissertations", []), ppg_id)
    ]


def list_articles(ppg_id: str) -> List[dict]:
    return [
        _ensure_standard_status(row, "articles")
        for row in _filter_by_ppg(get_db().get("articles", []), ppg_id)
    ]


def list_ptts(ppg_id: str) -> List[dict]:
    return [
        _ensure_standard_status(row, "ptts")
        for row in _filter_by_ppg(get_db().get("ptts", []), ppg_id)
    ]


def get_evaluation_forms() -> dict:
    return get_db().get("evaluation_forms", {})


def list_evaluations(
    target_type: Optional[str] = None, target_id: Optional[str] = None, ppg_id: Optional[str] = None
) -> List[dict]:
    ppg = ppg_id or current_ppg() or (get_db().get("ppgs", [{}])[0].get("id"))
    evaluations = _filter_by_ppg(get_db().get("evaluations", []), ppg)
    if target_type:
        evaluations = [ev for ev in evaluations if ev.get("target_type") == target_type]
    if target_id:
        evaluations = [ev for ev in evaluations if ev.get("target_id") == target_id]
    return evaluations


def upsert_evaluation(payload: dict) -> dict:
    if not payload.get("id"):
        payload["id"] = next_id("eval")
    return _upsert("evaluations", payload)


def add_evaluation(payload: dict) -> dict:
    return upsert_evaluation(payload)


def stats_evaluations(target_type: str, target_id: str, ppg_id: Optional[str] = None) -> Tuple[int, Optional[float], Optional[float], Optional[str]]:
    evaluations = list_evaluations(target_type=target_type, target_id=target_id, ppg_id=ppg_id)
    if not evaluations:
        return 0, None, None, None
    scores = [ev.get("final_score") for ev in evaluations if ev.get("final_score") is not None]
    avg = round(sum(scores) / len(scores), 2) if scores else None
    latest = sorted(evaluations, key=lambda ev: ev.get("created_at", ""))[-1]
    return len(evaluations), avg, latest.get("final_score"), latest.get("created_at")


def get_by_id(entity: str, entity_id: str) -> Optional[dict]:
    return next((row for row in get_db().get(entity, []) if row.get("id") == entity_id), None)


def orientadores_by_line(line_id: str) -> List[dict]:
    return [
        p
        for p in get_db().get("people", [])
        if line_id in p.get("linhas_de_pesquisa_ids", []) or line_id in p.get("linhas_ids", [])
    ]


def mestrandos_by_orientador(orientador_id: str) -> List[dict]:
    return [p for p in get_db().get("people", []) if p.get("role") == "mestrando" and p.get("orientador_id") == orientador_id]


def dissertations_by_project(project_id: str) -> List[dict]:
    return [d for d in get_db().get("dissertations", []) if d.get("project_id") == project_id]


def articles_by_project(project_id: str) -> List[dict]:
    return [a for a in get_db().get("articles", []) if a.get("project_id") == project_id]


def ptts_by_project(project_id: str) -> List[dict]:
    return [p for p in get_db().get("ptts", []) if p.get("project_id") == project_id]


def articles_by_dissertation(dissertation_id: str) -> List[dict]:
    return [a for a in get_db().get("articles", []) if a.get("dissertation_id") == dissertation_id]


def ptts_by_dissertation(dissertation_id: str) -> List[dict]:
    return [p for p in get_db().get("ptts", []) if p.get("dissertation_id") == dissertation_id]


def _upsert(collection: str, payload: dict) -> dict:
    payload = _ensure_standard_status(payload, collection)
    db = get_db()
    rows = db.setdefault(collection, [])
    existing = get_by_id(collection, payload.get("id"))
    if existing:
        existing.update(payload)
        return existing
    rows.append(payload)
    return payload


def _delete(collection: str, entity_id: str) -> None:
    db = get_db()
    db[collection] = [row for row in db.get(collection, []) if row.get("id") != entity_id]


def _ensure_standard_status(payload: dict, collection: str) -> dict:
    if collection not in {"dissertations", "articles", "ptts"}:
        return payload
    status_value = str(payload.get("status") or "").lower()
    normalized = STATUS_SYNONYMS.get(status_value, status_value)
    if normalized not in STANDARD_STATUSES:
        normalized = "planejado"
    payload["status"] = normalized
    return payload


__all__ = [
    "get_db",
    "reset_db",
    "export_db_json",
    "import_db_json",
    "next_id",
    "list_people",
    "list_lines",
    "list_projects",
    "list_dissertations",
    "list_articles",
    "list_ptts",
    "list_evaluations",
    "get_by_id",
    "orientadores_by_line",
    "mestrandos_by_orientador",
    "dissertations_by_project",
    "articles_by_project",
    "ptts_by_project",
    "articles_by_dissertation",
    "ptts_by_dissertation",
    "_upsert",
    "_delete",
    "add_evaluation",
    "stats_evaluations",
]
