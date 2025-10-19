"""Role based access helpers."""
from __future__ import annotations

from typing import Set

ROLE_PERMISSIONS: dict[str, Set[str]] = {
    "coordenador": {
        "view_overview",
        "manage_ppg_admin",
        "manage_projects",
        "manage_dissertations",
        "manage_articles",
        "manage_ptts",
        "manage_evaluations",
        "view_reports",
    },
    "professor": {
        "view_overview",
        "manage_projects",
        "manage_dissertations",
        "manage_articles",
        "manage_ptts",
        "manage_evaluations",
        "view_reports",
    },
    "mestrando": {
        "view_overview",
        "view_projects",
        "view_dissertations",
        "submit_articles",
        "submit_ptts",
        "view_reports",
    },
}


def can(role: str, action: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(role, set())
    return action in permissions or action in {"view_overview"}


def allowed_actions(role: str) -> Set[str]:
    return ROLE_PERMISSIONS.get(role, set())
