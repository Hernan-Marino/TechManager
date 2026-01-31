# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - CONFIGURACIÓN DEL SISTEMA
============================================================================
Gestión de la configuración global del sistema
============================================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class Configuracion:
    """
    Clase Singleton para gestionar la configuración del sistema
    """
    _instancia = None
    
    def __new__(cls):
        """
        Implementa el patrón Singleton
        Solo puede existir una instancia de Configuracion
        """
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia
    
    def __init__(self):
        """
        Inicializa la configuración
        """
        if self._inicializado:
            return
        
        # Determinar ruta base según si es ejecutable o desarrollo
        if getattr(sys, 'frozen', False):
            # Si es ejecutable compilado con PyInstaller
            self.ruta_base = Path(sys.executable).parent
            
            # Para datos que necesitan escritura, usar AppData
            # Esto evita problemas de permisos en Program Files
            appdata_local = Path(os.getenv('LOCALAPPDATA'))
            self.ruta_datos = appdata_local / "TechManager" / "datos"
            self.ruta_logs = appdata_local / "TechManager" / "logs"
        else:
            # Si es desarrollo (Python directo)
            self.ruta_base = Path(__file__).parent.parent
            self.ruta_datos = self.ruta_base / "datos"
            self.ruta_logs = self.ruta_base / "logs"
        
        # Rutas del sistema (comunes para ambos modos)
        self.ruta_base_datos = self.ruta_datos / "techmanager.db"
        self.ruta_backups = self.ruta_datos / "backups"
        self.ruta_exportaciones = self.ruta_datos / "exportaciones"
        self.ruta_temporal = self.ruta_datos / "temporal"
        self.ruta_recursos = self.ruta_base / "recursos"
        self.ruta_imagenes = self.ruta_recursos / "imagenes"
        
        # Usuario actual (se setea después del login)
        self.usuario_actual = None
        self.es_admin = False
        
        # Configuración de la aplicación (se carga de la BD)
        self.nombre_negocio = "TechManager"
        self.telefono_contacto = ""
        self.direccion = ""
        self.email = ""
        self.color_primario = "#2563eb"
        self.color_secundario = "#64748b"
        self.dias_alerta_equipo = 2
        self.backup_automatico = False
        
        # Logos (se cargan de la BD)
        self.logo_sistema = None
        self.logo_remito = None
        self.logo_comprobante = None
        self.imagen_header = None
        
        # Configuración de backups
        self.ruta_backup_local = str(self.ruta_backups)
        self.backup_nube_activo = False
        self.tipo_backup_nube = "Sin backup en nube"
        
        # Flag de inicialización
        self._inicializado = True
    
    def establecer_usuario(self, usuario, rol):
        """
        Establece el usuario que inició sesión
        
        Args:
            usuario (str): Nombre de usuario
            rol (str): Rol del usuario ('admin' o 'tecnico')
        """
        self.usuario_actual = usuario
        self.es_admin = (rol == 'admin')
    
    def cerrar_sesion(self):
        """
        Cierra la sesión del usuario actual
        """
        self.usuario_actual = None
        self.es_admin = False
    
    def cargar_configuracion_bd(self, datos):
        """
        Carga la configuración desde la base de datos
        
        Args:
            datos (dict): Diccionario con los datos de configuración
        """
        self.nombre_negocio = datos.get('nombre_negocio', self.nombre_negocio)
        self.telefono_contacto = datos.get('telefono_contacto', '')
        self.direccion = datos.get('direccion', '')
        self.email = datos.get('email', '')
        self.color_primario = datos.get('color_primario', self.color_primario)
        self.color_secundario = datos.get('color_secundario', self.color_secundario)
        self.dias_alerta_equipo = datos.get('dias_alerta_equipo', 2)
        self.backup_automatico = datos.get('backup_automatico', False)
        self.ruta_backup_local = datos.get('ruta_backup_local', str(self.ruta_backups))
        self.backup_nube_activo = datos.get('backup_nube_activo', False)
        self.tipo_backup_nube = datos.get('tipo_backup_nube', 'Sin backup en nube')
        
        # Logos (se guardan como BLOB en la BD)
        self.logo_sistema = datos.get('logo_sistema')
        self.logo_remito = datos.get('logo_remito')
        self.logo_comprobante = datos.get('logo_comprobante')
        self.imagen_header = datos.get('imagen_header')
    
    def obtener_ruta_absoluta(self, ruta_relativa):
        """
        Convierte una ruta relativa en absoluta
        
        Args:
            ruta_relativa (str): Ruta relativa
            
        Returns:
            Path: Ruta absoluta
        """
        return self.ruta_base / ruta_relativa
    
    def crear_directorios(self):
        """
        Crea todos los directorios necesarios si no existen
        """
        directorios = [
            self.ruta_datos,
            self.ruta_backups,
            self.ruta_exportaciones,
            self.ruta_temporal,
            self.ruta_logs,
            self.ruta_recursos,
            self.ruta_imagenes
        ]
        
        for directorio in directorios:
            directorio.mkdir(parents=True, exist_ok=True)
    
    def obtener_info_sistema(self):
        """
        Retorna información del sistema para mostrar en la interfaz
        
        Returns:
            dict: Información del sistema
        """
        from sistema_base.constantes import VERSION, NOMBRE_COMPLETO
        
        return {
            'nombre': NOMBRE_COMPLETO,
            'version': VERSION,
            'usuario': self.usuario_actual,
            'rol': 'Administrador' if self.es_admin else 'Técnico',
            'nombre_negocio': self.nombre_negocio
        }
    
    def guardar_log(self, mensaje, tipo='INFO'):
        """
        Guarda un mensaje en el archivo de log
        
        Args:
            mensaje (str): Mensaje a guardar
            tipo (str): Tipo de mensaje (INFO, WARNING, ERROR)
        """
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea_log = f"[{fecha_hora}] [{tipo}] {mensaje}\n"
        
        archivo_log = self.ruta_logs / f"sistema_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        try:
            with open(archivo_log, 'a', encoding='utf-8') as f:
                f.write(linea_log)
        except Exception as e:
            print(f"Error al escribir log: {e}")


# ============================================================================
# Instancia global de configuración (Singleton)
# ============================================================================
config = Configuracion()
