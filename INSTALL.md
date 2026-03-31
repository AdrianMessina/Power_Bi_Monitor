# Guia de Instalacion Detallada - YPF BI Monitor

**Para usuarios sin experiencia tecnica**

Esta guia te llevara paso a paso por la instalacion completa, sin asumir conocimientos previos.

---

## Paso 0: Identificar tu situacion

### Pregunta 1: ¿Tienes Python instalado?

**Como verificar:**

1. Presiona las teclas `Windows + R` al mismo tiempo
2. Aparecera una ventana pequeña que dice "Ejecutar"
3. Escribe: `cmd`
4. Presiona Enter
5. Se abrira una ventana negra (la "terminal" o "consola")
6. Escribe: `python --version`
7. Presiona Enter

**Resultado A - Python instalado:**
```
Python 3.12.1
```
✅ Continua al Paso 1

**Resultado B - Python NO instalado:**
```
'python' no se reconoce como un comando interno o externo
```
⚠️ Continua a "Instalar Python" (abajo)

---

### Instalar Python (solo si no lo tienes)

1. Abrir navegador web
2. Ir a: `https://www.python.org/downloads/`
3. Click en el boton amarillo grande: **"Download Python 3.XX"**
4. Esperar que descargue (archivo `python-3.XX-amd64.exe`)
5. Abrir el archivo descargado (doble click)
6. **⚠️ MUY IMPORTANTE:** Marcar la casilla **"Add Python to PATH"** (abajo)
   ```
   [✓] Add Python 3.XX to PATH
   ```
7. Click en **"Install Now"**
8. Esperar que termine (2-3 minutos)
9. Click en **"Close"**
10. **Cerrar y volver a abrir** la terminal (CMD) que tenias abierta
11. Verificar nuevamente: `python --version`

---

### Pregunta 2: ¿Estas en la red corporativa YPF?

**Como saber:**

- ¿Tu WiFi dice "YPF" o algo relacionado? → **SI**
- ¿Estas conectado con VPN de YPF? → **SI**
- ¿Trabajas desde tu casa/externo sin VPN? → **NO**

**Si dijiste SI:** Necesitas configurar PROXY (sigue "Instalacion con Proxy")
**Si dijiste NO:** Instalacion normal (sigue "Instalacion sin Proxy")

---

## Instalacion CON Proxy (Red Corporativa YPF)

### Paso 1: Descargar el proyecto

**1.1** Ir a la pagina de GitHub del proyecto en tu navegador

**1.2** Click en el boton verde **"Code"**

**1.3** Click en **"Download ZIP"**

**1.4** Esperar que descargue (archivo `ypf_bi_monitor-main.zip`)

**1.5** Ir a Descargas, hacer click derecho en el ZIP

**1.6** Seleccionar **"Extraer todo..."**

**1.7** Click en **"Extraer"**

**1.8** Recordar donde quedo la carpeta (ej: `C:\Users\TuNombre\Downloads\ypf_bi_monitor-main`)

---

### Paso 2: Abrir terminal en la carpeta del proyecto

**2.1** Abrir el Explorador de Archivos (Windows + E)

**2.2** Navegar a la carpeta descomprimida (ej: `C:\Users\TuNombre\Downloads\ypf_bi_monitor-main`)

**2.3** Click en la barra de direccion (arriba, donde dice la ruta)

**2.4** Escribir: `cmd`

**2.5** Presionar Enter

Se abre una terminal ya posicionada en esa carpeta.

---

### Paso 3: Crear entorno virtual

**3.1** En la terminal, escribir:
```cmd
python -m venv venv
```

**3.2** Presionar Enter

**3.3** Esperar 10-20 segundos (no aparece ningun mensaje, es normal)

**3.4** Verificar que se creo una carpeta `venv` dentro del proyecto

---

### Paso 4: Activar entorno virtual

**4.1** En la terminal, escribir:
```cmd
venv\Scripts\activate.bat
```

**4.2** Presionar Enter

**4.3** Ahora la linea debe empezar con `(venv)`:
```
(venv) C:\Users\TuNombre\Downloads\ypf_bi_monitor-main>
```

---

### Paso 5: Configurar PROXY (⚠️ CRITICO)

**5.1** En la misma terminal, escribir EXACTAMENTE:
```cmd
set HTTPS_PROXY=http://proxy-azure
```

**5.2** Presionar Enter

**5.3** Escribir:
```cmd
set HTTP_PROXY=http://proxy-azure
```

**5.4** Presionar Enter

**⚠️ IMPORTANTE:** Estos comandos NO muestran ningun mensaje. Eso es normal.

---

### Paso 6: Instalar las librerias

**6.1** Escribir:
```cmd
pip install -r requirements.txt
```

**6.2** Presionar Enter

**6.3** Esperar 3-5 minutos mientras se descargan e instalan

**Veras algo como:**
```
Collecting streamlit>=1.31.0
Downloading streamlit-1.31.0...
...
Successfully installed streamlit-1.31.0 pandas-2.1.4 plotly-5.18.0 ...
```

**Si vez errores de "connection timeout":**
- Volver al Paso 5 y ejecutar los comandos de proxy nuevamente
- Luego repetir este Paso 6

---

### Paso 7: Ejecutar la aplicacion

**7.1** Escribir:
```cmd
streamlit run main.py
```

**7.2** Presionar Enter

**7.3** Esperar 5-10 segundos

**7.4** Se abrira automaticamente tu navegador en `http://localhost:8501`

**7.5** Deberias ver el dashboard de YPF BI Monitor con el logo YPF

---

### ✅ Si todo funciono

¡Felicitaciones! Ya puedes usar YPF BI Monitor.

**Para ejecutar en el futuro:**
1. Doble click en `run_app.bat` (en la carpeta del proyecto)
2. O repetir Paso 4 (activar venv) y Paso 7 (streamlit run)

---

## Instalacion SIN Proxy (Usuarios Externos)

### Paso 1: Descargar el proyecto

*(Igual que instalacion CON proxy - ver arriba)*

---

### Paso 2: Abrir terminal en la carpeta del proyecto

*(Igual que instalacion CON proxy - ver arriba)*

---

### Paso 3: Crear entorno virtual

**3.1** En la terminal, escribir:
```cmd
python -m venv venv
```

**3.2** Presionar Enter y esperar

---

### Paso 4: Activar entorno virtual

**4.1** Escribir:
```cmd
venv\Scripts\activate.bat
```

**4.2** Presionar Enter

**4.3** Veras `(venv)` al inicio de la linea

---

### Paso 5: Instalar las librerias (SIN proxy)

**5.1** Escribir:
```cmd
pip install -r requirements.txt
```

**5.2** Presionar Enter

**5.3** Esperar 2-4 minutos

**Resultado esperado:**
```
Successfully installed streamlit-1.31.0 pandas-2.1.4 ...
```

---

### Paso 6: Ejecutar la aplicacion

**6.1** Escribir:
```cmd
streamlit run main.py
```

**6.2** Se abre el navegador en `http://localhost:8501`

---

## ❌ Problemas y Soluciones

### "python no se reconoce como comando"

**Solucion:**
1. Instalar Python (ver "Instalar Python" al inicio)
2. **CRITICO:** Marcar "Add Python to PATH" durante instalacion
3. Cerrar y volver a abrir la terminal

---

### "Connection to pypi.org timed out"

**Causa:** Estas en red corporativa pero no configuraste proxy

**Solucion:**
1. Ejecutar los comandos del Paso 5 (configurar proxy)
2. Volver a ejecutar `pip install -r requirements.txt`

---

### "Access denied" o "Permission denied"

**Solucion:**
1. Cerrar la terminal
2. Click derecho en CMD → **"Ejecutar como administrador"**
3. Navegar nuevamente a la carpeta
4. Repetir los pasos

---

### El navegador no se abre automaticamente

**Solucion:**
1. Abrir navegador manualmente (Chrome, Edge, Firefox)
2. Ir a: `http://localhost:8501`

---

### "Address already in use"

**Causa:** Ya hay otra instancia corriendo

**Solucion Windows:**
1. Presionar Ctrl + C en la terminal actual
2. Escribir: `taskkill /F /IM streamlit.exe`
3. Presionar Enter
4. Volver a ejecutar `streamlit run main.py`

---

### Veo errores en rojo al ejecutar

**Si dice "Warning":** Es solo un aviso, la app funciona igual
**Si dice "Error":** Copia el mensaje completo y contacta soporte

---

## 📞 Ayuda Adicional

**Si estos pasos no funcionaron:**

1. Tomar captura de pantalla del error
2. Anotar:
   - ¿Estas en red corporativa YPF? (Si/No)
   - ¿En que paso te trabaste?
   - ¿Que mensaje de error aparece?
3. Contactar: IT Analytics - YPF S.A.

---

**Guia creada:** 2026
**Version YPF BI Monitor:** 1.0
