from __future__ import annotations

import streamlit as st

from auth import AuthState, get_auth_state, login
import demo_data
from provider import (
    is_demo_mode,
    load_memberships,
    logout,
    set_demo_auth,
)


def _set_page_config() -> None:
    st.set_page_config(page_title="PPG Manager", layout="wide")


def _require_login() -> AuthState | None:
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
                st.experimental_rerun()
            else:
                st.error("Credenciais inválidas. Verifique seu e-mail e senha.")
        except Exception as exc:  # pragma: no cover - feedback para o usuário
            st.error(f"Erro ao autenticar: {exc}")
    st.stop()


def _render_demo_banner() -> None:
    st.info(
        "Você está no modo demonstração: os dados são simulados e ficam apenas nesta sessão.\n\n"
        "Para produção, desative DEMO_MODE e configure Supabase (SUPABASE_URL, SUPABASE_ANON_KEY)."
    )
    if st.button("Resetar dados da demo", type="secondary"):
        demo_data.reset_demo_data()
        st.success("Dados de demonstração reiniciados.")
        st.experimental_rerun()


def _demo_user_selector() -> AuthState:
    demo_data.seed_demo_data()
    ppgs = demo_data.list_ppgs()
    ppg_names = {ppg["nome"]: ppg for ppg in ppgs}
    ppg_label = st.selectbox("Selecione o PPG", list(ppg_names.keys()))
    ppg = ppg_names[ppg_label]

    roles = ["coordenador", "professor", "mestrando"]
    role = st.selectbox("Perfil", roles)
    users = demo_data.demo_users_by_ppg_and_role(ppg["id"], role)
    if not users:
        st.warning("Nenhum usuário de demonstração disponível para este perfil.")
        st.stop()

    user_options = {f"{u.get('nome')} ({u.get('email')})": u for u in users}
    user_label = st.selectbox("Usuário", list(user_options.keys()))
    user = user_options[user_label]

    st.session_state["ppg_id"] = ppg["id"]
    st.session_state["role"] = role
    st.session_state["user"] = {"id": user.get("id"), "email": user.get("email"), "name": user.get("nome")}
    return set_demo_auth(user.get("id", "demo"), user.get("email", "demo@demo"))


def _select_membership(auth_state: AuthState) -> None:
    memberships = load_memberships(auth_state.user_id)
    if not memberships:
        st.warning("Seu usuário não possui vínculo com nenhum PPG. Solicite acesso ao coordenador.")
        st.stop()

    options = {f"PPG {m['ppg_id']} ({m['role']})": m for m in memberships}
    selected_label = st.sidebar.selectbox("Selecione o PPG", list(options.keys()))
    membership = options[selected_label]
    st.session_state["ppg_id"] = membership["ppg_id"]
    st.session_state["role"] = membership["role"]


def _render_sidebar(auth_state: AuthState) -> None:
    st.sidebar.title("PPG Manager")
    st.sidebar.caption(f"Usuário: {auth_state.email}")
    if st.session_state.get("ppg_id"):
        st.sidebar.caption(f"PPG selecionado: {st.session_state['ppg_id']} | Perfil: {st.session_state.get('role')}")
    if st.sidebar.button("Sair", use_container_width=True):
        logout()
        st.experimental_rerun()

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
    demo_mode = is_demo_mode()
    if demo_mode:
        _render_demo_banner()
        auth_state = _demo_user_selector()
    else:
        auth_state = _require_login()
        _select_membership(auth_state)

    _render_sidebar(auth_state)
    st.success("Selecione uma página na barra lateral para começar.")


if __name__ == "__main__":
    main()
