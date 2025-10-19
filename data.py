"""Data helpers for interacting with Supabase tables."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from supabase import Client

from auth import get_supabase_admin_client, get_supabase_client


def _client() -> Client:
    return get_supabase_client()


def list_memberships(user_id: str) -> List[Dict[str, Any]]:
    """Return the PPG memberships for the given user."""

    response = (
        _client()
        .table("ppg_memberships")
        .select("id, ppg_id, role")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data or []


def list_records(table: str, ppg_id: Optional[str] = None, order_by: Optional[str] = None) -> List[Dict[str, Any]]:
    query = _client().table(table).select("*")
    if ppg_id:
        query = query.eq("ppg_id", ppg_id)
    if order_by:
        query = query.order(order_by, desc=True)
    response = query.execute()
    return response.data or []


def upsert_record(table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = (
        _client()
        .table(table)
        .upsert(payload, returning="representation")
        .execute()
    )
    if not response.data:
        return {}
    return response.data[0]


def delete_record(table: str, record_id: Any) -> None:
    _client().table(table).delete().eq("id", record_id).execute()


def user_management_available() -> bool:
    """Return True when the app can manage Supabase users with a service key."""

    return get_supabase_admin_client() is not None


def create_user_and_membership(ppg_id: str, email: str, password: str, role: str) -> Dict[str, Any]:
    """Create a Supabase Auth user and link it to the PPG membership table."""

    admin_client = get_supabase_admin_client()
    if not admin_client:
        raise RuntimeError(
            "Para cadastrar usuários configure SUPABASE_SERVICE_ROLE_KEY nas variáveis de ambiente."
        )

    user_response = admin_client.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
        }
    )
    user = getattr(user_response, "user", None)
    if not user:
        raise RuntimeError("Supabase não retornou o usuário criado.")

    membership_payload = {"ppg_id": ppg_id, "user_id": user.id, "role": role}
    membership = upsert_record("ppg_memberships", membership_payload)
    return {"user": {"id": user.id, "email": user.email}, "membership": membership}


def list_ppg_memberships(ppg_id: str) -> List[Dict[str, Any]]:
    """Return memberships for the selected PPG and enrich with user emails when possible."""

    response = (
        _client()
        .table("ppg_memberships")
        .select("id, user_id, role, created_at")
        .eq("ppg_id", ppg_id)
        .order("created_at")
        .execute()
    )
    registros = response.data or []

    admin_client = get_supabase_admin_client()
    if not admin_client:
        return registros

    enriquecidos: List[Dict[str, Any]] = []
    for registro in registros:
        try:
            detalhes = admin_client.auth.admin.get_user_by_id(registro["user_id"])  # type: ignore[index]
            usuario = getattr(detalhes, "user", None)
            email = getattr(usuario, "email", None)
        except Exception:  # pragma: no cover - fallback se a API falhar
            email = None
        enriquecidos.append({**registro, "email": email})
    return enriquecidos


# -- Specific helpers -----------------------------------------------------

def list_articles(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("artigos", ppg_id=ppg_id, order_by="created_at")


def create_article(ppg_id: str, titulo: str, autores: str, ano: int, status: str) -> Dict[str, Any]:
    payload = {
        "ppg_id": ppg_id,
        "titulo": titulo,
        "autores": autores,
        "ano": ano,
        "status": status,
    }
    return upsert_record("artigos", payload)


def list_ptts(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("ptts", ppg_id=ppg_id, order_by="created_at")


def create_ptt(ppg_id: str, tema: str, responsavel: str, status: str) -> Dict[str, Any]:
    payload = {
        "ppg_id": ppg_id,
        "tema": tema,
        "responsavel": responsavel,
        "status": status,
    }
    return upsert_record("ptts", payload)


def list_fichas(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("fichas", ppg_id=ppg_id, order_by="created_at")


def list_criterios(ficha_id: str) -> List[Dict[str, Any]]:
    response = (
        _client()
        .table("ficha_criterios")
        .select("id, descricao, peso")
        .eq("ficha_id", ficha_id)
        .order("ordem")
        .execute()
    )
    return response.data or []


def list_avaliacoes(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("avaliacoes", ppg_id=ppg_id, order_by="created_at")


def create_avaliacao(
    ppg_id: str,
    ficha_id: str,
    avaliador_id: str,
    avaliavel: str,
    notas: Dict[str, float],
) -> Dict[str, Any]:
    total = 0.0
    criterios = {c["id"]: c for c in list_criterios(ficha_id)}
    for criterio_id, nota in notas.items():
        peso_val = criterios.get(criterio_id, {}).get("peso", 1)
        try:
            peso_num = float(peso_val)
        except (TypeError, ValueError):
            peso_num = 1.0
        total += float(nota) * peso_num

    avaliacao_payload = {
        "ppg_id": ppg_id,
        "ficha_id": ficha_id,
        "avaliador_id": avaliador_id,
        "avaliavel": avaliavel,
        "total": total,
    }
    avaliacao = upsert_record("avaliacoes", avaliacao_payload)
    avaliacao_id = avaliacao.get("id")
    if avaliacao_id:
        _persist_notas(avaliacao_id, notas)
    avaliacao["total"] = total
    return avaliacao


def _persist_notas(avaliacao_id: Any, notas: Dict[str, float]) -> None:
    registros = [
        {"avaliacao_id": avaliacao_id, "criterio_id": criterio_id, "nota": valor}
        for criterio_id, valor in notas.items()
    ]
    if not registros:
        return
    _client().table("avaliacao_notas").upsert(registros).execute()


def list_swot(ppg_id: str) -> Dict[str, List[Dict[str, Any]]]:
    dados = list_records("swot", ppg_id=ppg_id, order_by="created_at")
    agrupado: Dict[str, List[Dict[str, Any]]] = {"forcas": [], "fraquezas": [], "oportunidades": [], "ameacas": []}
    for item in dados:
        categoria = item.get("categoria")
        agrupado.setdefault(categoria, []).append(item)
    return agrupado


def list_objetivos(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("objetivos", ppg_id=ppg_id, order_by="ordem")


def list_linhas(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("linhas_pesquisa", ppg_id=ppg_id, order_by="nome")


def list_projetos(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("projetos", ppg_id=ppg_id, order_by="created_at")


def upsert_projeto(ppg_id: str, titulo: str, lider: str, status: str) -> Dict[str, Any]:
    payload = {"ppg_id": ppg_id, "titulo": titulo, "lider": lider, "status": status}
    return upsert_record("projetos", payload)


def list_dissertacoes(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("dissertacoes", ppg_id=ppg_id, order_by="defesa_prevista")


def upsert_dissertacao(ppg_id: str, titulo: str, autor: str, orientador: str, defesa_prevista: str) -> Dict[str, Any]:
    payload = {
        "ppg_id": ppg_id,
        "titulo": titulo,
        "autor": autor,
        "orientador": orientador,
        "defesa_prevista": defesa_prevista,
    }
    return upsert_record("dissertacoes", payload)


def list_relatorios(ppg_id: str) -> List[Dict[str, Any]]:
    return list_records("relatorios", ppg_id=ppg_id, order_by="periodo")


def save_relatorio(ppg_id: str, periodo: str, resumo: str) -> Dict[str, Any]:
    payload = {"ppg_id": ppg_id, "periodo": periodo, "resumo": resumo}
    return upsert_record("relatorios", payload)
