"""Simple role-based access control helper for the demo context."""
from __future__ import annotations

import streamlit as st

from demo_context import current_profile


ROLE_PERMS = {
    "coordenador": {"ver", "criar", "editar", "apagar", "admin"},
    "orientador": {"ver", "criar", "editar"},
    "mestrando": {"ver", "criar", "editar"},
}


def can(action: str) -> bool:
    role = current_profile() if hasattr(st, "session_state") else None
    if not role:
        return False
    return action in ROLE_PERMS.get(role, set())


__all__ = ["can", "ROLE_PERMS"]
