"""
YPF BI Monitor - Shared Styles Module
Unified CSS and header components for corporate consistency.
"""
import streamlit as st
from pathlib import Path


# YPF Corporate Color Palette
YPF_BLUE = "#0451E4"
YPF_BLACK = "#000000"
YPF_WHITE = "#FFFFFF"
YPF_GRAY_BG = "#F8FAFC"
YPF_GRAY_TEXT = "#666666"
YPF_TEXT_DARK = "#1E293B"
YPF_BORDER = "#E2E8F0"


def get_shared_css():
    """Return the unified YPF corporate CSS to inject in all apps."""
    return """
    <style>
    /* ==========================================
       YPF BI Monitor - Corporate Design System
       ========================================== */

    /* --- App Header Banner --- */
    .ypf-header {
        background: linear-gradient(135deg, #000000 0%, #1a1a2e 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        border-bottom: 4px solid #0451E4;
        margin-bottom: 1.5rem;
    }
    .ypf-header h1 {
        color: #0451E4;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .ypf-header .subtitle {
        color: #cccccc;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
    }
    .ypf-header .version {
        color: #888888;
        font-size: 0.75rem;
        margin: 0.2rem 0 0 0;
    }

    /* --- Section Headers --- */
    .section-header {
        background: #E6E6E6;
        border-left: 4px solid #0451E4;
        padding: 0.5rem 1rem;
        font-weight: 700;
        margin: 1rem 0 0.5rem 0;
        border-radius: 0 6px 6px 0;
    }

    /* --- Info / Help Boxes --- */
    .help-box {
        background: #E6E6E6;
        border-left: 4px solid #0451E4;
        padding: 1rem;
        border-radius: 0 6px 6px 0;
        margin: 0.5rem 0;
    }

    /* --- Buttons (Streamlit) --- */
    .stButton > button {
        background: linear-gradient(135deg, #0451E4 0%, #0340B8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 200ms ease !important;
    }
    .stButton > button:hover {
        background: #000000 !important;
        color: #0451E4 !important;
    }

    /* --- Download Button --- */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0451E4 0%, #0340B8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 200ms ease !important;
    }
    .stDownloadButton > button:hover {
        background: #000000 !important;
        color: #0451E4 !important;
    }

    /* --- Expanders --- */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1E293B;
    }

    /* --- Metric Cards --- */
    [data-testid="stMetricValue"] {
        color: #1E293B !important;
        font-weight: 700 !important;
    }

    /* --- Footer --- */
    .ypf-footer {
        text-align: center;
        color: #666;
        font-size: 0.75rem;
        border-top: 1px solid #333;
        padding-top: 0.5rem;
        margin-top: 2rem;
    }

    /* --- Feature Cards (Home page) --- */
    .feature-card {
        background: white;
        border-left: 5px solid #0451E4;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        transition: transform 200ms ease, box-shadow 200ms ease;
    }
    .feature-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .feature-card h3 {
        color: #000000;
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
    }
    .feature-card p {
        color: #666;
        font-size: 0.85rem;
        margin: 0;
    }

    /* --- PBIP Input Section --- */
    .pbip-input-section {
        background: rgba(4, 81, 228, 0.05);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0451E4;
        border-radius: 0 8px 8px 0;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* --- Loader / Spinner (YPF branded) --- */
    .ypf-loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem;
    }
    .ypf-loader {
        width: 50px;
        height: 50px;
        border: 4px solid #E2E8F0;
        border-top: 4px solid #0451E4;
        border-radius: 50%;
        animation: ypf-spin 1s linear infinite;
    }
    @keyframes ypf-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .ypf-loader-text {
        color: #666;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    </style>
    """


def render_app_header(title: str, subtitle: str = "", version: str = ""):
    """Render a standardized YPF corporate app header.

    Args:
        title: App title (e.g. "Power BI Analyzer")
        subtitle: Short description
        version: Version string (e.g. "1.1")
    """
    version_html = f'<p class="version">v{version}</p>' if version else ''
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ''

    st.markdown(f"""
    <div class="ypf-header">
        <h1>{title}</h1>
        {subtitle_html}
        {version_html}
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render a standardized YPF footer."""
    st.markdown("""
    <div class="ypf-footer">
        YPF S.A. | Equipo de desarrollo de visualización | 2026
    </div>
    """, unsafe_allow_html=True)


def inject_shared_styles():
    """Inject shared CSS into the Streamlit page. Call once at the top of each app."""
    st.markdown(get_shared_css(), unsafe_allow_html=True)
