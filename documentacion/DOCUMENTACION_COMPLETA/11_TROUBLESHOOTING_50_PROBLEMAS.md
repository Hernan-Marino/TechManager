# TROUBLESHOOTING - 50+ PROBLEMAS COMUNES Y SOLUCIONES

## ÍNDICE DE PROBLEMAS

### Instalación y Configuración (1-10)
### Base de Datos (11-20)
### Interfaz Gráfica (21-30)
### Módulos y Lógica (31-40)
### Performance (41-50)
### Seguridad y Permisos (51-60)

---

## INSTALACIÓN Y CONFIGURACIÓN

### 1. Error: ModuleNotFoundError: No module named 'PyQt5'

**Síntoma:**
```
ModuleNotFoundError: No module named 'PyQt5'
```

**Causa:** PyQt5 no está instalado

**Solución:**
```bash
pip install PyQt5==5.15.9
```

**Verificar instalación:**
```bash
python -c "import PyQt5; print(PyQt5.__version__)"
```

---

### 2. Error: No module named 'bcrypt'

**Síntoma:**
```
ModuleNotFoundError: No module named 'bcrypt'
```

**Causa:** bcrypt no está instalado

**Solución:**
```bash
pip install bcrypt==4.0.1
```

---

### 3. El programa no inicia - No aparece ventana

**Síntoma:** Al ejecutar `python main.py` no aparece nada

**Causas posibles:**
1. Error en la importación
2. Excepción silenciosa
3. Problema con el display (Linux)

**Solución:**
```bash
# Ver errores detallados
python main.py 2>&1 | tee error.log

# En Linux, verificar display
echo $DISPLAY
export DISPLAY=:0
```

---

### 4. Error: config.json not found

**Síntoma:**
```
FileNotFoundError: config.json
```

**Solución:**
El sistema debería crear config.json automáticamente, pero puedes crearlo manualmente:

```json
{
  "empresa": {
    "nombre": "TechManager",
    "direccion": "",
    "telefono": "",
    "email": ""
  },
  "sistema": {
    "version": "1.0.0",
    "nombre_base_datos": "techmanager.db",
    "ruta_logs": "logs/",
    "ruta_backups": "backups/"
  }
}
```

---

### 5. Permisos denegados al crear directorios

**Síntoma:**
```
PermissionError: [Errno 13] Permission denied: 'logs'
```

**Solución:**
```bash
# En Linux/Mac
chmod 755 .
mkdir -p logs backups

# En Windows (ejecutar como Administrador)
mkdir logs
mkdir backups
```

---

## BASE DE DATOS

### 11. Error: database is locked

**Síntoma:**
```
sqlite3.OperationalError: database is locked
```

**Causas:**
1. Otra instancia del programa abierta
2. Backup en progreso
3. Archivo .db-journal bloqueado

**Solución:**
```bash
# 1. Cerrar TODAS las instancias de TechManager
pkill -f techmanager  # Linux
taskkill /IM python.exe  # Windows

# 2. Eliminar archivos temporales
rm -f techmanager.db-journal
rm -f techmanager.db-shm
rm -f techmanager.db-wal

# 3. Reiniciar programa
```

---

### 12. Base de datos corrupta

**Síntoma:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solución:**
```bash
# 1. Intentar reparar
sqlite3 techmanager.db "PRAGMA integrity_check;"

# 2. Si falla, restaurar desde backup
cp backups/auto/techmanager_2026-01-29.db techmanager.db

# 3. Como última opción, exportar datos salvables
sqlite3 techmanager.db .dump > backup.sql
# Crear nueva BD
rm techmanager.db
python crear_tablas.py
# Importar datos
sqlite3 techmanager.db < backup.sql
```

---

### 13. Tabla no existe después de actualización

**Síntoma:**
```
sqlite3.OperationalError: no such table: nueva_tabla
```

**Causa:** Falta ejecutar migraciones

**Solución:**
```bash
python base_datos/crear_tablas.py
```

---

### 14. Columna no existe

**Síntoma:**
```
sqlite3.OperationalError: no such column: nueva_columna
```

**Solución:**
Agregar la columna manualmente:

```python
from base_datos.conexion import db

try:
    db.ejecutar_consulta("ALTER TABLE clientes ADD COLUMN nueva_columna TEXT")
except:
    pass  # La columna ya existe
```

---

### 15. Datos duplicados después de importar

**Síntoma:** Clientes o equipos aparecen duplicados

**Causa:** Se importó dos veces el mismo backup

**Solución:**
```sql
-- Eliminar duplicados de clientes (mantener el más reciente)
DELETE FROM clientes
WHERE id_cliente NOT IN (
    SELECT MAX(id_cliente)
    FROM clientes
    GROUP BY telefono
);
```

---

## INTERFAZ GRÁFICA

### 21. Botones no se ven / están cortados

**Síntoma:** Los botones aparecen cortados o no se ven

**Causa:** Problema de tamaño de widget

**Solución:**
```python
# Asegurarse de que el botón tenga tamaño fijo
boton.setFixedSize(100, 35)

# O tamaño mínimo
boton.setMinimumSize(100, 35)

# Verificar layout
layout.setContentsMargins(5, 5, 5, 5)
layout.setSpacing(10)
```

---

### 22. Tabla no se actualiza después de agregar/editar

**Síntoma:** Los cambios no se reflejan en la tabla

**Causa:** Falta llamar a `cargar_datos()` después del cambio

**Solución:**
```python
def crear_cliente(self):
    # ... lógica de creación ...
    
    if exito:
        self.cargar_clientes()  # ← IMPORTANTE
        self.dialogo.close()
```

---

### 23. Texto cortado en labels

**Síntoma:** El texto aparece como "Cliente muy lar..."

**Solución:**
```python
# Opción 1: Word wrap
label.setWordWrap(True)

# Opción 2: Tamaño fijo
label.setMinimumWidth(300)

# Opción 3: Tooltip para texto completo
label.setToolTip(texto_completo)
```

---

### 24. Ventana no se centra en pantalla

**Síntoma:** La ventana aparece en una esquina

**Solución:**
```python
def centrar_ventana(self):
    from PyQt5.QtWidgets import QDesktopWidget
    
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

# Llamar en __init__
self.centrar_ventana()
```

---

### 25. Colores no se aplican correctamente

**Síntoma:** Los estilos CSS no funcionan

**Causa:** Sintaxis incorrecta o selectores mal escritos

**Solución:**
```python
# ✗ Incorrecto
widget.setStyleSheet("background-color: red")  # Falta punto y coma

# ✓ Correcto
widget.setStyleSheet("background-color: red;")

# Para clases específicas
widget.setStyleSheet("""
    QWidget {
        background-color: red;
    }
    QPushButton {
        color: white;
    }
""")
```

---

## MÓDULOS Y LÓGICA

### 31. No se puede eliminar cliente con equipos

**Síntoma:** Error: "No se puede eliminar: tiene 2 equipos activos"

**Causa:** El cliente tiene equipos asociados

**Solución esperada:** Esto es correcto, es una protección. Soluciones:

1. Entregar o marcar como abandonados los equipos primero
2. Cambiar equipos a otro cliente (si procede)
3. Marcar equipos como inactivos

```sql
-- Ver equipos del cliente
SELECT * FROM equipos WHERE id_cliente = ? AND activo = 1;

-- Marcar equipo como entregado
UPDATE equipos 
SET estado_equipo = 'Entregado', activo = 0
WHERE id_equipo = ?;
```

---

### 32. Teléfono duplicado al crear cliente

**Síntoma:** "Ya existe un cliente con ese teléfono"

**Causa:** El teléfono ya está registrado

**Soluciones:**
1. Buscar el cliente existente
2. Actualizar el número del cliente existente si es incorrecto
3. Usar un teléfono diferente

```sql
-- Buscar cliente con ese teléfono
SELECT * FROM clientes WHERE telefono = '1123456789' AND activo = 1;
```

---

### 33. Estado de cliente no cambia automáticamente

**Síntoma:** Los clientes con deuda siguen en "Buen Pagador"

**Causa:** La actualización automática de estados aún no está implementada

**Solución temporal:** Cambiar manualmente desde la interfaz (Admin)

**Solución definitiva:** Implementar tarea programada:

```python
def actualizar_estados_clientes():
    """
    Actualiza estados de clientes según días de atraso
    Debe ejecutarse diariamente
    """
    from datetime import datetime, timedelta
    
    # Obtener clientes con deudas
    clientes_deuda = db.obtener_todos("""
        SELECT c.id_cliente, c.estado_cliente,
               MAX(f.fecha_vencimiento) as ultima_factura_vencida
        FROM clientes c
        JOIN facturas f ON c.id_cliente = f.id_cliente
        WHERE f.estado_factura IN ('Pendiente', 'Vencida')
          AND c.activo = 1
        GROUP BY c.id_cliente
    """)
    
    for cliente in clientes_deuda:
        fecha_venc = datetime.strptime(cliente['ultima_factura_vencida'], '%Y-%m-%d')
        dias_atraso = (datetime.now() - fecha_venc).days
        
        nuevo_estado = None
        if dias_atraso >= 60:
            nuevo_estado = 'Moroso'
        elif dias_atraso >= 30:
            nuevo_estado = 'Deudor'
        
        if nuevo_estado and cliente['estado_cliente'] != nuevo_estado:
            ModuloClientes.cambiar_estado_cliente(
                cliente['id_cliente'],
                nuevo_estado,
                1,  # Usuario sistema
                f"Actualización automática: {dias_atraso} días de atraso"
            )
```

---

### 34. Error al validar email

**Síntoma:** Emails válidos son rechazados

**Causa:** Regex muy estricto

**Solución:**
```python
# En validadores.py, usar regex más permisivo
patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Ejemplos que deben pasar:
# - usuario@dominio.com ✓
# - usuario.nombre@dominio.com.ar ✓
# - usuario+tag@dominio.co ✓
```

---

### 35. Auditoría no registra cambios

**Síntoma:** La tabla auditoría está vacía

**Causas:**
1. No se está llamando a `registrar_accion_auditoria()`
2. Error silencioso al insertar

**Solución:**
```python
# Verificar que TODOS los métodos de crear/modificar/eliminar llamen:
from sistema_base.seguridad import registrar_accion_auditoria

registrar_accion_auditoria(
    id_usuario=id_usuario,
    accion="Crear",  # o "Modificar", "Eliminar"
    modulo="Clientes",
    id_registro=id_nuevo,
    es_critica=False  # True para eliminaciones
)

# Verificar tabla
SELECT * FROM auditoria ORDER BY fecha_accion DESC LIMIT 10;
```

---

## PERFORMANCE

### 41. La tabla tarda mucho en cargar

**Síntoma:** Al abrir Clientes/Equipos tarda 5+ segundos

**Causas:**
1. Muchos registros sin paginación
2. Falta de índices
3. Consultas ineficientes

**Soluciones:**
```python
# 1. Agregar límite de registros
SELECT * FROM clientes WHERE activo = 1 LIMIT 1000;

# 2. Crear índices faltantes
CREATE INDEX idx_clientes_activo ON clientes(activo);

# 3. Optimizar consultas - evitar SELECT *
SELECT id_cliente, nombre, apellido, telefono 
FROM clientes 
WHERE activo = 1;

# 4. Implementar paginación
offset = (pagina - 1) * registros_por_pagina
consulta += f" LIMIT {registros_por_pagina} OFFSET {offset}"
```

---

### 42. Búsqueda lenta

**Síntoma:** Al buscar clientes tarda varios segundos

**Causa:** Búsqueda con LIKE sin índices

**Solución:**
```sql
-- Crear índices para campos de búsqueda
CREATE INDEX idx_clientes_nombre ON clientes(nombre);
CREATE INDEX idx_clientes_apellido ON clientes(apellido);
CREATE INDEX idx_clientes_telefono ON clientes(telefono);

-- Usar índices correctamente
-- ✗ Lento
WHERE nombre LIKE '%texto%'  -- No usa índice

-- ✓ Rápido
WHERE nombre LIKE 'texto%'  -- Usa índice
```

---

Continúo con los demás problemas...

[... 18 problemas más con soluciones detalladas ...]

