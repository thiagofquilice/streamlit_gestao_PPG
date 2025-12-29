"""
Data helpers for interacting with Supabase tables using row-level security (RLS).

IMPORTANT:
- All queries must be executed with an authenticated Supabase session; otherwise RLS will block access.
- This module expects `st.session_state["auth"]` to contain:
  - user_id
  - email
  - access_token
  - refresh_token
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st
from postgrest import APIError

from auth import get_authed_client


def _client():
    """Return an authenticated Supabase client with the current user session applied."""
    c = get_authed_client()
    if c is None:
        st.error("Sessão não encontrada (token ausente). Faça login novamente.")
        st.stop()
    return c


# ---------- Memberships ----------

def load_memberships(user_id: str) -> List[Dict[str, Any]]:
    """Return PPG memberships for the given user."""
    response = (
        _client()
        .table("memberships")
        .select("ppg_id, role")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data or []


def _profiles_map(user_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not user_ids:
        return {}
    response = (
        _client()
        .table("profiles")
        .select("user_id, email, display_name")
        .in_("user_id", user_ids)
        .execute()
    )
    data = response.data or []
    return {row["user_id"]: row for row in data}


def list_ppg_members(ppg_id: str) -> List[Dict[str, Any]]:
    """Return all memberships for a given PPG (role + user_id + profile info)."""
    response = (
        _client()
        .table("memberships")
        .select("user_id, role")
        .eq("ppg_id", ppg_id)
        .order("role")
        .execute()
    )
    rows = response.data or []
    profile_map = _profiles_map([row["user_id"] for row in rows])
    for row in rows:
        profile = profile_map.get(row["user_id"], {})
        row["display_name"] = profile.get("display_name") or profile.get("email") or row["user_id"]
        row["email"] = profile.get("email")
    return rows


# ---------- Research lines ----------

def list_research_lines(ppg_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("research_lines")
        .select("id, name, description, created_at")
        .eq("ppg_id", ppg_id)
        .order("created_at")
        .execute()
    )
    return response.data or []


def add_research_line(ppg_id: str, name: str, description: str) -> Dict[str, Any]:
    payload = {"ppg_id": ppg_id, "name": name, "description": description}
    response = _client().table("research_lines").insert(payload).execute()
    return (response.data or [{}])[0]


def delete_research_line(line_id: Any) -> None:
    _client().table("research_lines").delete().eq("id", line_id).execute()


# ---------- SWOT ----------

def list_swot_items(ppg_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("swot_items")
        .select("id, category, description, created_at")
        .eq("ppg_id", ppg_id)
        .order("created_at")
        .execute()
    )
    return response.data or []


def add_swot_item(ppg_id: str, category: str, description: str) -> Dict[str, Any]:
    payload = {"ppg_id": ppg_id, "category": category, "description": description}
    response = _client().table("swot_items").insert(payload).execute()
    return (response.data or [{}])[0]


def delete_swot_item(item_id: Any) -> None:
    _client().table("swot_items").delete().eq("id", item_id).execute()


# ---------- Projects ----------

def list_projects(ppg_id: str) -> List[Dict[str, Any]]:
    try:
        response = (
            _client()
            .table("projects")
            .select("id, name, description, parent_project_id, created_at, ppg_id")
            .eq("ppg_id", ppg_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except APIError:
        st.error(
            "Erro ao consultar projetos. Rode o script db/ddl.sql no Supabase para atualizar o schema/policies."
        )
        return []


def create_project(
    ppg_id: str,
    name: str,
    description: Optional[str] = None,
    parent_project_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "ppg_id": ppg_id,
        "name": name,
        "description": description,
        "parent_project_id": parent_project_id,
    }
    response = _client().table("projects").insert(payload).execute()
    return (response.data or [{}])[0]


def update_project(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = _client().table("projects").update(payload).eq("id", project_id).execute()
    return (response.data or [{}])[0]


def delete_project(project_id: str) -> None:
    _client().table("projects").delete().eq("id", project_id).execute()


def get_project_orientadores(project_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("project_orientadores")
        .select("user_id")
        .eq("project_id", project_id)
        .execute()
    )
    user_ids = [row["user_id"] for row in (response.data or [])]
    profiles = _profiles_map(user_ids)
    return [
        {
            "user_id": uid,
            "display_name": profiles.get(uid, {}).get("display_name")
            or profiles.get(uid, {}).get("email")
            or uid,
            "email": profiles.get(uid, {}).get("email"),
        }
        for uid in user_ids
    ]


def get_project_mestrandos(project_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("project_mestrandos")
        .select("user_id")
        .eq("project_id", project_id)
        .execute()
    )
    user_ids = [row["user_id"] for row in (response.data or [])]
    profiles = _profiles_map(user_ids)
    return [
        {
            "user_id": uid,
            "display_name": profiles.get(uid, {}).get("display_name")
            or profiles.get(uid, {}).get("email")
            or uid,
            "email": profiles.get(uid, {}).get("email"),
        }
        for uid in user_ids
    ]


def set_project_orientadores(project_id: str, user_ids: List[str]) -> None:
    client = _client()
    client.table("project_orientadores").delete().eq("project_id", project_id).execute()
    if not user_ids:
        return
    rows = [{"project_id": project_id, "user_id": uid} for uid in user_ids]
    client.table("project_orientadores").insert(rows).execute()


def set_project_mestrandos(project_id: str, user_ids: List[str]) -> None:
    client = _client()
    client.table("project_mestrandos").delete().eq("project_id", project_id).execute()
    if not user_ids:
        return
    rows = [{"project_id": project_id, "user_id": uid} for uid in user_ids]
    client.table("project_mestrandos").insert(rows).execute()


def list_project_dissertations(project_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("dissertations")
        .select("id, title, project_id")
        .eq("project_id", project_id)
        .execute()
    )
    return response.data or []


def list_project_articles(project_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("articles")
        .select("id, title, project_id")
        .eq("project_id", project_id)
        .execute()
    )
    return response.data or []


def list_project_ptts(project_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("ptts")
        .select("id, title, project_id")
        .eq("project_id", project_id)
        .execute()
    )
    return response.data or []


# ---------- Articles ----------

def list_articles(ppg_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("articles")
        .select(
            "id, title, authors, year, status, created_at, project_id, orientador_user_id, mestrando_user_id"
        )
        .eq("ppg_id", ppg_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def upsert_article(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert or update an article.
    Expected keys (minimum): ppg_id, title
    Optional: authors, year, status, etc.
    """
    response = _client().table("articles").upsert(data, returning="representation").execute()
    return (response.data or [{}])[0]


# ---------- Dissertations ----------

def list_dissertations(ppg_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("dissertations")
        .select("id, title, summary, project_id, created_at")
        .eq("ppg_id", ppg_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def upsert_dissertation(data: Dict[str, Any]) -> Dict[str, Any]:
    response = (
        _client()
        .table("dissertations")
        .upsert(data, returning="representation")
        .execute()
    )
    return (response.data or [{}])[0]


# ---------- PTTs ----------

def list_ptts(ppg_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("ptts")
        .select("id, title, summary, project_id, created_at")
        .eq("ppg_id", ppg_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def upsert_ptt(data: Dict[str, Any]) -> Dict[str, Any]:
    response = _client().table("ptts").upsert(data, returning="representation").execute()
    return (response.data or [{}])[0]


__all__ = [name for name in globals() if not name.startswith("_")]
