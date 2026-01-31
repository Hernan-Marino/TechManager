# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE PRESUPUESTOS
============================================================================
Ventana de gestión de presupuestos con diseño moderno
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QTextEdit, QCheckBox,
                             QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              ListaDesplegable, Mensaje)
from interfaz.estilos.estilos import Estilos
from modulos.presupuestos_LOGICA import ModuloPresupuestos
from modulos.equipos_LOGICA import ModuloEquipos
from sistema_base.configuracion import config
from sistema_base.utilidades import formatear_dinero


class VentanaPresupuestos(QWidget):
    """Ventana principal de gestión de presupuestos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.inicializar_ui()
        self.cargar_presupuestos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tarjetas estadísticas
        tarjetas = self.crear_tarjetas_estadisticas()
        layout.addWidget(tarjetas)
        
        # Tabla
        self.tabla = self.crear_tabla_presupuestos()
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
        # Botón Volver al Dashboard
        boton_volver = Boton("← Volver al Dashboard", "neutro")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar por cliente, equipo, descripción...")
        self.campo_busqueda.textChanged.connect(self.buscar_presupuestos)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Filtro estado
        self.combo_estado = ListaDesplegable()
        self.combo_estado.addItem("Todos los estados", "")
        for estado in ModuloPresupuestos.ESTADOS_PRESUPUESTO:
            self.combo_estado.addItem(estado, estado)
        self.combo_estado.currentIndexChanged.connect(self.cargar_presupuestos)
        layout.addWidget(self.combo_estado)
        
        # Checkbox solo vencidos
        self.check_vencidos = QCheckBox("Solo vencidos")
        self.check_vencidos.stateChanged.connect(self.cargar_presupuestos)
        layout.addWidget(self.check_vencidos)
        
        # Botones
        boton_nuevo = Boton("➕ Nuevo Presupuesto", "exito")
        boton_nuevo.clicked.connect(self.abrir_dialogo_nuevo)
        layout.addWidget(boton_nuevo)
        
        boton_actualizar = Boton("🔄 Actualizar", "secundario")
        boton_actualizar.clicked.connect(self.cargar_presupuestos)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tarjetas_estadisticas(self):
        """Crea tarjetas de estadísticas"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        stats = ModuloPresupuestos.obtener_estadisticas_presupuestos()
        
        # Total
        t1 = self.crear_tarjeta("Total Presupuestos", str(stats['total']), "#3498db")
        layout.addWidget(t1)
        
        # Pendientes
        t2 = self.crear_tarjeta("Pendientes", str(stats['pendientes']), "#ffc107")
        layout.addWidget(t2)
        
        # Aceptados
        t3 = self.crear_tarjeta("Aceptados", str(stats['aceptados']), "#28a745")
        layout.addWidget(t3)
        
        # Rechazados
        t4 = self.crear_tarjeta("Rechazados", str(stats['rechazados']), "#dc3545")
        layout.addWidget(t4)
        
        # Vencidos
        t5 = self.crear_tarjeta("Vencidos", str(stats['vencidos']), "#e74c3c")
        layout.addWidget(t5)
        
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
    
    def crear_tabla_presupuestos(self):
        """Crea la tabla de presupuestos"""
        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Equipo", "Monto Total", "Estado", 
            "Fecha Creación", "Vencimiento", "Acciones"
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
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        tabla.setColumnWidth(7, 320)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_presupuestos(self):
        """Carga los presupuestos en la tabla"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            filtro_estado = self.combo_estado.currentData()
            solo_vencidos = self.check_vencidos.isChecked()
            
            presupuestos = ModuloPresupuestos.listar_presupuestos(
                filtro_estado=filtro_estado,
                solo_vencidos=solo_vencidos,
                busqueda=busqueda
            )
            
            self.tabla.setRowCount(0)
            
            for presup in presupuestos:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(presup['id_presupuesto'])))
                
                # Cliente
                self.tabla.setItem(fila, 1, QTableWidgetItem(presup['nombre_cliente']))
                
                # Equipo
                equipo_texto = f"{presup['marca']} {presup['modelo']}"
                self.tabla.setItem(fila, 2, QTableWidgetItem(equipo_texto))
                
                # Monto Total
                monto_item = QTableWidgetItem(formatear_dinero(presup['monto_total']))
                monto_item.setForeground(QColor("#2563eb"))
                monto_item.setFont(self.tabla.font())
                f = monto_item.font()
                f.setBold(True)
                monto_item.setFont(f)
                self.tabla.setItem(fila, 3, monto_item)
                
                # Estado
                estado_item = QTableWidgetItem(presup['estado_presupuesto'])
                if presup['estado_presupuesto'] == "Pendiente":
                    estado_item.setForeground(QColor("#ffc107"))
                elif presup['estado_presupuesto'] == "Aceptado":
                    estado_item.setForeground(QColor("#28a745"))
                else:
                    estado_item.setForeground(QColor("#dc3545"))
                self.tabla.setItem(fila, 4, estado_item)
                
                # Fecha creación
                fecha_creacion = presup['fecha_creacion'].split()[0] if isinstance(presup['fecha_creacion'], str) else str(presup['fecha_creacion'])
                self.tabla.setItem(fila, 5, QTableWidgetItem(fecha_creacion))
                
                # Vencimiento
                fecha_venc = presup['fecha_vencimiento'].split()[0] if isinstance(presup['fecha_vencimiento'], str) else str(presup['fecha_vencimiento'])
                venc_item = QTableWidgetItem(fecha_venc)
                
                # Marcar vencidos en rojo
                if presup.get('esta_vencido', False):
                    venc_item.setForeground(QColor("#dc3545"))
                    f = venc_item.font()
                    f.setBold(True)
                    venc_item.setFont(f)
                
                self.tabla.setItem(fila, 6, venc_item)
                
                # Botones de acción
                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout()
                layout_acciones.setContentsMargins(5, 2, 5, 2)
                layout_acciones.setSpacing(5)
                
                # Botón Ver
                boton_ver = Boton("👁️ Ver", "neutro")
                boton_ver.setMaximumWidth(80)
                boton_ver.clicked.connect(lambda checked, p=presup: self.ver_presupuesto(p))
                layout_acciones.addWidget(boton_ver)
                
                # Botón Aceptar (solo si está pendiente)
                if presup['estado_presupuesto'] == "Pendiente":
                    boton_aceptar = Boton("✓ Aceptar", "exito")
                    boton_aceptar.setMaximumWidth(90)
                    boton_aceptar.clicked.connect(lambda checked, id=presup['id_presupuesto']: self.aceptar_presupuesto(id))
                    layout_acciones.addWidget(boton_aceptar)
                    
                    boton_rechazar = Boton("✗ Rechazar", "peligro")
                    boton_rechazar.setMaximumWidth(100)
                    boton_rechazar.clicked.connect(lambda checked, id=presup['id_presupuesto']: self.rechazar_presupuesto(id))
                    layout_acciones.addWidget(boton_rechazar)
                
                # Botón Imprimir
                boton_imprimir = Boton("🖨️ PDF", "neutro")
                boton_imprimir.setMaximumWidth(80)
                boton_imprimir.clicked.connect(lambda checked, id=presup['id_presupuesto']: self.imprimir_presupuesto(id))
                layout_acciones.addWidget(boton_imprimir)
                
                layout_acciones.addStretch()
                widget_acciones.setLayout(layout_acciones)
                self.tabla.setCellWidget(fila, 7, widget_acciones)
            
            # Recargar estadísticas
            self.actualizar_estadisticas()
            
        except Exception as e:
            Mensaje.error("Error", f"Error al cargar presupuestos: {str(e)}", self)
    
    def buscar_presupuestos(self):
        """Busca presupuestos según el texto ingresado"""
        self.cargar_presupuestos()
    
    def actualizar_estadisticas(self):
        """Actualiza las tarjetas de estadísticas"""
        # Eliminar tarjetas actuales
        for i in reversed(range(self.layout().count())):
            item = self.layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), QFrame):
                # Verificar si es el contenedor de tarjetas
                if item.widget().layout() and item.widget().layout().count() == 5:
                    item.widget().deleteLater()
                    # Insertar nuevas tarjetas en la misma posición
                    tarjetas = self.crear_tarjetas_estadisticas()
                    self.layout().insertWidget(1, tarjetas)
                    break
    
    def abrir_dialogo_nuevo(self):
        """Abre diálogo para crear presupuesto"""
        dialogo = DialogoNuevoPresupuesto(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_presupuestos()
    
    def ver_presupuesto(self, presupuesto):
        """Muestra detalles del presupuesto"""
        dialogo = DialogoDetallePresupuesto(presupuesto, self)
        dialogo.exec_()
    
    def aceptar_presupuesto(self, id_presupuesto):
        """Acepta un presupuesto"""
        if Mensaje.confirmacion(
            "Aceptar Presupuesto",
            "¿Confirma que desea aceptar este presupuesto?",
            self
        ):
            exito, mensaje = ModuloPresupuestos.aceptar_presupuesto(
                id_presupuesto,
                config.usuario_actual['id_usuario']
            )
            
            if exito:
                Mensaje.exito("Éxito", mensaje, self)
                self.cargar_presupuestos()
            else:
                Mensaje.error("Error", mensaje, self)
    
    def rechazar_presupuesto(self, id_presupuesto):
        """Rechaza un presupuesto"""
        if Mensaje.confirmacion(
            "Rechazar Presupuesto",
            "¿Confirma que el cliente rechazó este presupuesto?",
            self
        ):
            exito, mensaje = ModuloPresupuestos.rechazar_presupuesto_cliente(
                id_presupuesto,
                config.usuario_actual['id_usuario']
            )
            
            if exito:
                Mensaje.exito("Éxito", mensaje, self)
                self.cargar_presupuestos()
            else:
                Mensaje.error("Error", mensaje, self)
    
    def imprimir_presupuesto(self, id_presupuesto):
        """Genera PDF del presupuesto"""
        try:
            exito, mensaje, ruta = ModuloPresupuestos.generar_pdf_presupuesto(id_presupuesto)
            
            if exito:
                Mensaje.exito("PDF Generado", f"El presupuesto se guardó en:\n{ruta}", self)
            else:
                Mensaje.error("Error", mensaje, self)
                
        except Exception as e:
            Mensaje.error("Error", f"Error al generar PDF: {str(e)}", self)


class DialogoNuevoPresupuesto(QDialog):
    """Diálogo para crear nuevo presupuesto"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Presupuesto")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Crear Nuevo Presupuesto", "subtitulo")
        layout.addWidget(titulo)
        
        # Selección de equipo
        layout.addWidget(Etiqueta("Equipo:"))
        self.combo_equipo = ListaDesplegable()
        self.cargar_equipos()
        layout.addWidget(self.combo_equipo)
        
        # Descripción del trabajo
        layout.addWidget(Etiqueta("Descripción del Trabajo:"))
        self.texto_descripcion = QTextEdit()
        self.texto_descripcion.setMinimumHeight(100)
        self.texto_descripcion.setStyleSheet(Estilos.campo_texto_multilinea())
        layout.addWidget(self.texto_descripcion)
        
        # Monto sin recargo
        layout.addWidget(Etiqueta("Monto (sin recargo):"))
        self.campo_monto = CampoTexto("0.00")
        layout.addWidget(self.campo_monto)
        
        # Aplicar recargo
        self.check_recargo = QCheckBox(f"Aplicar recargo de {config.porcentaje_recargo_transferencia}% (pago por transferencia)")
        self.check_recargo.setChecked(True)
        layout.addWidget(self.check_recargo)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        boton_crear = Boton("Crear Presupuesto", "exito")
        boton_crear.clicked.connect(self.crear_presupuesto)
        layout_botones.addWidget(boton_crear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_equipos(self):
        """Carga equipos disponibles"""
        equipos = ModuloEquipos.listar_equipos(
            filtro_estado="Ingresado",
            busqueda=""
        )
        
        for equipo in equipos:
            texto = f"{equipo['marca']} {equipo['modelo']} - {equipo['nombre_cliente']}"
            self.combo_equipo.addItem(texto, equipo['id_equipo'])
    
    def crear_presupuesto(self):
        """Crea el presupuesto"""
        try:
            # Validar
            if self.combo_equipo.currentIndex() < 0:
                Mensaje.advertencia("Atención", "Debe seleccionar un equipo", self)
                return
            
            descripcion = self.texto_descripcion.toPlainText().strip()
            if not descripcion:
                Mensaje.advertencia("Atención", "Debe ingresar la descripción del trabajo", self)
                return
            
            try:
                monto = float(self.campo_monto.text().replace(',', '.'))
                if monto <= 0:
                    raise ValueError()
            except:
                Mensaje.advertencia("Atención", "Debe ingresar un monto válido mayor a cero", self)
                return
            
            # Crear presupuesto
            exito, mensaje, id_nuevo = ModuloPresupuestos.crear_presupuesto(
                id_equipo=self.combo_equipo.currentData(),
                descripcion_trabajo=descripcion,
                monto_sin_recargo=monto,
                aplicar_recargo=self.check_recargo.isChecked(),
                id_usuario=config.usuario_actual['id_usuario']
            )
            
            if exito:
                Mensaje.exito("Éxito", mensaje, self)
                self.accept()
            else:
                Mensaje.error("Error", mensaje, self)
                
        except Exception as e:
            Mensaje.error("Error", f"Error al crear presupuesto: {str(e)}", self)


class DialogoDetallePresupuesto(QDialog):
    """Diálogo que muestra detalles del presupuesto"""
    
    def __init__(self, presupuesto, parent=None):
        super().__init__(parent)
        self.presupuesto = presupuesto
        self.setWindowTitle(f"Presupuesto #{presupuesto['id_presupuesto']}")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta(f"Presupuesto #{self.presupuesto['id_presupuesto']}", "titulo")
        layout.addWidget(titulo)
        
        # Información del cliente y equipo
        frame_info = QFrame()
        frame_info.setStyleSheet(f"""
            QFrame {{
                background-color: {Estilos.COLOR_GRIS_50};
                padding: 15px;
            }}
        """)
        layout_info = QVBoxLayout()
        
        layout_info.addWidget(Etiqueta(f"Cliente: {self.presupuesto['nombre_cliente']}"))
        layout_info.addWidget(Etiqueta(f"Equipo: {self.presupuesto['marca']} {self.presupuesto['modelo']}"))
        layout_info.addWidget(Etiqueta(f"Estado: {self.presupuesto['estado_presupuesto']}"))
        
        frame_info.setLayout(layout_info)
        layout.addWidget(frame_info)
        
        # Descripción
        layout.addWidget(Etiqueta("Descripción del Trabajo:", "subtitulo"))
        texto_desc = QLabel(self.presupuesto.get('descripcion_trabajo', ''))
        texto_desc.setWordWrap(True)
        texto_desc.setStyleSheet(f"padding: 10px; background-color: {Estilos.COLOR_FONDO_CLARO};")
        layout.addWidget(texto_desc)
        
        # Montos
        layout.addWidget(Etiqueta("Detalle de Montos:", "subtitulo"))
        
        layout.addWidget(Etiqueta(f"Monto base: {formatear_dinero(self.presupuesto['monto_sin_recargo'])}"))
        layout.addWidget(Etiqueta(f"Recargo: {formatear_dinero(self.presupuesto['recargo_transferencia'])}"))
        
        monto_total = Etiqueta(f"TOTAL: {formatear_dinero(self.presupuesto['monto_total'])}")
        monto_total.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2563eb;")
        layout.addWidget(monto_total)
        
        # Fechas
        layout.addWidget(Etiqueta(f"Fecha creación: {self.presupuesto['fecha_creacion']}"))
        layout.addWidget(Etiqueta(f"Fecha vencimiento: {self.presupuesto['fecha_vencimiento']}"))
        
        # Botón cerrar
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout.addWidget(boton_cerrar)
        
        self.setLayout(layout)

    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        if self.parent():
            ventana_principal = self.parent()
            layout = ventana_principal.area_trabajo.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            dashboard = ventana_principal.crear_dashboard_completo()
            layout.addWidget(dashboard)

