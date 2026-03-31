"""
BI Bot - Integrado en YPF BI Monitor
Replica funcionalidad completa de powerbi-bot
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
from loguru import logger
import tempfile


def render_app(logger_suite):
    """
    Wrapper para BI Bot integrado en YPF BI Monitor

    Args:
        logger_suite: Logger de la suite para tracking de uso
    """

    # Imports absolutos - NO requiere manipular sys.path
    from apps_core.bot_core.core.xmla_connector import XMLAConnector
    from apps_core.bot_core.core.pbix_file_reader import PBIXFileReader

    # Variable para logger
    usage_logger = logger_suite
    LOGGING_ENABLED = logger_suite is not None

    
    # Import shared styles
    from apps_core.layout_core.shared_styles import render_app_header, render_footer

    # Minimal app-specific CSS
    st.markdown("""
    <style>
        .status-connected { color: #28a745; font-weight: bold; }
        .status-disconnected { color: #dc3545; font-weight: bold; }
        .chat-message { padding: 1rem; margin: 0.5rem 0; border-radius: 0.5rem; }
        .user-message { background-color: #E6E6E6; border-left: 3px solid #0451E4; text-align: right; }
        .bot-message { background-color: #f5f5f5; border-left: 3px solid #000000; }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'connector' not in st.session_state:
        st.session_state.connector = None
    if 'is_connected' not in st.session_state:
        st.session_state.is_connected = False
    if 'file_reader' not in st.session_state:
        st.session_state.file_reader = None
    if 'model_data' not in st.session_state:
        st.session_state.model_data = None
    if 'mode' not in st.session_state:
        st.session_state.mode = None  # 'xmla' o 'file'
    
    def check_connection():
        """Verifica y establece conexión a Power BI Desktop"""
        try:
            if st.session_state.connector is None:
                st.session_state.connector = XMLAConnector()
    
            if st.session_state.connector.connect():
                st.session_state.is_connected = True
                return True
            else:
                st.session_state.is_connected = False
                return False
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            st.session_state.is_connected = False
            return False
    
    def display_model_input():
        """PBIP input and XMLA connection - in main content area"""
        # Only show if no model is loaded yet
        if st.session_state.mode is None or (st.session_state.mode == 'file' and st.session_state.file_reader is None):
            st.markdown("### 📁 Cargar Modelo PBIP")

            # PBIP text input
            pbip_path = st.text_input(
                "Ruta del archivo .pbip",
                placeholder=r"C:\ruta\a\tu\archivo.pbip",
                help="Pega la ruta completa del archivo .pbip (se detectan y eliminan comillas automáticamente)"
            )

            # Instructions
            with st.expander("💡 ¿Cómo copiar la ruta?"):
                st.markdown("""
                **Desde el Explorador de Windows:**
                1. Navega a tu archivo `.pbip`
                2. **SHIFT + Click derecho** en el archivo
                3. **Copiar como ruta de acceso**
                4. Pega arriba (comillas se eliminan automáticamente)

                **Estructura PBIP:**
                - `reporte.pbip` (archivo principal)
                - `reporte.SemanticModel/` (modelo)
                - `reporte.Report/` (visualizaciones)
                """)

            # Process PBIP path
            if pbip_path and pbip_path.strip():
                clean_path = pbip_path.strip().strip('"').strip("'")

                if os.path.exists(clean_path):
                    if clean_path.endswith('.pbip'):
                        if st.session_state.file_reader is None or st.session_state.mode != 'file':
                            with st.spinner("Extrayendo modelo PBIP..."):
                                reader = PBIXFileReader(clean_path)
                                st.session_state.model_data = reader.extract_model()
                                st.session_state.file_reader = reader
                                st.session_state.mode = 'file'

                            st.success("✓ Modelo PBIP cargado")
                            st.rerun()
                    else:
                        st.warning("⚠️ El archivo debe tener extensión .pbip")
                else:
                    st.error("❌ Archivo no encontrado. Verifica la ruta.")

            st.markdown("---")
            st.markdown("### 🔌 O Conectar a Power BI Desktop")

            if st.button("🔄 Detectar Power BI Desktop", use_container_width=True):
                with st.spinner("Detectando..."):
                    if check_connection():
                        st.session_state.mode = 'xmla'
                        st.rerun()

            st.markdown("---")

    def display_sidebar():
        """Panel lateral con model stats"""
        with st.sidebar:

            # Mostrar información según el modo
            if st.session_state.mode == 'file' and st.session_state.model_data:
                st.markdown('<p class="status-connected">✓ Modelo cargado (Archivo PBIP)</p>', unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 📊 Modelo")
                st.info(f"""
                **Modo:** Lectura desde archivo PBIP
                """)
    
                # Estadísticas del modelo desde archivo
                summary = st.session_state.file_reader.get_summary()
                st.markdown("### 📈 Estadísticas")
    
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Tablas", summary.get('tables_count', 0))
                    st.metric("Medidas", summary.get('measures_count', 0))
                with col2:
                    st.metric("Ocultas", f"{summary.get('hidden_tables_count', 0)} tablas")
                    st.metric("Relaciones", summary.get('relationships_count', 0))
    
                # Listar tablas
                if st.checkbox("Mostrar tablas"):
                    for table_name in summary.get('tables', []):
                        st.text(f"• {table_name}")
    
            elif st.session_state.is_connected and st.session_state.mode == 'xmla':
                st.markdown('<p class="status-connected">✓ Conectado (XMLA)</p>', unsafe_allow_html=True)
    
                st.markdown("---")
                st.markdown("### 📊 Modelo")
    
                # Info del modelo
                connector = st.session_state.connector
                st.info(f"""
                **Puerto:** {connector.port if connector else 'N/A'}
                **Modo:** XMLA (Tiempo Real)
                """)
    
                st.markdown("### 📈 Estadísticas")
    
                # TOM wrapper
                tom = connector.get_tom_wrapper() if connector else None
    
                if tom and tom.is_connected:
                    try:
                        summary = tom.get_model_summary()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Tablas", summary.get('tables_count', 0))
                            st.metric("Medidas", summary.get('measures_count', 0))
                        with col2:
                            st.metric("Ocultas", f"{summary.get('hidden_tables_count', 0)} tablas")
                            st.metric("Relaciones", summary.get('relationships_count', 0))
    
                        # Listar tablas
                        if st.checkbox("Mostrar tablas"):
                            for table_name in summary.get('tables', []):
                                st.text(f"• {table_name}")
                    except Exception as e:
                        st.error(f"Error obteniendo estadísticas: {e}")
                        st.caption("⏳ TOM requiere pythonnet instalado")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tablas", "⏳")
                        st.metric("Medidas", "⏳")
                    with col2:
                        st.metric("Columnas", "⏳")
                        st.metric("Relaciones", "⏳")
                    st.caption("ℹ️ Instala pythonnet para acceder al modelo")
            else:
                st.markdown('<p class="status-disconnected">✗ No conectado</p>', unsafe_allow_html=True)
                st.warning("""
                **Power BI Desktop no detectado**
    
                Para conectar:
                1. Abre un archivo .pbix en Power BI Desktop
                2. Haz clic en "Detectar Power BI Desktop"
                """)
    
            st.markdown("---")
            st.markdown("### ℹ️ Información")
            st.caption("**Versión:** 0.1.0-MVP")
            st.caption("**YPF - Equipo de desarrollo de visualización**")
            st.caption(f"**Última actualización:** {datetime.now().strftime('%H:%M:%S')}")
    
    def display_chat():
        """Área de chat principal"""
        st.markdown('<p class="main-header">🤖 Power BI Bot - Asistente BI</p>', unsafe_allow_html=True)
    
        # Verificar si hay modelo cargado
        has_model = (st.session_state.mode == 'file' and st.session_state.model_data) or \
                    (st.session_state.mode == 'xmla' and st.session_state.is_connected)
    
        if not has_model:
            # Mensaje de bienvenida
            st.markdown("""
            ### 👋 Bienvenido a Power BI Bot
    
            **Asistente conversacional para modelos de Power BI**
            """)
    
            st.info("""
            **Para comenzar:**
            1. 📁 Carga un archivo .pbix desde el panel izquierdo
            2. **O** 🔌 Conecta a Power BI Desktop (si tienes un modelo abierto)
            3. Hazme preguntas en lenguaje natural
            """)
    
            # Capacidades
            col1, col2 = st.columns(2)
    
            with col1:
                st.markdown("""
                **✅ Ya puedes:**
                - 📊 Consultar medidas DAX
                - 📋 Ver tablas y columnas
                - 🔗 Analizar relaciones
                - 📈 Obtener estadísticas
                """)
    
            with col2:
                st.markdown("""
                **⏳ Próximamente:**
                - ✨ Crear medidas DAX
                - ✏️ Modificar medidas
                - ➕ Columnas calculadas
                - 🔄 Renombrar elementos
                """)
    
            # Ejemplos
            with st.expander("💡 Ejemplos de preguntas que puedes hacer"):
                st.markdown("""
                **Consultas:**
                - "¿Qué medidas tengo?"
                - "Muéstrame las tablas del modelo"
                - "¿Cuántas relaciones hay?"
                - "Dame un resumen del modelo"
    
                **Búsquedas:**
                - "¿Qué medidas hay en la tabla Ventas?"
                - "Muéstrame las columnas de Clientes"
                - "¿Qué tablas están relacionadas con Ventas?"
    
                **Ayuda:**
                - "Ayuda"
                - "¿Qué puedo hacer?"
                - "¿Qué capacidades tienes?"
                """)
    
            return
    
        # Área de chat
        st.markdown("### 💬 Chat")
    
        # Mostrar historial
        chat_container = st.container()
        with chat_container:
            # Mensaje de bienvenida automático si no hay historial
            if len(st.session_state.chat_history) == 0:
                mode = "archivo" if st.session_state.mode == 'file' else "XMLA (tiempo real)"
                welcome_msg = f"""👋 **¡Modelo cargado!** (modo: {mode})
    
    **Puedo ayudarte con:**
    • Ver medidas, tablas y relaciones
    • Buscar elementos específicos
    • Estadísticas del modelo
    
    **Prueba preguntarme:**
    • "¿Qué medidas tengo?"
    • "Muéstrame las tablas"
    • "¿Cuántas relaciones hay?"
    
    Escribe tu pregunta abajo."""
    
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Bot:</strong> {welcome_msg}
                </div>
                """, unsafe_allow_html=True)
    
            # Mostrar historial de mensajes
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>Tú:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>Bot:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
    
        # Input de usuario
        st.markdown("---")
    
        col1, col2 = st.columns([5, 1])
    
        with col1:
            user_input = st.text_input(
                "Escribe tu mensaje:",
                key="user_input",
                placeholder="Ej: ¿Qué medidas tengo en el modelo?",
                label_visibility="collapsed"
            )
    
        with col2:
            send_button = st.button("Enviar", use_container_width=True)
    
        # Sugerencias rápidas (solo si no hay historial)
        if len(st.session_state.chat_history) == 0:
            st.caption("💡 **Prueba estas preguntas:**")
            col1, col2, col3, col4 = st.columns(4)
    
            quick_questions = [
                ("📊 Medidas", "¿Qué medidas tengo?"),
                ("📋 Tablas", "¿Qué tablas tengo?"),
                ("🔗 Relaciones", "Muéstrame las relaciones"),
                ("📈 Resumen", "Dame un resumen del modelo")
            ]
    
            for idx, (col, (label, question)) in enumerate(zip([col1, col2, col3, col4], quick_questions)):
                with col:
                    if st.button(label, key=f"quick_{idx}", use_container_width=True):
                        # Agregar pregunta al historial
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': question,
                            'timestamp': datetime.now()
                        })
                        # Generar respuesta
                        bot_response = process_message(question)
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': bot_response,
                            'timestamp': datetime.now()
                        })
                        st.rerun()
    
        # Procesar mensaje
        if send_button and user_input:
            # Agregar mensaje del usuario
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
    
            # Respuesta del bot (por ahora simulada)
            bot_response = process_message(user_input)
    
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.now()
            })
    
            # Recargar para mostrar nuevos mensajes
            st.rerun()
    
    def process_message(user_input: str) -> str:
        """
        Procesa el mensaje del usuario y genera respuesta.
        Funciona con modo archivo o XMLA
        """
        user_input_lower = user_input.lower()
    
        # Saludos
        if any(word in user_input_lower for word in ["hola", "buenos", "buenas", "hi", "hello"]):
            return """¡Hola! 👋 Soy tu asistente de Power BI.
    
    Puedo ayudarte a consultar tu modelo. Pregúntame lo que necesites."""
    
        # Ayuda
        elif any(word in user_input_lower for word in ["ayuda", "help", "qué puedo", "capacidades", "comandos"]):
            mode = "archivo" if st.session_state.mode == 'file' else "XMLA"
            return f"""🤖 **Power BI Bot - Guía de Uso**
    
    **📊 Modo actual:** {mode}
    
    ---
    
    ### ✅ **LO QUE PUEDO HACER AHORA:**
    
    **📊 Consultar Medidas:**
    - "¿Qué medidas tengo?"
    - "Muéstrame las medidas de la tabla Ventas"
    - "¿Cuántas medidas hay?"
    
    **📋 Consultar Tablas:**
    - "¿Qué tablas tengo?"
    - "Muéstrame las columnas de Clientes"
    - "¿Cuántas tablas están ocultas?"
    
    **🔗 Consultar Relaciones:**
    - "Muéstrame las relaciones"
    - "¿Qué tablas están relacionadas con Ventas?"
    - "¿Cuántas relaciones hay?"
    
    **📈 Estadísticas:**
    - "Dame un resumen del modelo"
    - "¿Cuántos elementos tiene el modelo?"
    
    ---
    
    ### ⏳ **PRÓXIMAMENTE:**
    
    **🔧 Modificar Modelos** (requiere Claude API + XMLA):
    - Crear medidas DAX automáticamente
    - Modificar medidas existentes
    - Crear columnas calculadas
    - Renombrar elementos
    - Eliminar medidas
    
    **Una vez habilitado podrás:**
    - "Crea una medida de ventas del año pasado"
    - "Modifica la medida Total Ventas para usar SUM"
    - "Agrega una columna Margen en tabla Ventas"
    
    ---
    
    💡 **Escribe tu pregunta en lenguaje natural - no necesitas sintaxis exacta!**"""
    
        # Modo archivo
        elif st.session_state.mode == 'file' and st.session_state.model_data:
            return process_file_mode(user_input_lower, user_input)
    
        # Modo XMLA
        elif st.session_state.mode == 'xmla' and st.session_state.is_connected:
            return process_xmla_mode(user_input_lower, user_input)
    
        else:
            return "👈 Carga un archivo .pbix o conecta a Power BI Desktop para comenzar."
    
    def process_file_mode(user_input_lower: str, user_input: str) -> str:
        """Procesa mensajes en modo archivo con detección inteligente"""
        model_data = st.session_state.model_data
    
        # Detectar intención: MEDIDAS
        if any(word in user_input_lower for word in ["medida", "medidas", "measure", "measures", "dax", "calculo", "formula"]):
            measures = model_data.measures
            if not measures:
                return "No se encontraron medidas en el modelo."
    
            response = f"📊 **Encontré {len(measures)} medidas en tu modelo:**\n\n"
    
            # Agrupar por tabla
            by_table = {}
            for m in measures:
                table = m['table']
                if table not in by_table:
                    by_table[table] = []
                by_table[table].append(m)
    
            for table, table_measures in by_table.items():
                response += f"\n**Tabla: {table}** ({len(table_measures)} medidas)\n"
                for m in table_measures[:5]:
                    response += f"- {m['name']}\n"
                if len(table_measures) > 5:
                    response += f"  ... y {len(table_measures) - 5} más\n"
    
            return response
    
        # Detectar intención: TABLAS
        elif any(word in user_input_lower for word in ["tabla", "tablas", "table", "tables", "entidad", "entidades"]):
            tables = model_data.tables
            if not tables:
                return "No se encontraron tablas en el modelo."
    
            response = f"📋 **Encontré {len(tables)} tablas en tu modelo:**\n\n"
    
            for t in tables:
                hidden_mark = "🔒" if t.get('is_hidden', False) else ""
                response += f"**{hidden_mark} {t['name']}**\n"
                response += f"  - Columnas: {t.get('columns_count', 0)}\n"
                response += f"  - Medidas: {t.get('measures_count', 0)}\n"
                if t.get('description'):
                    response += f"  - Descripción: {t['description'][:50]}...\n"
                response += "\n"
    
            return response
    
        # Detectar intención: RELACIONES
        elif any(word in user_input_lower for word in ["relacion", "relaciones", "relationship", "relationships", "vinculo", "vinculos", "conexion"]):
            relationships = model_data.relationships
            if not relationships:
                return "No se encontraron relaciones en el modelo."
    
            response = f"🔗 **Encontré {len(relationships)} relaciones:**\n\n"
    
            for r in relationships[:10]:
                response += f"- {r['from_table']}.{r['from_column']} → {r['to_table']}.{r['to_column']}\n"
    
            if len(relationships) > 10:
                response += f"\n... y {len(relationships) - 10} más\n"
    
            return response
    
        # Detectar intención: RESUMEN/ESTADÍSTICAS
        elif any(word in user_input_lower for word in ["resumen", "estadistica", "estadisticas", "cuantas", "cuantos", "summary", "stats"]):
            tables = model_data.tables
            measures = model_data.measures
            relationships = model_data.relationships
    
            return f"""📊 **Resumen del Modelo:**
    
    • **Tablas:** {len(tables)}
    • **Medidas:** {len(measures)}
    • **Relaciones:** {len(relationships)}
    
    ¿Quieres ver detalles de algún elemento específico?"""
    
        # No entendió la pregunta
        else:
            return f"""No estoy seguro de qué información necesitas sobre el modelo.
    
    Intenta preguntarme sobre:
    • Medidas
    • Tablas
    • Relaciones
    • Resumen del modelo
    
    O escribe "ayuda" para ver ejemplos."""
    
    def process_xmla_mode(user_input_lower: str, user_input: str) -> str:
        """Procesa mensajes en modo XMLA con detección inteligente"""
        connector = st.session_state.connector
        tom = connector.get_tom_wrapper() if connector else None
    
        # Detectar intención: MEDIDAS
        if any(word in user_input_lower for word in ["medida", "medidas", "measure", "measures", "dax", "calculo", "formula"]) and tom and tom.is_connected:
            try:
                measures = tom.get_measures()
                if not measures:
                    return "No se encontraron medidas en el modelo."
    
                response = f"📊 **Encontré {len(measures)} medidas en tu modelo:**\n\n"
    
                # Agrupar por tabla
                by_table = {}
                for m in measures:
                    table = m.table_name
                    if table not in by_table:
                        by_table[table] = []
                    by_table[table].append(m)
    
                for table, table_measures in by_table.items():
                    response += f"\n**Tabla: {table}** ({len(table_measures)} medidas)\n"
                    for m in table_measures[:5]:
                        response += f"- {m.name}\n"
                    if len(table_measures) > 5:
                        response += f"  ... y {len(table_measures) - 5} más\n"
    
                return response
            except Exception as e:
                return f"❌ Error obteniendo medidas: {e}"
    
        # Detectar intención: TABLAS
        elif any(word in user_input_lower for word in ["tabla", "tablas", "table", "tables", "entidad", "entidades"]):
            if tom and tom.is_connected:
                try:
                    tables = tom.get_tables()
                    if not tables:
                        return "No se encontraron tablas en el modelo."
    
                    response = f"📋 **Encontré {len(tables)} tablas en tu modelo:**\n\n"
    
                    for t in tables:
                        hidden_mark = "🔒" if t.is_hidden else ""
                        response += f"**{hidden_mark} {t.name}**\n"
                        response += f"  - Columnas: {t.columns_count}\n"
                        response += f"  - Medidas: {t.measures_count}\n"
                        if t.description:
                            response += f"  - Descripción: {t.description[:50]}...\n"
                        response += "\n"
    
                    return response
                except Exception as e:
                    return f"❌ Error obteniendo tablas: {e}"
            else:
                return "📋 Requiere pythonnet instalado para acceder al modelo vía XMLA."
    
        # Detectar intención: CREAR/MODIFICAR (futuro)
        elif any(word in user_input_lower for word in ["crea", "crear", "modifica", "modificar", "agrega", "agregar", "elimina", "eliminar"]):
            return """⚠️ **Modificar modelos aún no está disponible.**
    
    Para habilitar esta funcionalidad necesito:
    1. Claude API Key (generar DAX inteligente)
    2. Herramientas MCP implementadas
    3. Validador de sintaxis DAX
    
    Una vez completo podrás:
    • Crear medidas DAX automáticamente
    • Modificar medidas existentes
    • Renombrar elementos
    
    Por ahora solo puedo **consultar** el modelo."""
    
        # No entendió la pregunta
        else:
            return f"""No estoy seguro de qué información necesitas sobre el modelo.
    
    Intenta preguntarme sobre:
    • Medidas
    • Tablas
    • Relaciones
    
    O escribe "ayuda" para ver ejemplos."""
    
    def main():
        """Función principal"""

        # Header
        render_app_header(
            "BI Bot",
            "Asistente conversacional para análisis de modelos Power BI",
            "0.1.0"
        )

        # Model input (main area) - only shown if no model loaded
        display_model_input()

        # Panel lateral with model stats
        display_sidebar()

        # Área principal de chat
        display_chat()

        # Footer
        st.markdown("---")
        render_footer()

    # Ejecutar la aplicación
    main()

    if __name__ == "__main__":
        # Configurar logging
        logger.add("logs/app_{time}.log", rotation="1 day", retention="7 days", level="INFO")
        logger.info("Iniciando Power BI Bot...")
    
        # Ejecutar app
        main()
