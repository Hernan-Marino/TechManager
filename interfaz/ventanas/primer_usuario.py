# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - VENTANA PRIMER USUARIO ADMINISTRADOR
============================================================================
Permite crear el primer usuario administrador del sistema
============================================================================
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget)
from PyQt5.QtCore import Qt
from interfaz.componentes.componentes import Boton, CampoTexto, CampoContrasena, Mensaje
from interfaz.estilos.estilos import Estilos
from sistema_base.seguridad import crear_usuario
from base_datos.conexion import db
import bcrypt


class VentanaPrimerUsuario(QDialog):
    """Ventana para crear el primer usuario administrador"""
    
    def __init__(self):
        super().__init__()
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("TechManager - Configuración Inicial")
        self.setFixedSize(600, 850)  # Aumentado de 780 a 850
        self.setModal(True)
        
        # No permitir cerrar con X
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panel superior azul
        panel_superior = self.crear_panel_superior()
        layout.addWidget(panel_superior)
        
        # Panel formulario
        panel_form = self.crear_panel_formulario()
        layout.addWidget(panel_form)
        
        self.setLayout(layout)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Estilos.COLOR_FONDO};
                border: none;
            }}
        """)
        
        # Focus en primer campo
        self.campo_nombre.setFocus()
    
    def crear_panel_superior(self):
        """Crea el panel superior informativo"""
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
        panel.setFixedHeight(350)  # Panel MÁS ALTO para dar espacio
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(18)
        layout.setContentsMargins(40, 60, 40, 50)  # Márgenes equilibrados
        
        # Icono - Engranaje ajustado perfectamente
        icono = QLabel("⚙")  # Engranaje
        icono.setStyleSheet("""
            font-size: 48pt;
            color: #FFD700;
            font-weight: bold;
        """)
        icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(icono)
        
        # Título - MÁS CHICO
        titulo = QLabel("¡Bienvenido a TechManager!")
        titulo.setStyleSheet("""
            color: white;
            font-size: 24pt;
            font-weight: 700;
            font-family: 'Segoe UI', Arial;
            padding: 8px 0px;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Mensaje - MÁS CHICO
        mensaje = QLabel("Cree su usuario administrador")
        mensaje.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95);
            font-size: 13pt;
            font-family: 'Segoe UI', Arial;
            padding: 6px 0px;
        """)
        mensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(mensaje)
        
        panel.setLayout(layout)
        return panel
    
    def crear_panel_formulario(self):
        """Crea el panel con el formulario"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)
        
        # Instrucciones
        instrucciones = QLabel(
            "Este será el usuario administrador con acceso completo al sistema.\n"
            "Podrá crear otros usuarios después."
        )
        instrucciones.setStyleSheet(f"""
            QLabel {{
                color: {Estilos.COLOR_GRIS_700};
                font-size: 10pt;
                font-family: 'Segoe UI', Arial;
                padding: 16px 18px;
                background-color: rgba(6, 182, 212, 0.08);
                border-left: 4px solid {Estilos.COLOR_INFO};
            }}
        """)
        instrucciones.setWordWrap(True)
        instrucciones.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        instrucciones.setMinimumHeight(65)
        layout.addWidget(instrucciones)
        
        layout.addSpacing(18)
        
        # Campo Nombre Completo
        label_nombre = QLabel("Nombre Completo")
        label_nombre.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                color: {Estilos.COLOR_GRIS_700};
            }}
        """)
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto("Ej: Juan Pérez")
        layout.addWidget(self.campo_nombre)
        
        layout.addSpacing(12)
        
        # Campo Usuario
        label_usuario = QLabel("Nombre de Usuario")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                color: {Estilos.COLOR_GRIS_700};
            }}
        """)
        layout.addWidget(label_usuario)
        
        self.campo_usuario = CampoTexto("Ej: juanperez (sin espacios)")
        layout.addWidget(self.campo_usuario)
        
        layout.addSpacing(12)
        
        # Campo Contraseña
        label_pass = QLabel("Contraseña")
        label_pass.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                color: {Estilos.COLOR_GRIS_700};
            }}
        """)
        layout.addWidget(label_pass)
        
        self.campo_password = CampoContrasena("Mínimo 6 caracteres")
        layout.addWidget(self.campo_password)
        
        layout.addSpacing(12)
        
        # Confirmar Contraseña
        label_conf = QLabel("Confirmar Contraseña")
        label_conf.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                color: {Estilos.COLOR_GRIS_700};
            }}
        """)
        layout.addWidget(label_conf)
        
        self.campo_confirmar = CampoContrasena("Repita la contraseña")
        layout.addWidget(self.campo_confirmar)
        
        layout.addSpacing(25)
        
        # Botón Crear
        self.boton_crear = Boton("Crear Usuario Administrador", "primario")
        self.boton_crear.setMinimumHeight(50)
        self.boton_crear.clicked.connect(self.crear_administrador)
        layout.addWidget(self.boton_crear)
        
        # Espacio flexible
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def crear_administrador(self):
        """Crea el primer usuario administrador"""
        # Obtener datos
        nombre = self.campo_nombre.text().strip()
        username = self.campo_usuario.text().strip()
        password = self.campo_password.text()
        confirmar = self.campo_confirmar.text()
        
        # Validaciones
        if not nombre:
            Mensaje.advertencia("Campo requerido", "Ingrese el nombre completo", self)
            self.campo_nombre.setFocus()
            return
        
        if not username:
            Mensaje.advertencia("Campo requerido", "Ingrese el nombre de usuario", self)
            self.campo_usuario.setFocus()
            return
        
        if len(username) < 3:
            Mensaje.advertencia("Usuario muy corto", "El usuario debe tener al menos 3 caracteres", self)
            self.campo_usuario.setFocus()
            return
        
        if " " in username:
            Mensaje.advertencia("Usuario inválido", "El nombre de usuario no puede contener espacios", self)
            self.campo_usuario.setFocus()
            return
        
        if not password:
            Mensaje.advertencia("Campo requerido", "Ingrese una contraseña", self)
            self.campo_password.setFocus()
            return
        
        if len(password) < 6:
            Mensaje.advertencia("Contraseña muy corta", "La contraseña debe tener al menos 6 caracteres", self)
            self.campo_password.setFocus()
            return
        
        if password != confirmar:
            Mensaje.advertencia("Contraseñas no coinciden", "Las contraseñas ingresadas no son iguales", self)
            self.campo_confirmar.setFocus()
            return
        
        try:
            # Hashear contraseña
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insertar en base de datos
            consulta = """
            INSERT INTO usuarios (nombre, username, password_hash, rol, activo, primer_login, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            db.ejecutar_consulta(
                consulta,
                (nombre, username, password_hash.decode('utf-8'), "admin", 1, 0)
            )
            
            Mensaje.exito(
                "¡Usuario creado!",
                f"Usuario administrador '{username}' creado exitosamente.\n\nYa puede iniciar sesión con sus credenciales.",
                self
            )
            
            self.accept()
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                Mensaje.error("Usuario duplicado", "El nombre de usuario ya existe", self)
            else:
                Mensaje.error("Error", f"Error al crear usuario: {str(e)}", self)
