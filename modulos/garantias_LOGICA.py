# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE GARANTÍAS
============================================================================
Lógica de negocio para gestión de garantías
============================================================================
"""

from datetime import datetime, timedelta
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloGarantias:
    """Clase para manejar la lógica de negocio de garantías"""
    
    # Estados de garantía
    ESTADOS_GARANTIA = [
        "Vigente",
        "Vencida",
        "Utilizada"
    ]
    
    @staticmethod
    def crear_garantia(id_orden, dias_garantia=None, id_usuario=None):
        """
        Crea una garantía para una orden finalizada
        
        Args:
            id_orden (int): ID de la orden
            dias_garantia (int): Días de garantía (usa default si es None)
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_garantia_nueva)
        """
        try:
            # Obtener orden
            from modulos.ordenes import ModuloOrdenes
            orden = ModuloOrdenes.obtener_orden_por_id(id_orden)
            
            if not orden:
                return False, "Orden no encontrada", None
            
            # Verificar que esté finalizada con reparación
            if orden['estado_orden'] != "Finalizada con reparación":
                return False, "Solo se pueden crear garantías para órdenes finalizadas con reparación", None
            
            # Usar días de garantía configurados si no se especifica
            if dias_garantia is None:
                dias_garantia = getattr(config, "dias_garantia_reparacion", 90)
            
            # Calcular fechas
            fecha_inicio = datetime.now()
            fecha_vencimiento = fecha_inicio + timedelta(days=dias_garantia)
            
            # Insertar garantía
            consulta = """
            INSERT INTO garantias (
                id_orden, id_equipo, fecha_inicio, fecha_vencimiento,
                dias_garantia, estado_garantia, id_usuario_crea
            )
            VALUES (?, ?, ?, ?, ?, 'Vigente', ?)
            """
            
            id_nueva = db.ejecutar_consulta(
                consulta,
                (id_orden, orden['id_equipo'], fecha_inicio, fecha_vencimiento,
                 dias_garantia, id_usuario if id_usuario else 1)
            )
            
            # Agregar nota al equipo
            from modulos.equipos import ModuloEquipos
            ModuloEquipos.agregar_nota_equipo(
                orden['id_equipo'],
                f"Garantía creada: {dias_garantia} días (vence {fecha_vencimiento.strftime('%d/%m/%Y')})",
                id_usuario if id_usuario else 1
            )
            
            # Registrar en auditoría
            if id_usuario:
                from sistema_base.seguridad import registrar_accion_auditoria
                registrar_accion_auditoria(
                    id_usuario=id_usuario,
                    accion="Crear",
                    modulo="Garantías",
                    id_registro=id_nueva,
                    motivo=f"Garantía de {dias_garantia} días creada para orden ID {id_orden}"
                )
            
            config.guardar_log(f"Garantía ID {id_nueva} creada para orden ID {id_orden}", "INFO")
            return True, f"Garantía de {dias_garantia} días creada", id_nueva
            
        except Exception as e:
            config.guardar_log(f"Error al crear garantía: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_garantias(filtro_estado="", busqueda=""):
        """
        Lista todas las garantías
        
        Args:
            filtro_estado (str): Filtrar por estado
            busqueda (str): Buscar en cliente, equipo
            
        Returns:
            list: Lista de garantías
        """
        try:
            consulta = """
            SELECT 
                g.*,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono
            FROM garantias g
            INNER JOIN equipos e ON g.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            WHERE 1=1
            """
            
            parametros = []
            
            if filtro_estado:
                consulta += " AND g.estado_garantia = ?"
                parametros.append(filtro_estado)
            
            if busqueda:
                consulta += """ AND (
                    c.nombre LIKE ? OR
                    e.marca LIKE ? OR
                    e.modelo LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 3)
            
            consulta += " ORDER BY g.fecha_vencimiento ASC"
            
            garantias = db.obtener_todos(consulta, tuple(parametros))
            
            # Calcular días restantes
            for garantia in garantias:
                garantia['dias_restantes'] = ModuloGarantias.calcular_dias_restantes(
                    garantia['fecha_vencimiento'],
                    garantia['estado_garantia']
                )
            
            return garantias
            
        except Exception as e:
            config.guardar_log(f"Error al listar garantías: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_garantia_por_id(id_garantia):
        """
        Obtiene una garantía por su ID
        
        Args:
            id_garantia (int): ID de la garantía
            
        Returns:
            dict: Datos de la garantía o None
        """
        try:
            consulta = """
            SELECT 
                g.*,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.identificador,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                o.descripcion_reparacion
            FROM garantias g
            INNER JOIN equipos e ON g.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            LEFT JOIN ordenes_trabajo o ON g.id_orden = o.id_orden
            WHERE g.id_garantia = ?
            """
            
            garantia = db.obtener_uno(consulta, (id_garantia,))
            
            if garantia:
                garantia['dias_restantes'] = ModuloGarantias.calcular_dias_restantes(
                    garantia['fecha_vencimiento'],
                    garantia['estado_garantia']
                )
            
            return garantia
            
        except Exception as e:
            config.guardar_log(f"Error al obtener garantía: {e}", "ERROR")
            return None
    
    @staticmethod
    def validar_garantia(id_equipo):
        """
        Valida si un equipo tiene garantía vigente
        
        Args:
            id_equipo (int): ID del equipo
            
        Returns:
            tuple: (tiene_garantia, garantia_data)
        """
        try:
            consulta = """
            SELECT *
            FROM garantias
            WHERE id_equipo = ?
            AND estado_garantia = 'Vigente'
            AND fecha_vencimiento >= ?
            ORDER BY fecha_vencimiento DESC
            LIMIT 1
            """
            
            garantia = db.obtener_uno(consulta, (id_equipo, datetime.now()))
            
            if garantia:
                return True, garantia
            else:
                return False, None
            
        except Exception as e:
            config.guardar_log(f"Error al validar garantía: {e}", "ERROR")
            return False, None
    
    @staticmethod
    def marcar_garantia_utilizada(id_garantia, motivo_uso, id_usuario):
        """
        Marca una garantía como utilizada
        
        Args:
            id_garantia (int): ID de la garantía
            motivo_uso (str): Motivo por el que se usa
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            garantia = ModuloGarantias.obtener_garantia_por_id(id_garantia)
            
            if not garantia:
                return False, "Garantía no encontrada"
            
            if garantia['estado_garantia'] != "Vigente":
                return False, f"La garantía está {garantia['estado_garantia'].lower()}"
            
            # Actualizar garantía
            consulta = """
            UPDATE garantias
            SET estado_garantia = 'Utilizada',
                fecha_uso = ?,
                motivo_uso = ?
            WHERE id_garantia = ?
            """
            
            db.ejecutar_consulta(consulta, (datetime.now(), motivo_uso, id_garantia))
            
            # Agregar nota al equipo
            from modulos.equipos import ModuloEquipos
            ModuloEquipos.agregar_nota_equipo(
                garantia['id_equipo'],
                f"Garantía utilizada: {motivo_uso}",
                id_usuario
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Garantías",
                id_registro=id_garantia,
                campo_modificado="estado_garantia",
                valor_anterior="Vigente",
                valor_nuevo="Utilizada",
                motivo=motivo_uso
            )
            
            config.guardar_log(f"Garantía ID {id_garantia} marcada como utilizada", "INFO")
            return True, "Garantía marcada como utilizada"
            
        except Exception as e:
            config.guardar_log(f"Error al marcar garantía utilizada: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def verificar_vencimientos():
        """
        Verifica y marca garantías vencidas automáticamente
        
        Returns:
            int: Cantidad de garantías marcadas como vencidas
        """
        try:
            fecha_actual = datetime.now()
            
            # Buscar garantías vigentes vencidas
            consulta = """
            SELECT id_garantia
            FROM garantias
            WHERE estado_garantia = 'Vigente'
            AND fecha_vencimiento < ?
            """
            
            vencidas = db.obtener_todos(consulta, (fecha_actual,))
            
            for garantia in vencidas:
                consulta_update = """
                UPDATE garantias
                SET estado_garantia = 'Vencida'
                WHERE id_garantia = ?
                """
                
                db.ejecutar_consulta(consulta_update, (garantia['id_garantia'],))
            
            if len(vencidas) > 0:
                config.guardar_log(f"{len(vencidas)} garantías marcadas como vencidas", "INFO")
            
            return len(vencidas)
            
        except Exception as e:
            config.guardar_log(f"Error al verificar vencimientos de garantías: {e}", "ERROR")
            return 0
    
    @staticmethod
    def calcular_dias_restantes(fecha_vencimiento, estado):
        """
        Calcula los días restantes de garantía
        
        Args:
            fecha_vencimiento: Fecha de vencimiento
            estado (str): Estado de la garantía
            
        Returns:
            int: Días restantes (negativo si venció)
        """
        try:
            if estado != "Vigente":
                return 0
            
            if isinstance(fecha_vencimiento, str):
                fecha = datetime.fromisoformat(fecha_vencimiento.replace('Z', '+00:00'))
            else:
                fecha = fecha_vencimiento
            
            diferencia = fecha - datetime.now()
            return diferencia.days
            
        except:
            return 0
    
    @staticmethod
    def obtener_estadisticas_garantias():
        """
        Obtiene estadísticas de garantías
        
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            # Total
            consulta = "SELECT COUNT(*) as total FROM garantias"
            resultado = db.obtener_uno(consulta)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Por estado
            for estado in ModuloGarantias.ESTADOS_GARANTIA:
                consulta = "SELECT COUNT(*) as total FROM garantias WHERE estado_garantia = ?"
                resultado = db.obtener_uno(consulta, (estado,))
                key = estado.lower()
                estadisticas[key] = resultado['total'] if resultado else 0
            
            # Próximas a vencer (vigentes con menos de 7 días)
            fecha_limite = datetime.now() + timedelta(days=7)
            consulta = """
            SELECT COUNT(*) as total 
            FROM garantias 
            WHERE estado_garantia = 'Vigente'
            AND fecha_vencimiento <= ?
            """
            resultado = db.obtener_uno(consulta, (fecha_limite,))
            estadisticas['proximas_a_vencer'] = resultado['total'] if resultado else 0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de garantías: {e}", "ERROR")
            return {'total': 0}
