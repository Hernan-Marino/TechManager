# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE CLIENTES
============================================================================
Ventana de gestión de clientes del sistema
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, CampoTextoMultilinea)
from interfaz.estilos.estilos import Estilos
from modulos.clientes import ModuloClientes
from sistema_base.configuracion import config
from sistema_base.utilidades import formatear_dinero


class VentanaClientes(QWidget):
    """Ventana principal de gestión de clientes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_clientes()
    
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
        
        # Tabla de clientes
        self.tabla = self.crear_tabla_clientes()
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
        # Botón Volver al Dashboard
        boton_volver = Boton("← Volver al Dashboard", "neutro")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Campo de búsqueda
        self.campo_busqueda = CampoTexto("Buscar cliente por nombre, teléfono, dirección...")
        self.campo_busqueda.textChanged.connect(self.buscar_clientes)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Botón Nuevo Cliente
        boton_nuevo = Boton("➕ Nuevo Cliente", "exito")
        boton_nuevo.clicked.connect(self.abrir_dialogo_nuevo_cliente)
        layout.addWidget(boton_nuevo)
        
        # Botón Actualizar
        boton_actualizar = Boton("🔄 Actualizar", "secundario")
        boton_actualizar.clicked.connect(self.cargar_clientes)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tarjetas_estadisticas(self):
        """Crea las tarjetas con estadísticas de clientes"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Obtener estadísticas
        stats = ModuloClientes.obtener_estadisticas_clientes()
        
        # Tarjeta Total
        tarjeta_total = self.crear_tarjeta_estadistica(
            "Total de Clientes",
            str(stats['total']),
            "#3498db"
        )
        layout.addWidget(tarjeta_total)
        
        # Tarjeta Con Deudas
        tarjeta_deudas = self.crear_tarjeta_estadistica(
            "Con Deudas",
            str(stats['con_deudas']),
            "#dc3545"
        )
        layout.addWidget(tarjeta_deudas)
        
        # Tarjeta Total Incobrables
        tarjeta_monto = self.crear_tarjeta_estadistica(
            "Total Incobrables",
            formatear_dinero(stats['total_incobrables']),
            "#e74c3c"
        )
        layout.addWidget(tarjeta_monto)
        
        # Tarjeta Buenos Pagadores
        tarjeta_buenos = self.crear_tarjeta_estadistica(
            "Buenos Pagadores",
            str(stats['buenos']),
            "#28a745"
        )
        layout.addWidget(tarjeta_buenos)
        
        # Tarjeta Malos Pagadores
        tarjeta_malos = self.crear_tarjeta_estadistica(
            "Malos Pagadores",
            str(stats['malos']),
            "#ffc107"
        )
        layout.addWidget(tarjeta_malos)
        
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
    
    def crear_tabla_clientes(self):
        """Crea la tabla de clientes"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Teléfono", "Dirección", "Deuda", "Confiabilidad", "Acciones"
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
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Dirección
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Deuda
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Confiabilidad
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Acciones
        tabla.setColumnWidth(6, 250)
        
        # Aplicar estilos
        tabla.setStyleSheet(Estilos.tabla())
        
        return tabla
    
    def cargar_clientes(self):
        """Carga los clientes en la tabla"""
        try:
            # Obtener búsqueda
            busqueda = self.campo_busqueda.text().strip()
            
            # Obtener clientes
            clientes = ModuloClientes.listar_clientes(busqueda=busqueda)
            
            # Limpiar tabla
            self.tabla.setRowCount(0)
            
            # Llenar tabla
            for cliente in clientes:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(cliente['id_cliente'])))
                
                # Nombre
                item_nombre = QTableWidgetItem(cliente['nombre'])
                # Si tiene deudas, marcar en rojo
                if cliente['tiene_incobrables']:
                    item_nombre.setForeground(QColor("#dc3545"))
                    item_nombre.setText(f"⚠️ {cliente['nombre']}")
                self.tabla.setItem(fila, 1, item_nombre)
                
                # Teléfono
                self.tabla.setItem(fila, 2, QTableWidgetItem(cliente['telefono']))
                
                # Dirección
                direccion = cliente['direccion'] if cliente['direccion'] else "-"
                self.tabla.setItem(fila, 3, QTableWidgetItem(direccion))
                
                # Deuda
                if cliente['tiene_incobrables']:
                    item_deuda = QTableWidgetItem(formatear_dinero(cliente['total_incobrables']))
                    item_deuda.setForeground(QColor("#dc3545"))
                else:
                    item_deuda = QTableWidgetItem("-")
                self.tabla.setItem(fila, 4, item_deuda)
                
                # Confiabilidad
                confiabilidad = cliente['confiabilidad_pago']
                item_conf = QTableWidgetItem(confiabilidad)
                
                if confiabilidad == "Bueno":
                    item_conf.setForeground(QColor("#28a745"))
                elif confiabilidad == "Regular":
                    item_conf.setForeground(QColor("#ffc107"))
                elif confiabilidad == "Malo":
                    item_conf.setForeground(QColor("#dc3545"))
                
                self.tabla.setItem(fila, 5, item_conf)
                
                # Botones de acciones
                widget_acciones = self.crear_botones_acciones(cliente)
                self.tabla.setCellWidget(fila, 6, widget_acciones)
            
        except Exception as e:
            config.guardar_log(f"Error al cargar clientes: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar clientes: {str(e)}", self)
    
    def crear_botones_acciones(self, cliente):
        """Crea los botones de acciones para cada fila"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver Detalle
        boton_detalle = Boton("👁️ Ver", "primario")
        boton_detalle.setMaximumWidth(70)
        boton_detalle.clicked.connect(lambda: self.ver_detalle_cliente(cliente['id_cliente']))
        layout.addWidget(boton_detalle)
        
        # Botón Editar
        boton_editar = Boton("✏️ Editar", "secundario")
        boton_editar.setMaximumWidth(80)
        boton_editar.clicked.connect(lambda: self.abrir_dialogo_editar_cliente(cliente['id_cliente']))
        layout.addWidget(boton_editar)
        
        # Botón Marcar Incobrable (solo admin)
        if config.es_admin:
            boton_incobrable = Boton("💰", "peligro")
            boton_incobrable.setToolTip("Marcar deuda incobrable")
            boton_incobrable.setMaximumWidth(50)
            boton_incobrable.clicked.connect(lambda: self.marcar_incobrable(cliente['id_cliente']))
            layout.addWidget(boton_incobrable)
        
        widget.setLayout(layout)
        return widget
    
    def buscar_clientes(self):
        """Busca clientes según el texto ingresado"""
        self.cargar_clientes()
    
    def abrir_dialogo_nuevo_cliente(self):
        """Abre el diálogo para crear un nuevo cliente"""
        dialogo = DialogoNuevoCliente(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_clientes()
    
    def abrir_dialogo_editar_cliente(self, id_cliente):
        """Abre el diálogo para editar un cliente"""
        dialogo = DialogoEditarCliente(id_cliente, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_clientes()
    
    def ver_detalle_cliente(self, id_cliente):
        """Muestra el detalle completo de un cliente"""
        dialogo = DialogoDetalleCliente(id_cliente, self)
        dialogo.exec_()
    
    def marcar_incobrable(self, id_cliente):
        """Marca una deuda como incobrable"""
        dialogo = DialogoMarcarIncobrable(id_cliente, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_clientes()


class DialogoNuevoCliente(QDialog):
    """Diálogo para crear un nuevo cliente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Nuevo Cliente")
        self.setFixedSize(550, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Crear Nuevo Cliente", "titulo")
        layout.addWidget(titulo)
        
        layout.addSpacing(10)
        
        # Campo Nombre
        label_nombre = Etiqueta("Nombre Completo: *")
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto("Ej: Juan Pérez")
        layout.addWidget(self.campo_nombre)
        
        # Campo Teléfono
        label_telefono = Etiqueta("Teléfono: *")
        layout.addWidget(label_telefono)
        
        self.campo_telefono = CampoTexto("Ej: 221-555-1234")
        layout.addWidget(self.campo_telefono)
        
        # Campo Dirección
        label_direccion = Etiqueta("Dirección:")
        layout.addWidget(label_direccion)
        
        self.campo_direccion = CampoTexto("Ej: Calle 50 N° 123")
        layout.addWidget(self.campo_direccion)
        
        # Campo Email
        label_email = Etiqueta("Email:")
        layout.addWidget(label_email)
        
        self.campo_email = CampoTexto("Ej: cliente@email.com")
        layout.addWidget(self.campo_email)
        
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
        
        self.boton_crear = Boton("Crear Cliente", "exito")
        self.boton_crear.clicked.connect(self.crear_cliente)
        layout_botones.addWidget(self.boton_crear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
        
        # Focus inicial
        self.campo_nombre.setFocus()
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def crear_cliente(self):
        """Crea el nuevo cliente"""
        # Obtener datos
        nombre = self.campo_nombre.text().strip()
        telefono = self.campo_telefono.text().strip()
        direccion = self.campo_direccion.text().strip()
        email = self.campo_email.text().strip()
        
        # Validar datos
        if not nombre:
            self.mostrar_error("El nombre es obligatorio")
            return
        
        if not telefono:
            self.mostrar_error("El teléfono es obligatorio")
            return
        
        # Deshabilitar botón
        self.boton_crear.setEnabled(False)
        self.boton_crear.setText("Creando...")
        
        # Crear cliente
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_nuevo = ModuloClientes.crear_cliente(
            nombre,
            telefono,
            direccion,
            email,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Cliente Creado", mensaje, self)
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_crear.setEnabled(True)
            self.boton_crear.setText("Crear Cliente")


class DialogoEditarCliente(QDialog):
    """Diálogo para editar un cliente existente"""
    
    def __init__(self, id_cliente, parent=None):
        super().__init__(parent)
        self.id_cliente = id_cliente
        self.cliente = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Editar Cliente")
        self.setFixedSize(550, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Editar Cliente", "titulo")
        layout.addWidget(titulo)
        
        layout.addSpacing(10)
        
        # Campo Nombre
        label_nombre = Etiqueta("Nombre Completo: *")
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto()
        layout.addWidget(self.campo_nombre)
        
        # Campo Teléfono
        label_telefono = Etiqueta("Teléfono: *")
        layout.addWidget(label_telefono)
        
        self.campo_telefono = CampoTexto()
        layout.addWidget(self.campo_telefono)
        
        # Campo Dirección
        label_direccion = Etiqueta("Dirección:")
        layout.addWidget(label_direccion)
        
        self.campo_direccion = CampoTexto()
        layout.addWidget(self.campo_direccion)
        
        # Campo Email
        label_email = Etiqueta("Email:")
        layout.addWidget(label_email)
        
        self.campo_email = CampoTexto()
        layout.addWidget(self.campo_email)
        
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
        """Carga los datos del cliente"""
        self.cliente = ModuloClientes.obtener_cliente_por_id(self.id_cliente)
        
        if self.cliente:
            self.campo_nombre.setText(self.cliente['nombre'])
            self.campo_telefono.setText(self.cliente['telefono'])
            self.campo_direccion.setText(self.cliente['direccion'] if self.cliente['direccion'] else "")
            self.campo_email.setText(self.cliente['email'] if self.cliente['email'] else "")
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def guardar_cambios(self):
        """Guarda los cambios del cliente"""
        # Obtener datos
        nombre = self.campo_nombre.text().strip()
        telefono = self.campo_telefono.text().strip()
        direccion = self.campo_direccion.text().strip()
        email = self.campo_email.text().strip()
        
        # Validar datos
        if not nombre:
            self.mostrar_error("El nombre es obligatorio")
            return
        
        if not telefono:
            self.mostrar_error("El teléfono es obligatorio")
            return
        
        # Deshabilitar botón
        self.boton_guardar.setEnabled(False)
        self.boton_guardar.setText("Guardando...")
        
        # Guardar cambios
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloClientes.modificar_cliente(
            self.id_cliente,
            nombre,
            telefono,
            direccion,
            email,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Éxito", mensaje, self)
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_guardar.setEnabled(True)
            self.boton_guardar.setText("Guardar Cambios")


class DialogoMarcarIncobrable(QDialog):
    """Diálogo para marcar una deuda como incobrable"""
    
    def __init__(self, id_cliente, parent=None):
        super().__init__(parent)
        self.id_cliente = id_cliente
        self.cliente = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Marcar Deuda Incobrable")
        self.setFixedSize(550, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Marcar Deuda como Incobrable", "titulo")
        layout.addWidget(titulo)
        
        # Advertencia
        advertencia = QLabel("⚠️ ACCIÓN CRÍTICA: Esta acción quedará registrada en la auditoría del sistema.")
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
        
        # Info del cliente
        self.label_cliente = QLabel()
        self.label_cliente.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #495057;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.label_cliente)
        
        # Campo Monto
        label_monto = Etiqueta("Monto de la Deuda: *")
        layout.addWidget(label_monto)
        
        self.campo_monto = CampoTexto("Ej: 5000")
        layout.addWidget(self.campo_monto)
        
        # Campo Motivo
        label_motivo = Etiqueta("Motivo: *")
        layout.addWidget(label_motivo)
        
        self.campo_motivo = CampoTexto("Ej: Cliente desapareció, no responde llamadas")
        layout.addWidget(self.campo_motivo)
        
        # Campo Observaciones
        label_obs = Etiqueta("Observaciones Adicionales:")
        layout.addWidget(label_obs)
        
        self.campo_observaciones = CampoTextoMultilinea("Detalles adicionales...")
        layout.addWidget(self.campo_observaciones)
        
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
        
        self.boton_marcar = Boton("Marcar como Incobrable", "peligro")
        self.boton_marcar.clicked.connect(self.marcar_incobrable)
        layout_botones.addWidget(self.boton_marcar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
        
        # Focus inicial
        self.campo_monto.setFocus()
    
    def cargar_datos(self):
        """Carga los datos del cliente"""
        self.cliente = ModuloClientes.obtener_cliente_por_id(self.id_cliente)
        
        if self.cliente:
            deuda_actual = formatear_dinero(self.cliente['total_incobrables']) if self.cliente['tiene_incobrables'] else "$0,00"
            self.label_cliente.setText(
                f"Cliente: {self.cliente['nombre']}\nDeuda Actual: {deuda_actual}"
            )
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def marcar_incobrable(self):
        """Marca la deuda como incobrable"""
        # Obtener datos
        monto_texto = self.campo_monto.text().strip()
        motivo = self.campo_motivo.text().strip()
        observaciones = self.campo_observaciones.toPlainText().strip()
        
        # Validar datos
        if not monto_texto:
            self.mostrar_error("El monto es obligatorio")
            return
        
        try:
            monto = float(monto_texto.replace(",", "."))
            if monto <= 0:
                self.mostrar_error("El monto debe ser mayor a cero")
                return
        except:
            self.mostrar_error("El monto debe ser un número válido")
            return
        
        if not motivo:
            self.mostrar_error("El motivo es obligatorio")
            return
        
        # Confirmar acción
        confirmacion = Mensaje.confirmacion(
            "Confirmar Acción Crítica",
            f"¿Está seguro que desea marcar una deuda de {formatear_dinero(monto)} como incobrable para {self.cliente['nombre']}?\n\nEsta acción quedará registrada en la auditoría.",
            self
        )
        
        if not confirmacion:
            return
        
        # Deshabilitar botón
        self.boton_marcar.setEnabled(False)
        self.boton_marcar.setText("Marcando...")
        
        # Marcar incobrable
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloClientes.marcar_deuda_incobrable(
            self.id_cliente,
            monto,
            motivo,
            observaciones,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Deuda Marcada", mensaje, self)
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_marcar.setEnabled(True)
            self.boton_marcar.setText("Marcar como Incobrable")


class DialogoDetalleCliente(QDialog):
    """Diálogo para ver el detalle completo de un cliente"""
    
    def __init__(self, id_cliente, parent=None):
        super().__init__(parent)
        self.id_cliente = id_cliente
        self.cliente = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Detalle del Cliente")
        self.setMinimumSize(900, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título y datos del cliente
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Datos principales
        self.frame_datos = self.crear_frame_datos()
        layout.addWidget(self.frame_datos)
        
        # Pestañas
        from PyQt5.QtWidgets import QTabWidget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2563eb;
            }
        """)
        
        # Pestaña Equipos
        self.widget_equipos = self.crear_tab_equipos()
        tabs.addTab(self.widget_equipos, "📱 Equipos")
        
        # Pestaña Timeline de Notas
        self.widget_timeline = self.crear_tab_timeline()
        tabs.addTab(self.widget_timeline, "📝 Timeline")
        
        layout.addWidget(tabs, 1)
        
        # Botón cerrar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def crear_frame_datos(self):
        """Crea el frame con los datos principales del cliente"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Grid con datos
        from PyQt5.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Fila 1
        grid.addWidget(QLabel("<b>Teléfono:</b>"), 0, 0)
        self.label_telefono = QLabel()
        grid.addWidget(self.label_telefono, 0, 1)
        
        grid.addWidget(QLabel("<b>Email:</b>"), 0, 2)
        self.label_email = QLabel()
        grid.addWidget(self.label_email, 0, 3)
        
        # Fila 2
        grid.addWidget(QLabel("<b>Dirección:</b>"), 1, 0)
        self.label_direccion = QLabel()
        grid.addWidget(self.label_direccion, 1, 1, 1, 3)
        
        # Fila 3
        grid.addWidget(QLabel("<b>Confiabilidad:</b>"), 2, 0)
        self.label_confiabilidad = QLabel()
        grid.addWidget(self.label_confiabilidad, 2, 1)
        
        grid.addWidget(QLabel("<b>Deuda Total:</b>"), 2, 2)
        self.label_deuda = QLabel()
        grid.addWidget(self.label_deuda, 2, 3)
        
        layout.addLayout(grid)
        
        frame.setLayout(layout)
        return frame
    
    def crear_tab_equipos(self):
        """Crea la pestaña de equipos"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabla de equipos
        self.tabla_equipos = QTableWidget()
        self.tabla_equipos.setColumnCount(6)
        self.tabla_equipos.setHorizontalHeaderLabels([
            "ID", "Tipo", "Marca", "Modelo", "Estado", "Fecha Ingreso"
        ])
        
        # Configurar tabla
        self.tabla_equipos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_equipos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_equipos.verticalHeader().setVisible(False)
        self.tabla_equipos.setAlternatingRowColors(True)
        
        # Configurar ancho de columnas
        header = self.tabla_equipos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.tabla_equipos.setStyleSheet(Estilos.tabla())
        
        layout.addWidget(self.tabla_equipos)
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_timeline(self):
        """Crea la pestaña de timeline de notas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Botón agregar nota
        layout_agregar = QHBoxLayout()
        
        self.campo_nueva_nota = CampoTexto("Escribe una nota...")
        layout_agregar.addWidget(self.campo_nueva_nota, 1)
        
        boton_agregar = Boton("➕ Agregar Nota", "exito")
        boton_agregar.clicked.connect(self.agregar_nota)
        layout_agregar.addWidget(boton_agregar)
        
        layout.addLayout(layout_agregar)
        
        # Scroll area con notas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.widget_notas = QWidget()
        self.layout_notas = QVBoxLayout()
        self.layout_notas.setSpacing(10)
        self.layout_notas.setAlignment(Qt.AlignTop)
        self.widget_notas.setLayout(self.layout_notas)
        
        scroll.setWidget(self.widget_notas)
        layout.addWidget(scroll, 1)
        
        widget.setLayout(layout)
        return widget
    
    def cargar_datos(self):
        """Carga todos los datos del cliente"""
        # Cargar cliente
        self.cliente = ModuloClientes.obtener_cliente_por_id(self.id_cliente)
        
        if not self.cliente:
            return
        
        # Título
        self.label_titulo.setText(self.cliente['nombre'])
        
        # Datos principales
        self.label_telefono.setText(self.cliente['telefono'])
        self.label_email.setText(self.cliente['email'] if self.cliente['email'] else "-")
        self.label_direccion.setText(self.cliente['direccion'] if self.cliente['direccion'] else "-")
        
        # Confiabilidad
        conf = self.cliente['confiabilidad_pago']
        if conf == "Bueno":
            self.label_confiabilidad.setText(f"<span style='color: #28a745;'>{conf}</span>")
        elif conf == "Regular":
            self.label_confiabilidad.setText(f"<span style='color: #ffc107;'>{conf}</span>")
        elif conf == "Malo":
            self.label_confiabilidad.setText(f"<span style='color: #dc3545;'>{conf}</span>")
        
        # Deuda
        if self.cliente['tiene_incobrables']:
            self.label_deuda.setText(
                f"<span style='color: #dc3545; font-weight: bold;'>{formatear_dinero(self.cliente['total_incobrables'])}</span>"
            )
        else:
            self.label_deuda.setText("$0,00")
        
        # Cargar equipos
        self.cargar_equipos()
        
        # Cargar timeline
        self.cargar_timeline()
    
    def cargar_equipos(self):
        """Carga los equipos del cliente"""
        equipos = ModuloClientes.obtener_equipos_cliente(self.id_cliente)
        
        self.tabla_equipos.setRowCount(0)
        
        for equipo in equipos:
            fila = self.tabla_equipos.rowCount()
            self.tabla_equipos.insertRow(fila)
            
            self.tabla_equipos.setItem(fila, 0, QTableWidgetItem(str(equipo['id_equipo'])))
            self.tabla_equipos.setItem(fila, 1, QTableWidgetItem(equipo['tipo_dispositivo']))
            self.tabla_equipos.setItem(fila, 2, QTableWidgetItem(equipo['marca']))
            self.tabla_equipos.setItem(fila, 3, QTableWidgetItem(equipo['modelo']))
            self.tabla_equipos.setItem(fila, 4, QTableWidgetItem(equipo['estado_actual']))
            
            # Fecha
            fecha_str = equipo['fecha_ingreso']
            if isinstance(fecha_str, str):
                try:
                    from datetime import datetime
                    fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    fecha_formateada = fecha.strftime('%d/%m/%Y')
                except:
                    fecha_formateada = fecha_str
            else:
                fecha_formateada = str(fecha_str)
            
            self.tabla_equipos.setItem(fila, 5, QTableWidgetItem(fecha_formateada))
    
    def cargar_timeline(self):
        """Carga el timeline de notas"""
        # Limpiar notas anteriores
        while self.layout_notas.count():
            item = self.layout_notas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Obtener notas
        notas = ModuloClientes.obtener_notas_cliente(self.id_cliente)
        
        if not notas:
            label_sin_notas = QLabel("No hay notas registradas")
            label_sin_notas.setStyleSheet("color: #6c757d; padding: 20px;")
            label_sin_notas.setAlignment(Qt.AlignCenter)
            self.layout_notas.addWidget(label_sin_notas)
            return
        
        # Agregar cada nota
        for nota in notas:
            widget_nota = self.crear_widget_nota(nota)
            self.layout_notas.addWidget(widget_nota)
    
    def crear_widget_nota(self, nota):
        """Crea un widget para una nota"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-left: 4px solid #2563eb;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Header con usuario y fecha
        layout_header = QHBoxLayout()
        
        label_usuario = QLabel(f"<b>{nota['usuario_nombre']}</b>")
        label_usuario.setStyleSheet("color: #2563eb;")
        layout_header.addWidget(label_usuario)
        
        layout_header.addStretch()
        
        # Fecha
        fecha_str = nota['fecha_hora']
        if isinstance(fecha_str, str):
            try:
                from datetime import datetime
                fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                fecha_formateada = fecha.strftime('%d/%m/%Y %H:%M')
            except:
                fecha_formateada = fecha_str
        else:
            fecha_formateada = str(fecha_str)
        
        label_fecha = QLabel(fecha_formateada)
        label_fecha.setStyleSheet("color: #6c757d; font-size: 9pt;")
        layout_header.addWidget(label_fecha)
        
        if nota['editado']:
            label_editado = QLabel("(editado)")
            label_editado.setStyleSheet("color: #6c757d; font-size: 8pt; font-style: italic;")
            layout_header.addWidget(label_editado)
        
        layout.addLayout(layout_header)
        
        # Contenido de la nota
        label_nota = QLabel(nota['nota'])
        label_nota.setWordWrap(True)
        label_nota.setStyleSheet("color: #212529; padding: 5px 0;")
        layout.addWidget(label_nota)
        
        frame.setLayout(layout)
        return frame
    
    def agregar_nota(self):
        """Agrega una nueva nota al cliente"""
        nota_texto = self.campo_nueva_nota.text().strip()
        
        if not nota_texto:
            Mensaje.advertencia("Nota Vacía", "Escribe algo en la nota antes de agregar", self)
            return
        
        # Agregar nota
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloClientes.agregar_nota_cliente(
            self.id_cliente,
            nota_texto,
            usuario_actual['id_usuario']
        )
        
        if exito:
            self.campo_nueva_nota.clear()
            self.cargar_timeline()
        else:
            Mensaje.error("Error", mensaje, self)

    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        if self.parent():
            ventana_principal = self.parent()
            layout = ventana_principal.area_trabajo.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            dashboard = ventana_principal.crear_dashboard_completo()
            layout.addWidget(dashboard)

