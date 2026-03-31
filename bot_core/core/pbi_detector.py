"""
Power BI Desktop Detector
Detecta la instalación de Power BI Desktop y localiza las DLLs necesarias
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PowerBIDetector:
    """Detecta Power BI Desktop y sus componentes"""

    def __init__(self):
        self.pbi_path: Optional[Path] = None
        self.dll_path: Optional[Path] = None
        self.version: Optional[str] = None

    def detect_installation(self) -> bool:
        """
        Detecta la instalación de Power BI Desktop.

        Returns:
            True si se encontró Power BI Desktop
        """
        # Rutas comunes de instalación
        possible_paths = [
            Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / "Microsoft Power BI Desktop",
            Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')) / "Microsoft Power BI Desktop",
            Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft\\WindowsApps\\Microsoft.MicrosoftPowerBIDesktop_8wekyb3d8bbwe",
        ]

        for path in possible_paths:
            if path.exists():
                self.pbi_path = path
                logger.info(f"Power BI Desktop encontrado en: {path}")

                # Buscar DLLs
                if self._find_dlls():
                    return True

        logger.warning("Power BI Desktop no encontrado")
        return False

    def _find_dlls(self) -> bool:
        """
        Busca las DLLs de Analysis Services.

        Returns:
            True si se encontraron las DLLs
        """
        if not self.pbi_path:
            return False

        # Buscar en subdirectorio bin
        bin_path = self.pbi_path / "bin"

        if bin_path.exists():
            # Verificar DLLs necesarias (AMO de Power BI Desktop)
            required_dlls = [
                "Microsoft.PowerBI.Amo.dll",
                "Microsoft.AnalysisServices.AdomdClient.dll",
            ]

            # Verificar que al menos la principal exista
            main_dll = bin_path / "Microsoft.PowerBI.Amo.dll"
            if main_dll.exists():
                self.dll_path = bin_path
                logger.info(f"DLLs encontradas en: {bin_path}")
                return True

        logger.warning("DLLs de Analysis Services no encontradas")
        return False

    def get_dll_paths(self) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Obtiene las rutas a las DLLs principales.

        Returns:
            Tupla (path_amo_dll, path_adomd_dll)
        """
        if not self.dll_path:
            return None, None

        return (
            self.dll_path / "Microsoft.PowerBI.Amo.dll",
            self.dll_path / "Microsoft.AnalysisServices.AdomdClient.dll"
        )

    def get_info(self) -> dict:
        """Retorna información sobre la instalación detectada"""
        return {
            "pbi_path": str(self.pbi_path) if self.pbi_path else None,
            "dll_path": str(self.dll_path) if self.dll_path else None,
            "version": self.version,
            "installed": self.pbi_path is not None
        }


# Instancia global
_detector = None

def get_detector() -> PowerBIDetector:
    """Obtiene o crea el detector singleton"""
    global _detector
    if _detector is None:
        _detector = PowerBIDetector()
        _detector.detect_installation()
    return _detector
