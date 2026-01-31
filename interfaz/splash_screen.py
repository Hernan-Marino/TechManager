# -*- coding: utf-8 -*-
"""
TECHMANAGER v1.0 - SPLASH SCREEN MODERNO
Pantalla de carga con diseño estilo Canva
"""

from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient


class SplashScreenModerno(QSplashScreen):
    """Splash screen moderno estilo Canva"""
    
    def __init__(self):
        pixmap = QPixmap(700, 450)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.progress = 0
        self.mensaje = "Iniciando..."
        
        self.pintar_splash()
    
    def pintar_splash(self):
        """Pinta el splash con diseño moderno"""
        pixmap = QPixmap(700, 450)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradiente azul
        gradient = QLinearGradient(0, 0, 0, 450)
        gradient.setColorAt(0, QColor("#2563eb"))
        gradient.setColorAt(1, QColor("#1e40af"))
        painter.fillRect(0, 0, 700, 450, gradient)
        
        # Rectángulo blanco
        painter.fillRect(50, 80, 600, 290, QColor("#ffffff"))
        painter.fillRect(50, 80, 600, 8, QColor("#2563eb"))
        
        # Icono
        painter.setPen(QColor("#2563eb"))
        fuente_icono = QFont("Segoe UI Emoji", 72, QFont.Bold)
        painter.setFont(fuente_icono)
        painter.drawText(QRect(50, 110, 600, 100), Qt.AlignCenter, "🔧")
        
        # Título
        painter.setPen(QColor("#1f2937"))
        fuente_titulo = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(fuente_titulo)
        painter.drawText(QRect(50, 220, 600, 50), Qt.AlignCenter, "TechManager")
        
        # Subtítulo
        painter.setPen(QColor("#6b7280"))
        fuente_subtitulo = QFont("Segoe UI", 13)
        painter.setFont(fuente_subtitulo)
        painter.drawText(QRect(50, 270, 600, 30), Qt.AlignCenter, "Sistema de Gestión de Servicio Técnico")
        
        # Versión
        painter.setPen(QColor("#9ca3af"))
        fuente_version = QFont("Segoe UI", 11)
        painter.setFont(fuente_version)
        painter.drawText(QRect(50, 300, 600, 25), Qt.AlignCenter, "Versión 1.0")
        
        # Barra progreso
        barra_x = 100
        barra_y = 340
        barra_ancho = 500
        barra_alto = 8
        
        painter.fillRect(barra_x, barra_y, barra_ancho, barra_alto, QColor("#e5e7eb"))
        
        if self.progress > 0:
            ancho_progreso = int((barra_ancho * self.progress) / 100)
            painter.fillRect(barra_x, barra_y, ancho_progreso, barra_alto, QColor("#2563eb"))
        
        # Mensaje
        painter.setPen(QColor("#6b7280"))
        fuente_mensaje = QFont("Segoe UI", 10)
        painter.setFont(fuente_mensaje)
        painter.drawText(QRect(50, 360, 600, 25), Qt.AlignCenter, self.mensaje)
        
        # Footer
        painter.setPen(QColor("#ffffff"))
        fuente_footer = QFont("Segoe UI", 9)
        painter.setFont(fuente_footer)
        painter.drawText(QRect(0, 410, 700, 30), Qt.AlignCenter, "© 2025 TechManager")
        
        painter.end()
        self.setPixmap(pixmap)
    
    def actualizar_progreso(self, valor, mensaje=""):
        """Actualiza progreso y mensaje"""
        self.progress = valor
        if mensaje:
            self.mensaje = mensaje
        self.pintar_splash()
