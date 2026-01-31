# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE ÓRDENES DE TRABAJO
============================================================================
Ventana de gestión de órdenes de trabajo y reparaciones
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, CampoTextoMultilinea,
                                              ListaDesplegable)
from interfaz.estilos.estilos import Estilos
from modulos.ordenes_LOGICA import ModuloOrdenes
from modulos.equipos_LOGICA import ModuloEquipos
from sistema_base.configuracion import config
from datetime import datetime


class VentanaOrdenes(QWidget):
    """Ventana principal de gestión de órdenes de trabajo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_ordenes()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título con fondo blanco
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("🔧 Órdenes de Trabajo", "titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_titulo.addWidget(titulo)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tarjetas estadísticas
        tarjetas = self.crear_tarjetas_estadisticas()
        layout.addWidget(tarjetas)
        
        # Tabla
        self.tabla = self.crear_tabla_ordenes()
        layout.addWidget(self.tabla, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                padding: 20px;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)        
        # Botón Volver
        boton_volver = Boton("← Volver", "primario")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar por cliente, equipo...")
        self.campo_busqueda.textChanged.connect(self.buscar_ordenes)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Filtro estado
        self.combo_estado = ListaDesplegable()
        self.combo_estado.addItem("Todos los estados", "")
        for estado in ModuloOrdenes.ESTADOS_ORDEN:
            self.combo_estado.addItem(estado, estado)
        self.combo_estado.currentIndexChanged.connect(self.cargar_ordenes)
        layout.addWidget(self.combo_estado)
        
        # Botones
        boton_nueva = Boton("➕ Nueva Orden", "exito")
        boton_nueva.clicked.connect(self.abrir_dialogo_nueva)
        layout.addWidget(boton_nueva)
        
        boton_actualizar = Boton("🔄 Actualizar", "primario")
        boton_actualizar.clicked.connect(self.cargar_ordenes)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tarjetas_estadisticas(self):
        """Crea tarjetas de estadísticas"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        stats = ModuloOrdenes.obtener_estadisticas_ordenes()
        
        # Total
        t1 = self.crear_tarjeta("Total", str(stats.get('total', 0)), "#3498db")
        layout.addWidget(t1)
        
        # En curso
        t2 = self.crear_tarjeta("En Curso", str(stats.get('en_curso', 0)), "#ffc107")
        layout.addWidget(t2)
        
        # Finalizadas exitosas
        t3 = self.crear_tarjeta("Exitosas", str(stats.get('exitosas', 0)), "#28a745")
        layout.addWidget(t3)
        
        # Sin reparación
        t4 = self.crear_tarjeta("Sin Reparación", str(stats.get('sin_reparacion', 0)), "#dc3545")
        layout.addWidget(t4)
        
        contenedor.setLayout(layout)
        return contenedor
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea una tarjeta de estadística"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 20px;
                min-width: 160px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            font-size: {Estilos.TAMANO_SM}pt;
            color: {Estilos.COLOR_GRIS_600};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            font-weight: 500;
            border: none;
        """)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            font-size: 28pt;
            font-weight: 700;
            color: {color};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
            padding: 4px 0px;
        """)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_ordenes(self):
        """Crea la tabla de órdenes"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Equipo", "Técnico", "Estado", "Fecha Inicio", "Acciones"
        ])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        tabla.setColumnWidth(6, 250)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_ordenes(self):
        """Carga las órdenes"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            filtro_estado = self.combo_estado.currentData()
            
            ordenes = ModuloOrdenes.listar_ordenes(
                filtro_estado=filtro_estado,
                busqueda=busqueda
            )
            
            self.tabla.setRowCount(0)
            
            for orden in ordenes:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(orden['id_orden'])))
                
                # Cliente
                self.tabla.setItem(fila, 1, QTableWidgetItem(orden['cliente_nombre']))
                
                # Equipo
                equipo = f"{orden['tipo_dispositivo']} {orden['marca']} {orden['modelo']}"
                self.tabla.setItem(fila, 2, QTableWidgetItem(equipo))
                
                # Técnico
                tecnico = orden['tecnico_nombre'] if orden['tecnico_nombre'] else "-"
                self.tabla.setItem(fila, 3, QTableWidgetItem(tecnico))
                
                # Estado
                item_estado = QTableWidgetItem(orden['estado_orden'])
                if orden['estado_orden'] == "Finalizada con reparación":
                    item_estado.setForeground(QColor("#28a745"))
                elif orden['estado_orden'].startswith("Finalizada"):
                    item_estado.setForeground(QColor("#6c757d"))
                elif orden['estado_orden'] == "En reparación":
                    item_estado.setForeground(QColor("#ffc107"))
                self.tabla.setItem(fila, 4, item_estado)
                
                # Fecha inicio
                try:
                    fecha = datetime.fromisoformat(str(orden['fecha_inicio']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y')
                except:
                    fecha_texto = str(orden['fecha_inicio'])
                self.tabla.setItem(fila, 5, QTableWidgetItem(fecha_texto))
                
                # Acciones
                widget_acciones = self.crear_botones_acciones(orden)
                self.tabla.setCellWidget(fila, 6, widget_acciones)
        
        except Exception as e:
            config.guardar_log(f"Error al cargar órdenes: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar órdenes: {str(e)}", self)
    
    def crear_botones_acciones(self, orden):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver
        boton_ver = Boton("👁️ Ver", "primario")
        boton_ver.setMaximumWidth(70)
        boton_ver.clicked.connect(lambda: self.ver_detalle(orden['id_orden']))
        layout.addWidget(boton_ver)
        
        # Botón Cambiar Estado (si no está finalizada)
        if not orden['estado_orden'].startswith('Finalizada'):
            boton_estado = Boton("🔄 Estado", "secundario")
            boton_estado.setMaximumWidth(90)
            boton_estado.clicked.connect(lambda: self.cambiar_estado(orden['id_orden']))
            layout.addWidget(boton_estado)
            
            # Botón Finalizar
            boton_finalizar = Boton("✅", "exito")
            boton_finalizar.setToolTip("Finalizar orden")
            boton_finalizar.setMaximumWidth(50)
            boton_finalizar.clicked.connect(lambda: self.finalizar_orden(orden['id_orden']))
            layout.addWidget(boton_finalizar)
        
        widget.setLayout(layout)
        return widget
    
    def buscar_ordenes(self):
        """Busca órdenes"""
        self.cargar_ordenes()
    
    def abrir_dialogo_nueva(self):
        """Abre diálogo para nueva orden"""
        dialogo = DialogoNuevaOrden(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_ordenes()
    
    def ver_detalle(self, id_orden):
        """Ver detalle de la orden"""
        dialogo = DialogoDetalleOrden(id_orden, self)
        dialogo.exec_()
        self.cargar_ordenes()
    
    def cambiar_estado(self, id_orden):
        """Cambiar estado de la orden"""
        dialogo = DialogoCambiarEstadoOrden(id_orden, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_ordenes()
    
    def finalizar_orden(self, id_orden):
        """Finalizar orden"""
        dialogo = DialogoFinalizarOrden(id_orden, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_ordenes()
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)

class DialogoNuevaOrden(QDialog):
    """Diálogo para crear nueva orden manual"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.equipo_seleccionado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Nueva Orden de Trabajo")
        self.setFixedSize(600, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Nueva Orden de Trabajo (Manual)", "titulo")
        layout.addWidget(titulo)
        
        # Buscar equipo
        label_equipo = Etiqueta("1. SELECCIONAR EQUIPO")
        layout.addWidget(label_equipo)
        
        layout_buscar = QHBoxLayout()
        self.campo_buscar = CampoTexto("Buscar equipo...")
        layout_buscar.addWidget(self.campo_buscar, 1)
        
        boton_buscar = Boton("🔍", "primario")
        boton_buscar.setMaximumWidth(60)
        boton_buscar.clicked.connect(self.buscar_equipo)
        layout_buscar.addWidget(boton_buscar)
        
        layout.addLayout(layout_buscar)
        
        self.label_equipo = QLabel("No se ha seleccionado ningún equipo")
        self.label_equipo.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                color: #6c757d;
            }
        """)
        layout.addWidget(self.label_equipo)
        
        # Descripción
        label_desc = Etiqueta("2. DESCRIPCIÓN DEL TRABAJO")
        layout.addWidget(label_desc)
        
        self.campo_descripcion = CampoTextoMultilinea("Detalle el trabajo a realizar...")
        layout.addWidget(self.campo_descripcion)
        
        # Cobra diagnóstico
        self.check_diagnostico = QCheckBox("Cobra diagnóstico")
        layout.addWidget(self.check_diagnostico)
        
        # Error
        self.label_error = Etiqueta("", "error")
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_crear = Boton("Crear Orden", "exito")
        self.boton_crear.clicked.connect(self.crear_orden)
        layout_botones.addWidget(self.boton_crear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def buscar_equipo(self):
        """Busca equipos"""
        busqueda = self.campo_buscar.text().strip()
        if not busqueda:
            return
        
        equipos = ModuloEquipos.listar_equipos(busqueda=busqueda)
        if not equipos:
            Mensaje.informacion("Sin Resultados", "No se encontraron equipos", self)
            return
        
        if len(equipos) == 1:
            self.seleccionar_equipo(equipos[0])
        else:
            Mensaje.informacion("Múltiples Resultados", 
                              f"Se encontraron {len(equipos)} equipos", self)
    
    def seleccionar_equipo(self, equipo):
        """Selecciona un equipo"""
        self.equipo_seleccionado = equipo
        
        texto = f"✅ {equipo['tipo_dispositivo']} {equipo['marca']} {equipo['modelo']}\n"
        texto += f"Cliente: {equipo['cliente_nombre']}"
        
        self.label_equipo.setText(texto)
        self.label_equipo.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                color: #155724;
                font-weight: bold;
            }
        """)
    
    def crear_orden(self):
        """Crea la orden"""
        if not self.equipo_seleccionado:
            self.label_error.setText("Debes seleccionar un equipo")
            self.label_error.setVisible(True)
            return
        
        descripcion = self.campo_descripcion.toPlainText().strip()
        if not descripcion:
            self.label_error.setText("La descripción es obligatoria")
            self.label_error.setVisible(True)
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_nueva = ModuloOrdenes.crear_orden_manual(
            self.equipo_seleccionado['id_equipo'],
            descripcion,
            usuario_actual['id_usuario'],  # Se asigna al usuario actual
            self.check_diagnostico.isChecked(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Orden Creada", mensaje, self)
            self.accept()
        else:
            self.label_error.setText(mensaje)
            self.label_error.setVisible(True)


class DialogoCambiarEstadoOrden(QDialog):
    """Diálogo para cambiar estado de orden"""
    
    def __init__(self, id_orden, parent=None):
        super().__init__(parent)
        self.id_orden = id_orden
        self.orden = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Cambiar Estado de Orden")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Cambiar Estado de Orden", "titulo")
        layout.addWidget(titulo)
        
        # Info orden
        self.label_orden = QLabel()
        self.label_orden.setWordWrap(True)
        self.label_orden.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.label_orden)
        
        # Estado actual
        layout_actual = QHBoxLayout()
        layout_actual.addWidget(QLabel("<b>Estado Actual:</b>"))
        self.label_estado_actual = QLabel()
        self.label_estado_actual.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout_actual.addWidget(self.label_estado_actual)
        layout_actual.addStretch()
        layout.addLayout(layout_actual)
        
        # Nuevo estado
        label_nuevo = Etiqueta("Nuevo Estado:")
        layout.addWidget(label_nuevo)
        
        self.combo_estado = ListaDesplegable()
        for estado in ModuloOrdenes.ESTADOS_ORDEN:
            if not estado.startswith('Finalizada'):
                self.combo_estado.addItem(estado, estado)
        layout.addWidget(self.combo_estado)
        
        # Observaciones
        label_obs = Etiqueta("Observaciones:")
        layout.addWidget(label_obs)
        
        self.campo_observaciones = CampoTextoMultilinea("Detalles...")
        layout.addWidget(self.campo_observaciones)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_cambiar = Boton("Cambiar Estado", "exito")
        self.boton_cambiar.clicked.connect(self.cambiar_estado)
        layout_botones.addWidget(self.boton_cambiar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos de la orden"""
        self.orden = ModuloOrdenes.obtener_orden_por_id(self.id_orden)
        
        if self.orden:
            texto = f"Orden N° {self.orden['id_orden']}\n"
            texto += f"{self.orden['tipo_dispositivo']} {self.orden['marca']} {self.orden['modelo']}"
            self.label_orden.setText(texto)
            
            self.label_estado_actual.setText(self.orden['estado_orden'])
            
            # Preseleccionar estado actual
            index = self.combo_estado.findData(self.orden['estado_orden'])
            if index >= 0:
                self.combo_estado.setCurrentIndex(index)
    
    def cambiar_estado(self):
        """Cambia el estado"""
        nuevo_estado = self.combo_estado.currentData()
        observaciones = self.campo_observaciones.toPlainText().strip()
        
        if nuevo_estado == self.orden['estado_orden']:
            Mensaje.advertencia("Mismo Estado", "El estado seleccionado es el actual", self)
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloOrdenes.cambiar_estado_orden(
            self.id_orden,
            nuevo_estado,
            observaciones,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Estado Cambiado", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)


class DialogoFinalizarOrden(QDialog):
    """Diálogo para finalizar orden"""
    
    def __init__(self, id_orden, parent=None):
        super().__init__(parent)
        self.id_orden = id_orden
        self.orden = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Finalizar Orden de Trabajo")
        self.setFixedSize(600, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Finalizar Orden de Trabajo", "titulo")
        layout.addWidget(titulo)
        
        # Info orden
        self.label_orden = QLabel()
        self.label_orden.setWordWrap(True)
        self.label_orden.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.label_orden)
        
        # ¿Se reparó?
        label_reparado = Etiqueta("1. ¿SE REPARÓ EL EQUIPO?")
        layout.addWidget(label_reparado)
        
        self.check_con_reparacion = QCheckBox("Sí, el equipo fue reparado exitosamente")
        self.check_con_reparacion.setChecked(True)
        layout.addWidget(self.check_con_reparacion)
        
        # Trabajo realizado
        label_trabajo = Etiqueta("2. TRABAJO REALIZADO")
        layout.addWidget(label_trabajo)
        
        self.campo_trabajo = CampoTextoMultilinea("Descripción del trabajo realizado...")
        layout.addWidget(self.campo_trabajo)
        
        # Observaciones finales
        label_obs = Etiqueta("3. OBSERVACIONES FINALES")
        layout.addWidget(label_obs)
        
        self.campo_observaciones = CampoTextoMultilinea("Observaciones adicionales...")
        layout.addWidget(self.campo_observaciones)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_finalizar = Boton("Finalizar Orden", "exito")
        self.boton_finalizar.clicked.connect(self.finalizar)
        layout_botones.addWidget(self.boton_finalizar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos"""
        self.orden = ModuloOrdenes.obtener_orden_por_id(self.id_orden)
        
        if self.orden:
            texto = f"Orden N° {self.orden['id_orden']}\n"
            texto += f"{self.orden['tipo_dispositivo']} {self.orden['marca']} {self.orden['modelo']}\n"
            texto += f"Cliente: {self.orden['cliente_nombre']}"
            self.label_orden.setText(texto)
    
    def finalizar(self):
        """Finaliza la orden"""
        trabajo = self.campo_trabajo.toPlainText().strip()
        if not trabajo:
            Mensaje.advertencia("Campo Requerido", "El trabajo realizado es obligatorio", self)
            return
        
        confirmacion = Mensaje.confirmacion(
            "Finalizar Orden",
            "¿Está seguro que desea finalizar esta orden?\n\nEsta acción no se puede deshacer.",
            self
        )
        
        if not confirmacion:
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloOrdenes.finalizar_orden(
            self.id_orden,
            self.check_con_reparacion.isChecked(),
            trabajo,
            0.0,  # Monto diagnóstico (se puede agregar campo si se necesita)
            self.campo_observaciones.toPlainText().strip(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Orden Finalizada", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)


class DialogoDetalleOrden(QDialog):
    """Diálogo para ver detalle de orden"""
    
    def __init__(self, id_orden, parent=None):
        super().__init__(parent)
        self.id_orden = id_orden
        self.orden = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle de Orden")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Frame datos
        self.frame_datos = QFrame()
        self.frame_datos.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout_datos = QVBoxLayout()
        
        self.label_cliente = QLabel()
        self.label_equipo = QLabel()
        self.label_tecnico = QLabel()
        self.label_descripcion = QLabel()
        self.label_estado = QLabel()
        self.label_fechas = QLabel()
        
        for label in [self.label_cliente, self.label_equipo, self.label_tecnico,
                     self.label_descripcion, self.label_estado, self.label_fechas]:
            label.setWordWrap(True)
            layout_datos.addWidget(label)
        
        self.frame_datos.setLayout(layout_datos)
        layout.addWidget(self.frame_datos)
        
        layout.addStretch()
        
        # Botón cerrar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos"""
        self.orden = ModuloOrdenes.obtener_orden_por_id(self.id_orden)
        
        if not self.orden:
            return
        
        self.label_titulo.setText(f"Orden de Trabajo N° {self.orden['id_orden']}")
        
        self.label_cliente.setText(f"<b>Cliente:</b> {self.orden['cliente_nombre']} - {self.orden['cliente_telefono']}")
        
        self.label_equipo.setText(f"<b>Equipo:</b> {self.orden['tipo_dispositivo']} {self.orden['marca']} {self.orden['modelo']}")
        
        tecnico = self.orden['tecnico_nombre'] if self.orden['tecnico_nombre'] else "Sin asignar"
        self.label_tecnico.setText(f"<b>Técnico:</b> {tecnico}")
        
        self.label_descripcion.setText(f"<b>Trabajo a realizar:</b><br>{self.orden['descripcion_reparacion']}")
        
        self.label_estado.setText(f"<b>Estado:</b> {self.orden['estado_orden']}")
        
        try:
            fecha_inicio = datetime.fromisoformat(str(self.orden['fecha_inicio']).replace('Z', '+00:00'))
            fechas_texto = f"<b>Fecha inicio:</b> {fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
            
            if self.orden['fecha_finalizacion']:
                fecha_fin = datetime.fromisoformat(str(self.orden['fecha_finalizacion']).replace('Z', '+00:00'))
                fechas_texto += f"<br><b>Fecha finalización:</b> {fecha_fin.strftime('%d/%m/%Y %H:%M')}"
            
            self.label_fechas.setText(fechas_texto)
        except:
            self.label_fechas.setText("")
