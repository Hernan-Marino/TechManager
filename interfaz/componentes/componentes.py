# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - COMPONENTES REUTILIZABLES MODERNOS
============================================================================
Componentes de interfaz profesionales con diseño moderno
============================================================================
"""

from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QMessageBox, 
                             QComboBox, QTextEdit)
from PyQt5.QtCore import Qt
from interfaz.estilos.estilos import Estilos


class Boton(QPushButton):
    """Botón personalizado con estilos modernos"""
    
    def __init__(self, texto, tipo="primario", parent=None):
        super().__init__(texto, parent)
        self.aplicar_estilo(tipo)
        self.setCursor(Qt.PointingHandCursor)
        # Altura mínima más generosa
        self.setMinimumHeight(42)
    
    def aplicar_estilo(self, tipo):
        """Aplica el estilo según el tipo de botón"""
        if tipo == "primario":
            self.setStyleSheet(Estilos.boton_primario())
        elif tipo == "secundario":
            self.setStyleSheet(Estilos.boton_secundario())
        elif tipo == "exito":
            self.setStyleSheet(Estilos.boton_exito())
        elif tipo == "peligro":
            self.setStyleSheet(Estilos.boton_peligro())
        elif tipo == "neutro":
            self.setStyleSheet(Estilos.boton_neutro())


class CampoTexto(QLineEdit):
    """Campo de texto moderno con placeholder mejorado"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(Estilos.campo_entrada())
        # Altura más generosa
        self.setMinimumHeight(44)


class CampoContrasena(QLineEdit):
    """Campo de contraseña moderno"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet(Estilos.campo_entrada())
        self.setMinimumHeight(44)


class CampoTextoMultilinea(QTextEdit):
    """Campo de texto multilínea moderno"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(Estilos.campo_texto_multilinea())
        self.setMinimumHeight(120)


class ListaDesplegable(QComboBox):
    """Lista desplegable moderna"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(Estilos.combobox())
        self.setMinimumHeight(44)


class Etiqueta(QLabel):
    """Etiqueta personalizada moderna"""
    
    def __init__(self, texto, tipo="normal", parent=None):
        super().__init__(texto, parent)
        self.aplicar_estilo(tipo)
        # Permitir selección de texto
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
    
    def aplicar_estilo(self, tipo):
        """Aplica el estilo según el tipo de etiqueta"""
        if tipo == "titulo":
            self.setStyleSheet(Estilos.etiqueta_titulo())
        elif tipo == "subtitulo":
            self.setStyleSheet(Estilos.etiqueta_subtitulo())
        elif tipo == "normal":
            self.setStyleSheet(Estilos.etiqueta_normal())
        elif tipo == "error":
            self.setStyleSheet(Estilos.etiqueta_error())
        elif tipo == "exito":
            self.setStyleSheet(Estilos.etiqueta_exito())


class Mensaje:
    """Clase para mostrar mensajes modernos al usuario"""
    
    @staticmethod
    def exito(titulo, mensaje, parent=None):
        """Muestra un mensaje de éxito moderno"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                min-width: 400px;
            }}
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                padding: {Estilos.ESPACIADO_LG};
            }}
            QPushButton {{
                background-color: {Estilos.COLOR_EXITO};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_EXITO_HOVER};
            }}
        """)
        msg.exec_()
    
    @staticmethod
    def error(titulo, mensaje, parent=None):
        """Muestra un mensaje de error moderno"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                min-width: 400px;
            }}
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                padding: {Estilos.ESPACIADO_LG};
            }}
            QPushButton {{
                background-color: {Estilos.COLOR_ERROR};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_ERROR_HOVER};
            }}
        """)
        msg.exec_()
    
    @staticmethod
    def advertencia(titulo, mensaje, parent=None):
        """Muestra un mensaje de advertencia moderno"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                min-width: 400px;
            }}
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                padding: {Estilos.ESPACIADO_LG};
            }}
            QPushButton {{
                background-color: {Estilos.COLOR_ADVERTENCIA};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_ADVERTENCIA_HOVER};
            }}
        """)
        msg.exec_()
    
    @staticmethod
    def confirmacion(titulo, mensaje, parent=None):
        """Muestra un mensaje de confirmación moderno y retorna True/False"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                min-width: 400px;
            }}
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                padding: {Estilos.ESPACIADO_LG};
            }}
            QPushButton {{
                background-color: {Estilos.COLOR_PRIMARIO};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                min-width: 80px;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_PRIMARIO_HOVER};
            }}
        """)
        
        # Traducir botones
        boton_si = msg.button(QMessageBox.Yes)
        boton_si.setText("Sí")
        boton_no = msg.button(QMessageBox.No)
        boton_no.setText("No")
        
        resultado = msg.exec_()
        return resultado == QMessageBox.Yes
    
    @staticmethod
    def informacion(titulo, mensaje, parent=None):
        """Muestra un mensaje informativo moderno"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                min-width: 400px;
            }}
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                padding: {Estilos.ESPACIADO_LG};
            }}
            QPushButton {{
                background-color: {Estilos.COLOR_INFO};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_INFO_HOVER};
            }}
        """)
        msg.exec_()
