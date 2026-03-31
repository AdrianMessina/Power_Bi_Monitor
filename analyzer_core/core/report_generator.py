"""
Generador de reportes HTML y PDF
"""

import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import json


class ReportGenerator:
    """Genera reportes visuales a partir de los resultados del análisis"""

    def __init__(self, template_dir: str = None):
        """
        Inicializa el generador de reportes

        Args:
            template_dir: Directorio de templates Jinja2
        """
        if template_dir is None:
            template_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'templates'
            )

        self.env = Environment(loader=FileSystemLoader(template_dir))
        # Filtro round mejorado que maneja strings y números
        def safe_round(x, decimals=2):
            try:
                # Si es un número, redondearlo
                if isinstance(x, (int, float)):
                    return round(x, decimals)
                # Si es string, intentar extraer el número
                if isinstance(x, str):
                    # Si ya tiene formato (ej: "28.62 MB"), retornar tal cual
                    if any(char.isalpha() for char in x):
                        return x
                    # Si es número en string, convertir y redondear
                    return round(float(x), decimals)
                return x
            except (ValueError, TypeError):
                # Si falla, retornar el valor original
                return x
        self.env.filters['round'] = safe_round

    def generate_html_report(self, analysis_result: Dict[str, Any], output_path: str = None) -> str:
        """
        Genera un reporte HTML

        Args:
            analysis_result: Resultado del análisis de PBIXAnalyzer
            output_path: Ruta donde guardar el reporte (opcional)

        Returns:
            HTML string o ruta del archivo guardado
        """
        template = self.env.get_template('report_template.html')

        # Preparar datos para el template
        context = {
            'report_name': analysis_result['report_name'],
            'report_path': analysis_result['report_path'],
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': analysis_result['score'],
            'score_category': analysis_result['score_category'],
            'metrics': analysis_result['metrics'],
            'recommendations': analysis_result['recommendations'],
            'metric_scores': analysis_result['metrics'].get('metric_scores', {}),
            'developer': 'Adrián Javier Messina',
            'team': 'Torre Visualización',
        }

        # Agregar datos para gráficos
        context['chart_data'] = self._prepare_chart_data(analysis_result)

        html_content = template.render(**context)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return output_path

        return html_content

    def _prepare_chart_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara datos para visualizaciones"""
        metrics = analysis_result['metrics']

        # Datos para gráfico de tipos de visuales
        visual_types = metrics.get('visual_types', {})

        # Datos para score por métrica
        metric_scores = metrics.get('metric_scores', {})
        score_labels = []
        score_values = []
        score_colors = []

        for metric_name, metric_data in metric_scores.items():
            score_labels.append(self._format_metric_name(metric_name))
            score_values.append(metric_data['score'])

            # Colores según status
            if metric_data['status'] == 'good':
                score_colors.append('#28a745')  # verde
            elif metric_data['status'] == 'warning':
                score_colors.append('#ffc107')  # amarillo
            else:
                score_colors.append('#dc3545')  # rojo

        return {
            'visual_types': visual_types,
            'score_labels': score_labels,
            'score_values': score_values,
            'score_colors': score_colors,
        }

    def _format_metric_name(self, metric_name: str) -> str:
        """Formatea nombres de métricas para display"""
        names = {
            'visualizations_per_page': 'Visualizaciones',
            'filters_per_page': 'Filtros',
            'custom_visuals': 'Custom Visuals',
            'embedded_images_mb': 'Imágenes',
            'total_pages': 'Páginas',
            'dax_measures_complex': 'Medidas DAX',
            'tables_in_model': 'Tablas',
            'relationships': 'Relaciones',
        }
        return names.get(metric_name, metric_name)

    def generate_pdf_report(self, analysis_result: Dict[str, Any], output_path: str):
        """
        Genera un reporte PDF

        Args:
            analysis_result: Resultado del análisis
            output_path: Ruta donde guardar el PDF
        """
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration

            # Generar HTML primero
            html_content = self.generate_html_report(analysis_result)

            # CSS adicional para PDF
            pdf_css = CSS(string='''
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-size: 10pt;
                }
                .no-print {
                    display: none;
                }
            ''')

            font_config = FontConfiguration()

            # Convertir a PDF
            HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[pdf_css],
                font_config=font_config
            )

            return output_path

        except ImportError:
            print("Error: WeasyPrint no está instalado. Instalar con: pip install weasyprint")
            raise

    def generate_json_report(self, analysis_result: Dict[str, Any], output_path: str):
        """
        Genera un reporte en formato JSON

        Args:
            analysis_result: Resultado del análisis
            output_path: Ruta donde guardar el JSON
        """
        # Agregar información del desarrollador y torre al resultado
        result_with_metadata = analysis_result.copy()
        result_with_metadata['metadata'] = {
            'team': 'Torre Visualización',
            'developer': 'Adrián Javier Messina',
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tool': 'Power BI Analyzer v1.1'
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_with_metadata, f, indent=2, ensure_ascii=False)

        return output_path
