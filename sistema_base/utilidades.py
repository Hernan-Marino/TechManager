# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - UTILIDADES GENERALES
============================================================================
Funciones auxiliares usadas en todo el sistema
============================================================================
"""

from datetime import datetime, timedelta
import os
import shutil


def formatear_fecha(fecha, formato="%d/%m/%Y"):
    """
    Formatea una fecha a string
    
    Args:
        fecha (datetime): Fecha a formatear
        formato (str): Formato deseado
        
    Returns:
        str: Fecha formateada
    """
    if fecha is None:
        return ""
    
    if isinstance(fecha, str):
        try:
            fecha = datetime.fromisoformat(fecha)
        except:
            return fecha
    
    return fecha.strftime(formato)


def formatear_fecha_hora(fecha_hora, formato="%d/%m/%Y %H:%M"):
    """
    Formatea una fecha y hora a string
    
    Args:
        fecha_hora (datetime): Fecha y hora a formatear
        formato (str): Formato deseado
        
    Returns:
        str: Fecha y hora formateada
    """
    return formatear_fecha(fecha_hora, formato)


def calcular_dias_transcurridos(fecha_inicial, fecha_final=None):
    """
    Calcula los días transcurridos entre dos fechas
    
    Args:
        fecha_inicial (datetime): Fecha inicial
        fecha_final (datetime): Fecha final (por defecto: hoy)
        
    Returns:
        int: Días transcurridos
    """
    if fecha_final is None:
        fecha_final = datetime.now()
    
    if isinstance(fecha_inicial, str):
        fecha_inicial = datetime.fromisoformat(fecha_inicial)
    
    if isinstance(fecha_final, str):
        fecha_final = datetime.fromisoformat(fecha_final)
    
    diferencia = fecha_final - fecha_inicial
    return diferencia.days


def agregar_dias(fecha, dias):
    """
    Agrega días a una fecha
    
    Args:
        fecha (datetime): Fecha base
        dias (int): Días a agregar
        
    Returns:
        datetime: Nueva fecha
    """
    if isinstance(fecha, str):
        fecha = datetime.fromisoformat(fecha)
    
    return fecha + timedelta(days=dias)


def formatear_dinero(monto):
    """
    Formatea un monto de dinero
    
    Args:
        monto (float): Monto a formatear
        
    Returns:
        str: Monto formateado (ej: "$1.234,56")
    """
    if monto is None:
        return "$0,00"
    
    # Formatear con separador de miles y 2 decimales
    return f"${monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_porcentaje(valor, total):
    """
    Calcula el porcentaje que representa un valor del total
    
    Args:
        valor (float): Valor
        total (float): Total
        
    Returns:
        float: Porcentaje
    """
    if total == 0:
        return 0
    
    return (valor / total) * 100


def aplicar_porcentaje(monto, porcentaje):
    """
    Aplica un porcentaje a un monto
    
    Args:
        monto (float): Monto base
        porcentaje (float): Porcentaje a aplicar
        
    Returns:
        float: Monto con porcentaje aplicado
    """
    return monto * (porcentaje / 100)


def generar_numero_remito():
    """
    Genera un número de remito único
    
    Returns:
        str: Número de remito (ej: "R-20250113-0001")
    """
    from base_datos.conexion import db
    
    # Formato: R-YYYYMMDD-NNNN
    fecha_hoy = datetime.now().strftime("%Y%m%d")
    
    # Buscar último remito del día
    consulta = """
    SELECT numero_remito FROM remitos 
    WHERE numero_remito LIKE ?
    ORDER BY numero_remito DESC
    LIMIT 1
    """
    
    patron = f"R-{fecha_hoy}-%"
    ultimo = db.obtener_uno(consulta, (patron,))
    
    if ultimo:
        # Extraer número secuencial
        numero_str = ultimo['numero_remito'].split('-')[-1]
        numero = int(numero_str) + 1
    else:
        numero = 1
    
    return f"R-{fecha_hoy}-{numero:04d}"


def limpiar_texto(texto):
    """
    Limpia un texto eliminando espacios extras y caracteres especiales
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    if texto is None:
        return ""
    
    # Eliminar espacios extras
    texto = " ".join(texto.split())
    
    return texto.strip()


def truncar_texto(texto, longitud=50):
    """
    Trunca un texto a una longitud específica
    
    Args:
        texto (str): Texto a truncar
        longitud (int): Longitud máxima
        
    Returns:
        str: Texto truncado
    """
    if texto is None:
        return ""
    
    if len(texto) <= longitud:
        return texto
    
    return texto[:longitud-3] + "..."


def obtener_tamano_archivo(ruta):
    """
    Obtiene el tamaño de un archivo en bytes
    
    Args:
        ruta (str): Ruta del archivo
        
    Returns:
        int: Tamaño en bytes
    """
    try:
        return os.path.getsize(ruta)
    except:
        return 0


def formatear_tamano_archivo(bytes):
    """
    Formatea el tamaño de un archivo en formato legible
    
    Args:
        bytes (int): Tamaño en bytes
        
    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes/1024:.1f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes/(1024*1024):.1f} MB"
    else:
        return f"{bytes/(1024*1024*1024):.1f} GB"


def copiar_archivo(origen, destino):
    """
    Copia un archivo de un lugar a otro
    
    Args:
        origen (str): Ruta origen
        destino (str): Ruta destino
        
    Returns:
        bool: True si fue exitoso, False si no
    """
    try:
        shutil.copy2(origen, destino)
        return True
    except Exception as e:
        from sistema_base.configuracion import config
        config.guardar_log(f"Error al copiar archivo: {e}", "ERROR")
        return False


def crear_backup_archivo(ruta):
    """
    Crea una copia de backup de un archivo
    
    Args:
        ruta (str): Ruta del archivo
        
    Returns:
        str: Ruta del backup creado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base, extension = os.path.splitext(ruta)
    ruta_backup = f"{nombre_base}_backup_{timestamp}{extension}"
    
    if copiar_archivo(ruta, ruta_backup):
        return ruta_backup
    return None


def validar_rango_fechas(fecha_inicio, fecha_fin):
    """
    Valida que un rango de fechas sea correcto
    
    Args:
        fecha_inicio (datetime): Fecha de inicio
        fecha_fin (datetime): Fecha de fin
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if fecha_inicio is None or fecha_fin is None:
        return False, "Ambas fechas son obligatorias"
    
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.fromisoformat(fecha_inicio)
    
    if isinstance(fecha_fin, str):
        fecha_fin = datetime.fromisoformat(fecha_fin)
    
    if fecha_inicio > fecha_fin:
        return False, "La fecha de inicio no puede ser mayor a la fecha de fin"
    
    return True, ""


def es_fecha_futura(fecha):
    """
    Verifica si una fecha está en el futuro
    
    Args:
        fecha (datetime): Fecha a verificar
        
    Returns:
        bool: True si es futura, False si no
    """
    if isinstance(fecha, str):
        fecha = datetime.fromisoformat(fecha)
    
    return fecha > datetime.now()


def es_fecha_pasada(fecha):
    """
    Verifica si una fecha está en el pasado
    
    Args:
        fecha (datetime): Fecha a verificar
        
    Returns:
        bool: True si es pasada, False si no
    """
    if isinstance(fecha, str):
        fecha = datetime.fromisoformat(fecha)
    
    return fecha < datetime.now()


def normalizar_texto_busqueda(texto):
    """
    Normaliza un texto para búsquedas (minúsculas, sin acentos)
    
    Args:
        texto (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    if texto is None:
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Eliminar acentos
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n'
    }
    
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    
    return texto
