# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - VENTANA PRINCIPAL REFACTORIZADA
============================================================================
Ventana principal con QStackedWidget para navegación limpia
============================================================================
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QStackedWidget, QScrollArea,
                             QGridLayout, QGraphicsDropShadowEffect, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap
from interfaz.componentes.componentes import Mensaje
from interfaz.estilos.estilos import Estilos
from sistema_base.configuracion import config
from sistema_base.seguridad import registrar_logout


class VentanaPrincipal(QMainWindow):
    """Ventana principal del sistema con QStackedWidget"""
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"TechManager - {config.nombre_negocio}")
        self.setMinimumSize(1280, 800)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal vertical
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Barra superior
        barra_superior = self.crear_barra_superior()
        layout_principal.addWidget(barra_superior)
        
        # QStackedWidget para manejar vistas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #e5e7eb;")
        
        # Página 0: Dashboard
        dashboard = self.crear_dashboard()
        self.stacked_widget.addWidget(dashboard)
        
        layout_principal.addWidget(self.stacked_widget, 1)
        
        widget_central.setLayout(layout_principal)
        
        # Estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e5e7eb;
                border: none;
            }
        """)
        
        # Maximizar ventana
        self.showMaximized()
    
    def crear_barra_superior(self):
        """Crea la barra superior"""
        barra = QFrame()
        barra.setFixedHeight(90)
        barra.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Estilos.COLOR_PRIMARIO},
                    stop:1 {Estilos.COLOR_PRIMARIO_HOVER});
                border: none;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 0, 40, 0)
        layout.setSpacing(20)
        
        # Logo + Nombre
        icono_sistema = QLabel("⚙")
        icono_sistema.setStyleSheet("font-size: 32pt; color: #FFD700; background: transparent;")
        layout.addWidget(icono_sistema)
        
        nombre_sistema = QLabel("TechManager")
        nombre_sistema.setStyleSheet("""
            color: white;
            font-size: 22pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial;
            background: transparent;
        """)
        layout.addWidget(nombre_sistema)
        
        layout.addStretch()
        
        # Info usuario
        info_usuario = QWidget()
        info_usuario.setStyleSheet("background: transparent;")
        layout_usuario = QHBoxLayout()
        layout_usuario.setSpacing(15)
        
        icono_usuario = QLabel("👤")
        icono_usuario.setStyleSheet("font-size: 28pt; background: transparent;")
        layout_usuario.addWidget(icono_usuario)
        
        layout_datos = QVBoxLayout()
        layout_datos.setSpacing(4)
        
        nombre = QLabel(self.usuario['nombre'])
        nombre.setStyleSheet("""
            color: white;
            font-size: 13pt;
            font-weight: 700;
            background: transparent;
        """)
        layout_datos.addWidget(nombre)
        
        rol = QLabel("Administrador" if config.es_admin else "Técnico")
        rol.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95);
            font-size: 10pt;
            background: transparent;
        """)
        layout_datos.addWidget(rol)
        
        layout_usuario.addLayout(layout_datos)
        info_usuario.setLayout(layout_usuario)
        layout.addWidget(info_usuario)
        
        # Botón cerrar sesión
        boton_cerrar = QPushButton("Cerrar Sesión")
        boton_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 15px 28px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        boton_cerrar.setCursor(Qt.PointingHandCursor)
        boton_cerrar.clicked.connect(self.cerrar_sesion)
        layout.addWidget(boton_cerrar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_dashboard(self):
        """Crea el dashboard con las tarjetas de módulos"""
        contenedor = QWidget()
        contenedor.setStyleSheet("background-color: #e5e7eb;")
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(50, 40, 50, 40)
        layout_principal.setSpacing(40)
        
        # Header
        header = QLabel(f"¡Bienvenido, {self.usuario['nombre']}!")
        header.setStyleSheet("""
            font-size: 32pt;
            font-weight: 700;
            color: #1e293b;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(header)
        
        # Espacio extra
        layout_principal.addSpacing(20)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Grid de tarjetas
        contenedor_tarjetas = QWidget()
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Módulos
        modulos = [
            ("👥", "Clientes", "Gestiona la información de tus clientes", "clientes"),
            ("📱", "Equipos", "Registra equipos ingresados al taller", "equipos"),
            ("📋", "Remitos", "Genera remitos de ingreso de equipos", "remitos"),
            ("💰", "Presupuestos", "Crea presupuestos de reparación", "presupuestos"),
            ("🔧", "Órdenes de Trabajo", "Administra órdenes en curso", "ordenes"),
            ("📦", "Repuestos", "Controla inventario de repuestos", "repuestos"),
            ("💳", "Pagos", "Registra pagos de clientes", "pagos"),
            ("🧾", "Facturación", "Genera facturas y controla cobros", "facturacion"),
            ("✅", "Garantías", "Gestiona garantías de reparaciones", "garantias"),
            ("📊", "Reportes", "Visualiza estadísticas del negocio", "reportes"),
            ("👨‍💼", "Usuarios", "Administra usuarios del sistema", "usuarios"),
            ("⚙", "Configuración", "Configura parámetros del sistema", "configuracion"),
            ("📝", "Auditoría", "Consulta registro de acciones", "auditoria"),
            ("💾", "Backups", "Gestiona copias de seguridad", "backups"),
        ]
        
        row, col = 0, 0
        for icono, titulo, desc, id_mod in modulos:
            tarjeta = self.crear_tarjeta(icono, titulo, desc, id_mod)
            grid.addWidget(tarjeta, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        contenedor_tarjetas.setLayout(grid)
        scroll.setWidget(contenedor_tarjetas)
        layout_principal.addWidget(scroll)
        
        contenedor.setLayout(layout_principal)
        return contenedor
    
    def crear_tarjeta(self, icono, titulo, descripcion, id_modulo):
        """Crea una tarjeta de módulo"""
        tarjeta = QPushButton()
        tarjeta.setCursor(Qt.PointingHandCursor)
        tarjeta.setFixedSize(300, 180)
        tarjeta.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                text-align: center;
                padding: 28px 16px;
            }}
            QPushButton:hover {{
                background-color: #f8fafc;
                border: 2px solid {Estilos.COLOR_PRIMARIO};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_icono = QLabel(icono)
        label_icono.setStyleSheet("font-size: 50pt; border: none; padding: 0px; background: transparent;")
        label_icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_icono)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("""
            font-size: 13pt;
            font-weight: 700;
            color: #1e293b;
            border: none;
            padding: 0px;
            background: transparent;
        """)
        label_titulo.setAlignment(Qt.AlignCenter)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        if descripcion:
            label_desc = QLabel(descripcion)
            label_desc.setStyleSheet("""
                font-size: 8.5pt;
                color: #64748b;
                border: none;
                padding: 0px;
                background: transparent;
            """)
            label_desc.setAlignment(Qt.AlignCenter)
            label_desc.setWordWrap(True)
            layout.addWidget(label_desc)
        
        tarjeta.setLayout(layout)
        tarjeta.clicked.connect(lambda: self.abrir_modulo(id_modulo))
        
        return tarjeta
    
    def abrir_modulo(self, id_modulo):
        """Abre un módulo en el QStackedWidget"""
        try:
            ventana_modulo = None
            
            if id_modulo == "usuarios":
                from interfaz.ventanas.usuarios import VentanaUsuarios
                ventana_modulo = VentanaUsuarios(self.stacked_widget)
            
            elif id_modulo == "clientes":
                from interfaz.ventanas.clientes import VentanaClientes
                ventana_modulo = VentanaClientes(self.stacked_widget)
            
            elif id_modulo == "equipos":
                from interfaz.ventanas.equipos import VentanaEquipos
                ventana_modulo = VentanaEquipos(self.stacked_widget)
            
            elif id_modulo == "remitos":
                from interfaz.ventanas.remitos import VentanaRemitos
                ventana_modulo = VentanaRemitos(self.stacked_widget)
            
            elif id_modulo == "presupuestos":
                from interfaz.ventanas.presupuestos import VentanaPresupuestos
                ventana_modulo = VentanaPresupuestos(self.stacked_widget)
            
            elif id_modulo == "ordenes":
                from interfaz.ventanas.ordenes import VentanaOrdenes
                ventana_modulo = VentanaOrdenes(self.stacked_widget)
            
            elif id_modulo == "repuestos":
                from interfaz.ventanas.repuestos import VentanaRepuestos
                ventana_modulo = VentanaRepuestos(self.stacked_widget)
            
            elif id_modulo == "pagos" or id_modulo == "facturacion":
                from interfaz.ventanas.facturacion_pagos import VentanaFacturacionPagos
                ventana_modulo = VentanaFacturacionPagos(self.stacked_widget)
            
            elif id_modulo == "garantias":
                from interfaz.ventanas.garantias import VentanaGarantias
                ventana_modulo = VentanaGarantias(self.stacked_widget)
            
            elif id_modulo == "reportes":
                from interfaz.ventanas.reportes import VentanaReportes
                ventana_modulo = VentanaReportes(self.stacked_widget)
            
            elif id_modulo == "configuracion":
                from interfaz.ventanas.configuracion import VentanaConfiguracion
                ventana_modulo = VentanaConfiguracion(self.stacked_widget)
            
            elif id_modulo == "auditoria":
                from interfaz.ventanas.auditoria import VentanaAuditoria
                ventana_modulo = VentanaAuditoria(self.stacked_widget)
            
            elif id_modulo == "backups":
                from interfaz.ventanas.backups import VentanaBackups
                ventana_modulo = VentanaBackups(self.stacked_widget)
            
            if ventana_modulo:
                # Agregar al stack y mostrar
                self.stacked_widget.addWidget(ventana_modulo)
                self.stacked_widget.setCurrentWidget(ventana_modulo)
            else:
                Mensaje.advertencia("Módulo no disponible", f"El módulo '{id_modulo}' no está implementado", self)
        
        except (ModuleNotFoundError, ImportError) as e:
            Mensaje.error("Error", f"No se pudo cargar el módulo: {str(e)}", self)
        except Exception as e:
            Mensaje.error("Error", f"Error al abrir módulo: {str(e)}", self)
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        confirmacion = Mensaje.confirmacion(
            "Cerrar Sesión",
            "¿Desea cerrar sesión?",
            self
        )
        
        if confirmacion:
            registrar_logout(self.usuario['id_usuario'])
            config.cerrar_sesion()
            self.close()
            
            from interfaz.ventanas.login import VentanaLogin
            login = VentanaLogin()
            
            if login.exec_() == QDialog.Accepted:
                usuario_nuevo = login.obtener_usuario_autenticado()
                
                if usuario_nuevo:
                    if usuario_nuevo['primer_login'] == 1:
                        from interfaz.ventanas.cambio_obligatorio import DialogoCambioObligatorio
                        dialogo_cambio = DialogoCambioObligatorio(usuario_nuevo)
                        
                        if dialogo_cambio.exec_() != QDialog.Accepted:
                            return
                    
                    nueva_ventana = VentanaPrincipal(usuario_nuevo)
                    nueva_ventana.show()
