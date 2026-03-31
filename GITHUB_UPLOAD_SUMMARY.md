# Resumen de Contenido para GitHub - YPF BI Monitor

**Fecha:** Marzo 2026
**Version:** 1.0

---

## 📦 Que se sube a GitHub

### Total: 106 archivos

---

## 📋 Archivos de Documentacion (5)

| Archivo | Descripcion | Para quien |
|---------|-------------|-----------|
| `README.md` | Documentacion principal con 2 rutas de instalacion | Usuarios tecnicos y no tecnicos |
| `INSTALL.md` | Guia detallada paso a paso con capturas conceptuales | Usuarios sin experiencia tecnica |
| `PROXY_SETUP.md` | Referencia rapida de comandos proxy corporativo | Usuarios en red YPF |
| `requirements.txt` | Lista de dependencias Python (comentada) | Instalacion automatica |
| `.env.example` | Template de variables de entorno | Configuracion opcional |

---

## 🚀 Archivos de Ejecucion (4)

| Archivo | Descripcion | SO |
|---------|-------------|-----|
| `main.py` | Punto de entrada de la aplicacion | Todos |
| `run_app.bat` | Lanzador automatico | Windows |
| `run_app.sh` | Lanzador automatico | Linux/Mac |
| `create_desktop_shortcut.ps1` | Crear acceso directo | Windows |

---

## ⚙️ Archivos de Configuracion (3)

| Archivo | Descripcion |
|---------|-------------|
| `.gitignore` | Excluye venv, logs, .env, cache |
| `.streamlit/config.toml` | Tema corporativo YPF (colores, puerto) |
| `config/analyzer_thresholds.yaml` | Umbrales para Power BI Analyzer |

---

## 🎨 Assets (2)

| Archivo | Descripcion |
|---------|-------------|
| `assets/logo_ypf.png` | Logo corporativo YPF |
| `templates/docgen/plantilla_corporativa_ypf.docx` | Template Word para documentacion |

---

## 💻 Codigo Fuente (92 archivos)

### Apps - Interfaz Usuario (7)
- `apps/home.py` - Dashboard principal
- `apps/powerbi_analyzer.py` - Analisis de PBIP
- `apps/documentation_generator.py` - Generacion de docs
- `apps/layout_organizer.py` - Organizacion de layouts
- `apps/dax_optimizer.py` - Optimizacion DAX
- `apps/bi_bot.py` - Bot conversacional
- `apps/usage_dashboard.py` - Metricas de uso (admin)

### Apps Core - Logica de Negocio (82)

**analyzer_core/** (4 archivos)
- Parsers PBIP/PBIX
- Generacion de reportes HTML/PDF
- Analisis de TMDL

**bot_core/** (7 archivos)
- Conector XMLA a Power BI Desktop
- Lector de archivos PBIP
- Detector de instancias Power BI

**dax_core/** (6 archivos)
- Parser DAX
- Analizador de medidas
- Sistema de sugerencias
- Ranking por complejidad

**docgen_core/** (33 archivos)
- Parsers: PBIP, TMDL, BIM
- Modelos: Table, Measure, Relationship, etc.
- Builders: Word (docx)
- Generadores: Diagramas ER (networkx)
- Validators: Modelo, relaciones

**layout_core/** (3 archivos)
- Organizador de layouts
- **shared_styles.py** - CSS corporativo unificado
- Wrapper Streamlit

### Shared - Utilidades (2)
- `shared/usage_logger.py` - Logger centralizado (JSONL)
- `shared/components.py` - Componentes UI reutilizables

---

## 🚫 Que NO se sube (excluido por .gitignore)

| Excluido | Razon | Tamaño aprox |
|----------|-------|--------------|
| `venv/` | Entorno virtual - se recrea con `pip install` | ~500-800 MB |
| `logs/` | Logs generados en runtime | Variable |
| `.env` | Contiene passwords/secrets | - |
| `__pycache__/` | Cache Python - se regenera | ~50 MB |
| `*.pyc` | Bytecode compilado | Variable |
| Archivos `.docx` generados | Salidas de Documentation Generator | Variable |

**Total GitHub repo:** ~20-30 MB (sin venv ni cache)

---

## 🔐 Seguridad

### Datos sensibles NUNCA subidos:
- ✅ Passwords de admin (`.env`)
- ✅ Logs de uso con informacion de usuarios
- ✅ Entorno virtual con posibles credenciales
- ✅ Archivos temporales

### Archivos publicos seguros:
- ✅ Codigo fuente (sin credenciales hardcodeadas)
- ✅ Template Word (sin datos sensibles)
- ✅ Configuraciones (sin passwords)

---

## 📊 Dependencias Requeridas

### Core (obligatorias)
```
streamlit>=1.31.0        # Framework web
pandas>=2.1.4            # Procesamiento datos
numpy>=1.26.4            # Operaciones numericas
plotly>=5.18.0           # Visualizaciones
networkx>=3.0            # Diagramas ER
python-docx>=1.1.0       # Generacion Word
pyyaml>=6.0.1            # Config YAML
loguru>=0.7.0            # Logging
```

### Adicionales (mejoran funcionalidad)
```
weasyprint>=61.2         # Export PDF (Power BI Analyzer)
jinja2>=3.1.4            # Templates HTML
requests>=2.27.0         # HTTP (para Lottie)
colorama>=0.4.6          # Colores en consola
```

### Opcionales (la app funciona sin ellas)
```
streamlit-extras>=0.3.0  # Componentes extra UI
streamlit-lottie>=0.0.5  # Animaciones
```

**Total instalacion:** ~300-400 MB (con todas las dependencias)

---

## 🎯 Casos de Uso

### Usuario Tipo 1: Analista BI en YPF (Red Corporativa)
1. Descargar ZIP desde GitHub
2. Seguir **INSTALL.md** con configuracion de proxy
3. Usar Power BI Analyzer y Documentation Generator

### Usuario Tipo 2: Consultor Externo (Sin Proxy)
1. Clonar repo con Git
2. Seguir **README.md** instalacion normal
3. Usar DAX Optimizer y BI Bot

### Usuario Tipo 3: Desarrollador (Extender funcionalidad)
1. Fork del repositorio
2. Crear nueva app en `apps/`
3. Pull request al repo principal

---

## ✅ Verificacion Pre-Upload

- [x] `.gitignore` configurado correctamente
- [x] `.env` excluido (no se sube)
- [x] Documentacion completa (3 archivos MD)
- [x] Codigo limpio sin credenciales
- [x] Template Word incluido
- [x] Logo YPF incluido
- [x] requirements.txt actualizado y comentado
- [x] Configuracion Streamlit incluida
- [x] Scripts de lanzamiento para Windows y Linux
- [x] Shared styles unificados (YPF corporativo)
- [x] Usage Dashboard protegido con password

---

## 🚀 Proximos Pasos Despues de Upload

1. **Crear Release v1.0** en GitHub
2. Crear **Wiki** con ejemplos de uso
3. Agregar **Screenshots** al README
4. Configurar **GitHub Actions** para CI (opcional)
5. Agregar badge de licencia

---

## 📞 Responsables

**Desarrollo:** IT Analytics Team - YPF S.A.
**Mantenimiento:** Equipo de visualizacion
**Contacto:** IT Analytics

---

**Documento generado:** 27-Mar-2026
**Preparado para upload a:** GitHub (publico/privado segun decision YPF)
