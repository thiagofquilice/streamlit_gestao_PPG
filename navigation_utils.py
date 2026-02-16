from __future__ import annotations

import streamlit as st

_NAV_TARGET_KEY = "_navigation_target"


def navigate_to(page_path: str, target_type: str, target_id: str | None) -> None:
    if not target_id:
        return
    st.session_state[_NAV_TARGET_KEY] = {"type": target_type, "id": target_id}
    if hasattr(st, "switch_page"):
        st.switch_page(page_path)


def consume_nav_target(target_type: str) -> str | None:
    target = st.session_state.get(_NAV_TARGET_KEY)
    if not isinstance(target, dict) or target.get("type") != target_type:
        return None
    st.session_state.pop(_NAV_TARGET_KEY, None)
    return target.get("id")
