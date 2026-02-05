# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - CREACIÓN DE TABLAS
============================================================================
Crea todas las tablas necesarias de la base de datos
============================================================================
"""

from base_datos.conexion import db
from sistema_base.configuracion import config


def crear_tabla_usuarios():
    """Crea la tabla de usuarios"""
    sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin', 'tecnico')),
        activo BOOLEAN NOT NULL DEFAULT 1,
        primer_login BOOLEAN NOT NULL DEFAULT 1,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        foto_perfil BLOB
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla usuarios creada/verificada", "INFO")


def crear_tabla_clientes():
    """Crea la tabla de clientes"""
    sql = """
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono TEXT NOT NULL,
        direccion TEXT,
        email TEXT,
        fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        notas TEXT,
        observaciones TEXT,
        estado_cliente TEXT NOT NULL DEFAULT 'Nuevo' 
            CHECK(estado_cliente IN ('Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable')),
        es_incobrable BOOLEAN NOT NULL DEFAULT 0,
        activo BOOLEAN NOT NULL DEFAULT 1,
        tiene_incobrables BOOLEAN NOT NULL DEFAULT 0,
        total_incobrables REAL NOT NULL DEFAULT 0,
        confiabilidad_pago TEXT NOT NULL DEFAULT 'Bueno' 
            CHECK(confiabilidad_pago IN ('Bueno', 'Regular', 'Malo'))
    )
    """
    db.ejecutar_consulta(sql)
    
    # Agregar columnas si no existen (para bases de datos existentes)
    try:
        db.ejecutar_consulta("ALTER TABLE clientes ADD COLUMN observaciones TEXT")
    except:
        pass
    
    try:
        db.ejecutar_consulta("ALTER TABLE clientes ADD COLUMN es_incobrable BOOLEAN NOT NULL DEFAULT 0")
    except:
        pass
    
    try:
        db.ejecutar_consulta("ALTER TABLE clientes ADD COLUMN apellido TEXT NOT NULL DEFAULT ''")
    except:
        pass
    
    try:
        db.ejecutar_consulta("ALTER TABLE clientes ADD COLUMN estado_cliente TEXT NOT NULL DEFAULT 'Nuevo'")
    except:
        pass
    
    config.guardar_log("Tabla clientes creada/verificada", "INFO")


def crear_tabla_equipos():
    """Crea la tabla de equipos"""
    sql = """
    CREATE TABLE IF NOT EXISTS equipos (
        id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        tipo_dispositivo TEXT NOT NULL,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        identificador TEXT UNIQUE,
        color TEXT,
        estado_fisico TEXT NOT NULL,
        accesorios TEXT,
        falla_declarada TEXT NOT NULL,
        diagnostico_tecnico TEXT,
        fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        estado_actual TEXT NOT NULL DEFAULT 'En revisión',
        fecha_cambio_estado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_ultimo_movimiento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        dias_sin_movimiento INTEGER NOT NULL DEFAULT 0,
        fecha_abandono DATETIME,
        activo BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    )
    """
    db.ejecutar_consulta(sql)
    
    # Agregar columnas si no existen (para bases de datos existentes)
    try:
        db.ejecutar_consulta("ALTER TABLE equipos ADD COLUMN fecha_ultimo_movimiento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
    except:
        pass
    
    try:
        db.ejecutar_consulta("ALTER TABLE equipos ADD COLUMN solucion_aplicada TEXT")
    except:
        pass
    
    try:
        db.ejecutar_consulta("ALTER TABLE equipos ADD COLUMN observaciones_internas TEXT")
    except:
        pass
    
    config.guardar_log("Tabla equipos creada/verificada", "INFO")


def crear_tabla_presupuestos():
    """Crea la tabla de presupuestos"""
    sql = """
    CREATE TABLE IF NOT EXISTS presupuestos (
        id_presupuesto INTEGER PRIMARY KEY AUTOINCREMENT,
        id_equipo INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        descripcion_trabajo TEXT NOT NULL,
        monto_total REAL NOT NULL,
        recargo_transferencia REAL NOT NULL DEFAULT 0,
        monto_sin_recargo REAL NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Pendiente',
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_vencimiento DATETIME NOT NULL,
        fecha_respuesta DATETIME,
        motivo_rechazo TEXT,
        notas TEXT,
        FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla presupuestos creada/verificada", "INFO")


def crear_tabla_ordenes():
    """Crea la tabla de órdenes de trabajo"""
    sql = """
    CREATE TABLE IF NOT EXISTS ordenes_trabajo (
        id_orden INTEGER PRIMARY KEY AUTOINCREMENT,
        id_presupuesto INTEGER NOT NULL,
        id_equipo INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_tecnico INTEGER NOT NULL,
        descripcion_reparacion TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'En diagnóstico',
        fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_finalizacion DATETIME,
        observaciones_tecnicas TEXT,
        cambios_realizados TEXT,
        cobro_diagnostico REAL,
        tiene_reparacion BOOLEAN NOT NULL DEFAULT 1,
        motivo_sin_reparacion TEXT,
        FOREIGN KEY (id_presupuesto) REFERENCES presupuestos(id_presupuesto),
        FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_tecnico) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla ordenes_trabajo creada/verificada", "INFO")


def crear_tabla_repuestos():
    """Crea la tabla de repuestos"""
    sql = """
    CREATE TABLE IF NOT EXISTS repuestos (
        id_repuesto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        tipo_dispositivo TEXT NOT NULL,
        modelos_compatibles TEXT,
        origen TEXT NOT NULL CHECK(origen IN ('Nuevo', 'Recuperado')),
        id_equipo_origen INTEGER,
        cantidad_disponible INTEGER NOT NULL DEFAULT 0,
        estado TEXT NOT NULL DEFAULT 'Funcionando',
        precio_referencia REAL,
        fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        notas TEXT,
        FOREIGN KEY (id_equipo_origen) REFERENCES equipos(id_equipo)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla repuestos creada/verificada", "INFO")


def crear_tabla_repuestos_usados():
    """Crea la tabla de repuestos usados en órdenes"""
    sql = """
    CREATE TABLE IF NOT EXISTS repuestos_usados (
        id_uso INTEGER PRIMARY KEY AUTOINCREMENT,
        id_orden INTEGER NOT NULL,
        id_repuesto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL DEFAULT 1,
        fecha_uso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        id_usuario INTEGER NOT NULL,
        FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
        FOREIGN KEY (id_repuesto) REFERENCES repuestos(id_repuesto),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla repuestos_usados creada/verificada", "INFO")


def crear_tabla_pagos():
    """Crea la tabla de pagos"""
    sql = """
    CREATE TABLE IF NOT EXISTS pagos (
        id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
        id_orden INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        monto REAL NOT NULL,
        metodo_pago TEXT NOT NULL,
        es_anticipo BOOLEAN NOT NULL DEFAULT 0,
        fecha_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        observaciones TEXT,
        id_usuario INTEGER NOT NULL,
        FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla pagos creada/verificada", "INFO")


def crear_tabla_facturacion():
    """Crea la tabla de facturación"""
    sql = """
    CREATE TABLE IF NOT EXISTS facturacion (
        id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
        id_orden INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        monto_total REAL NOT NULL,
        monto_pagado REAL NOT NULL DEFAULT 0,
        monto_adeudado REAL NOT NULL,
        descuento_aplicado REAL DEFAULT 0,
        fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        estado_cobro TEXT NOT NULL DEFAULT 'Pendiente',
        fecha_incobrable DATETIME,
        motivo_incobrable TEXT,
        observaciones_incobrable TEXT,
        marcado_incobrable_por INTEGER,
        notas TEXT,
        FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (marcado_incobrable_por) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla facturacion creada/verificada", "INFO")


def crear_tabla_garantias():
    """Crea la tabla de garantías"""
    sql = """
    CREATE TABLE IF NOT EXISTS garantias (
        id_garantia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_orden INTEGER NOT NULL,
        id_equipo INTEGER NOT NULL,
        descripcion_reparacion TEXT NOT NULL,
        fecha_inicio DATETIME NOT NULL,
        dias_garantia INTEGER NOT NULL DEFAULT 30,
        fecha_vencimiento DATETIME NOT NULL,
        que_cubre TEXT NOT NULL,
        que_no_cubre TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Vigente',
        notas TEXT,
        FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
        FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla garantias creada/verificada", "INFO")


def crear_tabla_remitos():
    """Crea la tabla de remitos"""
    sql = """
    CREATE TABLE IF NOT EXISTS remitos (
        id_remito INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_remito TEXT UNIQUE NOT NULL,
        id_equipo INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        observaciones TEXT,
        firma_cliente BLOB,
        firma_tecnico BLOB,
        impreso BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla remitos creada/verificada", "INFO")


def crear_tabla_comprobantes_entrega():
    """Crea la tabla de comprobantes de entrega"""
    sql = """
    CREATE TABLE IF NOT EXISTS comprobantes_entrega (
        id_comprobante INTEGER PRIMARY KEY AUTOINCREMENT,
        id_orden INTEGER NOT NULL,
        id_equipo INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        fecha_entrega DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        firma_cliente BLOB,
        id_usuario INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
        FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla comprobantes_entrega creada/verificada", "INFO")


def crear_tabla_equipos_abandonados():
    """Crea la tabla de equipos abandonados"""
    sql = """
    CREATE TABLE IF NOT EXISTS equipos_abandonados (
        id_abandonado INTEGER PRIMARY KEY AUTOINCREMENT,
        id_equipo INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_orden INTEGER,
        fecha_abandono DATETIME NOT NULL,
        estado_equipo TEXT NOT NULL,
        falla_original TEXT NOT NULL,
        trabajo_realizado TEXT,
        partes_recuperables TEXT,
        condicion_fisica TEXT NOT NULL,
        fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        registrado_por INTEGER NOT NULL,
        notas TEXT,
        FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
        FOREIGN KEY (registrado_por) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla equipos_abandonados creada/verificada", "INFO")


def crear_tabla_logs_sistema():
    """Crea la tabla de logs del sistema (auditoría)"""
    sql = """
    CREATE TABLE IF NOT EXISTS logs_sistema (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        accion TEXT NOT NULL,
        modulo TEXT NOT NULL,
        id_registro INTEGER,
        campo_modificado TEXT,
        valor_anterior TEXT,
        valor_nuevo TEXT,
        motivo_modificacion TEXT,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        es_accion_critica BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla logs_sistema creada/verificada", "INFO")


def crear_tabla_historial_notas():
    """Crea la tabla de historial de notas"""
    sql = """
    CREATE TABLE IF NOT EXISTS historial_notas (
        id_nota INTEGER PRIMARY KEY AUTOINCREMENT,
        modulo TEXT NOT NULL,
        id_registro INTEGER NOT NULL,
        nota TEXT NOT NULL,
        id_usuario INTEGER NOT NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        editado BOOLEAN NOT NULL DEFAULT 0,
        editado_por INTEGER,
        fecha_edicion DATETIME,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (editado_por) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla historial_notas creada/verificada", "INFO")


def crear_tabla_backups():
    """Crea la tabla de backups"""
    sql = """
    CREATE TABLE IF NOT EXISTS backups (
        id_backup INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_backup DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        tipo TEXT NOT NULL CHECK(tipo IN ('Manual', 'Automático')),
        ubicacion TEXT NOT NULL,
        tamanio_archivo INTEGER NOT NULL,
        exitoso BOOLEAN NOT NULL DEFAULT 1,
        mensaje_error TEXT,
        id_usuario INTEGER,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla backups creada/verificada", "INFO")


def crear_tabla_configuracion():
    """Crea la tabla de configuración del sistema"""
    sql = """
    CREATE TABLE IF NOT EXISTS configuracion_sistema (
        id_config INTEGER PRIMARY KEY CHECK(id_config = 1),
        nombre_negocio TEXT NOT NULL DEFAULT 'TechManager',
        logo_sistema BLOB,
        logo_remito BLOB,
        logo_comprobante BLOB,
        imagen_header BLOB,
        telefono_contacto TEXT NOT NULL,
        direccion TEXT,
        email TEXT,
        color_primario TEXT NOT NULL DEFAULT '#2563eb',
        color_secundario TEXT NOT NULL DEFAULT '#64748b',
        texto_remito_superior TEXT,
        texto_remito_inferior TEXT,
        dias_alerta_equipo INTEGER NOT NULL DEFAULT 2,
        backup_automatico BOOLEAN NOT NULL DEFAULT 0,
        ruta_backup_local TEXT,
        backup_nube_activo BOOLEAN NOT NULL DEFAULT 0,
        tipo_backup_nube TEXT DEFAULT 'Sin backup en nube',
        ultima_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modificado_por INTEGER,
        FOREIGN KEY (modificado_por) REFERENCES usuarios(id_usuario)
    )
    """
    db.ejecutar_consulta(sql)
    config.guardar_log("Tabla configuracion_sistema creada/verificada", "INFO")


def insertar_configuracion_inicial():
    """Inserta la configuración inicial del sistema si no existe"""
    try:
        # Verificar si ya existe configuración
        consulta = "SELECT COUNT(*) as total FROM configuracion_sistema WHERE id_config = 1"
        resultado = db.obtener_uno(consulta)
        
        if resultado and resultado['total'] == 0:
            # Insertar configuración por defecto
            sql = """
            INSERT INTO configuracion_sistema (
                id_config, 
                nombre_negocio, 
                telefono_contacto,
                color_primario,
                color_secundario,
                dias_alerta_equipo
            ) VALUES (1, 'TechManager', 'Sin configurar', '#2563eb', '#64748b', 2)
            """
            db.ejecutar_consulta(sql)
            config.guardar_log("Configuración inicial insertada", "INFO")
    except Exception as e:
        config.guardar_log(f"Error al insertar configuración inicial: {e}", "ERROR")


def inicializar_base_datos():
    """
    Inicializa la base de datos creando todas las tablas necesarias
    """
    try:
        print("    → Creando/verificando tablas...")
        
        # Crear tablas en orden (respetando foreign keys)
        crear_tabla_usuarios()
        crear_tabla_clientes()
        crear_tabla_equipos()
        crear_tabla_presupuestos()
        crear_tabla_ordenes()
        crear_tabla_repuestos()
        crear_tabla_repuestos_usados()
        crear_tabla_pagos()
        crear_tabla_facturacion()
        crear_tabla_garantias()
        crear_tabla_remitos()
        crear_tabla_comprobantes_entrega()
        crear_tabla_equipos_abandonados()
        crear_tabla_logs_sistema()
        crear_tabla_historial_notas()
        crear_tabla_backups()
        crear_tabla_configuracion()
        
        # Insertar datos iniciales
        insertar_configuracion_inicial()
        
        print("    ✓ Base de datos inicializada correctamente")
        config.guardar_log("Base de datos inicializada correctamente", "INFO")
        
    except Exception as e:
        print(f"    ✗ Error al inicializar base de datos: {e}")
        config.guardar_log(f"Error al inicializar base de datos: {e}", "ERROR")
        raise
