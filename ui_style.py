"""Reusable UI helpers for the demo app."""
from __future__ import annotations

import streamlit as st


def apply_modern_white_theme() -> None:
    """Inject a lightweight modern/clean theme with white backgrounds."""
    st.markdown(
        """
        <style>
        /* General layout */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
            background-color: #FFFFFF;
        }

        section[data-testid="stSidebar"] > div {
            background-color: #FFFFFF !important;
            padding-top: 1.5rem;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 650;
        }

        .st-emotion-cache-10trblm, .st-emotion-cache-1v0mbdj {
            font-size: 1.1rem;
        }

        /* Cards / expanders */
        div[data-testid="stExpander"] > details {
            border: 1px solid #E6E6E6;
            border-radius: 12px;
            background: #FAFAFA;
            padding: 0.25rem 0.75rem;
        }

        div[data-testid="stExpander"] > details summary {
            font-weight: 600;
        }

        /* Inputs */
        textarea, input, select, button, .st-bd, .st-af, .st-al {
            border-radius: 10px !important;
        }

        /* Buttons */
        button[kind="primary"], button[kind="secondary"], button[kind="tertiary"] {
            width: 100%;
        }

        /* Dividers spacing */
        hr {
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
