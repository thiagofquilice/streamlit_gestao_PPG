"""Reusable UI helpers for the demo app."""
from __future__ import annotations

import streamlit as st


def apply_modern_white_theme() -> None:
    """Inject a clean, high-contrast white theme using only CSS."""

    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
        }

        /* General layout */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF !important;
            color: #1F2937;
            font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        section[data-testid="stSidebar"] > div {
            background-color: #F8F9FA !important;
            color: #1F2937;
            padding-top: 1.75rem;
            padding-bottom: 1.5rem;
            border-right: 1px solid #E5E7EB;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: #111827;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        p, div, span, label, li {
            color: #1F2937;
        }

        small, figcaption, .stCaption, .st-emotion-cache-1q8dd3e, .st-emotion-cache-1kyxreq {
            color: #4B5563 !important;
        }

        /* Cards / expanders */
        div[data-testid="stExpander"] > details {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FAFAFA;
            padding: 0.5rem 0.9rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }

        div[data-testid="stExpander"] > details summary {
            font-weight: 600;
            color: #111827;
        }

        /* Inputs */
        textarea, input, select, .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
            color: #111827 !important;
            background: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 10px !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        textarea:focus, input:focus, select:focus, .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
            border-color: #9CA3AF !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.08);
        }

        /* Buttons */
        button[kind="primary"], button[kind="secondary"], button[kind="tertiary"], button[kind="outline"] {
            border-radius: 10px !important;
            font-weight: 600;
        }

        /* Segmented / radio controls */
        div[role="radiogroup"] > label {
            color: #1F2937;
        }

        /* Dividers spacing */
        hr {
            border-color: #E5E7EB;
            margin-top: 1.75rem;
            margin-bottom: 1.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
