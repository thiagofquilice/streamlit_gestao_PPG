"""Unified data access layer supporting Supabase and demo mode."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import streamlit as st

import data as supabase_data
import demo_data
from auth import AuthState, logout as supabase_logout


def is_demo_mode() -> bool:
    env_flag = os.environ.get("DEMO_MODE")
    if env_flag is None and hasattr(st, "secrets"):
        env_flag = st.secrets.get("DEMO_MODE")  # type: ignore[attr-defined]
    if env_flag is None:
        return False
    return str(env_flag).lower() == "true"


def _ensure_demo_seeded() -> None:
    if is_demo_mode():
        demo_data._db()  # ensures seeding


# -- Auth helpers ---------------------------------------------------------

def set_demo_auth(user_id: str, email: str) -> AuthState:
    auth_state = AuthState(user_id=user_id, email=email, access_token="demo")
    st.session_state["auth"] = {
        "user_id": auth_state.user_id,
        "email": auth_state.email,
        "access_token": auth_state.access_token,
    }
    return auth_state


def logout() -> None:
    if is_demo_mode():
        st.session_state.pop("auth", None)
        st.session_state.pop("ppg_id", None)
        st.session_state.pop("role", None)
        return
    supabase_logout()


# -- Memberships ----------------------------------------------------------

def load_memberships(user_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_memberships(user_id)
    return supabase_data.list_memberships(user_id)


def list_ppg_memberships(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_ppg_memberships(ppg_id)
    return supabase_data.list_ppg_memberships(ppg_id)


def create_user_and_membership(ppg_id: str, email: str, password: str, role: str) -> Dict[str, Any]:
    if is_demo_mode():
        raise RuntimeError("Cadastro de usuários indisponível no modo demonstração.")
    return supabase_data.create_user_and_membership(ppg_id, email, password, role)


def user_management_available() -> bool:
    if is_demo_mode():
        return False
    return supabase_data.user_management_available()


# -- Research lines, SWOT, objectives ------------------------------------

def list_research_lines(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_research_lines(ppg_id)
    return supabase_data.list_linhas(ppg_id)


def add_research_line(ppg_id: str, nome: str, descricao: str) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.add_research_line(ppg_id, nome, descricao)
    return supabase_data.upsert_record("linhas_pesquisa", {"ppg_id": ppg_id, "nome": nome, "descricao": descricao})


def remove_research_line(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_research_line(record_id)
        return
    supabase_data.delete_record("linhas_pesquisa", record_id)


def list_swot(ppg_id: str) -> Dict[str, List[Dict[str, Any]]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_swot(ppg_id)
    return supabase_data.list_swot(ppg_id)


def add_swot_item(ppg_id: str, categoria: str, descricao: str) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.add_swot_item(ppg_id, categoria, descricao)
    return supabase_data.upsert_record("swot", {"ppg_id": ppg_id, "categoria": categoria, "descricao": descricao})


def remove_swot_item(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_swot_item(record_id)
        return
    supabase_data.delete_record("swot", record_id)


def list_objectives(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_objectives(ppg_id)
    return supabase_data.list_objetivos(ppg_id)


def add_objective(ppg_id: str, ordem: int, descricao: str) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.add_objective(ppg_id, ordem, descricao)
    return supabase_data.upsert_record("objetivos", {"ppg_id": ppg_id, "ordem": ordem, "descricao": descricao})


def remove_objective(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_objective(record_id)
        return
    supabase_data.delete_record("objetivos", record_id)


# -- Projects, dissertations, outputs ------------------------------------

def list_projects(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_projects(ppg_id)
    return supabase_data.list_projetos(ppg_id)


def upsert_project(ppg_id: str, titulo: str, lider: str, status: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.upsert_project(ppg_id, titulo, lider, status, project_id)
    payload = {"ppg_id": ppg_id, "titulo": titulo, "lider": lider, "status": status}
    if project_id:
        payload["id"] = project_id
    return supabase_data.upsert_record("projetos", payload)


def remove_project(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_project(record_id)
        return
    supabase_data.delete_record("projetos", record_id)


def list_dissertations(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_dissertations(ppg_id)
    return supabase_data.list_dissertacoes(ppg_id)


def upsert_dissertation(
    ppg_id: str,
    titulo: str,
    autor: str,
    orientador: str,
    defesa_prevista: str,
    dissertation_id: Optional[str] = None,
) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.upsert_dissertation(ppg_id, titulo, autor, orientador, defesa_prevista, dissertation_id)
    payload = {
        "ppg_id": ppg_id,
        "titulo": titulo,
        "autor": autor,
        "orientador": orientador,
        "defesa_prevista": defesa_prevista,
    }
    if dissertation_id:
        payload["id"] = dissertation_id
    return supabase_data.upsert_record("dissertacoes", payload)


def remove_dissertation(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_dissertation(record_id)
        return
    supabase_data.delete_record("dissertacoes", record_id)


def list_articles(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_articles(ppg_id)
    return supabase_data.list_articles(ppg_id)


def upsert_article(ppg_id: str, titulo: str, autores: str, ano: int, status: str, article_id: Optional[str] = None) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.upsert_article(ppg_id, titulo, autores, ano, status, article_id)
    payload = {"ppg_id": ppg_id, "titulo": titulo, "autores": autores, "ano": ano, "status": status}
    if article_id:
        payload["id"] = article_id
    return supabase_data.upsert_record("artigos", payload)


def remove_article(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_article(record_id)
        return
    supabase_data.delete_record("artigos", record_id)


def list_ptts(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_ptts(ppg_id)
    return supabase_data.list_ptts(ppg_id)


def upsert_ptt(ppg_id: str, tema: str, responsavel: str, status: str, ptt_id: Optional[str] = None) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.upsert_ptt(ppg_id, tema, responsavel, status, ptt_id)
    payload = {"ppg_id": ppg_id, "tema": tema, "responsavel": responsavel, "status": status}
    if ptt_id:
        payload["id"] = ptt_id
    return supabase_data.upsert_record("ptts", payload)


def remove_ptt(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_ptt(record_id)
        return
    supabase_data.delete_record("ptts", record_id)


# -- Forms and evaluations -----------------------------------------------

def list_forms(ppg_id: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_forms(ppg_id, kind)
    return supabase_data.list_fichas(ppg_id)


def upsert_form(ppg_id: str, nome: str, kind: Optional[str] = None, form_id: Optional[str] = None) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.upsert_form(ppg_id, nome, kind, form_id)
    payload = {"ppg_id": ppg_id, "nome": nome}
    if form_id:
        payload["id"] = form_id
    return supabase_data.upsert_record("fichas", payload)


def remove_form(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_form(record_id)
        return
    supabase_data.delete_record("fichas", record_id)


def list_criteria(form_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_criteria(form_id)
    return supabase_data.list_criterios(form_id)


def upsert_criterion(form_id: str, descricao: str, peso: float, ordem: int, criterion_id: Optional[str] = None) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.upsert_criterion(form_id, descricao, peso, ordem, criterion_id)
    payload = {"ficha_id": form_id, "descricao": descricao, "peso": peso, "ordem": ordem}
    if criterion_id:
        payload["id"] = criterion_id
    return supabase_data.upsert_record("ficha_criterios", payload)


def remove_criterion(record_id: Any) -> None:
    if is_demo_mode():
        demo_data.remove_criterion(record_id)
        return
    supabase_data.delete_record("ficha_criterios", record_id)


def list_evaluations(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_evaluations(ppg_id)
    return supabase_data.list_avaliacoes(ppg_id)


def create_evaluation(
    target_type: str,
    target_id: str,
    form_id: str,
    scores: Dict[str, float],
    *,
    ppg_id: Optional[str] = None,
    evaluator_id: Optional[str] = None,
) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.create_evaluation(target_type, target_id, form_id, scores, ppg_id=ppg_id, evaluator_id=evaluator_id)
    if not ppg_id:
        ppg_id = st.session_state.get("ppg_id")
    return supabase_data.create_avaliacao(ppg_id, form_id, evaluator_id or "", target_id, scores)


# -- Reports --------------------------------------------------------------

def list_reports(ppg_id: str) -> List[Dict[str, Any]]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.list_reports(ppg_id)
    return supabase_data.list_relatorios(ppg_id)


def save_report(ppg_id: str, periodo: str, resumo: str) -> Dict[str, Any]:
    if is_demo_mode():
        _ensure_demo_seeded()
        return demo_data.save_report(ppg_id, periodo, resumo)
    return supabase_data.save_relatorio(ppg_id, periodo, resumo)


# -- Generic --------------------------------------------------------------

def delete_generic(table: str, record_id: Any) -> None:
    if is_demo_mode():
        demo_data.delete_generic(table, record_id)
        return
    supabase_data.delete_record(table, record_id)


__all__ = [name for name in globals() if not name.startswith("_")]
