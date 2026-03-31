"""
YPF BI Monitor - Main Entry Point
Suite integrada de herramientas para Power BI
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file if exists (for API keys, admin password, etc.)
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    with open(_env_path, 'r') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# Import apps
from apps import home, powerbi_analyzer, documentation_generator, layout_organizer
from apps import dax_optimizer, bi_bot, usage_dashboard

# Import shared logger
from shared.usage_logger import UsageLogger

# Page config
st.set_page_config(
    page_title="YPF BI Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger in session state
if 'logger' not in st.session_state:
    st.session_state.logger = UsageLogger(
        suite_name="YPF_BI_Monitor",
        version="1.0"
    )

logger = st.session_state.logger

# Import shared styles
from apps_core.layout_core.shared_styles import inject_shared_styles

# Inject shared CSS + global overrides
inject_shared_styles()
st.markdown("""
<style>
    /* Hide Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar styling - YPF dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #0451E4;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #cccccc !important;
        font-size: 1rem;
        padding: 0.5rem 0;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        background-color: transparent;
    }
    h1, h2, h3 {
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    # Logo YPF
    logo_path = Path(__file__).parent / "assets" / "logo_ypf.png"
    if logo_path.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(logo_path), width="stretch")
    else:
        st.markdown("### 🛠️ YPF BI Monitor")

    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
        <h2 style="color: #0451E4; font-size: 1.5rem; margin: 0; font-weight: 700;">
            BI Monitor
        </h2>
        <p style="color: #cccccc; font-size: 0.85rem; margin-top: 0.5rem;">
            Suite de Herramientas Power BI
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation menu
    nav_options = [
        "🏠 Home",
        "📊 Power BI Analyzer",
        "📄 Documentation Generator",
        "🎨 Layout Organizer",
        "⚡ DAX Optimizer",
        "🤖 BI Bot",
    ]
    # Only show Usage Dashboard if admin password is configured
    if os.environ.get('YPF_BI_ADMIN_PASSWORD'):
        nav_options.append("📈 Usage Dashboard")

    page = st.radio(
        "Navegación",
        nav_options,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Info box
    st.markdown("""
    <div style="background: rgba(4, 81, 228, 0.1);
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #0451E4;
                margin-top: 2rem;">
        <p style="color: #0451E4; margin: 0; font-size: 0.85rem; font-weight: 600;">
            ℹ️ Información
        </p>
        <p style="color: #cccccc; margin: 0.5rem 0 0 0; font-size: 0.75rem;">
            Todas las acciones quedan registradas para análisis de uso.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Version info
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #333;">
        <p style="color: #666; font-size: 0.7rem; margin: 0;">
            YPF S.A. | Equipo de desarrollo de visualización
        </p>
        <p style="color: #666; font-size: 0.7rem; margin: 0.25rem 0 0 0;">
            Versión 1.0 | 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content area - Routing
try:
    if page == "🏠 Home":
        home.render_app(logger)
    elif page == "📊 Power BI Analyzer":
        powerbi_analyzer.render_app(logger)
    elif page == "📄 Documentation Generator":
        documentation_generator.render_app(logger)
    elif page == "🎨 Layout Organizer":
        layout_organizer.render_app(logger)
    elif page == "⚡ DAX Optimizer":
        dax_optimizer.render_app(logger)
    elif page == "🤖 BI Bot":
        bi_bot.render_app(logger)
    elif page == "📈 Usage Dashboard":
        usage_dashboard.render_app(logger)
except Exception as e:
    st.error(f"Error al cargar la aplicación: {str(e)}")
    with st.expander("🔍 Ver detalles del error"):
        import traceback
        st.code(traceback.format_exc())

    st.info("""
    **Posibles soluciones:**
    - Verifica que todas las dependencias estén instaladas
    - Revisa que los archivos core de cada app estén en su lugar
    - Consulta la documentación de la app específica
    """)
