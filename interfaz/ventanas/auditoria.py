# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ COMPLETA MÓDULO DE AUDITORÍA
============================================================================
Consulta avanzada de logs de auditoría del sistema
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QDateEdit, QCheckBox,
                             QSpinBox, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, ListaDesplegable)
from interfaz.estilos.estilos import Estilos
from modulos.auditoria_LOGICA import ModuloAuditoria
from sistema_base.configuracion import config
from datetime import datetime, timedelta
import csv


class VentanaAuditoria(QWidget):
    """Ventana de consulta de auditoría"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.registros_actuales = []
        self.inicializar_ui()
        self.cargar_auditoria()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("📝 Auditoría del Sistema", "titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_titulo.addWidget(titulo)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
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
        self.tabla = self.crear_tabla_auditoria()
        layout.addWidget(self.tabla, 1)
        
        # Info de paginación
        self.label_paginacion = QLabel()
        self.label_paginacion.setStyleSheet("color: #6c757d; font-size: 9pt; padding: 5px;")
        layout.addWidget(self.label_paginacion)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet(f"QWidget {{ background-color: {Estilos.COLOR_FONDO_CLARO}; padding: 20px; border: none; }}")
        
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(15)
        
        # Primera fila
        layout_fila1 = QHBoxLayout()
        layout_fila1.setSpacing(15)
        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar en motivo, usuario...")
        self.campo_busqueda.textChanged.connect(self.cargar_auditoria)
        layout_fila1.addWidget(self.campo_busqueda, 1)
        
        # Módulo
        self.combo_modulo = ListaDesplegable()
        self.combo_modulo.addItem("Todos los módulos", "")
        modulos = ModuloAuditoria.obtener_modulos_disponibles()
        for modulo in modulos:
            self.combo_modulo.addItem(modulo, modulo)
        self.combo_modulo.currentIndexChanged.connect(self.cargar_auditoria)
        layout_fila1.addWidget(self.combo_modulo)
        
        # Acción
        self.combo_accion = ListaDesplegable()
        self.combo_accion.addItem("Todas las acciones", "")
        acciones = ModuloAuditoria.obtener_acciones_disponibles()
        for accion in acciones:
            self.combo_accion.addItem(accion, accion)
        self.combo_accion.currentIndexChanged.connect(self.cargar_auditoria)
        layout_fila1.addWidget(self.combo_accion)
        
        layout_principal.addLayout(layout_fila1)
        
        # Segunda fila
        layout_fila2 = QHBoxLayout()
        layout_fila2.setSpacing(15)
        
        # Filtro de fechas
        self.check_filtro_fecha = QCheckBox("Filtrar por fecha")
        self.check_filtro_fecha.stateChanged.connect(self.toggle_filtro_fecha)
        layout_fila2.addWidget(self.check_filtro_fecha)
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addDays(-7))
        self.fecha_desde.setEnabled(False)
        self.fecha_desde.dateChanged.connect(self.cargar_auditoria)
        layout_fila2.addWidget(self.fecha_desde)
        
        layout_fila2.addWidget(QLabel("hasta"))
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setEnabled(False)
        self.fecha_hasta.dateChanged.connect(self.cargar_auditoria)
        layout_fila2.addWidget(self.fecha_hasta)
        
        # Solo acciones críticas
        self.check_criticas = QCheckBox("Solo acciones críticas")
        self.check_criticas.stateChanged.connect(self.cargar_auditoria)
        layout_fila2.addWidget(self.check_criticas)
        
        # Límite de registros
        layout_fila2.addWidget(QLabel("Mostrar:"))
        self.spin_limite = QSpinBox()
        self.spin_limite.setMinimum(10)
        self.spin_limite.setMaximum(1000)
        self.spin_limite.setValue(200)
        self.spin_limite.setSingleStep(50)
        self.spin_limite.valueChanged.connect(self.cargar_auditoria)
        layout_fila2.addWidget(self.spin_limite)
        
        layout_fila2.addStretch()
        
        # Botones
        boton_exportar = Boton("📊 Exportar CSV", "secundario")
        boton_exportar.clicked.connect(self.exportar_csv)
        layout_fila2.addWidget(boton_exportar)
        
        boton_actualizar = Boton("🔄", "secundario")
        boton_actualizar.setMaximumWidth(50)
        boton_actualizar.setToolTip("Actualizar")
        boton_actualizar.clicked.connect(self.cargar_auditoria)
        layout_fila2.addWidget(boton_actualizar)
        
        # Botón Volver
        boton_volver = Boton("← Volver", "primario")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout_fila2.addWidget(boton_volver)
        
        layout_principal.addLayout(layout_fila2)
        
        barra.setLayout(layout_principal)
        return barra
    
    def toggle_filtro_fecha(self):
        """Activa/desactiva filtro de fecha"""
        activo = self.check_filtro_fecha.isChecked()
        self.fecha_desde.setEnabled(activo)
        self.fecha_hasta.setEnabled(activo)
        self.cargar_auditoria()
    
    def actualizar_estadisticas(self):
        """Actualiza estadísticas"""
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
        
        stats = ModuloAuditoria.obtener_estadisticas_auditoria(fecha_desde, fecha_hasta)
        
        # Crear tarjetas
        self.layout_stats.addWidget(self.crear_tarjeta("Total Registros", str(stats.get('total_registros', 0)), "#3498db"))
        self.layout_stats.addWidget(self.crear_tarjeta("Hoy", str(stats.get('hoy', 0)), "#28a745"))
        self.layout_stats.addWidget(self.crear_tarjeta("Esta Semana", str(stats.get('semana', 0)), "#17a2b8"))
        self.layout_stats.addWidget(self.crear_tarjeta("Usuarios Activos", str(stats.get('usuarios_activos', 0)), "#ffc107"))
        self.layout_stats.addWidget(self.crear_tarjeta("Módulos Usados", str(stats.get('modulos_usados', 0)), "#6c757d"))
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea tarjeta"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 18px;
                min-width: 140px;
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
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            font-size: 24pt;
            font-weight: 700;
            color: {color};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
            padding: 4px 0px;
        """)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_auditoria(self):
        """Crea la tabla de auditoría"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "Fecha/Hora", "Usuario", "Módulo", "Acción", "Registro", "Motivo", "Acciones"
        ])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        tabla.setColumnWidth(6, 100)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_auditoria(self):
        """Carga los registros de auditoría"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            modulo = self.combo_modulo.currentData()
            accion = self.combo_accion.currentData()
            limite = self.spin_limite.value()
            
            fecha_desde = None
            fecha_hasta = None
            
            if self.check_filtro_fecha.isChecked():
                fecha_desde = self.fecha_desde.date().toPyDate()
                fecha_hasta = self.fecha_hasta.date().toPyDate()
            
            solo_criticas = self.check_criticas.isChecked()
            
            self.registros_actuales = ModuloAuditoria.listar_auditoria(
                filtro_modulo=modulo,
                filtro_accion=accion,
                busqueda=busqueda,
                limite=limite,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                solo_criticas=solo_criticas
            )
            
            self.tabla.setRowCount(0)
            
            # Acciones críticas
            acciones_criticas = ["Eliminar", "Marcar incobrable", "Restaurar backup", "Cambiar contraseña"]
            
            for registro in self.registros_actuales:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # Fecha/Hora
                try:
                    fecha = datetime.fromisoformat(str(registro['fecha_hora']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    fecha_texto = str(registro['fecha_hora'])
                self.tabla.setItem(fila, 0, QTableWidgetItem(fecha_texto))
                
                # Usuario
                usuario_texto = registro['usuario_nombre'] if registro['usuario_nombre'] else "Sistema"
                item_usuario = QTableWidgetItem(usuario_texto)
                if usuario_texto == "Sistema":
                    item_usuario.setForeground(QColor("#6c757d"))
                    item_usuario.setFont(QFont("Arial", 9, QFont.Italic))
                self.tabla.setItem(fila, 1, item_usuario)
                
                # Módulo
                self.tabla.setItem(fila, 2, QTableWidgetItem(registro['modulo']))
                
                # Acción
                item_accion = QTableWidgetItem(registro['accion'])
                
                # Marcar acciones críticas
                if registro['accion'] in acciones_criticas:
                    item_accion.setForeground(QColor("#dc3545"))
                    item_accion.setFont(QFont("Arial", 10, QFont.Bold))
                    item_accion.setText(f"⚠️ {registro['accion']}")
                elif registro['accion'] in ["Crear", "Agregar"]:
                    item_accion.setForeground(QColor("#28a745"))
                elif registro['accion'] in ["Modificar", "Actualizar"]:
                    item_accion.setForeground(QColor("#17a2b8"))
                
                self.tabla.setItem(fila, 3, item_accion)
                
                # Registro
                self.tabla.setItem(fila, 4, QTableWidgetItem(str(registro['id_registro'])))
                
                # Motivo
                motivo = registro['motivo'] if registro['motivo'] else "-"
                self.tabla.setItem(fila, 5, QTableWidgetItem(motivo))
                
                # Acciones
                widget = self.crear_botones_acciones(registro)
                self.tabla.setCellWidget(fila, 6, widget)
            
            # Actualizar stats
            self.actualizar_estadisticas()
            
            # Actualizar info de paginación
            total_mostrado = len(self.registros_actuales)
            self.label_paginacion.setText(f"Mostrando {total_mostrado} registros")
        
        except Exception as e:
            config.guardar_log(f"Error al cargar auditoría: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar auditoría: {str(e)}", self)
    
    def crear_botones_acciones(self, registro):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver detalle
        boton_ver = Boton("👁️", "primario")
        boton_ver.setToolTip("Ver detalle completo")
        boton_ver.setMaximumWidth(50)
        boton_ver.clicked.connect(lambda: self.ver_detalle(registro))
        layout.addWidget(boton_ver)
        
        widget.setLayout(layout)
        return widget
    
    def ver_detalle(self, registro):
        """Ver detalle del registro"""
        dialogo = DialogoDetalleAuditoria(registro, self)
        dialogo.exec_()
    
    def exportar_csv(self):
        """Exporta los registros a CSV"""
        if not self.registros_actuales:
            Mensaje.advertencia("Sin Datos", "No hay registros para exportar", self)
            return
        
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Auditoría",
            f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        
        if archivo:
            try:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Encabezados
                    writer.writerow([
                        "Fecha/Hora", "Usuario", "Módulo", "Acción", 
                        "ID Registro", "Motivo"
                    ])
                    
                    # Datos
                    for reg in self.registros_actuales:
                        try:
                            fecha = datetime.fromisoformat(str(reg['fecha_hora']).replace('Z', '+00:00'))
                            fecha_texto = fecha.strftime('%d/%m/%Y %H:%M:%S')
                        except:
                            fecha_texto = str(reg['fecha_hora'])
                        
                        writer.writerow([
                            fecha_texto,
                            reg['usuario_nombre'] if reg['usuario_nombre'] else "Sistema",
                            reg['modulo'],
                            reg['accion'],
                            reg['id_registro'],
                            reg['motivo'] if reg['motivo'] else ""
                        ])
                
                Mensaje.exito("✓ Exportado", f"Se exportaron {len(self.registros_actuales)} registros a:\n{archivo}", self)
            
            except Exception as e:
                config.guardar_log(f"Error al exportar CSV: {e}", "ERROR")
                Mensaje.error("Error", f"Error al exportar: {str(e)}", self)
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)


class DialogoDetalleAuditoria(QDialog):
    """Diálogo para ver detalle completo de un registro de auditoría"""
    
    def __init__(self, registro, parent=None):
        super().__init__(parent)
        self.registro = registro
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle de Auditoría")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("📊 Detalle del Registro de Auditoría", "titulo")
        layout.addWidget(titulo)
        
        # Frame principal
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
        
        # Información básica
        label_basico = QLabel("<b style='color: #2563eb; font-size: 12pt;'>📋 INFORMACIÓN BÁSICA</b>")
        layout_datos.addWidget(label_basico)
        
        self.label_info_basica = QLabel()
        self.label_info_basica.setWordWrap(True)
        self.label_info_basica.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_info_basica)
        
        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(sep1)
        
        # Detalles de la acción
        label_accion = QLabel("<b style='color: #2563eb; font-size: 12pt;'>⚙️ DETALLES DE LA ACCIÓN</b>")
        layout_datos.addWidget(label_accion)
        
        self.label_detalles = QLabel()
        self.label_detalles.setWordWrap(True)
        self.label_detalles.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_detalles)
        
        # Si hay motivo
        self.frame_motivo = QFrame()
        self.frame_motivo.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        layout_motivo = QVBoxLayout()
        
        label_motivo_titulo = QLabel("<b style='color: #856404;'>💬 MOTIVO / OBSERVACIONES</b>")
        layout_motivo.addWidget(label_motivo_titulo)
        
        self.label_motivo = QLabel()
        self.label_motivo.setWordWrap(True)
        self.label_motivo.setStyleSheet("color: #856404; font-size: 10pt;")
        layout_motivo.addWidget(self.label_motivo)
        
        self.frame_motivo.setLayout(layout_motivo)
        layout_datos.addWidget(self.frame_motivo)
        
        frame_datos.setLayout(layout_datos)
        layout.addWidget(frame_datos)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los datos del registro"""
        # Información básica
        try:
            fecha = datetime.fromisoformat(str(self.registro['fecha_hora']).replace('Z', '+00:00'))
            fecha_texto = fecha.strftime('%d/%m/%Y a las %H:%M:%S')
        except:
            fecha_texto = str(self.registro['fecha_hora'])
        
        usuario = self.registro['usuario_nombre'] if self.registro['usuario_nombre'] else "Sistema Automático"
        
        texto_basico = f"<b>Fecha y hora:</b> {fecha_texto}<br>"
        texto_basico += f"<b>Usuario:</b> {usuario}<br>"
        texto_basico += f"<b>ID del registro de auditoría:</b> {self.registro['id_auditoria']}"
        
        self.label_info_basica.setText(texto_basico)
        
        # Detalles de la acción
        # Determinar si es crítica
        acciones_criticas = ["Eliminar", "Marcar incobrable", "Restaurar backup", "Cambiar contraseña"]
        es_critica = self.registro['accion'] in acciones_criticas
        
        texto_detalles = f"<b>Módulo:</b> {self.registro['modulo']}<br>"
        texto_detalles += f"<b>Acción:</b> "
        
        if es_critica:
            texto_detalles += f"<span style='color: #dc3545; font-weight: bold;'>⚠️ {self.registro['accion']} (CRÍTICA)</span><br>"
        else:
            texto_detalles += f"{self.registro['accion']}<br>"
        
        texto_detalles += f"<b>ID del registro afectado:</b> {self.registro['id_registro']}"
        
        self.label_detalles.setText(texto_detalles)
        
        # Motivo
        if self.registro['motivo']:
            self.label_motivo.setText(self.registro['motivo'])
            self.frame_motivo.setVisible(True)
        else:
            self.frame_motivo.setVisible(False)
