# BASE DE DATOS COMPLETA - TECHMANAGER

## TABLA DE CONTENIDOS
1. [Diagrama ER Completo](#diagrama-er-completo)
2. [Tabla 1: CLIENTES](#tabla-1-clientes)
3. [Tabla 2: EQUIPOS](#tabla-2-equipos)
4. [Tabla 3: ORDENES_TRABAJO](#tabla-3-ordenes_trabajo)
5. [Tabla 4: PRESUPUESTOS](#tabla-4-presupuestos)
6. [Tabla 5: REPUESTOS](#tabla-5-repuestos)
7. [Tabla 6: REPUESTOS_ORDEN](#tabla-6-repuestos_orden)
8. [Tabla 7: FACTURAS](#tabla-7-facturas)
9. [Tabla 8: PAGOS](#tabla-8-pagos)
10. [Tabla 9: REMITOS](#tabla-9-remitos)
11. [Tabla 10: GARANTIAS](#tabla-10-garantias)
12. [Tabla 11: USUARIOS](#tabla-11-usuarios)
13. [Tabla 12: AUDITORIA](#tabla-12-auditoria)
14. [Tabla 13: CONFIGURACION](#tabla-13-configuracion)
15. [Índices y Optimizaciones](#índices-y-optimizaciones)
16. [Triggers y Constraints](#triggers-y-constraints)

---

## DIAGRAMA ER COMPLETO

```
                                    ┌─────────────┐
                                    │  USUARIOS   │
                                    │ (id_usuario)│
                                    └──────┬──────┘
                                           │
                                           │ crea/modifica
                                           │
        ┌──────────────────────────────────┼────────────────────────────┐
        │                                  │                            │
        ▼                                  ▼                            ▼
┌──────────────┐                  ┌──────────────┐            ┌──────────────┐
│   CLIENTES   │                  │  AUDITORIA   │            │CONFIGURACION │
│ (id_cliente) │                  │(id_auditoria)│            │ (id_config)  │
└──────┬───────┘                  └──────────────┘            └──────────────┘
       │
       │ tiene
       │
       ▼
┌──────────────┐
│   EQUIPOS    │
│ (id_equipo)  │
└──────┬───────┘
       │
       ├──────────┐
       │          │
       │          │ tiene
       │          ▼
       │   ┌──────────────┐
       │   │  GARANTIAS   │
       │   │ (id_garantia)│
       │   └──────────────┘
       │
       │ genera
       │
       ├──────────┐
       │          │
       │          ▼
       │   ┌──────────────────┐
       │   │  PRESUPUESTOS    │
       │   │(id_presupuesto)  │
       │   └──────────────────┘
       │
       │ tiene
       │
       ▼
┌──────────────────┐
│ ORDENES_TRABAJO  │
│   (id_orden)     │
└────────┬─────────┘
         │
         │ usa
         │
         ▼
┌──────────────────┐         ┌──────────────┐
│ REPUESTOS_ORDEN  │◄────────│  REPUESTOS   │
│(id_repuesto_ord) │ referencia│(id_repuesto) │
└──────────────────┘         └──────────────┘


┌──────────────┐         ┌──────────────┐
│   FACTURAS   │◄────┐   │    PAGOS     │
│ (id_factura) │     └───│  (id_pago)   │
└──────┬───────┘         └──────────────┘
       │
       │ relacionada con
       │
       ▼
┌──────────────┐
│   REMITOS    │
│ (id_remito)  │
└──────────────┘
```

---

## TABLA 1: CLIENTES

### Descripción
Almacena la información completa de todos los clientes del taller.

### Schema SQL

```sql
CREATE TABLE clientes (
    -- Identificación
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Datos personales
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    
    -- Contacto
    telefono TEXT NOT NULL UNIQUE,
    direccion TEXT,
    email TEXT,
    
    -- Información adicional
    observaciones TEXT,
    
    -- Estado del cliente
    estado_cliente TEXT NOT NULL DEFAULT 'Nuevo' 
        CHECK(estado_cliente IN ('Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable')),
    
    -- Marcadores
    es_incobrable BOOLEAN NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT 1,
    tiene_incobrables BOOLEAN NOT NULL DEFAULT 0,
    
    -- Información financiera
    total_incobrables REAL NOT NULL DEFAULT 0,
    confiabilidad_pago TEXT NOT NULL DEFAULT 'Bueno' 
        CHECK(confiabilidad_pago IN ('Bueno', 'Regular', 'Malo')),
    
    -- Metadata
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_clientes_telefono ON clientes(telefono);
CREATE INDEX idx_clientes_activo ON clientes(activo);
CREATE INDEX idx_clientes_estado ON clientes(estado_cliente);
CREATE INDEX idx_clientes_apellido ON clientes(apellido);
```

### Campos Detallados

| Campo | Tipo | Obligatorio | Descripción | Valores Posibles |
|-------|------|-------------|-------------|------------------|
| id_cliente | INTEGER | Sí (PK) | Identificador único autoincremental | 1, 2, 3... |
| nombre | TEXT | Sí | Nombre del cliente | "Juan", "María" |
| apellido | TEXT | Sí | Apellido del cliente | "Pérez", "García" |
| telefono | TEXT | Sí (UNIQUE) | Teléfono principal | "1123456789" |
| direccion | TEXT | No | Dirección completa | "Av. Corrientes 1234" |
| email | TEXT | No | Email de contacto | "juan@email.com" |
| observaciones | TEXT | No | Notas adicionales | Texto libre |
| estado_cliente | TEXT | Sí | Estado actual del cliente | Nuevo, Buen Pagador, Deudor, Moroso, Incobrable |
| es_incobrable | BOOLEAN | Sí | Marcado como incobrable | 0 o 1 |
| activo | BOOLEAN | Sí | Cliente activo (soft delete) | 0 o 1 |
| tiene_incobrables | BOOLEAN | Sí | Tiene deudas incobrables | 0 o 1 |
| total_incobrables | REAL | Sí | Monto total de incobrables | 0.00, 1500.50 |
| confiabilidad_pago | TEXT | Sí | Historial de pagos | Bueno, Regular, Malo |
| fecha_registro | DATETIME | Sí | Fecha de creación del registro | 2026-01-29 10:30:00 |

### Estados del Cliente

```
NUEVO
  │
  ├──> (Paga bien) ──> BUEN PAGADOR
  │
  ├──> (30+ días atraso) ──> DEUDOR
  │
  ├──> (60+ días atraso) ──> MOROSO
  │
  └──> (Manual admin) ──> INCOBRABLE

NOTA: Una vez Deudor/Moroso, solo Admin puede volver a Buen Pagador
```

### Reglas de Negocio

1. **Teléfono único**: No pueden existir dos clientes con el mismo teléfono
2. **Soft delete**: Al eliminar, se marca `activo = 0` en vez de DELETE
3. **No eliminar con equipos activos**: Verificar que no tenga equipos con `activo = 1`
4. **Estado automático**: Se actualiza según días de atraso en pagos
5. **Cambio de estado manual**: Solo administradores pueden cambiar estados manualmente

### Ejemplos de Datos

```sql
-- Cliente nuevo
INSERT INTO clientes (nombre, apellido, telefono, direccion, email)
VALUES ('Juan', 'Pérez', '1123456789', 'Av. Corrientes 1234', 'juan@email.com');

-- Cliente con deuda
INSERT INTO clientes (nombre, apellido, telefono, estado_cliente, tiene_incobrables, total_incobrables)
VALUES ('María', 'García', '1198765432', 'Deudor', 1, 5000.00);

-- Actualizar estado
UPDATE clientes 
SET estado_cliente = 'Buen Pagador' 
WHERE id_cliente = 1;

-- Soft delete
UPDATE clientes 
SET activo = 0 
WHERE id_cliente = 2;

-- Listar solo activos
SELECT * FROM clientes WHERE activo = 1;
```

---

## TABLA 2: EQUIPOS

### Descripción
Registra todos los equipos que ingresan al taller para reparación.

### Schema SQL

```sql
CREATE TABLE equipos (
    -- Identificación
    id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    
    -- Información del equipo
    tipo_equipo TEXT NOT NULL,  -- Computadora, Celular, Tablet, etc.
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    numero_serie TEXT,
    color TEXT,
    
    -- Problema y accesorios
    descripcion_problema TEXT NOT NULL,
    accesorios TEXT,  -- Cargador, funda, etc.
    
    -- Estado
    estado_equipo TEXT NOT NULL DEFAULT 'Ingresado'
        CHECK(estado_equipo IN ('Ingresado', 'En Diagnóstico', 'Esperando Repuestos', 
                                'En Reparación', 'Reparado', 'No Tiene Solución', 
                                'Entregado', 'Abandonado')),
    
    -- Fechas
    fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada_entrega DATETIME,
    fecha_real_entrega DATETIME,
    
    -- Metadata
    activo BOOLEAN NOT NULL DEFAULT 1,
    
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- Índices
CREATE INDEX idx_equipos_cliente ON equipos(id_cliente);
CREATE INDEX idx_equipos_estado ON equipos(estado_equipo);
CREATE INDEX idx_equipos_activo ON equipos(activo);
CREATE INDEX idx_equipos_fecha_ingreso ON equipos(fecha_ingreso);
```

### Campos Detallados

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| id_equipo | INTEGER | Sí (PK) | Identificador único |
| id_cliente | INTEGER | Sí (FK) | Cliente propietario |
| tipo_equipo | TEXT | Sí | Tipo de dispositivo |
| marca | TEXT | Sí | Marca del equipo |
| modelo | TEXT | Sí | Modelo específico |
| numero_serie | TEXT | No | Número de serie |
| color | TEXT | No | Color del equipo |
| descripcion_problema | TEXT | Sí | Problema reportado |
| accesorios | TEXT | No | Accesorios entregados |
| estado_equipo | TEXT | Sí | Estado actual |
| fecha_ingreso | DATETIME | Sí | Fecha de ingreso |
| fecha_estimada_entrega | DATETIME | No | Fecha estimada |
| fecha_real_entrega | DATETIME | No | Fecha real de entrega |
| activo | BOOLEAN | Sí | Equipo activo |

### Estados del Equipo

```
INGRESADO
  │
  ▼
EN DIAGNÓSTICO
  │
  ├──> ESPERANDO REPUESTOS
  │      │
  │      ▼
  └──> EN REPARACIÓN
         │
         ├──> REPARADO ──> ENTREGADO
         │
         └──> NO TIENE SOLUCIÓN ──> ENTREGADO
         
ABANDONADO (si pasan 90+ días sin retirar)
```

### Tipos de Equipo Comunes

- Computadora de Escritorio
- Notebook/Laptop
- Celular/Smartphone
- Tablet
- Consola de Videojuegos
- All-in-One
- Monitor
- Impresora
- Router/Modem
- Disco Duro Externo
- Otro

### Ejemplos de Datos

```sql
-- Equipo nuevo
INSERT INTO equipos (
    id_cliente, tipo_equipo, marca, modelo, numero_serie, 
    descripcion_problema, accesorios
)
VALUES (
    1, 'Notebook', 'HP', 'Pavilion 15', 'SN123456789',
    'No enciende, se escucha el ventilador pero pantalla negra',
    'Cargador original, bolso de transporte'
);

-- Actualizar estado
UPDATE equipos 
SET estado_equipo = 'En Reparación',
    fecha_estimada_entrega = '2026-02-05'
WHERE id_equipo = 1;

-- Marcar como entregado
UPDATE equipos
SET estado_equipo = 'Entregado',
    fecha_real_entrega = CURRENT_TIMESTAMP
WHERE id_equipo = 1;

-- Buscar equipos pendientes de un cliente
SELECT * FROM equipos
WHERE id_cliente = 1
  AND estado_equipo NOT IN ('Entregado', 'Abandonado')
  AND activo = 1;
```

---

## TABLA 3: ORDENES_TRABAJO

### Descripción
Registra las órdenes de trabajo asociadas a cada equipo, con el diagnóstico, trabajo realizado y costos.

### Schema SQL

```sql
CREATE TABLE ordenes_trabajo (
    -- Identificación
    id_orden INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipo INTEGER NOT NULL,
    numero_orden TEXT NOT NULL UNIQUE,
    
    -- Descripción del trabajo
    descripcion_trabajo TEXT NOT NULL,
    diagnostico TEXT,
    trabajo_realizado TEXT,
    
    -- Estado
    estado_orden TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK(estado_orden IN ('Pendiente', 'En Proceso', 'Pausada', 'Completada', 'Cancelada')),
    
    -- Costos
    costo_mano_obra REAL DEFAULT 0,
    costo_repuestos REAL DEFAULT 0,
    costo_total REAL DEFAULT 0,
    
    -- Asignación
    id_usuario_asignado INTEGER,
    
    -- Fechas
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_finalizacion DATETIME,
    
    -- Prioridad
    prioridad TEXT NOT NULL DEFAULT 'Normal'
        CHECK(prioridad IN ('Baja', 'Normal', 'Alta', 'Urgente')),
    
    -- Notas
    observaciones TEXT,
    
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (id_usuario_asignado) REFERENCES usuarios(id_usuario)
);

-- Índices
CREATE INDEX idx_ordenes_equipo ON ordenes_trabajo(id_equipo);
CREATE INDEX idx_ordenes_numero ON ordenes_trabajo(numero_orden);
CREATE INDEX idx_ordenes_estado ON ordenes_trabajo(estado_orden);
CREATE INDEX idx_ordenes_usuario ON ordenes_trabajo(id_usuario_asignado);
CREATE INDEX idx_ordenes_fecha ON ordenes_trabajo(fecha_inicio);
```

### Campos Detallados

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| id_orden | INTEGER | Sí (PK) | Identificador único |
| id_equipo | INTEGER | Sí (FK) | Equipo asociado |
| numero_orden | TEXT | Sí (UNIQUE) | Número de orden (OT-2026-0001) |
| descripcion_trabajo | TEXT | Sí | Descripción del trabajo a realizar |
| diagnostico | TEXT | No | Diagnóstico técnico |
| trabajo_realizado | TEXT | No | Detalle del trabajo realizado |
| estado_orden | TEXT | Sí | Estado actual |
| costo_mano_obra | REAL | Sí | Costo de mano de obra |
| costo_repuestos | REAL | Sí | Costo total de repuestos |
| costo_total | REAL | Sí | Costo total (mano obra + repuestos) |
| id_usuario_asignado | INTEGER | No (FK) | Técnico asignado |
| fecha_inicio | DATETIME | Sí | Fecha de inicio |
| fecha_finalizacion | DATETIME | No | Fecha de finalización |
| prioridad | TEXT | Sí | Nivel de prioridad |
| observaciones | TEXT | No | Notas adicionales |

### Formato de Número de Orden

```
OT-AAAA-NNNN

OT: Prefijo fijo (Orden de Trabajo)
AAAA: Año (2026)
NNNN: Número secuencial con 4 dígitos (0001, 0002, etc.)

Ejemplos:
- OT-2026-0001
- OT-2026-0152
- OT-2026-1523
```

### Estados de Orden

```
PENDIENTE
  │
  ▼
EN PROCESO
  │
  ├──> PAUSADA ──> EN PROCESO
  │
  ├──> COMPLETADA
  │
  └──> CANCELADA
```

### Ejemplos de Datos

```sql
-- Crear orden de trabajo
INSERT INTO ordenes_trabajo (
    id_equipo, numero_orden, descripcion_trabajo, 
    diagnostico, id_usuario_asignado, prioridad
)
VALUES (
    1, 'OT-2026-0001', 
    'Revisión general y reparación de pantalla',
    'Pantalla rota, bisagra floja',
    2, 'Alta'
);

-- Actualizar con trabajo realizado
UPDATE ordenes_trabajo
SET trabajo_realizado = 'Reemplazo de pantalla LCD, ajuste de bisagras, limpieza interna',
    costo_mano_obra = 5000.00,
    costo_repuestos = 15000.00,
    costo_total = 20000.00,
    estado_orden = 'Completada',
    fecha_finalizacion = CURRENT_TIMESTAMP
WHERE id_orden = 1;

-- Consultar órdenes pendientes por técnico
SELECT o.*, e.marca, e.modelo, c.nombre, c.apellido
FROM ordenes_trabajo o
JOIN equipos e ON o.id_equipo = e.id_equipo
JOIN clientes c ON e.id_cliente = c.id_cliente
WHERE o.id_usuario_asignado = 2
  AND o.estado_orden IN ('Pendiente', 'En Proceso')
ORDER BY o.prioridad DESC, o.fecha_inicio ASC;
```

---

Continúo con las demás tablas...

## TABLA 4: PRESUPUESTOS

### Schema SQL

```sql
CREATE TABLE presupuestos (
    id_presupuesto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipo INTEGER NOT NULL,
    numero_presupuesto TEXT NOT NULL UNIQUE,
    
    -- Detalles
    descripcion TEXT NOT NULL,
    mano_obra REAL NOT NULL DEFAULT 0,
    costo_repuestos REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL,
    
    -- Estado
    estado_presupuesto TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK(estado_presupuesto IN ('Pendiente', 'Aprobado', 'Rechazado', 'Vencido')),
    
    -- Fechas
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATETIME,
    fecha_aprobacion DATETIME,
    
    -- Notas
    observaciones TEXT,
    
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);

CREATE INDEX idx_presupuestos_equipo ON presupuestos(id_equipo);
CREATE INDEX idx_presupuestos_numero ON presupuestos(numero_presupuesto);
CREATE INDEX idx_presupuestos_estado ON presupuestos(estado_presupuesto);
```

## TABLA 5: REPUESTOS

### Schema SQL

```sql
CREATE TABLE repuestos (
    id_repuesto INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria TEXT,
    marca TEXT,
    modelo_compatible TEXT,
    
    -- Stock
    stock_actual INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 5,
    
    -- Precios
    costo_unitario REAL NOT NULL DEFAULT 0,
    precio_venta REAL NOT NULL DEFAULT 0,
    
    -- Ubicación
    ubicacion TEXT,
    proveedor TEXT,
    
    -- Metadata
    activo BOOLEAN NOT NULL DEFAULT 1
);

CREATE INDEX idx_repuestos_codigo ON repuestos(codigo);
CREATE INDEX idx_repuestos_nombre ON repuestos(nombre);
CREATE INDEX idx_repuestos_stock ON repuestos(stock_actual);
```

## TABLA 6: REPUESTOS_ORDEN

### Schema SQL

```sql
CREATE TABLE repuestos_orden (
    id_repuesto_orden INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL,
    id_repuesto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
    FOREIGN KEY (id_repuesto) REFERENCES repuestos(id_repuesto)
);

CREATE INDEX idx_repuestos_orden_orden ON repuestos_orden(id_orden);
CREATE INDEX idx_repuestos_orden_repuesto ON repuestos_orden(id_repuesto);
```

## TABLA 7: FACTURAS

### Schema SQL

```sql
CREATE TABLE facturas (
    id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT NOT NULL UNIQUE,
    id_cliente INTEGER NOT NULL,
    id_equipo INTEGER,
    
    -- Fechas
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATETIME,
    
    -- Montos
    subtotal REAL NOT NULL DEFAULT 0,
    impuestos REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL,
    
    -- Tipo y estado
    tipo_factura TEXT NOT NULL,  -- A, B, C, etc.
    estado_factura TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK(estado_factura IN ('Pendiente', 'Pagada', 'Parcial', 'Vencida', 'Anulada')),
    
    -- Notas
    observaciones TEXT,
    
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);

CREATE INDEX idx_facturas_numero ON facturas(numero_factura);
CREATE INDEX idx_facturas_cliente ON facturas(id_cliente);
CREATE INDEX idx_facturas_estado ON facturas(estado_factura);
```

## TABLA 8: PAGOS

### Schema SQL

```sql
CREATE TABLE pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_factura INTEGER NOT NULL,
    monto REAL NOT NULL,
    metodo_pago TEXT NOT NULL
        CHECK(metodo_pago IN ('Efectivo', 'Transferencia', 'Débito', 'Crédito', 'Cheque', 'Otro')),
    
    fecha_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    numero_referencia TEXT,
    observaciones TEXT,
    
    FOREIGN KEY (id_factura) REFERENCES facturas(id_factura)
);

CREATE INDEX idx_pagos_factura ON pagos(id_factura);
CREATE INDEX idx_pagos_fecha ON pagos(fecha_pago);
```

## TABLA 9: REMITOS

### Schema SQL

```sql
CREATE TABLE remitos (
    id_remito INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_remito TEXT NOT NULL UNIQUE,
    id_cliente INTEGER NOT NULL,
    id_equipo INTEGER,
    
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_remito TEXT NOT NULL
        CHECK(tipo_remito IN ('Entrada', 'Salida')),
    
    observaciones TEXT,
    
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);

CREATE INDEX idx_remitos_numero ON remitos(numero_remito);
CREATE INDEX idx_remitos_cliente ON remitos(id_cliente);
```

## TABLA 10: GARANTIAS

### Schema SQL

```sql
CREATE TABLE garantias (
    id_garantia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipo INTEGER NOT NULL,
    
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NOT NULL,
    descripcion_garantia TEXT NOT NULL,
    
    estado_garantia TEXT NOT NULL DEFAULT 'Vigente'
        CHECK(estado_garantia IN ('Vigente', 'Vencida', 'Utilizada', 'Cancelada')),
    
    observaciones TEXT,
    
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);

CREATE INDEX idx_garantias_equipo ON garantias(id_equipo);
CREATE INDEX idx_garantias_estado ON garantias(estado_garantia);
```

## TABLA 11: USUARIOS

### Schema SQL

```sql
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    
    rol TEXT NOT NULL DEFAULT 'tecnico'
        CHECK(rol IN ('admin', 'tecnico', 'recepcionista')),
    
    email TEXT,
    activo BOOLEAN NOT NULL DEFAULT 1,
    
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME
);

CREATE INDEX idx_usuarios_nombre_usuario ON usuarios(nombre_usuario);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
```

## TABLA 12: AUDITORIA

### Schema SQL

```sql
CREATE TABLE auditoria (
    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    
    accion TEXT NOT NULL,  -- Crear, Modificar, Eliminar, Login, Logout
    modulo TEXT NOT NULL,  -- Clientes, Equipos, Órdenes, etc.
    id_registro INTEGER,
    
    campo_modificado TEXT,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    
    fecha_accion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    es_critica BOOLEAN NOT NULL DEFAULT 0,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE INDEX idx_auditoria_usuario ON auditoria(id_usuario);
CREATE INDEX idx_auditoria_fecha ON auditoria(fecha_accion);
CREATE INDEX idx_auditoria_modulo ON auditoria(modulo);
CREATE INDEX idx_auditoria_critica ON auditoria(es_critica);
```

## TABLA 13: CONFIGURACION

### Schema SQL

```sql
CREATE TABLE configuracion (
    id_config INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_configuracion_clave ON configuracion(clave);
```

---

## ÍNDICES Y OPTIMIZACIONES

### Índices Recomendados

Todos los índices ya están definidos en cada tabla, pero aquí un resumen de los más importantes:

```sql
-- Búsquedas frecuentes
CREATE INDEX idx_clientes_telefono ON clientes(telefono);
CREATE INDEX idx_clientes_apellido ON clientes(apellido);
CREATE INDEX idx_equipos_cliente ON equipos(id_cliente);
CREATE INDEX idx_ordenes_equipo ON ordenes_trabajo(id_equipo);

-- Filtros por estado
CREATE INDEX idx_clientes_activo ON clientes(activo);
CREATE INDEX idx_equipos_estado ON equipos(estado_equipo);
CREATE INDEX idx_ordenes_estado ON ordenes_trabajo(estado_orden);

-- Búsquedas por fecha
CREATE INDEX idx_equipos_fecha_ingreso ON equipos(fecha_ingreso);
CREATE INDEX idx_pagos_fecha ON pagos(fecha_pago);
CREATE INDEX idx_auditoria_fecha ON auditoria(fecha_accion);
```

### Queries Optimizadas

```sql
-- Buscar cliente por teléfono (usa índice)
SELECT * FROM clientes 
WHERE telefono = '1123456789' 
  AND activo = 1;

-- Equipos pendientes (usa índices)
SELECT * FROM equipos 
WHERE estado_equipo NOT IN ('Entregado', 'Abandonado')
  AND activo = 1
ORDER BY fecha_ingreso DESC;

-- Órdenes por técnico (usa JOIN optimizado)
SELECT o.*, e.marca, e.modelo
FROM ordenes_trabajo o
INNER JOIN equipos e ON o.id_equipo = e.id_equipo
WHERE o.id_usuario_asignado = ?
  AND o.estado_orden = 'En Proceso';
```

---

## TRIGGERS Y CONSTRAINTS

### Triggers Útiles

```sql
-- Actualizar costo_total en ordenes_trabajo
CREATE TRIGGER actualizar_costo_total_orden
AFTER UPDATE OF costo_mano_obra, costo_repuestos ON ordenes_trabajo
BEGIN
    UPDATE ordenes_trabajo
    SET costo_total = NEW.costo_mano_obra + NEW.costo_repuestos
    WHERE id_orden = NEW.id_orden;
END;

-- Validar stock antes de usar repuesto
CREATE TRIGGER validar_stock_repuesto
BEFORE INSERT ON repuestos_orden
BEGIN
    SELECT CASE
        WHEN (SELECT stock_actual FROM repuestos WHERE id_repuesto = NEW.id_repuesto) < NEW.cantidad
        THEN RAISE(ABORT, 'Stock insuficiente')
    END;
END;

-- Actualizar stock al usar repuesto
CREATE TRIGGER actualizar_stock_repuesto
AFTER INSERT ON repuestos_orden
BEGIN
    UPDATE repuestos
    SET stock_actual = stock_actual - NEW.cantidad
    WHERE id_repuesto = NEW.id_repuesto;
END;
```

---

*Documento completo de base de datos - 13 tablas detalladas*
