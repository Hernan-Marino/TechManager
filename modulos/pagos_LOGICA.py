# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE PAGOS
============================================================================
Lógica de negocio para gestión de pagos
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloPagos:
    """Clase para manejar la lógica de negocio de pagos"""
    
    # Métodos de pago
    METODOS_PAGO = [
        "Efectivo",
        "Transferencia",
        "Mercado Pago",
        "Débito",
        "Crédito 1 pago",
        "Crédito 3 cuotas",
        "Crédito 6 cuotas",
        "Crédito 12 cuotas"
    ]
    
    @staticmethod
    def registrar_pago(id_factura, monto, metodo_pago, referencia, id_usuario):
        """
        Registra un pago
        
        Args:
            id_factura (int): ID de la factura
            monto (float): Monto del pago
            metodo_pago (str): Método de pago
            referencia (str): Referencia/comprobante
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_pago_nuevo)
        """
        try:
            if monto <= 0:
                return False, "El monto debe ser mayor a cero", None
            
            if metodo_pago not in ModuloPagos.METODOS_PAGO:
                return False, "Método de pago inválido", None
            
            # Obtener factura
            from modulos.facturacion import ModuloFacturacion
            factura = ModuloFacturacion.obtener_factura_por_id(id_factura)
            
            if not factura:
                return False, "Factura no encontrada", None
            
            # Verificar que no se sobrepase el total
            total_pagado_previo = ModuloPagos.obtener_total_pagado(id_factura)
            if total_pagado_previo + monto > factura['total']:
                return False, f"El pago supera el total de la factura. Resta: ${factura['total'] - total_pagado_previo:.2f}", None
            
            # Registrar pago
            consulta = """
            INSERT INTO pagos (
                id_factura, monto, metodo_pago, referencia,
                fecha_hora_pago, id_usuario_registra
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            id_nuevo = db.ejecutar_consulta(
                consulta,
                (id_factura, monto, metodo_pago, referencia, datetime.now(), id_usuario)
            )
            
            # Actualizar estado de factura
            ModuloFacturacion.actualizar_estado_cobro(id_factura)
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Pagos",
                id_registro=id_nuevo,
                motivo=f"Pago registrado: ${monto:.2f} ({metodo_pago})"
            )
            
            config.guardar_log(f"Pago ID {id_nuevo} registrado para factura ID {id_factura}", "INFO")
            return True, "Pago registrado exitosamente", id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al registrar pago: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def obtener_pagos_de_factura(id_factura):
        """
        Obtiene todos los pagos de una factura
        
        Args:
            id_factura (int): ID de la factura
            
        Returns:
            list: Lista de pagos
        """
        try:
            consulta = """
            SELECT 
                p.*,
                u.nombre as usuario_nombre
            FROM pagos p
            LEFT JOIN usuarios u ON p.id_usuario_registra = u.id_usuario
            WHERE p.id_factura = ?
            ORDER BY p.fecha_hora_pago DESC
            """
            
            return db.obtener_todos(consulta, (id_factura,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener pagos de factura: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_total_pagado(id_factura):
        """
        Obtiene el total pagado de una factura
        
        Args:
            id_factura (int): ID de la factura
            
        Returns:
            float: Total pagado
        """
        try:
            consulta = "SELECT SUM(monto) as total FROM pagos WHERE id_factura = ?"
            resultado = db.obtener_uno(consulta, (id_factura,))
            
            return resultado['total'] if resultado and resultado['total'] else 0.0
            
        except Exception as e:
            config.guardar_log(f"Error al obtener total pagado: {e}", "ERROR")
            return 0.0
    
    @staticmethod
    def listar_pagos(busqueda="", fecha_desde=None, fecha_hasta=None, metodo_pago=""):
        """
        Lista todos los pagos con filtros
        
        Args:
            busqueda (str): Buscar en referencia, cliente
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            metodo_pago (str): Filtrar por método
            
        Returns:
            list: Lista de pagos
        """
        try:
            consulta = """
            SELECT 
                p.*,
                f.numero_factura,
                c.nombre as cliente_nombre,
                u.nombre as usuario_nombre
            FROM pagos p
            INNER JOIN facturas f ON p.id_factura = f.id_factura
            INNER JOIN clientes c ON f.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON p.id_usuario_registra = u.id_usuario
            WHERE 1=1
            """
            
            parametros = []
            
            if busqueda:
                consulta += """ AND (
                    p.referencia LIKE ? OR
                    c.nombre LIKE ? OR
                    f.numero_factura LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 3)
            
            if fecha_desde:
                consulta += " AND p.fecha_hora_pago >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                consulta += " AND p.fecha_hora_pago <= ?"
                parametros.append(fecha_hasta)
            
            if metodo_pago:
                consulta += " AND p.metodo_pago = ?"
                parametros.append(metodo_pago)
            
            consulta += " ORDER BY p.fecha_hora_pago DESC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar pagos: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_estadisticas_pagos(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de pagos
        
        Args:
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            # Base de consulta
            where_fecha = ""
            parametros = []
            
            if fecha_desde:
                where_fecha += " AND fecha_hora_pago >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                where_fecha += " AND fecha_hora_pago <= ?"
                parametros.append(fecha_hasta)
            
            # Total de pagos
            consulta = f"SELECT COUNT(*) as total FROM pagos WHERE 1=1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['total_pagos'] = resultado['total'] if resultado else 0
            
            # Monto total
            consulta = f"SELECT SUM(monto) as total FROM pagos WHERE 1=1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['monto_total'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            # Por método de pago
            for metodo in ModuloPagos.METODOS_PAGO:
                consulta = f"SELECT SUM(monto) as total FROM pagos WHERE metodo_pago = ? {where_fecha}"
                params = [metodo] + parametros
                resultado = db.obtener_uno(consulta, tuple(params))
                key = metodo.lower().replace(" ", "_")
                estadisticas[key] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de pagos: {e}", "ERROR")
            return {'total_pagos': 0, 'monto_total': 0.0}
