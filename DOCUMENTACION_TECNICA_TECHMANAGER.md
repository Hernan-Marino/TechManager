# DOCUMENTACIÓN TÉCNICA - TECHMANAGER v1.0

## ÍNDICE
1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Directorios](#estructura-de-directorios)
4. [Base de Datos](#base-de-datos)
5. [Módulos del Sistema](#módulos-del-sistema)
6. [Interfaz de Usuario](#interfaz-de-usuario)
7. [Sistema de Seguridad](#sistema-de-seguridad)
8. [Patrones de Diseño](#patrones-de-diseño)
9. [Flujo de Datos](#flujo-de-datos)
10. [Convenciones de Código](#convenciones-de-código)

---

## VISIÓN GENERAL DEL SISTEMA

### ¿Qué es TechManager?
Sistema de gestión integral para talleres de reparación de equipos electrónicos (computadoras, celulares, tablets, etc.).

### Tecnologías Principales
- **Lenguaje**: Python 3.x
- **Framework GUI**: PyQt5
- **Base de Datos**: SQLite3
- **Arquitectura**: Modular MVC (Modelo-Vista-Controlador)

### Características Principales
- Gestión de clientes con estados dinámicos
- Control de equipos ingresados
- Órdenes de trabajo
- Presupuestos y facturación
- Control de repuestos e inventario
- Sistema de garantías
- Auditoría completa
- Backups automáticos
- Multi-usuario con permisos

---

## ARQUITECTURA DEL SISTEMA

### Patrón Arquitectónico: MVC Modular

```
┌─────────────────────────────────────────────────────┐
│                   VISTA (PyQt5)                      │
│            interfaz/ventanas/*.py                    │
│  - Clientes, Equipos, Órdenes, Presupuestos, etc.  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              CONTROLADOR (Módulos)                   │
│                modulos/*.py                          │
│   - Lógica de negocio                               │
│   - Validaciones                                     │
│   - Reglas de negocio                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              MODELO (Base de Datos)                  │
│           base_datos/conexion.py                     │
│           base_datos/crear_tablas.py                 │
│   - SQLite3                                          │
│   - 12 tablas principales                           │
└─────────────────────────────────────────────────────┘
```

### Capas del Sistema

1. **Capa de Presentación** (`interfaz/`)
   - Ventanas PyQt5
   - Componentes reutilizables
   - Estilos centralizados

2. **Capa de Lógica de Negocio** (`modulos/`)
   - Un módulo por funcionalidad
   - Métodos estáticos
   - Validaciones

3. **Capa de Datos** (`base_datos/`)
   - Conexión SQLite
   - Gestión de transacciones
   - Migraciones

4. **Capa de Utilidades** (`sistema_base/`)
   - Seguridad y autenticación
   - Validadores
   - Configuración
   - Mensajes

---

## ESTRUCTURA DE DIRECTORIOS

```
TechManager/
│
├── main.py                          # Punto de entrada principal
├── config.json                      # Configuración del sistema
├── techmanager.db                   # Base de datos SQLite
│
├── base_datos/
│   ├── __init__.py
│   ├── conexion.py                  # Clase DatabaseManager
│   └── crear_tablas.py              # Schema y migraciones
│
├── sistema_base/
│   ├── __init__.py
│   ├── seguridad.py                 # Login, permisos, auditoría
│   ├── validadores.py               # Validación de datos
│   ├── configuracion.py             # Clase ConfigManager
│   └── mensajes.py                  # Clase Mensaje (QMessageBox wrapper)
│
├── modulos/
│   ├── __init__.py
│   ├── clientes.py                  # ModuloClientes
│   ├── equipos.py                   # ModuloEquipos
│   ├── ordenes.py                   # ModuloOrdenes
│   ├── presupuestos.py              # ModuloPresupuestos
│   ├── repuestos.py                 # ModuloRepuestos
│   ├── facturacion_pagos.py         # ModuloFacturacionPagos
│   ├── remitos.py                   # ModuloRemitos
│   ├── garantias.py                 # ModuloGarantias
│   ├── usuarios.py                  # ModuloUsuarios
│   ├── auditoria.py                 # ModuloAuditoria
│   ├── backups.py                   # ModuloBackups
│   └── reportes.py                  # ModuloReportes
│
├── interfaz/
│   ├── __init__.py
│   ├── login.py                     # Ventana de login
│   ├── dashboard.py                 # Dashboard principal
│   │
│   ├── componentes/
│   │   ├── __init__.py
│   │   ├── boton.py                 # Clase Boton reutilizable
│   │   ├── campo_texto.py           # Clase CampoTexto
│   │   ├── etiqueta.py              # Clase Etiqueta
│   │   └── estilos.py               # Clase Estilos (CSS centralizado)
│   │
│   └── ventanas/
│       ├── __init__.py
│       ├── clientes.py              # Ventana Clientes (COMPLETADO ✅)
│       ├── equipos.py               # Ventana Equipos
│       ├── ordenes.py               # Ventana Órdenes
│       ├── presupuestos.py          # Ventana Presupuestos
│       ├── repuestos.py             # Ventana Repuestos
│       ├── facturacion_pagos.py     # Ventana Facturación
│       ├── remitos.py               # Ventana Remitos
│       ├── garantias.py             # Ventana Garantías
│       ├── usuarios.py              # Ventana Usuarios
│       ├── configuracion.py         # Ventana Configuración
│       ├── auditoria.py             # Ventana Auditoría
│       ├── backups.py               # Ventana Backups
│       └── reportes.py              # Ventana Reportes
│
└── logs/
    └── sistema.log                  # Log de eventos del sistema
```

---

## BASE DE DATOS

### Motor: SQLite3
- **Archivo**: `techmanager.db`
- **Codificación**: UTF-8
- **Tipo de transacciones**: ACID compliant

### Tablas Principales (12 tablas)

#### 1. CLIENTES
```sql
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    telefono TEXT NOT NULL UNIQUE,
    direccion TEXT,
    email TEXT,
    observaciones TEXT,
    estado_cliente TEXT NOT NULL DEFAULT 'Nuevo' 
        CHECK(estado_cliente IN ('Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable')),
    es_incobrable BOOLEAN NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT 1,
    tiene_incobrables BOOLEAN NOT NULL DEFAULT 0,
    total_incobrables REAL NOT NULL DEFAULT 0,
    confiabilidad_pago TEXT NOT NULL DEFAULT 'Bueno' 
        CHECK(confiabilidad_pago IN ('Bueno', 'Regular', 'Malo')),
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Campos clave:**
- `estado_cliente`: Estado actual del cliente (se actualiza manual o automáticamente)
- `activo`: Soft delete (0 = eliminado, 1 = activo)
- `nombre` y `apellido`: Separados para mejor organización

#### 2. EQUIPOS
```sql
CREATE TABLE equipos (
    id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    tipo_equipo TEXT NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    numero_serie TEXT,
    descripcion_problema TEXT NOT NULL,
    accesorios TEXT,
    estado_equipo TEXT NOT NULL DEFAULT 'Ingresado',
    fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada_entrega DATETIME,
    fecha_real_entrega DATETIME,
    activo BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);
```

#### 3. ORDENES_TRABAJO
```sql
CREATE TABLE ordenes_trabajo (
    id_orden INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipo INTEGER NOT NULL,
    numero_orden TEXT NOT NULL UNIQUE,
    descripcion_trabajo TEXT NOT NULL,
    diagnostico TEXT,
    trabajo_realizado TEXT,
    estado_orden TEXT NOT NULL DEFAULT 'Pendiente',
    costo_mano_obra REAL DEFAULT 0,
    id_usuario_asignado INTEGER,
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_finalizacion DATETIME,
    prioridad TEXT NOT NULL DEFAULT 'Normal',
    observaciones TEXT,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (id_usuario_asignado) REFERENCES usuarios(id_usuario)
);
```

#### 4. PRESUPUESTOS
```sql
CREATE TABLE presupuestos (
    id_presupuesto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipo INTEGER NOT NULL,
    numero_presupuesto TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    mano_obra REAL NOT NULL DEFAULT 0,
    costo_repuestos REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL,
    estado_presupuesto TEXT NOT NULL DEFAULT 'Pendiente',
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATETIME,
    fecha_aprobacion DATETIME,
    observaciones TEXT,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);
```

#### 5. REPUESTOS
```sql
CREATE TABLE repuestos (
    id_repuesto INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria TEXT,
    marca TEXT,
    modelo_compatible TEXT,
    stock_actual INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 5,
    costo_unitario REAL NOT NULL DEFAULT 0,
    precio_venta REAL NOT NULL DEFAULT 0,
    ubicacion TEXT,
    proveedor TEXT,
    activo BOOLEAN NOT NULL DEFAULT 1
);
```

#### 6. FACTURAS
```sql
CREATE TABLE facturas (
    id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT NOT NULL UNIQUE,
    id_cliente INTEGER NOT NULL,
    id_equipo INTEGER,
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal REAL NOT NULL DEFAULT 0,
    impuestos REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL,
    tipo_factura TEXT NOT NULL,
    estado_factura TEXT NOT NULL DEFAULT 'Pendiente',
    fecha_vencimiento DATETIME,
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);
```

#### 7. PAGOS
```sql
CREATE TABLE pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_factura INTEGER NOT NULL,
    monto REAL NOT NULL,
    metodo_pago TEXT NOT NULL,
    fecha_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    numero_referencia TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_factura) REFERENCES facturas(id_factura)
);
```

#### 8. REMITOS
```sql
CREATE TABLE remitos (
    id_remito INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_remito TEXT NOT NULL UNIQUE,
    id_cliente INTEGER NOT NULL,
    id_equipo INTEGER,
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_remito TEXT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);
```

#### 9. GARANTIAS
```sql
CREATE TABLE garantias (
    id_garantia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipo INTEGER NOT NULL,
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NOT NULL,
    descripcion_garantia TEXT NOT NULL,
    estado_garantia TEXT NOT NULL DEFAULT 'Vigente',
    observaciones TEXT,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
);
```

#### 10. USUARIOS
```sql
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'tecnico',
    email TEXT,
    activo BOOLEAN NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME
);
```

**Roles:**
- `admin`: Acceso total
- `tecnico`: Acceso operativo
- `recepcionista`: Acceso limitado

#### 11. AUDITORIA
```sql
CREATE TABLE auditoria (
    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    accion TEXT NOT NULL,
    modulo TEXT NOT NULL,
    id_registro INTEGER,
    campo_modificado TEXT,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    fecha_accion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    es_critica BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
```

#### 12. CONFIGURACION
```sql
CREATE TABLE configuracion (
    id_config INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Relaciones entre Tablas

```
CLIENTES (1) ──────── (N) EQUIPOS
    │                      │
    │                      │
    │                  (1) ├─── (N) ORDENES_TRABAJO
    │                      │
    │                      │
    │                  (1) ├─── (N) PRESUPUESTOS
    │                      │
    │                      │
    │                  (1) ├─── (N) GARANTIAS
    │                      │
    │                      │
    │                  (1) └─── (N) REMITOS
    │
    │
(1) └──────────────────── (N) FACTURAS ──── (N) PAGOS
```

---

## MÓDULOS DEL SISTEMA

### Estructura de un Módulo Estándar

Todos los módulos siguen el mismo patrón:

```python
class ModuloXXX:
    """Clase para manejar la lógica de negocio de XXX"""
    
    @staticmethod
    def listar_xxx(filtros):
        """Lista registros con filtros"""
        pass
    
    @staticmethod
    def obtener_xxx_por_id(id_xxx):
        """Obtiene un registro por ID"""
        pass
    
    @staticmethod
    def crear_xxx(datos, id_usuario):
        """Crea un nuevo registro"""
        # 1. Validar datos
        # 2. Insertar en BD
        # 3. Registrar en auditoría
        # 4. Retornar (exito, mensaje, id_nuevo)
        pass
    
    @staticmethod
    def modificar_xxx(id_xxx, datos, id_usuario):
        """Modifica un registro existente"""
        # 1. Validar datos
        # 2. Obtener valores anteriores
        # 3. Actualizar en BD
        # 4. Registrar en auditoría
        # 5. Retornar (exito, mensaje)
        pass
    
    @staticmethod
    def eliminar_xxx(id_xxx, id_usuario):
        """Elimina (soft delete) un registro"""
        # 1. Verificar dependencias
        # 2. Marcar activo = 0
        # 3. Registrar en auditoría
        # 4. Retornar (exito, mensaje)
        pass
```

### 1. ModuloClientes (✅ COMPLETADO)

**Ubicación**: `modulos/clientes.py`

**Métodos principales:**
- `listar_clientes(solo_activos, busqueda, orden)`
- `obtener_cliente_por_id(id_cliente)`
- `crear_cliente(nombre, apellido, telefono, direccion, email, id_usuario)`
- `modificar_cliente(id_cliente, nombre, telefono, direccion, email, id_usuario)`
- `eliminar_cliente(id_cliente, id_usuario)` - Soft delete, verifica equipos activos
- `cambiar_estado_cliente(id_cliente, nuevo_estado, id_usuario, motivo)`
- `marcar_deuda_incobrable(id_cliente, monto, motivo, observaciones, id_usuario)`
- `obtener_equipos_cliente(id_cliente)`
- `obtener_notas_cliente(id_cliente)`
- `agregar_nota_cliente(id_cliente, nota, id_usuario)`
- `obtener_estadisticas_clientes()`

**Validaciones:**
- Teléfono único
- Nombre y apellido obligatorios
- Email válido (si se proporciona)

**Estados del cliente:**
- **Nuevo**: Cliente recién creado
- **Buen Pagador**: Paga en tiempo y forma
- **Deudor**: Tiene deuda (30+ días)
- **Moroso**: Deuda antigua (60+ días)
- **Incobrable**: Marcado manualmente por admin

**Lógica de negocio:**
- No se puede eliminar si tiene equipos activos
- Los estados se pueden cambiar manualmente (solo Admin)
- El estado se actualiza automáticamente según atrasos de pago
- Una vez Deudor/Moroso, solo Admin puede volver a Buen Pagador

### 2. ModuloEquipos

**Métodos principales:**
- `listar_equipos(filtros)`
- `obtener_equipo_por_id(id_equipo)`
- `crear_equipo(id_cliente, datos, id_usuario)`
- `modificar_equipo(id_equipo, datos, id_usuario)`
- `cambiar_estado_equipo(id_equipo, nuevo_estado, id_usuario)`
- `obtener_historial_equipo(id_equipo)`

**Estados del equipo:**
- Ingresado
- En diagnóstico
- Esperando repuestos
- En reparación
- Reparado
- No tiene solución
- Entregado
- Abandonado

### 3-12. Otros Módulos

Todos siguen el mismo patrón de:
- Listar
- Obtener por ID
- Crear
- Modificar
- Eliminar
- Métodos específicos según funcionalidad

---

## INTERFAZ DE USUARIO

### Patrón de Ventanas Estándar

Todas las ventanas principales siguen este patrón:

```python
class VentanaXXX(QWidget):
    """Ventana para gestionar XXX"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        # 1. Layout principal
        # 2. Título blanco centrado
        # 3. Barra de búsqueda y botones (azul primario)
        # 4. Tabla de datos
        # 5. Botón "← Volver" (azul)
        pass
    
    def crear_tabla(self):
        """Crea la tabla de datos"""
        pass
    
    def cargar_datos(self):
        """Carga datos desde el módulo"""
        pass
    
    def volver_dashboard(self):
        """Vuelve al dashboard"""
        self.parent_window.mostrar_dashboard()
```

### Componentes Reutilizables

#### 1. Boton (`interfaz/componentes/boton.py`)

```python
class Boton(QPushButton):
    """Botón estilizado reutilizable"""
    
    def __init__(self, texto, tipo="primario"):
        # Tipos: primario, secundario, exito, peligro, neutro
        pass
```

**Colores:**
- `primario`: Azul (#2563eb)
- `secundario`: Gris (#6c757d)
- `exito`: Verde (#28a745)
- `peligro`: Rojo (#dc3545)
- `neutro`: Gris claro (#e9ecef)

#### 2. CampoTexto (`interfaz/componentes/campo_texto.py`)

```python
class CampoTexto(QLineEdit):
    """Campo de texto con placeholder estilizado"""
    
    def __init__(self, placeholder=""):
        pass
```

#### 3. Etiqueta (`interfaz/componentes/etiqueta.py`)

```python
class Etiqueta(QLabel):
    """Etiqueta con estilos predefinidos"""
    
    def __init__(self, texto, tipo="normal"):
        # Tipos: normal, titulo, subtitulo, error
        pass
```

#### 4. Estilos (`interfaz/componentes/estilos.py`)

```python
class Estilos:
    """Clase con estilos CSS centralizados"""
    
    @staticmethod
    def tabla():
        """Estilos para QTableWidget"""
        pass
    
    @staticmethod
    def ventana_principal():
        """Estilos para ventanas principales"""
        pass
```

### Patrón de Ventana Clientes (REFERENCIA ✅)

```python
class VentanaClientes(QWidget):
    def __init__(self, parent=None):
        # Constructor
    
    def inicializar_ui(self):
        # Layout + Título + Búsqueda + Tabla + Botón Volver
    
    def crear_tabla_clientes(self):
        # 7 columnas: ID, Nombre, Teléfono, Dirección, Estado, Observaciones, Deuda
        # Sin columna Acciones (los botones están en ventana de detalles)
    
    def cargar_clientes(self):
        # Cargar desde ModuloClientes.listar_clientes()
    
    def abrir_dialogo_nuevo_cliente(self):
        # DialogoNuevoCliente con nombre y apellido separados
    
    def abrir_dialogo_editar_cliente(self, id_cliente):
        # DialogoEditarCliente con nombre y apellido separados
    
    def ver_detalle_cliente(self, id_cliente):
        # DialogoDetalleCliente con:
        #   - Panel info (5 recuadros unidos)
        #   - Pestañas (Equipos, Timeline)
        #   - Botones (Editar, Cambiar Estado, Eliminar, Cerrar)
    
    def cambiar_estado_cliente(self, id_cliente):
        # Solo Admin - Diálogo para cambiar estado
    
    def eliminar_cliente(self, id_cliente):
        # Solo Admin - Confirmación en español ("Sí" / "No")
        # Verifica equipos activos antes de eliminar
    
    def volver_dashboard(self):
        # Volver al dashboard
```

**ESTE PATRÓN SE DEBE REPLICAR EN TODOS LOS MÓDULOS**

---

## SISTEMA DE SEGURIDAD

### Login y Autenticación

**Archivo**: `sistema_base/seguridad.py`

```python
def autenticar_usuario(nombre_usuario, password):
    """
    Autentica un usuario
    Returns: (exito, mensaje, datos_usuario)
    """
    # 1. Buscar usuario en BD
    # 2. Verificar password con bcrypt
    # 3. Actualizar último acceso
    # 4. Guardar usuario en sesión
    pass

def obtener_usuario_actual():
    """Obtiene el usuario logueado"""
    return usuario_actual  # Variable global

def cerrar_sesion():
    """Cierra la sesión actual"""
    global usuario_actual
    usuario_actual = None
```

### Sistema de Permisos

```python
# En sistema_base/configuracion.py
class ConfigManager:
    def __init__(self):
        self.es_admin = False  # Se actualiza al hacer login
    
    def cargar_permisos_usuario(self, usuario):
        self.es_admin = (usuario['rol'] == 'admin')
```

**Uso en interfaz:**
```python
if config.es_admin:
    # Mostrar botones de admin
    boton_eliminar.setVisible(True)
```

### Auditoría

Todas las acciones críticas se registran:

```python
def registrar_accion_auditoria(id_usuario, accion, modulo, 
                                id_registro=None, campo_modificado=None,
                                valor_anterior=None, valor_nuevo=None,
                                motivo="", es_critica=False):
    """Registra una acción en auditoría"""
    # INSERT en tabla auditoria
```

**Acciones auditadas:**
- Crear, Modificar, Eliminar (cualquier módulo)
- Cambios de estado
- Login/Logout
- Cambios de permisos
- Backups

---

## PATRONES DE DISEÑO

### 1. Singleton (ConfigManager)

```python
# Una única instancia de configuración
config = ConfigManager()
```

### 2. Factory (Estilos)

```python
# Genera estilos según tipo
Estilos.tabla()
Estilos.boton("primario")
```

### 3. MVC (Model-View-Controller)

- **Model**: `modulos/*.py` (lógica) + `base_datos/*.py` (datos)
- **View**: `interfaz/ventanas/*.py` (interfaz)
- **Controller**: Métodos de la vista que llaman al modelo

### 4. Repository (DatabaseManager)

```python
class DatabaseManager:
    def obtener_todos(self, consulta, parametros):
        """Ejecuta SELECT y retorna todos los registros"""
    
    def obtener_uno(self, consulta, parametros):
        """Ejecuta SELECT y retorna un registro"""
    
    def ejecutar_consulta(self, consulta, parametros):
        """Ejecuta INSERT/UPDATE/DELETE"""
```

---

## FLUJO DE DATOS

### Ejemplo: Crear Cliente

```
1. USUARIO hace clic en "➕ Nuevo Cliente"
   ↓
2. INTERFAZ abre DialogoNuevoCliente
   ↓
3. USUARIO completa formulario (nombre, apellido, teléfono, etc.)
   ↓
4. USUARIO hace clic en "Crear Cliente"
   ↓
5. INTERFAZ obtiene datos del formulario
   ↓
6. INTERFAZ llama a ModuloClientes.crear_cliente(datos)
   ↓
7. MÓDULO valida datos (teléfono único, campos obligatorios)
   ↓
8. MÓDULO inserta en base_datos usando db.ejecutar_consulta()
   ↓
9. BASE DE DATOS retorna ID del nuevo cliente
   ↓
10. MÓDULO registra acción en auditoría
   ↓
11. MÓDULO retorna (True, "Cliente creado", id_nuevo)
   ↓
12. INTERFAZ muestra mensaje de éxito
   ↓
13. INTERFAZ cierra diálogo
   ↓
14. INTERFAZ recarga tabla de clientes
```

### Ejemplo: Eliminar Cliente

```
1. USUARIO hace clic en "🗑️ Eliminar Cliente"
   ↓
2. INTERFAZ verifica if config.es_admin (si no, no muestra botón)
   ↓
3. INTERFAZ muestra diálogo de confirmación ("Sí" / "No")
   ↓
4. USUARIO confirma eliminación
   ↓
5. INTERFAZ llama a ModuloClientes.eliminar_cliente(id, id_usuario)
   ↓
6. MÓDULO verifica equipos activos (SELECT COUNT)
   ↓
7a. SI tiene equipos activos → retorna (False, "No se puede eliminar: tiene X equipos")
   ↓
   INTERFAZ muestra error
   ↓
   FIN
   ↓
7b. SI NO tiene equipos activos → continúa
   ↓
8. MÓDULO ejecuta UPDATE clientes SET activo = 0
   ↓
9. MÓDULO registra en auditoría (acción crítica)
   ↓
10. MÓDULO retorna (True, "Cliente eliminado")
   ↓
11. INTERFAZ muestra mensaje de éxito
   ↓
12. INTERFAZ recarga tabla (filtrada por activo = 1)
```

---

## CONVENCIONES DE CÓDIGO

### Nomenclatura

#### Variables
```python
# Snake case
nombre_cliente = "Juan"
id_usuario = 1
fecha_ingreso = datetime.now()
```

#### Clases
```python
# Pascal case
class ModuloClientes:
    pass

class VentanaEquipos(QWidget):
    pass
```

#### Métodos
```python
# Snake case
def crear_cliente(self):
    pass

def obtener_cliente_por_id(self, id_cliente):
    pass
```

#### Constantes
```python
# Mayúsculas con guión bajo
ESTADO_NUEVO = "Nuevo"
ESTADO_BUEN_PAGADOR = "Buen Pagador"
```

### Estructura de Métodos en Módulos

```python
@staticmethod
def metodo_ejemplo(parametro1, parametro2, id_usuario):
    """
    Descripción del método
    
    Args:
        parametro1 (tipo): Descripción
        parametro2 (tipo): Descripción
        id_usuario (int): ID del usuario que ejecuta la acción
    
    Returns:
        tuple: (exito, mensaje) o (exito, mensaje, id_nuevo)
    """
    try:
        # 1. Validaciones
        if not parametro1:
            return False, "Error de validación", None
        
        # 2. Lógica principal
        resultado = db.ejecutar_consulta(...)
        
        # 3. Auditoría
        registrar_accion_auditoria(...)
        
        # 4. Log
        config.guardar_log("Acción completada", "INFO")
        
        # 5. Retorno
        return True, "Éxito", resultado
        
    except Exception as e:
        config.guardar_log(f"Error: {e}", "ERROR")
        return False, f"Error: {str(e)}", None
```

### Manejo de Errores

```python
# Siempre usar try-except en métodos de módulos
try:
    # Código que puede fallar
    resultado = operacion_riesgosa()
except Exception as e:
    # Registrar error
    config.guardar_log(f"Error en metodo_x: {e}", "ERROR")
    # Retornar tupla de error
    return False, f"Error: {str(e)}"
```

### Comentarios

```python
# Comentario de línea para explicación breve

"""
Comentario de bloque
para explicaciones más largas
o documentación de clases/métodos
"""

# TODO: Tarea pendiente
# FIXME: Bug conocido que necesita arreglo
# NOTE: Nota importante sobre implementación
```

### Validaciones

```python
# Validar datos ANTES de insertar en BD
if not nombre or not nombre.strip():
    return False, "El nombre es obligatorio"

if not telefono:
    return False, "El teléfono es obligatorio"

# Usar validadores centralizados
from sistema_base.validadores import validar_telefono, validar_email

es_valido, mensaje = validar_telefono(telefono)
if not es_valido:
    return False, mensaje
```

### Soft Delete

```python
# NUNCA hacer DELETE, usar UPDATE activo = 0
consulta = "UPDATE tabla SET activo = 0 WHERE id = ?"
db.ejecutar_consulta(consulta, (id_registro,))

# Al listar, filtrar por activo = 1
consulta = "SELECT * FROM tabla WHERE activo = 1"
```

---

## DECISIONES DE DISEÑO IMPORTANTES

### 1. ¿Por qué SQLite y no MySQL/PostgreSQL?
- **Simplicidad**: Un solo archivo de BD
- **Portabilidad**: Fácil de hacer backup (copiar archivo)
- **Sin servidor**: No requiere instalación de servidor de BD
- **Suficiente**: Para talleres pequeños/medianos (< 10,000 registros/tabla)

### 2. ¿Por qué PyQt5 y no Tkinter/wxPython?
- **Profesionalismo**: Interfaces más modernas
- **Componentes**: Mayor cantidad de widgets nativos
- **Estabilidad**: Framework maduro y bien documentado
- **Cross-platform**: Funciona igual en Windows/Linux/Mac

### 3. ¿Por qué Soft Delete?
- **Auditoría**: Mantener historial completo
- **Recuperación**: Poder deshacer eliminaciones
- **Integridad**: No romper relaciones con otras tablas

### 4. ¿Por qué Módulos Estáticos?
- **Simplicidad**: No necesita instanciar clases
- **Claridad**: ModuloClientes.crear_cliente() es directo
- **Sin estado**: No mantiene variables de instancia

### 5. ¿Por qué Separar Interfaz y Lógica?
- **Mantenibilidad**: Cambiar UI sin tocar lógica
- **Testing**: Probar lógica sin UI
- **Reutilización**: Misma lógica en diferentes interfaces

---

## PRÓXIMOS PASOS DE DESARROLLO

### Módulos Pendientes (11 de 12)
- [ ] Equipos
- [ ] Órdenes de Trabajo
- [ ] Presupuestos
- [ ] Repuestos
- [ ] Facturación y Pagos
- [ ] Remitos
- [ ] Garantías
- [ ] Usuarios
- [ ] Configuración
- [ ] Auditoría
- [ ] Backups
- [ ] Reportes

### Patrón a Seguir (Basado en Clientes ✅)

Para cada módulo:

1. **Base de Datos**
   - Verificar tabla existe
   - Agregar columnas necesarias (apellido, activo, etc.)
   - Crear índices si son necesarios

2. **Módulo de Lógica**
   - Implementar métodos CRUD básicos
   - Agregar validaciones
   - Implementar soft delete
   - Registrar auditoría en acciones críticas

3. **Interfaz**
   - Título blanco centrado
   - Barra búsqueda + botones (azul primario)
   - Tabla sin columna Acciones
   - Botón "← Volver" azul
   - Diálogo de creación/edición
   - Ventana de detalles con botones de acción

4. **Testing Manual**
   - Crear registro
   - Editar registro
   - Eliminar registro (si admin)
   - Buscar registros
   - Ver detalles

---

## PROBLEMAS CONOCIDOS Y SOLUCIONES

### Problema: Botones de Acciones no se veían
**Solución aplicada**: Mover botones a ventana de detalles en vez de columna en tabla

### Problema: Nombre completo en un solo campo
**Solución aplicada**: Separar en nombre y apellido con campos independientes

### Problema: Estados de cliente no dinámicos
**Solución aplicada**: Sistema de estados con cambio manual (Admin) y preparado para automático

### Problema: No se podía eliminar clientes
**Solución aplicada**: Soft delete con verificación de equipos activos

---

## RECURSOS Y DEPENDENCIAS

### Dependencias Python (requirements.txt)
```
PyQt5==5.15.9
bcrypt==4.0.1
```

### Instalación
```bash
pip install PyQt5 bcrypt
```

### Ejecución
```bash
python main.py
```

---

## CONTACTO Y MANTENIMIENTO

**Sistema**: TechManager v1.0  
**Desarrollado para**: Taller de reparación de equipos  
**Arquitectura**: Modular MVC  
**Base de datos**: SQLite3  
**Interfaz**: PyQt5  

---

*Última actualización: Enero 2026*
*Módulos completados: 1/12 (Clientes ✅)*

---

## DIAGRAMAS ADICIONALES

### Diagrama de Flujo - Eliminar Cliente

\`\`\`
INICIO
  │
  ▼
Usuario hace clic en "Eliminar Cliente"
  │
  ▼
¿Es Admin? ──NO──> Botón no visible → FIN
  │
 SÍ
  │
  ▼
Mostrar diálogo confirmación
"¿Estás seguro? Sí / No"
  │
  ▼
Usuario selecciona ──NO──> Cancelar → FIN
  │
 SÍ
  │
  ▼
Llamar ModuloClientes.eliminar_cliente(id, id_usuario)
  │
  ▼
Verificar equipos activos
SELECT COUNT(*) FROM equipos WHERE id_cliente=? AND activo=1
  │
  ├──> COUNT > 0 ──> Retornar (False, "Tiene X equipos activos")
  │                       │
  │                       ▼
  │                  Mostrar error al usuario
  │                       │
  │                       ▼
  │                      FIN
  │
  └──> COUNT = 0
        │
        ▼
   UPDATE clientes SET activo=0 WHERE id_cliente=?
        │
        ▼
   Registrar en auditoría
   (acción CRÍTICA)
        │
        ▼
   Retornar (True, "Cliente eliminado")
        │
        ▼
   Mostrar mensaje éxito
        │
        ▼
   Recargar tabla clientes
   (filtrada por activo=1)
        │
        ▼
      FIN
\`\`\`

---

## SISTEMA DE CONFIGURACIÓN COMPLETO

### Archivo config.json

\`\`\`json
{
  "empresa": {
    "nombre": "TechRepair Solutions",
    "direccion": "Av. Principal 1234",
    "telefono": "011-1234-5678",
    "email": "info@techrepair.com",
    "cuit": "20-12345678-9"
  },
  "sistema": {
    "version": "1.0.0",
    "nombre_base_datos": "techmanager.db",
    "ruta_logs": "logs/",
    "ruta_backups": "backups/",
    "nivel_log": "INFO"
  },
  "backups": {
    "automatico": true,
    "frecuencia": "diario",
    "hora": "02:00",
    "mantener_ultimos": 30,
    "ruta_auto": "backups/auto/",
    "ruta_manual": "backups/manual/"
  },
  "clientes": {
    "dias_moroso": 30,
    "dias_incobrable": 60,
    "actualizar_estados_auto": true
  },
  "equipos": {
    "dias_abandono": 90,
    "alertar_abandono": 60
  },
  "facturacion": {
    "tipo_factura_default": "B",
    "iva_defecto": 21,
    "incluir_iva": true
  },
  "interfaz": {
    "tema": "claro",
    "fuente": "Segoe UI",
    "tamano_fuente": 10,
    "mostrar_ayuda": true
  }
}
\`\`\`

### Clase ConfigManager Completa

\`\`\`python
import json
import os
from datetime import datetime

class ConfigManager:
    """Gestor centralizado de configuración del sistema"""
    
    def __init__(self, archivo_config="config.json"):
        self.archivo_config = archivo_config
        self.config = {}
        self.es_admin = False
        self.usuario_actual = None
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.crear_configuracion_default()
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            self.crear_configuracion_default()
    
    def crear_configuracion_default(self):
        """Crea archivo de configuración por defecto"""
        self.config = {
            "empresa": {
                "nombre": "TechManager",
                "direccion": "",
                "telefono": "",
                "email": "",
                "cuit": ""
            },
            "sistema": {
                "version": "1.0.0",
                "nombre_base_datos": "techmanager.db",
                "ruta_logs": "logs/",
                "ruta_backups": "backups/",
                "nivel_log": "INFO"
            },
            "backups": {
                "automatico": True,
                "frecuencia": "diario",
                "hora": "02:00",
                "mantener_ultimos": 30
            },
            "clientes": {
                "dias_moroso": 30,
                "dias_incobrable": 60
            }
        }
        self.guardar_configuracion()
    
    def guardar_configuracion(self):
        """Guarda la configuración en el archivo JSON"""
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def obtener(self, clave, default=None):
        """Obtiene un valor de configuración"""
        try:
            keys = clave.split('.')
            valor = self.config
            for key in keys:
                valor = valor.get(key)
                if valor is None:
                    return default
            return valor
        except:
            return default
    
    def establecer(self, clave, valor):
        """Establece un valor de configuración"""
        try:
            keys = clave.split('.')
            config = self.config
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            config[keys[-1]] = valor
            return self.guardar_configuracion()
        except Exception as e:
            print(f"Error al establecer configuración: {e}")
            return False
    
    def cargar_permisos_usuario(self, usuario):
        """Carga los permisos del usuario actual"""
        self.usuario_actual = usuario
        self.es_admin = (usuario.get('rol') == 'admin')
    
    def guardar_log(self, mensaje, nivel="INFO"):
        """Guarda un mensaje en el log del sistema"""
        try:
            ruta_logs = self.obtener('sistema.ruta_logs', 'logs/')
            os.makedirs(ruta_logs, exist_ok=True)
            
            archivo_log = os.path.join(ruta_logs, 'sistema.log')
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            linea_log = f"[{timestamp}] [{nivel}] {mensaje}\\n"
            
            with open(archivo_log, 'a', encoding='utf-8') as f:
                f.write(linea_log)
            
            # Si es error, también guardarlo en errores.log
            if nivel in ['ERROR', 'CRITICAL']:
                archivo_errores = os.path.join(ruta_logs, 'errores.log')
                with open(archivo_errores, 'a', encoding='utf-8') as f:
                    f.write(linea_log)
                    
        except Exception as e:
            print(f"Error al guardar log: {e}")

# Instancia global
config = ConfigManager()
\`\`\`

---

## SISTEMA DE VALIDADORES COMPLETO

### Archivo validadores.py

\`\`\`python
import re
from datetime import datetime

def validar_email(email):
    """
    Valida formato de email
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    if not email or not email.strip():
        return False, "El email no puede estar vacío"
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    
    if not re.match(patron, email.strip()):
        return False, "Formato de email inválido"
    
    return True, ""

def validar_telefono(telefono):
    """
    Valida formato de teléfono
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    if not telefono or not telefono.strip():
        return False, "El teléfono no puede estar vacío"
    
    # Remover espacios, guiones y paréntesis
    telefono_limpio = telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Debe tener entre 7 y 15 dígitos
    if not telefono_limpio.isdigit():
        return False, "El teléfono solo debe contener números"
    
    if len(telefono_limpio) < 7:
        return False, "El teléfono debe tener al menos 7 dígitos"
    
    if len(telefono_limpio) > 15:
        return False, "El teléfono no puede tener más de 15 dígitos"
    
    return True, ""

def limpiar_telefono(telefono):
    """
    Limpia el teléfono removiendo caracteres no numéricos
    
    Returns:
        str: Teléfono limpio
    """
    if not telefono:
        return ""
    
    return telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

def validar_nombre(nombre):
    """
    Valida que el nombre solo contenga letras y espacios
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío"
    
    nombre = nombre.strip()
    
    if len(nombre) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(nombre) > 100:
        return False, "El nombre no puede tener más de 100 caracteres"
    
    # Permitir letras, espacios y caracteres acentuados
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$'
    
    if not re.match(patron, nombre):
        return False, "El nombre solo puede contener letras y espacios"
    
    return True, ""

def validar_cuit(cuit):
    """
    Valida formato de CUIT argentino
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    if not cuit:
        return True, ""  # CUIT es opcional
    
    # Remover guiones
    cuit_limpio = cuit.replace("-", "").strip()
    
    if not cuit_limpio.isdigit():
        return False, "El CUIT solo debe contener números"
    
    if len(cuit_limpio) != 11:
        return False, "El CUIT debe tener 11 dígitos"
    
    return True, ""

def validar_precio(precio):
    """
    Valida que el precio sea un número positivo
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    try:
        precio_float = float(precio)
        
        if precio_float < 0:
            return False, "El precio no puede ser negativo"
        
        return True, ""
    except ValueError:
        return False, "El precio debe ser un número válido"

def validar_stock(stock):
    """
    Valida que el stock sea un número entero positivo
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    try:
        stock_int = int(stock)
        
        if stock_int < 0:
            return False, "El stock no puede ser negativo"
        
        return True, ""
    except ValueError:
        return False, "El stock debe ser un número entero"

def validar_fecha(fecha_str, formato="%Y-%m-%d"):
    """
    Valida formato de fecha
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    try:
        datetime.strptime(fecha_str, formato)
        return True, ""
    except ValueError:
        return False, f"Formato de fecha inválido. Use {formato}"

def formatear_dinero(monto):
    """
    Formatea un monto como dinero
    
    Returns:
        str: Monto formateado (ej: "$1.234,56")
    """
    try:
        monto_float = float(monto)
        # Formato: separador de miles punto, decimales coma
        return f"${monto_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "$0,00"
\`\`\`

---

## TROUBLESHOOTING COMÚN

### Problema 1: Error al iniciar el sistema

**Síntoma**: `ModuleNotFoundError: No module named 'PyQt5'`

**Solución**:
\`\`\`bash
pip install PyQt5
\`\`\`

### Problema 2: Base de datos bloqueada

**Síntoma**: `sqlite3.OperationalError: database is locked`

**Causas posibles**:
1. Otra instancia del programa está abierta
2. Backup en progreso
3. Archivo .db-journal presente

**Solución**:
\`\`\`bash
# 1. Cerrar todas las instancias
# 2. Eliminar archivo journal si existe
rm techmanager.db-journal
# 3. Reiniciar el programa
\`\`\`

### Problema 3: No se pueden eliminar clientes

**Síntoma**: "No se puede eliminar: el cliente tiene X equipo(s) activo(s)"

**Causa**: El cliente tiene equipos asociados marcados como activos

**Solución**:
1. Entregar o marcar como abandonados los equipos del cliente
2. Luego eliminar el cliente

### Problema 4: Botones no responden

**Síntoma**: Los botones no hacen nada al hacer clic

**Causas posibles**:
1. Error en el connect() del botón
2. Método no implementado
3. Excepción silenciosa

**Solución**:
\`\`\`python
# Verificar que el connect esté bien
boton.clicked.connect(self.metodo)  # ✓ Correcto
boton.clicked.connect(self.metodo())  # ✗ Incorrecto (ejecuta inmediatamente)

# Agregar try-catch para ver errores
def metodo(self):
    try:
        # código
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
\`\`\`

### Problema 5: Campos de texto no validan

**Síntoma**: Se pueden ingresar datos inválidos

**Solución**: Agregar validadores

\`\`\`python
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp

# Solo números
validador_numeros = QRegExpValidator(QRegExp("[0-9]+"))
campo.setValidator(validador_numeros)

# Solo letras
validador_letras = QRegExpValidator(QRegExp("[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+"))
campo.setValidator(validador_letras)
\`\`\`

---

## PREGUNTAS FRECUENTES (FAQ)

### ¿Cómo agregar un nuevo campo a una tabla?

\`\`\`python
# En crear_tablas.py, agregar migration:
try:
    db.ejecutar_consulta("ALTER TABLE clientes ADD COLUMN nuevo_campo TEXT")
except:
    pass  # La columna ya existe
\`\`\`

### ¿Cómo crear un nuevo módulo?

1. Crear archivo en `modulos/nuevo_modulo.py`
2. Copiar estructura de `modulos/clientes.py`
3. Implementar métodos: listar, obtener_por_id, crear, modificar, eliminar
4. Crear ventana en `interfaz/ventanas/nuevo_modulo.py`
5. Copiar estructura de `interfaz/ventanas/clientes.py`
6. Agregar botón en Dashboard

### ¿Cómo cambiar los colores del sistema?

Editar `interfaz/componentes/estilos.py`:

\`\`\`python
# Cambiar color primario
PRIMARIO = "#2563eb"  # Azul actual
PRIMARIO = "#10b981"  # Verde alternativo
\`\`\`

### ¿Cómo hacer backup manual?

\`\`\`python
import shutil
from datetime import datetime

fecha = datetime.now().strftime('%Y-%m-%d_%H-%M')
shutil.copy('techmanager.db', f'backups/manual/backup_{fecha}.db')
\`\`\`

### ¿Cómo restaurar un backup?

\`\`\`bash
# 1. Cerrar el programa
# 2. Renombrar BD actual
mv techmanager.db techmanager_old.db
# 3. Copiar backup
cp backups/manual/backup_2026-01-29.db techmanager.db
# 4. Reiniciar programa
\`\`\`

---

## ROADMAP Y FUTURAS MEJORAS

### Versión 1.1 (Próxima)
- [ ] Notificaciones automáticas de vencimientos
- [ ] Exportación a Excel
- [ ] Impresión de presupuestos y facturas
- [ ] Sistema de plantillas de email

### Versión 1.2
- [ ] Dashboard con gráficos estadísticos
- [ ] Reportes personalizables
- [ ] API REST para integraciones
- [ ] App móvil (consulta de estados)

### Versión 2.0 (Futuro)
- [ ] Multi-sucursal
- [ ] Base de datos MySQL/PostgreSQL
- [ ] Sistema de turnos online
- [ ] Integración con AFIP
- [ ] Firma digital de presupuestos

---

*Documentación actualizada: Enero 2026*
*Versión del sistema: 1.0*
*Módulos completados: 1/12 (Clientes ✅)*

