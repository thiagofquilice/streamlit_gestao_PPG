"""Data helpers for interacting with Supabase tables using row-level security."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from auth import get_client


def _client():
    return get_client()


def load_memberships(user_id: str) -> List[Dict[str, Any]]:
    """Return PPG memberships for the given user."""

    response = (
        _client()
        .table("memberships")
        .select("id, ppg_id, role")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    return response.data or []


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
    response = _client().table("articles").upsert(data, returning="representation").execute()
    return (response.data or [{}])[0]


__all__ = [name for name in globals() if not name.startswith("_")]
