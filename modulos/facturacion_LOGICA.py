# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE FACTURACIÓN
============================================================================
Lógica de negocio para generación y gestión de facturas
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloFacturacion:
    """Clase para manejar la lógica de negocio de facturas"""
    
    # Estados de cobro
    ESTADOS_COBRO = [
        "Pendiente",
        "Pago parcial",
        "Pagado",
        "Incobrable"
    ]
    
    @staticmethod
    def generar_numero_factura():
        """
        Genera un número único de factura con formato: F-YYYY-####
        
        Returns:
            str: Número de factura generado
        """
        try:
            anio_actual = datetime.now().year
            prefijo = f"F-{anio_actual}-"
            
            # Buscar la última factura del año
            consulta = """
            SELECT numero_factura 
            FROM facturas 
            WHERE numero_factura LIKE ?
            ORDER BY numero_factura DESC
            LIMIT 1
            """
            
            resultado = db.obtener_uno(consulta, (f"{prefijo}%",))
            
            if resultado:
                ultimo_numero = resultado['numero_factura']
                secuencial = int(ultimo_numero.split('-')[-1])
                nuevo_secuencial = secuencial + 1
            else:
                nuevo_secuencial = 1
            
            return f"{prefijo}{nuevo_secuencial:04d}"
            
        except Exception as e:
            config.guardar_log(f"Error al generar número de factura: {e}", "ERROR")
            return f"F-{datetime.now().strftime('%Y-%m%d-%H%M%S')}"
    
    @staticmethod
    def generar_factura_desde_orden(id_orden, id_usuario):
        """
        Genera una factura desde una orden de trabajo finalizada
        
        Args:
            id_orden (int): ID de la orden
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_factura_nueva)
        """
        try:
            # Obtener datos de la orden
            from modulos.ordenes import ModuloOrdenes
            orden = ModuloOrdenes.obtener_orden_por_id(id_orden)
            
            if not orden:
                return False, "Orden no encontrada", None
            
            # Verificar que esté finalizada con reparación
            if orden['estado_orden'] != "Finalizada con reparación":
                return False, "La orden debe estar finalizada con reparación", None
            
            # Generar número de factura
            numero_factura = ModuloFacturacion.generar_numero_factura()
            
            # Obtener monto del presupuesto
            monto_total = orden['monto_presupuesto'] if orden['monto_presupuesto'] else 0.0
            
            # Insertar factura
            consulta = """
            INSERT INTO facturas (
                numero_factura, id_cliente, id_orden, total,
                estado_cobro, fecha_emision, id_usuario_genera
            )
            VALUES (?, ?, ?, ?, 'Pendiente', ?, ?)
            """
            
            id_nueva = db.ejecutar_consulta(
                consulta,
                (numero_factura, orden['id_cliente'], id_orden, 
                 monto_total, datetime.now(), id_usuario)
            )
            
            # Agregar nota al equipo
            from modulos.equipos import ModuloEquipos
            ModuloEquipos.agregar_nota_equipo(
                orden['id_equipo'],
                f"Factura {numero_factura} generada: ${monto_total:.2f}",
                id_usuario
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Facturas",
                id_registro=id_nueva,
                motivo=f"Factura {numero_factura} generada desde orden ID {id_orden}"
            )
            
            config.guardar_log(f"Factura {numero_factura} generada desde orden ID {id_orden}", "INFO")
            return True, f"Factura {numero_factura} generada", id_nueva
            
        except Exception as e:
            config.guardar_log(f"Error al generar factura: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def generar_factura_diagnostico(id_orden, monto_diagnostico, id_usuario):
        """
        Genera una factura por diagnóstico (sin reparación)
        
        Args:
            id_orden (int): ID de la orden
            monto_diagnostico (float): Monto del diagnóstico
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_factura_nueva)
        """
        try:
            # Obtener orden
            from modulos.ordenes import ModuloOrdenes
            orden = ModuloOrdenes.obtener_orden_por_id(id_orden)
            
            if not orden:
                return False, "Orden no encontrada", None
            
            # Generar número
            numero_factura = ModuloFacturacion.generar_numero_factura()
            
            # Insertar factura
            consulta = """
            INSERT INTO facturas (
                numero_factura, id_cliente, id_orden, total,
                estado_cobro, fecha_emision, id_usuario_genera
            )
            VALUES (?, ?, ?, ?, 'Pendiente', ?, ?)
            """
            
            id_nueva = db.ejecutar_consulta(
                consulta,
                (numero_factura, orden['id_cliente'], id_orden,
                 monto_diagnostico, datetime.now(), id_usuario)
            )
            
            config.guardar_log(f"Factura {numero_factura} de diagnóstico generada", "INFO")
            return True, f"Factura {numero_factura} generada", id_nueva
            
        except Exception as e:
            config.guardar_log(f"Error al generar factura de diagnóstico: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_facturas(filtro_estado="", busqueda="", fecha_desde=None, fecha_hasta=None):
        """
        Lista todas las facturas
        
        Args:
            filtro_estado (str): Filtrar por estado de cobro
            busqueda (str): Buscar en número, cliente
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            
        Returns:
            list: Lista de facturas
        """
        try:
            consulta = """
            SELECT 
                f.*,
                c.nombre as cliente_nombre,
                c.tiene_incobrables
            FROM facturas f
            INNER JOIN clientes c ON f.id_cliente = c.id_cliente
            WHERE 1=1
            """
            
            parametros = []
            
            if filtro_estado:
                consulta += " AND f.estado_cobro = ?"
                parametros.append(filtro_estado)
            
            if busqueda:
                consulta += """ AND (
                    f.numero_factura LIKE ? OR
                    c.nombre LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param, busqueda_param])
            
            if fecha_desde:
                consulta += " AND f.fecha_emision >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                consulta += " AND f.fecha_emision <= ?"
                parametros.append(fecha_hasta)
            
            consulta += " ORDER BY f.fecha_emision DESC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar facturas: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_factura_por_id(id_factura):
        """
        Obtiene una factura por su ID
        
        Args:
            id_factura (int): ID de la factura
            
        Returns:
            dict: Datos de la factura o None
        """
        try:
            consulta = """
            SELECT 
                f.*,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                c.direccion as cliente_direccion,
                u.nombre as usuario_nombre
            FROM facturas f
            INNER JOIN clientes c ON f.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON f.id_usuario_genera = u.id_usuario
            WHERE f.id_factura = ?
            """
            
            return db.obtener_uno(consulta, (id_factura,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener factura: {e}", "ERROR")
            return None
    
    @staticmethod
    def actualizar_estado_cobro(id_factura):
        """
        Actualiza el estado de cobro de una factura según los pagos
        
        Args:
            id_factura (int): ID de la factura
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            factura = ModuloFacturacion.obtener_factura_por_id(id_factura)
            if not factura:
                return False, "Factura no encontrada"
            
            # Obtener total pagado
            from modulos.pagos import ModuloPagos
            total_pagado = ModuloPagos.obtener_total_pagado(id_factura)
            
            # Determinar estado
            if total_pagado == 0:
                nuevo_estado = "Pendiente"
            elif total_pagado >= factura['total']:
                nuevo_estado = "Pagado"
            else:
                nuevo_estado = "Pago parcial"
            
            # Actualizar
            consulta = "UPDATE facturas SET estado_cobro = ? WHERE id_factura = ?"
            db.ejecutar_consulta(consulta, (nuevo_estado, id_factura))
            
            return True, f"Estado actualizado a '{nuevo_estado}'"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar estado de cobro: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def marcar_incobrable(id_factura, motivo, id_usuario):
        """
        Marca una factura como incobrable
        
        Args:
            id_factura (int): ID de la factura
            motivo (str): Motivo
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Solo admin
            if not config.es_admin:
                return False, "Solo administradores pueden marcar facturas como incobrables"
            
            factura = ModuloFacturacion.obtener_factura_por_id(id_factura)
            if not factura:
                return False, "Factura no encontrada"
            
            # Actualizar factura
            consulta = "UPDATE facturas SET estado_cobro = 'Incobrable' WHERE id_factura = ?"
            db.ejecutar_consulta(consulta, (id_factura,))
            
            # Marcar deuda incobrable en cliente
            from modulos.clientes import ModuloClientes
            
            # Calcular monto pendiente
            from modulos.pagos import ModuloPagos
            total_pagado = ModuloPagos.obtener_total_pagado(id_factura)
            monto_pendiente = factura['total'] - total_pagado
            
            if monto_pendiente > 0:
                ModuloClientes.marcar_deuda_incobrable(
                    factura['id_cliente'],
                    monto_pendiente,
                    f"Factura {factura['numero_factura']} incobrable",
                    motivo,
                    id_usuario
                )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Facturas",
                id_registro=id_factura,
                campo_modificado="estado_cobro",
                valor_anterior=factura['estado_cobro'],
                valor_nuevo="Incobrable",
                motivo=motivo,
                es_critica=True
            )
            
            config.guardar_log(f"Factura ID {id_factura} marcada como incobrable", "WARNING")
            return True, "Factura marcada como incobrable"
            
        except Exception as e:
            config.guardar_log(f"Error al marcar factura incobrable: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_estadisticas_facturas(fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de facturas
        
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
                where_fecha += " AND fecha_emision >= ?"
                parametros.append(fecha_desde)
            
            if fecha_hasta:
                where_fecha += " AND fecha_emision <= ?"
                parametros.append(fecha_hasta)
            
            # Total facturas
            consulta = f"SELECT COUNT(*) as total FROM facturas WHERE 1=1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Por estado
            for estado in ModuloFacturacion.ESTADOS_COBRO:
                consulta = f"SELECT COUNT(*) as total FROM facturas WHERE estado_cobro = ? {where_fecha}"
                params = [estado] + parametros
                resultado = db.obtener_uno(consulta, tuple(params))
                key = estado.lower().replace(" ", "_")
                estadisticas[key] = resultado['total'] if resultado else 0
            
            # Monto total facturado
            consulta = f"SELECT SUM(total) as total FROM facturas WHERE 1=1 {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['monto_total'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            # Monto cobrado (facturas pagadas)
            consulta = f"SELECT SUM(total) as total FROM facturas WHERE estado_cobro = 'Pagado' {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['monto_cobrado'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            # Monto pendiente
            consulta = f"SELECT SUM(total) as total FROM facturas WHERE estado_cobro IN ('Pendiente', 'Pago parcial') {where_fecha}"
            resultado = db.obtener_uno(consulta, tuple(parametros))
            estadisticas['monto_pendiente'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de facturas: {e}", "ERROR")
            return {'total': 0, 'monto_total': 0.0}
