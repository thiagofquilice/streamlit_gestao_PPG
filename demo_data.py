"""Demo mode data seeding and in-memory CRUD helpers."""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import streamlit as st


DemoRecord = Dict[str, Any]


def _db() -> Dict[str, Any]:
    if "demo_db" not in st.session_state:
        seed_demo_data()
    return st.session_state["demo_db"]


def reset_demo_data() -> None:
    st.session_state.pop("demo_db", None)
    seed_demo_data()


def seed_demo_data() -> None:
    """Populate the session_state with a realistic demo dataset."""

    ppgs = [
        {"id": "ppg-piloto", "nome": "PPG Piloto", "descricao": "Programa focado em inovação aplicada."},
        {"id": "ppg-formiga", "nome": "PPG Formiga", "descricao": "Pesquisa em sustentabilidade e energia."},
        {"id": "ppg-ouro", "nome": "PPG Ouro Branco", "descricao": "Excelência em materiais avançados."},
    ]

    usuarios = [
        {"id": "u-coord", "nome": "Dra. Clara Coordenadora", "email": "clara.coord@demo.br"},
        {"id": "u-prof1", "nome": "Prof. Paulo Pesquisa", "email": "paulo.prof@demo.br"},
        {"id": "u-prof2", "nome": "Profa. Bianca Ensino", "email": "bianca.prof@demo.br"},
        {"id": "u-mest1", "nome": "Ana Dissertação", "email": "ana.mestranda@demo.br"},
        {"id": "u-mest2", "nome": "João Projeto", "email": "joao.mestrando@demo.br"},
    ]

    memberships = [
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "user_id": "u-coord", "role": "coordenador"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "user_id": "u-prof1", "role": "professor"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "user_id": "u-mest1", "role": "mestrando"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-formiga", "user_id": "u-coord", "role": "coordenador"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-formiga", "user_id": "u-prof2", "role": "professor"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-formiga", "user_id": "u-mest2", "role": "mestrando"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-ouro", "user_id": "u-prof1", "role": "professor"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-ouro", "user_id": "u-mest1", "role": "mestrando"},
    ]

    linhas = [
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-piloto",
            "nome": "Inteligência Artificial Aplicada",
            "descricao": "Modelagem de soluções para indústria 4.0",
        },
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-formiga",
            "nome": "Energias Renováveis",
            "descricao": "Armazenamento de energia e redes inteligentes",
        },
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-ouro",
            "nome": "Materiais Avançados",
            "descricao": "Cerâmicas técnicas e compósitos leves",
        },
    ]

    swot = [
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "categoria": "forcas", "descricao": "Laboratórios equipados"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "categoria": "fraquezas", "descricao": "Equipe administrativa enxuta"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "categoria": "oportunidades", "descricao": "Parcerias com startups"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "categoria": "ameacas", "descricao": "Cortes de orçamento"},
    ]

    objetivos = [
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "ordem": 1, "descricao": "Aumentar publicações em periódicos A2"},
        {"id": str(uuid.uuid4()), "ppg_id": "ppg-piloto", "ordem": 2, "descricao": "Dobrar convênios com empresas"},
    ]

    projetos = [
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-piloto",
            "titulo": "Plataforma de monitoramento industrial",
            "lider": "Prof. Paulo Pesquisa",
            "status": "Em andamento",
        },
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-formiga",
            "titulo": "Micro-redes para comunidades isoladas",
            "lider": "Profa. Bianca Ensino",
            "status": "Planejado",
        },
    ]

    dissertacoes = [
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-piloto",
            "titulo": "Aplicação de visão computacional em inspeção",
            "autor": "Ana Dissertação",
            "orientador": "Prof. Paulo Pesquisa",
            "defesa_prevista": "2025-03-30",
        },
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-ouro",
            "titulo": "Compósitos leves para veículos elétricos",
            "autor": "João Projeto",
            "orientador": "Profa. Bianca Ensino",
            "defesa_prevista": "2024-11-15",
        },
    ]

    artigos = [
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-piloto",
            "titulo": "Edge AI para detecção de falhas",
            "autores": "Ana Dissertação; Paulo Pesquisa",
            "ano": 2024,
            "status": "Submetido",
        },
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-formiga",
            "titulo": "Modelagem de baterias de fluxo",
            "autores": "Bianca Ensino",
            "ano": 2023,
            "status": "Publicado",
        },
    ]

    ptts = [
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-piloto",
            "tema": "Revisão bibliográfica em IA generativa",
            "responsavel": "Ana Dissertação",
            "status": "Em revisão",
        },
        {
            "id": str(uuid.uuid4()),
            "ppg_id": "ppg-formiga",
            "tema": "Estudo de viabilidade de micro-redes",
            "responsavel": "João Projeto",
            "status": "Rascunho",
        },
    ]

    fichas = [
        {"id": "ficha-artigos", "ppg_id": "ppg-piloto", "nome": "Avaliação de Artigos", "kind": "artigo"},
        {"id": "ficha-ptt", "ppg_id": "ppg-piloto", "nome": "Avaliação de PTT", "kind": "ptt"},
    ]

    ficha_criterios = [
        {"id": str(uuid.uuid4()), "ficha_id": "ficha-artigos", "descricao": "Originalidade", "peso": 2, "ordem": 1},
        {"id": str(uuid.uuid4()), "ficha_id": "ficha-artigos", "descricao": "Metodologia", "peso": 1.5, "ordem": 2},
        {"id": str(uuid.uuid4()), "ficha_id": "ficha-ptt", "descricao": "Alinhamento ao PPG", "peso": 1, "ordem": 1},
        {"id": str(uuid.uuid4()), "ficha_id": "ficha-ptt", "descricao": "Viabilidade", "peso": 1.2, "ordem": 2},
    ]

    avaliacoes: List[DemoRecord] = []
    avaliacao_notas: List[DemoRecord] = []

    st.session_state["demo_db"] = {
        "ppgs": ppgs,
        "usuarios": usuarios,
        "memberships": memberships,
        "linhas_pesquisa": linhas,
        "swot": swot,
        "objetivos": objetivos,
        "projetos": projetos,
        "dissertacoes": dissertacoes,
        "artigos": artigos,
        "ptts": ptts,
        "fichas": fichas,
        "ficha_criterios": ficha_criterios,
        "avaliacoes": avaliacoes,
        "avaliacao_notas": avaliacao_notas,
    }


def demo_users_by_ppg_and_role(ppg_id: str, role: str) -> List[DemoRecord]:
    db = _db()
    users_index = {u["id"]: u for u in db["usuarios"]}
    return [
        {**users_index.get(m["user_id"], {}), **m}
        for m in db["memberships"]
        if m["ppg_id"] == ppg_id and m["role"] == role
    ]


def list_ppgs() -> List[DemoRecord]:
    return _db()["ppgs"]


def list_memberships(user_id: str) -> List[DemoRecord]:
    return [m for m in _db()["memberships"] if m.get("user_id") == user_id]


def list_ppg_memberships(ppg_id: str) -> List[DemoRecord]:
    db = _db()
    users_index = {u["id"]: u for u in db["usuarios"]}
    registros: List[DemoRecord] = []
    for m in db["memberships"]:
        if m.get("ppg_id") != ppg_id:
            continue
        usuario = users_index.get(m.get("user_id"), {})
        registros.append({**m, "email": usuario.get("email")})
    return registros


def _upsert(table: str, payload: DemoRecord) -> DemoRecord:
    db = _db()
    registros = db.setdefault(table, [])
    record_id = payload.get("id") or str(uuid.uuid4())
    payload["id"] = record_id
    for idx, registro in enumerate(registros):
        if registro.get("id") == record_id:
            registros[idx] = {**registro, **payload}
            break
    else:
        registros.append(payload)
    return payload


def _delete(table: str, record_id: Any) -> None:
    db = _db()
    db[table] = [r for r in db.get(table, []) if r.get("id") != record_id]


def list_research_lines(ppg_id: str) -> List[DemoRecord]:
    return [l for l in _db()["linhas_pesquisa"] if l.get("ppg_id") == ppg_id]


def add_research_line(ppg_id: str, nome: str, descricao: str) -> DemoRecord:
    return _upsert("linhas_pesquisa", {"ppg_id": ppg_id, "nome": nome, "descricao": descricao})


def remove_research_line(record_id: Any) -> None:
    _delete("linhas_pesquisa", record_id)


def list_swot(ppg_id: str) -> Dict[str, List[DemoRecord]]:
    agrupado: Dict[str, List[DemoRecord]] = {"forcas": [], "fraquezas": [], "oportunidades": [], "ameacas": []}
    for item in _db()["swot"]:
        if item.get("ppg_id") != ppg_id:
            continue
        agrupado.setdefault(item.get("categoria", ""), []).append(item)
    return agrupado


def add_swot_item(ppg_id: str, categoria: str, descricao: str) -> DemoRecord:
    return _upsert("swot", {"ppg_id": ppg_id, "categoria": categoria, "descricao": descricao})


def remove_swot_item(record_id: Any) -> None:
    _delete("swot", record_id)


def list_objectives(ppg_id: str) -> List[DemoRecord]:
    return [o for o in _db()["objetivos"] if o.get("ppg_id") == ppg_id]


def add_objective(ppg_id: str, ordem: int, descricao: str) -> DemoRecord:
    return _upsert("objetivos", {"ppg_id": ppg_id, "ordem": ordem, "descricao": descricao})


def remove_objective(record_id: Any) -> None:
    _delete("objetivos", record_id)


def list_projects(ppg_id: str) -> List[DemoRecord]:
    return [p for p in _db()["projetos"] if p.get("ppg_id") == ppg_id]


def upsert_project(ppg_id: str, titulo: str, lider: str, status: str, project_id: Optional[str] = None) -> DemoRecord:
    return _upsert("projetos", {"id": project_id, "ppg_id": ppg_id, "titulo": titulo, "lider": lider, "status": status})


def remove_project(record_id: Any) -> None:
    _delete("projetos", record_id)


def list_dissertations(ppg_id: str) -> List[DemoRecord]:
    return [d for d in _db()["dissertacoes"] if d.get("ppg_id") == ppg_id]


def upsert_dissertation(
    ppg_id: str,
    titulo: str,
    autor: str,
    orientador: str,
    defesa_prevista: str,
    dissertation_id: Optional[str] = None,
) -> DemoRecord:
    return _upsert(
        "dissertacoes",
        {
            "id": dissertation_id,
            "ppg_id": ppg_id,
            "titulo": titulo,
            "autor": autor,
            "orientador": orientador,
            "defesa_prevista": defesa_prevista,
        },
    )


def remove_dissertation(record_id: Any) -> None:
    _delete("dissertacoes", record_id)


def list_articles(ppg_id: str) -> List[DemoRecord]:
    return [a for a in _db()["artigos"] if a.get("ppg_id") == ppg_id]


def upsert_article(ppg_id: str, titulo: str, autores: str, ano: int, status: str, article_id: Optional[str] = None) -> DemoRecord:
    return _upsert(
        "artigos",
        {"id": article_id, "ppg_id": ppg_id, "titulo": titulo, "autores": autores, "ano": ano, "status": status},
    )


def remove_article(record_id: Any) -> None:
    _delete("artigos", record_id)


def list_ptts(ppg_id: str) -> List[DemoRecord]:
    return [p for p in _db()["ptts"] if p.get("ppg_id") == ppg_id]


def upsert_ptt(ppg_id: str, tema: str, responsavel: str, status: str, ptt_id: Optional[str] = None) -> DemoRecord:
    return _upsert(
        "ptts",
        {"id": ptt_id, "ppg_id": ppg_id, "tema": tema, "responsavel": responsavel, "status": status},
    )


def remove_ptt(record_id: Any) -> None:
    _delete("ptts", record_id)


def list_forms(ppg_id: str, kind: Optional[str] = None) -> List[DemoRecord]:
    forms = [f for f in _db()["fichas"] if f.get("ppg_id") == ppg_id]
    if kind:
        forms = [f for f in forms if f.get("kind") == kind]
    return forms


def upsert_form(ppg_id: str, nome: str, kind: Optional[str] = None, form_id: Optional[str] = None) -> DemoRecord:
    return _upsert("fichas", {"id": form_id, "ppg_id": ppg_id, "nome": nome, "kind": kind})


def remove_form(record_id: Any) -> None:
    _delete("fichas", record_id)


def list_criteria(form_id: str) -> List[DemoRecord]:
    criterios = [c for c in _db()["ficha_criterios"] if c.get("ficha_id") == form_id]
    return sorted(criterios, key=lambda c: c.get("ordem", 0))


def upsert_criterion(form_id: str, descricao: str, peso: float, ordem: int, criterion_id: Optional[str] = None) -> DemoRecord:
    return _upsert(
        "ficha_criterios",
        {"id": criterion_id, "ficha_id": form_id, "descricao": descricao, "peso": peso, "ordem": ordem},
    )


def remove_criterion(record_id: Any) -> None:
    _delete("ficha_criterios", record_id)


def list_evaluations(ppg_id: str) -> List[DemoRecord]:
    return [a for a in _db()["avaliacoes"] if a.get("ppg_id") == ppg_id]


def create_evaluation(
    target_type: str,
    target_id: str,
    form_id: str,
    scores: Dict[str, float],
    *,
    ppg_id: Optional[str] = None,
    evaluator_id: Optional[str] = None,
) -> DemoRecord:
    criterios = {c["id"]: c for c in list_criteria(form_id)}
    total = 0.0
    for criterio_id, nota in scores.items():
        peso = criterios.get(criterio_id, {}).get("peso", 1)
        try:
            peso_num = float(peso)
        except (TypeError, ValueError):
            peso_num = 1.0
        total += float(nota) * peso_num

    avaliacao = _upsert(
        "avaliacoes",
        {
            "ppg_id": ppg_id,
            "ficha_id": form_id,
            "evaluator_id": evaluator_id,
            "target_type": target_type,
            "target_id": target_id,
            "total": total,
        },
    )

    notas_registros = [
        {
            "id": str(uuid.uuid4()),
            "avaliacao_id": avaliacao["id"],
            "criterio_id": criterio_id,
            "nota": nota,
        }
        for criterio_id, nota in scores.items()
    ]
    _db().setdefault("avaliacao_notas", []).extend(notas_registros)
    return {**avaliacao, "total": total}


def list_reports(ppg_id: str) -> List[DemoRecord]:
    return [r for r in _db().get("relatorios", []) if r.get("ppg_id") == ppg_id]


def save_report(ppg_id: str, periodo: str, resumo: str) -> DemoRecord:
    return _upsert("relatorios", {"ppg_id": ppg_id, "periodo": periodo, "resumo": resumo})


def delete_generic(table: str, record_id: Any) -> None:
    _delete(table, record_id)

