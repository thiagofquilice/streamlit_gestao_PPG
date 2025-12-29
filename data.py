"""
Data helpers for interacting with Supabase tables using row-level security (RLS).

IMPORTANT:
- All queries must be executed with an authenticated Supabase session; otherwise RLS will block access.
- This module expects `st.session_state["auth"]` to contain:
  - user_id
  - email
  - access_token
  - refresh_token

It also assumes your tables/columns follow the names used below:
- memberships: user_id, ppg_id, role  (optionally: id, created_at)
- research_lines: id, ppg_id, name, description, created_at
- swot_items: id, ppg_id, category, description, created_at
- articles: id, ppg_id, title, authors, year, status, created_at
- projects: id, ppg_id, title, description, start_date, end_date, status
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from auth import get_authed_client


def _client():
    """
    Return an authenticated Supabase client with the current user session applied.
    Stops the app if no authenticated session is present (to avoid silent RLS failures).
    """
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


def list_ppg_members(ppg_id: str) -> List[Dict[str, Any]]:
    """Return all memberships for a given PPG (role + user_id)."""
    response = (
        _client()
        .table("memberships")
        .select("user_id, role")
        .eq("ppg_id", ppg_id)
        .order("role")
        .execute()
    )
    return response.data or []


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
    response = (
        _client()
        .table("projects")
        .select("id, title, description, start_date, end_date, status, created_at, ppg_id")
        .eq("ppg_id", ppg_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def add_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = _client().table("projects").insert(payload).execute()
    return (response.data or [{}])[0]


def update_project(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = _client().table("projects").update(payload).eq("id", project_id).execute()
    return (response.data or [{}])[0]


def delete_project(project_id: str) -> None:
    _client().table("projects").delete().eq("id", project_id).execute()


def list_project_orientadores(project_id: str) -> List[str]:
    response = (
        _client().table("project_orientadores").select("user_id").eq("project_id", project_id).execute()
    )
    return [row["user_id"] for row in (response.data or [])]


def list_project_mestrandos(project_id: str) -> List[str]:
    response = _client().table("project_mestrandos").select("user_id").eq("project_id", project_id).execute()
    return [row["user_id"] for row in (response.data or [])]


def set_project_orientadores(project_id: str, ppg_id: str, user_ids: List[str]) -> None:
    client = _client()
    client.table("project_orientadores").delete().eq("project_id", project_id).execute()
    if not user_ids:
        return
    rows = [{"project_id": project_id, "user_id": uid, "ppg_id": ppg_id} for uid in user_ids]
    client.table("project_orientadores").insert(rows).execute()


def set_project_mestrandos(project_id: str, user_ids: List[str]) -> None:
    client = _client()
    client.table("project_mestrandos").delete().eq("project_id", project_id).execute()
    if not user_ids:
        return
    rows = [{"project_id": project_id, "user_id": uid} for uid in user_ids]
    client.table("project_mestrandos").insert(rows).execute()


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


__all__ = [name for name in globals() if not name.startswith("_")]
