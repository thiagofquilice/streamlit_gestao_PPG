from __future__ import annotations

import streamlit as st

from demo_context import get_ctx, set_person, set_profile
from demo_seed import ensure_demo_db
from demo_store import export_db_json, import_db_json, list_people, reset_db


PAGE_LINKS = [
    ("pages/02_PPG_Admin.py", "PPG Admin"),
    ("pages/01_Visão_Geral.py", "Visão Geral"),
    ("pages/03_Linhas_de_Pesquisa.py", "Linhas de Pesquisa"),
    ("pages/03_Projetos.py", "Projetos"),
    ("pages/04_Dissertações.py", "Dissertações"),
    ("pages/05_Artigos.py", "Artigos"),
    ("pages/06_PTTs.py", "PTTs"),
    ("pages/07_Avaliações.py", "Cadastro de Classificações"),
]


def configure_page(title: str = "PPG Manager (Demo)") -> None:
    st.set_page_config(page_title=title, layout="wide", initial_sidebar_state="expanded")


def render_sidebar() -> None:
    ensure_demo_db()
    ctx = get_ctx()
    st.sidebar.title("PPG Demo")

    profiles = ["coordenador", "orientador", "mestrando"]
    profile = st.sidebar.selectbox("Perfil atual", profiles, index=profiles.index(ctx.get("profile", "coordenador")))
    set_profile(profile)

    people = list_people(ctx.get("ppg_id"))
    person_options = [p for p in people if p.get("role") == profile]
    if profile != "coordenador":
        options = [None] + [p.get("id") for p in person_options]
        current_person_id = ctx.get("person_id")
        selected_index = options.index(current_person_id) if current_person_id in options else 0
        selected = st.sidebar.selectbox(
            "Pessoa atual",
            options,
            format_func=lambda pid: next((p.get("name") for p in people if p.get("id") == pid), "Não definido")
            if pid
            else "Selecione",
            index=selected_index,
        )
        set_person(selected)
    else:
        set_person(None)

    ppg_id = ctx.get("ppg_id")
    st.sidebar.write(f"PPG atual: {ppg_id}")

    st.sidebar.divider()
    st.sidebar.header("Navegação")
    for page_path, label in PAGE_LINKS:
        st.sidebar.page_link(page_path, label=label)

    st.sidebar.divider()
    if st.sidebar.button("Resetar demo", use_container_width=True):
        reset_db()
        st.rerun()

    st.sidebar.download_button("Exportar JSON", export_db_json(), file_name="demo_db.json", use_container_width=True)
    uploaded = st.sidebar.file_uploader("Importar JSON", type="json")
    if uploaded:
        import_db_json(uploaded)
        st.success("Banco demo importado.")
        st.rerun()
