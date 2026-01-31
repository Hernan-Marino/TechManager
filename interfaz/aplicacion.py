# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - APLICACIÓN PRINCIPAL
============================================================================
Maneja el flujo completo de la aplicación: primer usuario, login, ventana principal
============================================================================
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from interfaz.ventanas.login import VentanaLogin
from interfaz.ventanas.primer_usuario import VentanaPrimerUsuario
from interfaz.ventanas.cambio_obligatorio import DialogoCambioObligatorio
from interfaz.ventanas.ventana_principal import VentanaPrincipal
from sistema_base.configuracion import config
from base_datos.conexion import db


class AplicacionPrincipal:
    """Clase principal que maneja el flujo de la aplicación"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("TechManager")
        self.ventana_principal = None
    
    def verificar_primer_uso(self):
        """Verifica si es la primera vez que se usa el sistema"""
        try:
            # Verificar si la tabla existe
            if not db.tabla_existe('usuarios'):
                return True
            
            # Si existe, contar usuarios
            consulta = "SELECT COUNT(*) as total FROM usuarios"
            resultado = db.obtener_uno(consulta)
            return resultado['total'] == 0
        except Exception as e:
            # Si hay cualquier error, asumir primera vez
            print(f"Error al verificar primer uso: {e}")
            return True
    
    def iniciar(self):
        """Inicia la aplicación"""
        # Verificar si es primera vez
        if self.verificar_primer_uso():
            # Mostrar ventana de creación de primer usuario
            ventana_primer_usuario = VentanaPrimerUsuario()
            resultado = ventana_primer_usuario.exec_()
            
            if resultado != ventana_primer_usuario.Accepted:
                # Usuario cerró sin crear el administrador
                sys.exit(0)
        
        # Mostrar ventana de login
        ventana_login = VentanaLogin()
        resultado = ventana_login.exec_()
        
        if resultado == ventana_login.Accepted:
            # Login exitoso
            usuario = ventana_login.obtener_usuario_autenticado()
            
            if usuario:
                # Verificar si es primer login
                if usuario['primer_login'] == 1:
                    # Mostrar cambio obligatorio de contraseña
                    ventana_cambio = DialogoCambioObligatorio(usuario)
                    resultado_cambio = ventana_cambio.exec_()
                    
                    if resultado_cambio == ventana_cambio.Accepted:
                        # Contraseña cambiada, abrir ventana principal
                        self.abrir_ventana_principal(usuario)
                    else:
                        # Usuario canceló el cambio (no debería pasar)
                        sys.exit(0)
                else:
                    # Login normal, abrir ventana principal
                    self.abrir_ventana_principal(usuario)
        else:
            # Usuario cerró el login sin autenticarse
            sys.exit(0)
        
        # Ejecutar la aplicación
        sys.exit(self.app.exec_())
    
    def abrir_ventana_principal(self, usuario):
        """Abre la ventana principal del sistema"""
        self.ventana_principal = VentanaPrincipal(usuario)
        self.ventana_principal.show()
