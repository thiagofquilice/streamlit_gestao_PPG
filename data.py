"""Facade layer for the demo in-memory store."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from demo_context import current_ppg
from demo_seed import ensure_demo_db
from demo_store import (
    _delete,
    _upsert,
    articles_by_dissertation,
    articles_by_project,
    export_db_json,
    get_by_id,
    get_db,
    import_db_json,
    list_articles,
    list_dissertations,
    list_lines,
    list_people,
    list_projects,
    list_ptts,
    mestrandos_by_orientador,
    next_id,
    orientadores_by_line,
    ptts_by_dissertation,
    ptts_by_project,
    reset_db,
)


ensure_demo_db()


def list_ppgs() -> List[Dict[str, Any]]:
    return get_db().get("ppgs", [])


def update_ppg(ppg_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    for row in db.get("ppgs", []):
        if row.get("id") == ppg_id:
            row.update(payload)
            return row
    raise ValueError("PPG não encontrado")


# Research lines

def list_research_lines(ppg_id: str) -> List[Dict[str, Any]]:
    return list_lines(ppg_id)


def add_research_line(ppg_id: str, name: str, description: str) -> Dict[str, Any]:
    return _upsert(
        "research_lines",
        {"id": next_id("line"), "ppg_id": ppg_id, "name": name, "description": description},
    )


def update_research_line(line_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["id"] = line_id
    return _upsert("research_lines", payload)


def delete_research_line(line_id: str) -> None:
    _delete("research_lines", line_id)


# People

def list_ppg_members(ppg_id: str) -> List[Dict[str, Any]]:
    members: List[Dict[str, Any]] = []
    for person in list_people(ppg_id):
        members.append(
            {
                **person,
                "user_id": person.get("id"),
                "display_name": person.get("name"),
                "label": person.get("name"),
                "role": person.get("role"),
            }
        )
    return members


def upsert_person(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload.get("id"):
        payload["id"] = next_id("person")
    return _upsert("people", payload)


# Projects

def create_project(ppg_id: str, name: str, description: Optional[str], line_id: Optional[str], status: str) -> Dict[str, Any]:
    return _upsert(
        "projects",
        {
            "id": next_id("proj"),
            "ppg_id": ppg_id,
            "name": name,
            "description": description,
            "line_id": line_id,
            "status": status,
            "orientadores_ids": [],
            "mestrandos_ids": [],
        },
    )


def update_project(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["id"] = project_id
    project = _upsert("projects", payload)
    return project


def delete_project(project_id: str) -> None:
    _delete("projects", project_id)
    # remove links from articles/dissertations/ptts
    for collection in ["articles", "dissertations", "ptts"]:
        for row in get_db().get(collection, []):
            if row.get("project_id") == project_id:
                row["project_id"] = None


def set_project_orientadores(project_id: str, orientadores: List[str]) -> None:
    project = get_by_id("projects", project_id)
    if project is not None:
        project["orientadores_ids"] = orientadores


def set_project_mestrandos(project_id: str, mestrandos: List[str]) -> None:
    project = get_by_id("projects", project_id)
    if project is not None:
        project["mestrandos_ids"] = mestrandos


def list_project_dissertations(project_id: str) -> List[Dict[str, Any]]:
    return [d for d in list_dissertations(current_ppg() or "") if d.get("project_id") == project_id]


def list_project_articles(project_id: str) -> List[Dict[str, Any]]:
    return articles_by_project(project_id)


def list_project_ptts(project_id: str) -> List[Dict[str, Any]]:
    return ptts_by_project(project_id)


def get_project_orientadores(project_id: str) -> List[Dict[str, Any]]:
    proj = get_by_id("projects", project_id) or {}
    ids = proj.get("orientadores_ids", [])
    return [p for p in get_db().get("people", []) if p.get("id") in ids]


def get_project_mestrandos(project_id: str) -> List[Dict[str, Any]]:
    proj = get_by_id("projects", project_id) or {}
    ids = proj.get("mestrandos_ids", [])
    return [p for p in get_db().get("people", []) if p.get("id") in ids]


# Dissertations

def upsert_dissertation(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload.get("id"):
        payload["id"] = next_id("diss")
    diss = _upsert("dissertations", payload)
    _sync_dissertation_links(diss)
    return diss


def delete_dissertation(dissertation_id: str) -> None:
    _delete("dissertations", dissertation_id)
    for article in get_db().get("articles", []):
        if article.get("dissertation_id") == dissertation_id:
            article["dissertation_id"] = None
    for ptt in get_db().get("ptts", []):
        if ptt.get("dissertation_id") == dissertation_id:
            ptt["dissertation_id"] = None


def _sync_dissertation_links(dissertation: Dict[str, Any]) -> None:
    diss_id = dissertation.get("id")
    desired_articles = set(dissertation.get("artigos_ids", []))
    desired_ptts = set(dissertation.get("ptts_ids", []))
    for article in get_db().get("articles", []):
        if article.get("dissertation_id") == diss_id and article.get("id") not in desired_articles:
            article["dissertation_id"] = None
        if article.get("id") in desired_articles:
            article["dissertation_id"] = diss_id
    for ptt in get_db().get("ptts", []):
        if ptt.get("dissertation_id") == diss_id and ptt.get("id") not in desired_ptts:
            ptt["dissertation_id"] = None
        if ptt.get("id") in desired_ptts:
            ptt["dissertation_id"] = diss_id


# Articles

def upsert_article(payload: Dict[str, Any]) -> Dict[str, Any]:
    is_new = not payload.get("id")
    if is_new:
        payload["id"] = next_id("art")
    article = _upsert("articles", payload)
    _maybe_attach_to_dissertation(article)
    return article


def _maybe_attach_to_dissertation(article: Dict[str, Any]) -> None:
    diss_id = article.get("dissertation_id")
    if diss_id:
        diss = get_by_id("dissertations", diss_id)
        if diss:
            ids = set(diss.get("artigos_ids", []))
            ids.add(article["id"])
            diss["artigos_ids"] = list(ids)
    for diss in get_db().get("dissertations", []):
        if diss.get("id") != diss_id and article.get("id") in diss.get("artigos_ids", []):
            diss["artigos_ids"] = [aid for aid in diss.get("artigos_ids", []) if aid != article.get("id")]


# PTTs

def upsert_ptt(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload.get("id"):
        payload["id"] = next_id("ptt")
    ptt = _upsert("ptts", payload)
    _maybe_attach_ptt_to_dissertation(ptt)
    return ptt


def _maybe_attach_ptt_to_dissertation(ptt: Dict[str, Any]) -> None:
    diss_id = ptt.get("dissertation_id")
    if diss_id:
        diss = get_by_id("dissertations", diss_id)
        if diss:
            ids = set(diss.get("ptts_ids", []))
            ids.add(ptt["id"])
            diss["ptts_ids"] = list(ids)
    for diss in get_db().get("dissertations", []):
        if diss.get("id") != diss_id and ptt.get("id") in diss.get("ptts_ids", []):
            diss["ptts_ids"] = [pid for pid in diss.get("ptts_ids", []) if pid != ptt.get("id")]


__all__ = [name for name in globals() if not name.startswith("_")]
