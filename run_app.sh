#!/bin/bash
# YPF BI Monitor Suite - Launcher Script
# Linux/Mac Shell Script

echo "========================================"
echo "   YPF BI Monitor Suite"
echo "   Iniciando aplicación..."
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[!] No se encontró entorno virtual."
    echo "[*] Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual"
        exit 1
    fi
    echo "[OK] Entorno virtual creado"
fi

# Activate venv
echo "[*] Activando entorno virtual..."
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "[*] Instalando dependencias..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Error al instalar dependencias"
        exit 1
    fi
    echo "[OK] Dependencias instaladas"
fi

# Start Streamlit
echo ""
echo "[*] Iniciando YPF BI Monitor Suite..."
echo "[*] La aplicación se abrirá en tu navegador"
echo ""
echo "Presiona Ctrl+C para detener la aplicación"
echo "========================================"
echo ""

streamlit run main.py
