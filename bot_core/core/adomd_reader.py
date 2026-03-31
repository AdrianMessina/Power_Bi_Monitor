"""
ADOMD Reader - Lectura de modelos Power BI usando ADOMD
Alternativa más simple que TOM para consultas de solo lectura
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ADOMD_AVAILABLE = False
AdomdConnection = None

try:
    import clr
    import sys
    from .pbi_detector import get_detector

    detector = get_detector()
    if detector.dll_path:
        sys.path.append(str(detector.dll_path))

        # Cargar ADOMD Client (más ligero para consultas)
        adomd_path = detector.dll_path / "Microsoft.AnalysisServices.AdomdClient.dll"
        if adomd_path.exists():
            clr.AddReference(str(adomd_path))
            from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand
            ADOMD_AVAILABLE = True
            logger.info("ADOMD Client cargado OK")
        else:
            logger.warning("ADOMD Client DLL no encontrada")
    else:
        logger.warning("Power BI Desktop no encontrado")

except Exception as e:
    logger.error(f"Error cargando ADOMD: {e}")


@dataclass
class ModelInfo:
    """Información básica del modelo"""
    tables: List[str]
    measures: List[Dict[str, str]]
    relationships: List[Dict[str, str]]


class AdomdReader:
    """Lector de modelos usando ADOMD (solo lectura)"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self._is_connected = False

    def connect(self) -> bool:
        """Establece conexión usando ADOMD"""
        if not ADOMD_AVAILABLE:
            logger.error("ADOMD no disponible")
            return False

        try:
            self.connection = AdomdConnection(self.connection_string)
            self.connection.Open()
            self._is_connected = True
            logger.info("Conectado via ADOMD")
            return True
        except Exception as e:
            logger.error(f"Error conectando ADOMD: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def execute_query(self, query: str) -> List[List]:
        """Ejecuta una consulta DMV"""
        if not self.is_connected:
            return []

        try:
            command = AdomdCommand(query, self.connection)
            reader = command.ExecuteReader()

            results = []
            while reader.Read():
                row = []
                for i in range(reader.FieldCount):
                    row.append(str(reader[i]) if reader[i] is not None else "")
                results.append(row)

            reader.Close()
            return results
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            return []

    def get_tables(self) -> List[str]:
        """Obtiene lista de tablas usando DMV"""
        query = """
        SELECT [Name]
        FROM $SYSTEM.TMSCHEMA_TABLES
        WHERE [Hidden] = false
        ORDER BY [Name]
        """

        results = self.execute_query(query)
        return [row[0] for row in results]

    def get_measures(self) -> List[Dict[str, str]]:
        """Obtiene lista de medidas usando DMV"""
        query = """
        SELECT
            t.[Name] as TableName,
            m.[Name] as MeasureName,
            m.[Expression] as Expression
        FROM $SYSTEM.TMSCHEMA_MEASURES m
        JOIN $SYSTEM.TMSCHEMA_TABLES t ON m.[TableID] = t.[ID]
        WHERE m.[Hidden] = false
        ORDER BY t.[Name], m.[Name]
        """

        results = self.execute_query(query)
        measures = []
        for row in results:
            measures.append({
                'table': row[0],
                'name': row[1],
                'expression': row[2]
            })
        return measures

    def get_relationships(self) -> List[Dict[str, str]]:
        """Obtiene relaciones usando DMV"""
        query = """
        SELECT
            ft.[Name] as FromTable,
            fc.[Name] as FromColumn,
            tt.[Name] as ToTable,
            tc.[Name] as ToColumn
        FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS r
        JOIN $SYSTEM.TMSCHEMA_COLUMNS fc ON r.[FromColumnID] = fc.[ID]
        JOIN $SYSTEM.TMSCHEMA_TABLES ft ON fc.[TableID] = ft.[ID]
        JOIN $SYSTEM.TMSCHEMA_COLUMNS tc ON r.[ToColumnID] = tc.[ID]
        JOIN $SYSTEM.TMSCHEMA_TABLES tt ON tc.[TableID] = tt.[ID]
        ORDER BY ft.[Name], tt.[Name]
        """

        results = self.execute_query(query)
        relationships = []
        for row in results:
            relationships.append({
                'from_table': row[0],
                'from_column': row[1],
                'to_table': row[2],
                'to_column': row[3]
            })
        return relationships

    def get_model_info(self) -> ModelInfo:
        """Obtiene información completa del modelo"""
        return ModelInfo(
            tables=self.get_tables(),
            measures=self.get_measures(),
            relationships=self.get_relationships()
        )

    def disconnect(self) -> None:
        """Cierra conexión"""
        if self.connection and self._is_connected:
            try:
                self.connection.Close()
                self._is_connected = False
                logger.info("ADOMD desconectado")
            except Exception as e:
                logger.error(f"Error desconectando: {e}")
