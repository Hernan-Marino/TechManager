# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE REPORTES
============================================================================
Visualización de estadísticas y reportes del negocio
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QTabWidget, QDateEdit, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from interfaz.componentes.componentes import (Boton, Etiqueta, Mensaje)
from interfaz.estilos.estilos import Estilos
from sistema_base.configuracion import config
from datetime import datetime, timedelta


class VentanaReportes(QWidget):
    """Ventana principal de reportes y estadísticas"""
    
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
        
        titulo = Etiqueta("📊 Reportes y Estadísticas", "titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_titulo.addWidget(titulo)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tabs de reportes
        tabs = self.crear_tabs_reportes()
        layout.addWidget(tabs, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet(f"QWidget {{ background-color: {Estilos.COLOR_FONDO_CLARO}; padding: 20px; }}")
        layout = QHBoxLayout()
        
        # Botón Volver
        boton_volver = Boton("← Volver", "primario")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        
        layout.addStretch()
        
        # Filtro de fecha
        self.check_filtro_fecha = QCheckBox("Filtrar por fecha")
        layout.addWidget(self.check_filtro_fecha)
        
        layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setCalendarPopup(True)
        layout.addWidget(self.fecha_desde)
        
        layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        layout.addWidget(self.fecha_hasta)
        
        # Botón Generar
        boton_generar = Boton("🔄 Generar Reporte", "primario")
        boton_generar.clicked.connect(self.generar_reporte)
        layout.addWidget(boton_generar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tabs_reportes(self):
        """Crea las pestañas de reportes"""
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
                font-weight: bold;
            }
        """)
        
        # Tab Resumen General
        tab_resumen = self.crear_tab_resumen()
        tabs.addTab(tab_resumen, "📊 Resumen General")
        
        # Tab Ingresos
        tab_ingresos = self.crear_tab_ingresos()
        tabs.addTab(tab_ingresos, "💰 Ingresos")
        
        # Tab Equipos
        tab_equipos = self.crear_tab_equipos()
        tabs.addTab(tab_equipos, "📱 Equipos")
        
        # Tab Clientes
        tab_clientes = self.crear_tab_clientes()
        tabs.addTab(tab_clientes, "👥 Clientes")
        
        return tabs
    
    def crear_tab_resumen(self):
        """Tab de resumen general"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("Resumen General del Negocio")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tarjetas de estadísticas
        layout_tarjetas = QHBoxLayout()
        
        self.tarjeta_equipos_ingresados = self.crear_tarjeta("Equipos Ingresados", "0", "#3498db")
        layout_tarjetas.addWidget(self.tarjeta_equipos_ingresados)
        
        self.tarjeta_ordenes_finalizadas = self.crear_tarjeta("Órdenes Finalizadas", "0", "#28a745")
        layout_tarjetas.addWidget(self.tarjeta_ordenes_finalizadas)
        
        self.tarjeta_ingresos_totales = self.crear_tarjeta("Ingresos Totales", "$0", "#ffc107")
        layout_tarjetas.addWidget(self.tarjeta_ingresos_totales)
        
        self.tarjeta_clientes_nuevos = self.crear_tarjeta("Clientes Nuevos", "0", "#17a2b8")
        layout_tarjetas.addWidget(self.tarjeta_clientes_nuevos)
        
        layout.addLayout(layout_tarjetas)
        
        layout.addStretch()
        
        # Mensaje informativo
        info = QLabel("Seleccione un rango de fechas y presione 'Generar Reporte' para ver las estadísticas")
        info.setStyleSheet("color: #6c757d; font-style: italic; padding: 20px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        tab.setLayout(layout)
        return tab
    
    def crear_tab_ingresos(self):
        """Tab de ingresos"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        titulo = QLabel("Análisis de Ingresos")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tarjetas
        layout_tarjetas = QHBoxLayout()
        
        self.tarjeta_facturas_cobradas = self.crear_tarjeta("Facturas Cobradas", "0", "#28a745")
        layout_tarjetas.addWidget(self.tarjeta_facturas_cobradas)
        
        self.tarjeta_monto_cobrado = self.crear_tarjeta("Monto Cobrado", "$0", "#3498db")
        layout_tarjetas.addWidget(self.tarjeta_monto_cobrado)
        
        self.tarjeta_pendiente_cobro = self.crear_tarjeta("Pendiente de Cobro", "$0", "#dc3545")
        layout_tarjetas.addWidget(self.tarjeta_pendiente_cobro)
        
        layout.addLayout(layout_tarjetas)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def crear_tab_equipos(self):
        """Tab de equipos"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        titulo = QLabel("Estadísticas de Equipos")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tarjetas
        layout_tarjetas = QHBoxLayout()
        
        self.tarjeta_equipos_reparados = self.crear_tarjeta("Equipos Reparados", "0", "#28a745")
        layout_tarjetas.addWidget(self.tarjeta_equipos_reparados)
        
        self.tarjeta_equipos_sin_reparacion = self.crear_tarjeta("Sin Reparación", "0", "#dc3545")
        layout_tarjetas.addWidget(self.tarjeta_equipos_sin_reparacion)
        
        self.tarjeta_equipos_en_curso = self.crear_tarjeta("En Curso", "0", "#ffc107")
        layout_tarjetas.addWidget(self.tarjeta_equipos_en_curso)
        
        layout.addLayout(layout_tarjetas)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def crear_tab_clientes(self):
        """Tab de clientes"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        titulo = QLabel("Estadísticas de Clientes")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tarjetas
        layout_tarjetas = QHBoxLayout()
        
        self.tarjeta_total_clientes = self.crear_tarjeta("Total Clientes", "0", "#3498db")
        layout_tarjetas.addWidget(self.tarjeta_total_clientes)
        
        self.tarjeta_clientes_activos = self.crear_tarjeta("Clientes Activos", "0", "#28a745")
        layout_tarjetas.addWidget(self.tarjeta_clientes_activos)
        
        self.tarjeta_clientes_incobrables = self.crear_tarjeta("Incobrables", "0", "#dc3545")
        layout_tarjetas.addWidget(self.tarjeta_clientes_incobrables)
        
        layout.addLayout(layout_tarjetas)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea una tarjeta de estadística"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                padding: 20px;
                border-radius: 5px;
                min-width: 200px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setFont(QFont("Arial", 24, QFont.Bold))
        label_valor.setStyleSheet(f"color: {color};")
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def generar_reporte(self):
        """Genera el reporte con los filtros seleccionados"""
        Mensaje.informacion(
            "Reportes",
            "La funcionalidad de reportes está en desarrollo.\n\n" +
            "Próximamente podrás visualizar:\n" +
            "• Gráficos de ingresos\n" +
            "• Estadísticas de equipos\n" +
            "• Análisis de clientes\n" +
            "• Exportación a PDF/Excel",
            self
        )
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)
