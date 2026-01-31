# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE EQUIPOS
============================================================================
Lógica de negocio para gestión de equipos/dispositivos
============================================================================
"""

from datetime import datetime, timedelta
from base_datos.conexion import db
from sistema_base.validadores import validar_requerido
from sistema_base.configuracion import config


class ModuloEquipos:
    """Clase para manejar la lógica de negocio de equipos"""
    
    # Tipos de dispositivos soportados
    TIPOS_DISPOSITIVOS = [
        "Celular",
        "Tablet",
        "PC/Notebook",
        "Consola",
        "Otro"
    ]
    
    # Estados posibles de un equipo
    ESTADOS_EQUIPOS = [
        "En revisión",
        "En reparación",
        "Esperando repuesto",
        "Listo",
        "Entregado",
        "Sin reparación",
        "Abandonado"
    ]
    
    @staticmethod
    def listar_equipos(filtro_estado="", filtro_tipo="", filtro_cliente="", busqueda="", orden="fecha_desc"):
        """
        Lista todos los equipos
        
        Args:
            filtro_estado (str): Filtrar por estado específico
            filtro_tipo (str): Filtrar por tipo de dispositivo
            filtro_cliente (str): Filtrar por ID de cliente
            busqueda (str): Buscar en marca, modelo, identificador
            orden (str): fecha_desc, fecha_asc, cliente
            
        Returns:
            list: Lista de equipos con datos del cliente
        """
        try:
            consulta = """
            SELECT 
                e.id_equipo,
                e.id_cliente,
                c.nombre as cliente_nombre,
                c.tiene_incobrables,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.identificador,
                e.estado_actual,
                e.fecha_ingreso,
                e.fecha_ultimo_movimiento,
                e.falla_declarada
            FROM equipos e
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            WHERE e.activo = 1
            """
            
            parametros = []
            
            # Filtros
            if filtro_estado:
                consulta += " AND e.estado_actual = ?"
                parametros.append(filtro_estado)
            
            if filtro_tipo:
                consulta += " AND e.tipo_dispositivo = ?"
                parametros.append(filtro_tipo)
            
            if filtro_cliente:
                consulta += " AND e.id_cliente = ?"
                parametros.append(filtro_cliente)
            
            if busqueda:
                consulta += """ AND (
                    e.marca LIKE ? OR 
                    e.modelo LIKE ? OR 
                    e.identificador LIKE ? OR
                    c.nombre LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param, busqueda_param, busqueda_param, busqueda_param])
            
            # Ordenamiento
            if orden == "fecha_asc":
                consulta += " ORDER BY e.fecha_ingreso ASC"
            elif orden == "cliente":
                consulta += " ORDER BY c.nombre ASC, e.fecha_ingreso DESC"
            else:  # fecha_desc (default)
                consulta += " ORDER BY e.fecha_ingreso DESC"
            
            equipos = db.obtener_todos(consulta, tuple(parametros))
            
            # Calcular días sin movimiento para cada equipo
            for equipo in equipos:
                equipo['dias_sin_movimiento'] = ModuloEquipos.calcular_dias_sin_movimiento(
                    equipo['fecha_ultimo_movimiento']
                )
                
                # Marcar si necesita alerta
                equipo['alerta_estancado'] = equipo['dias_sin_movimiento'] >= config.dias_alerta_equipo_estancado
                equipo['alerta_abandonado'] = equipo['dias_sin_movimiento'] >= config.dias_alerta_equipo_abandonado
            
            return equipos
            
        except Exception as e:
            config.guardar_log(f"Error al listar equipos: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_equipo_por_id(id_equipo):
        """
        Obtiene un equipo por su ID con todos sus datos
        
        Args:
            id_equipo (int): ID del equipo
            
        Returns:
            dict: Datos completos del equipo o None
        """
        try:
            consulta = """
            SELECT 
                e.*,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                c.tiene_incobrables
            FROM equipos e
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            WHERE e.id_equipo = ?
            """
            
            equipo = db.obtener_uno(consulta, (id_equipo,))
            
            if equipo:
                equipo['dias_sin_movimiento'] = ModuloEquipos.calcular_dias_sin_movimiento(
                    equipo['fecha_ultimo_movimiento']
                )
            
            return equipo
            
        except Exception as e:
            config.guardar_log(f"Error al obtener equipo: {e}", "ERROR")
            return None
    
    @staticmethod
    def ingresar_equipo(id_cliente, tipo_dispositivo, marca, modelo, identificador,
                        color, estado_fisico, accesorios, falla_declarada, id_usuario):
        """
        Ingresa un nuevo equipo al sistema
        
        Args:
            id_cliente (int): ID del cliente
            tipo_dispositivo (str): Tipo de dispositivo
            marca (str): Marca
            modelo (str): Modelo
            identificador (str): IMEI, serial, etc. (puede ser vacío)
            color (str): Color del dispositivo
            estado_fisico (str): Descripción del estado físico
            accesorios (str): Accesorios que trae
            falla_declarada (str): Falla declarada por el cliente
            id_usuario (int): ID del usuario que ingresa
            
        Returns:
            tuple: (exito, mensaje, id_equipo_nuevo)
        """
        try:
            # Validaciones
            es_valido, mensaje = validar_requerido(marca, "Marca")
            if not es_valido:
                return False, mensaje, None
            
            es_valido, mensaje = validar_requerido(modelo, "Modelo")
            if not es_valido:
                return False, mensaje, None
            
            es_valido, mensaje = validar_requerido(falla_declarada, "Falla declarada")
            if not es_valido:
                return False, mensaje, None
            
            if tipo_dispositivo not in ModuloEquipos.TIPOS_DISPOSITIVOS:
                return False, "Tipo de dispositivo inválido", None
            
            # Si tiene identificador, verificar que no exista
            if identificador and identificador.strip():
                consulta_verificar = """
                SELECT COUNT(*) as total 
                FROM equipos 
                WHERE identificador = ? AND identificador != ''
                """
                resultado = db.obtener_uno(consulta_verificar, (identificador.strip(),))
                
                if resultado and resultado['total'] > 0:
                    return False, f"Ya existe un equipo con el identificador '{identificador}'", None
            
            # Insertar equipo
            fecha_actual = datetime.now()
            
            consulta = """
            INSERT INTO equipos (
                id_cliente, tipo_dispositivo, marca, modelo, identificador,
                color, estado_fisico, accesorios, falla_declarada,
                estado_actual, fecha_ingreso, fecha_ultimo_movimiento, activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'En revisión', ?, ?, 1)
            """
            
            id_nuevo = db.ejecutar_consulta(
                consulta,
                (id_cliente, tipo_dispositivo, marca, modelo, identificador.strip() if identificador else "",
                 color, estado_fisico, accesorios, falla_declarada, fecha_actual, fecha_actual)
            )
            
            # TODO: Generar remito automáticamente cuando el módulo esté listo
            # from modulos.remitos import ModuloRemitos
            # exito_remito, mensaje_remito, numero_remito = ModuloRemitos.generar_remito(
            #     id_equipo=id_nuevo,
            #     id_usuario=id_usuario
            # )
            exito_remito = False
            numero_remito = None
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Equipos",
                id_registro=id_nuevo,
                motivo=f"Ingreso de equipo {tipo_dispositivo} {marca} {modelo}"
            )
            
            mensaje_final = f"Equipo ingresado exitosamente"
            if exito_remito:
                mensaje_final += f"\nRemito N° {numero_remito} generado"
            
            config.guardar_log(f"Equipo ID {id_nuevo} ingresado por usuario ID {id_usuario}", "INFO")
            return True, mensaje_final, id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al ingresar equipo: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def cambiar_estado_equipo(id_equipo, nuevo_estado, id_usuario, observaciones=""):
        """
        Cambia el estado de un equipo
        
        Args:
            id_equipo (int): ID del equipo
            nuevo_estado (str): Nuevo estado
            id_usuario (int): ID del usuario que cambia el estado
            observaciones (str): Observaciones del cambio
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if nuevo_estado not in ModuloEquipos.ESTADOS_EQUIPOS:
                return False, "Estado inválido"
            
            # Obtener equipo actual
            equipo = ModuloEquipos.obtener_equipo_por_id(id_equipo)
            if not equipo:
                return False, "Equipo no encontrado"
            
            estado_anterior = equipo['estado_actual']
            
            # Actualizar estado
            fecha_actual = datetime.now()
            
            consulta = """
            UPDATE equipos
            SET estado_actual = ?,
                fecha_ultimo_movimiento = ?
            WHERE id_equipo = ?
            """
            
            db.ejecutar_consulta(consulta, (nuevo_estado, fecha_actual, id_equipo))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            motivo = f"Cambio de estado: {estado_anterior} → {nuevo_estado}"
            if observaciones:
                motivo += f". {observaciones}"
            
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Equipos",
                id_registro=id_equipo,
                campo_modificado="estado_actual",
                valor_anterior=estado_anterior,
                valor_nuevo=nuevo_estado,
                motivo=motivo
            )
            
            # Agregar nota automática
            ModuloEquipos.agregar_nota_equipo(
                id_equipo,
                f"Estado cambiado a: {nuevo_estado}" + (f" - {observaciones}" if observaciones else ""),
                id_usuario
            )
            
            config.guardar_log(f"Equipo ID {id_equipo} cambió de estado: {estado_anterior} → {nuevo_estado}", "INFO")
            return True, f"Estado cambiado a '{nuevo_estado}'"
            
        except Exception as e:
            config.guardar_log(f"Error al cambiar estado de equipo: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def marcar_como_abandonado(id_equipo, id_usuario, partes_recuperables="", observaciones=""):
        """
        Marca un equipo como abandonado
        
        Args:
            id_equipo (int): ID del equipo
            id_usuario (int): ID del usuario
            partes_recuperables (str): Lista de partes que se pueden recuperar
            observaciones (str): Observaciones adicionales
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Obtener equipo
            equipo = ModuloEquipos.obtener_equipo_por_id(id_equipo)
            if not equipo:
                return False, "Equipo no encontrado"
            
            # Cambiar estado
            exito, mensaje = ModuloEquipos.cambiar_estado_equipo(
                id_equipo,
                "Abandonado",
                id_usuario,
                f"Marcado como abandonado. {observaciones}"
            )
            
            if not exito:
                return False, mensaje
            
            # Registrar en tabla de abandonados
            consulta = """
            INSERT INTO equipos_abandonados (
                id_equipo, fecha_abandono, estado_al_abandonar,
                falla_original, partes_recuperables, condicion_fisica,
                id_usuario_registra, notas
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db.ejecutar_consulta(
                consulta,
                (id_equipo, datetime.now(), equipo['estado_actual'],
                 equipo['falla_declarada'], partes_recuperables,
                 equipo['estado_fisico'], id_usuario, observaciones)
            )
            
            config.guardar_log(f"Equipo ID {id_equipo} marcado como abandonado", "WARNING")
            return True, "Equipo marcado como abandonado"
            
        except Exception as e:
            config.guardar_log(f"Error al marcar equipo como abandonado: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def calcular_dias_sin_movimiento(fecha_ultimo_movimiento):
        """
        Calcula los días transcurridos desde el último movimiento
        
        Args:
            fecha_ultimo_movimiento: Fecha del último movimiento
            
        Returns:
            int: Días sin movimiento
        """
        try:
            if isinstance(fecha_ultimo_movimiento, str):
                fecha = datetime.fromisoformat(fecha_ultimo_movimiento.replace('Z', '+00:00'))
            else:
                fecha = fecha_ultimo_movimiento
            
            diferencia = datetime.now() - fecha
            return diferencia.days
            
        except:
            return 0
    
    @staticmethod
    def obtener_estadisticas_equipos():
        """
        Obtiene estadísticas generales de equipos
        
        Returns:
            dict: Estadísticas de equipos
        """
        try:
            estadisticas = {}
            
            # Total de equipos
            consulta_total = "SELECT COUNT(*) as total FROM equipos"
            resultado = db.obtener_uno(consulta_total)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Por estado
            for estado in ModuloEquipos.ESTADOS_EQUIPOS:
                consulta = "SELECT COUNT(*) as total FROM equipos WHERE estado_actual = ?"
                resultado = db.obtener_uno(consulta, (estado,))
                key = estado.lower().replace(" ", "_").replace("/", "_")
                estadisticas[key] = resultado['total'] if resultado else 0
            
            # Equipos estancados (más de X días sin movimiento)
            dias_alerta = config.dias_alerta_equipo_estancado
            fecha_limite = datetime.now() - timedelta(days=dias_alerta)
            
            consulta_estancados = """
            SELECT COUNT(*) as total 
            FROM equipos 
            WHERE fecha_ultimo_movimiento < ? 
            AND estado_actual NOT IN ('Entregado', 'Abandonado')
            """
            resultado = db.obtener_uno(consulta_estancados, (fecha_limite,))
            estadisticas['estancados'] = resultado['total'] if resultado else 0
            
            # Por tipo de dispositivo
            for tipo in ModuloEquipos.TIPOS_DISPOSITIVOS:
                consulta = "SELECT COUNT(*) as total FROM equipos WHERE tipo_dispositivo = ?"
                resultado = db.obtener_uno(consulta, (tipo,))
                key = f"tipo_{tipo.lower().replace(' ', '_').replace('/', '_')}"
                estadisticas[key] = resultado['total'] if resultado else 0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de equipos: {e}", "ERROR")
            return {'total': 0}
    
    @staticmethod
    def obtener_notas_equipo(id_equipo):
        """
        Obtiene todas las notas de un equipo
        
        Args:
            id_equipo (int): ID del equipo
            
        Returns:
            list: Lista de notas ordenadas por fecha
        """
        try:
            consulta = """
            SELECT 
                n.id_nota,
                n.nota,
                n.fecha_hora,
                n.editado,
                u.nombre as usuario_nombre
            FROM historial_notas n
            LEFT JOIN usuarios u ON n.id_usuario = u.id_usuario
            WHERE n.modulo = 'Equipos' AND n.id_registro = ?
            ORDER BY n.fecha_hora DESC
            """
            
            return db.obtener_todos(consulta, (id_equipo,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener notas del equipo: {e}", "ERROR")
            return []
    
    @staticmethod
    def agregar_nota_equipo(id_equipo, nota, id_usuario):
        """
        Agrega una nota a un equipo
        
        Args:
            id_equipo (int): ID del equipo
            nota (str): Texto de la nota
            id_usuario (int): ID del usuario que agrega la nota
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not nota or nota.strip() == "":
                return False, "La nota no puede estar vacía"
            
            consulta = """
            INSERT INTO historial_notas (modulo, id_registro, nota, id_usuario, fecha_hora, editado)
            VALUES (?, ?, ?, ?, ?, 0)
            """
            
            db.ejecutar_consulta(consulta, ("Equipos", id_equipo, nota.strip(), id_usuario, datetime.now()))
            
            config.guardar_log(f"Nota agregada al equipo ID {id_equipo} por usuario ID {id_usuario}", "INFO")
            return True, "Nota agregada exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al agregar nota: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def obtener_presupuestos_equipo(id_equipo):
        """
        Obtiene todos los presupuestos de un equipo
        
        Args:
            id_equipo (int): ID del equipo
            
        Returns:
            list: Lista de presupuestos
        """
        try:
            consulta = """
            SELECT 
                id_presupuesto,
                descripcion_trabajo,
                monto_sin_recargo,
                recargo_transferencia,
                monto_total,
                estado_presupuesto,
                fecha_creacion,
                fecha_vencimiento
            FROM presupuestos
            WHERE id_equipo = ?
            ORDER BY fecha_creacion DESC
            """
            
            return db.obtener_todos(consulta, (id_equipo,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener presupuestos del equipo: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_ordenes_equipo(id_equipo):
        """
        Obtiene todas las órdenes de trabajo de un equipo
        
        Args:
            id_equipo (int): ID del equipo
            
        Returns:
            list: Lista de órdenes
        """
        try:
            consulta = """
            SELECT 
                o.id_orden,
                o.descripcion_reparacion,
                o.estado_orden,
                o.fecha_inicio,
                o.fecha_finalizacion,
                u.nombre as tecnico_nombre
            FROM ordenes_trabajo o
            LEFT JOIN usuarios u ON o.id_tecnico_asignado = u.id_usuario
            WHERE o.id_equipo = ?
            ORDER BY o.fecha_inicio DESC
            """
            
            return db.obtener_todos(consulta, (id_equipo,))
            
        except Exception as e:
            config.guardar_log(f"Error al obtener órdenes del equipo: {e}", "ERROR")
            return []
    
    @staticmethod
    def verificar_alertas_automaticas():
        """
        Verifica y marca equipos que necesitan alertas automáticas
        (Se ejecutaría periódicamente o al listar equipos)
        
        Returns:
            dict: Resumen de alertas generadas
        """
        try:
            resumen = {
                'estancados': 0,
                'abandonados': 0
            }
            
            # Equipos estancados (más de X días sin movimiento)
            dias_estancado = config.dias_alerta_equipo_estancado
            fecha_limite_estancado = datetime.now() - timedelta(days=dias_estancado)
            
            consulta_estancados = """
            SELECT id_equipo, marca, modelo
            FROM equipos
            WHERE fecha_ultimo_movimiento < ?
            AND estado_actual NOT IN ('Entregado', 'Abandonado')
            """
            
            equipos_estancados = db.obtener_todos(consulta_estancados, (fecha_limite_estancado,))
            resumen['estancados'] = len(equipos_estancados)
            
            # Equipos abandonados (más de X días sin retirar)
            dias_abandonado = config.dias_alerta_equipo_abandonado
            fecha_limite_abandonado = datetime.now() - timedelta(days=dias_abandonado)
            
            consulta_abandonados = """
            SELECT id_equipo, marca, modelo, estado_actual
            FROM equipos
            WHERE fecha_ultimo_movimiento < ?
            AND estado_actual NOT IN ('Entregado', 'Abandonado')
            """
            
            equipos_abandonados = db.obtener_todos(consulta_abandonados, (fecha_limite_abandonado,))
            
            # Marcar automáticamente como abandonados
            for equipo in equipos_abandonados:
                # Solo si está en estado "Listo" o "Sin reparación"
                if equipo['estado_actual'] in ['Listo', 'Sin reparación']:
                    ModuloEquipos.marcar_como_abandonado(
                        equipo['id_equipo'],
                        1,  # Usuario sistema
                        "",
                        "Marcado automáticamente por el sistema (90+ días sin retirar)"
                    )
                    resumen['abandonados'] += 1
            
            return resumen
            
        except Exception as e:
            config.guardar_log(f"Error al verificar alertas automáticas: {e}", "ERROR")
            return {'estancados': 0, 'abandonados': 0}
    
    @staticmethod
    def buscar_equipo_por_identificador(identificador):
        """
        Busca un equipo por su identificador (IMEI, serial, etc.)
        
        Args:
            identificador (str): Identificador a buscar
            
        Returns:
            dict: Equipo encontrado o None
        """
        try:
            consulta = """
            SELECT 
                e.*,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono
            FROM equipos e
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            WHERE e.identificador = ?
            """
            
            return db.obtener_uno(consulta, (identificador,))
            
        except Exception as e:
            config.guardar_log(f"Error al buscar equipo por identificador: {e}", "ERROR")
            return None

    @staticmethod
    def crear_equipo(datos_equipo, id_usuario):
        """
        Crea un nuevo equipo
        
        Args:
            datos_equipo (dict): Datos del equipo
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_nuevo)
        """
        try:
            # Validaciones básicas
            if not validar_requerido(datos_equipo.get('id_cliente'), "Cliente"):
                return False, "Debe seleccionar un cliente", None
            
            if not validar_requerido(datos_equipo.get('tipo_dispositivo'), "Tipo de dispositivo"):
                return False, "Debe seleccionar el tipo de dispositivo", None
            
            if not validar_requerido(datos_equipo.get('marca'), "Marca"):
                return False, "Debe ingresar la marca", None
            
            if not validar_requerido(datos_equipo.get('modelo'), "Modelo"):
                return False, "Debe ingresar el modelo", None
            
            if not validar_requerido(datos_equipo.get('estado_fisico'), "Estado físico"):
                return False, "Debe describir el estado físico", None
            
            if not validar_requerido(datos_equipo.get('falla_declarada'), "Falla declarada"):
                return False, "Debe describir la falla declarada", None
            
            # Insertar equipo
            consulta = """
            INSERT INTO equipos (
                id_cliente, tipo_dispositivo, marca, modelo,
                identificador, color, estado_fisico, accesorios,
                falla_declarada, fecha_ingreso, estado_actual,
                fecha_ultimo_movimiento, activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'En revisión', ?, 1)
            """
            
            fecha_actual = datetime.now()
            
            id_nuevo = db.ejecutar_consulta(
                consulta,
                (
                    datos_equipo['id_cliente'],
                    datos_equipo['tipo_dispositivo'],
                    datos_equipo['marca'],
                    datos_equipo['modelo'],
                    datos_equipo.get('identificador', ''),
                    datos_equipo.get('color', ''),
                    datos_equipo['estado_fisico'],
                    datos_equipo.get('accesorios', ''),
                    datos_equipo['falla_declarada'],
                    fecha_actual,
                    fecha_actual
                )
            )
            
            # TODO: Generar remito automáticamente cuando el módulo esté listo
            # from modulos.remitos_LOGICA import ModuloRemitos
            # exito_remito, msg_remito, numero_remito = ModuloRemitos.generar_remito(
            #     id_nuevo, 
            #     id_usuario
            # )
            exito_remito = False
            numero_remito = None
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Equipos",
                id_registro=id_nuevo,
                motivo=f"Equipo creado: {datos_equipo['marca']} {datos_equipo['modelo']}"
            )
            
            config.guardar_log(f"Equipo ID {id_nuevo} creado", "INFO")
            
            mensaje = f"Equipo creado exitosamente"
            if exito_remito:
                mensaje += f"\nRemito generado: {numero_remito}"
            
            return True, mensaje, id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al crear equipo: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def modificar_equipo(id_equipo, datos, id_usuario):
        """
        Modifica un equipo existente
        
        Args:
            id_equipo (int): ID del equipo
            datos (dict): Datos a modificar
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Obtener equipo actual
            equipo_actual = ModuloEquipos.obtener_equipo_por_id(id_equipo)
            
            if not equipo_actual:
                return False, "Equipo no encontrado"
            
            # Construir UPDATE dinámicamente
            campos_actualizar = []
            valores = []
            
            for campo, valor in datos.items():
                if campo in ['marca', 'modelo', 'identificador', 'color', 
                             'estado_fisico', 'accesorios', 'falla_declarada', 
                             'diagnostico_tecnico']:
                    campos_actualizar.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos_actualizar:
                return False, "No hay campos para actualizar"
            
            valores.append(id_equipo)
            
            consulta = f"""
            UPDATE equipos
            SET {', '.join(campos_actualizar)}
            WHERE id_equipo = ?
            """
            
            db.ejecutar_consulta(consulta, tuple(valores))
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Equipos",
                id_registro=id_equipo,
                motivo="Equipo modificado"
            )
            
            config.guardar_log(f"Equipo ID {id_equipo} modificado", "INFO")
            return True, "Equipo modificado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al modificar equipo: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def eliminar_equipo(id_equipo, id_usuario):
        """
        Elimina (desactiva) un equipo
        
        Args:
            id_equipo: ID del equipo a eliminar
            id_usuario: ID del usuario que elimina
            
        Returns:
            tuple: (exito: bool, mensaje: str)
        """
        try:
            # Verificar que el equipo existe
            equipo = ModuloEquipos.obtener_equipo_por_id(id_equipo)
            if not equipo:
                return False, "Equipo no encontrado"
            
            # Verificar que no tenga presupuestos activos
            consulta_presupuestos = """
            SELECT COUNT(*) as total
            FROM presupuestos
            WHERE id_equipo = ? AND estado NOT IN ('Rechazado', 'Vencido')
            """
            resultado_presu = db.obtener_uno(consulta_presupuestos, (id_equipo,))
            
            if resultado_presu and resultado_presu['total'] > 0:
                return False, f"No se puede eliminar: el equipo tiene {resultado_presu['total']} presupuesto(s) activo(s)"
            
            # Verificar que no tenga órdenes activas
            consulta_ordenes = """
            SELECT COUNT(*) as total
            FROM ordenes_trabajo
            WHERE id_equipo = ? AND estado NOT IN ('Cancelada', 'Completada')
            """
            resultado_ordenes = db.obtener_uno(consulta_ordenes, (id_equipo,))
            
            if resultado_ordenes and resultado_ordenes['total'] > 0:
                return False, f"No se puede eliminar: el equipo tiene {resultado_ordenes['total']} orden(es) de trabajo activa(s)"
            
            # Soft delete
            consulta = """
            UPDATE equipos
            SET activo = 0
            WHERE id_equipo = ?
            """
            
            db.ejecutar_consulta(consulta, (id_equipo,))
            
            # Registrar en auditoría (acción crítica)
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Eliminar",
                modulo="Equipos",
                id_registro=id_equipo,
                motivo=f"Equipo desactivado: {equipo['marca']} {equipo['modelo']}",
                es_critica=True
            )
            
            config.guardar_log(f"Equipo ID {id_equipo} eliminado por usuario ID {id_usuario}", "INFO")
            return True, "Equipo eliminado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al eliminar equipo: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def eliminar_equipo(id_equipo, id_usuario):
        """
        Elimina (desactiva) un equipo
        
        Args:
            id_equipo (int): ID del equipo
            id_usuario (int): ID del usuario que elimina
            
        Returns:
            tuple: (exito: bool, mensaje: str)
        """
        try:
            # Verificar que existe
            equipo = ModuloEquipos.obtener_equipo_por_id(id_equipo)
            if not equipo:
                return False, "Equipo no encontrado"
            
            # Verificar que no tenga presupuestos aprobados o pendientes
            try:
                consulta_presupuestos = """
                SELECT COUNT(*) as total
                FROM presupuestos
                WHERE id_equipo = ? AND estado_presupuesto IN ('Pendiente', 'Aprobado')
                """
                resultado = db.obtener_uno(consulta_presupuestos, (id_equipo,))
                
                if resultado and resultado['total'] > 0:
                    return False, f"No se puede eliminar: el equipo tiene {resultado['total']} presupuesto(s) activo(s)"
            except:
                pass  # Tabla presupuestos no existe aún
            
            # Verificar que no tenga órdenes activas
            try:
                consulta_ordenes = """
                SELECT COUNT(*) as total
                FROM ordenes_trabajo
                WHERE id_equipo = ? AND estado_orden NOT IN ('Completada', 'Cancelada')
                """
                resultado = db.obtener_uno(consulta_ordenes, (id_equipo,))
                
                if resultado and resultado['total'] > 0:
                    return False, f"No se puede eliminar: el equipo tiene {resultado['total']} orden(es) activa(s)"
            except:
                pass  # Tabla ordenes_trabajo no existe aún
            
            # Soft delete
            db.ejecutar_consulta(
                "UPDATE equipos SET activo = 0 WHERE id_equipo = ?",
                (id_equipo,)
            )
            
            # Auditoría (acción crítica)
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Eliminar",
                modulo="Equipos",
                id_registro=id_equipo,
                motivo="Equipo desactivado",
                es_critica=True
            )
            
            config.guardar_log(f"Equipo ID {id_equipo} eliminado por usuario ID {id_usuario}", "INFO")
            return True, "Equipo eliminado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al eliminar equipo: {e}", "ERROR")
            return False, f"Error al eliminar equipo: {str(e)}"
