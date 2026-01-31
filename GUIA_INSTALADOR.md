# GUÍA COMPLETA: INSTALADOR PROFESIONAL

## 🎯 OBJETIVO
Crear un instalador con wizard para vender a tus clientes.

## 📋 REQUISITOS (SOLO PARA VOS)

### 1. Python y dependencias
```bash
pip install -r requirements.txt
```

### 2. Inno Setup (para el wizard)
Descargar: https://jrsoftware.org/isdl.php
Instalar: innosetup-6.x.x.exe

## 🚀 COMPILAR (UN COMANDO)

```bash
python build_installer.py
```

Eso es TODO. El script hace automáticamente:
1. Limpia archivos viejos
2. Verifica herramientas
3. Genera icono
4. Compila .exe
5. Crea instalador con wizard
6. Empaqueta todo

## 📦 RESULTADO

`TechManager_v1.0_Final/`
- TechManager_v1.0_Installer.exe ← Dale ESTE a clientes
- TechManager_Portable.exe ← Alternativo
- LEEME.txt

## 👥 PARA TUS CLIENTES

### Reciben:
TechManager_v1.0_Installer.exe

### Hacen:
1. Doble click
2. Siguiente → Siguiente → Instalar
3. ¡Listo!

### NO necesitan:
- Python
- Comandos
- Configuración

## ✨ EL WIZARD INCLUYE

✓ Pantalla bienvenida
✓ Licencia
✓ Selección carpeta
✓ Checkbox escritorio
✓ Barra progreso
✓ Desinstalador automático

## 🎯 RESUMEN

**VOS (una vez):**
1. Instalar Inno Setup
2. python build_installer.py
3. Obtener TechManager_v1.0_Installer.exe

**TUS CLIENTES (siempre):**
1. Doble click instalador
2. Siguiente → Siguiente
3. ¡Funciona!

---
© 2025 TechManager
