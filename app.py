
import streamlit as st
from pathlib import Path

from src.ui.theme import apply_theme, render_brand


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AquaSentinel AI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent
PAGES_DIR = PROJECT_ROOT / "pages"


# ==========================================
# 3. PAGE DEFINITIONS
# ==========================================

PAGE_CONFIG = {
    "Overview": ("1_Overview.py", "🏠"),
    "Demand Forecasting": ("Demand_Forecasting.py", "📈"),
    "Anomaly Detection": ("3_Anomaly_Detection.py", "🔍"),
    "Resource Optimization": ("4_Resource_Optimization.py", "⚖️"),
    "Crisis Simulator": ("5_Crisis_Simulator.py", "🚨"),
    "AI Agent": ("6_AI_Agent.py", "🤖")
}


# ==========================================
# 4. VALIDATE PAGE FILES
# ==========================================

missing_pages = [
    filename
    for filename, icon in PAGE_CONFIG.values()
    if not (PAGES_DIR / filename).is_file()
]

if missing_pages:
    st.error("The following page files are missing:")

    for filename in missing_pages:
        st.write(f"- {filename}")

    st.stop()


# ==========================================
# 5. APPLY GLOBAL THEME
# ==========================================

apply_theme()


# ==========================================
# 6. CREATE PAGE OBJECTS
# ==========================================

pages = []

for page_name, (filename, icon) in PAGE_CONFIG.items():

    pages.append(
        st.Page(
            str(PAGES_DIR / filename),
            title=page_name,
            icon=icon,
            default=(page_name == "Overview")
        )
    )


# ==========================================
# 7. INITIALIZE NATIVE NAVIGATION
# ==========================================

navigation = st.navigation(
    pages,
    position="sidebar"
)


# ==========================================
# 8. SIDEBAR BRANDING
# ==========================================

render_brand()


# ==========================================
# 9. APPLICATION HEADER
# ==========================================

st.markdown(
    """
    <div style="
        color: #54D6C4;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 8px;">
        URBAN WATER INTELLIGENCE PLATFORM
    </div>
    """,
    unsafe_allow_html=True
)

st.title("AquaSentinel AI")

st.markdown(
    "Predictive water intelligence, anomaly investigation "
    "and equitable resource allocation."
)

st.divider()


# ==========================================
# 10. RUN SELECTED PAGE
# ==========================================

navigation.run()
