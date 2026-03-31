"""
Power BI Analyzer Core Module
"""

import os
from .pbix_analyzer import PBIXAnalyzer, analyze_pbix_file
from .pbip_analyzer import PBIPAnalyzer, analyze_pbip_file
from .report_generator import ReportGenerator


def analyze_powerbi_file(file_path: str, config_path: str = None):
    """
    Analiza un archivo o proyecto de Power BI automáticamente
    Detecta si es PBIX (archivo) o PBIP (carpeta) y usa el analizador apropiado

    Args:
        file_path: Ruta al archivo .pbix o carpeta .pbip
        config_path: Ruta al archivo de configuración (opcional)

    Returns:
        Diccionario con resultados del análisis
    """
    if os.path.isdir(file_path):
        # Es una carpeta, probablemente PBIP
        # Verificar si contiene archivos típicos de PBIP
        if os.path.exists(os.path.join(file_path, 'definition')):
            print("Detectado: Proyecto PBIP")
            return analyze_pbip_file(file_path, config_path)
        elif any(f.endswith('.bim') for f in os.listdir(file_path)):
            print("Detectado: Proyecto PBIP")
            return analyze_pbip_file(file_path, config_path)
        else:
            raise ValueError(f"La carpeta {file_path} no parece ser un proyecto PBIP válido")
    elif os.path.isfile(file_path):
        # Es un archivo
        if file_path.endswith('.pbix'):
            print("Detectado: Archivo PBIX")
            return analyze_pbix_file(file_path, config_path)
        elif file_path.endswith('.pbip'):
            print("Detectado: Archivo PBIP")
            return analyze_pbip_file(file_path, config_path)
        else:
            raise ValueError(f"El archivo {file_path} debe ser .pbix o .pbip")
    else:
        raise ValueError(f"La ruta {file_path} no existe")


__all__ = [
    'PBIXAnalyzer',
    'PBIPAnalyzer',
    'analyze_pbix_file',
    'analyze_pbip_file',
    'analyze_powerbi_file',
    'ReportGenerator'
]
