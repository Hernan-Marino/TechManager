# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE PRESUPUESTOS
============================================================================
Lógica de negocio para gestión de presupuestos
============================================================================
"""

from datetime import datetime, timedelta
from base_datos.conexion import db
from sistema_base.validadores import validar_requerido
from sistema_base.configuracion import config


class ModuloPresupuestos:
    """Clase para manejar la lógica de negocio de presupuestos"""
    
    # Estados posibles
    ESTADOS_PRESUPUESTO = [
        "Pendiente",
        "Aceptado",
        "Rechazado por cliente",
        "Rechazado por vencimiento"
    ]
    
    @staticmethod
    def crear_presupuesto(id_equipo, descripcion_trabajo, monto_sin_recargo, 
                          aplicar_recargo, id_usuario):
        """
        Crea un nuevo presupuesto
        
        Args:
            id_equipo (int): ID del equipo
            descripcion_trabajo (str): Descripción del trabajo a realizar
            monto_sin_recargo (float): Monto base
            aplicar_recargo (bool): Si aplica recargo del 10%
            id_usuario (int): ID del usuario que crea
            
        Returns:
            tuple: (exito, mensaje, id_presupuesto_nuevo)
        """
        try:
            # Validaciones
            es_valido, mensaje = validar_requerido(descripcion_trabajo, "Descripción del trabajo")
            if not es_valido:
                return False, mensaje, None
            
            if monto_sin_recargo <= 0:
                return False, "El monto debe ser mayor a cero", None
            
            # Calcular recargo
            recargo = 0.0
            if aplicar_recargo:
                recargo = monto_sin_recargo * (config.porcentaje_recargo_transferencia / 100.0)
            
            monto_total = monto_sin_recargo + recargo
            
            # Fecha de vencimiento (7 días por defecto)
            fecha_creacion = datetime.now()
            fecha_vencimiento = fecha_creacion + timedelta(days=config.dias_vencimiento_presupuesto)
            
            # Insertar presupuesto
            consulta = """
            INSERT INTO presupuestos (
                id_equipo,
                descripcion_trabajo,
                monto_sin_recargo,
                recargo_transferencia,
                monto_total,
                estado_presupuesto,
                fecha_creacion,
                fecha_vencimiento,
                id_usuario_crea
            )
            VALUES (?, ?, ?, ?, ?, 'Pendiente', ?, ?, ?)
            """
            
            id_nuevo = db.ejecutar_consulta(
                consulta,
                (id_equipo, descripcion_trabajo, monto_sin_recargo, recargo,
                 monto_total, fecha_creacion, fecha_vencimiento, id_usuario)
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Crear",
                modulo="Presupuestos",
                id_registro=id_nuevo,
                motivo=f"Presupuesto creado: ${monto_total:.2f}"
            )
            
            # Agregar nota al equipo
            from modulos.equipos_LOGICA import ModuloEquipos
            ModuloEquipos.agregar_nota_equipo(
                id_equipo,
                f"Presupuesto creado: ${monto_total:.2f}",
                id_usuario
            )
            
            config.guardar_log(f"Presupuesto ID {id_nuevo} creado para equipo ID {id_equipo}", "INFO")
            return True, "Presupuesto creado exitosamente", id_nuevo
            
        except Exception as e:
            config.guardar_log(f"Error al crear presupuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def listar_presupuestos(filtro_estado="", solo_vencidos=False, busqueda="", orden="fecha_desc"):
        """
        Lista todos los presupuestos
        
        Args:
            filtro_estado (str): Filtrar por estado
            solo_vencidos (bool): Mostrar solo presupuestos vencidos
            busqueda (str): Buscar en descripción, cliente, equipo
            orden (str): fecha_desc, fecha_asc, monto_desc
            
        Returns:
            list: Lista de presupuestos
        """
        try:
            consulta = """
            SELECT 
                p.id_presupuesto,
                p.descripcion_trabajo,
                p.monto_sin_recargo,
                p.recargo_transferencia,
                p.monto_total,
                p.estado_presupuesto,
                p.fecha_creacion,
                p.fecha_vencimiento,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.id_equipo,
                c.nombre as nombre_cliente
            FROM presupuestos p
            INNER JOIN equipos e ON p.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            WHERE 1=1
            """
            
            parametros = []
            
            # Filtros
            if filtro_estado:
                consulta += " AND p.estado_presupuesto = ?"
                parametros.append(filtro_estado)
            
            # Filtro solo vencidos
            if solo_vencidos:
                consulta += " AND p.estado_presupuesto = 'Pendiente' AND p.fecha_vencimiento < ?"
                parametros.append(datetime.now())
            
            if busqueda:
                consulta += """ AND (
                    p.descripcion_trabajo LIKE ? OR
                    c.nombre LIKE ? OR
                    e.marca LIKE ? OR
                    e.modelo LIKE ?
                )"""
                busqueda_param = f"%{busqueda}%"
                parametros.extend([busqueda_param] * 4)
            
            # Ordenamiento
            if orden == "fecha_asc":
                consulta += " ORDER BY p.fecha_creacion ASC"
            elif orden == "monto_desc":
                consulta += " ORDER BY p.monto_total DESC"
            else:
                consulta += " ORDER BY p.fecha_creacion DESC"
            
            presupuestos = db.obtener_todos(consulta, tuple(parametros))
            
            # Calcular días hasta vencimiento y marcar vencidos
            for presupuesto in presupuestos:
                presupuesto['dias_hasta_vencimiento'] = ModuloPresupuestos.calcular_dias_hasta_vencimiento(
                    presupuesto['fecha_vencimiento'],
                    presupuesto['estado_presupuesto']
                )
                
                # Marcar si está vencido
                if presupuesto['estado_presupuesto'] == 'Pendiente':
                    try:
                        fecha_venc = datetime.fromisoformat(str(presupuesto['fecha_vencimiento']).replace('Z', '+00:00'))
                        presupuesto['esta_vencido'] = fecha_venc < datetime.now()
                    except:
                        presupuesto['esta_vencido'] = False
                else:
                    presupuesto['esta_vencido'] = False
            
            return presupuestos
            
        except Exception as e:
            config.guardar_log(f"Error al listar presupuestos: {e}", "ERROR")
            return []
    
    @staticmethod
    def obtener_presupuesto_por_id(id_presupuesto):
        """
        Obtiene un presupuesto por su ID
        
        Args:
            id_presupuesto (int): ID del presupuesto
            
        Returns:
            dict: Datos completos del presupuesto o None
        """
        try:
            consulta = """
            SELECT 
                p.*,
                e.tipo_dispositivo,
                e.marca,
                e.modelo,
                e.identificador,
                e.id_cliente,
                c.nombre as cliente_nombre,
                c.telefono as cliente_telefono,
                u.nombre as usuario_nombre
            FROM presupuestos p
            INNER JOIN equipos e ON p.id_equipo = e.id_equipo
            INNER JOIN clientes c ON e.id_cliente = c.id_cliente
            LEFT JOIN usuarios u ON p.id_usuario_crea = u.id_usuario
            WHERE p.id_presupuesto = ?
            """
            
            presupuesto = db.obtener_uno(consulta, (id_presupuesto,))
            
            if presupuesto:
                presupuesto['dias_hasta_vencimiento'] = ModuloPresupuestos.calcular_dias_hasta_vencimiento(
                    presupuesto['fecha_vencimiento'],
                    presupuesto['estado_presupuesto']
                )
            
            return presupuesto
            
        except Exception as e:
            config.guardar_log(f"Error al obtener presupuesto: {e}", "ERROR")
            return None
    
    @staticmethod
    def aceptar_presupuesto(id_presupuesto, id_usuario):
        """
        Acepta un presupuesto y genera orden de trabajo
        
        Args:
            id_presupuesto (int): ID del presupuesto
            id_usuario (int): ID del usuario que acepta
            
        Returns:
            tuple: (exito, mensaje, id_orden_generada)
        """
        try:
            # Obtener presupuesto
            presupuesto = ModuloPresupuestos.obtener_presupuesto_por_id(id_presupuesto)
            
            if not presupuesto:
                return False, "Presupuesto no encontrado", None
            
            if presupuesto['estado_presupuesto'] != "Pendiente":
                return False, f"El presupuesto ya está {presupuesto['estado_presupuesto'].lower()}", None
            
            # Actualizar estado
            consulta_actualizar = """
            UPDATE presupuestos
            SET estado_presupuesto = 'Aceptado',
                fecha_aceptacion = ?
            WHERE id_presupuesto = ?
            """
            
            db.ejecutar_consulta(consulta_actualizar, (datetime.now(), id_presupuesto))
            
            # Cambiar estado del equipo a "En reparación"
            from modulos.equipos_LOGICA import ModuloEquipos
            ModuloEquipos.cambiar_estado_equipo(
                presupuesto['id_equipo'],
                "En reparación",
                id_usuario,
                "Presupuesto aceptado por el cliente"
            )
            
            # Generar orden de trabajo
            from modulos.ordenes_LOGICA import ModuloOrdenes
            exito, mensaje, id_orden = ModuloOrdenes.crear_orden_desde_presupuesto(
                id_presupuesto,
                id_usuario
            )
            
            if not exito:
                config.guardar_log(f"Error al crear orden desde presupuesto: {mensaje}", "ERROR")
                # No revertir la aceptación, solo avisar
                return True, "Presupuesto aceptado pero hubo un error al crear la orden de trabajo", None
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Presupuestos",
                id_registro=id_presupuesto,
                campo_modificado="estado_presupuesto",
                valor_anterior="Pendiente",
                valor_nuevo="Aceptado",
                motivo=f"Presupuesto aceptado - Orden de trabajo ID {id_orden} creada"
            )
            
            config.guardar_log(f"Presupuesto ID {id_presupuesto} aceptado - Orden ID {id_orden} creada", "INFO")
            return True, f"Presupuesto aceptado - Orden de trabajo N° {id_orden} creada", id_orden
            
        except Exception as e:
            config.guardar_log(f"Error al aceptar presupuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def rechazar_presupuesto(id_presupuesto, motivo, observaciones, id_usuario):
        """
        Rechaza un presupuesto
        
        Args:
            id_presupuesto (int): ID del presupuesto
            motivo (str): Motivo del rechazo
            observaciones (str): Observaciones adicionales
            id_usuario (int): ID del usuario que rechaza
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Obtener presupuesto
            presupuesto = ModuloPresupuestos.obtener_presupuesto_por_id(id_presupuesto)
            
            if not presupuesto:
                return False, "Presupuesto no encontrado"
            
            if presupuesto['estado_presupuesto'] != "Pendiente":
                return False, f"El presupuesto ya está {presupuesto['estado_presupuesto'].lower()}"
            
            # Actualizar estado
            consulta = """
            UPDATE presupuestos
            SET estado_presupuesto = 'Rechazado por cliente',
                motivo_rechazo = ?,
                fecha_rechazo = ?
            WHERE id_presupuesto = ?
            """
            
            motivo_completo = motivo
            if observaciones:
                motivo_completo += f" - {observaciones}"
            
            db.ejecutar_consulta(consulta, (motivo_completo, datetime.now(), id_presupuesto))
            
            # Cambiar estado del equipo a "Sin reparación"
            from modulos.equipos_LOGICA import ModuloEquipos
            ModuloEquipos.cambiar_estado_equipo(
                presupuesto['id_equipo'],
                "Sin reparación",
                id_usuario,
                f"Presupuesto rechazado: {motivo_completo}"
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Presupuestos",
                id_registro=id_presupuesto,
                campo_modificado="estado_presupuesto",
                valor_anterior="Pendiente",
                valor_nuevo="Rechazado por cliente",
                motivo=motivo_completo
            )
            
            config.guardar_log(f"Presupuesto ID {id_presupuesto} rechazado: {motivo}", "INFO")
            return True, "Presupuesto rechazado"
            
        except Exception as e:
            config.guardar_log(f"Error al rechazar presupuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def verificar_vencimientos():
        """
        Verifica y marca presupuestos vencidos automáticamente
        
        Returns:
            int: Cantidad de presupuestos marcados como vencidos
        """
        try:
            fecha_actual = datetime.now()
            
            # Buscar presupuestos pendientes vencidos
            consulta = """
            SELECT id_presupuesto, id_equipo
            FROM presupuestos
            WHERE estado_presupuesto = 'Pendiente'
            AND fecha_vencimiento < ?
            """
            
            vencidos = db.obtener_todos(consulta, (fecha_actual,))
            
            for presupuesto in vencidos:
                # Actualizar estado
                consulta_update = """
                UPDATE presupuestos
                SET estado_presupuesto = 'Rechazado por vencimiento',
                    motivo_rechazo = 'Vencimiento automático (7 días sin respuesta)',
                    fecha_rechazo = ?
                WHERE id_presupuesto = ?
                """
                
                db.ejecutar_consulta(consulta_update, (fecha_actual, presupuesto['id_presupuesto']))
                
                # Agregar nota al equipo
                from modulos.equipos_LOGICA import ModuloEquipos
                ModuloEquipos.agregar_nota_equipo(
                    presupuesto['id_equipo'],
                    "Presupuesto vencido automáticamente (7 días sin respuesta)",
                    1  # Usuario sistema
                )
            
            if len(vencidos) > 0:
                config.guardar_log(f"{len(vencidos)} presupuestos marcados como vencidos", "INFO")
            
            return len(vencidos)
            
        except Exception as e:
            config.guardar_log(f"Error al verificar vencimientos: {e}", "ERROR")
            return 0
    
    @staticmethod
    def calcular_dias_hasta_vencimiento(fecha_vencimiento, estado):
        """
        Calcula los días hasta el vencimiento
        
        Args:
            fecha_vencimiento: Fecha de vencimiento
            estado (str): Estado del presupuesto
            
        Returns:
            int: Días hasta vencimiento (negativo si ya venció)
        """
        try:
            if estado != "Pendiente":
                return 0
            
            if isinstance(fecha_vencimiento, str):
                fecha = datetime.fromisoformat(fecha_vencimiento.replace('Z', '+00:00'))
            else:
                fecha = fecha_vencimiento
            
            diferencia = fecha - datetime.now()
            return diferencia.days
            
        except:
            return 0
    
    @staticmethod
    def obtener_estadisticas_presupuestos():
        """
        Obtiene estadísticas de presupuestos
        
        Returns:
            dict: Estadísticas
        """
        try:
            estadisticas = {}
            
            # Total
            consulta = "SELECT COUNT(*) as total FROM presupuestos"
            resultado = db.obtener_uno(consulta)
            estadisticas['total'] = resultado['total'] if resultado else 0
            
            # Pendientes
            consulta = "SELECT COUNT(*) as total FROM presupuestos WHERE estado_presupuesto = 'Pendiente'"
            resultado = db.obtener_uno(consulta)
            estadisticas['pendientes'] = resultado['total'] if resultado else 0
            
            # Aceptados
            consulta = "SELECT COUNT(*) as total FROM presupuestos WHERE estado_presupuesto = 'Aceptado'"
            resultado = db.obtener_uno(consulta)
            estadisticas['aceptados'] = resultado['total'] if resultado else 0
            
            # Rechazados (ambos tipos)
            consulta = "SELECT COUNT(*) as total FROM presupuestos WHERE estado_presupuesto IN ('Rechazado por cliente', 'Rechazado por vencimiento')"
            resultado = db.obtener_uno(consulta)
            estadisticas['rechazados'] = resultado['total'] if resultado else 0
            
            # Vencidos (pendientes con fecha vencida)
            consulta = """
            SELECT COUNT(*) as total 
            FROM presupuestos 
            WHERE estado_presupuesto = 'Pendiente'
            AND fecha_vencimiento < ?
            """
            resultado = db.obtener_uno(consulta, (datetime.now(),))
            estadisticas['vencidos'] = resultado['total'] if resultado else 0
            
            # Monto total aceptados
            consulta = "SELECT SUM(monto_total) as total FROM presupuestos WHERE estado_presupuesto = 'Aceptado'"
            resultado = db.obtener_uno(consulta)
            estadisticas['monto_total_aceptados'] = resultado['total'] if resultado and resultado['total'] else 0.0
            
            # Próximos a vencer (pendientes con menos de 2 días)
            fecha_limite = datetime.now() + timedelta(days=2)
            consulta = """
            SELECT COUNT(*) as total 
            FROM presupuestos 
            WHERE estado_presupuesto = 'Pendiente'
            AND fecha_vencimiento <= ?
            """
            resultado = db.obtener_uno(consulta, (fecha_limite,))
            estadisticas['proximos_a_vencer'] = resultado['total'] if resultado else 0
            
            return estadisticas
            
        except Exception as e:
            config.guardar_log(f"Error al obtener estadísticas de presupuestos: {e}", "ERROR")
            return {
                'total': 0,
                'pendientes': 0,
                'aceptados': 0,
                'rechazados': 0,
                'vencidos': 0
            }
    
    @staticmethod
    def rechazar_presupuesto_cliente(id_presupuesto, id_usuario):
        """
        Rechaza un presupuesto cuando el cliente lo rechaza (versión simplificada)
        
        Args:
            id_presupuesto (int): ID del presupuesto
            id_usuario (int): ID del usuario que registra el rechazo
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Obtener presupuesto
            presupuesto = ModuloPresupuestos.obtener_presupuesto_por_id(id_presupuesto)
            
            if not presupuesto:
                return False, "Presupuesto no encontrado"
            
            if presupuesto['estado_presupuesto'] != "Pendiente":
                return False, f"El presupuesto ya está {presupuesto['estado_presupuesto'].lower()}"
            
            # Actualizar estado
            consulta = """
            UPDATE presupuestos
            SET estado_presupuesto = 'Rechazado por cliente',
                motivo_rechazo = 'Rechazado por el cliente',
                fecha_rechazo = ?
            WHERE id_presupuesto = ?
            """
            
            db.ejecutar_consulta(consulta, (datetime.now(), id_presupuesto))
            
            # Cambiar estado del equipo a "Sin reparación"
            from modulos.equipos_LOGICA import ModuloEquipos
            ModuloEquipos.cambiar_estado_equipo(
                presupuesto['id_equipo'],
                "Sin reparación",
                id_usuario,
                "Presupuesto rechazado por el cliente"
            )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Presupuestos",
                id_registro=id_presupuesto,
                campo_modificado="estado_presupuesto",
                valor_anterior="Pendiente",
                valor_nuevo="Rechazado por cliente",
                motivo="Cliente rechazó el presupuesto"
            )
            
            # Agregar nota al equipo
            ModuloEquipos.agregar_nota_equipo(
                presupuesto['id_equipo'],
                "Presupuesto rechazado por el cliente",
                id_usuario
            )
            
            config.guardar_log(f"Presupuesto ID {id_presupuesto} rechazado por cliente", "INFO")
            return True, "Presupuesto rechazado exitosamente"
            
        except Exception as e:
            config.guardar_log(f"Error al rechazar presupuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def generar_pdf_presupuesto(id_presupuesto):
        """
        Genera un PDF del presupuesto
        
        Args:
            id_presupuesto (int): ID del presupuesto
            
        Returns:
            tuple: (exito, mensaje, ruta_archivo)
        """
        try:
            # Obtener datos del presupuesto
            presupuesto = ModuloPresupuestos.obtener_presupuesto_por_id(id_presupuesto)
            
            if not presupuesto:
                return False, "Presupuesto no encontrado", None
            
            # Importar módulo de PDFs
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            import os
            
            # Crear directorio si no existe
            directorio_pdfs = os.path.join(config.directorio_base, "presupuestos")
            os.makedirs(directorio_pdfs, exist_ok=True)
            
            # Nombre del archivo
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"presupuesto_{id_presupuesto}_{fecha_str}.pdf"
            ruta_completa = os.path.join(directorio_pdfs, nombre_archivo)
            
            # Crear PDF
            doc = SimpleDocTemplate(ruta_completa, pagesize=letter)
            elementos = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para título
            estilo_titulo = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Título
            titulo = Paragraph(f"<b>PRESUPUESTO #{id_presupuesto}</b>", estilo_titulo)
            elementos.append(titulo)
            
            # Información del negocio
            info_negocio = [
                [Paragraph(f"<b>{config.nombre_negocio}</b>", styles['Normal'])],
                [Paragraph(f"{config.direccion_negocio}", styles['Normal'])],
                [Paragraph(f"Tel: {config.telefono_negocio}", styles['Normal'])],
            ]
            
            if config.email_negocio:
                info_negocio.append([Paragraph(f"Email: {config.email_negocio}", styles['Normal'])])
            
            tabla_negocio = Table(info_negocio, colWidths=[6*inch])
            tabla_negocio.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            elementos.append(tabla_negocio)
            elementos.append(Spacer(1, 0.3*inch))
            
            # Información del cliente y equipo
            fecha_creacion = datetime.fromisoformat(str(presupuesto['fecha_creacion']).replace('Z', '+00:00')).strftime('%d/%m/%Y')
            fecha_vencimiento = datetime.fromisoformat(str(presupuesto['fecha_vencimiento']).replace('Z', '+00:00')).strftime('%d/%m/%Y')
            
            datos_cliente = [
                ['<b>Fecha:</b>', fecha_creacion, '<b>Vencimiento:</b>', fecha_vencimiento],
                ['<b>Cliente:</b>', presupuesto['nombre_cliente'], '<b>Estado:</b>', presupuesto['estado_presupuesto']],
                ['<b>Equipo:</b>', f"{presupuesto['marca']} {presupuesto['modelo']}", '<b>Tipo:</b>', presupuesto['tipo_dispositivo']],
            ]
            
            tabla_cliente = Table(datos_cliente, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
            tabla_cliente.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8f9fa')),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elementos.append(tabla_cliente)
            elementos.append(Spacer(1, 0.3*inch))
            
            # Descripción del trabajo
            elementos.append(Paragraph('<b>Descripción del Trabajo:</b>', styles['Heading2']))
            elementos.append(Spacer(1, 0.1*inch))
            elementos.append(Paragraph(presupuesto['descripcion_trabajo'], styles['Normal']))
            elementos.append(Spacer(1, 0.3*inch))
            
            # Detalle de montos
            from sistema_base.utilidades import formatear_dinero
            
            datos_montos = [
                ['<b>Concepto</b>', '<b>Monto</b>'],
                ['Mano de obra y reparación', formatear_dinero(presupuesto['monto_sin_recargo'])],
                ['Recargo por transferencia', formatear_dinero(presupuesto['recargo_transferencia'])],
                ['<b>TOTAL</b>', f"<b>{formatear_dinero(presupuesto['monto_total'])}</b>"],
            ]
            
            tabla_montos = Table(datos_montos, colWidths=[4.5*inch, 2*inch])
            tabla_montos.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTSIZE', (0, -1), (-1, -1), 13),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elementos.append(tabla_montos)
            elementos.append(Spacer(1, 0.4*inch))
            
            # Texto del presupuesto
            if config.texto_presupuesto:
                elementos.append(Paragraph('<b>Condiciones:</b>', styles['Heading3']))
                elementos.append(Spacer(1, 0.1*inch))
                elementos.append(Paragraph(config.texto_presupuesto, styles['Normal']))
            
            # Generar PDF
            doc.build(elementos)
            
            config.guardar_log(f"PDF de presupuesto ID {id_presupuesto} generado: {ruta_completa}", "INFO")
            return True, "PDF generado exitosamente", ruta_completa
            
        except ImportError:
            return False, "Error: La librería reportlab no está instalada. Ejecute: pip install reportlab", None
        except Exception as e:
            config.guardar_log(f"Error al generar PDF de presupuesto: {e}", "ERROR")
            return False, f"Error al generar PDF: {str(e)}", None

    @staticmethod
    def aprobar_presupuesto(id_presupuesto, id_usuario):
        """
        Aprueba un presupuesto y crea la orden de trabajo
        
        Args:
            id_presupuesto (int): ID del presupuesto
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, id_orden_nueva)
        """
        try:
            presupuesto = ModuloPresupuestos.obtener_presupuesto_por_id(id_presupuesto)
            
            if not presupuesto:
                return False, "Presupuesto no encontrado", None
            
            if presupuesto['estado_presupuesto'] != 'Pendiente':
                return False, f"El presupuesto está {presupuesto['estado_presupuesto'].lower()}", None
            
            # Actualizar presupuesto a Aprobado
            consulta_update = """
            UPDATE presupuestos
            SET estado_presupuesto = 'Aprobado',
                fecha_respuesta = ?
            WHERE id_presupuesto = ?
            """
            
            db.ejecutar_consulta(consulta_update, (datetime.now(), id_presupuesto))
            
            # Crear orden de trabajo automáticamente
            from modulos.ordenes_LOGICA import ModuloOrdenes
            
            datos_orden = {
                'id_presupuesto': id_presupuesto,
                'id_equipo': presupuesto['id_equipo'],
                'id_cliente': presupuesto['id_cliente'],
                'id_tecnico': id_usuario,
                'descripcion_trabajo': presupuesto['descripcion_trabajo'],
                'monto_presupuestado': presupuesto['monto_total']
            }
            
            exito_orden, msg_orden, id_orden = ModuloOrdenes.crear_orden(datos_orden, id_usuario)
            
            if exito_orden:
                # Cambiar estado del equipo
                from modulos.equipos_LOGICA import ModuloEquipos
                ModuloEquipos.cambiar_estado_equipo(
                    presupuesto['id_equipo'],
                    'En reparación',
                    id_usuario
                )
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Presupuestos",
                id_registro=id_presupuesto,
                campo_modificado="estado_presupuesto",
                valor_anterior="Pendiente",
                valor_nuevo="Aprobado",
                motivo="Presupuesto aprobado por cliente"
            )
            
            config.guardar_log(f"Presupuesto ID {id_presupuesto} aprobado", "INFO")
            
            if exito_orden:
                return True, f"Presupuesto aprobado y orden de trabajo creada", id_orden
            else:
                return True, f"Presupuesto aprobado (advertencia: {msg_orden})", None
            
        except Exception as e:
            config.guardar_log(f"Error al aprobar presupuesto: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
