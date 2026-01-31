# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - CONSTANTES DEL SISTEMA
============================================================================
Valores constantes usados en todo el sistema
Modificar con cuidado - estos valores afectan el comportamiento del sistema
============================================================================
"""

# ============================================================================
# INFORMACIÓN DEL SISTEMA
# ============================================================================
VERSION = "1.0.0"
NOMBRE_SISTEMA = "TechManager"
NOMBRE_COMPLETO = "TechManager - Sistema de Gestión para Servicio Técnico"
DESARROLLADOR = "TechManager Development Team"
ANIO = "2025"

# ============================================================================
# BASE DE DATOS
# ============================================================================
NOMBRE_BASE_DATOS = "techmanager.db"
VERSION_ESQUEMA_BD = 1

# ============================================================================
# TIPOS DE DISPOSITIVOS
# ============================================================================
TIPOS_DISPOSITIVO = [
    "Celular",
    "Tablet",
    "PC / Notebook",
    "Consola",
    "Otro"
]

# ============================================================================
# ESTADOS DE EQUIPOS
# ============================================================================
ESTADOS_EQUIPO = [
    "En revisión",
    "En reparación",
    "Esperando repuesto",
    "Listo",
    "Entregado",
    "Sin reparación",
    "Abandonado"
]

# ============================================================================
# ESTADOS DE PRESUPUESTOS
# ============================================================================
ESTADOS_PRESUPUESTO = [
    "Pendiente",
    "Aceptado",
    "Rechazado por cliente",
    "Rechazado por vencimiento"
]

# ============================================================================
# MOTIVOS DE RECHAZO DE PRESUPUESTOS
# ============================================================================
MOTIVOS_RECHAZO_PRESUPUESTO = [
    "Cliente rechazó",
    "Vencido por tiempo (7 días sin respuesta)",
    "Precio muy alto",
    "Cliente desistió"
]

# ============================================================================
# ESTADOS DE ÓRDENES DE TRABAJO
# ============================================================================
ESTADOS_ORDEN = [
    "En diagnóstico",
    "En reparación",
    "Esperando repuesto",
    "Finalizado con reparación",
    "Finalizado sin reparación"
]

# ============================================================================
# TIPOS DE REPUESTOS
# ============================================================================
TIPOS_REPUESTO = [
    "Pantalla / Display",
    "Batería",
    "Módulo de carga",
    "Cámara",
    "Placa / Motherboard",
    "Flex",
    "Altavoz",
    "Micrófono",
    "Teclado",
    "Touchpad",
    "Disco duro / SSD",
    "Memoria RAM",
    "Fuente de alimentación",
    "Ventilador / Cooler",
    "Otro"
]

# ============================================================================
# ORIGEN DE REPUESTOS
# ============================================================================
ORIGENES_REPUESTO = [
    "Nuevo",
    "Recuperado"
]

# ============================================================================
# ESTADOS DE REPUESTOS
# ============================================================================
ESTADOS_REPUESTO = [
    "Funcionando",
    "Con detalles",
    "Para revisar"
]

# ============================================================================
# MÉTODOS DE PAGO
# ============================================================================
METODOS_PAGO = [
    "Efectivo",
    "Transferencia",
    "Mercado Pago",
    "Débito",
    "Crédito"
]

# ============================================================================
# ESTADOS DE COBRO
# ============================================================================
ESTADOS_COBRO = [
    "Pendiente",
    "Pagado parcial",
    "Pagado total",
    "Incobrable"
]

# ============================================================================
# MOTIVOS DE DEUDA INCOBRABLE
# ============================================================================
MOTIVOS_INCOBRABLE = [
    "Cliente no responde",
    "Cliente desapareció",
    "Cliente se negó a pagar",
    "Equipo abandonado",
    "Otro"
]

# ============================================================================
# ESTADOS DE GARANTÍA
# ============================================================================
ESTADOS_GARANTIA = [
    "Vigente",
    "Vencida"
]

# ============================================================================
# ROLES DE USUARIO
# ============================================================================
ROLES_USUARIO = [
    "admin",
    "tecnico"
]

# ============================================================================
# MÓDULOS DEL SISTEMA (para auditoría y notas)
# ============================================================================
MODULOS_SISTEMA = [
    "Usuarios",
    "Clientes",
    "Equipos",
    "Remitos",
    "Presupuestos",
    "Órdenes",
    "Repuestos",
    "Pagos",
    "Facturación",
    "Garantías",
    "Configuración",
    "Sistema"
]

# ============================================================================
# ACCIONES DEL SISTEMA (para auditoría)
# ============================================================================
ACCIONES_SISTEMA = [
    "Crear",
    "Modificar",
    "Eliminar",
    "Login",
    "Logout",
    "Consultar",
    "Exportar",
    "Importar",
    "Backup",
    "Restaurar"
]

# ============================================================================
# CONFIGURACIÓN DE ALERTAS
# ============================================================================
DIAS_ALERTA_EQUIPO_ESTANCADO = 2  # 48 horas = 2 días
DIAS_ABANDONO_EQUIPO = 90  # 90 días sin retirar
DIAS_VENCIMIENTO_PRESUPUESTO = 7  # 7 días sin respuesta

# ============================================================================
# CONFIGURACIÓN DE PAGOS
# ============================================================================
PORCENTAJE_ANTICIPO_MINIMO = 50  # 50% mínimo
PORCENTAJE_RECARGO_TRANSFERENCIA = 10  # 10% de recargo

# ============================================================================
# CONFIGURACIÓN DE REPORTES
# ============================================================================
PERIODOS_REPORTE = [
    "Hoy",
    "Últimos 7 días",
    "Últimos 30 días",
    "Últimos 90 días",
    "Rango personalizado",
    "Mes específico",
    "Año completo"
]

TIPOS_REPORTE = [
    "Ingresos",
    "Reparaciones",
    "Repuestos",
    "Clientes",
    "Técnicos",
    "General"
]

FORMATOS_EXPORTACION = [
    "PDF",
    "Excel"
]

# ============================================================================
# CONFIGURACIÓN DE BACKUPS
# ============================================================================
TIPOS_BACKUP = [
    "Manual",
    "Automático"
]

TIPOS_BACKUP_NUBE = [
    "Google Drive",
    "Dropbox",
    "Sin backup en nube"
]

# ============================================================================
# FORMATOS DE IMAGEN SOPORTADOS
# ============================================================================
FORMATOS_IMAGEN = [
    ".png",
    ".jpg",
    ".jpeg"
]

# ============================================================================
# CONFIGURACIÓN DE INTERFAZ
# ============================================================================
# Colores por defecto (pueden ser personalizados)
COLOR_PRIMARIO_DEFAULT = "#2563eb"  # Azul profesional
COLOR_SECUNDARIO_DEFAULT = "#64748b"  # Gris corporativo

# Tamaños de fuente
TAMANO_FUENTE_TITULO = 16
TAMANO_FUENTE_SUBTITULO = 12
TAMANO_FUENTE_NORMAL = 10
TAMANO_FUENTE_PEQUENA = 9

# ============================================================================
# VALORES DE VALIDACIÓN
# ============================================================================
LONGITUD_MINIMA_CONTRASENA = 6
LONGITUD_MAXIMA_NOMBRE = 100
LONGITUD_MAXIMA_DIRECCION = 200
LONGITUD_MAXIMA_EMAIL = 100
LONGITUD_MAXIMA_TELEFONO = 20
LONGITUD_MAXIMA_NOTA = 1000

# ============================================================================
# MENSAJES DE CONFIRMACIÓN
# ============================================================================
MENSAJE_CONFIRMAR_CREAR = "¿Desea crear este registro?"
MENSAJE_CONFIRMAR_MODIFICAR = "¿Desea guardar los cambios?"
MENSAJE_CONFIRMAR_ELIMINAR = "¿Desea ELIMINAR este registro?\n\n⚠️ ESTA ACCIÓN NO SE PUEDE DESHACER"
MENSAJE_CONFIRMAR_IMPRIMIR = "¿Desea imprimir este documento?"
MENSAJE_CONFIRMAR_EXPORTAR = "¿Desea exportar estos datos?"

# ============================================================================
# MENSAJES DE ERROR COMUNES
# ============================================================================
ERROR_CAMPO_OBLIGATORIO = "Este campo es obligatorio"
ERROR_FORMATO_INVALIDO = "El formato ingresado no es válido"
ERROR_VALOR_DUPLICADO = "Este valor ya existe en el sistema"
ERROR_NO_ENCONTRADO = "No se encontró el registro solicitado"
ERROR_PERMISO_DENEGADO = "No tiene permisos para realizar esta acción"
ERROR_BASE_DATOS = "Error al acceder a la base de datos"

# ============================================================================
# MENSAJES DE ÉXITO
# ============================================================================
EXITO_CREAR = "Registro creado exitosamente"
EXITO_MODIFICAR = "Cambios guardados exitosamente"
EXITO_ELIMINAR = "Registro eliminado exitosamente"
EXITO_IMPORTAR = "Datos importados exitosamente"
EXITO_EXPORTAR = "Datos exportados exitosamente"
EXITO_BACKUP = "Backup realizado exitosamente"

# ============================================================================
# FIN DE CONSTANTES
# ============================================================================
