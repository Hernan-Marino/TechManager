# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE USUARIOS
============================================================================
Ventana de gestión de usuarios del sistema
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QLineEdit, QRadioButton, QButtonGroup, QFrame,
                             QAbstractItemView, QFileDialog, QPushButton)
from PyQt5.QtCore import Qt, QBuffer, QIODevice
from PyQt5.QtGui import QColor, QPixmap
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              ListaDesplegable, Mensaje)
from interfaz.estilos.estilos import Estilos
from modulos.usuarios import ModuloUsuarios
from sistema_base.seguridad import generar_contrasena_temporal
from sistema_base.configuracion import config


class VentanaUsuarios(QWidget):
    """Ventana principal de gestión de usuarios"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_usuarios()
    
    def inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(20)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Barra de herramientas superior
        barra_herramientas = self.crear_barra_herramientas()
        layout_principal.addWidget(barra_herramientas)
        
        # Tarjetas de estadísticas
        tarjetas = self.crear_tarjetas_estadisticas()
        layout_principal.addWidget(tarjetas)
        
        # Tabla de usuarios
        self.tabla = self.crear_tabla_usuarios()
        layout_principal.addWidget(self.tabla, 1)
        
        self.setLayout(layout_principal)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas superior"""
        barra = QWidget()
        barra.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                padding: 20px;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Campo de búsqueda
        self.campo_busqueda = CampoTexto("Buscar usuario por nombre o username...")
        self.campo_busqueda.textChanged.connect(self.buscar_usuarios)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Botón Nuevo Usuario
        boton_nuevo = Boton("➕ Nuevo Usuario", "exito")
        boton_nuevo.clicked.connect(self.abrir_dialogo_nuevo_usuario)
        layout.addWidget(boton_nuevo)
        
        # Botón Actualizar
        boton_actualizar = Boton("🔄 Actualizar", "secundario")
        boton_actualizar.clicked.connect(self.cargar_usuarios)
        layout.addWidget(boton_actualizar)
        
        # Botón Volver
        boton_volver = Boton("← Volver", "secundario")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tarjetas_estadisticas(self):
        """Crea las tarjetas con estadísticas de usuarios"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Obtener estadísticas
        stats = ModuloUsuarios.obtener_estadisticas_usuarios()
        
        # Tarjeta Total
        tarjeta_total = self.crear_tarjeta_estadistica(
            "Total de Usuarios",
            str(stats['total']),
            "#3498db"
        )
        layout.addWidget(tarjeta_total)
        
        # Tarjeta Activos
        tarjeta_activos = self.crear_tarjeta_estadistica(
            "Usuarios Activos",
            str(stats['activos']),
            "#28a745"
        )
        layout.addWidget(tarjeta_activos)
        
        # Tarjeta Inactivos
        tarjeta_inactivos = self.crear_tarjeta_estadistica(
            "Usuarios Inactivos",
            str(stats['inactivos']),
            "#dc3545"
        )
        layout.addWidget(tarjeta_inactivos)
        
        # Tarjeta Administradores
        tarjeta_admin = self.crear_tarjeta_estadistica(
            "Administradores",
            str(stats['administradores']),
            "#ffc107"
        )
        layout.addWidget(tarjeta_admin)
        
        # Tarjeta Técnicos
        tarjeta_tecnicos = self.crear_tarjeta_estadistica(
            "Técnicos",
            str(stats['tecnicos']),
            "#17a2b8"
        )
        layout.addWidget(tarjeta_tecnicos)
        
        contenedor.setLayout(layout)
        return contenedor
    
    def crear_tarjeta_estadistica(self, titulo, valor, color):
        """Crea una tarjeta de estadística"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 20px;
                min-width: 160px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                font-size: {Estilos.TAMANO_SM}pt;
                color: {Estilos.COLOR_GRIS_600};
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                font-weight: 500;
                border: none;
            }}
        """)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        # Valor
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            QLabel {{
                font-size: 28pt;
                font-weight: 700;
                color: {color};
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                border: none;
                padding: 4px 0px;
            }}
        """)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_usuarios(self):
        """Crea la tabla de usuarios"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Usuario", "Rol", "Estado", "Fecha Creación", "Acciones"
        ])
        
        # Configurar tabla
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        # Configurar ancho de columnas
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Usuario
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Rol
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Fecha
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Acciones
        tabla.setColumnWidth(6, 300)
        
        # Aplicar estilos
        tabla.setStyleSheet(Estilos.tabla())
        
        return tabla
    
    def cargar_usuarios(self):
        """Carga los usuarios en la tabla"""
        try:
            # Obtener búsqueda
            busqueda = self.campo_busqueda.text().strip()
            
            # Obtener usuarios
            usuarios = ModuloUsuarios.listar_usuarios(busqueda=busqueda)
            
            # Limpiar tabla
            self.tabla.setRowCount(0)
            
            # Llenar tabla
            for usuario in usuarios:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(usuario['id_usuario'])))
                
                # Nombre
                self.tabla.setItem(fila, 1, QTableWidgetItem(usuario['nombre']))
                
                # Usuario
                self.tabla.setItem(fila, 2, QTableWidgetItem(usuario['username']))
                
                # Rol
                rol_texto = "Administrador" if usuario['rol'] == 'admin' else "Técnico"
                self.tabla.setItem(fila, 3, QTableWidgetItem(rol_texto))
                
                # Estado
                item_estado = QTableWidgetItem(usuario['estado'])
                if usuario['activo']:
                    item_estado.setForeground(QColor("#28a745"))
                else:
                    item_estado.setForeground(QColor("#dc3545"))
                self.tabla.setItem(fila, 4, item_estado)
                
                # Fecha
                fecha_str = usuario['fecha_creacion']
                if isinstance(fecha_str, str):
                    try:
                        from datetime import datetime
                        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                        fecha_formateada = fecha.strftime('%d/%m/%Y %H:%M')
                    except:
                        fecha_formateada = fecha_str
                else:
                    fecha_formateada = str(fecha_str)
                
                self.tabla.setItem(fila, 5, QTableWidgetItem(fecha_formateada))
                
                # Botones de acciones
                widget_acciones = self.crear_botones_acciones(usuario)
                self.tabla.setCellWidget(fila, 6, widget_acciones)
            
            # Actualizar estadísticas
            self.actualizar_estadisticas()
            
        except Exception as e:
            config.guardar_log(f"Error al cargar usuarios: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar usuarios: {str(e)}", self)
    
    def crear_botones_acciones(self, usuario):
        """Crea los botones de acciones para cada fila"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Editar
        boton_editar = Boton("✏️ Editar", "secundario")
        boton_editar.setMaximumWidth(80)
        boton_editar.clicked.connect(lambda: self.abrir_dialogo_editar_usuario(usuario['id_usuario']))
        layout.addWidget(boton_editar)
        
        # Botón Resetear Contraseña
        boton_reset = Boton("🔑 Reset", "neutro")
        boton_reset.setMaximumWidth(80)
        boton_reset.clicked.connect(lambda: self.abrir_dialogo_resetear_contrasena(usuario['id_usuario']))
        layout.addWidget(boton_reset)
        
        # Botón Activar/Desactivar
        if usuario['activo']:
            boton_estado = Boton("❌", "peligro")
            boton_estado.setToolTip("Desactivar usuario")
            boton_estado.clicked.connect(lambda: self.cambiar_estado_usuario(usuario['id_usuario'], False))
        else:
            boton_estado = Boton("✅", "exito")
            boton_estado.setToolTip("Activar usuario")
            boton_estado.clicked.connect(lambda: self.cambiar_estado_usuario(usuario['id_usuario'], True))
        
        boton_estado.setMaximumWidth(50)
        layout.addWidget(boton_estado)
        
        # Botón Historial
        boton_historial = Boton("📋", "primario")
        boton_historial.setToolTip("Ver historial")
        boton_historial.setMaximumWidth(50)
        boton_historial.clicked.connect(lambda: self.ver_historial_usuario(usuario['id_usuario']))
        layout.addWidget(boton_historial)
        
        widget.setLayout(layout)
        return widget
    
    def buscar_usuarios(self):
        """Busca usuarios según el texto ingresado"""
        self.cargar_usuarios()
    
    def actualizar_estadisticas(self):
        """Actualiza las tarjetas de estadísticas"""
        # Recargar estadísticas
        stats = ModuloUsuarios.obtener_estadisticas_usuarios()
        
        # Actualizar valores (esto requeriría acceso a las tarjetas)
        # Por simplicidad, se puede implementar recargando toda la ventana
        # O guardando referencias a las etiquetas de valor
    
    def abrir_dialogo_nuevo_usuario(self):
        """Abre el diálogo para crear un nuevo usuario"""
        dialogo = DialogoNuevoUsuario(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_usuarios()
    
    def abrir_dialogo_editar_usuario(self, id_usuario):
        """Abre el diálogo para editar un usuario"""
        dialogo = DialogoEditarUsuario(id_usuario, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_usuarios()
    
    def abrir_dialogo_resetear_contrasena(self, id_usuario):
        """Abre el diálogo para resetear contraseña"""
        dialogo = DialogoResetearContrasena(id_usuario, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_usuarios()
    
    def cambiar_estado_usuario(self, id_usuario, activar):
        """Cambia el estado de un usuario (activo/inactivo)"""
        accion = "activar" if activar else "desactivar"
        
        confirmacion = Mensaje.confirmacion(
            "Confirmar acción",
            f"¿Está seguro que desea {accion} este usuario?",
            self
        )
        
        if confirmacion:
            from sistema_base.seguridad import obtener_usuario_actual
            usuario_actual = obtener_usuario_actual()
            
            exito, mensaje = ModuloUsuarios.cambiar_estado_usuario(
                id_usuario,
                activar,
                usuario_actual['id_usuario']
            )
            
            if exito:
                Mensaje.exito("Éxito", mensaje, self)
                self.cargar_usuarios()
            else:
                Mensaje.error("Error", mensaje, self)
    
    def ver_historial_usuario(self, id_usuario):
        """Muestra el historial de acciones de un usuario"""
        dialogo = DialogoHistorialUsuario(id_usuario, self)
        dialogo.exec_()
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)


class DialogoNuevoUsuario(QDialog):
    """Diálogo para crear un nuevo usuario"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Nuevo Usuario")
        self.setFixedSize(500, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Crear Nuevo Usuario", "titulo")
        layout.addWidget(titulo)
        
        layout.addSpacing(10)
        
        # Campo Nombre
        label_nombre = Etiqueta("Nombre Completo:")
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto("Ej: Juan Pérez")
        layout.addWidget(self.campo_nombre)
        
        # Campo Username
        label_username = Etiqueta("Nombre de Usuario:")
        layout.addWidget(label_username)
        
        self.campo_username = CampoTexto("Ej: jperez (sin espacios)")
        layout.addWidget(self.campo_username)
        
        # Campo Contraseña Temporal
        label_password = Etiqueta("Contraseña Temporal (6-10 caracteres):")
        layout.addWidget(label_password)
        
        layout_password = QHBoxLayout()
        self.campo_password = CampoTexto("Ej: abc123")
        layout_password.addWidget(self.campo_password, 1)
        
        boton_generar = Boton("🎲 Generar", "secundario")
        boton_generar.setMaximumWidth(100)
        boton_generar.clicked.connect(self.generar_contrasena)
        layout_password.addWidget(boton_generar)
        
        layout.addLayout(layout_password)
        
        # Info contraseña
        info_password = QLabel("💡 Solo letras y números. El usuario deberá cambiarla en su primer login.")
        info_password.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #6c757d;
                background-color: #e9ecef;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        info_password.setWordWrap(True)
        layout.addWidget(info_password)
        
        # Selección de Rol
        label_rol = Etiqueta("Rol:")
        layout.addWidget(label_rol)
        
        layout_rol = QHBoxLayout()
        
        self.radio_admin = QRadioButton("Administrador")
        self.radio_admin.setStyleSheet("QRadioButton { font-size: 10pt; }")
        layout_rol.addWidget(self.radio_admin)
        
        self.radio_tecnico = QRadioButton("Técnico")
        self.radio_tecnico.setStyleSheet("QRadioButton { font-size: 10pt; }")
        self.radio_tecnico.setChecked(True)  # Por defecto técnico
        layout_rol.addWidget(self.radio_tecnico)
        
        layout_rol.addStretch()
        
        layout.addLayout(layout_rol)
        
        # Mensaje de error
        self.label_error = Etiqueta("", "error")
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        # Espacio flexible
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_crear = Boton("Crear Usuario", "exito")
        self.boton_crear.clicked.connect(self.crear_usuario)
        layout_botones.addWidget(self.boton_crear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
        
        # Focus inicial
        self.campo_nombre.setFocus()
    
    def generar_contrasena(self):
        """Genera una contraseña temporal automática"""
        password = generar_contrasena_temporal()
        self.campo_password.setText(password)
        
        Mensaje.informacion(
            "Contraseña Generada",
            f"Contraseña temporal: {password}\n\nAnótala para dársela al usuario.",
            self
        )
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def crear_usuario(self):
        """Crea el nuevo usuario"""
        # Obtener datos
        nombre = self.campo_nombre.text().strip()
        username = self.campo_username.text().strip()
        password = self.campo_password.text()
        rol = "admin" if self.radio_admin.isChecked() else "tecnico"
        
        # Validar datos
        from modulos.usuarios import ModuloUsuarios
        es_valido, mensaje_error = ModuloUsuarios.validar_datos_usuario(
            nombre, username, password, rol
        )
        
        if not es_valido:
            self.mostrar_error(mensaje_error)
            return
        
        # Deshabilitar botón
        self.boton_crear.setEnabled(False)
        self.boton_crear.setText("Creando...")
        
        # Crear usuario
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_nuevo = ModuloUsuarios.crear_usuario_completo(
            nombre,
            username,
            password,
            rol,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito(
                "Usuario Creado",
                f"{mensaje}\n\nUsuario: {username}\nContraseña temporal: {password}\n\nEl usuario deberá cambiarla en su primer login.",
                self
            )
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_crear.setEnabled(True)
            self.boton_crear.setText("Crear Usuario")


class DialogoEditarUsuario(QDialog):
    """Diálogo para editar un usuario existente"""
    
    def __init__(self, id_usuario, parent=None):
        super().__init__(parent)
        self.id_usuario = id_usuario
        self.usuario = None
        self.foto_perfil_data = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Editar Usuario")
        self.setFixedSize(500, 620)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Editar Usuario", "titulo")
        layout.addWidget(titulo)
        
        layout.addSpacing(10)
        
        # Campo Nombre
        label_nombre = Etiqueta("Nombre Completo:")
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto()
        layout.addWidget(self.campo_nombre)
        
        # Username (solo lectura)
        label_username = Etiqueta("Nombre de Usuario:")
        layout.addWidget(label_username)
        
        self.campo_username = CampoTexto()
        self.campo_username.setEnabled(False)
        layout.addWidget(self.campo_username)
        
        # Selección de Rol
        label_rol = Etiqueta("Rol:")
        layout.addWidget(label_rol)
        
        layout_rol = QHBoxLayout()
        
        self.radio_admin = QRadioButton("Administrador")
        self.radio_admin.setStyleSheet("QRadioButton { font-size: 10pt; }")
        layout_rol.addWidget(self.radio_admin)
        
        self.radio_tecnico = QRadioButton("Técnico")
        self.radio_tecnico.setStyleSheet("QRadioButton { font-size: 10pt; }")
        layout_rol.addWidget(self.radio_tecnico)
        
        layout_rol.addStretch()
        
        layout.addLayout(layout_rol)
        
        # Foto de perfil
        layout.addSpacing(15)
        label_foto = Etiqueta("Foto de Perfil:")
        layout.addWidget(label_foto)
        
        layout_foto = QHBoxLayout()
        
        # Preview de la foto
        self.label_foto_preview = QLabel()
        self.label_foto_preview.setFixedSize(80, 80)
        self.label_foto_preview.setStyleSheet("""
            border: 2px solid #cbd5e1;
            border-radius: 40px;
            background-color: #f1f5f9;
        """)
        self.label_foto_preview.setAlignment(Qt.AlignCenter)
        layout_foto.addWidget(self.label_foto_preview)
        
        # Botón cambiar foto
        boton_cambiar_foto = QPushButton("📷 Cambiar Foto")
        boton_cambiar_foto.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        boton_cambiar_foto.clicked.connect(self.cambiar_foto)
        boton_cambiar_foto.setCursor(Qt.PointingHandCursor)
        layout_foto.addWidget(boton_cambiar_foto)
        
        # Botón quitar foto
        boton_quitar_foto = QPushButton("🗑️ Quitar")
        boton_quitar_foto.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        boton_quitar_foto.clicked.connect(self.quitar_foto)
        boton_quitar_foto.setCursor(Qt.PointingHandCursor)
        layout_foto.addWidget(boton_quitar_foto)
        
        layout_foto.addStretch()
        layout.addLayout(layout_foto)
        
        # Mensaje de error
        self.label_error = Etiqueta("", "error")
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        # Espacio flexible
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_guardar = Boton("Guardar Cambios", "exito")
        self.boton_guardar.clicked.connect(self.guardar_cambios)
        layout_botones.addWidget(self.boton_guardar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los datos del usuario"""
        self.usuario = ModuloUsuarios.obtener_usuario_por_id(self.id_usuario)
        
        if self.usuario:
            self.campo_nombre.setText(self.usuario['nombre'])
            self.campo_username.setText(self.usuario['username'])
            
            if self.usuario['rol'] == 'admin':
                self.radio_admin.setChecked(True)
            else:
                self.radio_tecnico.setChecked(True)
            
            # Cargar foto de perfil si existe
            if self.usuario.get('foto_perfil'):
                pixmap = QPixmap()
                pixmap.loadFromData(self.usuario['foto_perfil'])
                preview = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_foto_preview.setPixmap(preview)
                self.label_foto_preview.setScaledContents(True)
                self.foto_perfil_data = self.usuario['foto_perfil']
            else:
                self.label_foto_preview.setText("Sin foto")
                self.label_foto_preview.setStyleSheet("""
                    border: 2px solid #cbd5e1;
                    border-radius: 40px;
                    background-color: #f1f5f9;
                    color: #64748b;
                    font-size: 9pt;
                """)
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def guardar_cambios(self):
        """Guarda los cambios del usuario"""
        # Obtener datos
        nombre = self.campo_nombre.text().strip()
        rol = "admin" if self.radio_admin.isChecked() else "tecnico"
        
        # Validar nombre
        from sistema_base.validadores import validar_nombre
        es_valido, mensaje_error = validar_nombre(nombre)
        if not es_valido:
            self.mostrar_error(mensaje_error)
            return
        
        # Deshabilitar botón
        self.boton_guardar.setEnabled(False)
        self.boton_guardar.setText("Guardando...")
        
        # Guardar cambios
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloUsuarios.modificar_usuario(
            self.id_usuario,
            nombre,
            rol,
            usuario_actual['id_usuario']
        )
        
        # Actualizar foto si cambió
        if exito and hasattr(self, 'foto_perfil_data') and self.foto_perfil_data is not None:
            ModuloUsuarios.actualizar_foto_perfil(self.id_usuario, self.foto_perfil_data)
        
        if exito:
            Mensaje.exito("Éxito", mensaje, self)
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_guardar.setEnabled(True)
            self.boton_guardar.setText("Guardar Cambios")
    
    def cambiar_foto(self):
        """Permite seleccionar una foto de perfil"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Foto de Perfil",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if archivo:
            try:
                # Cargar y redimensionar imagen
                pixmap = QPixmap(archivo)
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Convertir a bytes
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                pixmap.save(buffer, "PNG")
                self.foto_perfil_data = buffer.data().data()
                
                # Mostrar preview circular
                preview = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_foto_preview.setPixmap(preview)
                self.label_foto_preview.setScaledContents(True)
                
            except Exception as e:
                self.mostrar_error(f"Error al cargar la imagen: {str(e)}")
    
    def quitar_foto(self):
        """Quita la foto de perfil"""
        self.foto_perfil_data = b''  # Bytes vacíos para indicar eliminar
        self.label_foto_preview.clear()
        self.label_foto_preview.setText("Sin foto")
        self.label_foto_preview.setStyleSheet("""
            border: 2px solid #cbd5e1;
            border-radius: 40px;
            background-color: #f1f5f9;
            color: #64748b;
            font-size: 9pt;
        """)


class DialogoResetearContrasena(QDialog):
    """Diálogo para resetear la contraseña de un usuario"""
    
    def __init__(self, id_usuario, parent=None):
        super().__init__(parent)
        self.id_usuario = id_usuario
        self.usuario = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Resetear Contraseña")
        self.setFixedSize(500, 450)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Resetear Contraseña", "titulo")
        layout.addWidget(titulo)
        
        layout.addSpacing(10)
        
        # Info del usuario
        self.label_usuario = QLabel()
        self.label_usuario.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #495057;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.label_usuario)
        
        # Advertencia
        advertencia = QLabel("⚠️ Esta acción generará una nueva contraseña temporal que el usuario deberá cambiar en su próximo login.")
        advertencia.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #856404;
                background-color: #fff3cd;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ffeaa7;
            }
        """)
        advertencia.setWordWrap(True)
        layout.addWidget(advertencia)
        
        # Campo Nueva Contraseña
        label_password = Etiqueta("Nueva Contraseña Temporal (6-10 caracteres):")
        layout.addWidget(label_password)
        
        layout_password = QHBoxLayout()
        self.campo_password = CampoTexto("Ej: abc123")
        layout_password.addWidget(self.campo_password, 1)
        
        boton_generar = Boton("🎲 Generar", "secundario")
        boton_generar.setMaximumWidth(100)
        boton_generar.clicked.connect(self.generar_contrasena)
        layout_password.addWidget(boton_generar)
        
        layout.addLayout(layout_password)
        
        # Info contraseña
        info_password = QLabel("💡 Solo letras y números. Anota la contraseña para dársela al usuario.")
        info_password.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #6c757d;
                background-color: #e9ecef;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        info_password.setWordWrap(True)
        layout.addWidget(info_password)
        
        # Mensaje de error
        self.label_error = Etiqueta("", "error")
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        # Espacio flexible
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_resetear = Boton("Resetear Contraseña", "peligro")
        self.boton_resetear.clicked.connect(self.resetear_contrasena)
        layout_botones.addWidget(self.boton_resetear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
        
        # Focus inicial
        self.campo_password.setFocus()
    
    def cargar_datos(self):
        """Carga los datos del usuario"""
        self.usuario = ModuloUsuarios.obtener_usuario_por_id(self.id_usuario)
        
        if self.usuario:
            self.label_usuario.setText(
                f"Usuario: {self.usuario['username']} ({self.usuario['nombre']})"
            )
    
    def generar_contrasena(self):
        """Genera una contraseña temporal automática"""
        password = generar_contrasena_temporal()
        self.campo_password.setText(password)
        
        Mensaje.informacion(
            "Contraseña Generada",
            f"Contraseña temporal: {password}\n\nAnótala para dársela al usuario.",
            self
        )
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def resetear_contrasena(self):
        """Resetea la contraseña del usuario"""
        # Obtener contraseña
        password = self.campo_password.text()
        
        # Validar contraseña
        from sistema_base.seguridad import validar_contrasena_temporal
        es_valida, mensaje_error = validar_contrasena_temporal(password)
        if not es_valida:
            self.mostrar_error(mensaje_error)
            return
        
        # Confirmar acción
        confirmacion = Mensaje.confirmacion(
            "Confirmar Reseteo",
            f"¿Está seguro que desea resetear la contraseña de {self.usuario['username']}?\n\nEl usuario deberá cambiarla en su próximo login.",
            self
        )
        
        if not confirmacion:
            return
        
        # Deshabilitar botón
        self.boton_resetear.setEnabled(False)
        self.boton_resetear.setText("Reseteando...")
        
        # Resetear contraseña
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloUsuarios.resetear_contrasena(
            self.id_usuario,
            password,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito(
                "Contraseña Reseteada",
                f"{mensaje}\n\nContraseña temporal: {password}",
                self
            )
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_resetear.setEnabled(True)
            self.boton_resetear.setText("Resetear Contraseña")


class DialogoHistorialUsuario(QDialog):
    """Diálogo para ver el historial de acciones de un usuario"""
    
    def __init__(self, id_usuario, parent=None):
        super().__init__(parent)
        self.id_usuario = id_usuario
        self.usuario = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Historial de Usuario")
        self.setMinimumSize(900, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = Etiqueta("Historial de Acciones", "titulo")
        layout.addWidget(titulo)
        
        # Info del usuario
        self.label_usuario = QLabel()
        self.label_usuario.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #495057;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.label_usuario)
        
        # Tabla de historial
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha/Hora", "Acción", "Módulo", "Campo", "Anterior", "Nuevo", "Crítica"
        ])
        
        # Configurar tabla
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        
        # Configurar ancho de columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.tabla.setStyleSheet(Estilos.tabla())
        
        layout.addWidget(self.tabla, 1)
        
        # Botón cerrar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los datos del usuario y su historial"""
        # Cargar usuario
        self.usuario = ModuloUsuarios.obtener_usuario_por_id(self.id_usuario)
        
        if self.usuario:
            self.label_usuario.setText(
                f"Usuario: {self.usuario['username']} ({self.usuario['nombre']}) - Últimas 50 acciones"
            )
        
        # Cargar historial
        historial = ModuloUsuarios.obtener_historial_usuario(self.id_usuario, 50)
        
        # Llenar tabla
        self.tabla.setRowCount(0)
        
        for accion in historial:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            
            # Fecha/Hora
            fecha_str = accion['fecha_hora']
            if isinstance(fecha_str, str):
                try:
                    from datetime import datetime
                    fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    fecha_formateada = fecha.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    fecha_formateada = fecha_str
            else:
                fecha_formateada = str(fecha_str)
            
            self.tabla.setItem(fila, 0, QTableWidgetItem(fecha_formateada))
            
            # Acción
            self.tabla.setItem(fila, 1, QTableWidgetItem(accion['accion'] or ""))
            
            # Módulo
            self.tabla.setItem(fila, 2, QTableWidgetItem(accion['modulo'] or ""))
            
            # Campo
            self.tabla.setItem(fila, 3, QTableWidgetItem(accion['campo_modificado'] or "-"))
            
            # Valor anterior
            self.tabla.setItem(fila, 4, QTableWidgetItem(accion['valor_anterior'] or "-"))
            
            # Valor nuevo
            self.tabla.setItem(fila, 5, QTableWidgetItem(accion['valor_nuevo'] or "-"))
            
            # Crítica
            if accion['es_accion_critica']:
                item_critica = QTableWidgetItem("⚠️ SÍ")
                item_critica.setForeground(QColor("#dc3545"))
            else:
                item_critica = QTableWidgetItem("-")
            
            self.tabla.setItem(fila, 6, item_critica)
