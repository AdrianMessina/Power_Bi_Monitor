# YPF BI Monitor Suite

Suite integrada de herramientas para analisis, documentacion y optimizacion de reportes Power BI.

**Version:** 1.0 | **Desarrollado por:** IT Analytics - YPF S.A.

---

## 📋 Que incluye esta suite

| App | Descripcion |
|-----|-------------|
| **Power BI Analyzer** | Analisis completo de proyectos PBIP: metricas, modelo de datos, visualizaciones |
| **Documentation Generator** | Genera documentacion tecnica-funcional automatica en Word |
| **Layout Organizer** | Organiza diagramas de modelo Power BI automaticamente |
| **DAX Optimizer** | Analiza y optimiza medidas DAX con recomendaciones |
| **BI Bot** | Asistente para consultas sobre modelos Power BI |
| **Usage Dashboard** | Metricas de uso (solo administradores) |

---

## ⚡ Inicio Rapido

### 📚 Guias Disponibles

| Guia | Para quien | Link |
|------|-----------|------|
| **README.md** | Usuarios con experiencia tecnica | *(Este archivo)* |
| **INSTALL.md** | Usuarios sin experiencia tecnica (paso a paso detallado) | [Ver guia](INSTALL.md) |
| **PROXY_SETUP.md** | Referencia rapida de comandos proxy | [Ver guia](PROXY_SETUP.md) |

---

### Antes de empezar: ¿Estas en la red corporativa de YPF?

**Elige tu escenario:**

- ✅ **[OPCION A](#opcion-a-instalacion-en-red-corporativa-ypf)** - Estas conectado a la red corporativa de YPF (WiFi o VPN corporativa)
- ✅ **[OPCION B](#opcion-b-instalacion-fuera-de-red-corporativa)** - Eres usuario externo o estas fuera de la red YPF

> **¿Como saber si estoy en red corporativa?**
> - Si tu computadora esta conectada a WiFi YPF → RED CORPORATIVA
> - Si usas VPN de YPF → RED CORPORATIVA
> - Si trabajas desde casa sin VPN → FUERA DE RED
>
> **¿Primera vez instalando?** → Ver [INSTALL.md](INSTALL.md) para guia paso a paso

---

## OPCION A: Instalacion en Red Corporativa YPF

### Paso 1: Verificar Python

**1.1** Abrir terminal (CMD o PowerShell):
- Presiona `Windows + R`
- Escribe `cmd` y Enter

**1.2** Verificar que Python esta instalado:
```cmd
python --version
```

**Resultado esperado:** `Python 3.10.x` o superior

**Si no funciona:**
- Descargar Python desde: https://www.python.org/downloads/
- Durante instalacion: ✅ **Marcar "Add Python to PATH"** (IMPORTANTE)
- Reiniciar la terminal

---

### Paso 2: Descargar el proyecto

**2.1** Descargar el ZIP desde GitHub:
- Click en el boton verde **"Code"** → **"Download ZIP"**
- Descomprimir en una carpeta, por ejemplo: `C:\Users\TuUsuario\ypf_bi_monitor`

O si tienes Git instalado:
```cmd
git clone <URL_DEL_REPOSITORIO>
cd ypf_bi_monitor
```

---

### Paso 3: Crear entorno virtual

**3.1** Navegar a la carpeta del proyecto:
```cmd
cd C:\Users\TuUsuario\ypf_bi_monitor
```
*(Ajusta la ruta segun donde descargaste)*

**3.2** Crear entorno virtual:
```cmd
python -m venv venv
```

Veras que se crea una carpeta `venv\` en el directorio.

---

### Paso 4: Activar entorno virtual

```cmd
venv\Scripts\activate.bat
```

**Resultado esperado:** Veras `(venv)` al inicio de la linea:
```
(venv) C:\Users\TuUsuario\ypf_bi_monitor>
```

---

### Paso 5: Configurar PROXY CORPORATIVO (⚠️ IMPORTANTE)

**5.1** Configurar variables de entorno para pip:

**En CMD (Command Prompt):**
```cmd
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure
```

**En PowerShell:**
```powershell
$env:HTTPS_PROXY="http://proxy-azure"
$env:HTTP_PROXY="http://proxy-azure"
```

**En Git Bash:**
```bash
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure
```

> ⚠️ **IMPORTANTE:** Debes ejecutar estos comandos en CADA sesion nueva de terminal antes de usar pip.

---

### Paso 6: Instalar dependencias

```cmd
pip install -r requirements.txt
```

**Tiempo estimado:** 3-5 minutos

**Resultado esperado:**
```
Successfully installed streamlit-1.31.0 pandas-2.1.4 plotly-5.18.0 ...
```

**Si ves errores de conexion:**
- Verifica que ejecutaste los comandos del Paso 5 (proxy)
- Si el proxy cambio, consulta con IT

---

### Paso 7: Configurar variables de entorno (OPCIONAL)

Solo si quieres habilitar el Usage Dashboard:

```cmd
copy .env.example .env
notepad .env
```

Editar y cambiar:
```
YPF_BI_ADMIN_PASSWORD=tu_clave_secreta
```

Guardar y cerrar.

---

### Paso 8: Ejecutar la aplicacion

**Opcion mas facil - Doble click:**
```
Doble click en: run_app.bat
```

**O desde terminal:**
```cmd
venv\Scripts\activate.bat
streamlit run main.py
```

**Resultado:** Se abrira el navegador en `http://localhost:8501`

---

### Paso 9: Verificar que funciona

Si vez el dashboard de YPF BI Monitor con el logo YPF → ✅ **TODO OK**

---

## OPCION B: Instalacion Fuera de Red Corporativa

### Paso 1: Verificar Python

**1.1** Abrir terminal (CMD, PowerShell, o Terminal en Mac/Linux)

**1.2** Verificar que Python esta instalado:
```bash
python --version
```
o en Mac/Linux:
```bash
python3 --version
```

**Resultado esperado:** `Python 3.10.x` o superior

**Si no funciona:**
- Descargar Python desde: https://www.python.org/downloads/
- Durante instalacion: ✅ **Marcar "Add Python to PATH"** (IMPORTANTE)
- Reiniciar la terminal

---

### Paso 2: Descargar el proyecto

**2.1** Descargar el ZIP desde GitHub:
- Click en el boton verde **"Code"** → **"Download ZIP"**
- Descomprimir en una carpeta de tu eleccion

O si tienes Git:
```bash
git clone <URL_DEL_REPOSITORIO>
cd ypf_bi_monitor
```

---

### Paso 3: Crear entorno virtual

**Windows:**
```cmd
cd ruta\a\ypf_bi_monitor
python -m venv venv
```

**Mac/Linux:**
```bash
cd /ruta/a/ypf_bi_monitor
python3 -m venv venv
```

---

### Paso 4: Activar entorno virtual

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

Veras `(venv)` al inicio de la linea.

---

### Paso 5: Instalar dependencias

**SIMPLE - Sin configuracion de proxy:**

```bash
pip install -r requirements.txt
```

**Tiempo estimado:** 2-4 minutos

**Resultado esperado:**
```
Successfully installed streamlit-1.31.0 pandas-2.1.4 plotly-5.18.0 ...
```

---

### Paso 6: Configurar variables de entorno (OPCIONAL)

Solo si quieres habilitar el Usage Dashboard:

**Windows:**
```cmd
copy .env.example .env
notepad .env
```

**Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

Editar y cambiar:
```
YPF_BI_ADMIN_PASSWORD=tu_clave_secreta
```

Guardar y cerrar.

---

### Paso 7: Ejecutar la aplicacion

**Windows - Doble click:**
```
run_app.bat
```

**Mac/Linux:**
```bash
chmod +x run_app.sh
./run_app.sh
```

**O manualmente:**
```bash
# Activar venv (si no esta activo)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat  # Windows

# Ejecutar
streamlit run main.py
```

Se abrira el navegador en `http://localhost:8501`

---

## ❓ Problemas Comunes

### ❌ Error: "python no se reconoce como comando"

**Solucion:**
1. Reinstalar Python desde https://www.python.org/downloads/
2. Durante instalacion, marcar ✅ **"Add Python to PATH"**
3. Reiniciar la terminal

---

### ❌ Error: "Connection to pypi.org timed out" (Red Corporativa)

**Causa:** No configuraste el proxy antes de instalar

**Solucion:**
```cmd
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure
pip install -r requirements.txt
```

---

### ❌ Error: "No module named 'streamlit'"

**Causa:** El entorno virtual no esta activado

**Solucion:**
```cmd
venv\Scripts\activate.bat
```
Veras `(venv)` al inicio de la linea.

---

### ❌ Error: "cannot be loaded because running scripts is disabled" (PowerShell)

**Solucion:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Luego activar el entorno virtual nuevamente.

---

### ❌ Error instalando weasyprint en Windows

weasyprint necesita GTK3. Si falla:

**Opcion 1:** Instalar GTK3:
- Descargar desde: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
- Instalar y reiniciar terminal
- `pip install weasyprint`

**Opcion 2:** Instalar sin weasyprint (la app funciona igual, solo no exporta PDF):
```cmd
pip install -r requirements.txt --no-deps weasyprint
```

---

### ❌ La app se abre pero veo error "Address already in use"

**Causa:** Ya hay otra instancia corriendo

**Solucion:**
```cmd
# Cerrar todos los procesos de Streamlit
taskkill /F /IM streamlit.exe

# Volver a ejecutar
streamlit run main.py
```

---

### ❌ El Usage Dashboard no aparece en el menu

Es normal. Para habilitarlo:
1. Crear archivo `.env` copiando `.env.example`
2. Configurar `YPF_BI_ADMIN_PASSWORD=tu_clave`
3. Reiniciar la app

---

## 📁 Donde encontrar archivos .pbip

Los proyectos Power BI en formato PBIP se crean desde Power BI Desktop:

1. Abrir tu reporte en **Power BI Desktop**
2. **Archivo > Guardar como**
3. Seleccionar tipo: **Power BI Project (.pbip)**
4. Se crea una estructura de carpetas:
   ```
   MiReporte/
   ├── MiReporte.pbip              <-- Este es el archivo a usar
   ├── MiReporte.SemanticModel/
   └── MiReporte.Report/
   ```

**Ruta a ingresar en la app:**
```
C:/Users/TuUsuario/Documents/MiReporte/MiReporte.pbip
```

---

## 📊 Estructura del Proyecto

<details>
<summary>Click para expandir</summary>

```
ypf_bi_monitor/
│
├── main.py                          # Punto de entrada
├── requirements.txt                 # Dependencias
├── README.md                        # Esta documentacion
├── .env.example                     # Variables de entorno (ejemplo)
├── .gitignore                       # Archivos excluidos de Git
│
├── run_app.bat                      # Lanzador Windows
├── run_app.sh                       # Lanzador Mac/Linux
│
├── .streamlit/
│   └── config.toml                  # Tema YPF corporativo
│
├── apps/                            # Interfaces de usuario
│   ├── home.py
│   ├── powerbi_analyzer.py
│   ├── documentation_generator.py
│   ├── layout_organizer.py
│   ├── dax_optimizer.py
│   ├── bi_bot.py
│   └── usage_dashboard.py
│
├── apps_core/                       # Logica de negocio
│   ├── analyzer_core/
│   ├── docgen_core/
│   ├── layout_core/
│   ├── dax_core/
│   └── bot_core/
│
├── shared/                          # Utilidades compartidas
│   ├── usage_logger.py
│   └── components.py
│
├── config/
│   └── analyzer_thresholds.yaml
│
├── templates/
│   └── docgen/
│       └── plantilla_corporativa_ypf.docx
│
└── assets/
    └── logo_ypf.png
```

</details>

---

## 🔧 Uso de las Herramientas

### Power BI Analyzer

1. Click en **"Power BI Analyzer"** en el menu lateral
2. Ingresar ruta completa al archivo `.pbip`
3. Click en **"Analizar"**
4. Explorar las secciones: Metricas, Modelo, Visualizaciones, DAX

### Documentation Generator

1. Click en **"Documentation Generator"**
2. Ingresar ruta al `.pbip`
3. Completar campos opcionales (objetivo, alcance, version)
4. (Opcional) Subir imagen de diagrama ER y capturas
5. Click en **"Generar Documento"**
6. Descargar Word generado

### DAX Optimizer

1. Click en **"DAX Optimizer"**
2. Ingresar ruta al `.pbip`
3. Ajustar nivel de tolerancia (0-100)
4. Click en **"Analizar Medidas"**
5. Revisar criticos, warnings e informacion

### BI Bot

1. Click en **"BI Bot"**
2. Cargar modelo PBIP o conectar via Power BI Desktop
3. Hacer preguntas: "Cuantas tablas hay?", "Que medidas existen?"

### Layout Organizer

1. Click en **"Layout Organizer"**
2. Cargar proyecto PBIP
3. Seleccionar tipo de layout
4. Aplicar organizacion

---

## 🚀 Para Desarrolladores

### Agregar una nueva app

1. Crear `apps/mi_app.py` con funcion `render_app(logger)`
2. Crear `apps_core/mi_core/` con logica de negocio
3. Importar en `main.py` y agregar al menu
4. Usar `shared_styles.py` para header/footer

### Arquitectura

- **apps/**: Solo interfaz Streamlit (UI)
- **apps_core/**: Logica de negocio (sin Streamlit)
- **shared/**: Codigo comun (logger, componentes)

### CSS Corporativo

Centralizado en `apps_core/layout_core/shared_styles.py`:
- `inject_shared_styles()` - CSS global
- `render_app_header(titulo, subtitulo, version)` - Header
- `render_footer()` - Footer
- Paleta: `#0451E4` (azul YPF), `#000000`, `#F8FAFC`

---

## 📞 Soporte

**Para problemas de instalacion:**
- Revisa la seccion [Problemas Comunes](#-problemas-comunes)
- Verifica que seguiste tu [OPCION A](#opcion-a-instalacion-en-red-corporativa-ypf) u [OPCION B](#opcion-b-instalacion-fuera-de-red-corporativa) correctamente

**Para reportar bugs o sugerir mejoras:**
- Contactar al equipo de IT Analytics - YPF S.A.
- O crear un Issue en GitHub

---

## 📄 Licencia

© 2026 YPF S.A. - IT Analytics Team

Desarrollado con ❤️ para analistas de Power BI
