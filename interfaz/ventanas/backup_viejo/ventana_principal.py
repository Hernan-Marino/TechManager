# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - VENTANA PRINCIPAL MODERNA
============================================================================
Ventana principal del sistema con diseño profesional
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
    """Ventana principal del sistema con diseño moderno"""
    
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
        
        # Layout principal vertical (sin menú lateral)
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Barra superior
        barra_superior = self.crear_barra_superior_completa()
        layout_principal.addWidget(barra_superior)
        
        # Área de trabajo (dashboard completo)
        self.area_trabajo = self.crear_dashboard_completo()
        layout_principal.addWidget(self.area_trabajo, 1)
        
        widget_central.setLayout(layout_principal)
        
        # Aplicar estilos modernos
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f7fa;
                border: none;
            }}
        """)
        
        # Maximizar ventana
        self.showMaximized()
    
    def crear_barra_superior_completa(self):
        """Crea la barra superior moderna sin menú lateral"""
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
        
        # Logo + Nombre del sistema
        contenedor_logo = QWidget()
        contenedor_logo.setStyleSheet("background: transparent;")
        layout_logo = QHBoxLayout()
        layout_logo.setSpacing(15)
        layout_logo.setContentsMargins(0, 0, 0, 0)
        
        icono_sistema = QLabel("⚙")
        icono_sistema.setStyleSheet("""
            font-size: 32pt;
            color: #FFD700;
        """)
        layout_logo.addWidget(icono_sistema)
        
        nombre_sistema = QLabel("TechManager")
        nombre_sistema.setStyleSheet("""
            color: white;
            font-size: 22pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial;
        """)
        layout_logo.addWidget(nombre_sistema)
        
        contenedor_logo.setLayout(layout_logo)
        layout.addWidget(contenedor_logo)
        
        # Espacio flexible
        layout.addStretch()
        
        # Información del usuario - MISMO AZUL, sin cambio de tono
        info_usuario = QFrame()
        info_usuario.setStyleSheet("""
            background: transparent;
            border: none;
            padding: 18px 30px;
        """)
        info_usuario.setMinimumHeight(70)
        
        layout_usuario = QHBoxLayout()
        layout_usuario.setSpacing(18)
        layout_usuario.setContentsMargins(0, 0, 0, 0)
        
        # Foto de perfil o icono por defecto
        if self.usuario.get('foto_perfil'):
            # Cargar foto del usuario
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(self.usuario['foto_perfil'])
            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            icono_usuario = QLabel()
            icono_usuario.setPixmap(pixmap)
            icono_usuario.setStyleSheet("""
                border-radius: 25px;
                background: transparent;
            """)
            icono_usuario.setFixedSize(50, 50)
            icono_usuario.setScaledContents(True)
        else:
            # Icono por defecto
            icono_usuario = QLabel("👤")
            icono_usuario.setStyleSheet("""
                font-size: 24pt;
                padding: 8px;
                background: transparent;
            """)
            icono_usuario.setMinimumWidth(50)
            icono_usuario.setMinimumHeight(50)
        
        icono_usuario.setAlignment(Qt.AlignCenter)
        layout_usuario.addWidget(icono_usuario)
        
        # Datos del usuario
        layout_datos = QVBoxLayout()
        layout_datos.setSpacing(4)
        layout_datos.setContentsMargins(0, 0, 0, 0)
        
        nombre = QLabel(self.usuario['nombre'])
        nombre.setStyleSheet("""
            color: white;
            font-size: 13pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial;
            background: transparent;
        """)
        layout_datos.addWidget(nombre)
        
        rol = QLabel("Administrador" if config.es_admin else "Técnico")
        rol.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95);
            font-size: 10pt;
            font-family: 'Segoe UI', Arial;
            background: transparent;
        """)
        layout_datos.addWidget(rol)
        
        layout_usuario.addLayout(layout_datos)
        info_usuario.setLayout(layout_usuario)
        layout.addWidget(info_usuario)
        
        # Botón cerrar sesión - ROJO
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
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """)
        boton_cerrar.setCursor(Qt.PointingHandCursor)
        boton_cerrar.clicked.connect(self.cerrar_sesion)
        layout.addWidget(boton_cerrar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_dashboard_completo(self):
        """Crea el dashboard completo sin menú lateral"""
        contenedor = QWidget()
        contenedor.setStyleSheet("background-color: #f5f7fa;")
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(50, 40, 50, 40)
        layout_principal.setSpacing(40)
        
        # Header de bienvenida
        header = QLabel(f"¡Bienvenido, {self.usuario['nombre']}!")
        header.setStyleSheet("""
            font-size: 32pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial;
            color: #1e293b;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(header)
        
        subtitulo = QLabel("Selecciona un módulo para comenzar")
        subtitulo.setStyleSheet("""
            font-size: 14pt;
            font-family: 'Segoe UI', Arial;
            color: #64748b;
        """)
        subtitulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(subtitulo)
        
        # Scroll area para las tarjetas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Contenedor de tarjetas
        contenedor_tarjetas = QWidget()
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Todas las tarjetas del sistema
        modulos = [
            ("👤", "Clientes", "Gestiona la información de tus clientes", "clientes", "#3b82f6"),
            ("📱", "Equipos", "Registra equipos ingresados al taller", "equipos", "#10b981"),
            ("📋", "Remitos", "Genera remitos de ingreso y egreso", "remitos", "#f59e0b"),
            ("💵", "Presupuestos", "Crea presupuestos de reparación", "presupuestos", "#8b5cf6"),
            ("🔧", "Órdenes de Trabajo", "Administra órdenes en curso", "ordenes", "#ef4444"),
            ("📦", "Repuestos", "Controla inventario de repuestos", "repuestos", "#06b6d4"),
            ("💳", "Pagos", "Registra pagos de clientes", "pagos", "#ec4899"),
            ("💰", "Facturación", "Genera facturas y controla cobros", "facturacion", "#14b8a6"),
            ("✅", "Garantías", "Gestiona garantías de reparaciones", "garantias", "#84cc16"),
            ("📊", "Reportes", "Visualiza estadísticas del negocio", "reportes", "#6366f1"),
            ("👥", "Usuarios", "Administra usuarios del sistema", "usuarios", "#f97316"),
            ("⚙️", "Configuración", "Configura el sistema", "configuracion", "#64748b"),
        ]
        
        # Crear grid de 5 columnas
        for i, (icono, titulo, desc, modulo, color) in enumerate(modulos):
            fila = i // 5
            columna = i % 5
            tarjeta = self.crear_tarjeta_modulo(icono, titulo, desc, modulo, color)
            grid.addWidget(tarjeta, fila, columna)
        
        contenedor_tarjetas.setLayout(grid)
        scroll.setWidget(contenedor_tarjetas)
        layout_principal.addWidget(scroll)
        
        contenedor.setLayout(layout_principal)
        return contenedor
    
    def crear_tarjeta_modulo(self, icono, titulo, descripcion, modulo, color):
        """Crea una tarjeta de módulo compacta y plana"""
        tarjeta = QFrame()
        tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
            }}
            QFrame:hover {{
                background-color: #f8fafc;
                border: 1px solid {color};
            }}
        """)
        tarjeta.setFixedSize(240, 180)
        tarjeta.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icono centrado
        label_icono = QLabel(icono)
        label_icono.setStyleSheet("""
            font-size: 40pt;
            background: transparent;
            border: none;
        """)
        label_icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_icono)
        
        # Título centrado
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("""
            font-size: 14pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial;
            color: #1e293b;
            background: transparent;
            border: none;
        """)
        label_titulo.setAlignment(Qt.AlignCenter)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        # Descripción centrada
        label_desc = QLabel(descripcion)
        label_desc.setStyleSheet("""
            font-size: 9pt;
            font-family: 'Segoe UI', Arial;
            color: #64748b;
            background: transparent;
            border: none;
        """)
        label_desc.setAlignment(Qt.AlignCenter)
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)
        
        tarjeta.setLayout(layout)
        
        # Hacer que toda la tarjeta sea clickeable
        def click_handler(event):
            self.abrir_modulo(modulo)
        
        tarjeta.mousePressEvent = click_handler
        
        return tarjeta
    
    def abrir_modulo(self, id_modulo):
        """Abre un módulo del sistema"""
        # Actualizar título
        titulos = {
            "inicio": "Inicio",
            "dashboard": "Dashboard",
            "clientes": "Clientes",
            "equipos": "Equipos",
            "remitos": "Remitos",
            "presupuestos": "Presupuestos",
            "ordenes": "Órdenes de Trabajo",
            "repuestos": "Repuestos",
            "pagos": "Pagos",
            "facturacion": "Facturación",
            "reportes": "Reportes",
            "garantias": "Garantías",
            "abandonados": "Equipos Abandonados",
            "usuarios": "Usuarios",
            "configuracion": "Configuración",
            "auditoria": "Auditoría",
            "backups": "Backups"
        }
        
        # Limpiar área de trabajo
        layout = self.area_trabajo.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        try:
            # Cargar módulo correspondiente
            if id_modulo == "usuarios":
                from interfaz.ventanas.usuarios import VentanaUsuarios
                ventana = VentanaUsuarios(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "clientes":
                from interfaz.ventanas.clientes import VentanaClientes
                ventana = VentanaClientes(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "equipos":
                from interfaz.ventanas.equipos import VentanaEquipos
                ventana = VentanaEquipos(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "remitos":
                from interfaz.ventanas.remitos import VentanaRemitos
                ventana = VentanaRemitos(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "presupuestos":
                from interfaz.ventanas.presupuestos import VentanaPresupuestos
                ventana = VentanaPresupuestos(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "ordenes":
                from interfaz.ventanas.ordenes import VentanaOrdenes
                ventana = VentanaOrdenes(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "repuestos":
                from interfaz.ventanas.repuestos import VentanaRepuestos
                ventana = VentanaRepuestos(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "pagos" or id_modulo == "facturacion":
                from interfaz.ventanas.facturacion_pagos import VentanaFacturacionPagos
                ventana = VentanaFacturacionPagos(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "garantias":
                from interfaz.ventanas.garantias import VentanaGarantias
                ventana = VentanaGarantias(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "reportes":
                from interfaz.ventanas.reportes import VentanaReportes
                ventana = VentanaReportes(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "configuracion":
                from interfaz.ventanas.configuracion import VentanaConfiguracion
                ventana = VentanaConfiguracion(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "auditoria":
                from interfaz.ventanas.auditoria import VentanaAuditoria
                ventana = VentanaAuditoria(self)
                layout.addWidget(ventana)
            
            elif id_modulo == "backups":
                from interfaz.ventanas.backups import VentanaBackups
                ventana = VentanaBackups(self)
                layout.addWidget(ventana)
            
            else:
                # Módulo no reconocido
                self.mostrar_modulo_en_desarrollo(titulos.get(id_modulo, id_modulo))
        
        except (ModuleNotFoundError, ImportError) as e:
            # Módulo no implementado todavía
            self.mostrar_modulo_en_desarrollo(titulos.get(id_modulo, id_modulo))
        except Exception as e:
            # Error al cargar el módulo
            Mensaje.error("Error", f"Error al cargar el módulo: {str(e)}", self)
    
    def mostrar_modulo_en_desarrollo(self, nombre_modulo):
        """Muestra un mensaje indicando que el módulo está en desarrollo"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Icono
        icono = QLabel("🚧")
        icono.setStyleSheet("font-size: 80pt;")
        icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(icono)
        
        # Título
        titulo = QLabel("Módulo en Desarrollo")
        titulo.setStyleSheet("""
            font-size: 24pt;
            font-weight: 700;
            color: #64748b;
            font-family: 'Segoe UI', Arial;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Mensaje
        mensaje = QLabel(f"El módulo '{nombre_modulo}' estará disponible próximamente.")
        mensaje.setStyleSheet("""
            font-size: 14pt;
            color: #94a3b8;
            font-family: 'Segoe UI', Arial;
        """)
        mensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(mensaje)
        
        widget.setLayout(layout)
        
        # Agregar al área de trabajo
        area_layout = self.area_trabajo.layout()
        if area_layout is not None:
            area_layout.addWidget(widget)
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario y vuelve al login"""
        confirmacion = Mensaje.confirmacion(
            "Cerrar Sesión",
            "¿Desea cerrar sesión?",
            self
        )
        
        if confirmacion:
            # Registrar logout en auditoría
            registrar_logout(self.usuario['id_usuario'])
            
            # Cerrar sesión en configuración
            config.cerrar_sesion()
            
            # Cerrar esta ventana
            self.close()
            
            # Abrir ventana de login
            from interfaz.ventanas.login import VentanaLogin
            login = VentanaLogin()
            
            if login.exec_() == QDialog.Accepted:
                # Usuario hizo login exitoso
                usuario_nuevo = login.obtener_usuario_autenticado()
                
                if usuario_nuevo:
                    # Verificar si debe cambiar contraseña
                    if usuario_nuevo['primer_login'] == 1:
                        from interfaz.ventanas.cambio_obligatorio import DialogoCambioObligatorio
                        dialogo_cambio = DialogoCambioObligatorio(usuario_nuevo)
                        
                        if dialogo_cambio.exec_() != QDialog.Accepted:
                            # Canceló el cambio, no hacer nada
                            return
                    
                    # Crear nueva ventana principal con el nuevo usuario
                    nueva_ventana = VentanaPrincipal(usuario_nuevo)
                    nueva_ventana.show()
