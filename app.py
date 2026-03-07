from __future__ import annotations

from demo_seed import ensure_demo_db

ensure_demo_db()

import streamlit as st

from demo_context import current_person, current_ppg, current_profile, get_ctx
from layout import configure_page, render_sidebar


def main() -> None:
    configure_page()
    ensure_demo_db()
    render_sidebar()
    st.title("PPG Manager - Hub CAPES (Demo)")
    st.success("Use a barra lateral para navegar entre os módulos do hub de evidências CAPES.")
    st.info(
        "Esta versão utiliza dados em memória (st.session_state) com seed demo para validar cadastros-base e módulos CAPES 2025-2028."
    )
    ctx = get_ctx()
    st.write(f"Perfil: {current_profile()} | Pessoa: {current_person() or 'Coordenação'} | PPG: {current_ppg()}")


if __name__ == "__main__":
    main()
