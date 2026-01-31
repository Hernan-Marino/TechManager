# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - DIÁLOGO CAMBIO CONTRASEÑA OBLIGATORIO
============================================================================
Diálogo que obliga al usuario a cambiar su contraseña en el primer login
============================================================================
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from interfaz.componentes.componentes import (Boton, CampoContrasena, 
                                              Etiqueta, Mensaje)
from interfaz.estilos.estilos import Estilos
from sistema_base.seguridad import cambiar_contrasena_primer_login


class DialogoCambioObligatorio(QDialog):
    """
    Diálogo modal que obliga al usuario a cambiar su contraseña
    No se puede cerrar hasta completar el cambio
    """
    
    def __init__(self, usuario_info, parent=None):
        super().__init__(parent)
        self.usuario_info = usuario_info
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Cambio de Contraseña Obligatorio")
        self.setModal(True)
        self.setFixedSize(600, 550)
        
        # Deshabilitar botón de cerrar
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Panel superior con alerta
        panel_alerta = self.crear_panel_alerta()
        layout_principal.addWidget(panel_alerta)
        
        # Panel central con formulario
        panel_formulario = self.crear_panel_formulario()
        layout_principal.addWidget(panel_formulario)
        
        self.setLayout(layout_principal)
    
    def crear_panel_alerta(self):
        """Crea el panel superior de alerta"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Estilos.COLOR_ERROR},
                    stop:1 #c62828);
                padding: 35px;
                border: none;
            }}
        """)
        panel.setMinimumHeight(200)
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icono
        label_icono = QLabel("🔐")
        label_icono.setStyleSheet("font-size: 56pt; border: none;")
        label_icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_icono)
        
        # Título
        label_titulo = QLabel("CAMBIO DE CONTRASEÑA OBLIGATORIO")
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {Estilos.TAMANO_TITULO}pt;
                font-weight: 700;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                letter-spacing: -0.5px;
                border: none;
                padding: 8px 0px;
            }}
        """)
        label_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_titulo)
        
        # Subtítulo
        label_subtitulo = QLabel("Por seguridad, debe cambiar su contraseña temporal")
        label_subtitulo.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.95);
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 500;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                border: none;
                padding: 4px 0px;
            }}
        """)
        label_subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_subtitulo)
        
        panel.setLayout(layout)
        return panel
    
    def crear_panel_formulario(self):
        """Crea el panel central con el formulario"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                padding: 40px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        
        # Mensaje informativo
        frame_info = QFrame()
        frame_info.setStyleSheet(f"""
            QFrame {{
                background-color: {Estilos.COLOR_INFO_FONDO};
                border-left: 4px solid {Estilos.COLOR_INFO};
                padding: 16px;
            }}
        """)
        
        layout_info = QVBoxLayout()
        layout_info.setSpacing(8)
        
        label_info_titulo = QLabel("ℹ️ Información Importante")
        label_info_titulo.setStyleSheet(f"""
            QLabel {{
                color: {Estilos.COLOR_INFO};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
        """)
        layout_info.addWidget(label_info_titulo)
        
        label_info_texto = QLabel(
            f"Bienvenido/a <b>{self.usuario_info['nombre']}</b>.<br><br>"
            "Este es su primer ingreso al sistema. Por motivos de seguridad, "
            "debe cambiar la contraseña temporal por una contraseña personal.<br><br>"
            "• La contraseña debe tener al menos 6 caracteres<br>"
            "• Use una combinación de letras, números y símbolos<br>"
            "• No comparta su contraseña con nadie"
        )
        label_info_texto.setWordWrap(True)
        label_info_texto.setStyleSheet(f"""
            QLabel {{
                color: {Estilos.COLOR_GRIS_700};
                font-size: {Estilos.TAMANO_SM}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                line-height: 1.5;
            }}
        """)
        layout_info.addWidget(label_info_texto)
        
        frame_info.setLayout(layout_info)
        layout.addWidget(frame_info)
        
        # Formulario
        # Contraseña temporal
        layout.addWidget(Etiqueta("Contraseña Temporal:", peso=600))
        self.campo_temporal = CampoContrasena("Ingrese su contraseña temporal")
        layout.addWidget(self.campo_temporal)
        
        # Nueva contraseña
        layout.addWidget(Etiqueta("Nueva Contraseña:", peso=600))
        self.campo_nueva = CampoContrasena("Ingrese su nueva contraseña")
        layout.addWidget(self.campo_nueva)
        
        # Confirmar contraseña
        layout.addWidget(Etiqueta("Confirmar Nueva Contraseña:", peso=600))
        self.campo_confirmar = CampoContrasena("Confirme su nueva contraseña")
        layout.addWidget(self.campo_confirmar)
        
        layout.addStretch()
        
        # Botón cambiar
        boton_cambiar = Boton("🔐 Cambiar Contraseña", "exito")
        boton_cambiar.setMinimumHeight(48)
        boton_cambiar.clicked.connect(self.cambiar_contrasena)
        layout.addWidget(boton_cambiar)
        
        # Mensaje de ayuda
        label_ayuda = QLabel(
            "Si olvidó su contraseña temporal, contacte al administrador del sistema"
        )
        label_ayuda.setWordWrap(True)
        label_ayuda.setAlignment(Qt.AlignCenter)
        label_ayuda.setStyleSheet(f"""
            QLabel {{
                color: {Estilos.COLOR_GRIS_600};
                font-size: {Estilos.TAMANO_XS}pt;
                font-style: italic;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                margin-top: 10px;
            }}
        """)
        layout.addWidget(label_ayuda)
        
        panel.setLayout(layout)
        return panel
    
    def cambiar_contrasena(self):
        """Procesa el cambio de contraseña"""
        # Validaciones
        contrasena_temporal = self.campo_temporal.text().strip()
        contrasena_nueva = self.campo_nueva.text().strip()
        contrasena_confirmar = self.campo_confirmar.text().strip()
        
        # Validar campos vacíos
        if not contrasena_temporal:
            Mensaje.advertencia(
                "Campo Requerido",
                "Debe ingresar su contraseña temporal",
                self
            )
            self.campo_temporal.setFocus()
            return
        
        if not contrasena_nueva:
            Mensaje.advertencia(
                "Campo Requerido",
                "Debe ingresar su nueva contraseña",
                self
            )
            self.campo_nueva.setFocus()
            return
        
        if not contrasena_confirmar:
            Mensaje.advertencia(
                "Campo Requerido",
                "Debe confirmar su nueva contraseña",
                self
            )
            self.campo_confirmar.setFocus()
            return
        
        # Validar longitud mínima
        if len(contrasena_nueva) < 6:
            Mensaje.advertencia(
                "Contraseña Débil",
                "La nueva contraseña debe tener al menos 6 caracteres",
                self
            )
            self.campo_nueva.setFocus()
            return
        
        # Validar que las contraseñas coincidan
        if contrasena_nueva != contrasena_confirmar:
            Mensaje.advertencia(
                "Las Contraseñas No Coinciden",
                "La nueva contraseña y la confirmación no coinciden",
                self
            )
            self.campo_confirmar.clear()
            self.campo_confirmar.setFocus()
            return
        
        # Validar que no sea igual a la temporal
        if contrasena_temporal == contrasena_nueva:
            Mensaje.advertencia(
                "Contraseña Inválida",
                "La nueva contraseña no puede ser igual a la temporal",
                self
            )
            self.campo_nueva.clear()
            self.campo_confirmar.clear()
            self.campo_nueva.setFocus()
            return
        
        # Intentar cambiar contraseña
        exito, mensaje = cambiar_contrasena_primer_login(
            self.usuario_info['id_usuario'],
            contrasena_temporal,
            contrasena_nueva
        )
        
        if exito:
            Mensaje.exito(
                "✓ Contraseña Cambiada",
                "Su contraseña ha sido cambiada exitosamente.\n\n"
                "A partir de ahora, use su nueva contraseña para ingresar al sistema.",
                self
            )
            self.accept()  # Cerrar diálogo con éxito
        else:
            Mensaje.error(
                "Error al Cambiar Contraseña",
                mensaje,
                self
            )
            
            # Si la temporal es incorrecta, limpiar solo ese campo
            if "temporal" in mensaje.lower():
                self.campo_temporal.clear()
                self.campo_temporal.setFocus()
            else:
                # Limpiar todo y volver a empezar
                self.campo_temporal.clear()
                self.campo_nueva.clear()
                self.campo_confirmar.clear()
                self.campo_temporal.setFocus()
    
    def closeEvent(self, event):
        """
        Previene el cierre del diálogo sin cambiar la contraseña
        """
        event.ignore()
        Mensaje.advertencia(
            "Cambio Obligatorio",
            "Debe cambiar su contraseña para continuar usando el sistema.",
            self
        )
    
    def keyPressEvent(self, event):
        """
        Previene el cierre con Escape
        """
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
