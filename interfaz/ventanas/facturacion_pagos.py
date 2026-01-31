# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ COMPLETA FACTURACIÓN Y PAGOS
============================================================================
Ventana integrada completa para gestión de facturas y pagos
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QTabWidget, QDateEdit,
                             QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, ListaDesplegable,
                                              CampoTextoMultilinea)
from interfaz.estilos.estilos import Estilos
from modulos.facturacion_LOGICA import ModuloFacturacion
from modulos.pagos_LOGICA import ModuloPagos
from sistema_base.configuracion import config
from sistema_base.utilidades import formatear_dinero
from datetime import datetime, timedelta


class VentanaFacturacionPagos(QWidget):
    """Ventana integrada de facturación y pagos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título con fondo blanco
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("🧾 Facturación y Pagos", "titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_titulo.addWidget(titulo)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #2563eb;
                font-weight: bold;
            }
        """)
        
        # Pestaña Facturas
        self.tab_facturas = TabFacturas(self)
        tabs.addTab(self.tab_facturas, "📄 Facturas")
        
        # Pestaña Pagos
        self.tab_pagos = TabPagos(self)
        tabs.addTab(self.tab_pagos, "💰 Pagos")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)


class TabFacturas(QWidget):
    """Pestaña de facturas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_facturas()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Estadísticas
        self.frame_stats = QFrame()
        self.layout_stats = QHBoxLayout()
        self.layout_stats.setSpacing(15)
        self.frame_stats.setLayout(self.layout_stats)
        layout.addWidget(self.frame_stats)
        
        self.actualizar_estadisticas()
        
        # Tabla
        self.tabla = self.crear_tabla_facturas()
        layout.addWidget(self.tabla, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet(f"QWidget {{ background-color: {Estilos.COLOR_FONDO_CLARO}; padding: 20px; border: none; }}")
        
        layout = QHBoxLayout()
        layout.setSpacing(15)        
        # Botón Volver
        boton_volver = Boton("← Volver", "primario")
        boton_volver.clicked.connect(self.parent().volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar por número, cliente...")
        self.campo_busqueda.textChanged.connect(self.cargar_facturas)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Estado
        self.combo_estado = ListaDesplegable()
        self.combo_estado.addItem("Todos los estados", "")
        for estado in ModuloFacturacion.ESTADOS_COBRO:
            self.combo_estado.addItem(estado, estado)
        self.combo_estado.currentIndexChanged.connect(self.cargar_facturas)
        layout.addWidget(self.combo_estado)
        
        # Filtro de fechas
        self.check_filtro_fecha = QCheckBox("Filtrar por fecha")
        self.check_filtro_fecha.stateChanged.connect(self.toggle_filtro_fecha)
        layout.addWidget(self.check_filtro_fecha)
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setEnabled(False)
        self.fecha_desde.dateChanged.connect(self.cargar_facturas)
        layout.addWidget(self.fecha_desde)
        
        layout.addWidget(QLabel("hasta"))
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setEnabled(False)
        self.fecha_hasta.dateChanged.connect(self.cargar_facturas)
        layout.addWidget(self.fecha_hasta)
        
        # Botones
        boton_actualizar = Boton("🔄", "secundario")
        boton_actualizar.setMaximumWidth(50)
        boton_actualizar.setToolTip("Actualizar")
        boton_actualizar.clicked.connect(self.cargar_facturas)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def toggle_filtro_fecha(self):
        """Activa/desactiva filtro de fecha"""
        activo = self.check_filtro_fecha.isChecked()
        self.fecha_desde.setEnabled(activo)
        self.fecha_hasta.setEnabled(activo)
        self.cargar_facturas()
    
    def actualizar_estadisticas(self):
        """Actualiza tarjetas de estadísticas"""
        # Limpiar layout
        while self.layout_stats.count():
            child = self.layout_stats.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Obtener stats según filtros
        fecha_desde = None
        fecha_hasta = None
        
        if self.check_filtro_fecha.isChecked():
            fecha_desde = self.fecha_desde.date().toPyDate()
            fecha_hasta = self.fecha_hasta.date().toPyDate()
        
        stats = ModuloFacturacion.obtener_estadisticas_facturas(fecha_desde, fecha_hasta)
        
        # Crear tarjetas
        self.layout_stats.addWidget(self.crear_tarjeta("Total", str(stats.get('total', 0)), "#3498db"))
        self.layout_stats.addWidget(self.crear_tarjeta("Pendientes", str(stats.get('pendiente', 0)), "#ffc107"))
        self.layout_stats.addWidget(self.crear_tarjeta("Pago Parcial", str(stats.get('pago_parcial', 0)), "#17a2b8"))
        self.layout_stats.addWidget(self.crear_tarjeta("Pagadas", str(stats.get('pagado', 0)), "#28a745"))
        self.layout_stats.addWidget(self.crear_tarjeta("Monto Total", formatear_dinero(stats.get('monto_total', 0)), "#6c757d"))
        self.layout_stats.addWidget(self.crear_tarjeta("Cobrado", formatear_dinero(stats.get('monto_cobrado', 0)), "#28a745"))
        self.layout_stats.addWidget(self.crear_tarjeta("Pendiente", formatear_dinero(stats.get('monto_pendiente', 0)), "#dc3545"))
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea tarjeta de estadística"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 18px;
                min-width: 130px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            font-size: {Estilos.TAMANO_XS}pt;
            color: {Estilos.COLOR_GRIS_600};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            font-weight: 500;
            border: none;
        """)
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            font-size: 20pt;
            font-weight: 700;
            color: {color};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
            padding: 4px 0px;
        """)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_facturas(self):
        """Crea la tabla de facturas"""
        tabla = QTableWidget()
        tabla.setColumnCount(6)
        tabla.setHorizontalHeaderLabels(["Número", "Cliente", "Total", "Estado", "Fecha", "Acciones"])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        tabla.setColumnWidth(5, 280)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_facturas(self):
        """Carga facturas"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            filtro_estado = self.combo_estado.currentData()
            
            fecha_desde = None
            fecha_hasta = None
            
            if self.check_filtro_fecha.isChecked():
                fecha_desde = self.fecha_desde.date().toPyDate()
                fecha_hasta = self.fecha_hasta.date().toPyDate()
            
            facturas = ModuloFacturacion.listar_facturas(
                filtro_estado=filtro_estado,
                busqueda=busqueda,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            self.tabla.setRowCount(0)
            
            for factura in facturas:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # Número
                item_numero = QTableWidgetItem(factura['numero_factura'])
                item_numero.setFont(QFont("Courier", 10, QFont.Bold))
                self.tabla.setItem(fila, 0, item_numero)
                
                # Cliente
                self.tabla.setItem(fila, 1, QTableWidgetItem(factura['cliente_nombre']))
                
                # Total
                self.tabla.setItem(fila, 2, QTableWidgetItem(formatear_dinero(factura['total'])))
                
                # Estado
                item_estado = QTableWidgetItem(factura['estado_cobro'])
                if factura['estado_cobro'] == "Pagado":
                    item_estado.setForeground(QColor("#28a745"))
                    item_estado.setFont(QFont("Arial", 10, QFont.Bold))
                elif factura['estado_cobro'] == "Pendiente":
                    item_estado.setForeground(QColor("#ffc107"))
                elif factura['estado_cobro'] == "Pago parcial":
                    item_estado.setForeground(QColor("#17a2b8"))
                elif factura['estado_cobro'] == "Incobrable":
                    item_estado.setForeground(QColor("#dc3545"))
                    item_estado.setFont(QFont("Arial", 10, QFont.Bold))
                self.tabla.setItem(fila, 3, item_estado)
                
                # Fecha
                try:
                    fecha = datetime.fromisoformat(str(factura['fecha_emision']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y')
                except:
                    fecha_texto = str(factura['fecha_emision'])
                self.tabla.setItem(fila, 4, QTableWidgetItem(fecha_texto))
                
                # Acciones
                widget = self.crear_botones_acciones(factura)
                self.tabla.setCellWidget(fila, 5, widget)
            
            # Actualizar stats
            self.actualizar_estadisticas()
        
        except Exception as e:
            config.guardar_log(f"Error al cargar facturas: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar facturas: {str(e)}", self)
    
    def crear_botones_acciones(self, factura):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver
        boton_ver = Boton("👁️", "primario")
        boton_ver.setToolTip("Ver detalle")
        boton_ver.setMaximumWidth(50)
        boton_ver.clicked.connect(lambda: self.ver_factura(factura['id_factura']))
        layout.addWidget(boton_ver)
        
        # Botón Pagar (si no está pagada ni incobrable)
        if factura['estado_cobro'] not in ["Pagado", "Incobrable"]:
            boton_pagar = Boton("💰", "exito")
            boton_pagar.setToolTip("Registrar pago")
            boton_pagar.setMaximumWidth(50)
            boton_pagar.clicked.connect(lambda: self.registrar_pago(factura['id_factura']))
            layout.addWidget(boton_pagar)
        
        # Botón Marcar Incobrable (si no está pagada ni incobrable)
        if factura['estado_cobro'] not in ["Pagado", "Incobrable"]:
            boton_incobrable = Boton("❌", "peligro")
            boton_incobrable.setToolTip("Marcar como incobrable")
            boton_incobrable.setMaximumWidth(50)
            boton_incobrable.clicked.connect(lambda: self.marcar_incobrable(factura['id_factura']))
            layout.addWidget(boton_incobrable)
        
        # Botón Imprimir
        boton_imprimir = Boton("🖨️", "secundario")
        boton_imprimir.setToolTip("Imprimir/Exportar")
        boton_imprimir.setMaximumWidth(50)
        boton_imprimir.clicked.connect(lambda: self.imprimir_factura(factura['id_factura']))
        layout.addWidget(boton_imprimir)
        
        widget.setLayout(layout)
        return widget
    
    def ver_factura(self, id_factura):
        """Ver detalle de factura"""
        dialogo = DialogoDetalleFactura(id_factura, self)
        dialogo.exec_()
        self.cargar_facturas()
    
    def registrar_pago(self, id_factura):
        """Registrar pago"""
        dialogo = DialogoRegistrarPago(id_factura, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_facturas()
    
    def marcar_incobrable(self, id_factura):
        """Marcar como incobrable"""
        dialogo = DialogoMarcarIncobrable(id_factura, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_facturas()
    
    def imprimir_factura(self, id_factura):
        """Imprimir/Exportar factura"""
        Mensaje.informacion("Funcionalidad Próximamente", 
                          "La exportación a PDF estará disponible próximamente.", self)


class TabPagos(QWidget):
    """Pestaña de pagos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_pagos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Stats
        self.frame_stats = QFrame()
        self.layout_stats = QHBoxLayout()
        self.layout_stats.setSpacing(15)
        self.frame_stats.setLayout(self.layout_stats)
        layout.addWidget(self.frame_stats)
        
        self.actualizar_estadisticas()
        
        # Tabla
        self.tabla = self.crear_tabla_pagos()
        layout.addWidget(self.tabla, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        
        layout = QHBoxLayout()
        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar...")
        self.campo_busqueda.textChanged.connect(self.cargar_pagos)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Método
        self.combo_metodo = ListaDesplegable()
        self.combo_metodo.addItem("Todos los métodos", "")
        for metodo in ModuloPagos.METODOS_PAGO:
            self.combo_metodo.addItem(metodo, metodo)
        self.combo_metodo.currentIndexChanged.connect(self.cargar_pagos)
        layout.addWidget(self.combo_metodo)
        
        # Filtro de fechas
        self.check_filtro_fecha = QCheckBox("Filtrar por fecha")
        self.check_filtro_fecha.stateChanged.connect(self.toggle_filtro_fecha)
        layout.addWidget(self.check_filtro_fecha)
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setEnabled(False)
        self.fecha_desde.dateChanged.connect(self.cargar_pagos)
        layout.addWidget(self.fecha_desde)
        
        layout.addWidget(QLabel("hasta"))
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setEnabled(False)
        self.fecha_hasta.dateChanged.connect(self.cargar_pagos)
        layout.addWidget(self.fecha_hasta)
        
        # Botón actualizar
        boton_actualizar = Boton("🔄", "secundario")
        boton_actualizar.setMaximumWidth(50)
        boton_actualizar.setToolTip("Actualizar")
        boton_actualizar.clicked.connect(self.cargar_pagos)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def toggle_filtro_fecha(self):
        """Activa/desactiva filtro de fecha"""
        activo = self.check_filtro_fecha.isChecked()
        self.fecha_desde.setEnabled(activo)
        self.fecha_hasta.setEnabled(activo)
        self.cargar_pagos()
    
    def actualizar_estadisticas(self):
        """Actualiza estadísticas"""
        # Limpiar layout
        while self.layout_stats.count():
            child = self.layout_stats.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        fecha_desde = None
        fecha_hasta = None
        
        if self.check_filtro_fecha.isChecked():
            fecha_desde = self.fecha_desde.date().toPyDate()
            fecha_hasta = self.fecha_hasta.date().toPyDate()
        
        stats = ModuloPagos.obtener_estadisticas_pagos(fecha_desde, fecha_hasta)
        
        # Tarjetas
        self.layout_stats.addWidget(self.crear_tarjeta("Total Pagos", str(stats.get('total_pagos', 0)), "#3498db"))
        self.layout_stats.addWidget(self.crear_tarjeta("Monto Total", formatear_dinero(stats.get('monto_total', 0)), "#28a745"))
        self.layout_stats.addWidget(self.crear_tarjeta("Efectivo", formatear_dinero(stats.get('efectivo', 0)), "#6c757d"))
        self.layout_stats.addWidget(self.crear_tarjeta("Transferencia", formatear_dinero(stats.get('transferencia', 0)), "#17a2b8"))
        self.layout_stats.addWidget(self.crear_tarjeta("Mercado Pago", formatear_dinero(stats.get('mercado_pago', 0)), "#0077cc"))
        self.layout_stats.addWidget(self.crear_tarjeta("Tarjetas", formatear_dinero(stats.get('débito', 0) + stats.get('crédito_1_pago', 0)), "#dc3545"))
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea tarjeta"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 14px;
                min-width: 130px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("font-size: 9pt; color: #6c757d; border: none;")
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {color}; border: none; padding: 4px 0px;")
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_pagos(self):
        """Crea tabla de pagos"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(["Fecha/Hora", "Factura", "Cliente", "Monto", "Método", "Referencia", "Usuario"])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_pagos(self):
        """Carga pagos"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            metodo = self.combo_metodo.currentData()
            
            fecha_desde = None
            fecha_hasta = None
            
            if self.check_filtro_fecha.isChecked():
                fecha_desde = self.fecha_desde.date().toPyDate()
                fecha_hasta = self.fecha_hasta.date().toPyDate()
            
            pagos = ModuloPagos.listar_pagos(
                busqueda=busqueda,
                metodo_pago=metodo,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            self.tabla.setRowCount(0)
            
            for pago in pagos:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # Fecha
                try:
                    fecha = datetime.fromisoformat(str(pago['fecha_hora_pago']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    fecha_texto = str(pago['fecha_hora_pago'])
                self.tabla.setItem(fila, 0, QTableWidgetItem(fecha_texto))
                
                # Factura
                item_factura = QTableWidgetItem(pago['numero_factura'])
                item_factura.setFont(QFont("Courier", 10, QFont.Bold))
                self.tabla.setItem(fila, 1, item_factura)
                
                # Cliente
                self.tabla.setItem(fila, 2, QTableWidgetItem(pago['cliente_nombre']))
                
                # Monto
                item_monto = QTableWidgetItem(formatear_dinero(pago['monto']))
                item_monto.setForeground(QColor("#28a745"))
                item_monto.setFont(QFont("Arial", 10, QFont.Bold))
                self.tabla.setItem(fila, 3, item_monto)
                
                # Método
                self.tabla.setItem(fila, 4, QTableWidgetItem(pago['metodo_pago']))
                
                # Referencia
                self.tabla.setItem(fila, 5, QTableWidgetItem(pago['referencia'] if pago['referencia'] else "-"))
                
                # Usuario
                self.tabla.setItem(fila, 6, QTableWidgetItem(pago['usuario_nombre'] if pago['usuario_nombre'] else "-"))
            
            # Actualizar stats
            self.actualizar_estadisticas()
        
        except Exception as e:
            config.guardar_log(f"Error al cargar pagos: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar pagos: {str(e)}", self)


class DialogoRegistrarPago(QDialog):
    """Diálogo para registrar pago"""
    
    def __init__(self, id_factura, parent=None):
        super().__init__(parent)
        self.id_factura = id_factura
        self.factura = None
        self.pendiente = 0
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Registrar Pago")
        self.setFixedSize(580, 520)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("💰 Registrar Pago", "titulo")
        layout.addWidget(titulo)
        
        # Info factura
        self.label_factura = QLabel()
        self.label_factura.setWordWrap(True)
        self.label_factura.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.label_factura)
        
        # Monto
        label_monto = Etiqueta("Monto a Pagar: *")
        layout.addWidget(label_monto)
        
        layout_monto = QHBoxLayout()
        layout_monto.addWidget(QLabel("$"))
        self.campo_monto = CampoTexto("0.00")
        self.campo_monto.setStyleSheet("QLineEdit { font-size: 14pt; font-weight: bold; }")
        layout_monto.addWidget(self.campo_monto, 1)
        
        self.boton_total = Boton("Poner Total", "secundario")
        self.boton_total.setMaximumWidth(100)
        self.boton_total.clicked.connect(self.poner_total_pendiente)
        layout_monto.addWidget(self.boton_total)
        
        layout.addLayout(layout_monto)
        
        # Método de pago
        label_metodo = Etiqueta("Método de Pago: *")
        layout.addWidget(label_metodo)
        
        self.combo_metodo = ListaDesplegable()
        for metodo in ModuloPagos.METODOS_PAGO:
            self.combo_metodo.addItem(metodo, metodo)
        layout.addWidget(self.combo_metodo)
        
        # Referencia/Comprobante
        label_ref = Etiqueta("Referencia/Comprobante:")
        layout.addWidget(label_ref)
        
        self.campo_referencia = CampoTexto("N° de comprobante, operación...")
        layout.addWidget(self.campo_referencia)
        
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
        
        self.boton_registrar = Boton("💰 Registrar Pago", "exito")
        self.boton_registrar.clicked.connect(self.registrar_pago)
        layout_botones.addWidget(self.boton_registrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos de la factura"""
        self.factura = ModuloFacturacion.obtener_factura_por_id(self.id_factura)
        
        if self.factura:
            total_pagado = ModuloPagos.obtener_total_pagado(self.id_factura)
            self.pendiente = self.factura['total'] - total_pagado
            
            texto = f"<b>Factura:</b> {self.factura['numero_factura']}<br>"
            texto += f"<b>Cliente:</b> {self.factura['cliente_nombre']}<br><br>"
            texto += f"<b>Total factura:</b> {formatear_dinero(self.factura['total'])}<br>"
            texto += f"<b>Ya pagado:</b> {formatear_dinero(total_pagado)}<br>"
            texto += f"<b>Pendiente:</b> <span style='color: #dc3545; font-size: 14pt; font-weight: bold;'>{formatear_dinero(self.pendiente)}</span>"
            
            self.label_factura.setText(texto)
            self.campo_monto.setText(str(self.pendiente))
    
    def poner_total_pendiente(self):
        """Pone el monto total pendiente"""
        self.campo_monto.setText(str(self.pendiente))
        self.campo_monto.selectAll()
        self.campo_monto.setFocus()
    
    def registrar_pago(self):
        """Registra el pago"""
        try:
            monto = float(self.campo_monto.text().strip().replace(",", "."))
            if monto <= 0:
                raise ValueError()
        except:
            self.label_error.setText("El monto debe ser un número válido mayor a cero")
            self.label_error.setVisible(True)
            return
        
        self.boton_registrar.setEnabled(False)
        self.boton_registrar.setText("Registrando...")
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_pago = ModuloPagos.registrar_pago(
            self.id_factura,
            monto,
            self.combo_metodo.currentData(),
            self.campo_referencia.text().strip(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Pago Registrado", mensaje, self)
            self.accept()
        else:
            self.label_error.setText(mensaje)
            self.label_error.setVisible(True)
            self.boton_registrar.setEnabled(True)
            self.boton_registrar.setText("💰 Registrar Pago")


class DialogoMarcarIncobrable(QDialog):
    """Diálogo para marcar factura como incobrable"""
    
    def __init__(self, id_factura, parent=None):
        super().__init__(parent)
        self.id_factura = id_factura
        self.factura = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("⚠️ Marcar como Incobrable")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("⚠️ Marcar Factura como Incobrable", "titulo")
        titulo.setStyleSheet("QLabel { color: #dc3545; }")
        layout.addWidget(titulo)
        
        # Advertencia GRANDE
        advertencia = QLabel("⚠️ ATENCIÓN: ESTA ACCIÓN ES IRREVERSIBLE ⚠️")
        advertencia.setWordWrap(True)
        advertencia.setAlignment(Qt.AlignCenter)
        advertencia.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #f8d7da;
                border: 3px solid #dc3545;
                border-radius: 10px;
                color: #721c24;
                font-size: 13pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(advertencia)
        
        # Info adicional
        info = QLabel("• Se marcará al cliente con deuda incobrable\n"
                     "• Se registrará en auditoría como acción crítica\n"
                     "• NO se podrá revertir esta acción")
        info.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #fff3cd;
                border-radius: 5px;
                color: #856404;
                font-size: 10pt;
            }
        """)
        layout.addWidget(info)
        
        # Info factura
        self.label_factura = QLabel()
        self.label_factura.setWordWrap(True)
        self.label_factura.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.label_factura)
        
        # Motivo (OBLIGATORIO)
        label_motivo = Etiqueta("Motivo (OBLIGATORIO): *")
        layout.addWidget(label_motivo)
        
        self.campo_motivo = CampoTextoMultilinea("Explique detalladamente por qué esta factura es incobrable...")
        self.campo_motivo.setMaximumHeight(100)
        layout.addWidget(self.campo_motivo)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_marcar = Boton("❌ CONFIRMAR: Marcar Incobrable", "peligro")
        self.boton_marcar.clicked.connect(self.marcar_incobrable)
        layout_botones.addWidget(self.boton_marcar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos"""
        self.factura = ModuloFacturacion.obtener_factura_por_id(self.id_factura)
        
        if self.factura:
            total_pagado = ModuloPagos.obtener_total_pagado(self.id_factura)
            pendiente = self.factura['total'] - total_pagado
            
            texto = f"<b>Factura:</b> {self.factura['numero_factura']}<br>"
            texto += f"<b>Cliente:</b> {self.factura['cliente_nombre']}<br>"
            texto += f"<b>Monto pendiente:</b> <span style='color: #dc3545; font-size: 13pt; font-weight: bold;'>{formatear_dinero(pendiente)}</span>"
            
            self.label_factura.setText(texto)
    
    def marcar_incobrable(self):
        """Marca como incobrable"""
        motivo = self.campo_motivo.toPlainText().strip()
        
        if not motivo or len(motivo) < 10:
            Mensaje.advertencia("Motivo Requerido", 
                              "Debe especificar un motivo detallado (mínimo 10 caracteres)", self)
            return
        
        # Confirmación DOBLE
        confirmacion1 = Mensaje.confirmacion(
            "⚠️ PRIMERA CONFIRMACIÓN",
            f"¿Está SEGURO que desea marcar la factura {self.factura['numero_factura']} como INCOBRABLE?\n\n" +
            "Esta acción es IRREVERSIBLE.",
            self
        )
        
        if not confirmacion1:
            return
        
        confirmacion2 = Mensaje.confirmacion(
            "⚠️ SEGUNDA CONFIRMACIÓN",
            "ÚLTIMA ADVERTENCIA:\n\n" +
            "Al confirmar, se marcará al cliente con deuda incobrable.\n\n" +
            "¿Desea CONTINUAR?",
            self
        )
        
        if not confirmacion2:
            return
        
        self.boton_marcar.setEnabled(False)
        self.boton_marcar.setText("Marcando...")
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloFacturacion.marcar_incobrable(
            self.id_factura,
            motivo,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Factura Marcada", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)
            self.boton_marcar.setEnabled(True)
            self.boton_marcar.setText("❌ CONFIRMAR: Marcar Incobrable")


class DialogoDetalleFactura(QDialog):
    """Diálogo para ver detalle completo de factura"""
    
    def __init__(self, id_factura, parent=None):
        super().__init__(parent)
        self.id_factura = id_factura
        self.factura = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle de Factura")
        self.setMinimumSize(800, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Info general
        self.label_info = QLabel()
        self.label_info.setWordWrap(True)
        self.label_info.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.label_info)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: #dee2e6; max-height: 2px;")
        layout.addWidget(separador)
        
        # Sección de pagos
        label_pagos = Etiqueta("💰 Pagos Registrados:", "subtitulo")
        layout.addWidget(label_pagos)
        
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setColumnCount(5)
        self.tabla_pagos.setHorizontalHeaderLabels(["Fecha/Hora", "Monto", "Método", "Referencia", "Usuario"])
        self.tabla_pagos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_pagos.verticalHeader().setVisible(False)
        self.tabla_pagos.setMaximumHeight(300)
        self.tabla_pagos.setStyleSheet(Estilos.tabla())
        
        header = self.tabla_pagos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.tabla_pagos)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        
        self.boton_pagar = Boton("💰 Registrar Pago", "exito")
        self.boton_pagar.clicked.connect(self.registrar_pago)
        layout_botones.addWidget(self.boton_pagar)
        
        boton_ver_orden = Boton("📋 Ver Orden", "secundario")
        boton_ver_orden.clicked.connect(self.ver_orden)
        layout_botones.addWidget(boton_ver_orden)
        
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos de la factura"""
        self.factura = ModuloFacturacion.obtener_factura_por_id(self.id_factura)
        
        if not self.factura:
            return
        
        # Título
        self.label_titulo.setText(f"Factura {self.factura['numero_factura']}")
        
        # Info general
        total_pagado = ModuloPagos.obtener_total_pagado(self.id_factura)
        pendiente = self.factura['total'] - total_pagado
        
        try:
            fecha = datetime.fromisoformat(str(self.factura['fecha_emision']).replace('Z', '+00:00'))
            fecha_texto = fecha.strftime('%d/%m/%Y')
        except:
            fecha_texto = str(self.factura['fecha_emision'])
        
        # Estado con color
        estado_color = "#28a745" if self.factura['estado_cobro'] == "Pagado" else "#dc3545"
        
        texto = f"<b>Cliente:</b> {self.factura['cliente_nombre']}<br>"
        texto += f"<b>Teléfono:</b> {self.factura['cliente_telefono']}<br>"
        texto += f"<b>Fecha emisión:</b> {fecha_texto}<br><br>"
        texto += f"<b>Total factura:</b> {formatear_dinero(self.factura['total'])}<br>"
        texto += f"<b>Pagado:</b> {formatear_dinero(total_pagado)}<br>"
        texto += f"<b>Pendiente:</b> <span style='color: {estado_color}; font-size: 14pt; font-weight: bold;'>{formatear_dinero(pendiente)}</span><br><br>"
        texto += f"<b>Estado:</b> <span style='color: {estado_color}; font-weight: bold; font-size: 12pt;'>{self.factura['estado_cobro']}</span>"
        
        self.label_info.setText(texto)
        
        # Mostrar/ocultar botón pagar
        if self.factura['estado_cobro'] in ["Pagado", "Incobrable"]:
            self.boton_pagar.setVisible(False)
        
        # Cargar tabla de pagos
        self.cargar_pagos()
    
    def cargar_pagos(self):
        """Carga los pagos de la factura"""
        pagos = ModuloPagos.obtener_pagos_de_factura(self.id_factura)
        self.tabla_pagos.setRowCount(0)
        
        for pago in pagos:
            fila = self.tabla_pagos.rowCount()
            self.tabla_pagos.insertRow(fila)
            
            # Fecha
            try:
                fecha = datetime.fromisoformat(str(pago['fecha_hora_pago']).replace('Z', '+00:00'))
                fecha_texto = fecha.strftime('%d/%m/%Y %H:%M')
            except:
                fecha_texto = str(pago['fecha_hora_pago'])
            self.tabla_pagos.setItem(fila, 0, QTableWidgetItem(fecha_texto))
            
            # Monto
            item_monto = QTableWidgetItem(formatear_dinero(pago['monto']))
            item_monto.setForeground(QColor("#28a745"))
            item_monto.setFont(QFont("Arial", 10, QFont.Bold))
            self.tabla_pagos.setItem(fila, 1, item_monto)
            
            # Método
            self.tabla_pagos.setItem(fila, 2, QTableWidgetItem(pago['metodo_pago']))
            
            # Referencia
            self.tabla_pagos.setItem(fila, 3, QTableWidgetItem(pago['referencia'] if pago['referencia'] else "-"))
            
            # Usuario
            self.tabla_pagos.setItem(fila, 4, QTableWidgetItem(pago['usuario_nombre'] if pago['usuario_nombre'] else "-"))
    
    def registrar_pago(self):
        """Abre diálogo para registrar pago"""
        dialogo = DialogoRegistrarPago(self.id_factura, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_datos()
            # Notificar al padre
            if self.parent():
                self.parent().cargar_facturas()
    
    def ver_orden(self):
        """Ver orden asociada"""
        if self.factura and self.factura.get('id_orden'):
            from interfaz.ventanas.ordenes import DialogoDetalleOrden
            dialogo = DialogoDetalleOrden(self.factura['id_orden'], self)
            dialogo.exec_()
        else:
            Mensaje.informacion("Sin Orden", "Esta factura no tiene una orden asociada", self)
