# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE AUDITORÍA
============================================================================
Lógica de negocio para consulta de auditoría
(La escritura se hace desde sistema_base.seguridad)
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloAuditoria:
    """Clase para manejar la consulta de auditoría"""
    
    @staticmethod
    def listar_auditoria(filtro_modulo="", filtro_accion="", filtro_usuario="",
                        fecha_desde=None, fecha_hasta=None, busqueda="",
                        solo_criticas=False, limite=100):
        """
        Lista registros de auditoría con filtros
        
        Args:
            filtro_modulo (str): Filtrar por módulo
            filtro_accion (str): Filtrar por acción
            filtro_usuario (int): Filtrar por usuario
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            busqueda (str): Buscar en motivo, campo
            solo_criticas (bool): Solo acciones críticas
            limite (int): Cantidad máxima de registros
            
        Returns:
            list: Lista de registros de auditoría
        """
        try:
            consulta = """
            SELECT 
                a.*,
                u.nombre as usuario_nombre,
                u.username
            FROM auditoria a
            LEFT JOIN usuarios u ON a.id_usuario = u.id_usuario
            WHERE 1=1
            """
            
            parametros = []
            
            if filtro_modulo:
                consulta += " AND a.modulo = ?"
                parametros.append(filtro_modulo)
            
            if filtro_accion:
                consulta += " AND a.accion = ?"
                parametros.append(filtro_accion)
            
            if filtro_usuario:
                consulta += " AND a.id_usuario = ?"
                parametros.append(filtro_usuario)
            
            if fecha_desde:
                consulta += " AND a.fecha_hora >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                consulta += " AND a.fecha_hora <= ?"
                parametros.append(fecha_hasta)
            
            if busqueda:
                consulta += """ AND (
                    a.motivo LIKE ? OR
                    a.campo_modificado LIKE ? OR
                    a.modulo LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 3)
            
            if solo_criticas:
                consulta += " AND a.es_critica = 1"
            
            consulta += " ORDER BY a.fecha_hora DESC LIMIT ?"
            parametros.append(limite)
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar auditoría: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_auditoria_por_registro(modulo, id_registro, limite=50):
        """
        Obtiene el historial de auditoría de un registro específico
        
        Args:
            modulo (str): Módulo
            id_registro (int): ID del registro
            limite (int): Cantidad máxima
            
        Returns:
            list: Historial del registro
        """
        try:
            consulta = """
            SELECT 
                a.*,
                u.nombre as usuario_nombre
            FROM auditoria a
            LEFT JOIN usuarios u ON a.id_usuario = u.id_usuario
            WHERE a.modulo = ? AND a.id_registro = ?
            ORDER BY a.fecha_hora DESC
            LIMIT ?
            """
            
            return db.obtener_todos(consulta, (modulo, id_registro, limite))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener auditoría por registro: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_auditoria_por_usuario(id_usuario, limite=100):
        """
        Obtiene las acciones de un usuario
        
        Args:
            id_usuario (int): ID del usuario
            limite (int): Cantidad máxima
            
        Returns:
            list: Acciones del usuario
        """
        try:
            consulta = """
            SELECT *
            FROM auditoria
            WHERE id_usuario = ?
            ORDER BY fecha_hora DESC
            LIMIT ?
            """
            
            return db.obtener_todos(consulta, (id_usuario, limite))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener auditoría por usuario: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_modulos_disponibles():
        """
        Obtiene la lista de módulos que tienen registros de auditoría
        
        Returns:
            list: Lista de módulos
        """
        try:
            consulta = "SELECT DISTINCT modulo FROM auditoria ORDER BY modulo"
            resultados = db.obtener_todos(consulta)
            
            return [r['modulo'] for r in resultados]
            
        except Exception as e:
            config.guardar_log(f"Error al obtener módulos disponibles: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_acciones_disponibles():
        """
        Obtiene la lista de acciones registradas
        
        Returns:
            list: Lista de acciones
        """
        try:
            consulta = "SELECT DISTINCT accion FROM auditoria ORDER BY accion"
            resultados = db.obtener_todos(consulta)
            
            return [r['accion'] for r in resultados]
            
        except Exception as e:
            config.guardar_log(f"Error al obtener acciones disponibles: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_estadisticas_auditoria(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de auditoría
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            where_fecha = ""
            parametros = []
            
            if fecha_desde:
                where_fecha += " AND fecha_hora >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                where_fecha += " AND fecha_hora <= ?"
                parametros.append(fecha_hasta)
            
            # Total de acciones
            consulta = f"SELECT COUNT(*) as total FROM auditoria WHERE 1=1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['total_acciones'] = resultado['total'] if resultado else 0
            
            # Acciones críticas
            consulta = f"SELECT COUNT(*) as total FROM auditoria WHERE es_critica = 1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['acciones_criticas'] = resultado['total'] if resultado else 0
            
            # Por módulo (top 5)
            consulta = f"""
            SELECT modulo, COUNT(*) as total 
            FROM auditoria 
            WHERE 1=1 {where_fecha}
            GROUP BY modulo 
            ORDER BY total DESC 
            LIMIT 5
            """
            resultados = db.obtener_todos(consulta, tuple(parametros))
            estadisticas['por_modulo'] = {r['modulo']: r['total'] for r in resultados}
            
            # Por acción
            consulta = f"""
            SELECT accion, COUNT(*) as total 
            FROM auditoria 
            WHERE 1=1 {where_fecha}
            GROUP BY accion 
            ORDER BY total DESC
            """
            resultados = db.obtener_todos(consulta, tuple(parametros))
            estadisticas['por_accion'] = {r['accion']: r['total'] for r in resultados}
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de auditoría: {e}", "ERROR")
            return {'total_acciones': 0, 'acciones_criticas': 0}
