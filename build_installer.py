# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - SCRIPT DE COMPILACIÓN COMPLETO
============================================================================
Genera ejecutable + instalador profesional con wizard
============================================================================
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess


def print_step(step, total, message):
    """Imprime paso formateado"""
    print(f"\n[{step}/{total}] {message}")


def limpiar_todo():
    """Elimina todas las compilaciones anteriores"""
    print_step(1, 8, "Limpiando compilaciones previas...")
    
    directorios_limpiar = ['build', 'dist', 'instalador', 'TechManager_v1.0']
    archivos_limpiar = ['TechManager.spec', 'version_info.txt']
    
    for directorio in directorios_limpiar:
        if os.path.exists(directorio):
            shutil.rmtree(directorio)
            print(f"  ✓ Eliminado: {directorio}/")
    
    for archivo in archivos_limpiar:
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"  ✓ Eliminado: {archivo}")
    
    print("  ✓ Limpieza completada")


def verificar_herramientas():
    """Verifica que las herramientas necesarias estén instaladas"""
    print_step(2, 8, "Verificando herramientas...")
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("  ✗ PyInstaller no está instalado")
        print("\n  Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("  ✓ PyInstaller instalado")
    
    # Verificar Pillow (para generar icono)
    try:
        import PIL
        print(f"  ✓ Pillow encontrado")
    except ImportError:
        print("  ✗ Pillow no está instalado")
        print("\n  Instalando Pillow...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
        print("  ✓ Pillow instalado")
    
    # Verificar Inno Setup (opcional, manual)
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    inno_found = False
    for path in inno_paths:
        if os.path.exists(path):
            print(f"  ✓ Inno Setup encontrado: {path}")
            inno_found = True
            break
    
    if not inno_found:
        print("  ⚠ Inno Setup NO encontrado")
        print("    Para crear el instalador con wizard, descargue Inno Setup:")
        print("    https://jrsoftware.org/isdl.php")
        print("    (El ejecutable .exe se creará de todos modos)")
    
    return inno_found


def generar_recursos():
    """Genera icono y otros recursos"""
    print_step(3, 8, "Generando recursos gráficos...")
    
    try:
        # Importar PIL
        from PIL import Image, ImageDraw
        
        # Crear directorio si no existe
        os.makedirs('recursos/iconos', exist_ok=True)
        
        tamaños = [16, 32, 48, 64, 128, 256]
        imagenes = []
        
        for tamaño in tamaños:
            # Crear imagen cuadrada
            img = Image.new('RGBA', (tamaño, tamaño), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Fondo azul moderno
            color_azul = (37, 99, 235)
            draw.rectangle([0, 0, tamaño, tamaño], fill=color_azul)
            
            # Detalles blancos
            if tamaño >= 32:
                margen = max(2, int(tamaño * 0.2))
                draw.rectangle(
                    [margen, margen, tamaño - margen, tamaño - margen],
                    fill=(255, 255, 255)
                )
                
                if tamaño >= 48:
                    grosor = max(2, int(tamaño * 0.08))
                    draw.rectangle(
                        [tamaño // 2 - grosor, margen, tamaño // 2 + grosor, tamaño - margen],
                        fill=color_azul
                    )
            
            imagenes.append(img)
        
        # Guardar como .ico
        ruta_icono = 'recursos/iconos/techmanager.ico'
        imagenes[0].save(
            ruta_icono,
            format='ICO',
            sizes=[(img.width, img.height) for img in imagenes]
        )
        
        print(f"  ✓ Icono generado: {ruta_icono}")
        return ruta_icono
        
    except Exception as e:
        print(f"  ⚠ Error al generar icono: {e}")
        return None


def crear_archivo_version():
    """Crea archivo de versión para Windows"""
    print_step(4, 8, "Creando información de versión...")
    
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'TechManager'),
        StringStruct(u'FileDescription', u'Sistema de Gestión para Servicio Técnico'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'TechManager'),
        StringStruct(u'LegalCopyright', u'© 2025 TechManager'),
        StringStruct(u'OriginalFilename', u'TechManager.exe'),
        StringStruct(u'ProductName', u'TechManager'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("  ✓ Archivo de versión creado")
    return 'version_info.txt'


def compilar_ejecutable(ruta_icono, archivo_version):
    """Compila el ejecutable con PyInstaller"""
    print_step(5, 8, "Compilando ejecutable...")
    print("  ⏳ Esto puede tardar 5-10 minutos...")
    
    comando = [
        'pyinstaller',
        '--name=TechManager',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
    ]
    
    if ruta_icono and os.path.exists(ruta_icono):
        comando.append(f'--icon={ruta_icono}')
    
    if archivo_version and os.path.exists(archivo_version):
        comando.append(f'--version-file={archivo_version}')
    
    # Directorios a incluir
    directorios = [
        ('interfaz', 'interfaz'),
        ('base_datos', 'base_datos'),
        ('modulos', 'modulos'),
        ('sistema_base', 'sistema_base'),
        ('recursos', 'recursos'),
    ]
    
    for origen, destino in directorios:
        if os.path.exists(origen):
            comando.append(f'--add-data={origen}{os.pathsep}{destino}')
    
    # Hidden imports
    hidden_imports = [
        'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'PIL', 'PIL.Image', 'bcrypt', 'reportlab', 'openpyxl', 'sqlite3',
    ]
    
    for modulo in hidden_imports:
        comando.append(f'--hidden-import={modulo}')
    
    comando.append('main.py')
    
    print(f"\n  📦 Ejecutando PyInstaller...\n")
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print("  ✓ Compilación exitosa!")
        
        # Verificar tamaño
        exe_path = Path('dist') / 'TechManager.exe'
        if exe_path.exists():
            tamaño_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"  📊 Tamaño: {tamaño_mb:.2f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error en la compilación:")
        if e.stderr:
            print(e.stderr)
        return False


def preparar_archivos_instalador():
    """Prepara archivos necesarios para el instalador"""
    print_step(6, 8, "Preparando archivos para instalador...")
    
    # Verificar que existe el ejecutable
    exe_origen = Path('dist') / 'TechManager.exe'
    if not exe_origen.exists():
        print("  ✗ No se encontró TechManager.exe")
        return False
    
    print("  ✓ Ejecutable encontrado")
    
    # Verificar archivos necesarios
    archivos_necesarios = [
        'installer.iss',
        'LICENSE.txt',
        'ANTES_DE_INSTALAR.txt',
        'DESPUES_DE_INSTALAR.txt'
    ]
    
    todos_existen = True
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            print(f"  ✓ {archivo}")
        else:
            print(f"  ⚠ Falta: {archivo}")
            todos_existen = False
    
    return todos_existen


def compilar_instalador():
    """Compila el instalador con Inno Setup"""
    print_step(7, 8, "Compilando instalador con Inno Setup...")
    
    # Buscar Inno Setup
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    iscc_exe = None
    for path in inno_paths:
        if os.path.exists(path):
            iscc_exe = path
            break
    
    if not iscc_exe:
        print("  ⚠ Inno Setup no está instalado")
        print("  ℹ Descargue desde: https://jrsoftware.org/isdl.php")
        print("  ℹ Después de instalar, ejecute este script nuevamente")
        return False
    
    print(f"  ✓ Usando: {iscc_exe}")
    
    # Compilar instalador
    try:
        print("  ⏳ Compilando instalador...")
        resultado = subprocess.run(
            [iscc_exe, 'installer.iss'],
            check=True,
            capture_output=True,
            text=True
        )
        print("  ✓ Instalador compilado exitosamente!")
        
        # Verificar resultado
        instalador_path = Path('instalador') / 'TechManager_v1.0_Installer.exe'
        if instalador_path.exists():
            tamaño_mb = instalador_path.stat().st_size / (1024 * 1024)
            print(f"  📊 Tamaño: {tamaño_mb:.2f} MB")
            return True
        else:
            print("  ⚠ No se encontró el instalador generado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error al compilar instalador:")
        if e.stderr:
            print(e.stderr)
        return False


def crear_paquete_final():
    """Crea el paquete final de distribución"""
    print_step(8, 8, "Creando paquete de distribución...")
    
    # Crear carpeta de distribución
    carpeta_dist = Path('TechManager_v1.0_Final')
    if carpeta_dist.exists():
        shutil.rmtree(carpeta_dist)
    carpeta_dist.mkdir()
    
    # Copiar instalador si existe
    instalador_origen = Path('instalador') / 'TechManager_v1.0_Installer.exe'
    if instalador_origen.exists():
        shutil.copy2(instalador_origen, carpeta_dist / 'TechManager_v1.0_Installer.exe')
        print("  ✓ Instalador copiado")
    
    # Copiar ejecutable standalone
    exe_origen = Path('dist') / 'TechManager.exe'
    if exe_origen.exists():
        shutil.copy2(exe_origen, carpeta_dist / 'TechManager_Portable.exe')
        print("  ✓ Ejecutable portable copiado")
    
    # Crear README
    readme = """╔══════════════════════════════════════════════════════════════════════╗
║                     TECHMANAGER v1.0                                 ║
║          Sistema de Gestión para Servicio Técnico                    ║
╚══════════════════════════════════════════════════════════════════════╝

CONTENIDO:
══════════
1. TechManager_v1.0_Installer.exe (RECOMENDADO)
   - Instalador con wizard profesional
   - Crea accesos directos automáticamente
   - Incluye desinstalador

2. TechManager_Portable.exe (ALTERNATIVO)
   - Ejecutable sin instalación
   - Portátil (USB)

CREDENCIALES POR DEFECTO:
══════════════════════════
Usuario: admin
Contraseña: admin123

© 2025 TechManager
"""
    
    with open(carpeta_dist / 'LEEME.txt', 'w', encoding='utf-8') as f:
        f.write(readme)
    print("  ✓ Archivo LEEME.txt creado")
    
    return carpeta_dist


def main():
    """Función principal"""
    print("=" * 70)
    print("TECHMANAGER v1.0 - COMPILADOR COMPLETO")
    print("=" * 70)
    
    if not os.path.exists('main.py'):
        print("\n✗ Error: No se encontró main.py")
        return
    
    limpiar_todo()
    inno_disponible = verificar_herramientas()
    ruta_icono = generar_recursos()
    archivo_version = crear_archivo_version()
    
    if not compilar_ejecutable(ruta_icono, archivo_version):
        print("\n✗ La compilación del ejecutable falló")
        return
    
    archivos_ok = preparar_archivos_instalador()
    
    if inno_disponible and archivos_ok:
        instalador_ok = compilar_instalador()
    else:
        instalador_ok = False
    
    carpeta_final = crear_paquete_final()
    
    print("\n" + "=" * 70)
    print("✓ COMPILACIÓN COMPLETADA")
    print("=" * 70)
    print(f"\n📦 Archivos en: {carpeta_final}/\n")
    
    if instalador_ok:
        print("✓ Instalador: TechManager_v1.0_Installer.exe (RECOMENDADO)\n")
    
    print("✓ Portable: TechManager_Portable.exe\n")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Cancelado")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
