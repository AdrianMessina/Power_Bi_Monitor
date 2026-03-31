"""
Analizador de archivos Power BI (.pbix)
Extrae metadata y métricas de archivos .pbix para análisis de mejores prácticas
"""

import zipfile
import json
import os
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import yaml


class PBIXAnalyzer:
    """Clase principal para analizar archivos .pbix"""

    def __init__(self, pbix_path: str, config_path: str = None):
        """
        Inicializa el analizador

        Args:
            pbix_path: Ruta al archivo .pbix
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.pbix_path = pbix_path
        self.report_name = os.path.basename(pbix_path)
        self.config = self._load_config(config_path)
        self.metrics = {}
        self.warnings = []
        self.recommendations = []

    def _load_config(self, config_path: str = None) -> Dict:
        """Carga la configuración de umbrales"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config', 'thresholds.yaml'
            )

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Retorna configuración por defecto si no existe archivo"""
        return {
            'thresholds': {
                'visualizations_per_page': {'good': 10, 'warning': 15, 'critical': 20},
                'filters_per_page': {'good': 5, 'warning': 8, 'critical': 12},
                'custom_visuals': {'good': 3, 'warning': 5, 'critical': 8},
                'embedded_images_mb': {'good': 1.0, 'warning': 5.0, 'critical': 10.0},
                'total_pages': {'good': 10, 'warning': 20, 'critical': 30},
            },
            'weights': {
                'visualizations_per_page': 0.20,
                'filters_per_page': 0.20,
                'custom_visuals': 0.20,
                'embedded_images_mb': 0.20,
                'total_pages': 0.20,
            }
        }

    def analyze(self) -> Dict[str, Any]:
        """
        Ejecuta el análisis completo del archivo .pbix

        Returns:
            Diccionario con todas las métricas y resultados
        """
        print(f"Analizando: {self.report_name}")

        try:
            with zipfile.ZipFile(self.pbix_path, 'r') as zip_ref:
                # Analizar Layout (visualizaciones, páginas, filtros)
                self._analyze_layout(zip_ref)

                # Analizar DataModel (tablas, relaciones, medidas DAX)
                self._analyze_datamodel(zip_ref)

                # Analizar Custom Visuals
                self._analyze_custom_visuals(zip_ref)

                # Analizar imágenes embebidas
                self._analyze_embedded_resources(zip_ref)

                # Calcular tamaño del modelo
                self._calculate_model_size(zip_ref)

            # Calcular score general
            self._calculate_score()

            # Generar recomendaciones
            self._generate_recommendations()

            return self._build_result()

        except zipfile.BadZipFile:
            raise ValueError(f"El archivo {self.pbix_path} no es un archivo .pbix válido")
        except Exception as e:
            raise Exception(f"Error analizando el archivo: {str(e)}")

    def _analyze_layout(self, zip_ref: zipfile.ZipFile):
        """
        Analiza el layout del reporte (páginas, visuales, filtros, bookmarks, themes, etc.)

        IMPORTANTE: Esta información SÍ está disponible en archivos PBIX porque está en Report/Layout (JSON)
        """
        try:
            # El layout está en Report/Layout
            layout_data = zip_ref.read('Report/Layout').decode('utf-16-le')
            layout_json = json.loads(layout_data)

            # ===== ANÁLISIS DE PÁGINAS Y VISUALES =====
            pages = layout_json.get('sections', [])
            self.metrics['total_pages'] = len(pages)

            visuals_per_page = []
            filters_per_page = []
            total_visuals = 0
            visual_types = defaultdict(int)

            # Contadores específicos de diseño
            slicers_count = 0
            buttons_count = 0
            shapes_count = 0
            textboxes_count = 0
            images_count = 0
            tables_count = 0
            hidden_pages = 0
            tooltip_pages = 0

            # Detalles de páginas
            pages_detail = []

            for page in pages:
                page_info = {
                    'name': page.get('displayName', page.get('name', 'Sin nombre')),
                    'visuals_count': 0,
                    'filters_count': 0,
                    'hidden': False,
                    'tooltip': False,
                    'width': 0,
                    'height': 0
                }

                # Verificar si es página oculta
                if page.get('visibility', 0) == 1:
                    hidden_pages += 1
                    page_info['hidden'] = True

                # Verificar si es página de tooltip
                config = page.get('config', '{}')
                try:
                    page_config = json.loads(config) if isinstance(config, str) else config
                    if page_config.get('displayOption') == 3:  # 3 = Tooltip page
                        tooltip_pages += 1
                        page_info['tooltip'] = True
                except:
                    pass

                # Dimensiones de la página
                page_info['width'] = page.get('width', 0)
                page_info['height'] = page.get('height', 0)

                # Contar visuales por página
                visuals = page.get('visualContainers', [])
                visuals_per_page.append(len(visuals))
                total_visuals += len(visuals)
                page_info['visuals_count'] = len(visuals)

                # Tipos de visuales - MEJORADO con categorías específicas
                for visual in visuals:
                    config = visual.get('config', '{}')
                    try:
                        config_json = json.loads(config)
                        visual_type = config_json.get('singleVisual', {}).get('visualType', 'unknown')
                        visual_types[visual_type] += 1

                        # Categorizar visuales importantes para diseño
                        if visual_type == 'slicer':
                            slicers_count += 1
                        elif visual_type == 'actionButton':
                            buttons_count += 1
                        elif visual_type in ['shape', 'rectangle', 'ellipse', 'line']:
                            shapes_count += 1
                        elif visual_type == 'textbox':
                            textboxes_count += 1
                        elif visual_type == 'image':
                            images_count += 1
                        elif visual_type in ['tableEx', 'pivotTable', 'matrix']:
                            tables_count += 1
                    except:
                        pass

                # Contar filtros por página
                filters = page.get('filters', '[]')
                try:
                    filters_json = json.loads(filters) if isinstance(filters, str) else filters
                    filters_per_page.append(len(filters_json))
                    page_info['filters_count'] = len(filters_json)
                except:
                    filters_per_page.append(0)

                pages_detail.append(page_info)

            # Métricas de visuales
            self.metrics['total_visuals'] = total_visuals
            self.metrics['avg_visuals_per_page'] = sum(visuals_per_page) / len(pages) if pages else 0
            self.metrics['max_visuals_per_page'] = max(visuals_per_page) if visuals_per_page else 0
            self.metrics['visual_types'] = dict(visual_types)

            # Métricas de diseño específicas (NUEVO - v1.1)
            self.metrics['slicers_count'] = slicers_count
            self.metrics['buttons_count'] = buttons_count
            self.metrics['shapes_count'] = shapes_count
            self.metrics['textboxes_count'] = textboxes_count
            self.metrics['images_in_visuals_count'] = images_count
            self.metrics['tables_count'] = tables_count
            self.metrics['hidden_pages_count'] = hidden_pages
            self.metrics['tooltip_pages_count'] = tooltip_pages
            self.metrics['pages_detail'] = pages_detail

            # Métricas de filtros
            self.metrics['total_filters'] = sum(filters_per_page)
            self.metrics['avg_filters_per_page'] = sum(filters_per_page) / len(pages) if pages else 0
            self.metrics['max_filters_per_page'] = max(filters_per_page) if filters_per_page else 0

            # ===== FILTROS A NIVEL DE REPORTE (NUEVO - v1.1) =====
            report_filters = layout_json.get('filters', '[]')
            try:
                report_filters_json = json.loads(report_filters) if isinstance(report_filters, str) else report_filters
                self.metrics['report_level_filters'] = len(report_filters_json)
            except:
                self.metrics['report_level_filters'] = 0

            # ===== BOOKMARKS (NUEVO - v1.1) =====
            bookmarks = layout_json.get('bookmarks', [])
            self.metrics['bookmarks_count'] = len(bookmarks)
            self.metrics['bookmarks_detail'] = [{
                'name': bm.get('displayName', bm.get('name', 'Sin nombre')),
                'page': bm.get('explorationState', {}).get('activeSection', 'N/A')
            } for bm in bookmarks[:10]]  # Primeros 10 para no saturar

            # ===== THEME/TEMA (NUEVO - v1.1) =====
            theme = layout_json.get('config', '{}')
            try:
                theme_config = json.loads(theme) if isinstance(theme, str) else theme
                has_custom_theme = 'theme' in theme_config or 'themeJson' in theme_config
                self.metrics['has_custom_theme'] = has_custom_theme

                # Intentar obtener nombre del tema
                if has_custom_theme:
                    theme_json = theme_config.get('themeJson') or theme_config.get('theme', {})
                    if isinstance(theme_json, str):
                        theme_json = json.loads(theme_json)
                    self.metrics['theme_name'] = theme_json.get('name', 'Tema personalizado')
                else:
                    self.metrics['theme_name'] = 'Tema predeterminado'
            except:
                self.metrics['has_custom_theme'] = False
                self.metrics['theme_name'] = 'Desconocido'

            # ===== CONFIGURACIÓN DEL REPORTE (NUEVO - v1.1) =====
            self.metrics['report_config'] = {
                'default_page': layout_json.get('activeSection', 'Página 1'),
                'layout_type': layout_json.get('layoutType', 'Master'),
                'has_resource_packages': 'resourcePackages' in layout_json
            }

            print(f"[OK] Layout analizado: {len(pages)} paginas, {total_visuals} visuales")
            print(f"     Diseno: {slicers_count} slicers, {buttons_count} botones, {len(bookmarks) if isinstance(bookmarks, list) else 0} bookmarks")

        except KeyError as e:
            print(f"Warning: No se pudo leer el layout del reporte - {str(e)}")
            self.metrics['total_pages'] = 0
            self.metrics['total_visuals'] = 0
            # Inicializar nuevas métricas como 0
            self.metrics['slicers_count'] = 0
            self.metrics['buttons_count'] = 0
            self.metrics['bookmarks_count'] = 0
            self.metrics['has_custom_theme'] = False

    def _analyze_datamodel(self, zip_ref: zipfile.ZipFile):
        """
        Analiza el modelo de datos (tablas, relaciones, medidas DAX)

        IMPORTANTE: Para PBIX, solo podemos leer confiablemente si existe DataModelSchema (JSON).
        El DataModel binario es un formato propietario muy difícil de parsear.
        Para análisis completo del modelo, recomendamos usar formato PBIP.
        """
        try:
            # Intentar leer DataModelSchema primero (formato JSON) - ES CONFIABLE
            model_data = self._read_datamodel_schema(zip_ref)

            if model_data:
                print("[OK] DataModelSchema encontrado - analisis completo del modelo disponible")
                self._extract_model_metrics(model_data)
            else:
                # No hay DataModelSchema - NO intentar parsear binario, no es confiable
                print("[WARN] DataModelSchema no encontrado")
                print("   El archivo DataModel es binario y no se puede parsear confiablemente")
                print("   Para analisis completo del modelo, por favor convierte a formato PBIP:")
                print("   File -> Save As -> Power BI Project (.pbip)")

                # Inicializar métricas del modelo como N/A
                self._initialize_unavailable_model_metrics()

        except Exception as e:
            print(f"[WARN] Error analizando DataModel - {str(e)}")
            print("   Las metricas del modelo no estan disponibles para este archivo")
            print("   Para analisis completo, convierte a formato PBIP")
            self._initialize_unavailable_model_metrics()

    def _initialize_unavailable_model_metrics(self):
        """Inicializa métricas del modelo como no disponibles"""
        self.metrics['total_tables'] = None  # None indica "no disponible"
        self.metrics['total_relationships'] = None
        self.metrics['total_measures'] = None
        self.metrics['complex_dax_measures'] = None
        self.metrics['bidirectional_relationships'] = None
        self.metrics['calculated_columns'] = None
        self.metrics['calculated_tables'] = None
        self.metrics['calculated_columns_detail'] = []
        self.metrics['auto_date_time_enabled'] = 'No disponible'
        self.metrics['model_size_mb'] = None
        self.metrics['measures_by_table'] = {}
        self.metrics['columns_by_table'] = {}
        self.metrics['bidirectional_relationships_list'] = []
        self.metrics['model_analysis_available'] = False
        self.metrics['model_analysis_note'] = (
            "El análisis del modelo de datos no está disponible para este archivo PBIX. "
            "Para obtener métricas completas del modelo (tablas, medidas DAX, relaciones, etc.), "
            "por favor convierte tu reporte a formato PBIP: File → Save As → Power BI Project (.pbip)"
        )

    def _read_datamodel_schema(self, zip_ref: zipfile.ZipFile) -> Dict:
        """Lee el DataModelSchema (JSON) si existe"""
        try:
            schema_data = zip_ref.read('DataModelSchema').decode('utf-8')
            return json.loads(schema_data)
        except:
            return None

    def _read_datamodel_binary(self, zip_ref: zipfile.ZipFile) -> Dict:
        """Lee el DataModel binario y extrae lo que pueda"""
        try:
            # Intentar leer como UTF-16
            datamodel_data = zip_ref.read('DataModel').decode('utf-16-le', errors='ignore')

            # Buscar secciones JSON dentro del archivo binario
            # A veces el modelo contiene estructuras JSON embebidas
            json_pattern = r'\{[^{}]*"model"[^{}]*\}'
            json_matches = re.findall(json_pattern, datamodel_data, re.DOTALL)

            if json_matches:
                for match in json_matches:
                    try:
                        return json.loads(match)
                    except:
                        continue

            # Si no hay JSON, crear estructura básica con regex
            return {
                'model': {
                    'tables': self._extract_tables_regex(datamodel_data),
                    'relationships': self._extract_relationships_regex(datamodel_data)
                }
            }
        except Exception as e:
            print(f"Error leyendo DataModel binario: {str(e)}")
            return None

    def _extract_tables_regex(self, datamodel_data: str) -> List[Dict]:
        """Extrae información de tablas usando regex"""
        tables = []

        # Buscar nombres de tablas
        table_pattern = r'"Table"[^"]*"([^"]+)"'
        table_names = re.findall(table_pattern, datamodel_data)

        for table_name in set(table_names):
            # Buscar medidas para esta tabla
            measure_pattern = f'"{table_name}"[^"]*"Measure"[^"]*"Expression"[^"]*"([^"]+)"'
            measures = re.findall(measure_pattern, datamodel_data, re.DOTALL)

            tables.append({
                'name': table_name,
                'measures': [{'name': f'Measure_{i}', 'expression': m[:100]} for i, m in enumerate(measures)]
            })

        return tables

    def _extract_relationships_regex(self, datamodel_data: str) -> List[Dict]:
        """Extrae información de relaciones usando regex"""
        relationships = []

        # Patrón mejorado que captura más variaciones de formato
        # Busca bloques que contengan información de relaciones
        rel_patterns = [
            # Patrón 1: Formato JSON estándar
            r'"fromTable"\s*:\s*"([^"]+)"[^}]*"fromColumn"\s*:\s*"([^"]+)"[^}]*"toTable"\s*:\s*"([^"]+)"[^}]*"toColumn"\s*:\s*"([^"]+)"',
            # Patrón 2: Sin espacios
            r'"fromTable":"([^"]+)"[^}]*"fromColumn":"([^"]+)"[^}]*"toTable":"([^"]+)"[^}]*"toColumn":"([^"]+)"',
            # Patrón 3: Formato compacto
            r'fromTable["\s:]+([^"]+)["\s,]+fromColumn["\s:]+([^"]+)["\s,]+toTable["\s:]+([^"]+)["\s,]+toColumn["\s:]+([^"]+)'
        ]

        found_relationships = set()  # Para evitar duplicados

        for pattern in rel_patterns:
            rels = re.finditer(pattern, datamodel_data, re.IGNORECASE | re.DOTALL)
            for match in rels:
                from_table, from_col, to_table, to_col = match.groups()
                # Limpiar y crear identificador único
                rel_id = f"{from_table.strip()}.{from_col.strip()}-{to_table.strip()}.{to_col.strip()}"

                if rel_id not in found_relationships:
                    found_relationships.add(rel_id)

                    # Buscar crossFilteringBehavior en contexto cercano (500 chars antes y después)
                    start_pos = max(0, match.start() - 500)
                    end_pos = min(len(datamodel_data), match.end() + 500)
                    context = datamodel_data[start_pos:end_pos]

                    # Buscar crossFilteringBehavior en el contexto
                    cross_filter_pattern = r'"crossFilteringBehavior"\s*:\s*"([^"]+)"'
                    cross_filter_match = re.search(cross_filter_pattern, context, re.IGNORECASE)
                    cross_filter = cross_filter_match.group(1) if cross_filter_match else 'oneDirection'

                    relationships.append({
                        'fromTable': from_table.strip(),
                        'fromColumn': from_col.strip(),
                        'toTable': to_table.strip(),
                        'toColumn': to_col.strip(),
                        'crossFilteringBehavior': cross_filter
                    })

        print(f"DEBUG: Encontradas {len(relationships)} relaciones usando regex")
        return relationships

    def _extract_model_metrics(self, model_data: Dict):
        """Extrae métricas del modelo de datos"""
        model = model_data.get('model', {})

        # Tablas
        tables = model.get('tables', [])
        self.metrics['total_tables'] = len(tables)
        print(f"DEBUG: Encontradas {len(tables)} tablas")

        # Medidas DAX
        all_measures = []
        measures_by_table = {}
        calculated_columns = 0
        calculated_columns_detail = []  # Lista detallada
        calculated_tables = 0
        columns_by_table = {}

        for table in tables:
            table_name = table.get('name', 'Unknown')

            # Contar columnas
            columns = table.get('columns', [])
            columns_by_table[table_name] = len(columns)

            # Contar medidas
            measures = table.get('measures', [])
            for measure in measures:
                measure_info = {
                    'name': measure.get('name', 'Unknown'),
                    'table': table_name,
                    'expression': measure.get('expression', '')
                }
                all_measures.append(measure_info)

            if measures:
                measures_by_table[table_name] = [m.get('name', '') for m in measures]

            # Contar columnas calculadas CON DETALLE
            for col in columns:
                if 'expression' in col or col.get('type') == 'calculated':
                    calculated_columns += 1
                    # Estimar tamaño (aproximación simple)
                    expr = col.get('expression', '')
                    size_est = len(str(expr)) * 0.001  # KB aproximado
                    calculated_columns_detail.append({
                        'name': col.get('name', 'Unknown'),
                        'table': table_name,
                        'size_kb': size_est,
                        'expression_length': len(str(expr))
                    })

            # Contar tablas calculadas
            if 'partitions' in table:
                for partition in table['partitions']:
                    source_type = partition.get('source', {}).get('type', '')
                    if source_type == 'calculated' or 'expression' in partition.get('source', {}):
                        calculated_tables += 1
                        break

        self.metrics['total_measures'] = len(all_measures)
        self.metrics['measures_by_table'] = measures_by_table
        self.metrics['calculated_columns'] = calculated_columns
        self.metrics['calculated_columns_detail'] = calculated_columns_detail  # NUEVO
        self.metrics['calculated_tables'] = calculated_tables
        self.metrics['columns_by_table'] = columns_by_table

        print(f"DEBUG: Encontradas {len(all_measures)} medidas DAX")
        print(f"DEBUG: Encontradas {calculated_columns} columnas calculadas")
        print(f"DEBUG: Encontradas {calculated_tables} tablas calculadas")

        # Analizar complejidad de medidas DAX
        complex_measures = 0
        complex_functions = ['CALCULATE', 'FILTER', 'SUMX', 'AVERAGEX', 'COUNTX', 'MAXX', 'MINX']

        for measure in all_measures:
            expression = measure.get('expression', '')
            if isinstance(expression, list):
                expression = ' '.join(expression)

            # Contar funciones complejas
            complexity_score = sum(expression.upper().count(func) for func in complex_functions)
            if complexity_score >= 2 or len(expression) > 200:
                complex_measures += 1

        self.metrics['complex_dax_measures'] = complex_measures

        # Relaciones
        relationships = model.get('relationships', [])
        self.metrics['total_relationships'] = len(relationships)
        print(f"DEBUG: Encontradas {len(relationships)} relaciones")

        # Relaciones bidireccionales
        bidirectional = []
        for rel in relationships:
            cross_filter = rel.get('crossFilteringBehavior', 'oneDirection')
            if cross_filter == 'bothDirections':
                bidirectional.append({
                    'from': f"{rel.get('fromTable', 'Unknown')}.{rel.get('fromColumn', 'Unknown')}",
                    'to': f"{rel.get('toTable', 'Unknown')}.{rel.get('toColumn', 'Unknown')}"
                })

        self.metrics['bidirectional_relationships'] = len(bidirectional)
        self.metrics['bidirectional_relationships_list'] = bidirectional
        print(f"DEBUG: Encontradas {len(bidirectional)} relaciones bidireccionales")

        # Auto date/time
        default_mode = model.get('defaultMode', '')
        auto_datetime = model.get('defaultMode') == 'autoDateTime' or model.get('autoDateTime', False)
        self.metrics['auto_date_time_enabled'] = 'Sí' if auto_datetime else 'No'

        # Tamaño del modelo (estimado)
        # Nota: El tamaño real no está en el JSON, habría que calcular del binario
        self.metrics['model_size_mb'] = 0  # Se calculará en otra función

    def _analyze_custom_visuals(self, zip_ref: zipfile.ZipFile):
        """Analiza custom visuals instalados"""
        try:
            custom_visuals = []
            for file_info in zip_ref.filelist:
                if file_info.filename.startswith('Report/CustomVisuals/'):
                    custom_visuals.append(file_info.filename)

            self.metrics['custom_visuals_count'] = len(custom_visuals)
            self.metrics['custom_visuals_list'] = custom_visuals

        except:
            self.metrics['custom_visuals_count'] = 0
            self.metrics['custom_visuals_list'] = []

    def _analyze_embedded_resources(self, zip_ref: zipfile.ZipFile):
        """Analiza recursos embebidos (imágenes, etc)"""
        try:
            total_size = 0
            image_files = []

            for file_info in zip_ref.filelist:
                # Buscar imágenes en Report/StaticResources
                if file_info.filename.startswith('Report/StaticResources/'):
                    total_size += file_info.file_size
                    image_files.append({
                        'name': os.path.basename(file_info.filename),
                        'size_kb': file_info.file_size / 1024
                    })

            self.metrics['embedded_images_count'] = len(image_files)
            self.metrics['embedded_images_mb'] = total_size / (1024 * 1024)
            self.metrics['embedded_images_list'] = image_files

        except:
            self.metrics['embedded_images_count'] = 0
            self.metrics['embedded_images_mb'] = 0
            self.metrics['embedded_images_list'] = []

    def _calculate_model_size(self, zip_ref: zipfile.ZipFile):
        """Calcula el tamaño del modelo de datos"""
        try:
            total_size = 0

            # Buscar todos los archivos relacionados con el modelo
            model_files = ['DataModel', 'DataModelSchema']

            for file_info in zip_ref.filelist:
                if any(model_file in file_info.filename for model_file in model_files):
                    total_size += file_info.file_size

            if total_size > 0:
                self.metrics['model_size_mb'] = total_size / (1024 * 1024)
            else:
                # Si no se encontraron archivos del modelo, marcar como no disponible
                self.metrics['model_size_mb'] = None

        except:
            self.metrics['model_size_mb'] = None

    def _evaluate_metric(self, metric_key: str, value: float) -> Tuple[str, int]:
        """
        Evalúa una métrica contra los umbrales configurados

        Returns:
            Tupla (status, score) donde status es 'good', 'warning' o 'critical'
            y score es de 0-100
        """
        if metric_key not in self.config.get('thresholds', {}):
            return 'unknown', 50

        thresholds = self.config['thresholds'][metric_key]

        if value <= thresholds['good']:
            return 'good', 100
        elif value <= thresholds['warning']:
            return 'warning', 70
        else:
            return 'critical', 30

    def _calculate_score(self):
        """Calcula el score general del reporte (0-100)"""
        weights = self.config.get('weights', {})
        total_score = 0
        total_weight = 0

        metric_scores = {}

        # Mapeo de métricas a claves de configuración
        metric_mapping = {
            'max_visuals_per_page': 'visualizations_per_page',
            'max_filters_per_page': 'filters_per_page',
            'custom_visuals_count': 'custom_visuals',
            'embedded_images_mb': 'embedded_images_mb',
            'total_pages': 'total_pages',
            'complex_dax_measures': 'dax_measures_complex',
            'total_tables': 'tables_in_model',
            'total_relationships': 'relationships',
            'bidirectional_relationships': 'bidirectional_relationships',
            'calculated_columns': 'calculated_columns',
            'model_size_mb': 'model_size_mb',
        }

        for metric_key, config_key in metric_mapping.items():
            if metric_key in self.metrics and config_key in weights:
                value = self.metrics[metric_key]

                # Ignorar métricas no disponibles (None)
                if value is None:
                    continue

                status, score = self._evaluate_metric(config_key, value)

                metric_scores[config_key] = {
                    'value': value,
                    'status': status,
                    'score': score
                }

                weight = weights[config_key]
                total_score += score * weight
                total_weight += weight

        self.metrics['metric_scores'] = metric_scores
        self.metrics['overall_score'] = round(total_score / total_weight if total_weight > 0 else 0, 2)

        # Determinar categoría
        score = self.metrics['overall_score']
        if score >= self.config.get('scoring', {}).get('excellent', 90):
            self.metrics['score_category'] = 'excellent'
        elif score >= self.config.get('scoring', {}).get('good', 75):
            self.metrics['score_category'] = 'good'
        elif score >= self.config.get('scoring', {}).get('warning', 60):
            self.metrics['score_category'] = 'warning'
        else:
            self.metrics['score_category'] = 'poor'

    def _generate_recommendations(self):
        """Genera recomendaciones basadas en los hallazgos"""
        thresholds = self.config.get('thresholds', {})

        # Revisar cada métrica y generar recomendaciones
        for config_key, metric_data in self.metrics.get('metric_scores', {}).items():
            if metric_data['status'] in ['warning', 'critical']:
                threshold_config = thresholds.get(config_key, {})

                # Formatear el valor según el tipo de métrica
                current_val = metric_data['value']
                if config_key == 'embedded_images_mb':
                    current_val = f'{current_val:.2f} MB'
                elif isinstance(current_val, float):
                    # Redondear otros valores flotantes a 2 decimales
                    current_val = round(current_val, 2)

                self.recommendations.append({
                    'metric': config_key,
                    'severity': metric_data['status'],
                    'message': threshold_config.get('recommendation', 'Revisar esta métrica'),
                    'current_value': current_val,
                    'target_value': threshold_config.get('good', 'N/A')
                })

        # Recomendaciones adicionales específicas

        # Relaciones bidireccionales
        if (self.metrics.get('bidirectional_relationships') or 0) > 0:
            self.recommendations.append({
                'metric': 'bidirectional_relationships',
                'severity': 'warning',
                'message': 'Se encontraron relaciones bidireccionales que pueden causar ambigüedad y afectar el rendimiento. '
                          'Considera usar CROSSFILTER() en medidas específicas en lugar de relaciones bidireccionales.',
                'current_value': self.metrics['bidirectional_relationships'],
                'target_value': 0
            })

        # Auto date/time activado
        if self.metrics.get('auto_date_time_enabled') == 'Sí':
            self.recommendations.append({
                'metric': 'auto_date_time',
                'severity': 'warning',
                'message': 'Auto date/time está activado. Esto crea tablas ocultas para cada columna de fecha, '
                          'aumentando el tamaño del modelo. Considera usar una tabla de calendario personalizada.',
                'current_value': 'Activado',
                'target_value': 'Desactivado'
            })

        # Measure Killer - Modelo pesado (mejorado con columnas calculadas y debug)
        total_measures = self.metrics.get('total_measures') or 0
        model_size = self.metrics.get('model_size_mb') or 0
        calc_columns = self.metrics.get('calculated_columns') or 0

        print(f"DEBUG Measure Killer: measures={total_measures}, size={model_size}MB, calc_cols={calc_columns}")

        # Solo generar recomendaciones si las métricas del modelo están disponibles
        if self.metrics.get('model_analysis_available', True):
            # Condición mejorada: considera medidas, tamaño Y columnas calculadas
            # Crítico si: >100 medidas O >500MB O >20 columnas calculadas O combinación moderada
            is_critical = (
                total_measures > 100 or
                model_size > 500 or
                calc_columns > 20 or
                (total_measures > 50 and model_size > 250) or
                (total_measures > 50 and calc_columns > 10)
            )

            if is_critical:
                print(f"DEBUG: Generando recomendación CRÍTICA de Measure Killer")
                self.recommendations.append({
                'metric': 'model_optimization',
                'severity': 'critical',
                'message': (
                    f'El modelo tiene métricas que indican sobrecarga:\n\n'
                    f'• **Medidas DAX**: {total_measures} (objetivo: <50)\n'
                    f'• **Tamaño del modelo**: {model_size:.0f} MB (objetivo: <250 MB)\n'
                    f'• **Columnas calculadas**: {calc_columns} (objetivo: <10)\n\n'
                    f'**Recomendación**: Usa [Measure Killer](https://www.sqlbi.com/tools/measure-killer/) '
                    f'para identificar y eliminar medidas no utilizadas, reduciendo el tamaño del modelo.'
                ),
                'current_value': f'Medidas: {total_measures} | Tamaño: {model_size:.0f}MB | Cols Calc: {calc_columns}',
                'target_value': 'Medidas: <50 | Tamaño: <250MB | Cols Calc: <10'
                })
            elif total_measures > 30 or model_size > 100 or calc_columns > 5:
                print(f"DEBUG: Generando recomendación INFO de Measure Killer")
                self.recommendations.append({
                'metric': 'measure_count',
                'severity': 'info',
                'message': (
                    f'El modelo podría optimizarse:\n\n'
                    f'• **Medidas DAX**: {total_measures} (objetivo: <30)\n'
                    f'• **Columnas calculadas**: {calc_columns} (objetivo: <5)\n'
                    f'• **Tamaño del modelo**: {model_size:.0f} MB\n\n'
                    f'**Recomendación**: Revisa y elimina medidas no utilizadas usando '
                    f'[Measure Killer](https://www.sqlbi.com/tools/measure-killer/) para mantener el modelo limpio.'
                ),
                'current_value': f'Medidas: {total_measures} | Cols Calc: {calc_columns}',
                'target_value': 'Medidas: <30 | Cols Calc: <5'
                })
            else:
                print(f"DEBUG: No se generó recomendación de Measure Killer (valores dentro de umbrales)")

            # Columnas calculadas (advertencia adicional específica)
            # calc_columns ya está definido arriba
            if calc_columns > 10 and calc_columns <= 20:
                self.recommendations.append({
                'metric': 'calculated_columns',
                'severity': 'warning',
                'message': f'Se encontraron {calc_columns} columnas calculadas. Las columnas calculadas aumentan '
                'el tamaño del modelo. Considera mover el cálculo a Power Query o usar medidas cuando sea posible.',
                'current_value': calc_columns,
                    'target_value': '<10'
                })

        # ===== RECOMENDACIONES DE DISEÑO (NUEVO - v1.1) =====
        # Estas recomendaciones están basadas en métricas que SÍ están disponibles en PBIX

        # Slicers excesivos
        slicers_count = self.metrics.get('slicers_count', 0)
        if slicers_count > 15:
            self.recommendations.append({
                'metric': 'slicers_count',
                'severity': 'warning',
                'message': f'Se encontraron {slicers_count} slicers en el reporte. Demasiados slicers pueden '
                          'confundir a los usuarios y afectar la usabilidad. Considera usar sync slicers entre '
                          'páginas o agrupar filtros relacionados.',
                'current_value': slicers_count,
                'target_value': '< 15'
            })
        elif slicers_count > 25:
            self.recommendations.append({
                'metric': 'slicers_count',
                'severity': 'critical',
                'message': f'Se encontraron {slicers_count} slicers en el reporte. Esto es excesivo y degradará '
                          'significativamente la experiencia del usuario. Revisa y consolida los slicers.',
                'current_value': slicers_count,
                'target_value': '< 15'
            })

        # Imágenes embebidas pesadas
        embedded_images_mb = self.metrics.get('embedded_images_mb', 0)
        if embedded_images_mb > 5:
            self.recommendations.append({
                'metric': 'embedded_images',
                'severity': 'warning',
                'message': f'Las imágenes embebidas ocupan {embedded_images_mb:.2f}MB. Las imágenes pesadas aumentan '
                          'el tamaño del archivo y el tiempo de carga. Considera optimizar las imágenes antes de '
                          'embedarlas o usar referencias externas.',
                'current_value': f'{embedded_images_mb:.2f} MB',
                'target_value': '< 5 MB'
            })

        # Falta de bookmarks (oportunidad de mejora)
        bookmarks_count = self.metrics.get('bookmarks_count', 0)
        buttons_count = self.metrics.get('buttons_count', 0)
        total_pages = self.metrics.get('total_pages', 0)

        if total_pages > 5 and bookmarks_count == 0 and buttons_count == 0:
            self.recommendations.append({
                'metric': 'navigation',
                'severity': 'info',
                'message': f'El reporte tiene {total_pages} páginas pero no usa bookmarks ni botones de navegación. '
                          'Considera añadir bookmarks y botones para mejorar la navegación y crear storytelling '
                          'interactivo.',
                'current_value': f'{bookmarks_count} bookmarks, {buttons_count} botones',
                'target_value': 'Usar bookmarks y botones'
            })

        # Páginas con demasiados visuales
        max_visuals = self.metrics.get('max_visuals_per_page', 0)
        if max_visuals > 20:
            # Buscar el nombre de la página con más visuales
            page_name = 'Desconocida'
            pages_detail = self.metrics.get('pages_detail', [])
            if pages_detail:
                max_page = max(pages_detail, key=lambda p: p.get('visuals_count', 0), default=None)
                if max_page:
                    page_name = max_page.get('name', 'Desconocida')

            self.recommendations.append({
                'metric': 'visuals_per_page',
                'severity': 'critical',
                'message': (
                    f'La página **"{page_name}"** tiene **{max_visuals} elementos visuales** '
                    f'(incluye gráficos, slicers, shapes, textboxes, imágenes, etc.).\n\n'
                    f'**Impacto**: Esto afectará significativamente el rendimiento y la experiencia del usuario. '
                    f'Power BI debe renderizar todos estos elementos al cargar la página.\n\n'
                    f'**Soluciones recomendadas**:\n'
                    f'• Divide la página en múltiples páginas temáticas\n'
                    f'• Usa drill-through para detalles adicionales\n'
                    f'• Usa tooltips personalizados en vez de visuales adicionales\n'
                    f'• Elimina shapes y decoraciones innecesarias'
                ),
                'current_value': f'{max_visuals} elementos (página: {page_name})',
                'target_value': '< 15 elementos por página'
            })

        # Filtros excesivos por página
        max_filters = self.metrics.get('max_filters_per_page', 0)
        if max_filters > 12:
            # Buscar el nombre de la página con más filtros
            page_name = 'Desconocida'
            pages_detail = self.metrics.get('pages_detail', [])
            if pages_detail:
                max_page = max(pages_detail, key=lambda p: p.get('filters_count', 0), default=None)
                if max_page:
                    page_name = max_page.get('name', 'Desconocida')

            # Calcular promedio también para dar contexto
            avg_filters = self.metrics.get('avg_filters_per_page', 0)

            self.recommendations.append({
                'metric': 'filters_per_page',
                'severity': 'warning',
                'message': (
                    f'La página **"{page_name}"** tiene **{max_filters} filtros** (el máximo en todo el reporte). '
                    f'El promedio de filtros por página es {avg_filters:.1f}.\n\n'
                    f'**Impacto**: Demasiados filtros pueden:\n'
                    f'• Ralentizar la carga y actualización del reporte\n'
                    f'• Confundir a los usuarios con opciones excesivas\n'
                    f'• Ocupar mucho espacio visual\n\n'
                    f'**Soluciones recomendadas**:\n'
                    f'• Consolida filtros relacionados en jerarquías\n'
                    f'• Usa filtros a nivel de reporte cuando apliquen a todas las páginas\n'
                    f'• Considera usar drill-through para análisis detallados\n'
                    f'• Evalúa si todos los filtros son realmente necesarios'
                ),
                'current_value': f'{max_filters} filtros (página: {page_name})',
                'target_value': '≤ 5 filtros por página'
            })

        # Sin tema personalizado (oportunidad)
        has_custom_theme = self.metrics.get('has_custom_theme', False)
        if not has_custom_theme and total_pages > 1:
            self.recommendations.append({
                'metric': 'theme',
                'severity': 'info',
                'message': 'El reporte usa el tema predeterminado. Considera crear un tema personalizado que '
                          'refleje los colores corporativos y mejore la consistencia visual del reporte.',
                'current_value': 'Tema predeterminado',
                'target_value': 'Tema personalizado'
            })

    def _build_result(self) -> Dict[str, Any]:
        """Construye el resultado final del análisis"""
        return {
            'report_name': self.report_name,
            'report_path': self.pbix_path,
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'score': self.metrics.get('overall_score', 0),
            'score_category': self.metrics.get('score_category', 'unknown')
        }


def analyze_pbix_file(pbix_path: str, config_path: str = None) -> Dict[str, Any]:
    """
    Función helper para analizar un archivo .pbix

    Args:
        pbix_path: Ruta al archivo .pbix
        config_path: Ruta al archivo de configuración (opcional)

    Returns:
        Diccionario con resultados del análisis
    """
    analyzer = PBIXAnalyzer(pbix_path, config_path)
    return analyzer.analyze()
