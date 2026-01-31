@echo off
echo ====================================================================
echo LIMPIEZA COMPLETA Y RECOMPILACION
echo ====================================================================

cd /d "%~dp0"

echo.
echo [1/6] Eliminando TODOS los archivos compilados de Python...
FOR /d /r . %%d IN (__pycache__) DO @IF EXIST "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo   OK - Cache de Python eliminado

echo.
echo [2/6] Eliminando carpetas de compilacion...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist instalador rd /s /q instalador
if exist TechManager_v1.0_Final rd /s /q TechManager_v1.0_Final
echo   OK - Carpetas eliminadas

echo.
echo [3/6] Eliminando archivos temporales de PyInstaller...
if exist TechManager.spec del /q TechManager.spec
if exist version_info.txt del /q version_info.txt
echo   OK - Archivos temporales eliminados

echo.
echo [4/6] Verificando crear_tablas.py...
findstr /n "def crear_usuario_admin_inicial" base_datos\crear_tablas.py
if %ERRORLEVEL% EQU 0 (
    echo   ERROR - La funcion crear_usuario_admin_inicial EXISTE
    echo   El archivo NO fue reemplazado correctamente
    pause
    exit /b 1
) else (
    echo   OK - La funcion NO existe
)

echo.
echo [5/6] Compilando desde CERO...
python build_installer.py
if %ERRORLEVEL% NEQ 0 (
    echo   ERROR en la compilacion
    pause
    exit /b 1
)

echo.
echo [6/6] Verificacion final...
if exist "dist\TechManager.exe" (
    echo   OK - Ejecutable creado
) else (
    echo   ERROR - No se creo el ejecutable
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo COMPILACION COMPLETA - LISTA PARA INSTALAR
echo ====================================================================
echo.
echo Ahora:
echo 1. Desinstala TechManager
echo 2. Borra: C:\Program Files\TechManager
echo 3. Instala la nueva version
echo.
pause
