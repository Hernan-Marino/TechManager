# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO LÓGICA DE REPORTES
============================================================================
Lógica de negocio para generación de reportes y estadísticas
============================================================================
"""

from sistema_base.base_datos import BaseDatos
from datetime import datetime, timedelta


class ModuloReportes:
    """Módulo de lógica para reportes y estadísticas"""
    
    @staticmethod
    def obtener_resumen_general(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene resumen general del negocio
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            dict: Diccionario con estadísticas generales
        """
        try:
            db = BaseDatos()
            
            # Construir filtro de fechas
            filtro_fecha = ""
            params = []
            
            if fecha_desde and fecha_hasta:
                filtro_fecha = " WHERE fecha_ingreso BETWEEN ? AND ?"
                params = [fecha_desde, fecha_hasta]
            
            # Equipos ingresados
            query_equipos = f"SELECT COUNT(*) FROM equipos{filtro_fecha}"
            equipos_ingresados = db.ejecutar_query(query_equipos, params)[0][0]
            
            # Órdenes finalizadas
            filtro_ordenes = filtro_fecha.replace("fecha_ingreso", "fecha_inicio") if filtro_fecha else ""
            query_ordenes = f"""
                SELECT COUNT(*) FROM ordenes_trabajo 
                WHERE estado_orden LIKE 'Finalizada%' {' AND ' + filtro_ordenes.replace('WHERE ', '') if filtro_ordenes else ''}
            """
            ordenes_finalizadas = db.ejecutar_query(query_ordenes, params if filtro_ordenes else [])[0][0]
            
            # Ingresos totales (facturas cobradas)
            filtro_facturas = filtro_fecha.replace("fecha_ingreso", "fecha_emision") if filtro_fecha else ""
            query_ingresos = f"""
                SELECT COALESCE(SUM(monto_total), 0) FROM facturas 
                WHERE estado_pago IN ('Pagado', 'Pago Parcial') {' AND ' + filtro_facturas.replace('WHERE ', '') if filtro_facturas else ''}
            """
            ingresos_totales = db.ejecutar_query(query_ingresos, params if filtro_facturas else [])[0][0]
            
            # Clientes nuevos
            filtro_clientes = filtro_fecha.replace("fecha_ingreso", "fecha_registro") if filtro_fecha else ""
            query_clientes = f"SELECT COUNT(*) FROM clientes{filtro_clientes}"
            clientes_nuevos = db.ejecutar_query(query_clientes, params if filtro_clientes else [])[0][0]
            
            return {
                'equipos_ingresados': equipos_ingresados,
                'ordenes_finalizadas': ordenes_finalizadas,
                'ingresos_totales': float(ingresos_totales),
                'clientes_nuevos': clientes_nuevos
            }
            
        except Exception as e:
            print(f"Error al obtener resumen general: {e}")
            return {
                'equipos_ingresados': 0,
                'ordenes_finalizadas': 0,
                'ingresos_totales': 0.0,
                'clientes_nuevos': 0
            }
    
    @staticmethod
    def obtener_estadisticas_ingresos(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de ingresos
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            dict: Diccionario con estadísticas de ingresos
        """
        try:
            db = BaseDatos()
            
            # Construir filtro de fechas
            filtro_fecha = ""
            params = []
            
            if fecha_desde and fecha_hasta:
                filtro_fecha = " WHERE fecha_emision BETWEEN ? AND ?"
                params = [fecha_desde, fecha_hasta]
            
            # Facturas cobradas
            query_cobradas = f"""
                SELECT COUNT(*) FROM facturas 
                WHERE estado_pago = 'Pagado' {' AND ' + filtro_fecha.replace('WHERE ', '') if filtro_fecha else ''}
            """
            facturas_cobradas = db.ejecutar_query(query_cobradas, params if filtro_fecha else [])[0][0]
            
            # Monto cobrado
            query_monto = f"""
                SELECT COALESCE(SUM(monto_total), 0) FROM facturas 
                WHERE estado_pago = 'Pagado' {' AND ' + filtro_fecha.replace('WHERE ', '') if filtro_fecha else ''}
            """
            monto_cobrado = db.ejecutar_query(query_monto, params if filtro_fecha else [])[0][0]
            
            # Pendiente de cobro
            query_pendiente = f"""
                SELECT COALESCE(SUM(monto_total - monto_cobrado), 0) FROM facturas 
                WHERE estado_pago IN ('Pendiente', 'Pago Parcial') {' AND ' + filtro_fecha.replace('WHERE ', '') if filtro_fecha else ''}
            """
            pendiente_cobro = db.ejecutar_query(query_pendiente, params if filtro_fecha else [])[0][0]
            
            return {
                'facturas_cobradas': facturas_cobradas,
                'monto_cobrado': float(monto_cobrado),
                'pendiente_cobro': float(pendiente_cobro)
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas de ingresos: {e}")
            return {
                'facturas_cobradas': 0,
                'monto_cobrado': 0.0,
                'pendiente_cobro': 0.0
            }
    
    @staticmethod
    def obtener_estadisticas_equipos(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de equipos
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            dict: Diccionario con estadísticas de equipos
        """
        try:
            db = BaseDatos()
            
            # Construir filtro de fechas
            filtro_fecha = ""
            params = []
            
            if fecha_desde and fecha_hasta:
                filtro_fecha = " AND e.fecha_ingreso BETWEEN ? AND ?"
                params = [fecha_desde, fecha_hasta]
            
            # Equipos reparados
            query_reparados = f"""
                SELECT COUNT(DISTINCT e.id_equipo) FROM equipos e
                JOIN ordenes_trabajo o ON e.id_equipo = o.id_equipo
                WHERE o.estado_orden = 'Finalizada con reparación' {filtro_fecha}
            """
            equipos_reparados = db.ejecutar_query(query_reparados, params if filtro_fecha else [])[0][0]
            
            # Equipos sin reparación
            query_sin_reparacion = f"""
                SELECT COUNT(DISTINCT e.id_equipo) FROM equipos e
                JOIN ordenes_trabajo o ON e.id_equipo = o.id_equipo
                WHERE o.estado_orden = 'Finalizada sin reparación' {filtro_fecha}
            """
            equipos_sin_reparacion = db.ejecutar_query(query_sin_reparacion, params if filtro_fecha else [])[0][0]
            
            # Equipos en curso
            query_en_curso = f"""
                SELECT COUNT(DISTINCT e.id_equipo) FROM equipos e
                JOIN ordenes_trabajo o ON e.id_equipo = o.id_equipo
                WHERE o.estado_orden IN ('En diagnóstico', 'En reparación', 'Esperando repuesto') {filtro_fecha}
            """
            equipos_en_curso = db.ejecutar_query(query_en_curso, params if filtro_fecha else [])[0][0]
            
            return {
                'equipos_reparados': equipos_reparados,
                'equipos_sin_reparacion': equipos_sin_reparacion,
                'equipos_en_curso': equipos_en_curso
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas de equipos: {e}")
            return {
                'equipos_reparados': 0,
                'equipos_sin_reparacion': 0,
                'equipos_en_curso': 0
            }
    
    @staticmethod
    def obtener_estadisticas_clientes(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de clientes
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            dict: Diccionario con estadísticas de clientes
        """
        try:
            db = BaseDatos()
            
            # Total clientes
            query_total = "SELECT COUNT(*) FROM clientes"
            total_clientes = db.ejecutar_query(query_total)[0][0]
            
            # Clientes activos (con equipos ingresados en el período)
            if fecha_desde and fecha_hasta:
                query_activos = """
                    SELECT COUNT(DISTINCT e.id_cliente) FROM equipos e
                    WHERE e.fecha_ingreso BETWEEN ? AND ?
                """
                clientes_activos = db.ejecutar_query(query_activos, [fecha_desde, fecha_hasta])[0][0]
            else:
                clientes_activos = total_clientes
            
            # Clientes incobrables
            query_incobrables = "SELECT COUNT(*) FROM clientes WHERE es_incobrable = 1"
            clientes_incobrables = db.ejecutar_query(query_incobrables)[0][0]
            
            return {
                'total_clientes': total_clientes,
                'clientes_activos': clientes_activos,
                'clientes_incobrables': clientes_incobrables
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas de clientes: {e}")
            return {
                'total_clientes': 0,
                'clientes_activos': 0,
                'clientes_incobrables': 0
            }
