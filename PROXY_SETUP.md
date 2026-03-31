# Configuracion de Proxy - YPF Red Corporativa

**Guia Rapida de Referencia**

---

## ⚡ Comandos Rapidos

### CMD (Command Prompt)

```cmd
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure
```

---

### PowerShell

```powershell
$env:HTTPS_PROXY="http://proxy-azure"
$env:HTTP_PROXY="http://proxy-azure"
```

---

### Git Bash

```bash
export HTTPS_PROXY=http://proxy-azure
export HTTP_PROXY=http://proxy-azure
```

---

## 📋 Cuando usar estos comandos

**SIEMPRE antes de:**
- `pip install ...`
- `pip install -r requirements.txt`
- Cualquier comando `pip`

**NO es necesario antes de:**
- `streamlit run main.py`
- `python main.py`
- Ejecutar `run_app.bat`

---

## ⚠️ Importante

- Estos comandos se aplican SOLO a la sesion actual de terminal
- Si cierras la terminal, debes volver a ejecutarlos en la nueva sesion
- NO afectan otras aplicaciones de tu computadora
- NO es necesario reiniciar Windows

---

## 🔍 Como verificar que esta configurado

```cmd
echo %HTTPS_PROXY%
```

**Resultado esperado:**
```
http://proxy-azure
```

**Si sale vacio:** No esta configurado, ejecuta los comandos de arriba

---

## 💾 Guardar en archivo (Opcional)

Para no tener que escribir los comandos cada vez:

**1. Crear archivo `setup_proxy.bat`:**

```cmd
@echo off
set HTTPS_PROXY=http://proxy-azure
set HTTP_PROXY=http://proxy-azure
echo Proxy configurado correctamente
```

**2. Ejecutar antes de usar pip:**

```cmd
setup_proxy.bat
pip install -r requirements.txt
```

---

## ❌ Error Comun

### "Connection to pypi.org timed out"

**Causa:** No ejecutaste los comandos de proxy

**Solucion:**
1. Ejecutar los comandos de arriba (CMD/PowerShell/Bash segun tu terminal)
2. Volver a ejecutar el comando `pip` que fallo

---

## 📞 Contacto

Si el proxy cambio o estos comandos no funcionan:
- Contactar IT de YPF
- Verificar en: `C:\Users\<TuUsuario>\1 - Claude - Proyecto viz\Instalar librerias.txt`

---

**Proxy actual:** `http://proxy-azure`
**Ultima actualizacion:** Marzo 2026
