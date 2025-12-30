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
            "linhas_ids": ["line-a", "line-c"],
            "status": "ativo",
        },
        {
            "id": "prof-b",
            "ppg_id": ppg_id,
            "name": "Prof. B",
            "role": "orientador",
            "email": "prof.b@ppg.demo",
            "linhas_de_pesquisa_ids": ["line-b", "line-c"],
            "linhas_ids": ["line-b", "line-c"],
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
            "line_id": "line-a",
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
            "line_id": "line-a",
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
            "line_id": "line-b",
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
            "line_id": "line-c",
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
        {
            "id": "proj-4",
            "ppg_id": ppg_id,
            "name": "Projeto P4",
            "description": "Projeto aplicado com foco em gestão",
            "line_id": "line-b",
            "status": "concluido",
            "orientadores_ids": ["prof-b"],
            "mestrandos_ids": ["m2"],
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

    evaluation_forms = {
        "articles": {
            "name": "Ficha Administração - Artigos",
            "criteria": [
                {
                    "id": "aderencia_linha",
                    "name": "Aderência à linha",
                    "description": "Coerência com a linha de pesquisa do PPG e agenda da área.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "contribuicao",
                    "name": "Contribuição",
                    "description": "Avanço teórico ou prático para Administração.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "rigor_metodologico",
                    "name": "Rigor metodológico",
                    "description": "Adequação e robustez da metodologia empregada.",
                    "weight": 0.14,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "clareza",
                    "name": "Clareza",
                    "description": "Redação, estrutura e transparência dos resultados.",
                    "weight": 0.1,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "impacto",
                    "name": "Impacto",
                    "description": "Potencial de impacto acadêmico ou social.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "qualificacao_veiculo",
                    "name": "Qualificação do veículo",
                    "description": "Aderência ao estrato/qualidade do periódico ou evento.",
                    "weight": 0.14,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "internacionalizacao",
                    "name": "Internacionalização",
                    "description": "Participação ou alcance internacional do trabalho.",
                    "weight": 0.14,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "etica",
                    "name": "Ética",
                    "description": "Atendimento a requisitos éticos e de integridade.",
                    "weight": 0.12,
                    "response_type": "yes_no",
                },
            ],
        },
        "ptts": {
            "name": "Ficha Administração - PTTs",
            "ptt_types": ["software", "processo", "relatorio", "produto", "servico"],
            "criteria": [
                {
                    "id": "aplicabilidade",
                    "name": "Aplicabilidade gerencial",
                    "description": "Capacidade de resolver problemas práticos de gestão.",
                    "weight": 0.14,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "inovacao",
                    "name": "Inovação",
                    "description": "Grau de novidade em relação a soluções existentes.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "maturidade",
                    "name": "Maturidade/validação",
                    "description": "Nível de validação técnica ou de negócios.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "adocao",
                    "name": "Adoção/replicabilidade",
                    "description": "Facilidade de adoção em organizações e replicação.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "impacto_mensuravel",
                    "name": "Impacto mensurável",
                    "description": "Resultados demonstráveis (financeiros, operacionais ou sociais).",
                    "weight": 0.14,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "viabilidade",
                    "name": "Viabilidade",
                    "description": "Custo, tempo e recursos necessários para implantação.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "documentacao",
                    "name": "Documentação/transferibilidade",
                    "description": "Disponibilidade de materiais que permitam transferência.",
                    "weight": 0.12,
                    "response_type": "scale_1_5",
                },
                {
                    "id": "stakeholders",
                    "name": "Alinhamento com stakeholders",
                    "description": "Envolvimento e aderência às necessidades das partes interessadas.",
                    "weight": 0.12,
                    "response_type": "yes_no",
                },
            ],
        },
    }

    def _score_value(raw_value, response_type: str) -> float:
        if response_type == "yes_no":
            return 5.0 if bool(raw_value) else 0.0
        return float(raw_value)

    def _calculate_final_score(form: dict, scores: dict) -> float:
        total = 0.0
        for criterion in form.get("criteria", []):
            weight = float(criterion.get("weight", 0))
            value = _score_value(scores.get(criterion.get("id")), criterion.get("response_type", "scale_1_5"))
            total += weight * value
        return round(total, 2)

    def _make_scores(form: dict, base_value: int) -> dict:
        scores = {}
        for criterion in form.get("criteria", []):
            if criterion.get("response_type") == "yes_no":
                scores[criterion["id"]] = base_value % 2 == 0
            else:
                scores[criterion["id"]] = min(5, max(3, 3 + (base_value % 3)))
        return scores

    evaluations = []
    for idx, article in enumerate(articles, start=1):
        scores = _make_scores(evaluation_forms["articles"], idx)
        evaluations.append(
            {
                "id": f"eval-article-{idx}",
                "ppg_id": ppg_id,
                "target_type": "article",
                "target_id": article["id"],
                "form_type": "articles",
                "scores": scores,
                "final_score": _calculate_final_score(evaluation_forms["articles"], scores),
                "notes": f"Avaliação simulada do artigo {article['title']}",
                "evaluator_id": article.get("orientador_id") or "person-coord",
                "created_at": f"2024-01-{idx:02d}T00:00:00",
            }
        )

    for idx, ptt in enumerate(ptts, start=1):
        scores = _make_scores(evaluation_forms["ptts"], idx + len(articles))
        evaluations.append(
            {
                "id": f"eval-ptt-{idx}",
                "ppg_id": ppg_id,
                "target_type": "ptt",
                "target_id": ptt["id"],
                "form_type": "ptts",
                "scores": scores,
                "final_score": _calculate_final_score(evaluation_forms["ptts"], scores),
                "notes": f"Avaliação simulada do PTT {ptt['title']}",
                "evaluator_id": ptt.get("orientador_id") or "person-coord",
                "created_at": f"2024-02-{idx:02d}T00:00:00",
            }
        )

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
        "evaluation_forms": evaluation_forms,
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
