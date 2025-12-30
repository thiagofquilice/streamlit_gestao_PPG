from __future__ import annotations

import streamlit as st

from demo_context import current_person, current_ppg, current_profile, get_ctx, set_person, set_ppg, set_profile
from demo_seed import ensure_demo_db
from demo_store import export_db_json, import_db_json, list_people, reset_db


def _set_page_config() -> None:
    st.set_page_config(page_title="PPG Manager (Demo)", layout="wide")


def _sidebar() -> None:
    ensure_demo_db()
    ctx = get_ctx()
    st.sidebar.title("PPG Demo")

    profiles = ["coordenador", "orientador", "mestrando"]
    profile = st.sidebar.selectbox("Perfil atual", profiles, index=profiles.index(ctx.get("profile", "coordenador")))
    set_profile(profile)

    people = list_people(ctx.get("ppg_id"))
    person_options = [p for p in people if p.get("role") == profile]
    if profile != "coordenador":
        selected = st.sidebar.selectbox(
            "Pessoa atual",
            [None] + [p.get("id") for p in person_options],
            format_func=lambda pid: next((p.get("name") for p in people if p.get("id") == pid), "Não definido")
            if pid
            else "Selecione",
            index=0 if ctx.get("person_id") is None else ([None] + [p.get("id") for p in person_options]).index(ctx.get("person_id")),
        )
        set_person(selected)
    else:
        set_person(None)

    ppg_id = ctx.get("ppg_id")
    st.sidebar.write(f"PPG atual: {ppg_id}")

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

    st.sidebar.divider()
    st.sidebar.header("Navegação")
    st.sidebar.page_link("pages/01_Visão_Geral.py", label="Visão Geral")
    st.sidebar.page_link("pages/02_PPG_Admin.py", label="Administração do PPG")
    st.sidebar.page_link("pages/03_Projetos.py", label="Projetos")
    st.sidebar.page_link("pages/04_Dissertações.py", label="Dissertações")
    st.sidebar.page_link("pages/05_Artigos.py", label="Artigos")
    st.sidebar.page_link("pages/06_PTTs.py", label="PTTs")
    st.sidebar.page_link("pages/07_Avaliações.py", label="Avaliações")


def main() -> None:
    _set_page_config()
    ensure_demo_db()
    _sidebar()
    st.title("PPG Manager - Demo")
    st.success("Use a barra lateral para navegar entre as páginas.")
    st.info(
        "Esta versão utiliza apenas dados em memória (st.session_state) com seed pré-carregado para validar vínculos entre entidades."
    )
    ctx = get_ctx()
    st.write(f"Perfil: {current_profile()} | Pessoa: {current_person() or 'Coordenação'} | PPG: {current_ppg()}")


if __name__ == "__main__":
    main()
