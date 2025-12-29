"""Supabase authentication helpers for PPG Manager."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import streamlit as st
from supabase import Client, create_client


@dataclass
class AuthState:
    """Simple container for logged in user metadata."""

    user_id: str
    email: str


def _read_supabase_settings() -> tuple[Optional[str], Optional[str]]:
    """Load Supabase settings from environment variables or Streamlit secrets."""

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")

    if (not url or not key) and hasattr(st, "secrets"):
        url = url or st.secrets.get("SUPABASE_URL")
        key = key or st.secrets.get("SUPABASE_ANON_KEY")

    return url, key


@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    """Return a cached Supabase client instance."""

    url, key = _read_supabase_settings()
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. Configure SUPABASE_URL and SUPABASE_ANON_KEY."
        )
    return create_client(url, key)


def get_auth_state() -> Optional[AuthState]:
    auth_dict = st.session_state.get("auth")
    if not auth_dict:
        return None
    return AuthState(user_id=auth_dict.get("user_id", ""), email=auth_dict.get("email", ""))


def login(email: str, password: str) -> Optional[AuthState]:
    """Authenticate the user through Supabase and persist the session state."""

    client = get_client()
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    session = response.session
    user = response.user
    if not session or not user:
        return None

    auth_state = AuthState(user_id=user.id, email=user.email or "")
    st.session_state["auth"] = {"user_id": auth_state.user_id, "email": auth_state.email}
    return auth_state


def logout() -> None:
    """Clear the local session state and invalidate the Supabase session."""

    client = get_client()
    client.auth.sign_out()
    st.session_state.pop("auth", None)
    st.session_state.pop("ppg_id", None)
    st.session_state.pop("role", None)
