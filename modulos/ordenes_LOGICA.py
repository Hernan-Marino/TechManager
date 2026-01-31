# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE ÓRDENES DE TRABAJO
============================================================================
Lógica de negocio para órdenes de trabajo y reparaciones
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.validadores import validar_requerido
from sistema_base.configuracion import config


class ModuloOrdenes:
    """Clase para manejar la lógica de negocio de órdenes de trabajo"""
    
    # Estados posibles
    ESTADOS_ORDEN = [
        "En diagnóstico",
        "En reparación",
        "Esperando repuesto",
        "Pausada",
        "Finalizada con reparación",
        "Finalizada sin reparación"
    ]
    
    @staticmethod
    def crear_orden_desde_presupuesto(id_presupuesto, id_usuario):
        """
        Crea una orden de trabajo desde un presupuesto aceptado
        
        Args:
            id_presupuesto (int): ID del presupuesto
            id_usuario (int): ID del usuario técnico asignado
            
        Returns:
            tuple: (exito, mensaje, id_orden_nueva)
        """
        try:
            # Obtener datos del presupuesto
            consulta = """
            SELECT p.*, e.id_equipo
            FROM presupuestos p
            INNER JOIN equipos e ON p.id_equipo = e.id_equipo
            WHERE p.id_presupuesto = ?
            """
            
            presupuesto = db.obtener_uno(consulta, (id_presupuesto,))
            
            if not presupuesto:
                return False, "Presupuesto no encontrado", None
            
            # Crear orden de trabajo
            consulta_insertar = """
            INSERT INTO ordenes_trabajo (
                id_equipo,
                id_presupuesto,
                id_tecnico_asignado,
                descripcion_reparacion,
                estado_orden,
                fecha_inicio,
                cobra_diagnostico
            )
            VALUES (?, ?, ?, ?, 'En diagnóstico', ?, 0)
            """
            
            id_nueva = db.ejecutar_consulta(
                consulta_insertar,
                (presupuesto['id_equipo'], id_presupuesto, id_usuario,
                 presupuesto['descripcion_trabajo'], datetime.now())
            )
            
            # Agregar nota al equipo
            from modulos.equipos import ModuloEquipos
            ModuloEquipos.agregar_nota_equipo(
                presupuesto['id_equipo'],
                f"Orden de trabajo N° {id_nueva} creada",
                id_usuario
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Órdenes",
                id_registro=id_nueva,
                motivo=f"Orden creada desde presupuesto ID {id_presupuesto}"
            )
            
            config.guardar_log(f"Orden de trabajo ID {id_nueva} creada desde presupuesto ID {id_presupuesto}", "INFO")
            return True, f"Orden de trabajo N° {id_nueva} creada", id_nueva
            
        except Exception as e:
            config.guardar_log(f"Error al crear orden de trabajo: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def crear_orden_manual(id_equipo, descripcion, id_tecnico, cobra_diagnostico, id_usuario):
        """
        Crea una orden de trabajo manualmente (sin presupuesto)
        
        Args:
            id_equipo (int): ID del equipo
            descripcion (str): Descripción del trabajo
            id_tecnico (int): ID del técnico asignado
            cobra_diagnostico (bool): Si cobra diagnóstico
            id_usuario (int): ID del usuario que crea
            
        Returns:
            tuple: (exito, mensaje, id_orden_nueva)
        """
        try:
            # Validar descripción
            es_valido, mensaje = validar_requerido(descripcion, "Descripción del trabajo")
            if not es_valido:
                return False, mensaje, None
            
            # Crear orden
            consulta = """
            INSERT INTO ordenes_trabajo (
                id_equipo,
                id_tecnico_asignado,
                descripcion_reparacion,
                estado_orden,
                fecha_inicio,
                cobra_diagnostico
            )
            VALUES (?, ?, ?, 'En diagnóstico', ?, ?)
            """
            
            id_nueva = db.ejecutar_consulta(
                consulta,
                (id_equipo, id_tecnico, descripcion, datetime.now(), 1 if cobra_diagnostico else 0)
            )
            
            # Cambiar estado del equipo
            from modulos.equipos import ModuloEquipos
            ModuloEquipos.cambiar_estado_equipo(
                id_equipo,
                "En reparación",
                id_usuario,
                "Orden de trabajo creada"
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Órdenes",
                id_registro=id_nueva,
                motivo=f"Orden manual creada para equipo ID {id_equipo}"
            )
            
            config.guardar_log(f"Orden de trabajo ID {id_nueva} creada manualmente", "INFO")
            return True, f"Orden de trabajo N° {id_nueva} creada", id_nueva
            
        except Exception as e:
            config.guardar_log(f"Error al crear orden manual: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_ordenes(filtro_estado="", filtro_tecnico="", busqueda="", orden="fecha_desc"):
        """
        Lista todas las órdenes de trabajo
        
        Args:
            filtro_estado (str): Filtrar por estado
            filtro_tecnico (int): Filtrar por técnico
            busqueda (str): Buscar en descripción, cliente, equipo
            orden (str): fecha_desc, fecha_asc
            
        Returns:
            list: Lista de órdenes
        """
        try:
            consulta = """
            SELECT 
                o.id_orden,
                o.descripcion_reparacion,
                o.estado_orden,
                o.fecha_inicio,
                o.fecha_finalizacion,
                o.cobra_diagnostico,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.id_equipo,
                c.nombre as cliente_nombre,
                u.nombre as tecnico_nombre
            FROM ordenes_trabajo o
            INNER JOIN equipos e ON o.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON o.id_tecnico_asignado = u.id_usuario
            WHERE 1=1
            """
            
            parametros = []
            
            # Filtros
            if filtro_estado:
                consulta += " AND o.estado_orden = ?"
                parametros.append(filtro_estado)
            
            if filtro_tecnico:
                consulta += " AND o.id_tecnico_asignado = ?"
                parametros.append(filtro_tecnico)
            
            if busqueda:
                consulta += """ AND (
                    o.descripcion_reparacion LIKE ? OR
                    c.nombre LIKE ? OR
                    e.marca LIKE ? OR
                    e.modelo LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 4)
            
            # Ordenamiento
            if orden == "fecha_asc":
                consulta += " ORDER BY o.fecha_inicio ASC"
            else:
                consulta += " ORDER BY o.fecha_inicio DESC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar órdenes: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_orden_por_id(id_orden):
        """
        Obtiene una orden por su ID
        
        Args:
            id_orden (int): ID de la orden
            
        Returns:
            dict: Datos completos de la orden o None
        """
        try:
            consulta = """
            SELECT 
                o.*,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.identificador,
                e.id_cliente,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                u.nombre as tecnico_nombre,
                p.monto_total as monto_presupuesto
            FROM ordenes_trabajo o
            INNER JOIN equipos e ON o.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON o.id_tecnico_asignado = u.id_usuario
            LEFT JOIN presupuestos p ON o.id_presupuesto = p.id_presupuesto
            WHERE o.id_orden = ?
            """
            
            return db.obtener_uno(consulta, (id_orden,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener orden: {e}", "ERROR")
            return None
    
    @staticmethod
    def cambiar_estado_orden(id_orden, nuevo_estado, observaciones, id_usuario):
        """
        Cambia el estado de una orden
        
        Args:
            id_orden (int): ID de la orden
            nuevo_estado (str): Nuevo estado
            observaciones (str): Observaciones
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if nuevo_estado not in ModuloOrdenes.ESTADOS_ORDEN:
                return False, "Estado inválido"
            
            # Obtener orden
            orden = ModuloOrdenes.obtener_orden_por_id(id_orden)
            if not orden:
                return False, "Orden no encontrada"
            
            estado_anterior = orden['estado_orden']
            
            # Actualizar estado
            consulta = """
            UPDATE ordenes_trabajo
            SET estado_orden = ?
            WHERE id_orden = ?
            """
            
            db.ejecutar_consulta(consulta, (nuevo_estado, id_orden))
            
            # Agregar nota
            from modulos.equipos import ModuloEquipos
            nota = f"Orden N° {id_orden}: {estado_anterior} → {nuevo_estado}"
            if observaciones:
                nota += f" - {observaciones}"
            
            ModuloEquipos.agregar_nota_equipo(orden['id_equipo'], nota, id_usuario)
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Órdenes",
                id_registro=id_orden,
                campo_modificado="estado_orden",
                valor_anterior=estado_anterior,
                valor_nuevo=nuevo_estado,
                motivo=observaciones
            )
            
            config.guardar_log(f"Orden ID {id_orden} cambió de estado: {estado_anterior} → {nuevo_estado}", "INFO")
            return True, f"Estado cambiado a '{nuevo_estado}'"
            
        except Exception as e:
            config.guardar_log(f"Error al cambiar estado de orden: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def finalizar_orden(id_orden, con_reparacion, trabajo_realizado, 
                       monto_diagnostico, observaciones, id_usuario):
        """
        Finaliza una orden de trabajo
        
        Args:
            id_orden (int): ID de la orden
            con_reparacion (bool): Si se reparó o no
            trabajo_realizado (str): Descripción del trabajo realizado
            monto_diagnostico (float): Monto del diagnóstico (si aplica)
            observaciones (str): Observaciones finales
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Obtener orden
            orden = ModuloOrdenes.obtener_orden_por_id(id_orden)
            if not orden:
                return False, "Orden no encontrada"
            
            if orden['estado_orden'].startswith('Finalizada'):
                return False, "La orden ya está finalizada"
            
            # Determinar nuevo estado
            nuevo_estado = "Finalizada con reparación" if con_reparacion else "Finalizada sin reparación"
            
            # Actualizar orden
            consulta = """
            UPDATE ordenes_trabajo
            SET estado_orden = ?,
                trabajo_realizado = ?,
                observaciones_finales = ?,
                fecha_finalizacion = ?
            WHERE id_orden = ?
            """
            
            db.ejecutar_consulta(
                consulta,
                (nuevo_estado, trabajo_realizado, observaciones, datetime.now(), id_orden)
            )
            
            # Cambiar estado del equipo
            from modulos.equipos import ModuloEquipos
            if con_reparacion:
                ModuloEquipos.cambiar_estado_equipo(
                    orden['id_equipo'],
                    "Listo",
                    id_usuario,
                    f"Reparación finalizada - Orden N° {id_orden}"
                )
            else:
                ModuloEquipos.cambiar_estado_equipo(
                    orden['id_equipo'],
                    "Sin reparación",
                    id_usuario,
                    f"Sin reparación - Orden N° {id_orden}"
                )
            
            # Generar factura automática si corresponde
            if con_reparacion:
                from modulos.facturacion import ModuloFacturacion
                ModuloFacturacion.generar_factura_desde_orden(id_orden, id_usuario)
            elif orden['cobra_diagnostico'] and monto_diagnostico > 0:
                from modulos.facturacion import ModuloFacturacion
                ModuloFacturacion.generar_factura_diagnostico(
                    id_orden,
                    monto_diagnostico,
                    id_usuario
                )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Finalizar",
                modulo="Órdenes",
                id_registro=id_orden,
                motivo=f"Orden finalizada {'con' if con_reparacion else 'sin'} reparación"
            )
            
            config.guardar_log(f"Orden ID {id_orden} finalizada", "INFO")
            return True, "Orden finalizada exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al finalizar orden: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def agregar_repuesto_a_orden(id_orden, id_repuesto, cantidad, id_usuario):
        """
        Agrega un repuesto usado a una orden
        
        Args:
            id_orden (int): ID de la orden
            id_repuesto (int): ID del repuesto
            cantidad (int): Cantidad usada
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Verificar stock
            from modulos.repuestos import ModuloRepuestos
            repuesto = ModuloRepuestos.obtener_repuesto_por_id(id_repuesto)
            
            if not repuesto:
                return False, "Repuesto no encontrado"
            
            if repuesto['cantidad_disponible'] < cantidad:
                return False, f"Stock insuficiente. Disponible: {repuesto['cantidad_disponible']}"
            
            # Registrar uso
            consulta = """
            INSERT INTO repuestos_usados (
                id_orden, id_repuesto, cantidad_usada, 
                id_usuario_uso, fecha_uso
            )
            VALUES (?, ?, ?, ?, ?)
            """
            
            db.ejecutar_consulta(
                consulta,
                (id_orden, id_repuesto, cantidad, id_usuario, datetime.now())
            )
            
            # Descontar del inventario
            ModuloRepuestos.descontar_stock(id_repuesto, cantidad, id_usuario)
            
            # Agregar nota
            orden = ModuloOrdenes.obtener_orden_por_id(id_orden)
            from modulos.equipos import ModuloEquipos
            ModuloEquipos.agregar_nota_equipo(
                orden['id_equipo'],
                f"Repuesto usado: {repuesto['nombre']} x{cantidad}",
                id_usuario
            )
            
            config.guardar_log(f"Repuesto ID {id_repuesto} agregado a orden ID {id_orden}", "INFO")
            return True, "Repuesto agregado a la orden"
            
        except Exception as e:
            config.guardar_log(f"Error al agregar repuesto a orden: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_repuestos_usados(id_orden):
        """
        Obtiene los repuestos usados en una orden
        
        Args:
            id_orden (int): ID de la orden
            
        Returns:
            list: Lista de repuestos usados
        """
        try:
            consulta = """
            SELECT 
                ru.*,
                r.nombre as repuesto_nombre,
                r.precio_referencia,
                u.nombre as usuario_nombre
            FROM repuestos_usados ru
            INNER JOIN repuestos r ON ru.id_repuesto = r.id_repuesto
            LEFT JOIN usuarios u ON ru.id_usuario_uso = u.id_usuario
            WHERE ru.id_orden = ?
            ORDER BY ru.fecha_uso DESC
            """
            
            return db.obtener_todos(consulta, (id_orden,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener repuestos usados: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_estadisticas_ordenes():
        """
        Obtiene estadísticas de órdenes
        
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            # Total
            consulta = "SELECT COUNT(*) as total FROM ordenes_trabajo"
            resultado = db.obtener_uno(consulta)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Por estado
            for estado in ModuloOrdenes.ESTADOS_ORDEN:
                consulta = "SELECT COUNT(*) as total FROM ordenes_trabajo WHERE estado_orden = ?"
                resultado = db.obtener_uno(consulta, (estado,))
                key = estado.lower().replace(" ", "_")
                estadisticas[key] = resultado['total'] if resultado else 0
            
            # Finalizadas con éxito
            consulta = "SELECT COUNT(*) as total FROM ordenes_trabajo WHERE estado_orden = 'Finalizada con reparación'"
            resultado = db.obtener_uno(consulta)
            estadisticas['exitosas'] = resultado['total'] if resultado else 0
            
            # Finalizadas sin reparación
            consulta = "SELECT COUNT(*) as total FROM ordenes_trabajo WHERE estado_orden = 'Finalizada sin reparación'"
            resultado = db.obtener_uno(consulta)
            estadisticas['sin_reparacion'] = resultado['total'] if resultado else 0
            
            # En curso
            consulta = """
            SELECT COUNT(*) as total FROM ordenes_trabajo 
            WHERE estado_orden NOT LIKE 'Finalizada%'
            """
            resultado = db.obtener_uno(consulta)
            estadisticas['en_curso'] = resultado['total'] if resultado else 0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de órdenes: {e}", "ERROR")
            return {'total': 0}

