# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.forms import ptt_form
from provider import list_ptts, remove_ptt
from rbac import can


st.title("Planos de Trabalho (PTTs)")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

can_manage = can(role, "manage_ptts")
can_submit = can(role, "submit_ptts") or can_manage

if can_manage:
    ptts = list_ptts(ppg_id)
    if ptts:
        df = pd.DataFrame(ptts)
        st.dataframe(df, use_container_width=True)
        for ptt in ptts:
            if st.button("Excluir", key=f"del_ptt_{ptt['id']}"):
                remove_ptt(ptt["id"])
                st.experimental_rerun()
    else:
        st.info("Nenhum PTT cadastrado.")
else:
    st.info("Apenas seus PTTs serão exibidos após integração com Supabase.")

if can_submit:
    ptt_form(ppg_id)
else:
    st.info("Seu perfil não permite cadastrar PTTs.")
