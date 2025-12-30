"""Demo seed data for the in-memory PPG manager."""
from __future__ import annotations

from typing import Dict, List

import streamlit as st


def init_demo_db() -> Dict[str, List[dict]]:
    """Return deterministic demo data representing a full PPG."""
    ppg_id = "ppg-1"

    research_lines = [
        {"id": "line-a", "ppg_id": ppg_id, "name": "Linha A", "description": "Pesquisa aplicada A"},
        {"id": "line-b", "ppg_id": ppg_id, "name": "Linha B", "description": "Pesquisa aplicada B"},
        {"id": "line-c", "ppg_id": ppg_id, "name": "Linha C", "description": "Pesquisa aplicada C"},
    ]

    people = [
        {
            "id": "person-coord",
            "ppg_id": ppg_id,
            "name": "Coordenação PPG",
            "role": "coordenador",
            "email": "coordenacao@ppg.demo",
            "linhas_de_pesquisa_ids": [],
            "status": "ativo",
        },
        {
            "id": "prof-a",
            "ppg_id": ppg_id,
            "name": "Prof. A",
            "role": "orientador",
            "email": "prof.a@ppg.demo",
            "linhas_de_pesquisa_ids": ["line-a", "line-c"],
            "status": "ativo",
        },
        {
            "id": "prof-b",
            "ppg_id": ppg_id,
            "name": "Prof. B",
            "role": "orientador",
            "email": "prof.b@ppg.demo",
            "linhas_de_pesquisa_ids": ["line-b", "line-c"],
            "status": "ativo",
        },
        {
            "id": "m1",
            "ppg_id": ppg_id,
            "name": "Mestrando 1",
            "role": "mestrando",
            "email": "m1@ppg.demo",
            "orientador_id": "prof-a",
            "linha_id": "line-a",
            "status": "em andamento",
        },
        {
            "id": "m2",
            "ppg_id": ppg_id,
            "name": "Mestrando 2",
            "role": "mestrando",
            "email": "m2@ppg.demo",
            "orientador_id": "prof-a",
            "linha_id": "line-a",
            "status": "em andamento",
        },
        {
            "id": "m3",
            "ppg_id": ppg_id,
            "name": "Mestrando 3",
            "role": "mestrando",
            "email": "m3@ppg.demo",
            "orientador_id": "prof-b",
            "linha_id": "line-b",
            "status": "em andamento",
        },
        {
            "id": "m4",
            "ppg_id": ppg_id,
            "name": "Mestrando 4",
            "role": "mestrando",
            "email": "m4@ppg.demo",
            "orientador_id": "prof-a",
            "linha_id": "line-c",
            "status": "em andamento",
        },
    ]

    projects = [
        {
            "id": "proj-1",
            "ppg_id": ppg_id,
            "name": "Projeto P1",
            "description": "Projeto na Linha A",
            "line_id": "line-a",
            "status": "em_andamento",
            "orientadores_ids": ["prof-a"],
            "mestrandos_ids": ["m1", "m2"],
        },
        {
            "id": "proj-2",
            "ppg_id": ppg_id,
            "name": "Projeto P2",
            "description": "Projeto na Linha B",
            "line_id": "line-b",
            "status": "em_andamento",
            "orientadores_ids": ["prof-b"],
            "mestrandos_ids": ["m3"],
        },
        {
            "id": "proj-3",
            "ppg_id": ppg_id,
            "name": "Projeto P3",
            "description": "Projeto interdisciplinar na Linha C",
            "line_id": "line-c",
            "status": "planejamento",
            "orientadores_ids": ["prof-a", "prof-b"],
            "mestrandos_ids": ["m4"],
        },
    ]

    dissertations = [
        {
            "id": "diss-1",
            "ppg_id": ppg_id,
            "title": "D1: Sistema na Linha A",
            "summary": "Dissertação do Mestrando 1",
            "status": "em_andamento",
            "year": 2024,
            "line_id": "line-a",
            "project_id": "proj-1",
            "orientador_id": "prof-a",
            "mestrando_id": "m1",
            "artigos_ids": ["art-1"],
            "ptts_ids": ["ptt-1"],
        },
        {
            "id": "diss-2",
            "ppg_id": ppg_id,
            "title": "D2: Pesquisa aplicada B",
            "summary": "Dissertação do Mestrando 3",
            "status": "em_andamento",
            "year": 2024,
            "line_id": "line-b",
            "project_id": "proj-2",
            "orientador_id": "prof-b",
            "mestrando_id": "m3",
            "artigos_ids": ["art-3"],
            "ptts_ids": ["ptt-3"],
        },
        {
            "id": "diss-3",
            "ppg_id": ppg_id,
            "title": "D3: Integração linha C",
            "summary": "Dissertação do Mestrando 4",
            "status": "em_andamento",
            "year": 2025,
            "line_id": "line-c",
            "project_id": "proj-3",
            "orientador_id": "prof-a",
            "mestrando_id": "m4",
            "artigos_ids": ["art-4"],
            "ptts_ids": ["ptt-2"],
        },
    ]

    articles = [
        {
            "id": "art-1",
            "ppg_id": ppg_id,
            "title": "A1 - Artigo do Projeto P1",
            "summary": "Resultado inicial do Projeto P1",
            "status": "publicado",
            "year": 2024,
            "autores_texto": "Prof. A; Mestrando 1",
            "line_id": "line-a",
            "project_id": "proj-1",
            "orientador_id": "prof-a",
            "mestrando_id": "m1",
            "dissertation_id": "diss-1",
        },
        {
            "id": "art-2",
            "ppg_id": ppg_id,
            "title": "A2 - Extensão do P1",
            "summary": "Artigo sem dissertação vinculada",
            "status": "rascunho",
            "year": 2024,
            "autores_texto": "Prof. A; Mestrando 2",
            "line_id": "line-a",
            "project_id": "proj-1",
            "orientador_id": "prof-a",
            "mestrando_id": "m2",
            "dissertation_id": None,
        },
        {
            "id": "art-3",
            "ppg_id": ppg_id,
            "title": "A3 - Resultados do P2",
            "summary": "Artigo associado à dissertação D2",
            "status": "submetido",
            "year": 2024,
            "autores_texto": "Prof. B; Mestrando 3",
            "line_id": "line-b",
            "project_id": "proj-2",
            "orientador_id": "prof-b",
            "mestrando_id": "m3",
            "dissertation_id": "diss-2",
        },
        {
            "id": "art-4",
            "ppg_id": ppg_id,
            "title": "A4 - Integração Linha C",
            "summary": "Artigo associado à dissertação D3",
            "status": "rascunho",
            "year": 2025,
            "autores_texto": "Prof. A; Prof. B; Mestrando 4",
            "line_id": "line-c",
            "project_id": "proj-3",
            "orientador_id": "prof-a",
            "mestrando_id": "m4",
            "dissertation_id": "diss-3",
        },
    ]

    ptts = [
        {
            "id": "ptt-1",
            "ppg_id": ppg_id,
            "title": "T1 - Protótipo do P1",
            "summary": "Protótipo funcional relacionado à D1",
            "tipo_ptt": "software",
            "status": "entregue",
            "year": 2024,
            "line_id": "line-a",
            "project_id": "proj-1",
            "orientador_id": "prof-a",
            "mestrando_id": "m1",
            "dissertation_id": "diss-1",
        },
        {
            "id": "ptt-2",
            "ppg_id": ppg_id,
            "title": "T2 - Relatório de integração",
            "summary": "Resultado do P3 sem dissertação",
            "tipo_ptt": "relatorio",
            "status": "rascunho",
            "year": 2025,
            "line_id": "line-c",
            "project_id": "proj-3",
            "orientador_id": "prof-b",
            "mestrando_id": "m4",
            "dissertation_id": None,
        },
        {
            "id": "ptt-3",
            "ppg_id": ppg_id,
            "title": "T3 - Processo do P2",
            "summary": "PTT ligado à D2",
            "tipo_ptt": "processo",
            "status": "entregue",
            "year": 2024,
            "line_id": "line-b",
            "project_id": "proj-2",
            "orientador_id": "prof-b",
            "mestrando_id": "m3",
            "dissertation_id": "diss-2",
        },
    ]

    capes_forms = [
        {
            "id": "capes-artigo",
            "type": "article",
            "name": "Ficha CAPES - Artigos",
            "criteria": [
                {"id": "aderencia", "label": "Aderência", "weight": 0.3},
                {"id": "impacto", "label": "Impacto", "weight": 0.4},
                {"id": "qualidade", "label": "Qualidade", "weight": 0.3},
            ],
        },
        {
            "id": "capes-ptt",
            "type": "ptt",
            "name": "Ficha CAPES - PTT",
            "criteria": [
                {"id": "novidade", "label": "Novidade", "weight": 0.34},
                {"id": "implementacao", "label": "Implementação", "weight": 0.33},
                {"id": "documentacao", "label": "Documentação", "weight": 0.33},
            ],
            "tipos_ptt": ["software", "processo", "relatorio"],
        },
    ]

    evaluations = [
        {
            "id": "eval-art-1",
            "ppg_id": ppg_id,
            "target_type": "article",
            "target_id": "art-1",
            "form_id": "capes-artigo",
            "scores": {"aderencia": 4, "impacto": 5, "qualidade": 4},
            "comments": "Boa aderência e impacto inicial.",
        },
        {
            "id": "eval-ptt-1",
            "ppg_id": ppg_id,
            "target_type": "ptt",
            "target_id": "ptt-3",
            "form_id": "capes-ptt",
            "scores": {"novidade": 3, "implementacao": 4, "documentacao": 4},
            "comments": "Implementação consistente.",
        },
    ]

    ppgs = [
        {"id": ppg_id, "name": "PPG Piloto", "description": "Programa de pós-graduação demonstrativo."}
    ]

    return {
        "ppgs": ppgs,
        "research_lines": research_lines,
        "people": people,
        "projects": projects,
        "dissertations": dissertations,
        "articles": articles,
        "ptts": ptts,
        "capes_forms": capes_forms,
        "evaluations": evaluations,
    }


def ensure_demo_db() -> None:
    """Ensure demo database and context exist in session state."""
    if "db" not in st.session_state:
        st.session_state["db"] = init_demo_db()
    if "ctx" not in st.session_state:
        st.session_state["ctx"] = {
            "profile": "coordenador",
            "person_id": None,
            "ppg_id": st.session_state["db"]["ppgs"][0]["id"],
        }
    # Legacy keys used by páginas existentes
    st.session_state["ppg_id"] = st.session_state["ctx"]["ppg_id"]
    st.session_state["role"] = st.session_state["ctx"]["profile"]


__all__ = ["init_demo_db", "ensure_demo_db"]
