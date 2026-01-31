# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE REMITOS
============================================================================
Lógica de negocio para generación y gestión de remitos
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloRemitos:
    """Clase para manejar la lógica de negocio de remitos"""
    
    @staticmethod
    def generar_numero_remito():
        """
        Genera un número único de remito con formato: R-YYYYMMDD-####
        
        Returns:
            str: Número de remito generado
        """
        try:
            fecha_hoy = datetime.now().strftime('%Y%m%d')
            prefijo = f"R-{fecha_hoy}-"
            
            # Buscar el último remito del día
            consulta = """
            SELECT numero_remito 
            FROM remitos 
            WHERE numero_remito LIKE ?
            ORDER BY numero_remito DESC
            LIMIT 1
            """
            
            resultado = db.obtener_uno(consulta, (f"{prefijo}%",))
            
            if resultado:
                # Extraer el número secuencial
                ultimo_numero = resultado['numero_remito']
                secuencial = int(ultimo_numero.split('-')[-1])
                nuevo_secuencial = secuencial + 1
            else:
                # Primer remito del día
                nuevo_secuencial = 1
            
            return f"{prefijo}{nuevo_secuencial:04d}"
            
        except Exception as e:
            config.guardar_log(f"Error al generar número de remito: {e}", "ERROR")
            # Fallback
            return f"R-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    @staticmethod
    def generar_remito(id_equipo, id_usuario):
        """
        Genera un remito para un equipo
        
        Args:
            id_equipo (int): ID del equipo
            id_usuario (int): ID del usuario que genera el remito
            
        Returns:
            tuple: (exito, mensaje, numero_remito)
        """
        try:
            # Obtener datos del equipo
            consulta_equipo = """
            SELECT 
                e.*,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                c.direccion as cliente_direccion
            FROM equipos e
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            WHERE e.id_equipo = ?
            """
            
            equipo = db.obtener_uno(consulta_equipo, (id_equipo,))
            
            if not equipo:
                return False, "Equipo no encontrado", None
            
            # Generar número de remito
            numero_remito = ModuloRemitos.generar_numero_remito()
            
            # Insertar remito
            consulta_insertar = """
            INSERT INTO remitos (
                numero_remito,
                id_equipo,
                id_cliente,
                fecha_hora_generacion,
                id_usuario_genera
            )
            VALUES (?, ?, ?, ?, ?)
            """
            
            db.ejecutar_consulta(
                consulta_insertar,
                (numero_remito, id_equipo, equipo['id_cliente'], 
                 datetime.now(), id_usuario)
            )
            
            config.guardar_log(f"Remito {numero_remito} generado para equipo ID {id_equipo}", "INFO")
            return True, "Remito generado exitosamente", numero_remito
            
        except Exception as e:
            config.guardar_log(f"Error al generar remito: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def obtener_remito_por_numero(numero_remito):
        """
        Obtiene un remito por su número
        
        Args:
            numero_remito (str): Número del remito
            
        Returns:
            dict: Datos completos del remito o None
        """
        try:
            consulta = """
            SELECT 
                r.*,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.identificador,
                e.color,
                e.estado_fisico,
                e.accesorios,
                e.falla_declarada,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                c.direccion as cliente_direccion,
                u.nombre as usuario_nombre
            FROM remitos r
            INNER JOIN equipos e ON r.id_equipo = e.id_equipo
            INNER JOIN clientes c ON r.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON r.id_usuario_genera = u.id_usuario
            WHERE r.numero_remito = ?
            """
            
            return db.obtener_uno(consulta, (numero_remito,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener remito: {e}", "ERROR")
            return None
    
    @staticmethod
    def listar_remitos(busqueda="", orden="fecha_desc", fecha_desde=None, fecha_hasta=None, solo_no_retirados=False):
        """
        Lista todos los remitos
        
        Args:
            busqueda (str): Buscar por número, cliente, equipo
            orden (str): fecha_desc, fecha_asc
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            solo_no_retirados (bool): Solo remitos no retirados
            
        Returns:
            list: Lista de remitos
        """
        try:
            consulta = """
            SELECT 
                r.numero_remito,
                r.fecha_hora_generacion,
                c.nombre as cliente_nombre,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                u.nombre as usuario_nombre
            FROM remitos r
            INNER JOIN equipos e ON r.id_equipo = e.id_equipo
            INNER JOIN clientes c ON r.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON r.id_usuario_genera = u.id_usuario
            WHERE 1=1
            """
            
            parametros = []
            
            if busqueda:
                consulta += """ AND (
                    r.numero_remito LIKE ? OR
                    c.nombre LIKE ? OR
                    e.marca LIKE ? OR
                    e.modelo LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 4)
            
            if fecha_desde:
                consulta += " AND r.fecha_hora_generacion >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                consulta += " AND r.fecha_hora_generacion <= ?"
                parametros.append(fecha_hasta)
            
            if solo_no_retirados:
                consulta += " AND (r.retirado IS NULL OR r.retirado = 0)"
            
            if orden == "fecha_asc":
                consulta += " ORDER BY r.fecha_hora_generacion ASC"
            else:
                consulta += " ORDER BY r.fecha_hora_generacion DESC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar remitos: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_estadisticas_remitos(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de remitos
        
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
                where_fecha += " AND fecha_hora_generacion >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                where_fecha += " AND fecha_hora_generacion <= ?"
                parametros.append(fecha_hasta)
            
            # Total de remitos
            consulta = f"SELECT COUNT(*) as total FROM remitos WHERE 1=1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Remitos del último mes (solo si no hay filtro de fechas)
            if not fecha_desde and not fecha_hasta:
                from datetime import datetime, timedelta
                fecha_mes_atras = datetime.now() - timedelta(days=30)
                consulta = "SELECT COUNT(*) as total FROM remitos WHERE fecha_hora_generacion >= ?"
                resultado = db.obtener_uno(consulta, (fecha_mes_atras,))
                estadisticas['ultimo_mes'] = resultado['total'] if resultado else 0
            else:
                estadisticas['ultimo_mes'] = estadisticas['total']
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de remitos: {e}", "ERROR")
            return {'total': 0, 'ultimo_mes': 0}
