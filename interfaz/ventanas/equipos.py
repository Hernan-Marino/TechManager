# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ MÓDULO DE EQUIPOS
============================================================================
Ventana de gestión de equipos/dispositivos
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QComboBox, QScrollArea,
                             QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, CampoTextoMultilinea,
                                              ListaDesplegable)
from interfaz.estilos.estilos import Estilos
from modulos.equipos_LOGICA import ModuloEquipos
from modulos.clientes import ModuloClientes
from sistema_base.configuracion import config


class VentanaEquipos(QWidget):
    """Ventana principal de gestión de equipos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_equipos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(20)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Título con fondo blanco
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("📱 Gestión de Equipos", "titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_titulo.addWidget(titulo)
        
        frame_titulo.setLayout(layout_titulo)
        layout_principal.addWidget(frame_titulo)
        
        # Barra de herramientas superior
        barra_herramientas = self.crear_barra_herramientas()
        layout_principal.addWidget(barra_herramientas)
        
        # Tabla de equipos
        self.tabla = self.crear_tabla_equipos()
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
        # Botón Volver
        boton_volver = Boton("← Volver", "primario")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Campo de búsqueda
        self.campo_busqueda = CampoTexto("Buscar por marca, modelo, identificador, cliente...")
        self.campo_busqueda.textChanged.connect(self.buscar_equipos)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Filtro por estado (por defecto: solo equipos en taller, sin entregados)
        self.combo_estado = ListaDesplegable()
        self.combo_estado.addItem("En taller (pendientes de entrega)", ModuloEquipos.FILTRO_EN_TALLER)
        self.combo_estado.addItem("Todos los estados", "")
        for estado in ModuloEquipos.ESTADOS_EQUIPOS:
            self.combo_estado.addItem(estado, estado)
        self.combo_estado.currentIndexChanged.connect(self.cargar_equipos)
        layout.addWidget(self.combo_estado)
        
        # Filtro por tipo
        self.combo_tipo = ListaDesplegable()
        self.combo_tipo.addItem("Todos los tipos", "")
        for tipo in ModuloEquipos.TIPOS_DISPOSITIVOS:
            self.combo_tipo.addItem(tipo, tipo)
        self.combo_tipo.currentIndexChanged.connect(self.cargar_equipos)
        layout.addWidget(self.combo_tipo)
        
        # Botón Ingresar Equipo
        boton_nuevo = Boton("➕ Ingresar Equipo", "exito")
        boton_nuevo.clicked.connect(self.abrir_dialogo_ingresar_equipo)
        layout.addWidget(boton_nuevo)
        
        # Botón Actualizar
        boton_actualizar = Boton("🔄 Actualizar", "primario")
        boton_actualizar.clicked.connect(self.cargar_equipos)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def crear_tarjetas_estadisticas(self):
        """Crea las tarjetas con estadísticas de equipos"""
        contenedor = QWidget()
        contenedor.setStyleSheet("QWidget { border: none; }")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Obtener estadísticas
        stats = ModuloEquipos.obtener_estadisticas_equipos()
        
        # Tarjeta Total
        tarjeta_total = self.crear_tarjeta_estadistica(
            "Total de Equipos",
            str(stats['total']),
            "#3498db"
        )
        layout.addWidget(tarjeta_total)
        
        # Tarjeta En Reparación
        tarjeta_reparacion = self.crear_tarjeta_estadistica(
            "En Reparación",
            str(stats.get('en_reparación', 0)),
            "#ffc107"
        )
        layout.addWidget(tarjeta_reparacion)
        
        # Tarjeta Listos
        tarjeta_listos = self.crear_tarjeta_estadistica(
            "Listos para Retirar",
            str(stats.get('listo', 0)),
            "#28a745"
        )
        layout.addWidget(tarjeta_listos)
        
        # Tarjeta Estancados
        tarjeta_estancados = self.crear_tarjeta_estadistica(
            "Estancados (+48hs)",
            str(stats.get('estancados', 0)),
            "#dc3545"
        )
        layout.addWidget(tarjeta_estancados)
        
        # Tarjeta Entregados
        tarjeta_entregados = self.crear_tarjeta_estadistica(
            "Entregados",
            str(stats.get('entregado', 0)),
            "#6c757d"
        )
        layout.addWidget(tarjeta_entregados)
        
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
    
    def crear_tabla_equipos(self):
        """Crea la tabla de equipos"""
        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Tipo", "Marca", "Modelo", "Estado", 
            "Días", "Ingreso"
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
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Cliente
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Marca
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Modelo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Días
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Ingreso
        
        # Aplicar estilos
        tabla.setStyleSheet(Estilos.tabla())
        
        # Conectar doble clic para ver detalles
        tabla.cellDoubleClicked.connect(lambda fila: self.ver_detalle_equipo_desde_tabla(fila))
        
        return tabla
    
    def ver_detalle_equipo_desde_tabla(self, fila):
        """Abre el detalle del equipo desde la tabla"""
        try:
            id_equipo = int(self.tabla.item(fila, 0).text())
            self.ver_detalle_equipo(id_equipo)
        except Exception as e:
            config.guardar_log(f"Error al abrir detalle: {e}", "ERROR")
    
    def cargar_equipos(self):
        """Carga los equipos en la tabla"""
        try:
            # Obtener filtros
            busqueda = self.campo_busqueda.text().strip()
            filtro_estado = self.combo_estado.currentData()
            filtro_tipo = self.combo_tipo.currentData()
            
            # Obtener equipos ("En taller" excluye entregados; "Entregado" los muestra)
            equipos = ModuloEquipos.listar_equipos(
                filtro_estado=filtro_estado,
                filtro_tipo=filtro_tipo,
                busqueda=busqueda
            )
            
            # Se obtuvieron equipos
            
            # Limpiar tabla
            self.tabla.setRowCount(0)
            
            # Llenar tabla
            for equipo in equipos:
                # Procesando equipo
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # ID
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(equipo['id_equipo'])))
                
                # Cliente
                item_cliente = QTableWidgetItem(equipo['cliente_nombre'])
                # Si cliente tiene deudas, marcar en rojo
                if equipo['tiene_incobrables']:
                    item_cliente.setForeground(QColor("#dc3545"))
                    item_cliente.setText(f"⚠️ {equipo['cliente_nombre']}")
                self.tabla.setItem(fila, 1, item_cliente)
                
                # Tipo
                self.tabla.setItem(fila, 2, QTableWidgetItem(equipo['tipo_dispositivo']))
                
                # Marca
                self.tabla.setItem(fila, 3, QTableWidgetItem(equipo['marca']))
                
                # Modelo
                self.tabla.setItem(fila, 4, QTableWidgetItem(equipo['modelo']))
                
                # Estado
                item_estado = QTableWidgetItem(equipo['estado_actual'])
                # Color según estado
                if equipo['estado_actual'] == "Listo":
                    item_estado.setForeground(QColor("#28a745"))
                elif equipo['estado_actual'] == "En reparación":
                    item_estado.setForeground(QColor("#ffc107"))
                elif equipo['estado_actual'] == "Abandonado":
                    item_estado.setForeground(QColor("#6c757d"))
                elif equipo['estado_actual'] == "Sin reparación":
                    item_estado.setForeground(QColor("#dc3545"))
                
                self.tabla.setItem(fila, 5, item_estado)
                
                # Días sin movimiento
                dias = equipo['dias_sin_movimiento']
                item_dias = QTableWidgetItem(str(dias))
                
                # Alertas visuales
                if equipo['alerta_abandonado']:
                    item_dias.setForeground(QColor("#dc3545"))
                    item_dias.setText(f"🚨 {dias}")
                    item_dias.setToolTip("Más de 90 días sin movimiento")
                elif equipo['alerta_estancado']:
                    item_dias.setForeground(QColor("#ffc107"))
                    item_dias.setText(f"⚠️ {dias}")
                    item_dias.setToolTip("Más de 48 horas sin movimiento")
                
                self.tabla.setItem(fila, 6, item_dias)
                
                # Fecha ingreso
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
                
                self.tabla.setItem(fila, 7, QTableWidgetItem(fecha_formateada))
            
        except Exception as e:
            import traceback
            error_completo = traceback.format_exc()
            print(f"DEBUG ERROR: {error_completo}")  # DEBUG
            config.guardar_log(f"Error al cargar equipos: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar equipos: {str(e)}", self)
    
    def buscar_equipos(self):
        """Busca equipos según el texto ingresado"""
        self.cargar_equipos()
    
    def abrir_dialogo_ingresar_equipo(self):
        """Abre el diálogo para ingresar un nuevo equipo"""
        dialogo = DialogoIngresarEquipo(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_equipos()
    
    def ver_detalle_equipo(self, id_equipo):
        """Muestra el detalle completo de un equipo"""
        dialogo = DialogoDetalleEquipo(id_equipo, self)
        dialogo.exec_()
        self.cargar_equipos()  # Recargar por si hubo cambios
    
    def cambiar_estado(self, id_equipo):
        """Abre diálogo para cambiar el estado de un equipo"""
        dialogo = DialogoCambiarEstado(id_equipo, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_equipos()
    
    def ver_remito(self, id_equipo):
        """Muestra el remito del equipo"""
        Mensaje.informacion(
            "Ver Remito",
            "Funcionalidad de visualización de remitos próximamente.",
            self
        )
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)


class DialogoIngresarEquipo(QDialog):
    """Diálogo para ingresar un nuevo equipo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cliente_seleccionado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Ingresar Equipo")
        self.setMinimumSize(700, 750)
        self.setModal(True)
        
        # Scroll area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        widget_contenido = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Ingresar Nuevo Equipo", "titulo")
        layout.addWidget(titulo)
        
        layout.addSpacing(10)
        
        # SECCIÓN: CLIENTE
        label_seccion_cliente = Etiqueta("1. SELECCIONAR CLIENTE", "subtitulo")
        layout.addWidget(label_seccion_cliente)
        
        layout_cliente = QHBoxLayout()
        
        self.campo_buscar_cliente = CampoTexto("Buscar cliente por nombre o teléfono...")
        layout_cliente.addWidget(self.campo_buscar_cliente, 1)
        
        boton_buscar = Boton("🔍 Buscar", "primario")
        boton_buscar.clicked.connect(self.buscar_cliente)
        layout_cliente.addWidget(boton_buscar)
        
        layout.addLayout(layout_cliente)
        
        # Info cliente seleccionado
        self.label_cliente = QLabel("No se ha seleccionado ningún cliente")
        self.label_cliente.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                color: #6c757d;
            }
        """)
        layout.addWidget(self.label_cliente)
        
        layout.addSpacing(10)
        
        # SECCIÓN: DATOS DEL EQUIPO
        label_seccion_equipo = Etiqueta("2. DATOS DEL EQUIPO", "subtitulo")
        layout.addWidget(label_seccion_equipo)
        
        # Tipo de dispositivo
        label_tipo = Etiqueta("Tipo de Dispositivo: *")
        layout.addWidget(label_tipo)
        
        self.combo_tipo = ListaDesplegable()
        for tipo in ModuloEquipos.TIPOS_DISPOSITIVOS:
            self.combo_tipo.addItem(tipo, tipo)
        layout.addWidget(self.combo_tipo)
        
        # Marca
        label_marca = Etiqueta("Marca: *")
        layout.addWidget(label_marca)
        
        self.campo_marca = CampoTexto("Ej: Samsung, Apple, HP...")
        layout.addWidget(self.campo_marca)
        
        # Modelo
        label_modelo = Etiqueta("Modelo: *")
        layout.addWidget(label_modelo)
        
        self.campo_modelo = CampoTexto("Ej: Galaxy S21, iPhone 13, Pavilion...")
        layout.addWidget(self.campo_modelo)
        
        # Identificador (IMEI, Serial, etc.)
        label_identificador = Etiqueta("Identificador (IMEI, Serial, etc.):")
        layout.addWidget(label_identificador)
        
        self.campo_identificador = CampoTexto("Opcional - Ej: 123456789012345")
        layout.addWidget(self.campo_identificador)
        
        # Color
        label_color = Etiqueta("Color:")
        layout.addWidget(label_color)
        
        self.campo_color = CampoTexto("Ej: Negro, Blanco, Azul...")
        layout.addWidget(self.campo_color)
        
        layout.addSpacing(10)
        
        # SECCIÓN: ESTADO FÍSICO Y ACCESORIOS
        label_seccion_estado = Etiqueta("3. ESTADO Y ACCESORIOS", "subtitulo")
        layout.addWidget(label_seccion_estado)
        
        # Estado físico
        label_estado_fisico = Etiqueta("Estado Físico:")
        layout.addWidget(label_estado_fisico)
        
        self.campo_estado_fisico = CampoTextoMultilinea("Descripción de rayones, roturas, golpes, etc.")
        layout.addWidget(self.campo_estado_fisico)
        
        # Accesorios
        label_accesorios = Etiqueta("Accesorios:")
        layout.addWidget(label_accesorios)
        
        self.campo_accesorios = CampoTextoMultilinea("Ej: Cargador, funda, auriculares...")
        layout.addWidget(self.campo_accesorios)
        
        layout.addSpacing(10)
        
        # SECCIÓN: FALLA
        label_seccion_falla = Etiqueta("4. FALLA DECLARADA", "subtitulo")
        layout.addWidget(label_seccion_falla)
        
        label_falla = Etiqueta("Falla Declarada por el Cliente: *")
        layout.addWidget(label_falla)
        
        self.campo_falla = CampoTextoMultilinea("Descripción detallada de la falla...")
        layout.addWidget(self.campo_falla)
        
        # Mensaje de error
        self.label_error = Etiqueta("", "error")
        self.label_error.setVisible(False)
        layout.addWidget(self.label_error)
        
        # Espacio flexible
        layout.addStretch()
        
        widget_contenido.setLayout(layout)
        scroll.setWidget(widget_contenido)
        
        # Layout principal con scroll y botones
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.addWidget(scroll, 1)
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.setContentsMargins(20, 10, 20, 20)
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_ingresar = Boton("Ingresar Equipo", "exito")
        self.boton_ingresar.clicked.connect(self.ingresar_equipo)
        layout_botones.addWidget(self.boton_ingresar)
        
        layout_principal.addLayout(layout_botones)
        
        self.setLayout(layout_principal)
    
    def buscar_cliente(self):
        """Busca un cliente por nombre o teléfono"""
        busqueda = self.campo_buscar_cliente.text().strip()
        
        if not busqueda:
            Mensaje.advertencia("Búsqueda Vacía", "Ingresa un nombre o teléfono para buscar", self)
            return
        
        # Buscar clientes
        clientes = ModuloClientes.listar_clientes(busqueda=busqueda)
        
        if not clientes:
            Mensaje.informacion("Sin Resultados", "No se encontraron clientes con ese criterio", self)
            return
        
        # Si hay un solo cliente, seleccionarlo automáticamente
        if len(clientes) == 1:
            self.seleccionar_cliente(clientes[0])
            return
        
        # Si hay varios, mostrar diálogo de selección
        dialogo = DialogoSeleccionarCliente(clientes, self)
        if dialogo.exec_() == QDialog.Accepted and dialogo.cliente_seleccionado:
            self.seleccionar_cliente(dialogo.cliente_seleccionado)
    
    def seleccionar_cliente(self, cliente):
        """Selecciona un cliente"""
        self.cliente_seleccionado = cliente
        
        # Actualizar label
        texto = f"✅ Cliente: {cliente['nombre']}\n"
        texto += f"Teléfono: {cliente['telefono']}"
        if cliente['direccion']:
            texto += f"\nDirección: {cliente['direccion']}"
        
        self.label_cliente.setText(texto)
        self.label_cliente.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                color: #155724;
                font-weight: bold;
            }
        """)
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def ingresar_equipo(self):
        """Ingresa el equipo al sistema"""
        # Validar cliente
        if not self.cliente_seleccionado:
            self.mostrar_error("Debes seleccionar un cliente primero")
            return
        
        # Obtener datos
        tipo_dispositivo = self.combo_tipo.currentData()
        marca = self.campo_marca.text().strip()
        modelo = self.campo_modelo.text().strip()
        identificador = self.campo_identificador.text().strip()
        color = self.campo_color.text().strip()
        estado_fisico = self.campo_estado_fisico.toPlainText().strip()
        accesorios = self.campo_accesorios.toPlainText().strip()
        falla_declarada = self.campo_falla.toPlainText().strip()
        
        # Validar datos
        if not marca:
            self.mostrar_error("La marca es obligatoria")
            return
        
        if not modelo:
            self.mostrar_error("El modelo es obligatorio")
            return
        
        if not falla_declarada:
            self.mostrar_error("La falla declarada es obligatoria")
            return
        
        # Deshabilitar botón
        self.boton_ingresar.setEnabled(False)
        self.boton_ingresar.setText("Ingresando...")
        
        # Ingresar equipo
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_nuevo = ModuloEquipos.ingresar_equipo(
            self.cliente_seleccionado['id_cliente'],
            tipo_dispositivo,
            marca,
            modelo,
            identificador,
            color,
            estado_fisico,
            accesorios,
            falla_declarada,
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("Equipo Ingresado", mensaje, self)
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_ingresar.setEnabled(True)
            self.boton_ingresar.setText("Ingresar Equipo")


class DialogoSeleccionarCliente(QDialog):
    """Diálogo para seleccionar un cliente de una lista"""
    
    def __init__(self, clientes, parent=None):
        super().__init__(parent)
        self.clientes = clientes
        self.cliente_seleccionado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Seleccionar Cliente")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = Etiqueta(f"Se encontraron {len(self.clientes)} clientes", "titulo")
        layout.addWidget(titulo)
        
        # Tabla de clientes
        tabla = QTableWidget()
        tabla.setColumnCount(3)
        tabla.setHorizontalHeaderLabels(["Nombre", "Teléfono", "Dirección"])
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.horizontalHeader().setStretchLastSection(True)
        tabla.setStyleSheet(Estilos.tabla())
        
        # Llenar tabla
        for cliente in self.clientes:
            fila = tabla.rowCount()
            tabla.insertRow(fila)
            
            tabla.setItem(fila, 0, QTableWidgetItem(cliente['nombre']))
            tabla.setItem(fila, 1, QTableWidgetItem(cliente['telefono']))
            tabla.setItem(fila, 2, QTableWidgetItem(cliente['direccion'] if cliente['direccion'] else "-"))
        
        tabla.doubleClicked.connect(self.seleccionar)
        
        layout.addWidget(tabla, 1)
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        boton_seleccionar = Boton("Seleccionar", "exito")
        boton_seleccionar.clicked.connect(lambda: self.seleccionar(tabla.currentRow()))
        layout_botones.addWidget(boton_seleccionar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
        self.tabla = tabla
    
    def seleccionar(self, fila=None):
        """Selecciona el cliente de la fila indicada"""
        if fila is None or fila < 0:
            fila = self.tabla.currentRow()
        
        if fila >= 0 and fila < len(self.clientes):
            self.cliente_seleccionado = self.clientes[fila]
            self.accept()


class DialogoCambiarEstado(QDialog):
    """Diálogo para cambiar el estado de un equipo"""
    
    def __init__(self, id_equipo, parent=None):
        super().__init__(parent)
        self.id_equipo = id_equipo
        self.equipo = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Cambiar Estado del Equipo")
        self.setFixedSize(550, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Cambiar Estado del Equipo", "titulo")
        layout.addWidget(titulo)
        
        # Info del equipo
        self.label_equipo = QLabel()
        self.label_equipo.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #495057;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.label_equipo.setWordWrap(True)
        layout.addWidget(self.label_equipo)
        
        # Estado actual
        layout_estado_actual = QHBoxLayout()
        layout_estado_actual.addWidget(QLabel("<b>Estado Actual:</b>"))
        self.label_estado_actual = QLabel()
        self.label_estado_actual.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout_estado_actual.addWidget(self.label_estado_actual)
        layout_estado_actual.addStretch()
        layout.addLayout(layout_estado_actual)
        
        # Nuevo estado
        label_nuevo = Etiqueta("Nuevo Estado: *")
        layout.addWidget(label_nuevo)
        
        self.combo_estado = ListaDesplegable()
        for estado in ModuloEquipos.ESTADOS_EQUIPOS:
            self.combo_estado.addItem(estado, estado)
        layout.addWidget(self.combo_estado)
        
        # Observaciones
        label_obs = Etiqueta("Observaciones:")
        layout.addWidget(label_obs)
        
        self.campo_observaciones = CampoTextoMultilinea("Detalles del cambio...")
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
        
        self.boton_cambiar = Boton("Cambiar Estado", "exito")
        self.boton_cambiar.clicked.connect(self.cambiar_estado)
        layout_botones.addWidget(self.boton_cambiar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los datos del equipo"""
        self.equipo = ModuloEquipos.obtener_equipo_por_id(self.id_equipo)
        
        if self.equipo:
            self.label_equipo.setText(
                f"{self.equipo['tipo_dispositivo']} {self.equipo['marca']} {self.equipo['modelo']}"
            )
            self.label_estado_actual.setText(self.equipo['estado_actual'])
            
            # Preseleccionar el estado actual
            index = self.combo_estado.findData(self.equipo['estado_actual'])
            if index >= 0:
                self.combo_estado.setCurrentIndex(index)
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.label_error.setText(mensaje)
        self.label_error.setVisible(True)
    
    def cambiar_estado(self):
        """Cambia el estado del equipo"""
        nuevo_estado = self.combo_estado.currentData()
        observaciones = self.campo_observaciones.toPlainText().strip()
        
        # Verificar si es el mismo estado
        if nuevo_estado == self.equipo['estado_actual']:
            self.mostrar_error("El equipo ya está en ese estado")
            return
        
        # Deshabilitar botón
        self.boton_cambiar.setEnabled(False)
        self.boton_cambiar.setText("Cambiando...")
        
        # Cambiar estado
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloEquipos.cambiar_estado_equipo(
            self.id_equipo,
            nuevo_estado,
            usuario_actual['id_usuario'],
            observaciones
        )
        
        if exito:
            Mensaje.exito("Estado Cambiado", mensaje, self)
            self.accept()
        else:
            self.mostrar_error(mensaje)
            self.boton_cambiar.setEnabled(True)
            self.boton_cambiar.setText("Cambiar Estado")




# FRAGMENTO PARA REEMPLAZAR EN equipos.py - DialogoDetalleEquipo

class DialogoDetalleEquipo(QDialog):
    """Diálogo para ver/editar el detalle completo de un equipo"""
    
    def __init__(self, id_equipo, parent=None):
        super().__init__(parent)
        self.id_equipo = id_equipo
        self.equipo = None
        self.cliente = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Detalle del Equipo")
        self.setMinimumSize(900, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título con nombre del cliente
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Datos principales del equipo (en recuadros horizontales)
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
        
        # Pestaña Datos del Equipo
        self.widget_equipo = self.crear_tab_equipo()
        tabs.addTab(self.widget_equipo, "📱 Datos del Equipo")
        
        # Pestaña Estado y Diagnóstico
        self.widget_estado = self.crear_tab_estado()
        tabs.addTab(self.widget_estado, "🔧 Estado y Diagnóstico")
        
        layout.addWidget(tabs, 1)
        
        # Botones de acción
        layout_botones = QHBoxLayout()
        
        boton_guardar = Boton("💾 Guardar Cambios", "exito")
        boton_guardar.clicked.connect(self.guardar_cambios)
        layout_botones.addWidget(boton_guardar)
        
        if config.es_admin:
            boton_eliminar = Boton("🗑️ Eliminar Equipo", "peligro")
            boton_eliminar.clicked.connect(self.eliminar_equipo)
            layout_botones.addWidget(boton_eliminar)
        
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def crear_frame_datos(self):
        """Crea el frame con los datos principales del equipo"""
        # Layout horizontal para todos los recuadros
        layout_principal = QHBoxLayout()
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Recuadro Tipo
        rec_tipo = self.crear_recuadro_dato("Tipo")
        self.label_tipo = QLabel()
        self.label_tipo.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px 10px;")
        rec_tipo.layout().addWidget(self.label_tipo)
        layout_principal.addWidget(rec_tipo)
        
        # Recuadro Marca
        rec_marca = self.crear_recuadro_dato("Marca")
        self.label_marca = QLabel()
        self.label_marca.setStyleSheet("font-size: 13px; padding: 5px 10px;")
        rec_marca.layout().addWidget(self.label_marca)
        layout_principal.addWidget(rec_marca, 1)
        
        # Recuadro Modelo
        rec_modelo = self.crear_recuadro_dato("Modelo")
        self.label_modelo = QLabel()
        self.label_modelo.setStyleSheet("font-size: 13px; padding: 5px 10px;")
        rec_modelo.layout().addWidget(self.label_modelo)
        layout_principal.addWidget(rec_modelo, 1)
        
        # Recuadro Estado
        rec_estado = self.crear_recuadro_dato("Estado")
        self.label_estado_visual = QLabel()
        self.label_estado_visual.setStyleSheet("font-size: 13px; padding: 5px 10px;")
        rec_estado.layout().addWidget(self.label_estado_visual)
        layout_principal.addWidget(rec_estado)
        
        # Recuadro Fecha Ingreso
        rec_fecha = self.crear_recuadro_dato("Fecha Ingreso")
        self.label_fecha = QLabel()
        self.label_fecha.setStyleSheet("font-size: 13px; padding: 5px 10px;")
        rec_fecha.layout().addWidget(self.label_fecha)
        layout_principal.addWidget(rec_fecha)
        
        # Crear widget contenedor
        widget = QWidget()
        widget.setLayout(layout_principal)
        return widget
    
    def crear_recuadro_dato(self, titulo):
        """Crea un recuadro con título y valor"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 0px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("""
            background-color: #f8f9fa;
            color: #495057;
            font-size: 11px;
            font-weight: bold;
            padding: 5px 10px;
            border-bottom: 1px solid #dee2e6;
        """)
        layout.addWidget(label_titulo)
        
        frame.setLayout(layout)
        return frame
    
    def crear_tab_equipo(self):
        """Crea la pestaña con datos del equipo"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        layout_scroll = QVBoxLayout()
        layout_scroll.setSpacing(15)
        
        # Sección: Datos del Equipo
        layout_scroll.addWidget(Etiqueta("📱 DATOS DEL EQUIPO", "subtitulo"))
        
        # Tipo y Marca en horizontal
        h1 = QHBoxLayout()
        h1.setSpacing(10)
        
        # Tipo
        v_tipo = QVBoxLayout()
        v_tipo.setSpacing(2)
        v_tipo.addWidget(QLabel("Tipo de Dispositivo:"))
        self.combo_tipo = ListaDesplegable()
        self.combo_tipo.addItem("Celular", "Celular")
        self.combo_tipo.addItem("Tablet", "Tablet")
        self.combo_tipo.addItem("Notebook", "Notebook")
        self.combo_tipo.addItem("PC", "PC")
        self.combo_tipo.addItem("Consola", "Consola")
        self.combo_tipo.addItem("Otro", "Otro")
        v_tipo.addWidget(self.combo_tipo)
        h1.addLayout(v_tipo, 1)
        
        # Marca
        v_marca = QVBoxLayout()
        v_marca.setSpacing(2)
        v_marca.addWidget(QLabel("Marca:"))
        self.campo_marca = CampoTexto()
        v_marca.addWidget(self.campo_marca)
        h1.addLayout(v_marca, 1)
        
        layout_scroll.addLayout(h1)
        
        # Modelo e Identificador
        h2 = QHBoxLayout()
        h2.setSpacing(10)
        
        # Modelo
        v_modelo = QVBoxLayout()
        v_modelo.setSpacing(2)
        v_modelo.addWidget(QLabel("Modelo:"))
        self.campo_modelo = CampoTexto()
        v_modelo.addWidget(self.campo_modelo)
        h2.addLayout(v_modelo, 1)
        
        # Identificador
        v_id = QVBoxLayout()
        v_id.setSpacing(2)
        v_id.addWidget(QLabel("IMEI/Serie:"))
        self.campo_identificador = CampoTexto()
        v_id.addWidget(self.campo_identificador)
        h2.addLayout(v_id, 1)
        
        layout_scroll.addLayout(h2)
        
        # Color
        v_color = QVBoxLayout()
        v_color.setSpacing(2)
        v_color.addWidget(QLabel("Color:"))
        self.campo_color = CampoTexto()
        v_color.addWidget(self.campo_color)
        layout_scroll.addLayout(v_color)
        
        # Accesorios (label e input juntos para que no quede título espaciado del input)
        layout_scroll.addWidget(Etiqueta("📦 ACCESORIOS", "subtitulo"))
        v_accesorios = QVBoxLayout()
        v_accesorios.setSpacing(2)
        v_accesorios.addWidget(QLabel("Accesorios Entregados:"))
        self.campo_accesorios = CampoTextoMultilinea()
        self.campo_accesorios.setMinimumHeight(52)
        self.campo_accesorios.setMaximumHeight(65)
        v_accesorios.addWidget(self.campo_accesorios)
        layout_scroll.addLayout(v_accesorios)
        
        container.setLayout(layout_scroll)
        scroll.setWidget(container)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def crear_tab_estado(self):
        """Crea la pestaña de estado y diagnóstico"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        layout_scroll = QVBoxLayout()
        layout_scroll.setSpacing(2)  # Poco espacio entre label e input para que no se crucen
        
        # Estado Actual
        layout_scroll.addWidget(QLabel("Estado Actual:"))
        self.combo_estado = ListaDesplegable()
        self.combo_estado.addItem("En revisión", "En revisión")
        self.combo_estado.addItem("Esperando presupuesto", "Esperando presupuesto")
        self.combo_estado.addItem("Presupuesto aprobado", "Presupuesto aprobado")
        self.combo_estado.addItem("En reparación", "En reparación")
        self.combo_estado.addItem("Listo", "Listo")
        self.combo_estado.addItem("Entregado", "Entregado")
        self.combo_estado.addItem("Sin reparación", "Sin reparación")
        self.combo_estado.addItem("Abandonado", "Abandonado")
        layout_scroll.addWidget(self.combo_estado)
        
        layout_scroll.addSpacing(6)
        
        # Falla Declarada (altura doble para más espacio de texto)
        layout_scroll.addWidget(QLabel("Falla Declarada:"))
        self.campo_falla = CampoTextoMultilinea()
        self.campo_falla.setMinimumHeight(104)
        self.campo_falla.setMaximumHeight(130)
        layout_scroll.addWidget(self.campo_falla)
        
        layout_scroll.addSpacing(6)
        
        # Diagnóstico Técnico
        layout_scroll.addWidget(QLabel("Diagnóstico Técnico:"))
        self.campo_diagnostico = CampoTextoMultilinea()
        self.campo_diagnostico.setMinimumHeight(104)
        self.campo_diagnostico.setMaximumHeight(130)
        layout_scroll.addWidget(self.campo_diagnostico)
        
        layout_scroll.addSpacing(6)
        
        # Solución Aplicada
        layout_scroll.addWidget(QLabel("Solución Aplicada:"))
        self.campo_solucion = CampoTextoMultilinea()
        self.campo_solucion.setMinimumHeight(104)
        self.campo_solucion.setMaximumHeight(130)
        layout_scroll.addWidget(self.campo_solucion)
        
        layout_scroll.addSpacing(6)
        
        # Observaciones Internas
        layout_scroll.addWidget(QLabel("Observaciones Internas:"))
        self.campo_observaciones = CampoTextoMultilinea()
        self.campo_observaciones.setMinimumHeight(104)
        self.campo_observaciones.setMaximumHeight(130)
        layout_scroll.addWidget(self.campo_observaciones)
        
        layout_scroll.addStretch()
        
        container.setLayout(layout_scroll)
        scroll.setWidget(container)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    
    def cargar_datos(self):
        """Carga los datos del equipo"""
        self.equipo = ModuloEquipos.obtener_equipo_por_id(self.id_equipo)
        
        if not self.equipo:
            Mensaje.error("No se pudo cargar el equipo", self)
            self.reject()
            return
        
        # Cargar cliente
        self.cliente = ModuloClientes.obtener_cliente_por_id(self.equipo['id_cliente'])
        
        # Título
        cliente_nombre = f"{self.cliente['apellido']}, {self.cliente['nombre']}" if self.cliente else "Cliente desconocido"
        self.label_titulo.setText(cliente_nombre)
        
        # Datos visuales
        self.label_tipo.setText(self.equipo.get('tipo_dispositivo', '-'))
        self.label_marca.setText(self.equipo.get('marca', '-'))
        self.label_modelo.setText(self.equipo.get('modelo', '-'))
        self.label_estado_visual.setText(self.equipo.get('estado_actual', '-'))
        
        fecha_ingreso = self.equipo.get('fecha_ingreso')
        if fecha_ingreso:
            from datetime import datetime
            if isinstance(fecha_ingreso, str):
                fecha_obj = datetime.fromisoformat(fecha_ingreso.replace('Z', '+00:00'))
            else:
                fecha_obj = fecha_ingreso
            self.label_fecha.setText(fecha_obj.strftime('%d/%m/%Y'))
        else:
            self.label_fecha.setText('-')
        
        # Campos editables
        self.combo_tipo.setCurrentText(self.equipo.get('tipo_dispositivo', ''))
        self.campo_marca.setText(self.equipo.get('marca', ''))
        self.campo_modelo.setText(self.equipo.get('modelo', ''))
        self.campo_identificador.setText(self.equipo.get('identificador', ''))
        self.campo_color.setText(self.equipo.get('color', ''))
        self.campo_accesorios.setPlainText(self.equipo.get('accesorios', ''))
        
        self.combo_estado.setCurrentText(self.equipo.get('estado_actual', 'En revisión'))
        self.campo_falla.setPlainText(self.equipo.get('falla_declarada', ''))
        self.campo_diagnostico.setPlainText(self.equipo.get('diagnostico_tecnico', ''))
        self.campo_solucion.setPlainText(self.equipo.get('solucion_aplicada', ''))
        self.campo_observaciones.setPlainText(self.equipo.get('observaciones_internas', ''))
    
    def guardar_cambios(self):
        """Guarda los cambios del equipo"""
        # Recopilar datos
        datos = {
            'tipo_dispositivo': self.combo_tipo.currentText(),
            'marca': self.campo_marca.text().strip(),
            'modelo': self.campo_modelo.text().strip(),
            'identificador': self.campo_identificador.text().strip(),
            'color': self.campo_color.text().strip(),
            'estado_actual': self.combo_estado.currentText(),
            'falla_declarada': self.campo_falla.toPlainText().strip(),
            'diagnostico': self.campo_diagnostico.toPlainText().strip(),
            'solucion': self.campo_solucion.toPlainText().strip(),
            'accesorios': self.campo_accesorios.toPlainText().strip(),
            'observaciones_internas': self.campo_observaciones.toPlainText().strip()
        }
        
        # Obtener usuario actual
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        id_usuario = usuario_actual['id_usuario'] if usuario_actual else 1
        
        # Guardar
        exito, mensaje = ModuloEquipos.modificar_equipo(
            self.id_equipo,
            datos,
            id_usuario
        )
        
        if exito:
            Mensaje.exito("Cambios guardados", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def eliminar_equipo(self):
        """Elimina el equipo"""
        confirmacion = Mensaje.confirmacion(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar este equipo?\n\nEsta acción no se puede deshacer.",
            self
        )
        
        if not confirmacion:
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        id_usuario = usuario_actual['id_usuario'] if usuario_actual else 1
        
        exito, mensaje = ModuloEquipos.eliminar_equipo(self.id_equipo, id_usuario)
        
        if exito:
            Mensaje.exito("Equipo eliminado", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)

