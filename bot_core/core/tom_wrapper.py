"""
TOM (Tabular Object Model) Wrapper

Wrapper alrededor del TOM de Microsoft para manipular modelos de Power BI.
Requiere pythonnet para interoperar con las DLLs .NET de Analysis Services.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Flag para indicar si TOM está disponible
TOM_AVAILABLE = False
Server = None
Database = None
Model = None

try:
    import clr  # pythonnet
    import sys
    from .pbi_detector import get_detector

    # Detectar Power BI Desktop y cargar DLLs
    detector = get_detector()
    if detector.dll_path:
        # Agregar ruta al sys.path para cargar dependencias
        sys.path.append(str(detector.dll_path))

        # Cargar DLLs (AMO de Power BI Desktop)
        amo_dll, adomd_dll = detector.get_dll_paths()

        # Cargar AMO
        clr.AddReference(str(amo_dll))

        # Importar clases de AMO (Analysis Management Objects)
        # Power BI Desktop usa Microsoft.AnalysisServices, no Tabular
        from Microsoft.AnalysisServices import Server, Database

        TOM_AVAILABLE = True
        logger.info(f"TOM cargado desde: {detector.dll_path}")
    else:
        logger.warning("Power BI Desktop no encontrado - funcionalidad TOM limitada")

except ImportError as e:
    logger.warning(f"pythonnet no disponible: {e}")
except Exception as e:
    logger.error(f"Error cargando TOM: {e}")


class MeasureDataType(Enum):
    """Tipos de datos para medidas DAX"""
    STRING = "String"
    INTEGER = "Integer"
    DECIMAL = "Decimal"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    CURRENCY = "Currency"
    AUTOMATIC = "Automatic"


@dataclass
class DAXMeasure:
    """Representa una medida DAX"""
    name: str
    expression: str
    table_name: str
    description: Optional[str] = None
    format_string: Optional[str] = None
    data_type: MeasureDataType = MeasureDataType.AUTOMATIC
    is_hidden: bool = False


@dataclass
class TableInfo:
    """Información de una tabla del modelo"""
    name: str
    description: Optional[str] = None
    is_hidden: bool = False
    measures_count: int = 0
    columns_count: int = 0
    rows_count: Optional[int] = None


@dataclass
class RelationshipInfo:
    """Información de una relación entre tablas"""
    name: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    is_active: bool = True
    cardinality: str = "ManyToOne"
    cross_filter_direction: str = "Single"


class TOMWrapper:
    """
    Wrapper del Tabular Object Model de Microsoft.

    Proporciona una interfaz Python simplificada para manipular
    modelos tabulares de Power BI.
    """

    def __init__(self, connection_string: str):
        """
        Inicializa el wrapper TOM.

        Args:
            connection_string: Connection string al servidor XMLA
        """
        self.connection_string = connection_string
        self.server = None
        self.database = None
        self.model = None
        self._is_connected = False

    def connect(self) -> bool:
        """
        Establece conexión y obtiene referencia al modelo.

        Returns:
            True si la conexión fue exitosa
        """
        if not TOM_AVAILABLE:
            logger.error("TOM no está disponible - instalar pythonnet")
            return False

        try:
            logger.info(f"Conectando a {self.connection_string}")

            # Crear servidor y conectar
            self.server = Server()
            self.server.Connect(self.connection_string)

            # Obtener la primera base de datos (el modelo abierto)
            if self.server.Databases.Count > 0:
                self.database = self.server.Databases[0]
                self.model = self.database.Model
                self._is_connected = True
                logger.info(f"✓ Conectado al modelo: {self.database.Name}")
                return True
            else:
                logger.error("No se encontró ningún modelo en el servidor")
                return False

        except Exception as e:
            logger.error(f"Error conectando al modelo: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        """Verifica si está conectado"""
        return self._is_connected

    # ==================== CONSULTAS ====================

    def get_tables(self) -> List[TableInfo]:
        """
        Obtiene lista de todas las tablas del modelo.

        Returns:
            Lista de TableInfo
        """
        if not self.is_connected:
            logger.warning("No hay conexión activa")
            return []

        try:
            tables = []
            for table in self.model.Tables:
                tables.append(TableInfo(
                    name=table.Name,
                    description=table.Description if table.Description else None,
                    is_hidden=table.IsHidden,
                    measures_count=table.Measures.Count,
                    columns_count=table.Columns.Count
                ))
            return tables

        except Exception as e:
            logger.error(f"Error obteniendo tablas: {e}")
            return []

    def get_measures(self, table_name: Optional[str] = None) -> List[DAXMeasure]:
        """
        Obtiene lista de medidas del modelo.

        Args:
            table_name: Filtrar por tabla específica (opcional)

        Returns:
            Lista de DAXMeasure
        """
        if not self.is_connected:
            logger.warning("No hay conexión activa")
            return []

        try:
            measures = []
            for table in self.model.Tables:
                if table_name and table.Name != table_name:
                    continue
                for measure in table.Measures:
                    measures.append(DAXMeasure(
                        name=measure.Name,
                        expression=measure.Expression,
                        table_name=table.Name,
                        description=measure.Description if measure.Description else None,
                        format_string=measure.FormatString if measure.FormatString else None,
                        is_hidden=measure.IsHidden
                    ))
            return measures

        except Exception as e:
            logger.error(f"Error obteniendo medidas: {e}")
            return []

    def get_relationships(self) -> List[RelationshipInfo]:
        """
        Obtiene lista de relaciones del modelo.

        Returns:
            Lista de RelationshipInfo
        """
        if not self.is_connected:
            logger.warning("No hay conexión activa")
            return []

        try:
            relationships = []
            for rel in self.model.Relationships:
                relationships.append(RelationshipInfo(
                    name=rel.Name if rel.Name else f"{rel.FromTable.Name}_{rel.ToTable.Name}",
                    from_table=rel.FromTable.Name,
                    from_column=rel.FromColumn.Name,
                    to_table=rel.ToTable.Name,
                    to_column=rel.ToColumn.Name,
                    is_active=rel.IsActive,
                    cardinality=str(rel.Cardinality),
                    cross_filter_direction=str(rel.CrossFilteringBehavior)
                ))
            return relationships

        except Exception as e:
            logger.error(f"Error obteniendo relaciones: {e}")
            return []

    def find_measure(self, measure_name: str) -> Optional[DAXMeasure]:
        """
        Busca una medida específica por nombre.

        Args:
            measure_name: Nombre de la medida

        Returns:
            DAXMeasure o None si no se encuentra
        """
        measures = self.get_measures()
        for measure in measures:
            if measure.name == measure_name:
                return measure
        return None

    def find_dependencies(self, measure_name: str) -> List[str]:
        """
        Encuentra qué medidas/columnas dependen de una medida.

        Args:
            measure_name: Nombre de la medida

        Returns:
            Lista de nombres de elementos que dependen de la medida
        """
        if not self.is_connected:
            return []

        try:
            # TODO: Implementar análisis de dependencias
            # Buscar referencias en todas las medidas
            # Parsear expresiones DAX para encontrar referencias

            return []

        except Exception as e:
            logger.error(f"Error buscando dependencias: {e}")
            return []

    # ==================== MODIFICACIONES ====================

    def create_measure(
        self,
        table_name: str,
        measure_name: str,
        expression: str,
        description: Optional[str] = None,
        format_string: Optional[str] = None
    ) -> bool:
        """
        Crea una nueva medida DAX en el modelo.

        Args:
            table_name: Nombre de la tabla donde crear la medida
            measure_name: Nombre de la nueva medida
            expression: Expresión DAX
            description: Descripción opcional
            format_string: Formato de visualización opcional

        Returns:
            True si la medida fue creada exitosamente
        """
        if not self.is_connected:
            logger.error("No hay conexión activa")
            return False

        try:
            logger.info(f"Creando medida '{measure_name}' en tabla '{table_name}'")
            logger.debug(f"Expresión: {expression}")

            # TODO: Implementar con TOM
            # table = self.model.Tables.Find(table_name)
            # if not table:
            #     logger.error(f"Tabla '{table_name}' no encontrada")
            #     return False
            #
            # measure = Measure()
            # measure.Name = measure_name
            # measure.Expression = expression
            # if description:
            #     measure.Description = description
            # if format_string:
            #     measure.FormatString = format_string
            #
            # table.Measures.Add(measure)
            # self.model.SaveChanges()

            logger.info(f"✓ Medida '{measure_name}' creada")
            return True

        except Exception as e:
            logger.error(f"Error creando medida: {e}")
            return False

    def update_measure(
        self,
        table_name: str,
        measure_name: str,
        new_expression: str,
        new_description: Optional[str] = None
    ) -> bool:
        """
        Actualiza una medida existente.

        Args:
            table_name: Nombre de la tabla
            measure_name: Nombre de la medida
            new_expression: Nueva expresión DAX
            new_description: Nueva descripción (opcional)

        Returns:
            True si la medida fue actualizada
        """
        if not self.is_connected:
            logger.error("No hay conexión activa")
            return False

        try:
            logger.info(f"Actualizando medida '{measure_name}'")

            # TODO: Implementar con TOM
            # table = self.model.Tables.Find(table_name)
            # if not table:
            #     return False
            #
            # measure = table.Measures.Find(measure_name)
            # if not measure:
            #     return False
            #
            # measure.Expression = new_expression
            # if new_description:
            #     measure.Description = new_description
            #
            # self.model.SaveChanges()

            logger.info("✓ Medida actualizada")
            return True

        except Exception as e:
            logger.error(f"Error actualizando medida: {e}")
            return False

    def delete_measure(self, table_name: str, measure_name: str) -> bool:
        """
        Elimina una medida del modelo.

        Args:
            table_name: Nombre de la tabla
            measure_name: Nombre de la medida

        Returns:
            True si la medida fue eliminada
        """
        if not self.is_connected:
            logger.error("No hay conexión activa")
            return False

        try:
            logger.info(f"Eliminando medida '{measure_name}' de '{table_name}'")

            # TODO: Implementar con TOM
            # table = self.model.Tables.Find(table_name)
            # if not table:
            #     return False
            #
            # measure = table.Measures.Find(measure_name)
            # if not measure:
            #     return False
            #
            # table.Measures.Remove(measure)
            # self.model.SaveChanges()

            logger.info("✓ Medida eliminada")
            return True

        except Exception as e:
            logger.error(f"Error eliminando medida: {e}")
            return False

    def rename_measure(
        self,
        old_name: str,
        new_name: str,
        update_references: bool = True
    ) -> bool:
        """
        Renombra una medida.

        Args:
            old_name: Nombre actual
            new_name: Nuevo nombre
            update_references: Si True, actualiza todas las referencias

        Returns:
            True si el renombrado fue exitoso
        """
        if not self.is_connected:
            logger.error("No hay conexión activa")
            return False

        try:
            logger.info(f"Renombrando medida '{old_name}' → '{new_name}'")

            if update_references:
                # Encontrar dependencias primero
                dependencies = self.find_dependencies(old_name)
                logger.info(f"Encontradas {len(dependencies)} referencias a actualizar")

            # TODO: Implementar con TOM
            # Buscar la medida en todas las tablas
            # measure_found = None
            # table_found = None
            # for table in self.model.Tables:
            #     measure = table.Measures.Find(old_name)
            #     if measure:
            #         measure_found = measure
            #         table_found = table
            #         break
            #
            # if not measure_found:
            #     logger.error(f"Medida '{old_name}' no encontrada")
            #     return False
            #
            # # Renombrar
            # measure_found.Name = new_name
            #
            # # Actualizar referencias si es necesario
            # if update_references:
            #     self._update_measure_references(old_name, new_name)
            #
            # self.model.SaveChanges()

            logger.info(f"✓ Medida renombrada")
            return True

        except Exception as e:
            logger.error(f"Error renombrando medida: {e}")
            return False

    def _update_measure_references(self, old_name: str, new_name: str) -> None:
        """
        Actualiza todas las referencias a una medida renombrada.

        Args:
            old_name: Nombre antiguo
            new_name: Nombre nuevo
        """
        # TODO: Implementar
        # Buscar en todas las expresiones DAX
        # Reemplazar [old_name] por [new_name]
        # Considerar casos especiales: 'Table'[old_name], etc.
        pass

    # ==================== VALIDACIÓN ====================

    def validate_dax(self, expression: str) -> Tuple[bool, Optional[str]]:
        """
        Valida la sintaxis de una expresión DAX.

        Args:
            expression: Expresión DAX a validar

        Returns:
            Tupla (es_válida, mensaje_error)
        """
        if not self.is_connected:
            return False, "No hay conexión activa"

        try:
            # TODO: Implementar validación real
            # Crear una medida temporal e intentar compilarla
            # Si no hay errores, la sintaxis es válida

            # Validación básica por ahora
            if not expression.strip():
                return False, "Expresión vacía"

            return True, None

        except Exception as e:
            return False, str(e)

    # ==================== UTILIDADES ====================

    def get_model_summary(self) -> Dict:
        """
        Obtiene un resumen del modelo.

        Returns:
            Diccionario con estadísticas del modelo
        """
        if not self.is_connected:
            return {}

        tables = self.get_tables()
        measures = self.get_measures()
        relationships = self.get_relationships()

        return {
            "tables_count": len(tables),
            "measures_count": len(measures),
            "relationships_count": len(relationships),
            "tables": [t.name for t in tables],
            "hidden_tables_count": sum(1 for t in tables if t.is_hidden),
            "hidden_measures_count": sum(1 for m in measures if m.is_hidden)
        }

    def disconnect(self) -> None:
        """Cierra la conexión al modelo"""
        if self._is_connected:
            logger.info("Cerrando conexión al modelo")
            # TODO: Cerrar conexión TOM
            # if self.server:
            #     self.server.Disconnect()
            self._is_connected = False
            self.model = None
            self.database = None
            self.server = None

    def __enter__(self):
        """Context manager support"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.disconnect()
