# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE USUARIOS
============================================================================
Lógica de negocio para gestión de usuarios del sistema
============================================================================
"""

from datetime import datetime
from base_datos.conexion import db
from sistema_base.seguridad import (encriptar_contrasena, crear_usuario, 
                                     resetear_contrasena_admin, 
                                     validar_contrasena_temporal,
                                     generar_contrasena_temporal)
from sistema_base.validadores import validar_nombre, validar_requerido
from sistema_base.configuracion import config


class ModuloUsuarios:
    """Clase para manejar la lógica de negocio de usuarios"""
    
    @staticmethod
    def listar_usuarios(solo_activos=False, busqueda=""):
        """
        Lista todos los usuarios del sistema
        
        Args:
            solo_activos (bool): Si True, solo muestra usuarios activos
            busqueda (str): Texto para buscar en nombre o username
            
        Returns:
            list: Lista de diccionarios con datos de usuarios
        """
        try:
            consulta = """
            SELECT 
                id_usuario,
                nombre,
                username,
                rol,
                activo,
                fecha_creacion,
                CASE WHEN activo = 1 THEN 'Activo' ELSE 'Inactivo' END as estado
            FROM usuarios
            WHERE 1=1
            """
            
            parametros = []
            
            # Filtro por activos
            if solo_activos:
                consulta += " AND activo = 1"
            
            # Filtro por búsqueda
            if busqueda:
                consulta += " AND (nombre LIKE ? OR username LIKE ?)"
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param, busqueda_param])
            
            consulta += " ORDER BY nombre ASC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar usuarios: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_usuario_por_id(id_usuario):
        """
        Obtiene un usuario por su ID
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            dict: Datos del usuario o None
        """
        try:
            consulta = """
            SELECT 
                id_usuario,
                nombre,
                username,
                rol,
                activo,
                fecha_creacion
            FROM usuarios
            WHERE id_usuario = ?
            """
            
            return db.obtener_uno(consulta, (id_usuario,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener usuario: {e}", "ERROR")
            return None
    
    @staticmethod
    def crear_usuario_completo(nombre, username, password_temporal, rol, id_usuario_admin):
        """
        Crea un nuevo usuario en el sistema
        
        Args:
            nombre (str): Nombre completo del usuario
            username (str): Nombre de usuario para login
            password_temporal (str): Contraseña temporal (6-10 caracteres)
            rol (str): Rol del usuario ('admin' o 'tecnico')
            id_usuario_admin (int): ID del admin que crea el usuario
            
        Returns:
            tuple: (exito, mensaje, id_usuario_nuevo)
        """
        try:
            # Validar nombre
            es_valido, mensaje_error = validar_nombre(nombre)
            if not es_valido:
                return False, mensaje_error, None
            
            # Validar username
            es_valido, mensaje_error = validar_requerido(username, "Nombre de usuario")
            if not es_valido:
                return False, mensaje_error, None
            
            # Validar que username no tenga espacios
            if " " in username:
                return False, "El nombre de usuario no puede contener espacios", None
            
            # Validar rol
            if rol not in ['admin', 'tecnico']:
                return False, "El rol debe ser 'admin' o 'tecnico'", None
            
            # Llamar a la función de seguridad
            return crear_usuario(nombre, username, password_temporal, rol, id_usuario_admin)
            
        except Exception as e:
            config.guardar_log(f"Error al crear usuario: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def modificar_usuario(id_usuario, nombre, rol, id_usuario_modifica):
        """
        Modifica los datos de un usuario
        
        Args:
            id_usuario (int): ID del usuario a modificar
            nombre (str): Nuevo nombre
            rol (str): Nuevo rol
            id_usuario_modifica (int): ID del usuario que realiza la modificación
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Validar que quien modifica es admin
            if not config.es_admin:
                return False, "Solo los administradores pueden modificar usuarios"
            
            # Validar nombre
            es_valido, mensaje_error = validar_nombre(nombre)
            if not es_valido:
                return False, mensaje_error
            
            # Validar rol
            if rol not in ['admin', 'tecnico']:
                return False, "El rol debe ser 'admin' o 'tecnico'"
            
            # Obtener datos anteriores
            usuario_anterior = ModuloUsuarios.obtener_usuario_por_id(id_usuario)
            if not usuario_anterior:
                return False, "Usuario no encontrado"
            
            # Actualizar usuario
            consulta = """
            UPDATE usuarios
            SET nombre = ?, rol = ?
            WHERE id_usuario = ?
            """
            
            db.ejecutar_consulta(consulta, (nombre, rol, id_usuario))
            
            # Registrar en auditoría si cambió el nombre
            if usuario_anterior['nombre'] != nombre:
                from sistema_base.seguridad import registrar_accion_auditoria
                registrar_accion_auditoria(
                    id_usuario=id_usuario_modifica,
                    accion="Modificar",
                    modulo="Usuarios",
                    id_registro=id_usuario,
                    campo_modificado="nombre",
                    valor_anterior=usuario_anterior['nombre'],
                    valor_nuevo=nombre,
                    motivo="Modificación de usuario"
                )
            
            # Registrar en auditoría si cambió el rol
            if usuario_anterior['rol'] != rol:
                from sistema_base.seguridad import registrar_accion_auditoria
                registrar_accion_auditoria(
                    id_usuario=id_usuario_modifica,
                    accion="Modificar",
                    modulo="Usuarios",
                    id_registro=id_usuario,
                    campo_modificado="rol",
                    valor_anterior=usuario_anterior['rol'],
                    valor_nuevo=rol,
                    motivo="Modificación de usuario",
                    es_critica=True
                )
            
            config.guardar_log(f"Usuario ID {id_usuario} modificado por usuario ID {id_usuario_modifica}", "INFO")
            return True, "Usuario modificado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al modificar usuario: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def actualizar_foto_perfil(id_usuario, foto_data):
        """
        Actualiza la foto de perfil de un usuario
        
        Args:
            id_usuario (int): ID del usuario
            foto_data (bytes): Datos binarios de la imagen o None para eliminar
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            consulta = """
            UPDATE usuarios
            SET foto_perfil = ?
            WHERE id_usuario = ?
            """
            
            db.ejecutar_consulta(consulta, (foto_data, id_usuario))
            
            if foto_data is None or foto_data == b'':
                config.guardar_log(f"Foto de perfil eliminada para usuario ID {id_usuario}", "INFO")
                return True, "Foto eliminada exitosamente"
            else:
                config.guardar_log(f"Foto de perfil actualizada para usuario ID {id_usuario}", "INFO")
                return True, "Foto actualizada exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar foto: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def cambiar_estado_usuario(id_usuario, activo, id_usuario_modifica):
        """
        Activa o desactiva un usuario
        
        Args:
            id_usuario (int): ID del usuario
            activo (bool): True para activar, False para desactivar
            id_usuario_modifica (int): ID del usuario que realiza la acción
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Validar que quien modifica es admin
            if not config.es_admin:
                return False, "Solo los administradores pueden cambiar el estado de usuarios"
            
            # No permitir desactivar el propio usuario
            if id_usuario == id_usuario_modifica:
                return False, "No puedes desactivar tu propio usuario"
            
            # Obtener datos anteriores
            usuario = ModuloUsuarios.obtener_usuario_por_id(id_usuario)
            if not usuario:
                return False, "Usuario no encontrado"
            
            # Actualizar estado
            consulta = """
            UPDATE usuarios
            SET activo = ?
            WHERE id_usuario = ?
            """
            
            db.ejecutar_consulta(consulta, (1 if activo else 0, id_usuario))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario_modifica,
                accion="Modificar",
                modulo="Usuarios",
                id_registro=id_usuario,
                campo_modificado="activo",
                valor_anterior="Activo" if usuario['activo'] else "Inactivo",
                valor_nuevo="Activo" if activo else "Inactivo",
                motivo=f"Usuario {'activado' if activo else 'desactivado'}",
                es_critica=True
            )
            
            accion = "activado" if activo else "desactivado"
            config.guardar_log(f"Usuario ID {id_usuario} {accion} por usuario ID {id_usuario_modifica}", "INFO")
            return True, f"Usuario {accion} exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al cambiar estado de usuario: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def resetear_contrasena(id_usuario_objetivo, nueva_contrasena, id_usuario_admin):
        """
        Resetea la contraseña de un usuario (wrapper de la función de seguridad)
        
        Args:
            id_usuario_objetivo (int): ID del usuario a resetear
            nueva_contrasena (str): Nueva contraseña temporal
            id_usuario_admin (int): ID del admin que resetea
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            return resetear_contrasena_admin(id_usuario_admin, id_usuario_objetivo, nueva_contrasena)
            
        except Exception as e:
            config.guardar_log(f"Error al resetear contraseña: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_estadisticas_usuarios():
        """
        Obtiene estadísticas generales de usuarios
        
        Returns:
            dict: Estadísticas de usuarios
        """
        try:
            estadisticas = {}
            
            # Total de usuarios
            consulta_total = "SELECT COUNT(*) as total FROM usuarios"
            resultado = db.obtener_uno(consulta_total)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Usuarios activos
            consulta_activos = "SELECT COUNT(*) as total FROM usuarios WHERE activo = 1"
            resultado = db.obtener_uno(consulta_activos)
            estadisticas['activos'] = resultado['total'] if resultado else 0
            
            # Usuarios inactivos
            estadisticas['inactivos'] = estadisticas['total'] - estadisticas['activos']
            
            # Usuarios por rol
            consulta_admin = "SELECT COUNT(*) as total FROM usuarios WHERE rol = 'admin' AND activo = 1"
            resultado = db.obtener_uno(consulta_admin)
            estadisticas['administradores'] = resultado['total'] if resultado else 0
            
            consulta_tecnico = "SELECT COUNT(*) as total FROM usuarios WHERE rol = 'tecnico' AND activo = 1"
            resultado = db.obtener_uno(consulta_tecnico)
            estadisticas['tecnicos'] = resultado['total'] if resultado else 0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de usuarios: {e}", "ERROR")
            return {
                'total': 0,
                'activos': 0,
                'inactivos': 0,
                'administradores': 0,
                'tecnicos': 0
            }
    
    @staticmethod
    def obtener_historial_usuario(id_usuario, limite=50):
        """
        Obtiene el historial de acciones de un usuario
        
        Args:
            id_usuario (int): ID del usuario
            limite (int): Cantidad máxima de registros a retornar
            
        Returns:
            list: Lista de acciones del usuario
        """
        try:
            consulta = """
            SELECT 
                id_log,
                fecha_hora,
                accion,
                modulo,
                id_registro,
                campo_modificado,
                valor_anterior,
                valor_nuevo,
                motivo_modificacion,
                es_accion_critica
            FROM logs_sistema
            WHERE id_usuario = ?
            ORDER BY fecha_hora DESC
            LIMIT ?
            """
            
            return db.obtener_todos(consulta, (id_usuario, limite))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener historial de usuario: {e}", "ERROR")
            return []
    
    @staticmethod
    def validar_datos_usuario(nombre, username, password_temporal, rol):
        """
        Valida los datos de un usuario antes de crearlo
        
        Args:
            nombre (str): Nombre completo
            username (str): Nombre de usuario
            password_temporal (str): Contraseña temporal
            rol (str): Rol del usuario
            
        Returns:
            tuple: (es_valido, mensaje_error)
        """
        # Validar nombre
        es_valido, mensaje = validar_nombre(nombre)
        if not es_valido:
            return False, mensaje
        
        # Validar username
        es_valido, mensaje = validar_requerido(username, "Nombre de usuario")
        if not es_valido:
            return False, mensaje
        
        if " " in username:
            return False, "El nombre de usuario no puede contener espacios"
        
        if len(username) < 4:
            return False, "El nombre de usuario debe tener al menos 4 caracteres"
        
        # Validar contraseña temporal
        es_valida, mensaje = validar_contrasena_temporal(password_temporal)
        if not es_valida:
            return False, mensaje
        
        # Validar rol
        if rol not in ['admin', 'tecnico']:
            return False, "El rol debe ser 'admin' o 'tecnico'"
        
        return True, ""
