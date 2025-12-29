from __future__ import annotations

from dataclasses import dataclass
import os
import streamlit as st
from supabase import create_client

@dataclass(frozen=True)
class AuthState:
    user_id: str
    email: str
    access_token: str
    refresh_token: str

def _supabase_url() -> str:
    return os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")

def _supabase_key() -> str:
    return os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY", "")

def get_client():
    url = _supabase_url()
    key = _supabase_key()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL e SUPABASE_ANON_KEY não configurados (Secrets/ENV).")
    # IMPORTANTE: não cacheie o client para Auth em multipage
    return create_client(url, key)

def login(email: str, password: str) -> AuthState | None:
    supa = get_client()
    res = supa.auth.sign_in_with_password({"email": email, "password": password})

    # Se falhar, o supabase-py tende a levantar exception; mas por segurança:
    if not res or not getattr(res, "user", None) or not getattr(res, "session", None):
        return None

    state = AuthState(
        user_id=res.user.id,
        email=res.user.email,
        access_token=res.session.access_token,
        refresh_token=res.session.refresh_token,
    )

    # Persistir sessão no Streamlit
    st.session_state["auth"] = {
        "user_id": state.user_id,
        "email": state.email,
        "access_token": state.access_token,
        "refresh_token": state.refresh_token,
    }
    return state

def get_auth_state() -> AuthState | None:
    a = st.session_state.get("auth")
    if not a:
        return None
    # Se você já salvou sem tokens antes, isso evita crash:
    if not a.get("access_token") or not a.get("refresh_token"):
        return None
    return AuthState(
        user_id=a["user_id"],
        email=a["email"],
        access_token=a["access_token"],
        refresh_token=a["refresh_token"],
    )

def get_authed_client():
    """Client já com sessão aplicada (RLS funciona)."""
    state = get_auth_state()
    if not state:
        return None
    supa = get_client()
    supa.auth.set_session(state.access_token, state.refresh_token)
    return supa

def logout() -> None:
    try:
        supa = get_client()
        supa.auth.sign_out()
    except Exception:
        pass
    for k in ["auth", "ppg_id", "role"]:
        st.session_state.pop(k, None)

