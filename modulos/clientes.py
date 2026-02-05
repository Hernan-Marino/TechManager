# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE CLIENTES
============================================================================
Lógica de negocio para gestión de clientes
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.validadores import (validar_nombre, validar_telefono, 
                                       validar_email, limpiar_telefono)
from sistema_base.configuracion import config


class ModuloClientes:
    """Clase para manejar la lógica de negocio de clientes"""
    
    @staticmethod
    def listar_clientes(solo_activos=True, busqueda="", orden="nombre"):
        """
        Lista todos los clientes
        
        Args:
            solo_activos (bool): Si True, excluye clientes con equipos abandonados
            busqueda (str): Texto para buscar en nombre, teléfono, dirección
            orden (str): Campo por el que ordenar (nombre, fecha_registro)
            
        Returns:
            list: Lista de diccionarios con datos de clientes
        """
        try:
            consulta = """
            SELECT 
                id_cliente,
                nombre,
                apellido,
                telefono,
                direccion,
                email,
                observaciones,
                estado_cliente,
                es_incobrable,
                tiene_incobrables,
                total_incobrables,
                confiabilidad_pago,
                fecha_registro
            FROM clientes
            WHERE activo = 1
            """
            
            parametros = []
            
            # Filtro por búsqueda
            if busqueda:
                consulta += """ AND (
                    nombre LIKE ? OR 
                    apellido LIKE ? OR
                    telefono LIKE ? OR 
                    direccion LIKE ? OR
                    email LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param])
            
            # Ordenamiento
            if orden == "fecha_registro":
                consulta += " ORDER BY fecha_registro DESC"
            elif orden == "deuda":
                consulta += " ORDER BY total_incobrables DESC"
            else:
                consulta += " ORDER BY apellido ASC, nombre ASC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar clientes: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_cliente_por_id(id_cliente):
        """
        Obtiene un cliente por su ID
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            dict: Datos del cliente o None
        """
        try:
            consulta = """
            SELECT 
                id_cliente,
                nombre,
                apellido,
                telefono,
                direccion,
                email,
                observaciones,
                estado_cliente,
                es_incobrable,
                tiene_incobrables,
                total_incobrables,
                confiabilidad_pago,
                fecha_registro
            FROM clientes
            WHERE id_cliente = ?
            """
            
            return db.obtener_uno(consulta, (id_cliente,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener cliente: {e}", "ERROR")
            return None
    
    @staticmethod
    def crear_cliente(nombre, apellido, telefono, direccion, email, id_usuario):
        """
        Crea un nuevo cliente
        
        Args:
            nombre (str): Nombre del cliente
            apellido (str): Apellido del cliente
            telefono (str): Teléfono
            direccion (str): Dirección
            email (str): Email
            id_usuario (int): ID del usuario que crea el cliente
            
        Returns:
            tuple: (exito, mensaje, id_cliente_nuevo)
        """
        try:
            # Validar nombre
            if not nombre or not nombre.strip():
                return False, "El nombre es obligatorio", None
            
            # Validar apellido
            if not apellido or not apellido.strip():
                return False, "El apellido es obligatorio", None
            
            # Validar teléfono
            es_valido, mensaje_error = validar_telefono(telefono)
            if not es_valido:
                return False, mensaje_error, None
            
            # Limpiar teléfono
            telefono_limpio = limpiar_telefono(telefono)
            
            # Validar email si fue proporcionado
            if email and email.strip():
                es_valido, mensaje_error = validar_email(email)
                if not es_valido:
                    return False, mensaje_error, None
            
            # Verificar si ya existe un cliente con ese teléfono
            consulta_verificar = "SELECT COUNT(*) as total FROM clientes WHERE telefono = ?"
            resultado = db.obtener_uno(consulta_verificar, (telefono_limpio,))
            
            if resultado and resultado['total'] > 0:
                return False, "Ya existe un cliente con ese número de teléfono", None
            
            # Insertar cliente
            consulta = """
            INSERT INTO clientes (
                nombre, apellido, telefono, direccion, email, 
                observaciones, estado_cliente, es_incobrable, tiene_incobrables, total_incobrables, 
                confiabilidad_pago, fecha_registro
            )
            VALUES (?, ?, ?, ?, ?, '', 'Nuevo', 0, 0, 0.0, 'Bueno', ?)
            """
            
            id_nuevo = db.ejecutar_consulta(
                consulta,
                (nombre.strip(), apellido.strip(), telefono_limpio, direccion.strip(), email.strip(), datetime.now())
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Clientes",
                id_registro=id_nuevo,
                motivo=f"Creación de cliente '{apellido}, {nombre}'"
            )
            
            config.guardar_log(f"Cliente '{apellido}, {nombre}' creado por usuario ID {id_usuario}", "INFO")
            return True, "Cliente creado exitosamente", id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al crear cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def modificar_cliente(id_cliente, nombre, apellido, telefono, direccion, email, id_usuario):
        """
        Modifica los datos de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            nombre (str): Nuevo nombre
            apellido (str): Nuevo apellido
            telefono (str): Nuevo teléfono
            direccion (str): Nueva dirección
            email (str): Nuevo email
            id_usuario (int): ID del usuario que modifica
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Validar nombre
            if not nombre or not nombre.strip():
                return False, "El nombre es obligatorio"
            
            # Validar apellido
            if not apellido or not apellido.strip():
                return False, "El apellido es obligatorio"
            
            # Validar teléfono
            es_valido, mensaje_error = validar_telefono(telefono)
            if not es_valido:
                return False, mensaje_error
            
            # Limpiar teléfono
            telefono_limpio = limpiar_telefono(telefono)
            
            # Validar email si fue proporcionado
            if email and email.strip():
                es_valido, mensaje_error = validar_email(email)
                if not es_valido:
                    return False, mensaje_error
            
            # Obtener datos anteriores
            cliente_anterior = ModuloClientes.obtener_cliente_por_id(id_cliente)
            if not cliente_anterior:
                return False, "Cliente no encontrado"
            
            # Verificar si el teléfono ya existe (excluyendo el cliente actual)
            consulta_verificar = """
            SELECT COUNT(*) as total 
            FROM clientes 
            WHERE telefono = ? AND id_cliente != ?
            """
            resultado = db.obtener_uno(consulta_verificar, (telefono_limpio, id_cliente))
            
            if resultado and resultado['total'] > 0:
                return False, "Ya existe otro cliente con ese número de teléfono"
            
            # Actualizar cliente
            consulta = """
            UPDATE clientes
            SET nombre = ?, apellido = ?, telefono = ?, direccion = ?, email = ?
            WHERE id_cliente = ?
            """
            
            db.ejecutar_consulta(consulta, (
                nombre.strip(), 
                apellido.strip(), 
                telefono_limpio, 
                direccion.strip(), 
                email.strip() if email else "", 
                id_cliente
            ))
            
            # Registrar cambios en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            
            if cliente_anterior['nombre'] != nombre.strip():
                registrar_accion_auditoria(
                    id_usuario=id_usuario,
                    accion="Modificar",
                    modulo="Clientes",
                    id_registro=id_cliente,
                    campo_modificado="nombre",
                    valor_anterior=cliente_anterior['nombre'],
                    valor_nuevo=nombre.strip()
                )
            
            if cliente_anterior.get('apellido', '') != apellido.strip():
                registrar_accion_auditoria(
                    id_usuario=id_usuario,
                    accion="Modificar",
                    modulo="Clientes",
                    id_registro=id_cliente,
                    campo_modificado="apellido",
                    valor_anterior=cliente_anterior.get('apellido', ''),
                    valor_nuevo=apellido.strip()
                )
            
            if cliente_anterior['telefono'] != telefono_limpio:
                registrar_accion_auditoria(
                    id_usuario=id_usuario,
                    accion="Modificar",
                    modulo="Clientes",
                    id_registro=id_cliente,
                    campo_modificado="telefono",
                    valor_anterior=cliente_anterior['telefono'],
                    valor_nuevo=telefono_limpio
                )
            
            config.guardar_log(f"Cliente ID {id_cliente} ({apellido}, {nombre}) modificado por usuario ID {id_usuario}", "INFO")
            return True, "Cliente modificado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al modificar cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def marcar_deuda_incobrable(id_cliente, monto, motivo, observaciones, id_usuario):
        """
        Marca una deuda como incobrable
        
        Args:
            id_cliente (int): ID del cliente
            monto (float): Monto de la deuda
            motivo (str): Motivo de la deuda incobrable
            observaciones (str): Observaciones adicionales
            id_usuario (int): ID del usuario que marca
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Solo admin puede marcar incobrables
            if not config.es_admin:
                return False, "Solo los administradores pueden marcar deudas como incobrables"
            
            # Obtener cliente
            cliente = ModuloClientes.obtener_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente no encontrado"
            
            # Actualizar cliente
            nuevo_total = cliente['total_incobrables'] + monto
            
            consulta = """
            UPDATE clientes
            SET tiene_incobrables = 1,
                total_incobrables = ?,
                confiabilidad_pago = 'Malo'
            WHERE id_cliente = ?
            """
            
            db.ejecutar_consulta(consulta, (nuevo_total, id_cliente))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Clientes",
                id_registro=id_cliente,
                campo_modificado="tiene_incobrables",
                valor_anterior=str(cliente['tiene_incobrables']),
                valor_nuevo="1",
                motivo=f"Deuda incobrable: ${monto:.2f} - {motivo}. {observaciones}",
                es_critica=True
            )
            
            config.guardar_log(
                f"Cliente ID {id_cliente} marcado con deuda incobrable de ${monto:.2f} por usuario ID {id_usuario}", 
                "WARNING"
            )
            
            return True, f"Deuda de ${monto:.2f} marcada como incobrable"
            
        except Exception as e:
            config.guardar_log(f"Error al marcar deuda incobrable: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def cambiar_estado_cliente(id_cliente, nuevo_estado, id_usuario, motivo=""):
        """
        Cambia manualmente el estado de un cliente (solo Admin)
        
        Args:
            id_cliente (int): ID del cliente
            nuevo_estado (str): Nuevo estado ('Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable')
            id_usuario (int): ID del usuario que hace el cambio
            motivo (str): Motivo del cambio
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Validar estado
            estados_validos = ['Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable']
            if nuevo_estado not in estados_validos:
                return False, "Estado inválido"
            
            # Obtener estado actual
            cliente = ModuloClientes.obtener_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente no encontrado"
            
            estado_anterior = cliente.get('estado_cliente', 'Nuevo')
            
            # Actualizar estado
            consulta = "UPDATE clientes SET estado_cliente = ? WHERE id_cliente = ?"
            db.ejecutar_consulta(consulta, (nuevo_estado, id_cliente))
            
            # Si se marca como Incobrable, actualizar es_incobrable
            if nuevo_estado == 'Incobrable':
                db.ejecutar_consulta(
                    "UPDATE clientes SET es_incobrable = 1 WHERE id_cliente = ?",
                    (id_cliente,)
                )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            motivo_completo = f"Cambio de estado: '{estado_anterior}' → '{nuevo_estado}'"
            if motivo:
                motivo_completo += f" - {motivo}"
            
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Clientes",
                id_registro=id_cliente,
                campo_modificado="estado_cliente",
                valor_anterior=estado_anterior,
                valor_nuevo=nuevo_estado,
                motivo=motivo_completo,
                es_critica=True
            )
            
            config.guardar_log(
                f"Estado de cliente ID {id_cliente} cambiado de '{estado_anterior}' a '{nuevo_estado}' por usuario ID {id_usuario}",
                "INFO"
            )
            
            return True, f"Estado cambiado a '{nuevo_estado}' exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al cambiar estado de cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_estadisticas_clientes():
        """
        Obtiene estadísticas generales de clientes
        
        Returns:
            dict: Estadísticas de clientes
        """
        try:
            estadisticas = {}
            
            # Total de clientes
            consulta_total = "SELECT COUNT(*) as total FROM clientes"
            resultado = db.obtener_uno(consulta_total)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Clientes con deudas
            consulta_deudas = "SELECT COUNT(*) as total FROM clientes WHERE tiene_incobrables = 1"
            resultado = db.obtener_uno(consulta_deudas)
            estadisticas['con_deudas'] = resultado['total'] if resultado else 0
            
            # Total de deudas incobrables
            consulta_monto = "SELECT SUM(total_incobrables) as total FROM clientes"
            resultado = db.obtener_uno(consulta_monto)
            estadisticas['total_incobrables'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            # Clientes por confiabilidad
            consulta_buenos = "SELECT COUNT(*) as total FROM clientes WHERE confiabilidad_pago = 'Bueno'"
            resultado = db.obtener_uno(consulta_buenos)
            estadisticas['buenos'] = resultado['total'] if resultado else 0
            
            consulta_regulares = "SELECT COUNT(*) as total FROM clientes WHERE confiabilidad_pago = 'Regular'"
            resultado = db.obtener_uno(consulta_regulares)
            estadisticas['regulares'] = resultado['total'] if resultado else 0
            
            consulta_malos = "SELECT COUNT(*) as total FROM clientes WHERE confiabilidad_pago = 'Malo'"
            resultado = db.obtener_uno(consulta_malos)
            estadisticas['malos'] = resultado['total'] if resultado else 0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de clientes: {e}", "ERROR")
            return {
                'total': 0,
                'con_deudas': 0,
                'total_incobrables': 0.0,
                'buenos': 0,
                'regulares': 0,
                'malos': 0
            }
    
    @staticmethod
    def obtener_equipos_cliente(id_cliente):
        """
        Obtiene todos los equipos de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            list: Lista de equipos del cliente
        """
        try:
            consulta = """
            SELECT 
                id_equipo,
                tipo_dispositivo,
                marca,
                modelo,
                identificador,
                estado_actual,
                fecha_ingreso
            FROM equipos
            WHERE id_cliente = ?
            ORDER BY fecha_ingreso DESC
            """
            
            return db.obtener_todos(consulta, (id_cliente,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener equipos del cliente: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_notas_cliente(id_cliente):
        """
        Obtiene todas las notas de un cliente
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            list: Lista de notas ordenadas por fecha
        """
        try:
            consulta = """
            SELECT 
                n.id_nota,
                n.nota,
                n.fecha_hora,
                n.editado,
                u.nombre as usuario_nombre
            FROM historial_notas n
            LEFT JOIN usuarios u ON n.id_usuario = u.id_usuario
            WHERE n.modulo = 'Clientes' AND n.id_registro = ?
            ORDER BY n.fecha_hora DESC
            """
            
            return db.obtener_todos(consulta, (id_cliente,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener notas del cliente: {e}", "ERROR")
            return []
    
    @staticmethod
    def agregar_nota_cliente(id_cliente, nota, id_usuario):
        """
        Agrega una nota a un cliente
        
        Args:
            id_cliente (int): ID del cliente
            nota (str): Texto de la nota
            id_usuario (int): ID del usuario que agrega la nota
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not nota or nota.strip() == "":
                return False, "La nota no puede estar vacía"
            
            consulta = """
            INSERT INTO historial_notas (modulo, id_registro, nota, id_usuario, fecha_hora, editado)
            VALUES (?, ?, ?, ?, ?, 0)
            """
            
            db.ejecutar_consulta(consulta, ("Clientes", id_cliente, nota.strip(), id_usuario, datetime.now()))
            
            config.guardar_log(f"Nota agregada al cliente ID {id_cliente} por usuario ID {id_usuario}", "INFO")
            return True, "Nota agregada exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al agregar nota: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def buscar_cliente_por_telefono(telefono):
        """
        Busca un cliente por su número de teléfono
        
        Args:
            telefono (str): Teléfono a buscar
            
        Returns:
            dict: Cliente encontrado o None
        """
        try:
            telefono_limpio = limpiar_telefono(telefono)
            
            consulta = """
            SELECT 
                id_cliente,
                nombre,
                telefono,
                direccion,
                email,
                tiene_incobrables,
                total_incobrables,
                confiabilidad_pago
            FROM clientes
            WHERE telefono LIKE ?
            """
            
            return db.obtener_uno(consulta, (f"%{telefono_limpio}%",))
            
        except Exception as e:
            config.guardar_log(f"Error al buscar cliente por teléfono: {e}", "ERROR")
            return None

    @staticmethod
    def eliminar_cliente(id_cliente, id_usuario):
        """
        Elimina (desactiva) un cliente
        
        Args:
            id_cliente (int): ID del cliente
            id_usuario (int): ID del usuario que elimina
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Verificar que no tenga equipos activos
            consulta_equipos = """
            SELECT COUNT(*) as total
            FROM equipos
            WHERE id_cliente = ? AND activo = 1
            """
            
            resultado = db.obtener_uno(consulta_equipos, (id_cliente,))
            
            if resultado and resultado['total'] > 0:
                return False, f"No se puede eliminar: el cliente tiene {resultado['total']} equipo(s) activo(s)"
            
            # Soft delete - marcar como inactivo
            consulta = """
            UPDATE clientes
            SET activo = 0
            WHERE id_cliente = ?
            """
            
            db.ejecutar_consulta(consulta, (id_cliente,))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Eliminar",
                modulo="Clientes",
                id_registro=id_cliente,
                motivo="Cliente desactivado"
            )
            
            config.guardar_log(f"Cliente ID {id_cliente} desactivado", "INFO")
            return True, "Cliente eliminado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al eliminar cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def buscar_clientes(termino):
        """
        Busca clientes por nombre, teléfono o dirección
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            list: Lista de clientes que coinciden
        """
        try:
            if not termino or len(termino) < 2:
                return []
            
            consulta = """
            SELECT 
                id_cliente,
                nombre,
                telefono,
                direccion,
                email
            FROM clientes
            WHERE activo = 1
            AND (
                nombre LIKE ? OR
                telefono LIKE ? OR
                direccion LIKE ? OR
                email LIKE ?
            )
            ORDER BY nombre
            LIMIT 20
            """
            
            termino_busqueda = f"%{termino}%"
            parametros = [termino_busqueda] * 4
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al buscar clientes: {e}", "ERROR")
            return []
