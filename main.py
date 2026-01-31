#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - Sistema de Gestión para Servicio Técnico
============================================================================
Punto de entrada principal del sistema

Autor: TechManager Development Team
Fecha: 2025
============================================================================
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path de Python
sys.path.insert(0, str(Path(__file__).parent))

def verificar_dependencias():
    """
    Verifica que todas las dependencias necesarias estén instaladas
    """
    dependencias_faltantes = []
    
    try:
        from PyQt5 import QtWidgets
    except ImportError:
        dependencias_faltantes.append("PyQt5")
    
    try:
        from PIL import Image
    except ImportError:
        dependencias_faltantes.append("Pillow")
    
    try:
        import bcrypt
    except ImportError:
        dependencias_faltantes.append("bcrypt")
    
    if dependencias_faltantes:
        print("=" * 70)
        print("ERROR: Faltan dependencias necesarias")
        print("=" * 70)
        print("\nDependencias faltantes:")
        for dep in dependencias_faltantes:
            print(f"  - {dep}")
        print("\nPara instalar todas las dependencias, ejecute:")
        print("  pip install -r requirements.txt")
        print("=" * 70)
        sys.exit(1)


def crear_directorios_necesarios():
    """
    Crea los directorios necesarios si no existen
    """
    directorios = [
        'datos',
        'datos/backups',
        'datos/exportaciones',
        'datos/temporal',
        'logs',
        'recursos/imagenes',
        'recursos/fuentes'
    ]
    
    for directorio in directorios:
        ruta = Path(__file__).parent / directorio
        ruta.mkdir(parents=True, exist_ok=True)


def main():
    """
    Función principal que inicia el sistema
    """
    print("=" * 70)
    print("TECHMANAGER v1.0 - Sistema de Gestión para Servicio Técnico")
    print("=" * 70)
    print("\nIniciando sistema...")
    
    # 1. Verificar dependencias
    print("  [1/4] Verificando dependencias...")
    verificar_dependencias()
    
    # 2. Crear directorios necesarios
    print("  [2/4] Creando directorios necesarios...")
    crear_directorios_necesarios()
    
    # 3. Inicializar base de datos
    print("  [3/4] Inicializando base de datos...")
    from base_datos.crear_tablas import inicializar_base_datos
    inicializar_base_datos()
    
    # 4. Iniciar interfaz gráfica
    print("  [4/4] Iniciando interfaz gráfica...")
    from interfaz.aplicacion import AplicacionPrincipal
    
    app = AplicacionPrincipal()
    app.iniciar()
    
    print("\nSistema cerrado correctamente.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSistema interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR CRÍTICO")
        print("=" * 70)
        print(f"\nOcurrió un error inesperado: {e}")
        print("\nPor favor, contacte con soporte técnico.")
        print("=" * 70)
        
        # Guardar error en log
        import traceback
        log_path = Path(__file__).parent / "logs" / "errores.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"ERROR: {e}\n")
            f.write(traceback.format_exc())
            f.write("=" * 70 + "\n")
        
        sys.exit(1)
