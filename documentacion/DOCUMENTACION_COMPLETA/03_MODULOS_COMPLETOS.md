# MÓDULOS COMPLETOS - TECHMANAGER

## TABLA DE CONTENIDOS
1. [Estructura Estándar de Módulos](#estructura-estándar-de-módulos)
2. [ModuloClientes - REFERENCIA COMPLETA](#moduloclientes---referencia-completa)
3. [ModuloEquipos](#moduloequipos)
4. [ModuloOrdenes](#moduloordenes)
5. [ModuloPresupuestos](#modulopresupuestos)
6. [ModuloRepuestos](#modulorepuestos)
7. [ModuloFacturacionPagos](#modulofacturacionpagos)
8. [ModuloRemitos](#moduloremitos)
9. [ModuloGarantias](#modulogarantias)
10. [ModuloUsuarios](#modulousuarios)
11. [ModuloAuditoria](#moduloauditoria)
12. [ModuloBackups](#modulobackups)
13. [ModuloReportes](#moduloreportes)

---

## ESTRUCTURA ESTÁNDAR DE MÓDULOS

Todos los módulos en TechManager siguen esta estructura:

```python
class ModuloXXX:
    """
    Módulo para gestionar XXX
    
    Todos los métodos son estáticos para facilitar su uso
    sin necesidad de instanciar la clase.
    """
    
    @staticmethod
    def listar_xxx(filtros=None, busqueda="", orden=""):
        """
        Lista todos los registros con filtros opcionales
        
        Args:
            filtros (dict): Filtros a aplicar
            busqueda (str): Texto para buscar
            orden (str): Campo por el que ordenar
            
        Returns:
            List[dict]: Lista de registros
        """
        try:
            # 1. Construir consulta SQL
            consulta = "SELECT * FROM tabla WHERE activo = 1"
            parametros = []
            
            # 2. Aplicar filtros
            if busqueda:
                consulta += " AND campo LIKE ?"
                parametros.append(f"%{busqueda}%")
            
            # 3. Ordenamiento
            consulta += f" ORDER BY {orden}"
            
            # 4. Ejecutar y retornar
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_xxx_por_id(id_xxx):
        """
        Obtiene un registro por su ID
        
        Args:
            id_xxx (int): ID del registro
            
        Returns:
            dict: Registro encontrado o None
        """
        try:
            consulta = "SELECT * FROM tabla WHERE id_xxx = ?"
            return db.obtener_uno(consulta, (id_xxx,))
        except Exception as e:
            config.guardar_log(f"Error al obtener: {e}", "ERROR")
            return None
    
    @staticmethod
    def crear_xxx(datos, id_usuario):
        """
        Crea un nuevo registro
        
        Args:
            datos (dict): Datos del registro
            id_usuario (int): Usuario que crea
            
        Returns:
            tuple: (exito: bool, mensaje: str, id_nuevo: int)
        """
        try:
            # 1. Validar datos obligatorios
            if not datos.get('campo_obligatorio'):
                return False, "Campo obligatorio faltante", None
            
            # 2. Validaciones complejas
            from sistema_base.validadores import validar_xxx
            es_valido, mensaje = validar_xxx(datos['campo'])
            if not es_valido:
                return False, mensaje, None
            
            # 3. Verificar unicidad si aplica
            existe = db.obtener_uno(
                "SELECT id_xxx FROM tabla WHERE campo_unico = ?",
                (datos['campo_unico'],)
            )
            if existe:
                return False, "Ya existe un registro con ese valor", None
            
            # 4. Insertar en BD
            consulta = """
            INSERT INTO tabla (campo1, campo2, campo3)
            VALUES (?, ?, ?)
            """
            
            cursor = db.ejecutar_consulta(
                consulta,
                (datos['campo1'], datos['campo2'], datos['campo3'])
            )
            
            id_nuevo = cursor.lastrowid
            
            # 5. Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="XXX",
                id_registro=id_nuevo
            )
            
            # 6. Log
            config.guardar_log(f"XXX creado: ID {id_nuevo}", "INFO")
            
            # 7. Retornar éxito
            return True, "XXX creado exitosamente", id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al crear: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def modificar_xxx(id_xxx, datos, id_usuario):
        """
        Modifica un registro existente
        
        Args:
            id_xxx (int): ID del registro
            datos (dict): Nuevos datos
            id_usuario (int): Usuario que modifica
            
        Returns:
            tuple: (exito: bool, mensaje: str)
        """
        try:
            # 1. Verificar que existe
            registro_actual = ModuloXXX.obtener_xxx_por_id(id_xxx)
            if not registro_actual:
                return False, "Registro no encontrado"
            
            # 2. Validar datos
            # ... validaciones ...
            
            # 3. Actualizar en BD
            consulta = """
            UPDATE tabla
            SET campo1 = ?, campo2 = ?, campo3 = ?
            WHERE id_xxx = ?
            """
            
            db.ejecutar_consulta(
                consulta,
                (datos['campo1'], datos['campo2'], datos['campo3'], id_xxx)
            )
            
            # 4. Registrar cambios en auditoría
            for campo, valor_nuevo in datos.items():
                valor_anterior = registro_actual.get(campo)
                if valor_anterior != valor_nuevo:
                    registrar_accion_auditoria(
                        id_usuario=id_usuario,
                        accion="Modificar",
                        modulo="XXX",
                        id_registro=id_xxx,
                        campo_modificado=campo,
                        valor_anterior=str(valor_anterior),
                        valor_nuevo=str(valor_nuevo)
                    )
            
            # 5. Log
            config.guardar_log(f"XXX modificado: ID {id_xxx}", "INFO")
            
            return True, "XXX modificado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al modificar: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def eliminar_xxx(id_xxx, id_usuario):
        """
        Elimina (soft delete) un registro
        
        Args:
            id_xxx (int): ID del registro
            id_usuario (int): Usuario que elimina
            
        Returns:
            tuple: (exito: bool, mensaje: str)
        """
        try:
            # 1. Verificar que existe
            registro = ModuloXXX.obtener_xxx_por_id(id_xxx)
            if not registro:
                return False, "Registro no encontrado"
            
            # 2. Verificar dependencias (si aplica)
            tiene_dependencias = db.obtener_uno(
                "SELECT COUNT(*) as total FROM tabla_relacionada WHERE id_xxx = ?",
                (id_xxx,)
            )
            
            if tiene_dependencias and tiene_dependencias['total'] > 0:
                return False, f"No se puede eliminar: tiene {tiene_dependencias['total']} registros relacionados"
            
            # 3. Soft delete
            db.ejecutar_consulta(
                "UPDATE tabla SET activo = 0 WHERE id_xxx = ?",
                (id_xxx,)
            )
            
            # 4. Auditoría (acción crítica)
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Eliminar",
                modulo="XXX",
                id_registro=id_xxx,
                es_critica=True
            )
            
            # 5. Log
            config.guardar_log(f"XXX eliminado: ID {id_xxx}", "INFO")
            
            return True, "XXX eliminado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al eliminar: {e}", "ERROR")
            return False, f"Error: {str(e)}"
```

---

## MODULOCLIENTES - REFERENCIA COMPLETA

### Ubicación
`modulos/clientes.py`

### Descripción
Gestiona toda la lógica de negocio relacionada con clientes del taller.

### Código Completo

```python
from base_datos.conexion import db
from sistema_base.configuracion import config
from sistema_base.seguridad import registrar_accion_auditoria

class ModuloClientes:
    """Módulo para gestionar clientes"""
    
    @staticmethod
    def listar_clientes(solo_activos=True, busqueda="", orden="apellido"):
        """
        Lista todos los clientes
        
        Args:
            solo_activos (bool): Si True, solo clientes activos
            busqueda (str): Texto para buscar en nombre, apellido, teléfono
            orden (str): Campo por el que ordenar (apellido, fecha_registro)
            
        Returns:
            List[dict]: Lista de clientes
        """
        try:
            consulta = """
            SELECT 
                id_cliente,
                nombre,
                apellido,
                telefono,
                direccion,
                email,
                observaciones,
                estado_cliente,
                es_incobrable,
                tiene_incobrables,
                total_incobrables,
                confiabilidad_pago,
                fecha_registro
            FROM clientes
            WHERE activo = 1
            """
            
            parametros = []
            
            # Filtro por búsqueda
            if busqueda:
                consulta += """ AND (
                    nombre LIKE ? OR 
                    apellido LIKE ? OR
                    telefono LIKE ? OR 
                    direccion LIKE ? OR
                    email LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 5)
            
            # Ordenamiento
            if orden == "fecha_registro":
                consulta += " ORDER BY fecha_registro DESC"
            elif orden == "deuda":
                consulta += " ORDER BY total_incobrables DESC"
            else:
                consulta += " ORDER BY apellido ASC, nombre ASC"
            
            return db.obtener_todos(consulta, tuple(parametros))
            
        except Exception as e:
            config.guardar_log(f"Error al listar clientes: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_cliente_por_id(id_cliente):
        """Obtiene un cliente por su ID"""
        try:
            consulta = """
            SELECT * FROM clientes WHERE id_cliente = ?
            """
            return db.obtener_uno(consulta, (id_cliente,))
        except Exception as e:
            config.guardar_log(f"Error al obtener cliente: {e}", "ERROR")
            return None
    
    @staticmethod
    def crear_cliente(nombre, apellido, telefono, direccion, email, id_usuario):
        """
        Crea un nuevo cliente
        
        Returns:
            tuple: (exito: bool, mensaje: str, id_nuevo: int)
        """
        try:
            # Validar datos obligatorios
            if not nombre or not nombre.strip():
                return False, "El nombre es obligatorio", None
            
            if not apellido or not apellido.strip():
                return False, "El apellido es obligatorio", None
            
            if not telefono or not telefono.strip():
                return False, "El teléfono es obligatorio", None
            
            # Validar teléfono
            from sistema_base.validadores import validar_telefono
            es_valido, mensaje = validar_telefono(telefono)
            if not es_valido:
                return False, mensaje, None
            
            # Validar email si se proporcionó
            if email and email.strip():
                from sistema_base.validadores import validar_email
                es_valido, mensaje = validar_email(email)
                if not es_valido:
                    return False, mensaje, None
            
            # Verificar teléfono único
            existe = db.obtener_uno(
                "SELECT id_cliente FROM clientes WHERE telefono = ? AND activo = 1",
                (telefono,)
            )
            if existe:
                return False, "Ya existe un cliente con ese teléfono", None
            
            # Insertar cliente
            consulta = """
            INSERT INTO clientes (nombre, apellido, telefono, direccion, email)
            VALUES (?, ?, ?, ?, ?)
            """
            
            cursor = db.ejecutar_consulta(
                consulta,
                (nombre.strip(), apellido.strip(), telefono.strip(), 
                 direccion.strip() if direccion else None,
                 email.strip() if email else None)
            )
            
            id_nuevo = cursor.lastrowid
            
            # Auditoría
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Clientes",
                id_registro=id_nuevo
            )
            
            # Log
            config.guardar_log(f"Cliente creado: {apellido}, {nombre} (ID: {id_nuevo})", "INFO")
            
            return True, "Cliente creado exitosamente", id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al crear cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def modificar_cliente(id_cliente, nombre, telefono, direccion, email, id_usuario):
        """Modifica un cliente existente"""
        try:
            # Obtener datos actuales
            cliente_actual = ModuloClientes.obtener_cliente_por_id(id_cliente)
            if not cliente_actual:
                return False, "Cliente no encontrado"
            
            # Validaciones
            if not nombre or not nombre.strip():
                return False, "El nombre es obligatorio"
            
            if not telefono or not telefono.strip():
                return False, "El teléfono es obligatorio"
            
            # Validar teléfono
            from sistema_base.validadores import validar_telefono
            es_valido, mensaje = validar_telefono(telefono)
            if not es_valido:
                return False, mensaje
            
            # Verificar teléfono único (excepto el actual)
            existe = db.obtener_uno(
                "SELECT id_cliente FROM clientes WHERE telefono = ? AND id_cliente != ? AND activo = 1",
                (telefono, id_cliente)
            )
            if existe:
                return False, "Ya existe otro cliente con ese teléfono"
            
            # Actualizar
            consulta = """
            UPDATE clientes
            SET nombre = ?, telefono = ?, direccion = ?, email = ?
            WHERE id_cliente = ?
            """
            
            db.ejecutar_consulta(
                consulta,
                (nombre.strip(), telefono.strip(),
                 direccion.strip() if direccion else None,
                 email.strip() if email else None,
                 id_cliente)
            )
            
            # Auditoría de cambios
            cambios = {
                'nombre': nombre.strip(),
                'telefono': telefono.strip(),
                'direccion': direccion.strip() if direccion else None,
                'email': email.strip() if email else None
            }
            
            for campo, valor_nuevo in cambios.items():
                valor_anterior = cliente_actual.get(campo)
                if str(valor_anterior) != str(valor_nuevo):
                    registrar_accion_auditoria(
                        id_usuario=id_usuario,
                        accion="Modificar",
                        modulo="Clientes",
                        id_registro=id_cliente,
                        campo_modificado=campo,
                        valor_anterior=str(valor_anterior),
                        valor_nuevo=str(valor_nuevo)
                    )
            
            config.guardar_log(f"Cliente modificado: ID {id_cliente}", "INFO")
            return True, "Cliente modificado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al modificar cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def eliminar_cliente(id_cliente, id_usuario):
        """Elimina (desactiva) un cliente"""
        try:
            # Verificar que existe
            cliente = ModuloClientes.obtener_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente no encontrado"
            
            # Verificar que no tenga equipos activos
            consulta_equipos = """
            SELECT COUNT(*) as total
            FROM equipos
            WHERE id_cliente = ? AND activo = 1
            """
            
            resultado = db.obtener_uno(consulta_equipos, (id_cliente,))
            
            if resultado and resultado['total'] > 0:
                return False, f"No se puede eliminar: el cliente tiene {resultado['total']} equipo(s) activo(s)"
            
            # Soft delete
            db.ejecutar_consulta(
                "UPDATE clientes SET activo = 0 WHERE id_cliente = ?",
                (id_cliente,)
            )
            
            # Auditoría (acción crítica)
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Eliminar",
                modulo="Clientes",
                id_registro=id_cliente,
                motivo="Cliente desactivado",
                es_critica=True
            )
            
            config.guardar_log(f"Cliente eliminado: ID {id_cliente}", "INFO")
            return True, "Cliente eliminado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al eliminar cliente: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def cambiar_estado_cliente(id_cliente, nuevo_estado, id_usuario, motivo=""):
        """
        Cambia el estado de un cliente
        
        Estados válidos: 'Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable'
        """
        try:
            # Validar estado
            estados_validos = ['Nuevo', 'Buen Pagador', 'Deudor', 'Moroso', 'Incobrable']
            if nuevo_estado not in estados_validos:
                return False, f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
            
            # Obtener estado actual
            cliente = ModuloClientes.obtener_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente no encontrado"
            
            estado_anterior = cliente.get('estado_cliente')
            
            # Actualizar estado
            consulta = "UPDATE clientes SET estado_cliente = ? WHERE id_cliente = ?"
            
            # Si es Incobrable, marcar también es_incobrable
            if nuevo_estado == 'Incobrable':
                consulta = """
                UPDATE clientes 
                SET estado_cliente = ?, es_incobrable = 1 
                WHERE id_cliente = ?
                """
            
            db.ejecutar_consulta(consulta, (nuevo_estado, id_cliente))
            
            # Auditoría (cambio crítico)
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Clientes",
                id_registro=id_cliente,
                campo_modificado="estado_cliente",
                valor_anterior=estado_anterior,
                valor_nuevo=nuevo_estado,
                motivo=motivo,
                es_critica=True
            )
            
            config.guardar_log(
                f"Estado de cliente cambiado: ID {id_cliente} de '{estado_anterior}' a '{nuevo_estado}'", 
                "INFO"
            )
            
            return True, f"Estado cambiado a '{nuevo_estado}' exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al cambiar estado: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_equipos_cliente(id_cliente):
        """Obtiene todos los equipos de un cliente"""
        try:
            consulta = """
            SELECT *
            FROM equipos
            WHERE id_cliente = ? AND activo = 1
            ORDER BY fecha_ingreso DESC
            """
            return db.obtener_todos(consulta, (id_cliente,))
        except Exception as e:
            config.guardar_log(f"Error al obtener equipos: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_estadisticas_clientes():
        """Obtiene estadísticas generales de clientes"""
        try:
            stats = {}
            
            # Total de clientes activos
            total = db.obtener_uno("SELECT COUNT(*) as total FROM clientes WHERE activo = 1")
            stats['total_activos'] = total['total'] if total else 0
            
            # Por estado
            por_estado = db.obtener_todos("""
                SELECT estado_cliente, COUNT(*) as cantidad
                FROM clientes
                WHERE activo = 1
                GROUP BY estado_cliente
            """)
            stats['por_estado'] = {item['estado_cliente']: item['cantidad'] for item in por_estado}
            
            # Total incobrables
            incobrables = db.obtener_uno("""
                SELECT SUM(total_incobrables) as total
                FROM clientes
                WHERE activo = 1
            """)
            stats['total_incobrables'] = incobrables['total'] if incobrables and incobrables['total'] else 0
            
            return stats
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas: {e}", "ERROR")
            return {}
```

---

Continúo con los demás módulos en el siguiente archivo...

