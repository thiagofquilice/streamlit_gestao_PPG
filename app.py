from __future__ import annotations

import streamlit as st

from auth import AuthState, get_auth_state, login, logout
from data import load_memberships


def _set_page_config() -> None:
    st.set_page_config(page_title="PPG Manager", layout="wide")


def _require_login() -> AuthState:
    auth_state = get_auth_state()
    if auth_state:
        return auth_state

    st.title("PPG Manager")
    st.subheader("Acesso restrito")
    with st.form("login_form"):
        email = st.text_input("E-mail institucional")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
    if submitted:
        try:
            auth_state = login(email, password)
            if auth_state:
                st.success("Autenticado com sucesso.")
                st.rerun()

            else:
                st.error("Credenciais inválidas. Verifique seu e-mail e senha.")
        except Exception as exc:  # pragma: no cover - feedback para o usuário
            st.error(f"Erro ao autenticar: {exc}")
    st.stop()


def _select_membership(auth_state: AuthState) -> None:
    memberships = load_memberships(auth_state.user_id)
    if not memberships:
        st.warning("Seu usuário não possui vínculo com nenhum PPG. Solicite acesso ao coordenador.")
        st.stop()

    if not st.session_state.get("ppg_id"):
        first = memberships[0]
        st.session_state["ppg_id"] = first.get("ppg_id")
        st.session_state["role"] = first.get("role")

    options = {f"PPG {m['ppg_id']} ({m['role']})": m for m in memberships}
    selected_label = st.sidebar.selectbox("Selecione o PPG", list(options.keys()))
    membership = options[selected_label]
    st.session_state["ppg_id"] = membership.get("ppg_id")
    st.session_state["role"] = membership.get("role")


def _render_sidebar(auth_state: AuthState) -> None:
    st.sidebar.title("PPG Manager")
    st.sidebar.caption(f"Usuário: {auth_state.email}")
    if st.session_state.get("ppg_id"):
        st.sidebar.caption(
            f"PPG selecionado: {st.session_state['ppg_id']} | Perfil: {st.session_state.get('role')}"
        )
    if st.sidebar.button("Sair", use_container_width=True):
        logout()
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
    st.sidebar.page_link("pages/08_Relatórios.py", label="Relatórios")


def main() -> None:
    _set_page_config()
    auth_state = _require_login()
    _select_membership(auth_state)
    _render_sidebar(auth_state)

    st.success("Selecione uma página na barra lateral para começar.")


if __name__ == "__main__":
    main()
