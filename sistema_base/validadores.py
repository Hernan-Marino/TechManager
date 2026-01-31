# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - VALIDADORES
============================================================================
Funciones para validar datos de entrada del usuario
============================================================================
"""

import re
from datetime import datetime
from sistema_base.constantes import (
    LONGITUD_MINIMA_CONTRASENA,
    LONGITUD_MAXIMA_NOMBRE,
    LONGITUD_MAXIMA_DIRECCION,
    LONGITUD_MAXIMA_EMAIL,
    LONGITUD_MAXIMA_TELEFONO,
    ERROR_CAMPO_OBLIGATORIO,
    ERROR_FORMATO_INVALIDO
)


def validar_requerido(valor, nombre_campo="Campo"):
    """
    Valida que un campo no esté vacío
    
    Args:
        valor: Valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if valor is None or str(valor).strip() == "":
        return False, f"{nombre_campo}: {ERROR_CAMPO_OBLIGATORIO}"
    return True, ""


def validar_longitud(valor, longitud_max, nombre_campo="Campo"):
    """
    Valida que un campo no exceda una longitud máxima
    
    Args:
        valor (str): Valor a validar
        longitud_max (int): Longitud máxima permitida
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if len(str(valor)) > longitud_max:
        return False, f"{nombre_campo}: No puede exceder {longitud_max} caracteres"
    return True, ""


def validar_nombre(nombre):
    """
    Valida un nombre (cliente, usuario, etc.)
    
    Args:
        nombre (str): Nombre a validar
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Validar que no esté vacío
    es_valido, mensaje = validar_requerido(nombre, "Nombre")
    if not es_valido:
        return es_valido, mensaje
    
    # Validar longitud
    es_valido, mensaje = validar_longitud(nombre, LONGITUD_MAXIMA_NOMBRE, "Nombre")
    if not es_valido:
        return es_valido, mensaje
    
    # Validar que solo contenga letras, espacios, puntos y guiones
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-]+$', nombre):
        return False, f"Nombre: {ERROR_FORMATO_INVALIDO} (solo letras, espacios, puntos y guiones)"
    
    return True, ""


def validar_telefono(telefono):
    """
    Valida un número de teléfono
    
    Args:
        telefono (str): Teléfono a validar
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Validar que no esté vacío
    es_valido, mensaje = validar_requerido(telefono, "Teléfono")
    if not es_valido:
        return es_valido, mensaje
    
    # Validar longitud
    es_valido, mensaje = validar_longitud(telefono, LONGITUD_MAXIMA_TELEFONO, "Teléfono")
    if not es_valido:
        return es_valido, mensaje
    
    # Validar que solo contenga números, espacios, guiones y paréntesis
    if not re.match(r'^[\d\s\-\(\)\+]+$', telefono):
        return False, f"Teléfono: {ERROR_FORMATO_INVALIDO} (solo números, espacios, guiones y paréntesis)"
    
    return True, ""


def validar_email(email):
    """
    Valida un email (opcional)
    
    Args:
        email (str): Email a validar
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Si está vacío, es válido (campo opcional)
    if not email or email.strip() == "":
        return True, ""
    
    # Validar longitud
    es_valido, mensaje = validar_longitud(email, LONGITUD_MAXIMA_EMAIL, "Email")
    if not es_valido:
        return es_valido, mensaje
    
    # Validar formato de email
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron_email, email):
        return False, f"Email: {ERROR_FORMATO_INVALIDO}"
    
    return True, ""


def validar_direccion(direccion):
    """
    Valida una dirección (opcional)
    
    Args:
        direccion (str): Dirección a validar
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Si está vacío, es válido (campo opcional)
    if not direccion or direccion.strip() == "":
        return True, ""
    
    # Validar longitud
    es_valido, mensaje = validar_longitud(direccion, LONGITUD_MAXIMA_DIRECCION, "Dirección")
    if not es_valido:
        return es_valido, mensaje
    
    return True, ""


def validar_contrasena(contrasena, es_temporal=False):
    """
    Valida una contraseña
    
    Args:
        contrasena (str): Contraseña a validar
        es_temporal (bool): Si es contraseña temporal (6-10 caracteres, solo alfanuméricos)
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Validar que no esté vacía
    es_valido, mensaje = validar_requerido(contrasena, "Contraseña")
    if not es_valido:
        return es_valido, mensaje
    
    # Si es temporal: 6-10 caracteres, solo alfanuméricos
    if es_temporal:
        if len(contrasena) < 6:
            return False, "Contraseña temporal: Debe tener al menos 6 caracteres"
        if len(contrasena) > 10:
            return False, "Contraseña temporal: No puede tener más de 10 caracteres"
        if not contrasena.isalnum():
            return False, "Contraseña temporal: Solo puede contener letras y números (sin espacios ni símbolos)"
    else:
        # Contraseña personal: mínimo 6 caracteres (sin restricción de máximo)
        if len(contrasena) < LONGITUD_MINIMA_CONTRASENA:
            return False, f"Contraseña: Debe tener al menos {LONGITUD_MINIMA_CONTRASENA} caracteres"
    
    return True, ""


def validar_numero_positivo(valor, nombre_campo="Valor"):
    """
    Valida que un valor sea un número positivo
    
    Args:
        valor: Valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        numero = float(valor)
        if numero < 0:
            return False, f"{nombre_campo}: Debe ser un número positivo"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{nombre_campo}: {ERROR_FORMATO_INVALIDO} (debe ser un número)"


def validar_numero_entero_positivo(valor, nombre_campo="Valor"):
    """
    Valida que un valor sea un número entero positivo
    
    Args:
        valor: Valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        numero = int(valor)
        if numero < 0:
            return False, f"{nombre_campo}: Debe ser un número entero positivo"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{nombre_campo}: {ERROR_FORMATO_INVALIDO} (debe ser un número entero)"


def validar_fecha(fecha_str, formato="%Y-%m-%d"):
    """
    Valida que una cadena sea una fecha válida
    
    Args:
        fecha_str (str): Fecha en formato string
        formato (str): Formato esperado de la fecha
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        datetime.strptime(fecha_str, formato)
        return True, ""
    except (ValueError, TypeError):
        return False, f"Fecha: {ERROR_FORMATO_INVALIDO}"


def validar_rango(valor, minimo, maximo, nombre_campo="Valor"):
    """
    Valida que un valor esté dentro de un rango
    
    Args:
        valor: Valor a validar
        minimo: Valor mínimo permitido
        maximo: Valor máximo permitido
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        numero = float(valor)
        if numero < minimo or numero > maximo:
            return False, f"{nombre_campo}: Debe estar entre {minimo} y {maximo}"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{nombre_campo}: {ERROR_FORMATO_INVALIDO}"


def validar_porcentaje(valor, nombre_campo="Porcentaje"):
    """
    Valida que un valor sea un porcentaje válido (0-100)
    
    Args:
        valor: Valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    return validar_rango(valor, 0, 100, nombre_campo)


def validar_identificador(identificador):
    """
    Valida un identificador (IMEI, Serial, etc.) - opcional
    
    Args:
        identificador (str): Identificador a validar
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Si está vacío, es válido (campo opcional)
    if not identificador or identificador.strip() == "":
        return True, ""
    
    # Validar que solo contenga letras, números y guiones
    if not re.match(r'^[a-zA-Z0-9\-]+$', identificador):
        return False, f"Identificador: {ERROR_FORMATO_INVALIDO} (solo letras, números y guiones)"
    
    return True, ""


def validar_seleccion(valor, opciones, nombre_campo="Campo"):
    """
    Valida que un valor esté dentro de las opciones permitidas
    
    Args:
        valor: Valor a validar
        opciones (list): Lista de opciones válidas
        nombre_campo (str): Nombre del campo para el mensaje de error
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if valor not in opciones:
        return False, f"{nombre_campo}: Selección inválida"
    return True, ""


# ============================================================================
# Funciones auxiliares
# ============================================================================

def limpiar_telefono(telefono):
    """
    Limpia un número de teléfono eliminando espacios y caracteres especiales
    
    Args:
        telefono (str): Teléfono a limpiar
        
    Returns:
        str: Teléfono limpio
    """
    return re.sub(r'[^\d\+]', '', telefono)


def formatear_telefono(telefono):
    """
    Formatea un número de teléfono de manera consistente
    
    Args:
        telefono (str): Teléfono a formatear
        
    Returns:
        str: Teléfono formateado
    """
    # Limpiar
    telefono_limpio = limpiar_telefono(telefono)
    
    # Si es argentino (empieza con +54 o tiene 10 dígitos)
    if telefono_limpio.startswith('+54'):
        # +54 9 221 XXX-XXXX
        if len(telefono_limpio) == 13:  # +54 + 9 + 10 dígitos
            return f"+54 9 {telefono_limpio[4:7]} {telefono_limpio[7:10]}-{telefono_limpio[10:]}"
    elif len(telefono_limpio) == 10:
        # 221 XXX-XXXX
        return f"{telefono_limpio[0:3]} {telefono_limpio[3:6]}-{telefono_limpio[6:]}"
    
    # Si no coincide con formato argentino, devolver como está
    return telefono
