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
    # Avoid selecting columns that may not exist (id/created_at) unless you're sure they do.
    response = (
        _client()
        .table("memberships")
        .select("ppg_id, role")
        .eq("user_id", user_id)
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


# ---------- Articles ----------

def list_articles(ppg_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("articles")
        .select("id, title, authors, year, status, created_at")
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

