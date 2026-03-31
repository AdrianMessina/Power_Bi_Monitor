"""
PBIX File Reader - Lee archivos .pbix sin XMLA
Reutiliza el parser de documentation_generator_v3
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Parser no está disponible - usar XMLAConnector en su lugar
PARSER_AVAILABLE = False
logger.info("PBIXFileReader: Parser deshabilitado - usar XMLAConnector en su lugar")


@dataclass
class ModelData:
    """Datos extraídos del modelo"""
    tables: List[Dict]
    measures: List[Dict]
    relationships: List[Dict]
    columns: List[Dict]


class PBIXFileReader:
    """Lee archivos .pbix directamente sin XMLA"""

    def __init__(self, pbix_path: str):
        self.pbix_path = pbix_path
        self.model_data: Optional[ModelData] = None

    def extract_model(self) -> ModelData:
        """Extrae el modelo completo del .pbix"""

        if not PARSER_AVAILABLE:
            logger.error("Parser no disponible")
            return ModelData(tables=[], measures=[], relationships=[], columns=[])

        try:
            logger.info(f"Extrayendo modelo de: {self.pbix_path}")

            # Usar el parser existente
            parser = PBIXParser(self.pbix_path)
            model = parser.parse()

            # Extraer tablas
            tables = []
            for table in model.tables:
                tables.append({
                    'name': table.name,
                    'description': table.description if hasattr(table, 'description') else '',
                    'columns_count': len(table.columns) if hasattr(table, 'columns') else 0,
                    'measures_count': len(table.measures) if hasattr(table, 'measures') else 0,
                    'is_hidden': table.is_hidden if hasattr(table, 'is_hidden') else False
                })

            # Extraer medidas
            measures = []
            for table in model.tables:
                if hasattr(table, 'measures'):
                    for measure in table.measures:
                        measures.append({
                            'name': measure.name,
                            'table': table.name,
                            'expression': measure.expression if hasattr(measure, 'expression') else '',
                            'description': measure.description if hasattr(measure, 'description') else '',
                            'format': measure.format_string if hasattr(measure, 'format_string') else ''
                        })

            # Extraer relaciones
            relationships = []
            if hasattr(model, 'relationships'):
                for rel in model.relationships:
                    relationships.append({
                        'from_table': rel.from_table if hasattr(rel, 'from_table') else '',
                        'from_column': rel.from_column if hasattr(rel, 'from_column') else '',
                        'to_table': rel.to_table if hasattr(rel, 'to_table') else '',
                        'to_column': rel.to_column if hasattr(rel, 'to_column') else '',
                        'cardinality': rel.cardinality if hasattr(rel, 'cardinality') else 'Unknown',
                        'is_active': rel.is_active if hasattr(rel, 'is_active') else True
                    })

            # Extraer columnas
            columns = []
            for table in model.tables:
                if hasattr(table, 'columns'):
                    for column in table.columns:
                        columns.append({
                            'name': column.name,
                            'table': table.name,
                            'data_type': column.data_type if hasattr(column, 'data_type') else '',
                            'is_hidden': column.is_hidden if hasattr(column, 'is_hidden') else False
                        })

            self.model_data = ModelData(
                tables=tables,
                measures=measures,
                relationships=relationships,
                columns=columns
            )

            logger.info(f"Modelo extraído: {len(tables)} tablas, {len(measures)} medidas")
            return self.model_data

        except Exception as e:
            logger.error(f"Error extrayendo modelo: {e}")
            return ModelData(tables=[], measures=[], relationships=[], columns=[])

    def get_summary(self) -> Dict:
        """Obtiene resumen del modelo"""
        if not self.model_data:
            return {}

        return {
            'tables_count': len(self.model_data.tables),
            'measures_count': len(self.model_data.measures),
            'relationships_count': len(self.model_data.relationships),
            'columns_count': len(self.model_data.columns),
            'tables': [t['name'] for t in self.model_data.tables],
            'hidden_tables_count': sum(1 for t in self.model_data.tables if t.get('is_hidden', False))
        }

    def get_measures_by_table(self, table_name: Optional[str] = None) -> List[Dict]:
        """Obtiene medidas, opcionalmente filtradas por tabla"""
        if not self.model_data:
            return []

        measures = self.model_data.measures
        if table_name:
            measures = [m for m in measures if m['table'] == table_name]

        return measures

    def search_measures(self, query: str) -> List[Dict]:
        """Busca medidas por nombre o expresión"""
        if not self.model_data:
            return []

        query_lower = query.lower()
        results = []

        for measure in self.model_data.measures:
            if (query_lower in measure['name'].lower() or
                query_lower in measure.get('expression', '').lower()):
                results.append(measure)

        return results
