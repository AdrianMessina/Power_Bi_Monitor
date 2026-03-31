"""
Parser para archivos TMDL (Tabular Model Definition Language)
Formato nuevo de Power BI introducido en 2023
"""

import os
import re
from typing import Dict, List, Any


class TMDLParser:
    """Parser para archivos TMDL de Power BI"""

    def __init__(self, semantic_model_path: str):
        """
        Inicializa el parser TMDL

        Args:
            semantic_model_path: Ruta a la carpeta .SemanticModel
        """
        self.semantic_model_path = semantic_model_path
        self.definition_path = os.path.join(semantic_model_path, 'definition')

    def parse_model(self) -> Dict[str, Any]:
        """
        Parsea todo el modelo TMDL

        Returns:
            Diccionario con estructura similar a BIM para compatibilidad
        """
        print(f"📖 Parseando modelo TMDL desde: {self.semantic_model_path}")

        # Leer archivos principales
        tables_list = self._parse_model_file()
        relationships = self._parse_relationships()
        tables_detail = self._parse_all_tables()

        # Construir estructura compatible con BIM
        model = {
            'model': {
                'tables': tables_detail,
                'relationships': relationships,
                'cultures': [{'name': 'es-AR'}]  # Default
            }
        }

        print(f"✅ TMDL: {len(tables_detail)} tablas, {len(relationships)} relaciones parseadas")

        return model

    def _parse_model_file(self) -> List[str]:
        """Parsea model.tmdl para obtener lista de tablas"""
        model_file = os.path.join(self.definition_path, 'model.tmdl')

        if not os.path.exists(model_file):
            print(f"⚠️  No se encontró model.tmdl")
            return []

        tables = []
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Buscar líneas "ref table 'NombreTabla'" o "ref table NombreTabla"
            table_pattern = r"ref table ['\"]?([^'\"\n]+)['\"]?"
            matches = re.findall(table_pattern, content)

            for match in matches:
                table_name = match.strip()
                tables.append(table_name)

        print(f"📋 model.tmdl: {len(tables)} tablas referenciadas")
        return tables

    def _parse_relationships(self) -> List[Dict]:
        """Parsea relationships.tmdl"""
        rel_file = os.path.join(self.definition_path, 'relationships.tmdl')

        if not os.path.exists(rel_file):
            print(f"⚠️  No se encontró relationships.tmdl")
            return []

        relationships = []

        with open(rel_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Dividir por cada relationship
        rel_blocks = re.split(r'\nrelationship ', content)

        for block in rel_blocks[1:]:  # Saltar el primero que está vacío
            rel = self._parse_relationship_block(block)
            if rel:
                relationships.append(rel)

        print(f"🔗 relationships.tmdl: {len(relationships)} relaciones parseadas")

        return relationships

    def _parse_relationship_block(self, block: str) -> Dict:
        """Parsea un bloque de relación individual"""
        lines = block.strip().split('\n')

        rel = {
            'fromTable': None,
            'fromColumn': None,
            'toTable': None,
            'toColumn': None,
            'crossFilteringBehavior': 'oneDirection',  # Default
            'fromCardinality': 'many',  # Default
            'toCardinality': 'one'  # Default
        }

        for line in lines:
            line = line.strip()

            # fromColumn: 'Tabla'.'Columna' o Tabla.Columna
            # Soporta nombres con espacios: 'Vol Diario'.'Producto Cond'
            if line.startswith('fromColumn:'):
                match = re.search(r"fromColumn:\s*(?:'([^']+)'|([^\s.]+))\.(?:'([^']+)'|([^\s.]+))", line)
                if match:
                    rel['fromTable'] = (match.group(1) or match.group(2)).strip()
                    rel['fromColumn'] = (match.group(3) or match.group(4)).strip()

            # toColumn: 'Tabla'.'Columna' o Tabla.Columna
            # Soporta nombres con espacios: 'Vol Diario'.'Producto Cond'
            elif line.startswith('toColumn:'):
                match = re.search(r"toColumn:\s*(?:'([^']+)'|([^\s.]+))\.(?:'([^']+)'|([^\s.]+))", line)
                if match:
                    rel['toTable'] = (match.group(1) or match.group(2)).strip()
                    rel['toColumn'] = (match.group(3) or match.group(4)).strip()

            # crossFilteringBehavior: bothDirections o oneDirection
            elif line.startswith('crossFilteringBehavior:'):
                behavior = line.split(':', 1)[1].strip()
                rel['crossFilteringBehavior'] = behavior

            # fromCardinality: one, many
            elif line.startswith('fromCardinality:'):
                card = line.split(':', 1)[1].strip()
                rel['fromCardinality'] = card

            # toCardinality: one, many
            elif line.startswith('toCardinality:'):
                card = line.split(':', 1)[1].strip()
                rel['toCardinality'] = card

        # Validar que se encontraron los campos mínimos
        if rel['fromTable'] and rel['fromColumn'] and rel['toTable'] and rel['toColumn']:
            return rel

        return None

    def _parse_all_tables(self) -> List[Dict]:
        """Parsea todos los archivos .tmdl de tablas"""
        tables_dir = os.path.join(self.definition_path, 'tables')

        if not os.path.exists(tables_dir):
            print(f"⚠️  No se encontró carpeta tables/")
            return []

        tables = []

        for filename in os.listdir(tables_dir):
            if filename.endswith('.tmdl'):
                table_path = os.path.join(tables_dir, filename)
                table = self._parse_table_file(table_path)
                if table:
                    tables.append(table)

        print(f"📊 tables/: {len(tables)} archivos parseados")

        return tables

    def _parse_table_file(self, table_path: str) -> Dict:
        """Parsea un archivo de tabla individual"""
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraer nombre de la tabla (primera línea: "table NombreTabla")
        table_match = re.match(r"table ['\"]?([^'\"\n]+)['\"]?", content)
        if not table_match:
            return None

        table_name = table_match.group(1).strip()

        table = {
            'name': table_name,
            'columns': [],
            'measures': [],
            'partitions': []
        }

        # Parsear medidas
        measures = self._parse_measures(content, table_name)
        table['measures'] = measures

        # Parsear columnas
        columns = self._parse_columns(content, table_name)
        table['columns'] = columns

        # Detectar si es tabla calculada (tiene partition con expression)
        if 'partition' in content and 'mode: import' in content:
            # Buscar si tiene expression
            if re.search(r'partition.*?\n\s+mode:\s+import\n\s+source\s+=', content, re.DOTALL):
                table['partitions'].append({
                    'name': table_name,
                    'mode': 'import'
                })

        return table

    def _parse_measures(self, content: str, table_name: str) -> List[Dict]:
        """Parsea medidas DAX de un archivo de tabla"""
        measures = []

        # Patrón para encontrar medidas
        # measure 'Nombre' = expression
        # o measure 'Nombre' = ``` expression ```
        measure_pattern = r"measure ['\"]?([^'\"=]+)['\"]?\s*=\s*(`{3}[\s\S]*?`{3}|[^\n]+(?:\n\t\t[^\n]+)*)"

        matches = re.finditer(measure_pattern, content)

        for match in matches:
            measure_name = match.group(1).strip()
            expression = match.group(2).strip()

            # Limpiar backticks si existen
            expression = expression.replace('```', '').strip()

            measures.append({
                'name': measure_name,
                'expression': expression,
                'table': table_name
            })

        return measures

    def _parse_columns(self, content: str, table_name: str) -> List[Dict]:
        """Parsea columnas de un archivo de tabla"""
        columns = []

        # Patrón para columnas
        # column 'Nombre'
        column_pattern = r"column ['\"]?([^'\"=\n]+)['\"]?"

        matches = re.finditer(column_pattern, content)

        for match in matches:
            column_name = match.group(1).strip()

            # Verificar si es columna calculada (tiene =)
            # Buscar si después del nombre hay un =
            start_pos = match.end()
            next_lines = content[start_pos:start_pos+200]

            is_calculated = False
            expression = None

            if '=' in next_lines.split('\n')[0]:
                is_calculated = True
                # Extraer expresión
                expr_match = re.search(r'=\s*(`{3}[\s\S]*?`{3}|[^\n]+)', next_lines)
                if expr_match:
                    expression = expr_match.group(1).strip().replace('```', '')

            column = {
                'name': column_name,
                'table': table_name
            }

            if is_calculated and expression:
                column['expression'] = expression
                column['type'] = 'calculated'

            columns.append(column)

        return columns


def parse_tmdl_model(semantic_model_path: str) -> Dict[str, Any]:
    """
    Función helper para parsear un modelo TMDL

    Args:
        semantic_model_path: Ruta a la carpeta .SemanticModel

    Returns:
        Diccionario con estructura compatible con BIM
    """
    parser = TMDLParser(semantic_model_path)
    return parser.parse_model()
