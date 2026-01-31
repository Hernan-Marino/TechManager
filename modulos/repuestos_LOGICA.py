# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE REPUESTOS/INVENTARIO
============================================================================
Lógica de negocio para gestión de inventario de repuestos
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.validadores import validar_requerido
from sistema_base.configuracion import config


class ModuloRepuestos:
    """Clase para manejar la lógica de negocio de repuestos"""
    
    # Tipos de repuestos
    TIPOS_REPUESTOS = [
        "Pantalla",
        "Batería",
        "Placa",
        "Flex",
        "Cámara",
        "Conector",
        "Altavoz",
        "Micrófono",
        "Botón",
        "Teclado",
        "Disco Duro",
        "Memoria RAM",
        "Procesador",
        "Fuente",
        "Otro"
    ]
    
    # Tipos de dispositivos
    TIPOS_DISPOSITIVOS = [
        "Celular",
        "Tablet",
        "PC/Notebook",
        "Consola",
        "Otro"
    ]
    
    # Estados
    ESTADOS_REPUESTO = [
        "Funcionando",
        "Con detalles",
        "Para revisar"
    ]
    
    @staticmethod
    def agregar_repuesto(nombre, tipo_repuesto, tipo_dispositivo, modelos_compatibles,
                        origen, id_equipo_origen, cantidad, estado, precio_referencia,
                        notas, id_usuario):
        """
        Agrega un nuevo repuesto al inventario
        
        Args:
            nombre (str): Nombre del repuesto
            tipo_repuesto (str): Tipo de repuesto
            tipo_dispositivo (str): Tipo de dispositivo
            modelos_compatibles (str): Modelos compatibles
            origen (str): 'Nuevo' o 'Recuperado'
            id_equipo_origen (int): ID del equipo de donde se recuperó (si aplica)
            cantidad (int): Cantidad disponible
            estado (str): Estado del repuesto
            precio_referencia (float): Precio referencia
            notas (str): Notas adicionales
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_repuesto_nuevo)
        """
        try:
            # Validaciones
            es_valido, mensaje = validar_requerido(nombre, "Nombre del repuesto")
            if not es_valido:
                return False, mensaje, None
            
            if tipo_repuesto not in ModuloRepuestos.TIPOS_REPUESTOS:
                return False, "Tipo de repuesto inválido", None
            
            if tipo_dispositivo not in ModuloRepuestos.TIPOS_DISPOSITIVOS:
                return False, "Tipo de dispositivo inválido", None
            
            if estado not in ModuloRepuestos.ESTADOS_REPUESTO:
                return False, "Estado inválido", None
            
            if cantidad <= 0:
                return False, "La cantidad debe ser mayor a cero", None
            
            if origen not in ['Nuevo', 'Recuperado']:
                return False, "El origen debe ser 'Nuevo' o 'Recuperado'", None
            
            # Insertar repuesto
            consulta = """
            INSERT INTO repuestos (
                nombre, tipo_repuesto, tipo_dispositivo, modelos_compatibles,
                origen, id_equipo_origen, cantidad_disponible, estado,
                precio_referencia, notas, fecha_ingreso, id_usuario_ingreso
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            id_nuevo = db.ejecutar_consulta(
                consulta,
                (nombre, tipo_repuesto, tipo_dispositivo, modelos_compatibles,
                 origen, id_equipo_origen if id_equipo_origen else None, cantidad,
                 estado, precio_referencia, notas, datetime.now(), id_usuario)
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Repuestos",
                id_registro=id_nuevo,
                motivo=f"Repuesto agregado: {nombre} ({origen}) x{cantidad}"
            )
            
            config.guardar_log(f"Repuesto ID {id_nuevo} agregado al inventario", "INFO")
            return True, "Repuesto agregado exitosamente", id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al agregar repuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_repuestos(filtro_tipo_repuesto="", filtro_tipo_dispositivo="", 
                        filtro_origen="", filtro_estado="", busqueda="", 
                        solo_con_stock=False):
        """
        Lista todos los repuestos
        
        Args:
            filtro_tipo_repuesto (str): Filtrar por tipo de repuesto
            filtro_tipo_dispositivo (str): Filtrar por tipo de dispositivo
            filtro_origen (str): Filtrar por origen
            filtro_estado (str): Filtrar por estado
            busqueda (str): Buscar en nombre, modelos
            solo_con_stock (bool): Solo mostrar con stock disponible
            
        Returns:
            list: Lista de repuestos
        """
        try:
            consulta = """
            SELECT 
                r.*,
                e.marca as equipo_origen_marca,
                e.modelo as equipo_origen_modelo
            FROM repuestos r
            LEFT JOIN equipos e ON r.id_equipo_origen = e.id_equipo
            WHERE 1=1
            """
            
            parametros = []
            
            # Filtros
            if filtro_tipo_repuesto:
                consulta += " AND r.tipo_repuesto = ?"
                parametros.append(filtro_tipo_repuesto)
            
            if filtro_tipo_dispositivo:
                consulta += " AND r.tipo_dispositivo = ?"
                parametros.append(filtro_tipo_dispositivo)
            
            if filtro_origen:
                consulta += " AND r.origen = ?"
                parametros.append(filtro_origen)
            
            if filtro_estado:
                consulta += " AND r.estado = ?"
                parametros.append(filtro_estado)
            
            if solo_con_stock:
                consulta += " AND r.cantidad_disponible > 0"
            
            if busqueda:
                consulta += """ AND (
                    r.nombre LIKE ? OR
                    r.modelos_compatibles LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param, busqueda_param])
            
            consulta += " ORDER BY r.nombre ASC"
            
            repuestos = db.obtener_todos(consulta, tuple(parametros))
            
            # Marcar stock bajo
            for repuesto in repuestos:
                repuesto['stock_bajo'] = repuesto['cantidad_disponible'] <= config.cantidad_minima_stock_repuestos
            
            return repuestos
            
        except Exception as e:
            config.guardar_log(f"Error al listar repuestos: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_repuesto_por_id(id_repuesto):
        """
        Obtiene un repuesto por su ID
        
        Args:
            id_repuesto (int): ID del repuesto
            
        Returns:
            dict: Datos del repuesto o None
        """
        try:
            consulta = """
            SELECT 
                r.*,
                e.marca as equipo_origen_marca,
                e.modelo as equipo_origen_modelo,
                u.nombre as usuario_ingreso_nombre
            FROM repuestos r
            LEFT JOIN equipos e ON r.id_equipo_origen = e.id_equipo
            LEFT JOIN usuarios u ON r.id_usuario_ingreso = u.id_usuario
            WHERE r.id_repuesto = ?
            """
            
            repuesto = db.obtener_uno(consulta, (id_repuesto,))
            
            if repuesto:
                repuesto['stock_bajo'] = repuesto['cantidad_disponible'] <= config.cantidad_minima_stock_repuestos
            
            return repuesto
            
        except Exception as e:
            config.guardar_log(f"Error al obtener repuesto: {e}", "ERROR")
            return None
    
    @staticmethod
    def modificar_repuesto(id_repuesto, nombre, modelos_compatibles, cantidad, 
                          estado, precio_referencia, notas, id_usuario):
        """
        Modifica un repuesto
        
        Args:
            id_repuesto (int): ID del repuesto
            nombre (str): Nuevo nombre
            modelos_compatibles (str): Nuevos modelos
            cantidad (int): Nueva cantidad
            estado (str): Nuevo estado
            precio_referencia (float): Nuevo precio
            notas (str): Nuevas notas
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Obtener datos anteriores
            repuesto_anterior = ModuloRepuestos.obtener_repuesto_por_id(id_repuesto)
            if not repuesto_anterior:
                return False, "Repuesto no encontrado"
            
            # Actualizar
            consulta = """
            UPDATE repuestos
            SET nombre = ?, modelos_compatibles = ?, cantidad_disponible = ?,
                estado = ?, precio_referencia = ?, notas = ?
            WHERE id_repuesto = ?
            """
            
            db.ejecutar_consulta(
                consulta,
                (nombre, modelos_compatibles, cantidad, estado, precio_referencia, notas, id_repuesto)
            )
            
            # Registrar cambios en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            
            if repuesto_anterior['cantidad_disponible'] != cantidad:
                registrar_accion_auditoria(
                    id_usuario=id_usuario,
                    accion="Modificar",
                    modulo="Repuestos",
                    id_registro=id_repuesto,
                    campo_modificado="cantidad_disponible",
                    valor_anterior=str(repuesto_anterior['cantidad_disponible']),
                    valor_nuevo=str(cantidad),
                    motivo="Ajuste de inventario"
                )
            
            config.guardar_log(f"Repuesto ID {id_repuesto} modificado", "INFO")
            return True, "Repuesto modificado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al modificar repuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def descontar_stock(id_repuesto, cantidad, id_usuario):
        """
        Descuenta stock de un repuesto
        
        Args:
            id_repuesto (int): ID del repuesto
            cantidad (int): Cantidad a descontar
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            repuesto = ModuloRepuestos.obtener_repuesto_por_id(id_repuesto)
            if not repuesto:
                return False, "Repuesto no encontrado"
            
            if repuesto['cantidad_disponible'] < cantidad:
                return False, f"Stock insuficiente. Disponible: {repuesto['cantidad_disponible']}"
            
            nueva_cantidad = repuesto['cantidad_disponible'] - cantidad
            
            consulta = """
            UPDATE repuestos
            SET cantidad_disponible = ?
            WHERE id_repuesto = ?
            """
            
            db.ejecutar_consulta(consulta, (nueva_cantidad, id_repuesto))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Repuestos",
                id_registro=id_repuesto,
                campo_modificado="cantidad_disponible",
                valor_anterior=str(repuesto['cantidad_disponible']),
                valor_nuevo=str(nueva_cantidad),
                motivo=f"Uso en reparación: -{cantidad}"
            )
            
            config.guardar_log(f"Stock de repuesto ID {id_repuesto} descontado: -{cantidad}", "INFO")
            return True, "Stock descontado"
            
        except Exception as e:
            config.guardar_log(f"Error al descontar stock: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_estadisticas_repuestos():
        """
        Obtiene estadísticas del inventario
        
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            # Total de repuestos (diferentes)
            consulta = "SELECT COUNT(*) as total FROM repuestos"
            resultado = db.obtener_uno(consulta)
            estadisticas['total_items'] = resultado['total'] if resultado else 0
            
            # Total unidades
            consulta = "SELECT SUM(cantidad_disponible) as total FROM repuestos"
            resultado = db.obtener_uno(consulta)
            estadisticas['total_unidades'] = resultado['total'] if resultado and resultado['total'] else 0
            
            # Con stock bajo
            consulta = "SELECT COUNT(*) as total FROM repuestos WHERE cantidad_disponible <= ?"
            resultado = db.obtener_uno(consulta, (config.cantidad_minima_stock_repuestos,))
            estadisticas['stock_bajo'] = resultado['total'] if resultado else 0
            
            # Sin stock
            consulta = "SELECT COUNT(*) as total FROM repuestos WHERE cantidad_disponible = 0"
            resultado = db.obtener_uno(consulta)
            estadisticas['sin_stock'] = resultado['total'] if resultado else 0
            
            # Por origen
            consulta = "SELECT COUNT(*) as total FROM repuestos WHERE origen = 'Nuevo'"
            resultado = db.obtener_uno(consulta)
            estadisticas['nuevos'] = resultado['total'] if resultado else 0
            
            consulta = "SELECT COUNT(*) as total FROM repuestos WHERE origen = 'Recuperado'"
            resultado = db.obtener_uno(consulta)
            estadisticas['recuperados'] = resultado['total'] if resultado else 0
            
            # Valor total del inventario
            consulta = "SELECT SUM(cantidad_disponible * precio_referencia) as total FROM repuestos"
            resultado = db.obtener_uno(consulta)
            estadisticas['valor_total'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de repuestos: {e}", "ERROR")
            return {'total_items': 0, 'total_unidades': 0}
    
    @staticmethod
    def obtener_historial_uso(id_repuesto, limite=50):
        """
        Obtiene el historial de uso de un repuesto
        
        Args:
            id_repuesto (int): ID del repuesto
            limite (int): Cantidad máxima de registros
            
        Returns:
            list: Historial de uso
        """
        try:
            consulta = """
            SELECT 
                ru.*,
                o.id_orden,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                c.nombre as cliente_nombre,
                u.nombre as usuario_nombre
            FROM repuestos_usados ru
            INNER JOIN ordenes_trabajo o ON ru.id_orden = o.id_orden
            INNER JOIN equipos e ON o.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON ru.id_usuario_uso = u.id_usuario
            WHERE ru.id_repuesto = ?
            ORDER BY ru.fecha_uso DESC
            LIMIT ?
            """
            
            return db.obtener_todos(consulta, (id_repuesto, limite))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener historial de uso: {e}", "ERROR")
            return []
