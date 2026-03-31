@echo off
REM YPF BI Monitor Suite - Launcher Script
REM Windows Batch File

echo ========================================
echo    YPF BI Monitor Suite
echo    Iniciando aplicacion...
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [!] No se encontro entorno virtual.
    echo [*] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
)

REM Activate venv
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [*] Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
)

REM Start Streamlit
echo.
echo [*] Iniciando YPF BI Monitor Suite...
echo [*] La aplicacion se abrira en tu navegador
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo ========================================
echo.

streamlit run main.py

pause
