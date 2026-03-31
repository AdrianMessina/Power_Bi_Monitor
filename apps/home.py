"""
Home - Dashboard Principal de YPF BI Monitor
"""

import streamlit as st
from pathlib import Path
from apps_core.layout_core.shared_styles import render_app_header, render_footer


def render_app(logger):
    """
    Render home dashboard

    Args:
        logger: Logger de la suite para tracking de uso
    """

    # Header con diseño corporativo YPF
    render_app_header(
        "YPF BI Monitor Suite",
        "Suite Integrada de Herramientas para Power BI",
        "1.0"
    )

    # Descripción
    st.markdown("""
    ## Bienvenido a YPF BI Monitor

    Esta suite integra **5 herramientas especializadas** para análisis, documentación y optimización
    de reportes Power BI:
    """)

    # Crear tarjetas para cada app
    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        border-left: 5px solid #0451E4; margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #000; margin-top: 0;">📊 Power BI Analyzer</h3>
                <p style="color: #666;">
                    Análisis completo de archivos PBIX y PBIP con métricas detalladas,
                    visualizaciones interactivas y exportación a PowerPoint.
                </p>
                <ul style="color: #666;">
                    <li>Análisis de tablas, relaciones y medidas</li>
                    <li>Evaluación de páginas y visuales</li>
                    <li>Recomendaciones de optimización</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        border-left: 5px solid #0451E4; margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #000; margin-top: 0;">📄 Documentation Generator</h3>
                <p style="color: #666;">
                    Generación automática de documentación técnica-funcional en Word
                    usando template corporativo.
                </p>
                <ul style="color: #666;">
                    <li>Lectura de archivos PBIP</li>
                    <li>Formularios con campos autocompletables</li>
                    <li>Soporte para imágenes y diagramas ER</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        border-left: 5px solid #0451E4; margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #000; margin-top: 0;">🎨 Layout Organizer</h3>
                <p style="color: #666;">
                    Organización automática de diagramas de modelo Power BI
                    en layouts limpios y optimizados.
                </p>
                <ul style="color: #666;">
                    <li>Star y Grid layouts</li>
                    <li>Detección de snowflake dimensions</li>
                    <li>Creación de tabs focalizados</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        border-left: 5px solid #0451E4; margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #000; margin-top: 0;">⚡ DAX Optimizer</h3>
                <p style="color: #666;">
                    Análisis y optimización de medidas DAX con recomendaciones
                    de rendimiento y mejores prácticas.
                </p>
                <ul style="color: #666;">
                    <li>Detección de medidas complejas</li>
                    <li>Ranking de optimización</li>
                    <li>Visualizaciones de análisis</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        border-left: 5px solid #0451E4; margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #000; margin-top: 0;">🤖 BI Bot</h3>
                <p style="color: #666;">
                    Asistente conversacional para análisis de reportes Power BI
                    mediante consultas en lenguaje natural.
                </p>
                <ul style="color: #666;">
                    <li>Lectura de archivos PBIX/PBIP</li>
                    <li>Respuestas contextuales</li>
                    <li>Análisis de estructura de datos</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        border-left: 5px solid #0451E4; margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #000; margin-top: 0;">📈 Usage Dashboard</h3>
                <p style="color: #666;">
                    Dashboard de métricas y estadísticas de uso de todas las
                    herramientas de la suite.
                </p>
                <ul style="color: #666;">
                    <li>Tracking de eventos</li>
                    <li>Métricas de uso por app</li>
                    <li>Análisis temporal</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Instrucciones
    st.markdown("---")
    st.markdown("""
    ## 🚀 Cómo Usar

    1. **Selecciona una herramienta** en el menú lateral izquierdo
    2. **Sigue las instrucciones** específicas de cada aplicación
    3. **Todas las acciones quedan registradas** para análisis de uso

    ## 📊 Características Comunes

    - **Interfaz Unificada**: Navegación consistente entre todas las apps
    - **Logging Centralizado**: Tracking automático de todas las operaciones
    - **Diseño Corporativo**: Colores y estilos YPF
    - **100% Funcionalidad Preservada**: Todas las features de las apps standalone

    ## 📞 Soporte

    Para reportar problemas o sugerir mejoras, contacta al equipo de IT Analytics.
    """)

    # Footer
    st.markdown("---")
    render_footer()
