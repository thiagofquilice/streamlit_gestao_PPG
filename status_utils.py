from __future__ import annotations

from typing import Iterable, List, Optional

STATUS_ORDER = ["planejado", "em_execucao", "concluido"]
STATUS_LABELS = {
    "planejado": "Planejado",
    "em_execucao": "Em execução",
    "concluido": "Concluído",
}
STATUS_FILTER_LABELS = {
    "planejado": "Planejados",
    "em_execucao": "Em execução",
    "concluido": "Concluídos",
}

_STATUS_SYNONYMS = {
    "planejado": "planejado",
    "planejados": "planejado",
    "planejamento": "planejado",
    "rascunho": "planejado",
    "em_execucao": "em_execucao",
    "em execução": "em_execucao",
    "em_execução": "em_execucao",
    "em execuçãos": "em_execucao",
    "em andamento": "em_execucao",
    "andamento": "em_execucao",
    "submetido": "em_execucao",
    "em revisão": "em_execucao",
    "concluido": "concluido",
    "concluído": "concluido",
    "concluídos": "concluido",
    "publicado": "concluido",
    "aprovado": "concluido",
}


def status_key(value: Optional[str]) -> str:
    raw = str(value or "").strip().lower()
    normalized = _STATUS_SYNONYMS.get(raw, raw)
    return normalized if normalized in STATUS_ORDER else STATUS_ORDER[0]


def status_label(value: Optional[str]) -> str:
    return STATUS_LABELS[status_key(value)]


def status_filter_label(value: Optional[str]) -> str:
    return STATUS_FILTER_LABELS[status_key(value)]


def filter_label_to_key(value: Optional[str]) -> Optional[str]:
    if value in (None, "Todos"):
        return None
    for key, label in STATUS_FILTER_LABELS.items():
        if value == label:
            return key
    return None


def available_filter_labels(status_values: Iterable[Optional[str]]) -> List[str]:
    keys_present = {status_key(v) for v in status_values if v is not None}
    return [STATUS_FILTER_LABELS[key] for key in STATUS_ORDER if key in keys_present]


def selector_labels() -> List[str]:
    return [STATUS_LABELS[key] for key in STATUS_ORDER]


def selector_default_label(value: Optional[str]) -> str:
    return STATUS_LABELS[status_key(value)]


def selector_label_to_key(value: str) -> str:
    for key, label in STATUS_LABELS.items():
        if value == label:
            return key
    return status_key(value)
