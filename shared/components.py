"""
Componentes UI compartidos para YPF BI Monitor
"""

import streamlit as st


def render_header(app_name: str):
    """
    Render header for an app

    Args:
        app_name: Name of the current app
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                border-left: 5px solid #FFD100;">
        <h1 style="color: #FFD100; margin: 0; font-size: 2.5rem;">
            {app_name}
        </h1>
        <p style="color: #cccccc; margin: 0.5rem 0 0 0;">
            YPF BI Monitor Suite
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render footer for an app"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p style="margin: 0;">YPF S.A. | IT Analytics Team | 2026</p>
    </div>
    """, unsafe_allow_html=True)
