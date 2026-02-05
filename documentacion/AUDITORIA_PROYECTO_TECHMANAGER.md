# Auditoría técnica del proyecto TechManager v1.0

**Enfoque:** Ingeniería de sistemas – revisión de todos los módulos (terminados y en desarrollo), mejoras, correcciones y brechas.

**Fecha de auditoría:** Febrero 2026

---

## 1. Resumen ejecutivo

| Área | Estado | Crítico |
|------|--------|--------|
| Módulo Clientes (lógica + UI) | ✅ Terminado y consistente | No |
| Módulo Equipos (lógica + UI) | 🟡 En desarrollo – errores concretos | Sí |
| Órdenes, Presupuestos, Facturación, Pagos, etc. | 🟠 Parcial – incoherencias BD/imports | Sí |
| Reportes, Auditoría, Backups, Configuración | 🔴 Incompletos o rotos | Sí |
| Base de datos vs módulos | 🔴 Nombres de tablas/columnas no alineados | Sí |

Hay **errores que impiden ejecutar flujos completos** (imports incorrectos, tablas/columnas que no existen, métodos que no existen). Se recomienda priorizar la alineación BD + módulos y la corrección de imports antes de seguir con nuevas funcionalidades.

---

## 2. Módulos terminados – qué mejorar y corregir

### 2.1 Clientes (modulos/clientes.py + interfaz/ventanas/clientes.py)

**Estado:** Terminado y alineado con la BD.

**Mejoras recomendadas:**

1. **Listado:** El parámetro `solo_activos` en `listar_clientes()` no se usa (no filtra por equipos abandonados). Implementar el filtro o quitarlo de la firma/documentación.
2. **Validación:** Unificar criterio de “nombre”: hoy se exige nombre y apellido; si en otros módulos se muestra “apellido, nombre”, mantener ese orden en toda la app.
3. **Auditoría en modificar:** Estás registrando cada campo por separado; si hay muchos cambios, considerar un solo registro con motivo “Modificación múltiple” y detalle en motivo o en un JSON en valor_nuevo (según política de auditoría).
4. **Eliminar:** Verificar que el mensaje “X equipo(s) activo(s)” use correctamente singular/plural según `resultado['total']`.

**Correcciones menores:**

- En `obtener_cliente_por_id` el SELECT no incluye `notas`; si la UI muestra notas, añadir el campo para no tener que hacer otra consulta.

---

### 2.2 Equipos (modulos/equipos_LOGICA.py + interfaz/ventanas/equipos.py)

**Estado:** En desarrollo; la lógica tiene varios fallos que hay que corregir.

**Correcciones obligatorias:**

1. **Método duplicado `eliminar_equipo`**  
   Hay **dos definiciones** de `eliminar_equipo` (aprox. líneas 519–566 y 568–623). La segunda sobrescribe a la primera. Dejar **una sola** implementación:
   - Revisar nombres de columnas contra `crear_tablas.py`: en presupuestos la columna es `estado`, no `estado_presupuesto`; en ordenes es `estado`, no `estado_orden`.
   - Usar la versión que compruebe presupuestos/órdenes activos con los nombres reales de la BD.

2. **Tabla `equipos_abandonados`**  
   En `marcar_como_abandonado` se usan columnas que **no existen** en `crear_tablas.py`:
   - `estado_al_abandonar` → en BD es **`estado_equipo`**.
   - `id_usuario_registra` → en BD es **`registrado_por`**.
   - En la misma tabla, la BD tiene `id_orden` (puede ser NULL). Ajustar el INSERT para usar los nombres correctos y, si aplica, pasar `id_orden`.

3. **Config sin atributos**  
   Se usan `config.dias_alerta_equipo_estancado` y `config.dias_alerta_equipo_abandonado`. En `sistema_base/configuracion.py` solo existe `dias_alerta_equipo` (valor numérico). Opciones:
   - Añadir en `Configuracion` (y en `configuracion_sistema` si se persiste) `dias_alerta_equipo_estancado` y `dias_alerta_equipo_abandonado`, o
   - Usar un único `dias_alerta_equipo` para “estancado” y definir por código un valor por defecto para “abandonado” (p. ej. 90) hasta que exista en configuración.

4. **Estadísticas**  
   En `obtener_estadisticas_equipos()` se usa `config.dias_alerta_equipo_estancado`; si no se añade el atributo, usará un valor por defecto (p. ej. 2) para no romper.

5. **Presupuestos/órdenes del equipo**  
   - `obtener_presupuestos_equipo`: en BD la columna es `estado`, no `estado_presupuesto`. Ajustar SELECT/WHERE.
   - `obtener_ordenes_equipo`: en BD el técnico es `id_tecnico`, no `id_tecnico_asignado`; el estado es `estado`, no `estado_orden`. Corregir nombres en la consulta.

6. **Alertas automáticas**  
   En `verificar_alertas_automaticas()` no usar `id_usuario = 1` fijo; usar el usuario actual de `config` o un “usuario sistema” definido en configuración.

**Mejoras recomendadas:**

- Unificar entrada de equipos: tienes `ingresar_equipo()` y `crear_equipo(datos_equipo)`; la ventana debería usar una sola vía para no duplicar reglas.
- Conectar remito: cuando `ModuloRemitos.generar_remito()` esté estable y la tabla `remitos` esté alineada, descomentar y usar la generación de remito al ingresar equipo.
- Documentar en el docstring los estados de equipo que disparan “abandonado” automático (p. ej. “Listo”/“Sin reparación” + X días).

---

## 3. Módulos con incoherencias BD / imports / API

Estos módulos tienen lógica escrita pero **no son ejecutables tal cual** por desalineación con la BD, imports erróneos o métodos inexistentes.

### 3.1 Órdenes de trabajo (ordenes_LOGICA.py)

**Problemas:**

1. **Imports:** Se usa `from modulos.equipos import ModuloEquipos` y `from modulos.facturacion import ModuloFacturacion`. No existen:
   - `modulos/equipos.py` → el módulo es **`equipos_LOGICA`**.
   - `modulos/facturacion.py` → es **`facturacion_LOGICA`**.
   Corregir a:
   - `from modulos.equipos_LOGICA import ModuloEquipos`
   - `from modulos.facturacion_LOGICA import ModuloFacturacion`

2. **Nombres de columnas (crear_tablas.py):**
   - BD: `id_tecnico`, `estado`, `cobro_diagnostico`, `observaciones_tecnicas`, `cambios_realizados`.
   - Código usa: `id_tecnico_asignado`, `estado_orden`, `cobra_diagnostico`, `observaciones_finales`.
   Alinear todas las consultas (SELECT/UPDATE/INSERT) con los nombres reales de la BD.

3. **Orden manual sin presupuesto:** La tabla `ordenes_trabajo` tiene `id_presupuesto INTEGER NOT NULL`. No se puede crear una orden “manual” sin presupuesto sin:
   - Hacer `id_presupuesto` nullable y permitir NULL para órdenes manuales, o
   - Crear un presupuesto “interno” o registro dummy y asociarlo. La opción recomendable es hacer `id_presupuesto` nullable.

4. **Repuestos usados:** La tabla es `repuestos_usados` con columnas `id_orden`, `id_repuesto`, `cantidad`, `fecha_uso`, `id_usuario`. El código usa `cantidad_usada`, `id_usuario_uso`. Corregir a los nombres de la BD.

5. **Módulo repuestos:** Se importa `from modulos.repuestos import ModuloRepuestos`. El archivo es **`repuestos_LOGICA`**. Corregir import y, dentro de ese módulo, alinear nombres de columnas con la tabla `repuestos` (p. ej. en repuestos la BD tiene `tipo`, no `tipo_repuesto`; no hay `id_usuario_ingreso`).

6. **Facturacion:** `ModuloFacturacion.generar_factura_desde_orden` y `generar_factura_diagnostico` deben existir y trabajar sobre la tabla **`facturacion`** (no una tabla `facturas`), con las columnas definidas en `crear_tablas.py`.

---

### 3.2 Presupuestos (presupuestos_LOGICA.py)

**Problemas:**

1. **BD presupuestos:** Columnas reales: `estado`, `id_usuario`, `fecha_respuesta`, `motivo_rechazo`. No hay `estado_presupuesto`, `id_usuario_crea`, `fecha_aceptacion`, `fecha_rechazo`. Sustituir en todo el módulo:
   - `estado_presupuesto` → `estado`
   - `id_usuario_crea` → `id_usuario`
   - Donde se guarde “aceptado” usar `fecha_respuesta`; no existe `fecha_aceptacion`/`fecha_rechazo` (se puede usar una sola `fecha_respuesta` para ambos casos).

2. **Config:** Se usan `config.porcentaje_recargo_transferencia`, `config.dias_vencimiento_presupuesto`, `config.directorio_base`, `config.direccion_negocio`, `config.telefono_negocio`, `config.email_negocio`, `config.texto_presupuesto`. Esos atributos **no existen** en `sistema_base/configuracion.py`. Hay que:
   - Añadirlos en la clase Configuracion (y cargarlos desde `configuracion_sistema` si se guardan ahí), o
   - Usar los que ya existen: `nombre_negocio`, `telefono_contacto`, `direccion`, `email` (renombrando en el código o mapeando en un solo lugar).

3. **Generar PDF:** La ruta usa `config.directorio_base`; en config existe `ruta_base` y `ruta_datos`. Usar `config.ruta_datos` o una subcarpeta bajo `ruta_datos` (p. ej. `exportaciones` o `presupuestos`).

4. **Aprobar presupuesto:** Se llama a `ModuloOrdenes.crear_orden(datos_orden, id_usuario)`. En `ordenes_LOGICA.py` no existe `crear_orden`; existen `crear_orden_desde_presupuesto` y `crear_orden_manual`. Reemplazar la llamada por `crear_orden_desde_presupuesto(id_presupuesto, id_usuario)` y eliminar la construcción de `datos_orden` para ese flujo.

---

### 3.3 Facturación (facturacion_LOGICA.py)

**Problemas:**

1. **Tabla:** La BD tiene tabla **`facturacion`**, no `facturas`. Columnas: `id_factura`, `id_orden`, `id_cliente`, `monto_total`, `monto_pagado`, `monto_adeudado`, `estado_cobro`, `fecha_emision`, etc. No hay `numero_factura`, `total`, `id_usuario_genera`. Todo el módulo debe:
   - Usar la tabla `facturacion`.
   - Usar columnas `monto_total`, `monto_pagado`, `monto_adeudado`, `estado_cobro`, `fecha_emision`.
   - Si se desea número de factura, añadirlo como columna en la BD o generarlo como derivado (ej. `F-{id_factura}`) hasta definir el esquema final.

2. **Imports:** Cambiar `from modulos.ordenes import ModuloOrdenes` y `from modulos.equipos import ModuloEquipos` a `ordenes_LOGICA` y `equipos_LOGICA`.

---

### 3.4 Pagos (pagos_LOGICA.py)

**Problemas:**

1. **Modelo de datos:** La tabla `pagos` en la BD está ligada a **orden** y **cliente** (`id_orden`, `id_cliente`, `monto`, `metodo_pago`, `es_anticipo`, `fecha_pago`, `observaciones`, `id_usuario`). No hay `id_factura`. El módulo asume pagos por factura. Hay que:
   - O bien definir una tabla/interfaz de “factura” y asociar pagos a facturación (y entonces ampliar el modelo de BD), o
   - Adaptar el módulo a pagar por **orden**: registrar pagos en `pagos` con `id_orden`/`id_cliente` y actualizar `facturacion.monto_pagado`/`monto_adeudado` por orden. La tabla `facturacion` ya tiene `monto_pagado` y `monto_adeudado` por registro (por orden).

2. **Imports:** `from modulos.facturacion import ModuloFacturacion` → `facturacion_LOGICA`.

---

### 3.5 Garantías (garantias_LOGICA.py)

**Problemas:**

1. **BD garantias:** Columnas: `id_orden`, `id_equipo`, `descripcion_reparacion`, `fecha_inicio`, `dias_garantia`, `fecha_vencimiento`, `que_cubre`, `que_no_cubre`, `estado`, `notas`. No hay `estado_garantia` ni `id_usuario_crea`. Usar `estado` y, si se quiere auditoría, registrar en `logs_sistema` en lugar de un campo en garantías.

2. **Imports:** `from modulos.ordenes import ModuloOrdenes` y `from modulos.equipos import ModuloEquipos` → `ordenes_LOGICA` y `equipos_LOGICA`.

---

### 3.6 Repuestos (repuestos_LOGICA.py)

**Problemas:**

1. **BD repuestos:** Columnas: `nombre`, `tipo`, `tipo_dispositivo`, `modelos_compatibles`, `origen`, `id_equipo_origen`, `cantidad_disponible`, `estado`, `precio_referencia`, `fecha_ingreso`, `notas`. No hay `tipo_repuesto` ni `id_usuario_ingreso`. Usar `tipo` en lugar de `tipo_repuesto` y quitar `id_usuario_ingreso` del INSERT o añadirlo a la BD si se desea trazabilidad.

2. **Repuestos usados:** En ordenes se descontará stock; el método `descontar_stock` debe existir en repuestos_LOGICA y actualizar `cantidad_disponible` en la tabla `repuestos`.

---

### 3.7 Remitos (remitos_LOGICA.py)

**Problemas:**

1. **BD remitos:** Columnas: `numero_remito`, `id_equipo`, `id_cliente`, `id_usuario`, `fecha_emision`, `observaciones`, `firma_cliente`, `firma_tecnico`, `impreso`. No hay `fecha_hora_generacion` ni `id_usuario_genera`. Usar `fecha_emision` e `id_usuario` en INSERT/SELECT.

---

### 3.8 Auditoría (auditoria_LOGICA.py)

**Problemas:**

1. **Tabla:** Las consultas usan la tabla **`auditoria`**. En la BD la tabla se llama **`logs_sistema`**. Cambiar todas las referencias de `auditoria` a `logs_sistema`.
2. **Columnas:** En `logs_sistema` están `motivo_modificacion` y `es_accion_critica`. Ajustar SELECT/alias para usar esos nombres (p. ej. en el SELECT usar `motivo_modificacion AS motivo` si la UI espera “motivo”, y `es_accion_critica` para filtros de críticas).

---

### 3.9 Backups (backups_LOGICA.py)

**Problemas:**

1. **Config:** Se usa `config.directorio_base` y rutas tipo `config.directorio_base / "datos"`. En config existen `ruta_base`, `ruta_datos`, `ruta_backups`. Usar `config.ruta_datos` para la BD y `config.ruta_backups` para destino del backup.

2. **Tabla backups:** Columnas en BD: `fecha_backup`, `tipo`, `ubicacion`, `tamanio_archivo`, `exitoso`, `mensaje_error`, `id_usuario`. No hay `nombre_archivo`, `ruta_completa`, `tamanio_bytes`, `observaciones`, `fecha_hora_backup`, `id_usuario_genera`. Mapear:
   - `ubicacion` puede ser la ruta completa (o path relativo).
   - `tamanio_archivo` = tamaño en bytes.
   - `fecha_backup` = fecha/hora del backup.
   - `id_usuario` = quien generó.
   Eliminar o mapear columnas que no existan.

---

### 3.10 Configuración (configuracion_LOGICA.py)

**Problemas:**

1. **Config:** Lee muchos atributos que no existen en `sistema_base.configuracion`: `direccion_negocio`, `telefono_negocio`, `email_negocio`, `cuit_negocio`, `color_acento`, `ruta_logo_*`, `dias_alerta_equipo_estancado`, `dias_alerta_equipo_abandonado`, `dias_vencimiento_presupuesto`, `porcentaje_recargo_transferencia`, `porcentaje_minimo_anticipo`, `cantidad_minima_stock_repuestos`, `texto_pie_*`, `texto_garantia`, `backup_automatico_habilitado`, `backup_dias_intervalo`, `backup_dias_retencion`. La tabla `configuracion_sistema` tiene columnas fijas (nombre_negocio, telefono_contacto, direccion, email, etc.), no un esquema clave-valor. Hay que:
   - Extender la tabla y la clase Configuracion con los campos que la aplicación realmente use, o
   - Reducir la lógica de configuración a lo que ya existe (nombre_negocio, telefono_contacto, direccion, email, color_primario, color_secundario, dias_alerta_equipo, backup_automatico, etc.) y no leer atributos inexistentes.

2. **UPDATE:** No se puede hacer `UPDATE configuracion_sistema SET valor = ?` si no existe columna `valor`. Las actualizaciones deben ser por columna concreta (nombre_negocio, telefono_contacto, etc.).

---

### 3.11 Reportes (reportes_LOGICA.py)

**Problemas:**

1. **Capa de datos:** Usa `from sistema_base.base_datos import BaseDatos` y `db.ejecutar_query()`. No existe `sistema_base.base_datos` ni clase `BaseDatos`. Debe usar `from base_datos.conexion import db` y los métodos `db.obtener_uno()`, `db.obtener_todos()` (y no `ejecutar_query` que devuelve listas de tuplas).

2. **Nombres de columnas:** Usa `estado_orden`, `estado_pago`, tabla `facturas`. En la BD: órdenes con `estado`, facturación en tabla `facturacion` con `estado_cobro`. Corregir consultas y nombres.

3. **Ventana reportes:** Si la ventana usa `ModuloReportes`, no cargará datos hasta que el módulo use `db` correctamente y las tablas/columnas reales.

---

## 4. Módulos que faltan o están a medias

- **Usuarios:** Existe `modulos/usuarios.py` y ventana; depende de `sistema_base.seguridad` (crear_usuario, etc.). Revisar que roles y permisos se comprueben en la UI (ocultar acciones de admin a técnicos).
- **Ventana principal:** Todos los ítems del menú (Clientes, Equipos, Remitos, Presupuestos, Órdenes, Repuestos, Pagos, Facturación, Garantías, Reportes, Usuarios, Configuración, Auditoría, Backups) tienen ventana; varias de ellas fallarán al usar la lógica si no se corrigen los puntos anteriores.
- **Impresión/PDF:** Presupuestos tiene generación PDF pero depende de config y de nombres de columnas; remitos y comprobantes no se revisaron en detalle. Conviene un módulo o paquete común para rutas de exportación y opciones de impresión.

---

## 5. Base de datos – resumen de alineación

| Tabla | Nombre en código (incorrecto) | Nombre/columnas reales en BD |
|-------|-------------------------------|------------------------------|
| Presupuestos | estado_presupuesto, id_usuario_crea, fecha_aceptacion, fecha_rechazo | estado, id_usuario, fecha_respuesta, motivo_rechazo |
| Ordenes | id_tecnico_asignado, estado_orden, cobra_diagnostico, observaciones_finales | id_tecnico, estado, cobro_diagnostico, observaciones_tecnicas, cambios_realizados |
| Facturación | facturas, numero_factura, total, id_usuario_genera | facturacion, monto_total, monto_pagado, monto_adeudado, estado_cobro, fecha_emision |
| Pagos | id_factura | id_orden, id_cliente (pagos por orden) |
| Repuestos | tipo_repuesto, id_usuario_ingreso | tipo, (sin id_usuario_ingreso) |
| repuestos_usados | cantidad_usada, id_usuario_uso | cantidad, id_usuario |
| Garantías | estado_garantia, id_usuario_crea | estado (sin id_usuario_crea) |
| Remitos | fecha_hora_generacion, id_usuario_genera | fecha_emision, id_usuario |
| Auditoría | tabla "auditoria", motivo, es_critica | logs_sistema, motivo_modificacion, es_accion_critica |
| Backups | nombre_archivo, ruta_completa, tamanio_bytes, observaciones, fecha_hora_backup, id_usuario_genera | fecha_backup, tipo, ubicacion, tamanio_archivo, exitoso, mensaje_error, id_usuario |
| equipos_abandonados | estado_al_abandonar, id_usuario_registra | estado_equipo, registrado_por |

---

## 6. Imports incorrectos – lista de reemplazos

Reemplazar en todo el proyecto:

- `from modulos.equipos import ModuloEquipos` → `from modulos.equipos_LOGICA import ModuloEquipos`
- `from modulos.ordenes import ModuloOrdenes` → `from modulos.ordenes_LOGICA import ModuloOrdenes`
- `from modulos.facturacion import ModuloFacturacion` → `from modulos.facturacion_LOGICA import ModuloFacturacion`
- `from modulos.pagos import ModuloPagos` → `from modulos.pagos_LOGICA import ModuloPagos`
- `from modulos.repuestos import ModuloRepuestos` → `from modulos.repuestos_LOGICA import ModuloRepuestos`

Archivos afectados (entre otros):  
ordenes_LOGICA.py, facturacion_LOGICA.py, pagos_LOGICA.py, garantias_LOGICA.py, presupuestos_LOGICA.py.

---

## 7. Configuración (sistema_base.configuracion)

Atributos que usan los módulos pero **no están definidos** en `Configuracion`:

- directorio_base (usar ruta_base o ruta_datos según contexto)
- direccion_negocio, telefono_negocio, email_negocio (existen como direccion, telefono_contacto, email)
- dias_alerta_equipo_estancado, dias_alerta_equipo_abandonado
- dias_vencimiento_presupuesto, porcentaje_recargo_transferencia
- texto_presupuesto, texto_pie_remito, texto_pie_factura, texto_garantia
- dias_garantia_reparacion
- cuit_negocio, color_acento, ruta_logo_sistema, ruta_logo_remitos, ruta_logo_comprobantes
- backup_automatico_habilitado, backup_dias_intervalo, backup_dias_retencion
- cantidad_minima_stock_repuestos, porcentaje_minimo_anticipo

Acción: añadir en `Configuracion` (y en `configuracion_sistema` si aplica) solo los que se vayan a usar y cargar desde BD en `cargar_configuracion_bd`.

---

## 8. Plan de acción sugerido (prioridad)

1. **Crítico – Imports:** Sustituir todos los imports de `modulos.XXX` por `modulos.XXX_LOGICA` donde corresponda.
2. **Crítico – Equipos:** Eliminar método duplicado `eliminar_equipo`, corregir INSERT en `equipos_abandonados` y nombres en presupuestos/órdenes del equipo; ajustar config para días de alerta.
3. **Crítico – BD/consultas:** Unificar nombres de columnas y tablas en: presupuestos, ordenes, facturacion, pagos, repuestos, repuestos_usados, garantias, remitos, backups, auditoría (logs_sistema).
4. **Alto – Orden sin presupuesto:** Hacer `id_presupuesto` nullable en `ordenes_trabajo` y adaptar `crear_orden_manual`.
5. **Alto – Config:** Definir en Configuracion (y BD) los parámetros que usan presupuestos, equipos y backups; usar rutas existentes (ruta_datos, ruta_backups) donde aplique.
6. **Alto – Presupuestos:** Reemplazar llamada a `ModuloOrdenes.crear_orden` por `crear_orden_desde_presupuesto` y alinear estados/columnas con la BD.
7. **Medio – Reportes:** Cambiar a `base_datos.conexion.db` y consultas con nombres reales de tablas/columnas.
8. **Medio – Facturación/Pagos:** Decidir modelo (pago por orden vs por “factura”) y alinear facturacion + pagos con la misma decisión.
9. **Bajo – Documentación:** Actualizar LEEME_PRIMERO y README con el estado real de módulos y requisitos de configuración.
10. **Bajo – Limpieza:** Eliminar o archivar `interfaz/ventanas/backup_viejo` cuando no se use; evitar referencias a `modulos.auditoria`, `modulos.backups`, etc. sin _LOGICA.

---

## 9. Conclusión

El proyecto tiene una buena base (clientes terminado, equipos avanzado, ventanas y menú coherentes), pero **la capa de lógica y la BD están desincronizadas** en nombres de tablas/columnas, en el uso de `config` y en imports. Eso hace que varios flujos (presupuestos → órdenes → facturación → pagos, reportes, auditoría, backups) fallen en tiempo de ejecución.

Recomendación: **congelar nuevas features** hasta completar la alineación BD + módulos + config y la corrección de imports; luego ejecutar flujos completos (cliente → equipo → remito → presupuesto → orden → pago/facturación) y corregir fallos residuales. Después de eso, el resto de mejoras (clientes, equipos, reportes, documentación) se pueden abordar con más seguridad.

---

*Documento generado en el marco de la auditoría técnica del proyecto TechManager v1.0.*
