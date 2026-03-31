"""
XMLA Connector for Power BI Desktop

Detecta y se conecta al endpoint XMLA local de Power BI Desktop
cuando un archivo .pbix está abierto.
"""

import socket
import subprocess
import re
import json
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Metadata básica del modelo de Power BI"""
    name: str
    database_id: str
    compatibility_level: int
    tables_count: int
    measures_count: int
    relationships_count: int
    last_update: Optional[str] = None


class XMLAConnector:
    """
    Conector XMLA para Power BI Desktop.

    Power BI Desktop expone un endpoint XMLA local cuando un archivo
    está abierto. Este conector detecta el puerto y establece conexión.
    """

    def __init__(self):
        self.connection_string: Optional[str] = None
        self.port: Optional[int] = None
        self.is_connected: bool = False
        self._model_metadata: Optional[ModelMetadata] = None
        self._tom_wrapper = None

    def detect_pbi_port(self) -> Optional[int]:
        """
        Detecta el puerto XMLA activo de Power BI Desktop.

        Power BI Desktop usa un puerto dinámico que se puede encontrar en:
        1. Archivo msmdsrv.port.txt en AppData
        2. Procesos activos (buscar msmdsrv.exe)

        Returns:
            Puerto XMLA o None si no se encuentra
        """
        logger.info("Detectando puerto XMLA de Power BI Desktop...")

        # Método 1: Buscar archivo de puerto
        port = self._find_port_from_file()
        if port:
            logger.info(f"Puerto encontrado en archivo: {port}")
            return port

        # Método 2: Buscar en procesos activos
        port = self._find_port_from_process()
        if port:
            logger.info(f"Puerto encontrado en proceso: {port}")
            return port

        logger.warning("No se pudo detectar el puerto XMLA. ¿Power BI Desktop está abierto?")
        return None

    def _find_port_from_file(self) -> Optional[int]:
        """
        Busca el archivo msmdsrv.port.txt que contiene el puerto XMLA.

        La ubicación típica es:
        C:\\Users\\<user>\\AppData\\Local\\Microsoft\\Power BI Desktop\\AnalysisServicesWorkspaces\\<workspace>\\Data\\msmdsrv.port.txt
        """
        try:
            appdata_local = Path.home() / "AppData" / "Local" / "Microsoft" / "Power BI Desktop"
            workspaces_path = appdata_local / "AnalysisServicesWorkspaces"

            if not workspaces_path.exists():
                logger.debug("Directorio de workspaces no encontrado")
                return None

            # Buscar el archivo de puerto en todos los workspaces
            for workspace_dir in workspaces_path.iterdir():
                if workspace_dir.is_dir():
                    port_file = workspace_dir / "Data" / "msmdsrv.port.txt"
                    if port_file.exists():
                        try:
                            port = int(port_file.read_text().strip())
                            # Verificar que el puerto está en uso
                            if self._is_port_open(port):
                                return port
                        except (ValueError, OSError) as e:
                            logger.debug(f"Error leyendo {port_file}: {e}")
                            continue
        except Exception as e:
            logger.debug(f"Error buscando archivo de puerto: {e}")

        return None

    def _find_port_from_process(self) -> Optional[int]:
        """
        Busca el puerto XMLA desde los procesos activos.
        Busca msmdsrv.exe (Analysis Services) de Power BI Desktop.
        """
        try:
            # Usar netstat para encontrar puertos escuchando de msmdsrv.exe
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            # Parsear salida de netstat
            # Buscar líneas con LISTENING y localhost
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line and '127.0.0.1' in line:
                    # Extraer puerto
                    match = re.search(r'127\.0\.0\.1:(\d+)', line)
                    if match:
                        port = int(match.group(1))
                        # Verificar que sea un puerto típico de Analysis Services (rango 50000-60000)
                        if 50000 <= port <= 60000:
                            # Verificar que responda como servidor XMLA
                            if self._is_xmla_server(port):
                                return port
        except Exception as e:
            logger.debug(f"Error buscando puerto en procesos: {e}")

        return None

    def _is_port_open(self, port: int, host: str = "localhost") -> bool:
        """Verifica si un puerto está abierto"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False

    def _is_xmla_server(self, port: int) -> bool:
        """
        Verifica si el puerto es un servidor XMLA válido.
        Intenta una conexión básica.
        """
        # Por ahora, solo verificamos que el puerto esté abierto
        # En una implementación completa, haríamos una consulta XMLA de prueba
        return self._is_port_open(port)

    def connect(self, port: Optional[int] = None) -> bool:
        """
        Establece conexión con el servidor XMLA.

        Args:
            port: Puerto XMLA. Si es None, se detecta automáticamente.

        Returns:
            True si la conexión fue exitosa
        """
        if port is None:
            port = self.detect_pbi_port()

        if port is None:
            logger.error("No se pudo detectar el puerto XMLA")
            return False

        self.port = port
        self.connection_string = f"Provider=MSOLAP;Data Source=localhost:{port}"

        logger.info(f"Intentando conexión a {self.connection_string}")

        # TODO: Establecer conexión real usando pythonnet y AMO/TOM
        # Por ahora, marcamos como conectado si el puerto está abierto
        self.is_connected = self._is_port_open(port)

        if self.is_connected:
            logger.info("✓ Conexión establecida")
            # Obtener metadata del modelo
            self._load_model_metadata()
            # Crear TOM wrapper
            self._initialize_tom()
        else:
            logger.error("✗ No se pudo establecer conexión")

        return self.is_connected

    def _load_model_metadata(self) -> None:
        """Carga metadata básica del modelo conectado"""
        # TODO: Implementar con pythonnet y TOM
        # Por ahora, creamos metadata de prueba
        self._model_metadata = ModelMetadata(
            name="PowerBI_Model",
            database_id="local",
            compatibility_level=1500,
            tables_count=0,
            measures_count=0,
            relationships_count=0
        )

    def get_metadata(self) -> Optional[ModelMetadata]:
        """Obtiene metadata del modelo conectado"""
        if not self.is_connected:
            logger.warning("No hay conexión activa")
            return None
        return self._model_metadata

    def execute_tmsl(self, tmsl_script: str) -> Dict:
        """
        Ejecuta un script TMSL (Tabular Model Scripting Language).

        TMSL es el lenguaje de scripting para modificar modelos tabulares.

        Args:
            tmsl_script: Script TMSL en formato JSON

        Returns:
            Resultado de la ejecución
        """
        if not self.is_connected:
            raise ConnectionError("No hay conexión activa al servidor XMLA")

        logger.info("Ejecutando script TMSL...")
        logger.debug(f"Script: {tmsl_script}")

        # TODO: Implementar ejecución real con pythonnet
        # Por ahora, retornamos un resultado simulado
        return {
            "success": True,
            "message": "Script ejecutado (simulado)"
        }

    def get_tables(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de tablas del modelo.

        Returns:
            Lista de diccionarios con info de cada tabla
        """
        if not self.is_connected:
            return []

        # TODO: Implementar con TOM
        return []

    def get_measures(self, table_name: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Obtiene lista de medidas del modelo.

        Args:
            table_name: Filtrar por tabla específica (opcional)

        Returns:
            Lista de diccionarios con info de cada medida
        """
        if not self.is_connected:
            return []

        # TODO: Implementar con TOM
        return []

    def get_relationships(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de relaciones del modelo.

        Returns:
            Lista de diccionarios con info de cada relación
        """
        if not self.is_connected:
            return []

        # TODO: Implementar con TOM
        return []

    def _initialize_tom(self) -> None:
        """Inicializa el TOM Wrapper si está disponible"""
        try:
            from .tom_wrapper import TOMWrapper, TOM_AVAILABLE

            if TOM_AVAILABLE and self.connection_string:
                self._tom_wrapper = TOMWrapper(self.connection_string)
                if self._tom_wrapper.connect():
                    logger.info("✓ TOM Wrapper inicializado")
                else:
                    logger.warning("No se pudo inicializar TOM Wrapper")
                    self._tom_wrapper = None
        except Exception as e:
            logger.error(f"Error inicializando TOM: {e}")
            self._tom_wrapper = None

    def get_tom_wrapper(self):
        """Obtiene el TOM Wrapper para acceso directo al modelo"""
        return self._tom_wrapper

    def disconnect(self) -> None:
        """Cierra la conexión XMLA"""
        if self.is_connected:
            logger.info("Cerrando conexión XMLA")
            # Cerrar TOM si está activo
            if self._tom_wrapper:
                self._tom_wrapper.disconnect()
                self._tom_wrapper = None
            # TODO: Cerrar conexión real
            self.is_connected = False
            self.connection_string = None
            self.port = None
            self._model_metadata = None

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.disconnect()


# Función de utilidad para uso rápido
def quick_connect() -> Optional[XMLAConnector]:
    """
    Intenta conectarse rápidamente a Power BI Desktop.

    Returns:
        Conector conectado o None si falla
    """
    connector = XMLAConnector()
    if connector.connect():
        return connector
    return None
