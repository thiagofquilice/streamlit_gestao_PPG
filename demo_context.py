"""Session context helpers for the demo app."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from demo_seed import ensure_demo_db


def get_ctx() -> dict:
    ensure_demo_db()
    return st.session_state["ctx"]


def set_profile(profile: str) -> None:
    ctx = get_ctx()
    ctx["profile"] = profile
    if profile == "coordenador":
        ctx["person_id"] = None


def set_person(person_id: Optional[str]) -> None:
    ctx = get_ctx()
    ctx["person_id"] = person_id


def set_ppg(ppg_id: str) -> None:
    ctx = get_ctx()
    ctx["ppg_id"] = ppg_id


def current_profile() -> str:
    return get_ctx().get("profile", "coordenador")


def current_person() -> Optional[str]:
    return get_ctx().get("person_id")


def current_ppg() -> Optional[str]:
    return get_ctx().get("ppg_id")


__all__ = [
    "get_ctx",
    "set_profile",
    "set_person",
    "set_ppg",
    "current_profile",
    "current_person",
    "current_ppg",
]
