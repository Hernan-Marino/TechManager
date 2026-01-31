# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE BACKUPS
============================================================================
Lógica de negocio para gestión de copias de seguridad
============================================================================
"""

import os
import shutil
from datetime import datetime
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloBackups:
    """Clase para manejar la lógica de negocio de backups"""
    
    @staticmethod
    def crear_backup(tipo_backup="Manual", observaciones="", id_usuario=None):
        """
        Crea un backup de la base de datos
        
        Args:
            tipo_backup (str): 'Manual' o 'Automático'
            observaciones (str): Observaciones
            id_usuario (int): ID del usuario (si es manual)
            
        Returns:
            tuple: (exito, mensaje, ruta_backup)
        """
        try:
            # Crear carpeta de backups si no existe
            carpeta_backups = os.path.join(config.directorio_base, "backups")
            if not os.path.exists(carpeta_backups):
                os.makedirs(carpeta_backups)
            
            # Generar nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"backup_{timestamp}.db"
            ruta_backup = os.path.join(carpeta_backups, nombre_archivo)
            
            # Obtener ruta de la base de datos
            ruta_bd = os.path.join(config.directorio_base, "datos", "techmanager.db")
            
            # Copiar base de datos
            shutil.copy2(ruta_bd, ruta_backup)
            
            # Obtener tamaño del archivo
            tamanio = os.path.getsize(ruta_backup)
            
            # Registrar backup en BD
            consulta = """
            INSERT INTO backups (
                nombre_archivo, ruta_completa, tamanio_bytes,
                tipo_backup, observaciones, fecha_hora_backup,
                id_usuario_genera
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            id_backup = db.ejecutar_consulta(
                consulta,
                (nombre_archivo, ruta_backup, tamanio, tipo_backup,
                 observaciones, datetime.now(), id_usuario if id_usuario else None)
            )
            
            # Registrar en auditoría si es manual
            if tipo_backup == "Manual" and id_usuario:
                from sistema_base.seguridad import registrar_accion_auditoria
                registrar_accion_auditoria(
                    id_usuario=id_usuario,
                    accion="Crear",
                    modulo="Backups",
                    id_registro=id_backup,
                    motivo=f"Backup manual creado: {nombre_archivo}"
                )
            
            config.guardar_log(f"Backup creado: {nombre_archivo} ({tamanio} bytes)", "INFO")
            return True, f"Backup creado exitosamente: {nombre_archivo}", ruta_backup
            
        except Exception as e:
            config.guardar_log(f"Error al crear backup: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_backups(limite=50):
        """
        Lista todos los backups
        
        Args:
            limite (int): Cantidad máxima de registros
            
        Returns:
            list: Lista de backups
        """
        try:
            consulta = """
            SELECT 
                b.*,
                u.nombre as usuario_nombre
            FROM backups b
            LEFT JOIN usuarios u ON b.id_usuario_genera = u.id_usuario
            ORDER BY b.fecha_hora_backup DESC
            LIMIT ?
            """
            
            backups = db.obtener_todos(consulta, (limite,))
            
            # Verificar que los archivos existan
            for backup in backups:
                backup['existe'] = os.path.exists(backup['ruta_completa'])
            
            return backups
            
        except Exception as e:
            config.guardar_log(f"Error al listar backups: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_backup_por_id(id_backup):
        """
        Obtiene un backup por su ID
        
        Args:
            id_backup (int): ID del backup
            
        Returns:
            dict: Datos del backup o None
        """
        try:
            consulta = """
            SELECT 
                b.*,
                u.nombre as usuario_nombre
            FROM backups b
            LEFT JOIN usuarios u ON b.id_usuario_genera = u.id_usuario
            WHERE b.id_backup = ?
            """
            
            backup = db.obtener_uno(consulta, (id_backup,))
            
            if backup:
                backup['existe'] = os.path.exists(backup['ruta_completa'])
            
            return backup
            
        except Exception as e:
            config.guardar_log(f"Error al obtener backup: {e}", "ERROR")
            return None
    
    @staticmethod
    def restaurar_backup(id_backup, id_usuario):
        """
        Restaura un backup
        
        Args:
            id_backup (int): ID del backup
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Solo admin puede restaurar
            if not config.es_admin:
                return False, "Solo administradores pueden restaurar backups"
            
            backup = ModuloBackups.obtener_backup_por_id(id_backup)
            
            if not backup:
                return False, "Backup no encontrado"
            
            if not backup['existe']:
                return False, "El archivo de backup no existe"
            
            # IMPORTANTE: Crear un backup antes de restaurar
            ModuloBackups.crear_backup(
                "Automático",
                "Backup automático antes de restaurar",
                id_usuario
            )
            
            # Obtener ruta de la base de datos actual
            ruta_bd = os.path.join(config.directorio_base, "datos", "techmanager.db")
            
            # Cerrar conexión a la BD
            db.cerrar()
            
            # Restaurar (copiar backup sobre la BD actual)
            shutil.copy2(backup['ruta_completa'], ruta_bd)
            
            # Reconectar a la BD
            db.conectar()
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Restaurar",
                modulo="Backups",
                id_registro=id_backup,
                motivo=f"Backup restaurado: {backup['nombre_archivo']}",
                es_critica=True
            )
            
            config.guardar_log(f"Backup restaurado: {backup['nombre_archivo']}", "WARNING")
            return True, "Backup restaurado exitosamente. Reinicie la aplicación."
            
        except Exception as e:
            config.guardar_log(f"Error al restaurar backup: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def eliminar_backup(id_backup, id_usuario):
        """
        Elimina un backup
        
        Args:
            id_backup (int): ID del backup
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Solo admin
            if not config.es_admin:
                return False, "Solo administradores pueden eliminar backups"
            
            backup = ModuloBackups.obtener_backup_por_id(id_backup)
            
            if not backup:
                return False, "Backup no encontrado"
            
            # Eliminar archivo si existe
            if backup['existe']:
                os.remove(backup['ruta_completa'])
            
            # Eliminar registro de BD
            consulta = "DELETE FROM backups WHERE id_backup = ?"
            db.ejecutar_consulta(consulta, (id_backup,))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Eliminar",
                modulo="Backups",
                id_registro=id_backup,
                motivo=f"Backup eliminado: {backup['nombre_archivo']}"
            )
            
            config.guardar_log(f"Backup eliminado: {backup['nombre_archivo']}", "INFO")
            return True, "Backup eliminado"
            
        except Exception as e:
            config.guardar_log(f"Error al eliminar backup: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def limpiar_backups_antiguos(dias_antiguedad=90):
        """
        Elimina backups automáticos más antiguos que X días
        
        Args:
            dias_antiguedad (int): Días de antiguedad
            
        Returns:
            int: Cantidad de backups eliminados
        """
        try:
            from datetime import timedelta
            fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)
            
            # Buscar backups automáticos antiguos
            consulta = """
            SELECT id_backup, nombre_archivo, ruta_completa
            FROM backups
            WHERE tipo_backup = 'Automático'
            AND fecha_hora_backup < ?
            """
            
            backups_antiguos = db.obtener_todos(consulta, (fecha_limite,))
            
            for backup in backups_antiguos:
                # Eliminar archivo
                if os.path.exists(backup['ruta_completa']):
                    os.remove(backup['ruta_completa'])
                
                # Eliminar registro
                consulta_delete = "DELETE FROM backups WHERE id_backup = ?"
                db.ejecutar_consulta(consulta_delete, (backup['id_backup'],))
            
            if len(backups_antiguos) > 0:
                config.guardar_log(f"{len(backups_antiguos)} backups antiguos eliminados", "INFO")
            
            return len(backups_antiguos)
            
        except Exception as e:
            config.guardar_log(f"Error al limpiar backups antiguos: {e}", "ERROR")
            return 0
    
    @staticmethod
    def obtener_estadisticas_backups():
        """
        Obtiene estadísticas de backups
        
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            # Total de backups
            consulta = "SELECT COUNT(*) as total FROM backups"
            resultado = db.obtener_uno(consulta)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Por tipo
            consulta = "SELECT COUNT(*) as total FROM backups WHERE tipo_backup = 'Manual'"
            resultado = db.obtener_uno(consulta)
            estadisticas['manuales'] = resultado['total'] if resultado else 0
            
            consulta = "SELECT COUNT(*) as total FROM backups WHERE tipo_backup = 'Automático'"
            resultado = db.obtener_uno(consulta)
            estadisticas['automaticos'] = resultado['total'] if resultado else 0
            
            # Tamaño total
            consulta = "SELECT SUM(tamanio_bytes) as total FROM backups"
            resultado = db.obtener_uno(consulta)
            estadisticas['tamanio_total'] = resultado['total'] if resultado and resultado['total'] else 0
            
            # Último backup
            consulta = """
            SELECT fecha_hora_backup 
            FROM backups 
            ORDER BY fecha_hora_backup DESC 
            LIMIT 1
            """
            resultado = db.obtener_uno(consulta)
            estadisticas['ultimo_backup'] = resultado['fecha_hora_backup'] if resultado else None
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de backups: {e}", "ERROR")
            return {'total': 0}
