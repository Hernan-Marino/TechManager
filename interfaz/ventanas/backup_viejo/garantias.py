# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ COMPLETA MÓDULO DE GARANTÍAS
============================================================================
Ventana completa para gestión de garantías de reparación
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QDateEdit, QCheckBox,
                             QSpinBox, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, ListaDesplegable,
                                              CampoTextoMultilinea)
from interfaz.estilos.estilos import Estilos
from modulos.garantias import ModuloGarantias
from modulos.equipos import ModuloEquipos
from modulos.ordenes import ModuloOrdenes
from sistema_base.configuracion import config
from datetime import datetime, timedelta


class VentanaGarantias(QWidget):
    """Ventana principal de gestión de garantías"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_garantias()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título y nuevo
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("🛡️ Gestión de Garantías", "titulo")
        layout_titulo.addWidget(titulo)
        
        layout_titulo.addStretch()
        
        # Info
        label_info = QLabel(f"Las garantías se crean automáticamente al finalizar órdenes con reparación ({config.dias_garantia_reparacion} días)")
        label_info.setStyleSheet("color: #6c757d; font-style: italic;")
        layout_titulo.addWidget(label_info)
        
        # Botón crear manual
        boton_nueva = Boton("➕ Crear Garantía Manual", "exito")
        boton_nueva.clicked.connect(self.crear_garantia_manual)
        layout_titulo.addWidget(boton_nueva)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tarjetas estadísticas
        self.frame_stats = QFrame()
        self.layout_stats = QHBoxLayout()
        self.layout_stats.setSpacing(15)
        self.frame_stats.setLayout(self.layout_stats)
        layout.addWidget(self.frame_stats)
        
        self.actualizar_estadisticas()
        
        # Tabla
        self.tabla = self.crear_tabla_garantias()
        layout.addWidget(self.tabla, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet(f"QWidget {{ background-color: {Estilos.COLOR_FONDO_CLARO}; padding: 20px; border: none; }}")
        
        layout = QHBoxLayout()
        layout.setSpacing(15)        
        # Botón Volver al Dashboard
        boton_volver = Boton("← Volver al Dashboard", "neutro")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar por cliente, equipo...")
        self.campo_busqueda.textChanged.connect(self.cargar_garantias)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Estado
        self.combo_estado = ListaDesplegable()
        self.combo_estado.addItem("Todos los estados", "")
        for estado in ModuloGarantias.ESTADOS_GARANTIA:
            self.combo_estado.addItem(estado, estado)
        self.combo_estado.currentIndexChanged.connect(self.cargar_garantias)
        layout.addWidget(self.combo_estado)
        
        # Filtro de fechas
        self.check_filtro_fecha = QCheckBox("Filtrar por fecha vencimiento")
        self.check_filtro_fecha.stateChanged.connect(self.toggle_filtro_fecha)
        layout.addWidget(self.check_filtro_fecha)
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate())
        self.fecha_desde.setEnabled(False)
        self.fecha_desde.dateChanged.connect(self.cargar_garantias)
        layout.addWidget(self.fecha_desde)
        
        layout.addWidget(QLabel("hasta"))
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate().addMonths(3))
        self.fecha_hasta.setEnabled(False)
        self.fecha_hasta.dateChanged.connect(self.cargar_garantias)
        layout.addWidget(self.fecha_hasta)
        
        # Solo por vencer
        self.check_por_vencer = QCheckBox("Solo próximas a vencer (≤7 días)")
        self.check_por_vencer.stateChanged.connect(self.cargar_garantias)
        layout.addWidget(self.check_por_vencer)
        
        # Botones
        boton_actualizar = Boton("🔄", "secundario")
        boton_actualizar.setMaximumWidth(50)
        boton_actualizar.setToolTip("Actualizar")
        boton_actualizar.clicked.connect(self.cargar_garantias)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def toggle_filtro_fecha(self):
        """Activa/desactiva filtro de fecha"""
        activo = self.check_filtro_fecha.isChecked()
        self.fecha_desde.setEnabled(activo)
        self.fecha_hasta.setEnabled(activo)
        self.cargar_garantias()
    
    def actualizar_estadisticas(self):
        """Actualiza tarjetas de estadísticas"""
        # Limpiar layout
        while self.layout_stats.count():
            child = self.layout_stats.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Obtener stats
        fecha_desde = None
        fecha_hasta = None
        
        if self.check_filtro_fecha.isChecked():
            fecha_desde = self.fecha_desde.date().toPyDate()
            fecha_hasta = self.fecha_hasta.date().toPyDate()
        
        stats = ModuloGarantias.obtener_estadisticas_garantias(fecha_desde, fecha_hasta)
        
        # Crear tarjetas
        self.layout_stats.addWidget(self.crear_tarjeta("Total", str(stats['total']), "#3498db"))
        self.layout_stats.addWidget(self.crear_tarjeta("Vigentes", str(stats.get('vigente', 0)), "#28a745"))
        self.layout_stats.addWidget(self.crear_tarjeta("Por Vencer (≤7 días)", str(stats['proximas_a_vencer']), "#ffc107"))
        self.layout_stats.addWidget(self.crear_tarjeta("Vencidas", str(stats.get('vencida', 0)), "#6c757d"))
        self.layout_stats.addWidget(self.crear_tarjeta("Utilizadas", str(stats.get('utilizada', 0)), "#17a2b8"))
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea tarjeta de estadística"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 20px;
                min-width: 150px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            font-size: {Estilos.TAMANO_XS}pt;
            color: {Estilos.COLOR_GRIS_600};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            font-weight: 500;
            border: none;
        """)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            font-size: 26pt;
            font-weight: 700;
            color: {color};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
            padding: 4px 0px;
        """)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_garantias(self):
        """Crea la tabla de garantías"""
        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Equipo", "Estado", "Inicio", "Vencimiento", "Días Rest.", "Acciones"
        ])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
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
        tabla.setColumnWidth(7, 200)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_garantias(self):
        """Carga las garantías"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            filtro_estado = self.combo_estado.currentData()
            
            fecha_desde = None
            fecha_hasta = None
            
            if self.check_filtro_fecha.isChecked():
                fecha_desde = self.fecha_desde.date().toPyDate()
                fecha_hasta = self.fecha_hasta.date().toPyDate()
            
            solo_por_vencer = self.check_por_vencer.isChecked()
            
            garantias = ModuloGarantias.listar_garantias(
                filtro_estado=filtro_estado,
                busqueda=busqueda,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                solo_por_vencer=solo_por_vencer
            )
            
            self.tabla.setRowCount(0)
            
            for garantia in garantias:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(garantia['id_garantia'])))
                
                # Cliente
                self.tabla.setItem(fila, 1, QTableWidgetItem(garantia['cliente_nombre']))
                
                # Equipo
                equipo_texto = f"{garantia['tipo_dispositivo']} {garantia['marca']} {garantia['modelo']}"
                self.tabla.setItem(fila, 2, QTableWidgetItem(equipo_texto))
                
                # Estado
                item_estado = QTableWidgetItem(garantia['estado_garantia'])
                if garantia['estado_garantia'] == "Vigente":
                    item_estado.setForeground(QColor("#28a745"))
                    item_estado.setFont(QFont("Arial", 10, QFont.Bold))
                elif garantia['estado_garantia'] == "Vencida":
                    item_estado.setForeground(QColor("#6c757d"))
                elif garantia['estado_garantia'] == "Utilizada":
                    item_estado.setForeground(QColor("#17a2b8"))
                self.tabla.setItem(fila, 3, item_estado)
                
                # Fecha inicio
                try:
                    fecha = datetime.fromisoformat(str(garantia['fecha_inicio']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y')
                except:
                    fecha_texto = str(garantia['fecha_inicio'])
                self.tabla.setItem(fila, 4, QTableWidgetItem(fecha_texto))
                
                # Fecha vencimiento
                try:
                    fecha = datetime.fromisoformat(str(garantia['fecha_vencimiento']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y')
                except:
                    fecha_texto = str(garantia['fecha_vencimiento'])
                self.tabla.setItem(fila, 5, QTableWidgetItem(fecha_texto))
                
                # Días restantes
                if garantia['estado_garantia'] == "Vigente":
                    dias = garantia['dias_restantes']
                    if dias <= 7:
                        item_dias = QTableWidgetItem(f"⚠️ {dias}")
                        item_dias.setForeground(QColor("#dc3545"))
                        item_dias.setFont(QFont("Arial", 10, QFont.Bold))
                    elif dias <= 15:
                        item_dias = QTableWidgetItem(f"⚠️ {dias}")
                        item_dias.setForeground(QColor("#ffc107"))
                        item_dias.setFont(QFont("Arial", 10, QFont.Bold))
                    else:
                        item_dias = QTableWidgetItem(str(dias))
                        item_dias.setForeground(QColor("#28a745"))
                    self.tabla.setItem(fila, 6, item_dias)
                else:
                    self.tabla.setItem(fila, 6, QTableWidgetItem("-"))
                
                # Acciones
                widget = self.crear_botones_acciones(garantia)
                self.tabla.setCellWidget(fila, 7, widget)
            
            # Actualizar stats
            self.actualizar_estadisticas()
        
        except Exception as e:
            config.guardar_log(f"Error al cargar garantías: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar garantías: {str(e)}", self)
    
    def crear_botones_acciones(self, garantia):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver
        boton_ver = Boton("👁️", "primario")
        boton_ver.setToolTip("Ver detalle")
        boton_ver.setMaximumWidth(50)
        boton_ver.clicked.connect(lambda: self.ver_detalle(garantia['id_garantia']))
        layout.addWidget(boton_ver)
        
        # Botón Utilizar (solo si está vigente)
        if garantia['estado_garantia'] == "Vigente":
            boton_usar = Boton("✓", "exito")
            boton_usar.setToolTip("Marcar como utilizada")
            boton_usar.setMaximumWidth(50)
            boton_usar.clicked.connect(lambda: self.marcar_utilizada(garantia['id_garantia']))
            layout.addWidget(boton_usar)
        
        # Botón Ver Reparación
        boton_reparacion = Boton("🔧", "secundario")
        boton_reparacion.setToolTip("Ver reparación original")
        boton_reparacion.setMaximumWidth(50)
        boton_reparacion.clicked.connect(lambda: self.ver_reparacion(garantia.get('id_orden')))
        layout.addWidget(boton_reparacion)
        
        widget.setLayout(layout)
        return widget
    
    def crear_garantia_manual(self):
        """Crear garantía manualmente"""
        dialogo = DialogoCrearGarantiaManual(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_garantias()
    
    def ver_detalle(self, id_garantia):
        """Ver detalle de garantía"""
        dialogo = DialogoDetalleGarantia(id_garantia, self)
        dialogo.exec_()
    
    def marcar_utilizada(self, id_garantia):
        """Marcar garantía como utilizada"""
        dialogo = DialogoMarcarGarantiaUtilizada(id_garantia, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_garantias()
    
    def ver_reparacion(self, id_orden):
        """Ver la reparación original"""
        if id_orden:
            from interfaz.ventanas.ordenes import DialogoDetalleOrden
            dialogo = DialogoDetalleOrden(id_orden, self)
            dialogo.exec_()
        else:
            Mensaje.informacion("Sin Orden", 
                              "Esta garantía no tiene una orden de reparación asociada.", self)


class DialogoCrearGarantiaManual(QDialog):
    """Diálogo para crear garantía manualmente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.equipo_seleccionado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Crear Garantía Manual")
        self.setFixedSize(650, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("➕ Crear Garantía Manualmente", "titulo")
        layout.addWidget(titulo)
        
        # Info
        info = QLabel("Las garantías normalmente se crean automáticamente. Use esto solo en casos especiales.")
        info.setWordWrap(True)
        info.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #fff3cd;
                border-radius: 5px;
                color: #856404;
            }
        """)
        layout.addWidget(info)
        
        # Buscar equipo
        label_equipo = Etiqueta("Buscar Equipo: *")
        layout.addWidget(label_equipo)
        
        layout_buscar = QHBoxLayout()
        self.campo_buscar_equipo = CampoTexto("Marca, modelo, IMEI...")
        layout_buscar.addWidget(self.campo_buscar_equipo, 1)
        
        boton_buscar = Boton("🔍 Buscar", "primario")
        boton_buscar.clicked.connect(self.buscar_equipo)
        layout_buscar.addWidget(boton_buscar)
        
        layout.addLayout(layout_buscar)
        
        # Equipo seleccionado
        self.label_equipo_seleccionado = QLabel("No hay equipo seleccionado")
        self.label_equipo_seleccionado.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 5px;
                color: #6c757d;
            }
        """)
        layout.addWidget(self.label_equipo_seleccionado)
        
        # Días de garantía
        label_dias = Etiqueta("Días de Garantía: *")
        layout.addWidget(label_dias)
        
        layout_dias = QHBoxLayout()
        self.spin_dias = QSpinBox()
        self.spin_dias.setMinimum(1)
        self.spin_dias.setMaximum(365)
        self.spin_dias.setValue(config.dias_garantia_reparacion)
        layout_dias.addWidget(self.spin_dias)
        
        label_dias_info = QLabel(f"(Por defecto: {config.dias_garantia_reparacion} días)")
        label_dias_info.setStyleSheet("color: #6c757d;")
        layout_dias.addWidget(label_dias_info)
        layout_dias.addStretch()
        
        layout.addLayout(layout_dias)
        
        # Motivo
        label_motivo = Etiqueta("Motivo de Creación Manual: *")
        layout.addWidget(label_motivo)
        
        self.campo_motivo = CampoTextoMultilinea("Explique por qué se crea manualmente...")
        self.campo_motivo.setMaximumHeight(100)
        layout.addWidget(self.campo_motivo)
        
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
        
        self.boton_crear = Boton("✓ Crear Garantía", "exito")
        self.boton_crear.clicked.connect(self.crear_garantia)
        layout_botones.addWidget(self.boton_crear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def buscar_equipo(self):
        """Busca equipos"""
        busqueda = self.campo_buscar_equipo.text().strip()
        
        if not busqueda:
            Mensaje.advertencia("Búsqueda Vacía", "Ingrese un término de búsqueda", self)
            return
        
        # Buscar equipos (solo retirados o listos)
        equipos = ModuloEquipos.listar_equipos(busqueda=busqueda)
        equipos_validos = [e for e in equipos if e['estado_actual'] in ["Listo para retirar", "Retirado"]]
        
        if not equipos_validos:
            Mensaje.informacion("Sin Resultados", 
                              "No se encontraron equipos o los equipos encontrados no están en estado válido para garantía.", 
                              self)
            return
        
        # Si hay varios, mostrar selector simple (tomamos el primero por simplicidad)
        if len(equipos_validos) > 0:
            self.equipo_seleccionado = equipos_validos[0]
            
            texto = f"✓ <b>{self.equipo_seleccionado['tipo_dispositivo']} {self.equipo_seleccionado['marca']} {self.equipo_seleccionado['modelo']}</b><br>"
            texto += f"Cliente: {self.equipo_seleccionado['cliente_nombre']}"
            
            self.label_equipo_seleccionado.setText(texto)
            self.label_equipo_seleccionado.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                    color: #155724;
                }
            """)
    
    def crear_garantia(self):
        """Crea la garantía"""
        if not self.equipo_seleccionado:
            self.label_error.setText("Debe seleccionar un equipo")
            self.label_error.setVisible(True)
            return
        
        motivo = self.campo_motivo.toPlainText().strip()
        
        if not motivo or len(motivo) < 10:
            self.label_error.setText("Debe especificar un motivo (mínimo 10 caracteres)")
            self.label_error.setVisible(True)
            return
        
        self.boton_crear.setEnabled(False)
        self.boton_crear.setText("Creando...")
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_garantia = ModuloGarantias.crear_garantia(
            self.equipo_seleccionado['id_equipo'],
            self.spin_dias.value(),
            None,  # Sin orden asociada
            f"MANUAL: {motivo}",
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Garantía Creada", mensaje, self)
            self.accept()
        else:
            self.label_error.setText(mensaje)
            self.label_error.setVisible(True)
            self.boton_crear.setEnabled(True)
            self.boton_crear.setText("✓ Crear Garantía")


class DialogoMarcarGarantiaUtilizada(QDialog):
    """Diálogo para marcar garantía como utilizada"""
    
    def __init__(self, id_garantia, parent=None):
        super().__init__(parent)
        self.id_garantia = id_garantia
        self.garantia = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Utilizar Garantía")
        self.setFixedSize(550, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("✓ Marcar Garantía como Utilizada", "titulo")
        layout.addWidget(titulo)
        
        # Info garantía
        self.label_info = QLabel()
        self.label_info.setWordWrap(True)
        self.label_info.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.label_info)
        
        # Motivo de uso
        label_motivo = Etiqueta("Motivo de Uso de la Garantía: *")
        layout.addWidget(label_motivo)
        
        self.campo_motivo = CampoTextoMultilinea("¿Por qué se utiliza la garantía?")
        self.campo_motivo.setMaximumHeight(100)
        layout.addWidget(self.campo_motivo)
        
        # Info adicional
        info = QLabel("Al marcar como utilizada, la garantía dejará de estar vigente.")
        info.setWordWrap(True)
        info.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #fff3cd;
                border-radius: 5px;
                color: #856404;
                font-size: 9pt;
            }
        """)
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_marcar = Boton("✓ Marcar Utilizada", "exito")
        self.boton_marcar.clicked.connect(self.marcar_utilizada)
        layout_botones.addWidget(self.boton_marcar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos"""
        self.garantia = ModuloGarantias.obtener_garantia_por_id(self.id_garantia)
        
        if self.garantia:
            texto = f"<b>Cliente:</b> {self.garantia['cliente_nombre']}<br>"
            texto += f"<b>Equipo:</b> {self.garantia['tipo_dispositivo']} {self.garantia['marca']} {self.garantia['modelo']}<br>"
            texto += f"<b>Días de garantía:</b> {self.garantia['dias_garantia']}<br>"
            texto += f"<b>Días restantes:</b> {self.garantia['dias_restantes']}"
            
            self.label_info.setText(texto)
    
    def marcar_utilizada(self):
        """Marca como utilizada"""
        motivo = self.campo_motivo.toPlainText().strip()
        
        if not motivo:
            Mensaje.advertencia("Motivo Requerido", "Debe especificar el motivo", self)
            return
        
        confirmacion = Mensaje.confirmacion(
            "Confirmar",
            "¿Está seguro que desea marcar esta garantía como UTILIZADA?",
            self
        )
        
        if not confirmacion:
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloGarantias.marcar_garantia_utilizada(
            self.id_garantia,
            motivo,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Garantía Utilizada", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)


class DialogoDetalleGarantia(QDialog):
    """Diálogo para ver detalle completo de garantía"""
    
    def __init__(self, id_garantia, parent=None):
        super().__init__(parent)
        self.id_garantia = id_garantia
        self.garantia = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle de Garantía")
        self.setMinimumSize(750, 650)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Estado visual
        self.label_estado = QLabel()
        self.label_estado.setAlignment(Qt.AlignCenter)
        self.label_estado.setStyleSheet("""
            QLabel {
                padding: 15px;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.label_estado)
        
        # Frame de datos
        frame_datos = QFrame()
        frame_datos.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout_datos = QVBoxLayout()
        layout_datos.setSpacing(15)
        
        # Cliente
        label_cliente = QLabel("<b style='color: #2563eb; font-size: 12pt;'>👤 CLIENTE</b>")
        layout_datos.addWidget(label_cliente)
        
        self.label_datos_cliente = QLabel()
        self.label_datos_cliente.setWordWrap(True)
        self.label_datos_cliente.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout_datos.addWidget(self.label_datos_cliente)
        
        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(sep1)
        
        # Equipo
        label_equipo = QLabel("<b style='color: #2563eb; font-size: 12pt;'>📱 EQUIPO</b>")
        layout_datos.addWidget(label_equipo)
        
        self.label_datos_equipo = QLabel()
        self.label_datos_equipo.setWordWrap(True)
        self.label_datos_equipo.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout_datos.addWidget(self.label_datos_equipo)
        
        # Separador
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(sep2)
        
        # Detalles garantía
        label_garantia = QLabel("<b style='color: #2563eb; font-size: 12pt;'>🛡️ DETALLES DE LA GARANTÍA</b>")
        layout_datos.addWidget(label_garantia)
        
        self.label_detalles_garantia = QLabel()
        self.label_detalles_garantia.setWordWrap(True)
        self.label_detalles_garantia.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout_datos.addWidget(self.label_detalles_garantia)
        
        frame_datos.setLayout(layout_datos)
        layout.addWidget(frame_datos)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        
        self.boton_utilizar = Boton("✓ Marcar Utilizada", "exito")
        self.boton_utilizar.clicked.connect(self.marcar_utilizada)
        layout_botones.addWidget(self.boton_utilizar)
        
        self.boton_ver_reparacion = Boton("🔧 Ver Reparación", "secundario")
        self.boton_ver_reparacion.clicked.connect(self.ver_reparacion)
        layout_botones.addWidget(self.boton_ver_reparacion)
        
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos"""
        self.garantia = ModuloGarantias.obtener_garantia_por_id(self.id_garantia)
        
        if not self.garantia:
            return
        
        # Título
        self.label_titulo.setText(f"Garantía N° {self.garantia['id_garantia']}")
        
        # Estado
        if self.garantia['estado_garantia'] == "Vigente":
            self.label_estado.setText(f"✓ GARANTÍA VIGENTE - {self.garantia['dias_restantes']} días restantes")
            self.label_estado.setStyleSheet("""
                QLabel {
                    padding: 15px;
                    background-color: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    font-size: 14pt;
                    font-weight: bold;
                    color: #155724;
                }
            """)
            self.boton_utilizar.setVisible(True)
        elif self.garantia['estado_garantia'] == "Vencida":
            self.label_estado.setText("✗ GARANTÍA VENCIDA")
            self.label_estado.setStyleSheet("""
                QLabel {
                    padding: 15px;
                    background-color: #f8f9fa;
                    border: 2px solid #6c757d;
                    border-radius: 8px;
                    font-size: 14pt;
                    font-weight: bold;
                    color: #6c757d;
                }
            """)
            self.boton_utilizar.setVisible(False)
        else:  # Utilizada
            self.label_estado.setText("✓ GARANTÍA UTILIZADA")
            self.label_estado.setStyleSheet("""
                QLabel {
                    padding: 15px;
                    background-color: #d1ecf1;
                    border: 2px solid #17a2b8;
                    border-radius: 8px;
                    font-size: 14pt;
                    font-weight: bold;
                    color: #0c5460;
                }
            """)
            self.boton_utilizar.setVisible(False)
        
        # Cliente
        texto_cliente = f"<b>Nombre:</b> {self.garantia['cliente_nombre']}<br>"
        texto_cliente += f"<b>Teléfono:</b> {self.garantia['cliente_telefono']}"
        self.label_datos_cliente.setText(texto_cliente)
        
        # Equipo
        texto_equipo = f"<b>Tipo:</b> {self.garantia['tipo_dispositivo']}<br>"
        texto_equipo += f"<b>Marca:</b> {self.garantia['marca']}<br>"
        texto_equipo += f"<b>Modelo:</b> {self.garantia['modelo']}"
        self.label_datos_equipo.setText(texto_equipo)
        
        # Detalles garantía
        try:
            fecha_inicio = datetime.fromisoformat(str(self.garantia['fecha_inicio']).replace('Z', '+00:00'))
            fecha_venc = datetime.fromisoformat(str(self.garantia['fecha_vencimiento']).replace('Z', '+00:00'))
            inicio_texto = fecha_inicio.strftime('%d/%m/%Y')
            venc_texto = fecha_venc.strftime('%d/%m/%Y')
        except:
            inicio_texto = str(self.garantia['fecha_inicio'])
            venc_texto = str(self.garantia['fecha_vencimiento'])
        
        texto_garantia = f"<b>Días de garantía:</b> {self.garantia['dias_garantia']}<br>"
        texto_garantia += f"<b>Fecha inicio:</b> {inicio_texto}<br>"
        texto_garantia += f"<b>Fecha vencimiento:</b> {venc_texto}<br>"
        
        if self.garantia['estado_garantia'] == "Vigente":
            texto_garantia += f"<b>Días restantes:</b> <span style='color: #28a745; font-size: 12pt;'>{self.garantia['dias_restantes']}</span><br>"
        
        if self.garantia.get('motivo_uso'):
            texto_garantia += f"<br><b>Motivo de uso:</b> {self.garantia['motivo_uso']}"
        
        self.label_detalles_garantia.setText(texto_garantia)
        
        # Botón reparación
        if not self.garantia.get('id_orden'):
            self.boton_ver_reparacion.setVisible(False)
    
    def marcar_utilizada(self):
        """Marcar como utilizada"""
        dialogo = DialogoMarcarGarantiaUtilizada(self.id_garantia, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_datos()
            # Notificar al padre
            if self.parent():
                self.parent().cargar_garantias()
    
    def ver_reparacion(self):
        """Ver reparación original"""
        if self.garantia and self.garantia.get('id_orden'):
            from interfaz.ventanas.ordenes import DialogoDetalleOrden
            dialogo = DialogoDetalleOrden(self.garantia['id_orden'], self)
            dialogo.exec_()

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

