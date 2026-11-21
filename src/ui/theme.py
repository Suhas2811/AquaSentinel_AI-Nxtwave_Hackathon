
import streamlit as st
import textwrap


# ==========================================
# AQUASENTINEL AI — COLOR PALETTE
# ==========================================

COLORS = {
    "background": "#101B2A",
    "sidebar": "#142336",
    "surface": "#17283B",
    "surface_light": "#20364B",
    "primary": "#54D6C4",
    "secondary": "#39B9D3",
    "text": "#E6EDF5",
    "muted": "#A8BACB",
    "success": "#42C99A",
    "warning": "#E6A94A",
    "danger": "#F07178",
    "border": "#304459",
}


# ==========================================
# GLOBAL THEME
# ==========================================

def apply_theme():
    """Apply the AquaSentinel AI global theme."""

    st.markdown(
        """
        <style>

        /* MAIN APPLICATION */

        .stApp {
            background-color: #101B2A;
            color: #E6EDF5;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stDecoration"] {
            display: none;
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }


        /* SIDEBAR */

        [data-testid="stSidebar"] {
            background-color: #142336;
            border-right: 1px solid #304459;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: #E6EDF5;
        }


        /* NATIVE STREAMLIT NAVIGATION */

        [data-testid="stSidebarNav"] {
            background-color: #142336;
            padding-top: 8px;
        }

        [data-testid="stSidebarNav"] a {
            color: #E6EDF5 !important;
            border-radius: 8px;
            margin: 3px 8px;
            transition: background-color 0.2s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: #20364B !important;
            color: #54D6C4 !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #20364B !important;
            color: #54D6C4 !important;
            font-weight: 700;
        }


        /* TYPOGRAPHY */

        h1, h2, h3 {
            color: #E6EDF5 !important;
            font-weight: 650 !important;
        }

        p, label {
            color: #A8BACB;
        }


        /* BRANDING */

        .aqua-brand {
            color: #54D6C4;
            font-weight: 750;
            letter-spacing: 0.3px;
        }

        .aqua-muted {
            color: #A8BACB;
            font-size: 0.85rem;
        }


        /* METRIC CARDS */

        [data-testid="stMetric"] {
            background-color: #17283B;
            border: 1px solid #304459;
            border-radius: 14px;
            padding: 18px;
        }

        [data-testid="stMetricLabel"] {
            color: #A8BACB;
        }

        [data-testid="stMetricValue"] {
            color: #54D6C4;
        }


        /* ALERTS */

        [data-testid="stAlert"] {
            background-color: #17283B;
            border: 1px solid #304459;
            border-radius: 12px;
            color: #E6EDF5;
        }


        /* BUTTONS */

        .stButton > button {
            background-color: #54D6C4;
            color: #101B2A;
            border: none;
            border-radius: 9px;
            font-weight: 600;
            padding: 0.55rem 1.1rem;
        }

        .stButton > button:hover {
            background-color: #39B9D3;
            color: #101B2A;
        }


        /* INPUT FIELDS */

        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] {
            background-color: #17283B;
            color: #E6EDF5;
            border-radius: 8px;
        }


        /* DATA TABLES */

        [data-testid="stDataFrame"] {
            border: 1px solid #304459;
            border-radius: 10px;
        }


        /* DIVIDERS */

        hr {
            border-color: #304459;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# SIDEBAR BRANDING
# ==========================================

def render_brand():
    """Render AquaSentinel AI branding in the sidebar."""

    brand_html = (
        '<div style="padding:12px 4px 22px 4px;'
        'border-bottom:1px solid #304459;'
        'margin-bottom:18px;">'

        '<div style="font-size:32px;margin-bottom:10px;">'
        '💧'
        '</div>'

        '<div style="color:#54D6C4;'
        'font-size:21px;font-weight:750;'
        'letter-spacing:0.3px;">'
        'AquaSentinel AI'
        '</div>'

        '<div style="color:#A8BACB;'
        'font-size:10px;letter-spacing:1.2px;'
        'margin-top:5px;">'
        'URBAN WATER INTELLIGENCE'
        '</div>'

        '</div>'
    )

    with st.sidebar:
        st.markdown(
            brand_html,
            unsafe_allow_html=True
        )
