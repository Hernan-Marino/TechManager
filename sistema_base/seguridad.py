# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - SISTEMA DE SEGURIDAD
============================================================================
Maneja la autenticación de usuarios y encriptación de contraseñas
============================================================================
"""

import bcrypt
from datetime import datetime
from base_datos.conexion import db
from sistema_base.configuracion import config


def encriptar_contrasena(contrasena):
    """
    Encripta una contraseña usando bcrypt
    
    Args:
        contrasena (str): Contraseña en texto plano
        
    Returns:
        str: Contraseña encriptada
    """
    password_bytes = contrasena.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return password_hash.decode('utf-8')


def verificar_contrasena(contrasena, password_hash):
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        contrasena (str): Contraseña en texto plano
        password_hash (str): Hash almacenado en la base de datos
        
    Returns:
        bool: True si coinciden, False si no
    """
    password_bytes = contrasena.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def autenticar_usuario(username, contrasena):
    """
    Autentica un usuario verificando sus credenciales
    
    Args:
        username (str): Nombre de usuario
        contrasena (str): Contraseña en texto plano
        
    Returns:
        dict: Datos del usuario si es válido, None si no
    """
    try:
        # Buscar usuario en la base de datos
        consulta = """
        SELECT id_usuario, nombre, username, password_hash, rol, activo, primer_login
        FROM usuarios
        WHERE username = ? AND activo = 1
        """
        
        usuario = db.obtener_uno(consulta, (username,))
        
        if usuario is None:
            config.guardar_log(f"Intento de login fallido: usuario '{username}' no encontrado", "WARNING")
            return None
        
        # Verificar contraseña
        if verificar_contrasena(contrasena, usuario['password_hash']):
            # Login exitoso
            registrar_login(usuario['id_usuario'], usuario['username'])
            config.guardar_log(f"Login exitoso: {username} ({usuario['rol']})", "INFO")
            
            # Establecer usuario actual en la configuración
            config.establecer_usuario(usuario['username'], usuario['rol'])
            
            return {
                'id_usuario': usuario['id_usuario'],
                'nombre': usuario['nombre'],
                'username': usuario['username'],
                'rol': usuario['rol'],
                'primer_login': usuario['primer_login']
            }
        else:
            config.guardar_log(f"Intento de login fallido: contraseña incorrecta para '{username}'", "WARNING")
            return None
            
    except Exception as e:
        config.guardar_log(f"Error al autenticar usuario: {e}", "ERROR")
        return None


def registrar_login(id_usuario, username):
    """
    Registra un login exitoso en el log del sistema
    
    Args:
        id_usuario (int): ID del usuario
        username (str): Nombre de usuario
    """
    try:
        consulta = """
        INSERT INTO logs_sistema (
            id_usuario, accion, modulo, fecha_hora, es_accion_critica
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        db.ejecutar_consulta(
            consulta,
            (id_usuario, "Login", "Sistema", datetime.now(), 0)
        )
    except Exception as e:
        config.guardar_log(f"Error al registrar login: {e}", "ERROR")


def registrar_logout(id_usuario):
    """
    Registra un logout en el log del sistema
    
    Args:
        id_usuario (int): ID del usuario
    """
    try:
        consulta = """
        INSERT INTO logs_sistema (
            id_usuario, accion, modulo, fecha_hora, es_accion_critica
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        db.ejecutar_consulta(
            consulta,
            (id_usuario, "Logout", "Sistema", datetime.now(), 0)
        )
        
        config.guardar_log(f"Logout: usuario ID {id_usuario}", "INFO")
    except Exception as e:
        config.guardar_log(f"Error al registrar logout: {e}", "ERROR")


def cambiar_contrasena(id_usuario, contrasena_actual, contrasena_nueva):
    """
    Cambia la contraseña de un usuario
    
    Args:
        id_usuario (int): ID del usuario
        contrasena_actual (str): Contraseña actual
        contrasena_nueva (str): Nueva contraseña
        
    Returns:
        tuple: (exito, mensaje)
    """
    try:
        # Obtener usuario
        consulta = "SELECT password_hash FROM usuarios WHERE id_usuario = ?"
        usuario = db.obtener_uno(consulta, (id_usuario,))
        
        if usuario is None:
            return False, "Usuario no encontrado"
        
        # Verificar contraseña actual
        if not verificar_contrasena(contrasena_actual, usuario['password_hash']):
            config.guardar_log(f"Intento fallido de cambio de contraseña: contraseña actual incorrecta", "WARNING")
            return False, "La contraseña actual es incorrecta"
        
        # Encriptar nueva contraseña
        nuevo_hash = encriptar_contrasena(contrasena_nueva)
        
        # Actualizar en la base de datos Y marcar primer_login como False
        consulta_update = """
        UPDATE usuarios 
        SET password_hash = ?, primer_login = 0
        WHERE id_usuario = ?
        """
        
        db.ejecutar_consulta(consulta_update, (nuevo_hash, id_usuario))
        
        # Registrar en el log
        registrar_accion_auditoria(
            id_usuario=id_usuario,
            accion="Modificar",
            modulo="Usuarios",
            id_registro=id_usuario,
            campo_modificado="password_hash",
            valor_anterior="[ENCRIPTADO]",
            valor_nuevo="[ENCRIPTADO]",
            motivo="Cambio de contraseña",
            es_critica=True
        )
        
        config.guardar_log(f"Contraseña cambiada para usuario ID {id_usuario}", "INFO")
        return True, "Contraseña cambiada exitosamente"
        
    except Exception as e:
        config.guardar_log(f"Error al cambiar contraseña: {e}", "ERROR")
        return False, f"Error: {str(e)}"


def resetear_contrasena_admin(id_usuario_admin, id_usuario_objetivo, nueva_contrasena):
    """
    Permite a un admin resetear la contraseña de otro usuario
    Automáticamente marca primer_login = 1 para forzar cambio obligatorio
    
    Args:
        id_usuario_admin (int): ID del admin que realiza el reseteo
        id_usuario_objetivo (int): ID del usuario a resetear
        nueva_contrasena (str): Nueva contraseña temporal (6-10 caracteres)
        
    Returns:
        tuple: (exito, mensaje)
    """
    try:
        # Verificar que quien ejecuta es admin
        consulta = "SELECT rol FROM usuarios WHERE id_usuario = ?"
        usuario_admin = db.obtener_uno(consulta, (id_usuario_admin,))
        
        if usuario_admin is None or usuario_admin['rol'] != 'admin':
            return False, "Solo los administradores pueden resetear contraseñas"
        
        # Validar contraseña temporal (6-10 caracteres alfanuméricos)
        es_valida, mensaje_error = validar_contrasena_temporal(nueva_contrasena)
        if not es_valida:
            return False, mensaje_error
        
        # Obtener datos del usuario objetivo
        consulta_objetivo = "SELECT username FROM usuarios WHERE id_usuario = ?"
        usuario_objetivo = db.obtener_uno(consulta_objetivo, (id_usuario_objetivo,))
        
        if usuario_objetivo is None:
            return False, "Usuario no encontrado"
        
        # Encriptar nueva contraseña
        nuevo_hash = encriptar_contrasena(nueva_contrasena)
        
        # Actualizar contraseña Y marcar primer_login = 1 (forzar cambio)
        consulta_update = """
        UPDATE usuarios 
        SET password_hash = ?, primer_login = 1
        WHERE id_usuario = ?
        """
        
        db.ejecutar_consulta(consulta_update, (nuevo_hash, id_usuario_objetivo))
        
        # Registrar en el log (ACCIÓN CRÍTICA)
        registrar_accion_auditoria(
            id_usuario=id_usuario_admin,
            accion="Modificar",
            modulo="Usuarios",
            id_registro=id_usuario_objetivo,
            campo_modificado="password_hash",
            valor_anterior="[ENCRIPTADO]",
            valor_nuevo="[TEMPORAL]",
            motivo=f"Admin reseteó contraseña del usuario '{usuario_objetivo['username']}' (olvidó su contraseña)",
            es_critica=True
        )
        
        config.guardar_log(
            f"Admin ID {id_usuario_admin} reseteó contraseña del usuario ID {id_usuario_objetivo} ('{usuario_objetivo['username']}')", 
            "WARNING"
        )
        
        return True, f"Contraseña reseteada exitosamente.\n\nContraseña temporal: {nueva_contrasena}\n\nEl usuario DEBE cambiarla en su próximo login."
        
    except Exception as e:
        config.guardar_log(f"Error al resetear contraseña: {e}", "ERROR")
        return False, f"Error: {str(e)}"


def registrar_accion_auditoria(id_usuario, accion, modulo, id_registro=None, 
                                campo_modificado=None, valor_anterior=None, 
                                valor_nuevo=None, motivo=None, es_critica=False):
    """
    Registra una acción en el log de auditoría del sistema
    
    Args:
        id_usuario (int): ID del usuario que realiza la acción
        accion (str): Acción realizada (Crear, Modificar, Eliminar, etc.)
        modulo (str): Módulo donde se realizó la acción
        id_registro (int): ID del registro afectado
        campo_modificado (str): Campo que fue modificado
        valor_anterior (str): Valor anterior del campo
        valor_nuevo (str): Valor nuevo del campo
        motivo (str): Motivo o justificación de la acción
        es_critica (bool): Si es una acción crítica
    """
    try:
        consulta = """
        INSERT INTO logs_sistema (
            id_usuario, accion, modulo, id_registro, campo_modificado,
            valor_anterior, valor_nuevo, motivo_modificacion, 
            fecha_hora, es_accion_critica
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        db.ejecutar_consulta(
            consulta,
            (id_usuario, accion, modulo, id_registro, campo_modificado,
             valor_anterior, valor_nuevo, motivo, datetime.now(), es_critica)
        )
        
    except Exception as e:
        config.guardar_log(f"Error al registrar auditoría: {e}", "ERROR")


def verificar_permisos(rol_requerido):
    """
    Verifica si el usuario actual tiene los permisos necesarios
    
    Args:
        rol_requerido (str): Rol requerido ('admin' o 'tecnico')
        
    Returns:
        bool: True si tiene permisos, False si no
    """
    if rol_requerido == 'admin':
        return config.es_admin
    elif rol_requerido == 'tecnico':
        # Tanto admin como tecnico pueden hacer acciones de tecnico
        return config.usuario_actual is not None
    else:
        return False


def obtener_usuario_actual():
    """
    Obtiene los datos del usuario actualmente logueado
    
    Returns:
        dict: Datos del usuario o None si no hay sesión
    """
    if config.usuario_actual is None:
        return None
    
    try:
        consulta = """
        SELECT id_usuario, nombre, username, rol
        FROM usuarios
        WHERE username = ? AND activo = 1
        """
        
        return db.obtener_uno(consulta, (config.usuario_actual,))
        
    except Exception as e:
        config.guardar_log(f"Error al obtener usuario actual: {e}", "ERROR")
        return None


def crear_usuario(nombre, username, password_temporal, rol, id_usuario_admin):
    """
    Crea un nuevo usuario en el sistema (solo admin)
    
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
        # Validar que quien crea es admin
        if not config.es_admin:
            return False, "Solo los administradores pueden crear usuarios", None
        
        # Validar longitud de contraseña temporal (6-10 caracteres)
        if len(password_temporal) < 6 or len(password_temporal) > 10:
            return False, "La contraseña temporal debe tener entre 6 y 10 caracteres", None
        
        # Verificar que el username no exista
        consulta_verificar = "SELECT COUNT(*) as total FROM usuarios WHERE username = ?"
        resultado = db.obtener_uno(consulta_verificar, (username,))
        
        if resultado['total'] > 0:
            return False, f"El nombre de usuario '{username}' ya existe", None
        
        # Encriptar contraseña temporal
        password_hash = encriptar_contrasena(password_temporal)
        
        # Insertar usuario
        consulta_insertar = """
        INSERT INTO usuarios (nombre, username, password_hash, rol, activo, primer_login, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        id_nuevo = db.ejecutar_consulta(
            consulta_insertar,
            (nombre, username, password_hash, rol, 1, 1, datetime.now())
        )
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            id_usuario=id_usuario_admin,
            accion="Crear",
            modulo="Usuarios",
            id_registro=id_nuevo,
            motivo=f"Creación de usuario '{username}' con rol '{rol}'",
            es_critica=True
        )
        
        config.guardar_log(
            f"Usuario '{username}' creado por admin ID {id_usuario_admin}", 
            "INFO"
        )
        
        return True, "Usuario creado exitosamente", id_nuevo
        
    except Exception as e:
        config.guardar_log(f"Error al crear usuario: {e}", "ERROR")
        return False, f"Error: {str(e)}", None


def cambiar_contrasena_primer_login(id_usuario, contrasena_temporal, contrasena_nueva):
    """
    Cambia la contraseña en el primer login (obligatorio)
    NO requiere verificar la contraseña actual, solo validar que sea primer login
    
    Args:
        id_usuario (int): ID del usuario
        contrasena_temporal (str): Contraseña temporal para verificar
        contrasena_nueva (str): Nueva contraseña personal
        
    Returns:
        tuple: (exito, mensaje)
    """
    try:
        # Obtener usuario
        consulta = "SELECT password_hash, primer_login FROM usuarios WHERE id_usuario = ?"
        usuario = db.obtener_uno(consulta, (id_usuario,))
        
        if usuario is None:
            return False, "Usuario no encontrado"
        
        # Verificar que sea primer login
        if usuario['primer_login'] != 1:
            return False, "Este usuario ya cambió su contraseña inicial"
        
        # Verificar contraseña temporal
        if not verificar_contrasena(contrasena_temporal, usuario['password_hash']):
            config.guardar_log(f"Intento fallido de cambio primer login: contraseña temporal incorrecta", "WARNING")
            return False, "La contraseña temporal es incorrecta"
        
        # Validar nueva contraseña (mínimo 6 caracteres)
        if len(contrasena_nueva) < 6:
            return False, "La nueva contraseña debe tener al menos 6 caracteres"
        
        # Encriptar nueva contraseña
        nuevo_hash = encriptar_contrasena(contrasena_nueva)
        
        # Actualizar contraseña Y marcar primer_login como False
        consulta_update = """
        UPDATE usuarios 
        SET password_hash = ?, primer_login = 0
        WHERE id_usuario = ?
        """
        
        db.ejecutar_consulta(consulta_update, (nuevo_hash, id_usuario))
        
        # Registrar en el log
        registrar_accion_auditoria(
            id_usuario=id_usuario,
            accion="Modificar",
            modulo="Usuarios",
            id_registro=id_usuario,
            campo_modificado="password_hash",
            valor_anterior="[TEMPORAL]",
            valor_nuevo="[PERSONAL]",
            motivo="Cambio obligatorio de contraseña en primer login",
            es_critica=True
        )
        
        config.guardar_log(f"Usuario ID {id_usuario} cambió contraseña en primer login", "INFO")
        return True, "Contraseña cambiada exitosamente. Ahora puede usar el sistema."
        
    except Exception as e:
        config.guardar_log(f"Error al cambiar contraseña primer login: {e}", "ERROR")
        return False, f"Error: {str(e)}"


def validar_contrasena_temporal(password):
    """
    Valida que una contraseña temporal cumpla los requisitos
    
    Args:
        password (str): Contraseña a validar
        
    Returns:
        tuple: (es_valida, mensaje_error)
    """
    # Longitud: 6-10 caracteres
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 10:
        return False, "La contraseña no puede tener más de 10 caracteres"
    
    # Puede ser numérica, alfabética o alfanumérica (sin restricciones adicionales)
    # Solo caracteres alfanuméricos
    if not password.isalnum():
        return False, "La contraseña solo puede contener letras y números (sin espacios ni símbolos)"
    
    return True, ""


def generar_contrasena_temporal():
    """
    Genera una contraseña temporal aleatoria
    8 caracteres alfanuméricos (letras minúsculas y números)
    
    Returns:
        str: Contraseña temporal
    """
    import random
    import string
    
    # Caracteres permitidos: letras minúsculas y números
    caracteres = string.ascii_lowercase + string.digits
    
    # Generar contraseña de 8 caracteres
    password = ''.join(random.choice(caracteres) for _ in range(8))
    
    return password
