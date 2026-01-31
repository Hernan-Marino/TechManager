# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ COMPLETA MÓDULO DE REMITOS
============================================================================
Ventana para visualizar, buscar y reimprimir remitos de ingreso
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QDateEdit, QCheckBox,
                             QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, ListaDesplegable)
from interfaz.estilos.estilos import Estilos
from modulos.remitos import ModuloRemitos
from modulos.equipos import ModuloEquipos
from sistema_base.configuracion import config
from datetime import datetime


class VentanaRemitos(QWidget):
    """Ventana principal de gestión de remitos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_remitos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("📋 Gestión de Remitos", "titulo")
        layout_titulo.addWidget(titulo)
        
        layout_titulo.addStretch()
        
        # Info
        label_info = QLabel("Los remitos se generan automáticamente al ingresar equipos")
        label_info.setStyleSheet("color: #6c757d; font-style: italic;")
        layout_titulo.addWidget(label_info)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tarjetas estadísticas
        tarjetas = self.crear_tarjetas_estadisticas()
        layout.addWidget(tarjetas)
        
        # Tabla
        self.tabla = self.crear_tabla_remitos()
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
        self.campo_busqueda = CampoTexto("Buscar por número, cliente, equipo...")
        self.campo_busqueda.textChanged.connect(self.buscar_remitos)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Filtro de fechas
        self.check_filtro_fecha = QCheckBox("Filtrar por fecha")
        self.check_filtro_fecha.stateChanged.connect(self.toggle_filtro_fecha)
        layout.addWidget(self.check_filtro_fecha)
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setEnabled(False)
        self.fecha_desde.dateChanged.connect(self.cargar_remitos)
        layout.addWidget(self.fecha_desde)
        
        layout.addWidget(QLabel("hasta"))
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setEnabled(False)
        self.fecha_hasta.dateChanged.connect(self.cargar_remitos)
        layout.addWidget(self.fecha_hasta)
        
        # Checkbox solo no retirados
        self.check_no_retirados = QCheckBox("Solo equipos no retirados")
        self.check_no_retirados.stateChanged.connect(self.cargar_remitos)
        layout.addWidget(self.check_no_retirados)
        
        # Botones
        boton_actualizar = Boton("🔄 Actualizar", "secundario")
        boton_actualizar.clicked.connect(self.cargar_remitos)
        layout.addWidget(boton_actualizar)
        
        boton_exportar = Boton("📊 Exportar", "neutro")
        boton_exportar.clicked.connect(self.exportar_remitos)
        layout.addWidget(boton_exportar)
        
        barra.setLayout(layout)
        return barra
    
    def toggle_filtro_fecha(self):
        """Activa/desactiva filtro de fecha"""
        activo = self.check_filtro_fecha.isChecked()
        self.fecha_desde.setEnabled(activo)
        self.fecha_hasta.setEnabled(activo)
        self.cargar_remitos()
    
    def crear_tarjetas_estadisticas(self):
        """Crea tarjetas de estadísticas"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Obtener estadísticas
        fecha_desde = None
        fecha_hasta = None
        
        if self.check_filtro_fecha.isChecked():
            fecha_desde = self.fecha_desde.date().toPyDate()
            fecha_hasta = self.fecha_hasta.date().toPyDate()
        
        stats = ModuloRemitos.obtener_estadisticas_remitos(fecha_desde, fecha_hasta)
        
        # Total remitos
        tarjeta1 = self.crear_tarjeta("Total Remitos", str(stats.get('total', 0)), "#3498db")
        layout.addWidget(tarjeta1)
        
        # Este mes
        tarjeta2 = self.crear_tarjeta("Este Mes", str(stats.get('mes_actual', 0)), "#17a2b8")
        layout.addWidget(tarjeta2)
        
        # Equipos no retirados
        tarjeta3 = self.crear_tarjeta("No Retirados", str(stats.get('no_retirados', 0)), "#ffc107")
        layout.addWidget(tarjeta3)
        
        # Retirados
        tarjeta4 = self.crear_tarjeta("Retirados", str(stats.get('retirados', 0)), "#28a745")
        layout.addWidget(tarjeta4)
        
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
    
    def crear_tabla_remitos(self):
        """Crea la tabla de remitos"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "Número Remito", "Fecha", "Cliente", "Equipo", "Estado Equipo", "Retirado", "Acciones"
        ])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        tabla.setColumnWidth(6, 200)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_remitos(self):
        """Carga los remitos"""
        try:
            # Obtener filtros
            busqueda = self.campo_busqueda.text().strip()
            
            fecha_desde = None
            fecha_hasta = None
            if self.check_filtro_fecha.isChecked():
                fecha_desde = self.fecha_desde.date().toPyDate()
                fecha_hasta = self.fecha_hasta.date().toPyDate()
            
            solo_no_retirados = self.check_no_retirados.isChecked()
            
            # Obtener remitos
            remitos = ModuloRemitos.listar_remitos(
                busqueda=busqueda,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                solo_no_retirados=solo_no_retirados
            )
            
            # Limpiar tabla
            self.tabla.setRowCount(0)
            
            for remito in remitos:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # Número remito
                item_numero = QTableWidgetItem(remito['numero_remito'])
                item_numero.setFont(QFont("Courier", 10, QFont.Bold))
                self.tabla.setItem(fila, 0, item_numero)
                
                # Fecha
                try:
                    fecha = datetime.fromisoformat(str(remito['fecha_ingreso']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    fecha_texto = str(remito['fecha_ingreso'])
                self.tabla.setItem(fila, 1, QTableWidgetItem(fecha_texto))
                
                # Cliente
                self.tabla.setItem(fila, 2, QTableWidgetItem(remito['cliente_nombre']))
                
                # Equipo
                equipo_texto = f"{remito['tipo_dispositivo']} {remito['marca']} {remito['modelo']}"
                self.tabla.setItem(fila, 3, QTableWidgetItem(equipo_texto))
                
                # Estado equipo
                item_estado = QTableWidgetItem(remito['estado_actual'])
                if remito['estado_actual'] == "Retirado":
                    item_estado.setForeground(QColor("#28a745"))
                elif remito['estado_actual'] in ["En revisión", "En reparación"]:
                    item_estado.setForeground(QColor("#ffc107"))
                elif remito['estado_actual'] == "Listo para retirar":
                    item_estado.setForeground(QColor("#17a2b8"))
                self.tabla.setItem(fila, 4, item_estado)
                
                # Retirado
                if remito['estado_actual'] == "Retirado":
                    item_retirado = QTableWidgetItem("✓ SÍ")
                    item_retirado.setForeground(QColor("#28a745"))
                    item_retirado.setFont(QFont("Arial", 10, QFont.Bold))
                else:
                    item_retirado = QTableWidgetItem("✗ NO")
                    item_retirado.setForeground(QColor("#6c757d"))
                self.tabla.setItem(fila, 5, item_retirado)
                
                # Acciones
                widget_acciones = self.crear_botones_acciones(remito)
                self.tabla.setCellWidget(fila, 6, widget_acciones)
            
            # Actualizar estadísticas
            self.actualizar_estadisticas()
        
        except Exception as e:
            config.guardar_log(f"Error al cargar remitos: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar remitos: {str(e)}", self)
    
    def actualizar_estadisticas(self):
        """Actualiza las tarjetas de estadísticas"""
        # Limpiar y recrear tarjetas
        tarjetas = self.crear_tarjetas_estadisticas()
        # Esto actualizará las tarjetas existentes
    
    def crear_botones_acciones(self, remito):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver
        boton_ver = Boton("👁️", "primario")
        boton_ver.setToolTip("Ver detalle del remito")
        boton_ver.setMaximumWidth(50)
        boton_ver.clicked.connect(lambda: self.ver_detalle(remito['id_remito']))
        layout.addWidget(boton_ver)
        
        # Botón Reimprimir
        boton_imprimir = Boton("🖨️", "secundario")
        boton_imprimir.setToolTip("Reimprimir remito")
        boton_imprimir.setMaximumWidth(50)
        boton_imprimir.clicked.connect(lambda: self.reimprimir_remito(remito['id_remito']))
        layout.addWidget(boton_imprimir)
        
        # Botón Ver Equipo
        boton_equipo = Boton("📦", "neutro")
        boton_equipo.setToolTip("Ver equipo asociado")
        boton_equipo.setMaximumWidth(50)
        boton_equipo.clicked.connect(lambda: self.ver_equipo(remito['id_equipo']))
        layout.addWidget(boton_equipo)
        
        widget.setLayout(layout)
        return widget
    
    def buscar_remitos(self):
        """Busca remitos"""
        self.cargar_remitos()
    
    def ver_detalle(self, id_remito):
        """Ver detalle del remito"""
        dialogo = DialogoDetalleRemito(id_remito, self)
        dialogo.exec_()
    
    def reimprimir_remito(self, id_remito):
        """Reimprimir remito"""
        dialogo = DialogoReimprimirRemito(id_remito, self)
        dialogo.exec_()
    
    def ver_equipo(self, id_equipo):
        """Ver equipo asociado"""
        # Abrir ventana de equipos con el equipo seleccionado
        from interfaz.ventanas.equipos import DialogoDetalleEquipo
        dialogo = DialogoDetalleEquipo(id_equipo, self)
        dialogo.exec_()
    
    def exportar_remitos(self):
        """Exportar remitos a CSV"""
        Mensaje.informacion(
            "Exportar Remitos",
            "La funcionalidad de exportación estará disponible próximamente.",
            self
        )


class DialogoDetalleRemito(QDialog):
    """Diálogo para ver detalle completo del remito"""
    
    def __init__(self, id_remito, parent=None):
        super().__init__(parent)
        self.id_remito = id_remito
        self.remito = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle del Remito")
        self.setMinimumSize(800, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Frame principal con todos los datos
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
        
        # Datos del cliente
        label_cliente = QLabel("<b style='color: #2563eb; font-size: 14pt;'>📋 DATOS DEL CLIENTE</b>")
        layout_datos.addWidget(label_cliente)
        
        self.label_datos_cliente = QLabel()
        self.label_datos_cliente.setWordWrap(True)
        self.label_datos_cliente.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_datos_cliente)
        
        # Separador
        separador1 = QFrame()
        separador1.setFrameShape(QFrame.HLine)
        separador1.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(separador1)
        
        # Datos del equipo
        label_equipo = QLabel("<b style='color: #2563eb; font-size: 14pt;'>📱 DATOS DEL EQUIPO</b>")
        layout_datos.addWidget(label_equipo)
        
        self.label_datos_equipo = QLabel()
        self.label_datos_equipo.setWordWrap(True)
        self.label_datos_equipo.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_datos_equipo)
        
        # Separador
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.HLine)
        separador2.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(separador2)
        
        # Detalles del ingreso
        label_ingreso = QLabel("<b style='color: #2563eb; font-size: 14pt;'>📝 DETALLES DEL INGRESO</b>")
        layout_datos.addWidget(label_ingreso)
        
        self.label_detalles = QLabel()
        self.label_detalles.setWordWrap(True)
        self.label_detalles.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_detalles)
        
        # Separador
        separador3 = QFrame()
        separador3.setFrameShape(QFrame.HLine)
        separador3.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(separador3)
        
        # Estado actual
        label_estado = QLabel("<b style='color: #2563eb; font-size: 14pt;'>📊 ESTADO ACTUAL</b>")
        layout_datos.addWidget(label_estado)
        
        self.label_estado_actual = QLabel()
        self.label_estado_actual.setWordWrap(True)
        self.label_estado_actual.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #d4edda;
                border: 1px solid #28a745;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        layout_datos.addWidget(self.label_estado_actual)
        
        frame_datos.setLayout(layout_datos)
        layout.addWidget(frame_datos)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        
        boton_reimprimir = Boton("🖨️ Reimprimir Remito", "primario")
        boton_reimprimir.clicked.connect(self.reimprimir)
        layout_botones.addWidget(boton_reimprimir)
        
        boton_ver_equipo = Boton("📦 Ver Equipo", "secundario")
        boton_ver_equipo.clicked.connect(self.ver_equipo)
        layout_botones.addWidget(boton_ver_equipo)
        
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los datos del remito"""
        try:
            self.remito = ModuloRemitos.obtener_remito_por_id(self.id_remito)
            
            if not self.remito:
                Mensaje.error("Error", "Remito no encontrado", self)
                self.reject()
                return
            
            # Título
            self.label_titulo.setText(f"Remito: {self.remito['numero_remito']}")
            
            # Datos del cliente
            texto_cliente = f"<b>Nombre:</b> {self.remito['cliente_nombre']}<br>"
            texto_cliente += f"<b>Teléfono:</b> {self.remito['cliente_telefono']}<br>"
            if self.remito.get('cliente_direccion'):
                texto_cliente += f"<b>Dirección:</b> {self.remito['cliente_direccion']}"
            self.label_datos_cliente.setText(texto_cliente)
            
            # Datos del equipo
            texto_equipo = f"<b>Tipo:</b> {self.remito['tipo_dispositivo']}<br>"
            texto_equipo += f"<b>Marca:</b> {self.remito['marca']}<br>"
            texto_equipo += f"<b>Modelo:</b> {self.remito['modelo']}<br>"
            if self.remito.get('identificador'):
                texto_equipo += f"<b>IMEI/Serie:</b> {self.remito['identificador']}<br>"
            if self.remito.get('accesorios'):
                texto_equipo += f"<b>Accesorios:</b> {self.remito['accesorios']}<br>"
            if self.remito.get('patron_bloqueo'):
                texto_equipo += f"<b>Patrón/PIN:</b> {self.remito['patron_bloqueo']}"
            self.label_datos_equipo.setText(texto_equipo)
            
            # Detalles del ingreso
            try:
                fecha = datetime.fromisoformat(str(self.remito['fecha_ingreso']).replace('Z', '+00:00'))
                fecha_texto = fecha.strftime('%d/%m/%Y a las %H:%M')
            except:
                fecha_texto = str(self.remito['fecha_ingreso'])
            
            texto_detalles = f"<b>Fecha de ingreso:</b> {fecha_texto}<br>"
            texto_detalles += f"<b>Falla reportada:</b><br>{self.remito['falla_reportada']}<br>"
            if self.remito.get('observaciones_ingreso'):
                texto_detalles += f"<br><b>Observaciones:</b><br>{self.remito['observaciones_ingreso']}"
            self.label_detalles.setText(texto_detalles)
            
            # Estado actual
            texto_estado = f"Estado: {self.remito['estado_actual']}"
            if self.remito['estado_actual'] == "Retirado":
                self.label_estado_actual.setStyleSheet("""
                    QLabel {
                        padding: 15px;
                        background-color: #d4edda;
                        border: 2px solid #28a745;
                        border-radius: 5px;
                        font-size: 13pt;
                        font-weight: bold;
                        color: #155724;
                    }
                """)
                texto_estado = "✓ EQUIPO RETIRADO"
            elif self.remito['estado_actual'] == "Listo para retirar":
                self.label_estado_actual.setStyleSheet("""
                    QLabel {
                        padding: 15px;
                        background-color: #d1ecf1;
                        border: 2px solid #17a2b8;
                        border-radius: 5px;
                        font-size: 13pt;
                        font-weight: bold;
                        color: #0c5460;
                    }
                """)
                texto_estado = "✓ LISTO PARA RETIRAR"
            else:
                self.label_estado_actual.setStyleSheet("""
                    QLabel {
                        padding: 15px;
                        background-color: #fff3cd;
                        border: 2px solid #ffc107;
                        border-radius: 5px;
                        font-size: 13pt;
                        font-weight: bold;
                        color: #856404;
                    }
                """)
                texto_estado = f"⚙️ {self.remito['estado_actual'].upper()}"
            
            self.label_estado_actual.setText(texto_estado)
        
        except Exception as e:
            config.guardar_log(f"Error al cargar datos del remito: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar datos: {str(e)}", self)
    
    def reimprimir(self):
        """Reimprimir el remito"""
        dialogo = DialogoReimprimirRemito(self.id_remito, self)
        dialogo.exec_()
    
    def ver_equipo(self):
        """Ver el equipo asociado"""
        if self.remito:
            from interfaz.ventanas.equipos import DialogoDetalleEquipo
            dialogo = DialogoDetalleEquipo(self.remito['id_equipo'], self)
            dialogo.exec_()


class DialogoReimprimirRemito(QDialog):
    """Diálogo para reimprimir/visualizar remito"""
    
    def __init__(self, id_remito, parent=None):
        super().__init__(parent)
        self.id_remito = id_remito
        self.remito = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Reimprimir Remito")
        self.setMinimumSize(700, 800)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = Etiqueta("Vista Previa del Remito", "titulo")
        layout.addWidget(titulo)
        
        # Info
        info = QLabel("Vista previa del remito. Use el botón para exportar a PDF.")
        info.setStyleSheet("color: #6c757d; font-style: italic; padding: 5px;")
        layout.addWidget(info)
        
        # Área de vista previa (simulación del remito)
        self.texto_remito = QTextEdit()
        self.texto_remito.setReadOnly(True)
        self.texto_remito.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 20px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.texto_remito, 1)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        boton_exportar = Boton("📄 Exportar a PDF", "primario")
        boton_exportar.clicked.connect(self.exportar_pdf)
        layout_botones.addWidget(boton_exportar)
        
        boton_imprimir = Boton("🖨️ Imprimir", "secundario")
        boton_imprimir.clicked.connect(self.imprimir)
        layout_botones.addWidget(boton_imprimir)
        
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga y genera el contenido del remito"""
        try:
            self.remito = ModuloRemitos.obtener_remito_por_id(self.id_remito)
            
            if not self.remito:
                return
            
            # Generar contenido del remito (formato texto)
            contenido = self.generar_contenido_remito()
            self.texto_remito.setHtml(contenido)
        
        except Exception as e:
            config.guardar_log(f"Error al cargar remito para impresión: {e}", "ERROR")
    
    def generar_contenido_remito(self):
        """Genera el contenido HTML del remito"""
        try:
            fecha = datetime.fromisoformat(str(self.remito['fecha_ingreso']).replace('Z', '+00:00'))
            fecha_texto = fecha.strftime('%d/%m/%Y - %H:%M')
        except:
            fecha_texto = str(self.remito['fecha_ingreso'])
        
        html = f"""
        <div style='font-family: Arial, sans-serif;'>
            <div style='text-align: center; border-bottom: 3px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px;'>
                <h1 style='color: #2563eb; margin: 5px;'>{config.nombre_negocio}</h1>
                <p style='margin: 3px; font-size: 10pt;'>{config.direccion_negocio}</p>
                <p style='margin: 3px; font-size: 10pt;'>Tel: {config.telefono_negocio}</p>
                <h2 style='color: #dc3545; margin-top: 15px;'>REMITO DE INGRESO</h2>
                <p style='font-size: 14pt; font-weight: bold; margin: 5px;'>{self.remito['numero_remito']}</p>
            </div>
            
            <div style='margin: 20px 0;'>
                <p style='margin: 5px;'><b>Fecha de ingreso:</b> {fecha_texto}</p>
            </div>
            
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;'>
                <h3 style='color: #2563eb; margin-top: 0;'>DATOS DEL CLIENTE</h3>
                <p style='margin: 5px;'><b>Nombre:</b> {self.remito['cliente_nombre']}</p>
                <p style='margin: 5px;'><b>Teléfono:</b> {self.remito['cliente_telefono']}</p>
                {'<p style="margin: 5px;"><b>Dirección:</b> ' + self.remito.get('cliente_direccion', 'N/A') + '</p>' if self.remito.get('cliente_direccion') else ''}
            </div>
            
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;'>
                <h3 style='color: #2563eb; margin-top: 0;'>DATOS DEL EQUIPO</h3>
                <p style='margin: 5px;'><b>Tipo:</b> {self.remito['tipo_dispositivo']}</p>
                <p style='margin: 5px;'><b>Marca:</b> {self.remito['marca']}</p>
                <p style='margin: 5px;'><b>Modelo:</b> {self.remito['modelo']}</p>
                {'<p style="margin: 5px;"><b>IMEI/Serie:</b> ' + self.remito.get('identificador', 'N/A') + '</p>' if self.remito.get('identificador') else ''}
                {'<p style="margin: 5px;"><b>Accesorios:</b> ' + self.remito.get('accesorios', 'Ninguno') + '</p>' if self.remito.get('accesorios') else ''}
                {'<p style="margin: 5px;"><b>Patrón/PIN:</b> ' + self.remito.get('patron_bloqueo', 'N/A') + '</p>' if self.remito.get('patron_bloqueo') else ''}
            </div>
            
            <div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; border: 2px solid #ffc107; margin: 15px 0;'>
                <h3 style='color: #856404; margin-top: 0;'>FALLA REPORTADA</h3>
                <p style='margin: 5px;'>{self.remito['falla_reportada']}</p>
            </div>
            
            {'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;"><h3 style="color: #2563eb; margin-top: 0;">OBSERVACIONES</h3><p style="margin: 5px;">' + self.remito.get('observaciones_ingreso', '') + '</p></div>' if self.remito.get('observaciones_ingreso') else ''}
            
            <div style='margin-top: 30px; padding-top: 20px; border-top: 2px solid #dee2e6;'>
                <p style='font-size: 9pt; color: #6c757d; text-align: center;'>{config.texto_pie_remito}</p>
            </div>
            
            <div style='margin-top: 40px; text-align: center;'>
                <p style='margin: 30px 0 5px 0;'>_________________________________</p>
                <p style='margin: 0; font-weight: bold;'>Firma del Cliente</p>
            </div>
        </div>
        """
        
        return html
    
    def exportar_pdf(self):
        """Exportar a PDF"""
        Mensaje.informacion(
            "Exportar a PDF",
            "La funcionalidad de exportación a PDF estará disponible próximamente.\n\nPor ahora puede usar el botón 'Imprimir' y seleccionar 'Guardar como PDF'.",
            self
        )
    
    def imprimir(self):
        """Imprimir el remito"""
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            self.texto_remito.print_(printer)
            Mensaje.exito("Impresión", "Remito enviado a imprimir", self)

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

