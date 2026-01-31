# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - VENTANA DE LOGIN MODERNA
============================================================================
Ventana de inicio de sesión con diseño profesional
============================================================================
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from interfaz.componentes.componentes import (Boton, CampoTexto, CampoContrasena,
                                              Etiqueta, Mensaje)
from interfaz.estilos.estilos import Estilos
from sistema_base.seguridad import autenticar_usuario
from sistema_base.configuracion import config
from sistema_base.constantes import NOMBRE_COMPLETO, VERSION


class VentanaLogin(QDialog):
    """Ventana de login del sistema con diseño moderno"""
    
    def __init__(self):
        super().__init__()
        self.usuario_autenticado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("TechManager - Iniciar Sesión")
        self.setFixedSize(550, 800)  # Aumentado de 730 a 800
        self.setModal(True)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Panel superior con fondo de color
        panel_superior = self.crear_panel_superior()
        layout_principal.addWidget(panel_superior)
        
        # Panel central con formulario
        panel_central = self.crear_panel_central()
        layout_principal.addWidget(panel_central, 1)  # stretch factor
        
        # Panel inferior con versión
        panel_inferior = self.crear_panel_inferior()
        layout_principal.addWidget(panel_inferior)
        
        self.setLayout(layout_principal)
        
        # Aplicar estilos modernos - ELIMINAR border-radius
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Estilos.COLOR_FONDO};
                border: none;
            }}
        """)
        
        # Focus inicial en el campo de usuario
        self.campo_usuario.setFocus()
    
    def crear_panel_superior(self):
        """Crea el panel superior con logo y título"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Estilos.COLOR_PRIMARIO},
                    stop:1 {Estilos.COLOR_PRIMARIO_HOVER});
                border: none;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        panel.setFixedHeight(350)  # Mismo alto que primer_usuario
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(18)  # Mismo espaciado
        layout.setContentsMargins(40, 60, 40, 50)  # Mismos márgenes
        
        # Icono - Engranaje igual que primer_usuario
        icono = QLabel("⚙")
        icono.setStyleSheet("""
            font-size: 48pt;
            color: #FFD700;
            font-weight: bold;
        """)
        icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(icono)
        
        # Título
        titulo = QLabel("TechManager")
        titulo.setStyleSheet("""
            color: white;
            font-size: 28pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: -0.5px;
            padding: 8px 0px;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Sistema de Gestión")
        subtitulo.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95);
            font-size: 13pt;
            font-weight: 500;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 6px 0px;
        """)
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)
        
        panel.setLayout(layout)
        return panel
    
    def crear_panel_central(self):
        """Crea el panel central con el formulario de login"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)
        
        # Título del formulario
        titulo_form = QLabel("Iniciar Sesión")
        titulo_form.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_LG}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                letter-spacing: -0.3px;
            }}
        """)
        titulo_form.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo_form)
        
        # Espacio
        layout.addSpacing(10)
        
        # Campo Usuario
        label_usuario = QLabel("Usuario")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_GRIS_700};
                margin-bottom: 4px;
            }}
        """)
        layout.addWidget(label_usuario)
        
        self.campo_usuario = CampoTexto("Ingrese su usuario")
        layout.addWidget(self.campo_usuario)
        
        # Espacio entre campos
        layout.addSpacing(8)
        
        # Campo Contraseña
        label_contrasena = QLabel("Contraseña")
        label_contrasena.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_GRIS_700};
                margin-bottom: 4px;
            }}
        """)
        layout.addWidget(label_contrasena)
        
        self.campo_contrasena = CampoContrasena("Ingrese su contraseña")
        layout.addWidget(self.campo_contrasena)
        
        # Conectar eventos
        self.campo_usuario.returnPressed.connect(self.campo_contrasena.setFocus)
        self.campo_contrasena.returnPressed.connect(self.iniciar_sesion)
        
        # Espacio
        layout.addSpacing(8)
        
        # Mensaje de error
        self.label_error = QLabel("")
        self.label_error.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_ERROR};
                padding: 14px 18px;
                background-color: rgba(239, 68, 68, 0.08);
                border-left: 4px solid {Estilos.COLOR_ERROR};
                min-height: 45px;
            }}
        """)
        self.label_error.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_error.setWordWrap(True)
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        # Espacio
        layout.addSpacing(12)
        
        # Botón Iniciar Sesión
        self.boton_login = Boton("Iniciar Sesión", "primario")
        self.boton_login.setMinimumHeight(48)
        self.boton_login.clicked.connect(self.iniciar_sesion)
        layout.addWidget(self.boton_login)
        
        # Espacio flexible
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def crear_panel_inferior(self):
        """Crea el panel inferior con información de versión"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Versión
        version = QLabel(f"Versión {VERSION}")
        version.setStyleSheet(f"""
            QLabel {{
                color: {Estilos.COLOR_GRIS_500};
                font-size: {Estilos.TAMANO_SM}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
        """)
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        panel.setLayout(layout)
        return panel
    
    def iniciar_sesion(self):
        """Maneja el inicio de sesión"""
        # Obtener datos
        username = self.campo_usuario.text().strip()
        password = self.campo_contrasena.text()
        
        # Validar campos
        if not username or not password:
            self.mostrar_error("Por favor complete todos los campos")
            return
        
        # Deshabilitar botón mientras se procesa
        self.boton_login.setEnabled(False)
        self.boton_login.setText("Iniciando sesión...")
        
        # Autenticar usuario
        try:
            usuario = autenticar_usuario(username, password)
            
            if usuario:
                # Login exitoso
                self.usuario_autenticado = usuario
                
                # Verificar si es primer login
                if usuario['primer_login'] == 1:
                    # Debe cambiar contraseña obligatoriamente
                    self.accept()  # Cerrar ventana de login
                else:
                    # Login normal
                    self.accept()
            else:
                # Credenciales incorrectas
                self.mostrar_error("Usuario o contraseña incorrectos")
                self.boton_login.setEnabled(True)
                self.boton_login.setText("Iniciar Sesión")
                self.campo_contrasena.clear()
                self.campo_contrasena.setFocus()
                
        except Exception as e:
            self.mostrar_error(f"Error al iniciar sesión: {str(e)}")
            self.boton_login.setEnabled(True)
            self.boton_login.setText("Iniciar Sesión")
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def obtener_usuario_autenticado(self):
        """Retorna los datos del usuario autenticado"""
        return self.usuario_autenticado
