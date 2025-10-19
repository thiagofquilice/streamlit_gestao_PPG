# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.forms import article_form
from data import delete_record, list_articles
from rbac import can


st.title("Artigos")
ppg_id = st.session_state.get("ppg_id")
role = st.session_state.get("role")
if not ppg_id:
    st.warning("Selecione um PPG na página principal.")
    st.stop()

can_manage = can(role, "manage_articles")
can_submit = can(role, "submit_articles") or can_manage

if can_manage:
    artigos = list_articles(ppg_id)
    if artigos:
        df = pd.DataFrame(artigos)
        st.dataframe(df, use_container_width=True)
        for artigo in artigos:
            if st.button("Excluir", key=f"del_art_{artigo['id']}"):
                delete_record("artigos", artigo["id"])
                st.experimental_rerun()
    else:
        st.info("Nenhum artigo cadastrado.")
else:
    st.info("Somente artigos submetidos por você serão exibidos após integração com Supabase.")

if can_submit:
    article_form(ppg_id)
else:
    st.info("Seu perfil não permite cadastrar artigos.")
