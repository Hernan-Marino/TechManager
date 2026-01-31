# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE REPUESTOS/INVENTARIO
============================================================================
Ventana de gestión de inventario de repuestos
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, CampoTextoMultilinea,
                                              ListaDesplegable)
from interfaz.estilos.estilos import Estilos
from modulos.repuestos import ModuloRepuestos
from modulos.equipos import ModuloEquipos
from sistema_base.configuracion import config
from sistema_base.utilidades import formatear_dinero


class VentanaRepuestos(QWidget):
    """Ventana principal de gestión de repuestos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_repuestos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tarjetas estadísticas
        tarjetas = self.crear_tarjetas_estadisticas()
        layout.addWidget(tarjetas)
        
        # Tabla
        self.tabla = self.crear_tabla_repuestos()
        layout.addWidget(self.tabla, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
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
        

        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar por nombre, modelo...")
        self.campo_busqueda.textChanged.connect(self.buscar_repuestos)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Filtro tipo repuesto
        self.combo_tipo_repuesto = ListaDesplegable()
        self.combo_tipo_repuesto.addItem("Todos los tipos", "")
        for tipo in ModuloRepuestos.TIPOS_REPUESTOS:
            self.combo_tipo_repuesto.addItem(tipo, tipo)
        self.combo_tipo_repuesto.currentIndexChanged.connect(self.cargar_repuestos)
        layout.addWidget(self.combo_tipo_repuesto)
        
        # Filtro origen
        self.combo_origen = ListaDesplegable()
        self.combo_origen.addItem("Todos", "")
        self.combo_origen.addItem("Nuevos", "Nuevo")
        self.combo_origen.addItem("Recuperados", "Recuperado")
        self.combo_origen.currentIndexChanged.connect(self.cargar_repuestos)
        layout.addWidget(self.combo_origen)
        
        # Botones
        boton_nuevo = Boton("➕ Agregar Repuesto", "exito")
        boton_nuevo.clicked.connect(self.abrir_dialogo_agregar)
        layout.addWidget(boton_nuevo)
        
        boton_actualizar = Boton("🔄 Actualizar", "secundario")
        boton_actualizar.clicked.connect(self.cargar_repuestos)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tarjetas_estadisticas(self):
        """Crea tarjetas de estadísticas"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        stats = ModuloRepuestos.obtener_estadisticas_repuestos()
        
        # Total items
        t1 = self.crear_tarjeta("Items Diferentes", str(stats['total_items']), "#3498db")
        layout.addWidget(t1)
        
        # Total unidades
        t2 = self.crear_tarjeta("Total Unidades", str(stats['total_unidades']), "#17a2b8")
        layout.addWidget(t2)
        
        # Stock bajo
        t3 = self.crear_tarjeta("Stock Bajo", str(stats['stock_bajo']), "#ffc107")
        layout.addWidget(t3)
        
        # Sin stock
        t4 = self.crear_tarjeta("Sin Stock", str(stats['sin_stock']), "#dc3545")
        layout.addWidget(t4)
        
        # Valor total
        t5 = self.crear_tarjeta("Valor Total", formatear_dinero(stats['valor_total']), "#28a745")
        layout.addWidget(t5)
        
        contenedor.setLayout(layout)
        return contenedor
    
    def crear_tarjeta(self, titulo, valor, color):
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
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            font-size: {Estilos.TAMANO_SM}pt;
            color: {Estilos.COLOR_GRIS_600};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            font-weight: 500;
            border: none;
        """)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            font-size: 26pt;
            font-weight: 700;
            color: {color};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
            padding: 4px 0px;
        """)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_repuestos(self):
        """Crea la tabla de repuestos"""
        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Modelos", "Origen", "Stock", "Precio Ref.", "Acciones"
        ])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        tabla.setColumnWidth(7, 200)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_repuestos(self):
        """Carga los repuestos"""
        try:
            busqueda = self.campo_busqueda.text().strip()
            filtro_tipo = self.combo_tipo_repuesto.currentData()
            filtro_origen = self.combo_origen.currentData()
            
            repuestos = ModuloRepuestos.listar_repuestos(
                filtro_tipo_repuesto=filtro_tipo,
                filtro_origen=filtro_origen,
                busqueda=busqueda
            )
            
            self.tabla.setRowCount(0)
            
            for repuesto in repuestos:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(repuesto['id_repuesto'])))
                
                # Nombre
                self.tabla.setItem(fila, 1, QTableWidgetItem(repuesto['nombre']))
                
                # Tipo
                self.tabla.setItem(fila, 2, QTableWidgetItem(repuesto['tipo_repuesto']))
                
                # Modelos
                modelos = repuesto['modelos_compatibles'] if repuesto['modelos_compatibles'] else "-"
                self.tabla.setItem(fila, 3, QTableWidgetItem(modelos))
                
                # Origen
                item_origen = QTableWidgetItem(repuesto['origen'])
                if repuesto['origen'] == "Nuevo":
                    item_origen.setForeground(QColor("#28a745"))
                else:
                    item_origen.setForeground(QColor("#17a2b8"))
                self.tabla.setItem(fila, 4, item_origen)
                
                # Stock
                item_stock = QTableWidgetItem(str(repuesto['cantidad_disponible']))
                if repuesto['stock_bajo']:
                    item_stock.setForeground(QColor("#dc3545"))
                    item_stock.setText(f"⚠️ {repuesto['cantidad_disponible']}")
                self.tabla.setItem(fila, 5, item_stock)
                
                # Precio
                self.tabla.setItem(fila, 6, QTableWidgetItem(formatear_dinero(repuesto['precio_referencia'])))
                
                # Acciones
                widget_acciones = self.crear_botones_acciones(repuesto)
                self.tabla.setCellWidget(fila, 7, widget_acciones)
        
        except Exception as e:
            config.guardar_log(f"Error al cargar repuestos: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar repuestos: {str(e)}", self)
    
    def crear_botones_acciones(self, repuesto):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver
        boton_ver = Boton("👁️ Ver", "primario")
        boton_ver.setMaximumWidth(70)
        boton_ver.clicked.connect(lambda: self.ver_detalle(repuesto['id_repuesto']))
        layout.addWidget(boton_ver)
        
        # Botón Editar
        boton_editar = Boton("✏️", "secundario")
        boton_editar.setToolTip("Editar repuesto")
        boton_editar.setMaximumWidth(50)
        boton_editar.clicked.connect(lambda: self.editar_repuesto(repuesto['id_repuesto']))
        layout.addWidget(boton_editar)
        
        # Botón Historial
        boton_historial = Boton("📋", "neutro")
        boton_historial.setToolTip("Ver historial de uso")
        boton_historial.setMaximumWidth(50)
        boton_historial.clicked.connect(lambda: self.ver_historial(repuesto['id_repuesto']))
        layout.addWidget(boton_historial)
        
        widget.setLayout(layout)
        return widget
    
    def buscar_repuestos(self):
        """Busca repuestos"""
        self.cargar_repuestos()
    
    def abrir_dialogo_agregar(self):
        """Abre diálogo para agregar repuesto"""
        dialogo = DialogoAgregarRepuesto(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_repuestos()
    
    def ver_detalle(self, id_repuesto):
        """Ver detalle del repuesto"""
        dialogo = DialogoDetalleRepuesto(id_repuesto, self)
        dialogo.exec_()
    
    def editar_repuesto(self, id_repuesto):
        """Editar repuesto"""
        dialogo = DialogoEditarRepuesto(id_repuesto, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_repuestos()
    
    def ver_historial(self, id_repuesto):
        """Ver historial de uso"""
        dialogo = DialogoHistorialRepuesto(id_repuesto, self)
        dialogo.exec_()


class DialogoAgregarRepuesto(QDialog):
    """Diálogo para agregar repuesto"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.equipo_origen = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Agregar Repuesto")
        self.setFixedSize(650, 750)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Agregar Repuesto al Inventario", "titulo")
        layout.addWidget(titulo)
        
        # Nombre
        label_nombre = Etiqueta("Nombre del Repuesto: *")
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto("Ej: Pantalla LCD, Batería...")
        layout.addWidget(self.campo_nombre)
        
        # Tipo repuesto
        label_tipo = Etiqueta("Tipo de Repuesto: *")
        layout.addWidget(label_tipo)
        
        self.combo_tipo = ListaDesplegable()
        for tipo in ModuloRepuestos.TIPOS_REPUESTOS:
            self.combo_tipo.addItem(tipo, tipo)
        layout.addWidget(self.combo_tipo)
        
        # Tipo dispositivo
        label_dispositivo = Etiqueta("Tipo de Dispositivo: *")
        layout.addWidget(label_dispositivo)
        
        self.combo_dispositivo = ListaDesplegable()
        for tipo in ModuloRepuestos.TIPOS_DISPOSITIVOS:
            self.combo_dispositivo.addItem(tipo, tipo)
        layout.addWidget(self.combo_dispositivo)
        
        # Modelos compatibles
        label_modelos = Etiqueta("Modelos Compatibles:")
        layout.addWidget(label_modelos)
        
        self.campo_modelos = CampoTexto("Ej: Galaxy S20, S21...")
        layout.addWidget(self.campo_modelos)
        
        # Origen
        label_origen = Etiqueta("Origen: *")
        layout.addWidget(label_origen)
        
        layout_origen = QHBoxLayout()
        self.combo_origen = ListaDesplegable()
        self.combo_origen.addItem("Nuevo", "Nuevo")
        self.combo_origen.addItem("Recuperado", "Recuperado")
        self.combo_origen.currentIndexChanged.connect(self.cambio_origen)
        layout_origen.addWidget(self.combo_origen)
        layout.addLayout(layout_origen)
        
        # Equipo origen (si es recuperado)
        self.label_equipo_origen = QLabel()
        self.label_equipo_origen.setVisible(False)
        layout.addWidget(self.label_equipo_origen)
        
        self.boton_buscar_equipo = Boton("🔍 Buscar Equipo Origen", "secundario")
        self.boton_buscar_equipo.clicked.connect(self.buscar_equipo_origen)
        self.boton_buscar_equipo.setVisible(False)
        layout.addWidget(self.boton_buscar_equipo)
        
        # Cantidad
        label_cantidad = Etiqueta("Cantidad: *")
        layout.addWidget(label_cantidad)
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(9999)
        self.spin_cantidad.setValue(1)
        layout.addWidget(self.spin_cantidad)
        
        # Estado
        label_estado = Etiqueta("Estado: *")
        layout.addWidget(label_estado)
        
        self.combo_estado = ListaDesplegable()
        for estado in ModuloRepuestos.ESTADOS_REPUESTO:
            self.combo_estado.addItem(estado, estado)
        layout.addWidget(self.combo_estado)
        
        # Precio referencia
        label_precio = Etiqueta("Precio de Referencia: *")
        layout.addWidget(label_precio)
        
        layout_precio = QHBoxLayout()
        layout_precio.addWidget(QLabel("$"))
        self.campo_precio = CampoTexto("0.00")
        layout_precio.addWidget(self.campo_precio)
        layout.addLayout(layout_precio)
        
        # Notas
        label_notas = Etiqueta("Notas:")
        layout.addWidget(label_notas)
        
        self.campo_notas = CampoTextoMultilinea("Notas adicionales...")
        layout.addWidget(self.campo_notas)
        
        # Error
        self.label_error = Etiqueta("", "error")
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_agregar = Boton("Agregar Repuesto", "exito")
        self.boton_agregar.clicked.connect(self.agregar_repuesto)
        layout_botones.addWidget(self.boton_agregar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cambio_origen(self):
        """Maneja el cambio de origen"""
        es_recuperado = self.combo_origen.currentData() == "Recuperado"
        self.label_equipo_origen.setVisible(es_recuperado)
        self.boton_buscar_equipo.setVisible(es_recuperado)
    
    def buscar_equipo_origen(self):
        """Busca equipo de donde se recuperó"""
        from PyQt5.QtWidgets import QInputDialog
        texto, ok = QInputDialog.getText(self, "Buscar Equipo", "Buscar equipo por marca, modelo:")
        
        if ok and texto:
            equipos = ModuloEquipos.listar_equipos(busqueda=texto)
            if equipos:
                # Simplificado: tomar el primero
                self.equipo_origen = equipos[0]
                self.label_equipo_origen.setText(f"✅ Equipo: {equipos[0]['marca']} {equipos[0]['modelo']}")
                self.label_equipo_origen.setStyleSheet("color: #28a745; font-weight: bold;")
    
    def agregar_repuesto(self):
        """Agrega el repuesto"""
        nombre = self.campo_nombre.text().strip()
        if not nombre:
            self.label_error.setText("El nombre es obligatorio")
            self.label_error.setVisible(True)
            return
        
        try:
            precio = float(self.campo_precio.text().strip().replace(",", "."))
            if precio < 0:
                raise ValueError()
        except:
            self.label_error.setText("El precio debe ser un número válido")
            self.label_error.setVisible(True)
            return
        
        # Si es recuperado y no seleccionó equipo
        if self.combo_origen.currentData() == "Recuperado" and not self.equipo_origen:
            self.label_error.setText("Debes seleccionar el equipo de donde se recuperó")
            self.label_error.setVisible(True)
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_nuevo = ModuloRepuestos.agregar_repuesto(
            nombre,
            self.combo_tipo.currentData(),
            self.combo_dispositivo.currentData(),
            self.campo_modelos.text().strip(),
            self.combo_origen.currentData(),
            self.equipo_origen['id_equipo'] if self.equipo_origen else None,
            self.spin_cantidad.value(),
            self.combo_estado.currentData(),
            precio,
            self.campo_notas.toPlainText().strip(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Repuesto Agregado", mensaje, self)
            self.accept()
        else:
            self.label_error.setText(mensaje)
            self.label_error.setVisible(True)


class DialogoEditarRepuesto(QDialog):
    """Diálogo para editar repuesto"""
    
    def __init__(self, id_repuesto, parent=None):
        super().__init__(parent)
        self.id_repuesto = id_repuesto
        self.repuesto = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Editar Repuesto")
        self.setFixedSize(550, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Editar Repuesto", "titulo")
        layout.addWidget(titulo)
        
        # Nombre
        label_nombre = Etiqueta("Nombre:")
        layout.addWidget(label_nombre)
        
        self.campo_nombre = CampoTexto()
        layout.addWidget(self.campo_nombre)
        
        # Modelos
        label_modelos = Etiqueta("Modelos Compatibles:")
        layout.addWidget(label_modelos)
        
        self.campo_modelos = CampoTexto()
        layout.addWidget(self.campo_modelos)
        
        # Cantidad
        label_cantidad = Etiqueta("Cantidad:")
        layout.addWidget(label_cantidad)
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(0)
        self.spin_cantidad.setMaximum(9999)
        layout.addWidget(self.spin_cantidad)
        
        # Estado
        label_estado = Etiqueta("Estado:")
        layout.addWidget(label_estado)
        
        self.combo_estado = ListaDesplegable()
        for estado in ModuloRepuestos.ESTADOS_REPUESTO:
            self.combo_estado.addItem(estado, estado)
        layout.addWidget(self.combo_estado)
        
        # Precio
        label_precio = Etiqueta("Precio Referencia:")
        layout.addWidget(label_precio)
        
        layout_precio = QHBoxLayout()
        layout_precio.addWidget(QLabel("$"))
        self.campo_precio = CampoTexto()
        layout_precio.addWidget(self.campo_precio)
        layout.addLayout(layout_precio)
        
        # Notas
        label_notas = Etiqueta("Notas:")
        layout.addWidget(label_notas)
        
        self.campo_notas = CampoTextoMultilinea()
        layout.addWidget(self.campo_notas)
        
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
        """Carga datos del repuesto"""
        self.repuesto = ModuloRepuestos.obtener_repuesto_por_id(self.id_repuesto)
        
        if self.repuesto:
            self.campo_nombre.setText(self.repuesto['nombre'])
            self.campo_modelos.setText(self.repuesto['modelos_compatibles'] if self.repuesto['modelos_compatibles'] else "")
            self.spin_cantidad.setValue(self.repuesto['cantidad_disponible'])
            
            index = self.combo_estado.findData(self.repuesto['estado'])
            if index >= 0:
                self.combo_estado.setCurrentIndex(index)
            
            self.campo_precio.setText(str(self.repuesto['precio_referencia']))
            self.campo_notas.setPlainText(self.repuesto['notas'] if self.repuesto['notas'] else "")
    
    def guardar_cambios(self):
        """Guarda los cambios"""
        try:
            precio = float(self.campo_precio.text().strip().replace(",", "."))
        except:
            Mensaje.error("Error", "El precio debe ser un número válido", self)
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloRepuestos.modificar_repuesto(
            self.id_repuesto,
            self.campo_nombre.text().strip(),
            self.campo_modelos.text().strip(),
            self.spin_cantidad.value(),
            self.combo_estado.currentData(),
            precio,
            self.campo_notas.toPlainText().strip(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Cambios Guardados", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)


class DialogoDetalleRepuesto(QDialog):
    """Diálogo para ver detalle de repuesto"""
    
    def __init__(self, id_repuesto, parent=None):
        super().__init__(parent)
        self.id_repuesto = id_repuesto
        self.repuesto = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle del Repuesto")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        self.frame_datos = QFrame()
        self.frame_datos.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout_datos = QVBoxLayout()
        
        self.label_info = QLabel()
        self.label_info.setWordWrap(True)
        layout_datos.addWidget(self.label_info)
        
        self.frame_datos.setLayout(layout_datos)
        layout.addWidget(self.frame_datos)
        
        layout.addStretch()
        
        # Botón cerrar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos"""
        self.repuesto = ModuloRepuestos.obtener_repuesto_por_id(self.id_repuesto)
        
        if not self.repuesto:
            return
        
        self.label_titulo.setText(self.repuesto['nombre'])
        
        texto = f"<b>ID:</b> {self.repuesto['id_repuesto']}<br>"
        texto += f"<b>Tipo:</b> {self.repuesto['tipo_repuesto']}<br>"
        texto += f"<b>Para:</b> {self.repuesto['tipo_dispositivo']}<br>"
        texto += f"<b>Modelos compatibles:</b> {self.repuesto['modelos_compatibles'] if self.repuesto['modelos_compatibles'] else 'N/A'}<br>"
        texto += f"<b>Origen:</b> {self.repuesto['origen']}<br>"
        texto += f"<b>Stock disponible:</b> {self.repuesto['cantidad_disponible']}<br>"
        texto += f"<b>Estado:</b> {self.repuesto['estado']}<br>"
        texto += f"<b>Precio referencia:</b> {formatear_dinero(self.repuesto['precio_referencia'])}<br>"
        
        if self.repuesto['notas']:
            texto += f"<b>Notas:</b> {self.repuesto['notas']}"
        
        self.label_info.setText(texto)


class DialogoHistorialRepuesto(QDialog):
    """Diálogo para ver historial de uso de repuesto"""
    
    def __init__(self, id_repuesto, parent=None):
        super().__init__(parent)
        self.id_repuesto = id_repuesto
        self.inicializar_ui()
        self.cargar_historial()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Historial de Uso")
        self.setMinimumSize(800, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = Etiqueta("Historial de Uso del Repuesto", "titulo")
        layout.addWidget(titulo)
        
        # Tabla historial
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Orden", "Cliente", "Equipo", "Cantidad"
        ])
        
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
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
    
    def cargar_historial(self):
        """Carga el historial"""
        historial = ModuloRepuestos.obtener_historial_uso(self.id_repuesto)
        
        self.tabla.setRowCount(0)
        
        for uso in historial:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            
            # Fecha
            try:
                from datetime import datetime
                fecha = datetime.fromisoformat(str(uso['fecha_uso']).replace('Z', '+00:00'))
                fecha_texto = fecha.strftime('%d/%m/%Y %H:%M')
            except:
                fecha_texto = str(uso['fecha_uso'])
            self.tabla.setItem(fila, 0, QTableWidgetItem(fecha_texto))
            
            # Orden
            self.tabla.setItem(fila, 1, QTableWidgetItem(f"N° {uso['id_orden']}"))
            
            # Cliente
            self.tabla.setItem(fila, 2, QTableWidgetItem(uso['cliente_nombre']))
            
            # Equipo
            equipo = f"{uso['tipo_dispositivo']} {uso['marca']} {uso['modelo']}"
            self.tabla.setItem(fila, 3, QTableWidgetItem(equipo))
            
            # Cantidad
            self.tabla.setItem(fila, 4, QTableWidgetItem(str(uso['cantidad_usada'])))

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

