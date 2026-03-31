# Script para crear acceso directo de YPF BI Monitor en el escritorio
# PowerShell Script

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetPath = Join-Path $ScriptDir "run_app.bat"
$ShortcutPath = [Environment]::GetFolderPath("Desktop") + "\YPF BI Monitor.lnk"
$IconPath = Join-Path $ScriptDir "icon.ico"

Write-Host "========================================"
Write-Host "  Creando acceso directo"
Write-Host "  YPF BI Monitor Suite v1.0"
Write-Host "========================================"
Write-Host ""

# Crear objeto WScript.Shell
$WshShell = New-Object -ComObject WScript.Shell

# Crear acceso directo
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "YPF BI Monitor Suite - Suite integrada de herramientas Power BI"
$Shortcut.WindowStyle = 1  # Normal window

# Usar ícono si existe, sino usar el del batch
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
    Write-Host "[OK] Usando icono personalizado"
} else {
    Write-Host "[*] No se encontro icono personalizado, usando predeterminado"
}

# Guardar acceso directo
$Shortcut.Save()

if (Test-Path $ShortcutPath) {
    Write-Host ""
    Write-Host "[OK] Acceso directo creado exitosamente!"
    Write-Host ""
    Write-Host "Ubicacion: $ShortcutPath"
    Write-Host ""
    Write-Host "Ya puedes hacer doble click en 'YPF BI Monitor'"
    Write-Host "en tu escritorio para iniciar la aplicacion."
} else {
    Write-Host ""
    Write-Host "[ERROR] No se pudo crear el acceso directo"
    Write-Host ""
}

Write-Host ""
Write-Host "========================================"
Write-Host ""

# Pausar para ver el resultado
Read-Host "Presiona Enter para continuar"
