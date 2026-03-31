"""
Analizador de proyectos Power BI (.pbip)
Extrae metadata y métricas de proyectos .pbip para análisis de mejores prácticas
"""

import os
import json
from typing import Dict, List, Any
from pathlib import Path
import yaml


class PBIPAnalyzer:
    """Clase para analizar proyectos Power BI (.pbip)"""

    def __init__(self, pbip_path: str, config_path: str = None):
        """
        Inicializa el analizador

        Args:
            pbip_path: Ruta a la carpeta del proyecto .pbip O archivo .pbip
            config_path: Ruta al archivo de configuración (opcional)
        """
        # Auto-detectar carpetas .Report y .SemanticModel
        self.report_path, self.semantic_model_path = self._resolve_pbip_path(pbip_path)

        # Determinar el nombre del reporte
        if self.report_path:
            self.report_name = os.path.basename(self.report_path)
        elif self.semantic_model_path:
            self.report_name = os.path.basename(self.semantic_model_path)
        else:
            self.report_name = os.path.basename(pbip_path)

        self.config = self._load_config(config_path)
        self.metrics = {}
        self.warnings = []
        self.recommendations = []

    def _resolve_pbip_path(self, pbip_path: str) -> tuple:
        """
        Resuelve las rutas correctas del proyecto PBIP

        Returns:
            Tupla (report_path, semantic_model_path)
        """
        pbip_path = pbip_path.strip().strip('"').strip("'")

        # Si es un archivo .pbip, buscar las carpetas .Report y .SemanticModel
        if os.path.isfile(pbip_path) and pbip_path.endswith('.pbip'):
            base_dir = os.path.dirname(pbip_path)
            pbip_name = os.path.basename(pbip_path).replace('.pbip', '')

            # Buscar carpeta .Report
            report_folder = os.path.join(base_dir, f"{pbip_name}.Report")
            # Buscar carpeta .SemanticModel
            semantic_folder = os.path.join(base_dir, f"{pbip_name}.SemanticModel")
            # También buscar .Dataset (nombre antiguo)
            dataset_folder = os.path.join(base_dir, f"{pbip_name}.Dataset")

            # Determinar qué carpetas existen
            report_path = report_folder if os.path.exists(report_folder) else None
            semantic_path = None

            if os.path.exists(semantic_folder):
                semantic_path = semantic_folder
            elif os.path.exists(dataset_folder):
                semantic_path = dataset_folder

            if report_path or semantic_path:
                print(f"✅ Auto-detectadas carpetas del proyecto:")
                if report_path:
                    print(f"   📄 Report: {report_path}")
                if semantic_path:
                    print(f"   📊 Modelo: {semantic_path}")
                return (report_path, semantic_path)

            raise FileNotFoundError(
                f"No se encontraron las carpetas del proyecto PBIP.\n"
                f"Archivo: {pbip_path}\n"
                f"Buscadas: {report_folder}, {semantic_folder}\n"
                f"Verifica que el archivo .pbip esté en la misma carpeta que las carpetas del proyecto"
            )

        # Si es una carpeta, determinar si es .Report, .SemanticModel, o la carpeta base
        if os.path.isdir(pbip_path):
            # Caso 1: Es una carpeta .Report o .SemanticModel directamente
            if pbip_path.endswith('.Report'):
                # Buscar .SemanticModel hermana
                base_name = os.path.basename(pbip_path).replace('.Report', '')
                parent_dir = os.path.dirname(pbip_path)
                semantic_path = os.path.join(parent_dir, f"{base_name}.SemanticModel")
                if not os.path.exists(semantic_path):
                    semantic_path = os.path.join(parent_dir, f"{base_name}.Dataset")
                semantic_path = semantic_path if os.path.exists(semantic_path) else None

                print(f"📄 Carpeta .Report proporcionada: {pbip_path}")
                if semantic_path:
                    print(f"📊 Carpeta .SemanticModel encontrada: {semantic_path}")

                return (pbip_path, semantic_path)

            elif pbip_path.endswith('.SemanticModel') or pbip_path.endswith('.Dataset'):
                # Buscar .Report hermana
                base_name = os.path.basename(pbip_path).replace('.SemanticModel', '').replace('.Dataset', '')
                parent_dir = os.path.dirname(pbip_path)
                report_path = os.path.join(parent_dir, f"{base_name}.Report")
                report_path = report_path if os.path.exists(report_path) else None

                print(f"📊 Carpeta .SemanticModel proporcionada: {pbip_path}")
                if report_path:
                    print(f"📄 Carpeta .Report encontrada: {report_path}")

                return (report_path, pbip_path)

            # Caso 2: Es una carpeta genérica, buscar subcarpetas
            else:
                # Buscar .Report y .SemanticModel dentro
                report_path = None
                semantic_path = None

                for item in os.listdir(pbip_path):
                    item_path = os.path.join(pbip_path, item)
                    if os.path.isdir(item_path):
                        if item.endswith('.Report'):
                            report_path = item_path
                        elif item.endswith('.SemanticModel') or item.endswith('.Dataset'):
                            semantic_path = item_path

                if report_path or semantic_path:
                    print(f"✅ Carpetas encontradas en: {pbip_path}")
                    if report_path:
                        print(f"   📄 Report: {report_path}")
                    if semantic_path:
                        print(f"   📊 Modelo: {semantic_path}")
                    return (report_path, semantic_path)

                return (pbip_path, None)  # Asumir que es la carpeta del proyecto

        raise FileNotFoundError(f"La ruta no es válida: {pbip_path}")

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
        """Retorna configuración por defecto"""
        return {
            'thresholds': {},
            'weights': {}
        }

    def analyze(self) -> Dict[str, Any]:
        """
        Ejecuta el análisis completo del proyecto .pbip

        Returns:
            Diccionario con todas las métricas y resultados
        """
        print(f"Analizando proyecto PBIP: {self.report_name}")

        try:
            # Analizar el dataset/modelo (desde .SemanticModel)
            self._analyze_dataset()

            # Analizar el reporte (layout, visualizaciones) (desde .Report)
            self._analyze_report()

            # Calcular score general
            self._calculate_score()

            # Generar recomendaciones
            self._generate_recommendations()

            return self._build_result()

        except Exception as e:
            raise Exception(f"Error analizando el proyecto PBIP: {str(e)}")

    def _analyze_dataset(self):
        """Analiza el modelo de datos (BIM o TMDL)"""
        try:
            # Si no hay carpeta de modelo semántico, inicializar métricas vacías
            if not self.semantic_model_path:
                print("⚠️  No se encontró carpeta .SemanticModel - análisis del modelo no disponible")
                self._initialize_empty_metrics()
                return

            # Buscar carpeta definition
            definition_path = os.path.join(self.semantic_model_path, 'definition')
            if not os.path.exists(definition_path):
                definition_path = self.semantic_model_path

            # DETECTAR FORMATO: TMDL (nuevo) o BIM (antiguo)
            model_tmdl = os.path.join(definition_path, 'model.tmdl')

            if os.path.exists(model_tmdl):
                # FORMATO TMDL (nuevo, introducido en 2023)
                print("📖 Detectado formato TMDL - parseando archivos .tmdl")
                from .tmdl_parser import parse_tmdl_model
                model_data = parse_tmdl_model(self.semantic_model_path)
                self._extract_model_metrics(model_data)
            else:
                # FORMATO BIM (antiguo, JSON)
                print("📖 Detectado formato BIM - parseando archivo .bim")
                model_file = None
                for filename in ['dataset.bim', 'model.bim', 'Dataset.bim']:
                    potential_path = os.path.join(definition_path, filename)
                    if os.path.exists(potential_path):
                        model_file = potential_path
                        break

                if not model_file:
                    raise FileNotFoundError(
                        "No se encontró archivo del modelo.\n"
                        f"Carpeta revisada: {definition_path}\n"
                        "Formatos buscados: TMDL (model.tmdl) y BIM (dataset.bim, model.bim)"
                    )

                # Leer el modelo BIM (JSON)
                with open(model_file, 'r', encoding='utf-8-sig') as f:
                    model_data = json.load(f)

                # Extraer métricas del modelo
                self._extract_model_metrics(model_data)

        except Exception as e:
            print(f"⚠️  Error analizando dataset - {str(e)}")
            self._initialize_empty_metrics()

    def _extract_model_metrics(self, model_data: Dict):
        """Extrae métricas del modelo de datos"""
        model = model_data.get('model', {})

        # Tablas
        tables = model.get('tables', [])
        self.metrics['total_tables'] = len(tables)

        # Medidas DAX
        all_measures = []
        measures_by_table = {}
        calculated_columns = 0
        calculated_columns_detail = []
        calculated_tables = 0
        columns_by_table = {}

        print(f"DEBUG PBIP: Analizando {len(tables)} tablas")

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
                    source = partition.get('source', {})
                    if source.get('type') == 'calculated' or 'expression' in source:
                        calculated_tables += 1
                        break

        self.metrics['total_measures'] = len(all_measures)
        self.metrics['measures_by_table'] = measures_by_table
        self.metrics['calculated_columns'] = calculated_columns
        self.metrics['calculated_columns_detail'] = calculated_columns_detail
        self.metrics['calculated_tables'] = calculated_tables
        self.metrics['columns_by_table'] = columns_by_table

        print(f"DEBUG PBIP: {len(all_measures)} medidas, {calculated_columns} columnas calculadas")

        # Analizar complejidad de medidas DAX
        complex_measures = 0
        complex_functions = ['CALCULATE', 'FILTER', 'SUMX', 'AVERAGEX', 'COUNTX', 'MAXX', 'MINX',
                            'RANKX', 'TOPN', 'ADDCOLUMNS', 'SUMMARIZE', 'CROSSFILTER']

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
        print(f"DEBUG PBIP: Encontradas {len(relationships)} relaciones")

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
        print(f"DEBUG PBIP: Encontradas {len(bidirectional)} relaciones bidireccionales")

        # Auto date/time
        # En PBIP, esto puede estar en las opciones del modelo
        model_options = model.get('defaultPowerBIDataSourceVersion', '')
        auto_datetime = model.get('defaultMode') == 'import' and 'autoDateTime' in str(model_data)

        # Buscar configuración de auto date/time
        if 'autoDateTimeHierarchy' in str(model_data):
            auto_datetime = True

        self.metrics['auto_date_time_enabled'] = 'Sí' if auto_datetime else 'No'

        # Tamaño del modelo (estimado basado en cantidad de datos)
        # Esto es solo una estimación ya que el PBIP no contiene los datos
        estimated_size = len(tables) * 5  # Estimación muy aproximada
        self.metrics['model_size_mb'] = estimated_size
        self.metrics['model_size_note'] = 'Estimado (PBIP no contiene datos)'

    def _analyze_report(self):
        """Analiza el archivo report.json (visualizaciones, páginas)"""
        try:
            # Si no hay carpeta de reporte, inicializar métricas vacías
            if not self.report_path:
                print("⚠️  No se encontró carpeta .Report - análisis de visualizaciones no disponible")
                self._initialize_empty_report_metrics()
                return

            # Buscar carpeta definition
            definition_path = os.path.join(self.report_path, 'definition')
            if not os.path.exists(definition_path):
                definition_path = self.report_path

            # Buscar el archivo del reporte
            report_file = None
            for filename in ['report.json', 'Report.json']:
                potential_path = os.path.join(definition_path, filename)
                if os.path.exists(potential_path):
                    report_file = potential_path
                    break

            if not report_file:
                print("⚠️  No se encontró archivo report.json")
                self._initialize_empty_report_metrics()
                return

            # Leer el reporte
            with open(report_file, 'r', encoding='utf-8-sig') as f:
                report_data = json.load(f)

            # Extraer métricas del reporte
            self._extract_report_metrics(report_data)

        except Exception as e:
            print(f"⚠️  Error analizando reporte - {str(e)}")
            self._initialize_empty_report_metrics()

    def _extract_report_metrics(self, report_data: Dict):
        """Extrae métricas del reporte (páginas, visualizaciones, filtros)"""

        # DETECTAR FORMATO: Antiguo (sections) vs Nuevo (pages separadas)
        sections = report_data.get('sections', [])

        if sections:
            # FORMATO ANTIGUO (BIM): sections en report.json
            self._extract_report_metrics_old_format(report_data)
        else:
            # FORMATO NUEVO (TMDL): páginas en carpetas separadas
            self._extract_report_metrics_new_format()

    def _extract_report_metrics_old_format(self, report_data: Dict):
        """Extrae métricas del formato antiguo (sections en report.json)"""
        sections = report_data.get('sections', [])
        self.metrics['total_pages'] = len(sections)

        visuals_per_page = []
        filters_per_page = []
        total_visuals = 0
        visual_types = {}

        # Contadores específicos de diseño (NUEVO - como en PBIX)
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

        for section in sections:
            # Obtener nombre de página - MEJORADO para evitar puntos y nombres vacíos
            display_name = section.get('displayName', '')
            name = section.get('name', '')

            # Si displayName está vacío, es un punto, o es muy corto, usar name
            if not display_name or display_name.strip() in ['.', '..', ''] or len(display_name.strip()) < 2:
                page_name = name if name and name.strip() else 'Sin nombre'
            else:
                page_name = display_name

            # Si aún es un punto, usar un nombre descriptivo
            if page_name.strip() in ['.', '..', '.1', '.2', '.3']:
                page_name = f"Página {len(pages_detail) + 1}"

            page_info = {
                'name': page_name,
                'visuals_count': 0,
                'filters_count': 0,
                'hidden': False,
                'tooltip': False,
                'width': section.get('width', 0),
                'height': section.get('height', 0)
            }

            # Verificar si es página oculta
            if section.get('visibility', 0) == 1:
                hidden_pages += 1
                page_info['hidden'] = True

            # Verificar si es página de tooltip
            config = section.get('config', '{}')
            try:
                page_config = json.loads(config) if isinstance(config, str) else config
                if page_config.get('displayOption') == 3:  # 3 = Tooltip page
                    tooltip_pages += 1
                    page_info['tooltip'] = True
            except:
                pass

            # Contar visuales por página
            visuals = section.get('visualContainers', [])
            visuals_per_page.append(len(visuals))
            total_visuals += len(visuals)
            page_info['visuals_count'] = len(visuals)

            # Tipos de visuales - MEJORADO con categorías específicas
            for visual in visuals:
                config = visual.get('config', '')
                visual_type = 'unknown'

                try:
                    # Manejar config como string o como objeto
                    if isinstance(config, str):
                        config_json = json.loads(config) if config else {}
                    elif isinstance(config, dict):
                        config_json = config
                    else:
                        config_json = {}

                    # Intentar extraer visualType de diferentes ubicaciones
                    visual_type = (
                        config_json.get('singleVisual', {}).get('visualType') or
                        config_json.get('visualType') or
                        visual.get('type') or
                        'unknown'
                    )

                    visual_types[visual_type] = visual_types.get(visual_type, 0) + 1

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

                except Exception as e:
                    # Debug: mostrar muestra del config problemático
                    if visual_types.get('unknown', 0) < 3:  # Solo primeros 3 para no saturar
                        config_sample = str(config)[:200] if config else "vacío"
                        print(f"     [DEBUG] Visual sin tipo detectado. Config sample: {config_sample}")
                    visual_types['unknown'] = visual_types.get('unknown', 0) + 1

            # Contar filtros por página
            filters = section.get('filters', [])
            if isinstance(filters, str):
                try:
                    filters = json.loads(filters)
                except:
                    filters = []
            filters_count = len(filters) if isinstance(filters, list) else 0
            filters_per_page.append(filters_count)
            page_info['filters_count'] = filters_count

            pages_detail.append(page_info)

        self.metrics['total_visuals'] = total_visuals
        self.metrics['avg_visuals_per_page'] = sum(visuals_per_page) / len(sections) if sections else 0
        self.metrics['max_visuals_per_page'] = max(visuals_per_page) if visuals_per_page else 0
        self.metrics['visual_types'] = visual_types

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

        self.metrics['total_filters'] = sum(filters_per_page)
        self.metrics['avg_filters_per_page'] = sum(filters_per_page) / len(sections) if sections else 0
        self.metrics['max_filters_per_page'] = max(filters_per_page) if filters_per_page else 0

        # Filtros a nivel de reporte (NUEVO - v1.1)
        report_filters = report_data.get('filters', '[]')
        try:
            report_filters_json = json.loads(report_filters) if isinstance(report_filters, str) else report_filters
            self.metrics['report_level_filters'] = len(report_filters_json)
        except:
            self.metrics['report_level_filters'] = 0

        # Bookmarks (NUEVO - v1.1)
        bookmarks = report_data.get('bookmarks', [])
        self.metrics['bookmarks_count'] = len(bookmarks)
        self.metrics['bookmarks_detail'] = [{
            'name': bm.get('displayName', bm.get('name', 'Sin nombre')),
            'page': bm.get('explorationState', {}).get('activeSection', 'N/A')
        } for bm in bookmarks[:10]]  # Primeros 10 para no saturar

        # Theme/Tema (NUEVO - v1.1)
        theme = report_data.get('config', '{}')
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

        # Configuración del reporte (NUEVO - v1.1)
        self.metrics['report_config'] = {
            'default_page': report_data.get('activeSection', 'Página 1'),
            'layout_type': report_data.get('layoutType', 'Master'),
            'has_resource_packages': 'resourcePackages' in report_data
        }

        # Custom visuals (buscar en config)
        custom_visuals = set()
        for section in sections:
            for visual in section.get('visualContainers', []):
                config = visual.get('config', '')
                if 'customVisual' in str(config) or 'pbiviz' in str(config):
                    custom_visuals.add(visual.get('config', '')[:50])

        self.metrics['custom_visuals_count'] = len(custom_visuals)
        self.metrics['custom_visuals_list'] = list(custom_visuals)

        # Imágenes (en PBIP no están embebidas, son referencias)
        self.metrics['embedded_images_count'] = 0
        self.metrics['embedded_images_mb'] = 0
        self.metrics['embedded_images_list'] = []

        print(f"[OK] Formato antiguo: {len(sections)} páginas, {total_visuals} visuales")
        print(f"     Diseño: {slicers_count} slicers, {buttons_count} botones, {len(bookmarks)} bookmarks")
        print(f"     Tipos de visuales detectados: {list(visual_types.keys())[:10]}")
        if 'unknown' in visual_types and visual_types['unknown'] > 100:
            print(f"     ⚠️ ALERTA: {visual_types['unknown']} visuales con tipo 'unknown' - revisar formato de config")

    def _extract_report_metrics_new_format(self):
        """Extrae métricas del formato nuevo (páginas en carpetas separadas)"""
        definition_path = os.path.join(self.report_path, 'definition')
        pages_dir = os.path.join(definition_path, 'pages')

        if not os.path.exists(pages_dir):
            print("⚠️  No se encontró carpeta pages/")
            self._initialize_empty_report_metrics()
            return

        # Leer pages.json para obtener la lista de páginas
        pages_json_path = os.path.join(pages_dir, 'pages.json')
        if not os.path.exists(pages_json_path):
            print("⚠️  No se encontró pages.json")
            self._initialize_empty_report_metrics()
            return

        with open(pages_json_path, 'r', encoding='utf-8-sig') as f:
            pages_metadata = json.load(f)

        page_ids = pages_metadata.get('pageOrder', [])
        self.metrics['total_pages'] = len(page_ids)

        visuals_per_page = []
        filters_per_page = []
        total_visuals = 0
        visual_types = {}

        # Contadores específicos de diseño (NUEVO - como en PBIX)
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

        print(f"📄 Analizando {len(page_ids)} páginas...")

        for page_id in page_ids:
            page_dir = os.path.join(pages_dir, page_id)
            if not os.path.exists(page_dir):
                continue

            # Leer metadata de la página
            page_json_path = os.path.join(page_dir, 'page.json')
            page_name = page_id
            page_hidden = False
            page_tooltip = False
            filters_count = 0

            if os.path.exists(page_json_path):
                with open(page_json_path, 'r', encoding='utf-8-sig') as f:
                    page_data = json.load(f)

                page_name = page_data.get('displayName', page_data.get('name', page_id))

                # Verificar si es página oculta
                if page_data.get('visibility', 0) == 1:
                    hidden_pages += 1
                    page_hidden = True

                # Verificar si es página de tooltip
                display_option = page_data.get('displayOption', 0)
                if display_option == 3:  # 3 = Tooltip page
                    tooltip_pages += 1
                    page_tooltip = True

                # Contar filtros
                filters = page_data.get('filterConfig', {}).get('filters', [])
                filters_count = len(filters)
                filters_per_page.append(filters_count)

            page_info = {
                'name': page_name,
                'visuals_count': 0,
                'filters_count': filters_count,
                'hidden': page_hidden,
                'tooltip': page_tooltip,
                'width': 0,
                'height': 0
            }

            # Contar visuales (cada carpeta en visuals/ es un visual)
            visuals_dir = os.path.join(page_dir, 'visuals')
            if os.path.exists(visuals_dir):
                visual_folders = [f for f in os.listdir(visuals_dir) if os.path.isdir(os.path.join(visuals_dir, f))]
                num_visuals = len(visual_folders)
                visuals_per_page.append(num_visuals)
                total_visuals += num_visuals
                page_info['visuals_count'] = num_visuals

                # Analizar cada visual para obtener su tipo
                for visual_folder in visual_folders:
                    visual_json_path = os.path.join(visuals_dir, visual_folder, 'visual.json')
                    if os.path.exists(visual_json_path):
                        try:
                            with open(visual_json_path, 'r', encoding='utf-8-sig') as f:
                                visual_data = json.load(f)

                            # FORMATO TMDL: visualType está en visual_data['visual']['visualType']
                            visual_type = 'unknown'

                            # Opción 1: Dentro de 'visual' (formato TMDL nuevo)
                            if 'visual' in visual_data and isinstance(visual_data['visual'], dict):
                                visual_type = visual_data['visual'].get('visualType', 'unknown')

                            # Opción 2: Nivel raíz (formato antiguo)
                            if visual_type == 'unknown':
                                visual_type = visual_data.get('visualType', visual_data.get('type', 'unknown'))

                            # Opción 3: Buscar en config si existe
                            if visual_type == 'unknown' and 'config' in visual_data:
                                try:
                                    config = visual_data.get('config', '{}')
                                    if isinstance(config, str):
                                        config_json = json.loads(config)
                                    else:
                                        config_json = config

                                    visual_type = (
                                        config_json.get('singleVisual', {}).get('visualType') or
                                        config_json.get('visualType') or
                                        'unknown'
                                    )
                                except:
                                    pass

                            visual_types[visual_type] = visual_types.get(visual_type, 0) + 1

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
                        except Exception as e:
                            # Debug para ver qué está fallando
                            if visual_types.get('unknown', 0) < 3:
                                print(f"     [DEBUG] Error leyendo visual {visual_folder}: {str(e)}")
                            visual_types['unknown'] = visual_types.get('unknown', 0) + 1
            else:
                visuals_per_page.append(0)

            pages_detail.append(page_info)

        self.metrics['total_visuals'] = total_visuals
        self.metrics['avg_visuals_per_page'] = sum(visuals_per_page) / len(page_ids) if page_ids else 0
        self.metrics['max_visuals_per_page'] = max(visuals_per_page) if visuals_per_page else 0
        self.metrics['visual_types'] = visual_types

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

        self.metrics['total_filters'] = sum(filters_per_page) if filters_per_page else 0
        self.metrics['avg_filters_per_page'] = sum(filters_per_page) / len(page_ids) if page_ids and filters_per_page else 0
        self.metrics['max_filters_per_page'] = max(filters_per_page) if filters_per_page else 0

        # Filtros a nivel de reporte (NUEVO - v1.1)
        # En el formato nuevo, esto podría estar en un archivo separado
        self.metrics['report_level_filters'] = 0

        # Bookmarks (NUEVO - v1.1)
        # En formato TMDL, los bookmarks están en archivos individuales en la carpeta bookmarks/
        bookmarks_dir = os.path.join(definition_path, 'bookmarks')
        if os.path.exists(bookmarks_dir):
            try:
                # Contar archivos .bookmark.json
                bookmark_files = [f for f in os.listdir(bookmarks_dir) if f.endswith('.bookmark.json')]
                self.metrics['bookmarks_count'] = len(bookmark_files)

                # Leer detalles de primeros 10 bookmarks
                bookmarks_detail = []
                for bm_file in bookmark_files[:10]:
                    bm_path = os.path.join(bookmarks_dir, bm_file)
                    try:
                        with open(bm_path, 'r', encoding='utf-8-sig') as f:
                            bm_data = json.load(f)
                        bookmarks_detail.append({
                            'name': bm_data.get('displayName', bm_data.get('name', 'Sin nombre')),
                            'page': bm_data.get('explorationState', {}).get('activeSection', 'N/A')
                        })
                    except:
                        pass

                self.metrics['bookmarks_detail'] = bookmarks_detail
            except:
                self.metrics['bookmarks_count'] = 0
                self.metrics['bookmarks_detail'] = []
        else:
            self.metrics['bookmarks_count'] = 0
            self.metrics['bookmarks_detail'] = []

        # Theme/Tema (NUEVO - v1.1)
        theme_path = os.path.join(definition_path, 'theme.json')
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r', encoding='utf-8-sig') as f:
                    theme_data = json.load(f)
                self.metrics['has_custom_theme'] = True
                self.metrics['theme_name'] = theme_data.get('name', 'Tema personalizado')
            except:
                self.metrics['has_custom_theme'] = False
                self.metrics['theme_name'] = 'Desconocido'
        else:
            self.metrics['has_custom_theme'] = False
            self.metrics['theme_name'] = 'Tema predeterminado'

        # Configuración del reporte (NUEVO - v1.1)
        report_json_path = os.path.join(definition_path, 'report.json')
        default_page = 'N/A'
        if os.path.exists(report_json_path):
            try:
                with open(report_json_path, 'r', encoding='utf-8-sig') as f:
                    report_data = json.load(f)
                default_page = report_data.get('activeSection', 'Página 1')
            except:
                pass

        self.metrics['report_config'] = {
            'default_page': default_page,
            'layout_type': 'Master',
            'has_resource_packages': False
        }

        # Custom visuals
        custom_visuals_count = sum(1 for vtype in visual_types.keys() if 'custom' in vtype.lower() or 'pbiviz' in vtype.lower())
        self.metrics['custom_visuals_count'] = custom_visuals_count
        self.metrics['custom_visuals_list'] = [vtype for vtype in visual_types.keys() if 'custom' in vtype.lower() or 'pbiviz' in vtype.lower()]

        # Imágenes (en PBIP no están embebidas, son referencias)
        self.metrics['embedded_images_count'] = 0
        self.metrics['embedded_images_mb'] = 0
        self.metrics['embedded_images_list'] = []

        print(f"📊 Formato nuevo: {total_visuals} visuales en {len(page_ids)} páginas")
        print(f"     Diseño: {slicers_count} slicers, {buttons_count} botones, {self.metrics['bookmarks_count']} bookmarks")

    def _initialize_empty_metrics(self):
        """Inicializa métricas vacías para el modelo"""
        self.metrics['total_tables'] = 0
        self.metrics['total_relationships'] = 0
        self.metrics['total_measures'] = 0
        self.metrics['complex_dax_measures'] = 0
        self.metrics['bidirectional_relationships'] = 0
        self.metrics['calculated_columns'] = 0
        self.metrics['calculated_tables'] = 0
        self.metrics['auto_date_time_enabled'] = 'Desconocido'
        self.metrics['model_size_mb'] = 0
        self.metrics['measures_by_table'] = {}
        self.metrics['bidirectional_relationships_list'] = []

    def _initialize_empty_report_metrics(self):
        """Inicializa métricas vacías para el reporte"""
        self.metrics['total_pages'] = 0
        self.metrics['total_visuals'] = 0
        self.metrics['avg_visuals_per_page'] = 0
        self.metrics['max_visuals_per_page'] = 0
        self.metrics['visual_types'] = {}
        self.metrics['total_filters'] = 0
        self.metrics['avg_filters_per_page'] = 0
        self.metrics['max_filters_per_page'] = 0
        self.metrics['custom_visuals_count'] = 0
        self.metrics['custom_visuals_list'] = []
        self.metrics['embedded_images_count'] = 0
        self.metrics['embedded_images_mb'] = 0
        self.metrics['embedded_images_list'] = []

        # Métricas de diseño (NUEVO - v1.1)
        self.metrics['slicers_count'] = 0
        self.metrics['buttons_count'] = 0
        self.metrics['shapes_count'] = 0
        self.metrics['textboxes_count'] = 0
        self.metrics['images_in_visuals_count'] = 0
        self.metrics['tables_count'] = 0
        self.metrics['hidden_pages_count'] = 0
        self.metrics['tooltip_pages_count'] = 0
        self.metrics['pages_detail'] = []
        self.metrics['report_level_filters'] = 0
        self.metrics['bookmarks_count'] = 0
        self.metrics['bookmarks_detail'] = []
        self.metrics['has_custom_theme'] = False
        self.metrics['theme_name'] = 'Desconocido'
        self.metrics['report_config'] = {
            'default_page': 'N/A',
            'layout_type': 'Master',
            'has_resource_packages': False
        }

    def _calculate_score(self):
        """Calcula el score general del reporte (0-100)"""
        from .pbix_analyzer import PBIXAnalyzer
        # Reusar la lógica de scoring del PBIXAnalyzer
        dummy_analyzer = PBIXAnalyzer.__new__(PBIXAnalyzer)
        dummy_analyzer.config = self.config
        dummy_analyzer.metrics = self.metrics
        dummy_analyzer._calculate_score()
        self.metrics = dummy_analyzer.metrics

    def _generate_recommendations(self):
        """Genera recomendaciones basadas en los hallazgos"""
        from .pbix_analyzer import PBIXAnalyzer
        # Reusar la lógica de recomendaciones del PBIXAnalyzer
        dummy_analyzer = PBIXAnalyzer.__new__(PBIXAnalyzer)
        dummy_analyzer.config = self.config
        dummy_analyzer.metrics = self.metrics
        dummy_analyzer.recommendations = []
        dummy_analyzer._generate_recommendations()
        self.recommendations = dummy_analyzer.recommendations

    def _build_result(self) -> Dict[str, Any]:
        """Construye el resultado final del análisis"""
        return {
            'report_name': self.report_name,
            'report_path': self.report_path or self.semantic_model_path or 'unknown',
            'report_type': 'pbip',
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'score': self.metrics.get('overall_score', 0),
            'score_category': self.metrics.get('score_category', 'unknown')
        }


def analyze_pbip_file(pbip_path: str, config_path: str = None) -> Dict[str, Any]:
    """
    Función helper para analizar un proyecto .pbip

    Args:
        pbip_path: Ruta a la carpeta del proyecto .pbip
        config_path: Ruta al archivo de configuración (opcional)

    Returns:
        Diccionario con resultados del análisis
    """
    analyzer = PBIPAnalyzer(pbip_path, config_path)
    return analyzer.analyze()
