# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ COMPLETA MÓDULO DE CONFIGURACIÓN
============================================================================
Panel completo de configuración del sistema
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QTabWidget, QSpinBox, QFileDialog,
                             QScrollArea, QColorDialog, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, CampoTextoMultilinea)
from modulos.configuracion import ModuloConfiguracion
from sistema_base.configuracion import config
import os


class VentanaConfiguracion(QWidget):
    """Ventana de configuración del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        # Botón Volver
        boton_volver = Boton("← Volver al Dashboard", "neutro")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout_titulo.addWidget(boton_volver)
        
        layout_titulo.addSpacing(20)
        
        titulo = Etiqueta("⚙️ Configuración del Sistema", "titulo")
        layout_titulo.addWidget(titulo)
        
        layout_titulo.addStretch()
        
        # Info
        label_info = QLabel("Configure los parámetros del sistema según sus necesidades")
        label_info.setStyleSheet("color: #6c757d; font-style: italic;")
        layout_titulo.addWidget(label_info)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Tabs con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #2563eb;
                font-weight: bold;
            }
        """)
        
        # Pestañas
        tabs.addTab(self.crear_tab_negocio(), "🏢 Negocio")
        tabs.addTab(self.crear_tab_dias(), "⏰ Días y Alertas")
        tabs.addTab(self.crear_tab_porcentajes(), "💰 Porcentajes")
        tabs.addTab(self.crear_tab_textos(), "📝 Textos")
        tabs.addTab(self.crear_tab_logos(), "🖼️ Logos")
        tabs.addTab(self.crear_tab_colores(), "🎨 Colores")
        tabs.addTab(self.crear_tab_backups(), "💾 Backups")
        tabs.addTab(self.crear_tab_avanzado(), "⚡ Avanzado")
        
        scroll.setWidget(tabs)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def crear_tab_negocio(self):
        """Tab datos del negocio"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("Datos del Negocio", "titulo")
        layout.addWidget(titulo)
        
        info = QLabel("Esta información aparecerá en remitos, presupuestos y facturas")
        info.setStyleSheet("color: #6c757d; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Campos
        layout.addWidget(QLabel("<b>Nombre del Negocio: *</b>"))
        self.campo_nombre = CampoTexto()
        self.campo_nombre.setText(config.nombre_negocio)
        layout.addWidget(self.campo_nombre)
        
        layout.addWidget(QLabel("<b>Dirección:</b>"))
        self.campo_direccion = CampoTexto()
        self.campo_direccion.setText(config.direccion_negocio)
        layout.addWidget(self.campo_direccion)
        
        layout.addWidget(QLabel("<b>Teléfono: *</b>"))
        self.campo_telefono = CampoTexto()
        self.campo_telefono.setText(config.telefono_negocio)
        layout.addWidget(self.campo_telefono)
        
        layout.addWidget(QLabel("<b>Email:</b>"))
        self.campo_email = CampoTexto()
        self.campo_email.setText(config.email_negocio)
        layout.addWidget(self.campo_email)
        
        layout.addWidget(QLabel("<b>CUIT:</b>"))
        self.campo_cuit = CampoTexto()
        self.campo_cuit.setText(config.cuit_negocio)
        layout.addWidget(self.campo_cuit)
        
        layout.addStretch()
        
        # Botón guardar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_guardar = Boton("💾 Guardar Cambios", "exito")
        boton_guardar.clicked.connect(self.guardar_datos_negocio)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_dias(self):
        """Tab días y alertas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Configuración de Días y Alertas", "titulo")
        layout.addWidget(titulo)
        
        # Equipo estancado
        frame1 = self.crear_frame_config(
            "⚠️ Días para alerta de equipo estancado:",
            "Un equipo se considerará estancado si no cambia de estado en este tiempo"
        )
        self.spin_estancado = QSpinBox()
        self.spin_estancado.setMinimum(1)
        self.spin_estancado.setMaximum(365)
        self.spin_estancado.setValue(config.dias_alerta_equipo_estancado)
        self.spin_estancado.setSuffix(" días")
        frame1.layout().addWidget(self.spin_estancado)
        layout.addWidget(frame1)
        
        # Equipo abandonado
        frame2 = self.crear_frame_config(
            "❌ Días para alerta de equipo abandonado:",
            "Un equipo se considerará abandonado si pasa este tiempo sin ser retirado"
        )
        self.spin_abandonado = QSpinBox()
        self.spin_abandonado.setMinimum(1)
        self.spin_abandonado.setMaximum(365)
        self.spin_abandonado.setValue(config.dias_alerta_equipo_abandonado)
        self.spin_abandonado.setSuffix(" días")
        frame2.layout().addWidget(self.spin_abandonado)
        layout.addWidget(frame2)
        
        # Vencimiento presupuesto
        frame3 = self.crear_frame_config(
            "📋 Días de vencimiento de presupuestos:",
            "Tiempo que el cliente tiene para aceptar o rechazar un presupuesto"
        )
        self.spin_vencimiento = QSpinBox()
        self.spin_vencimiento.setMinimum(1)
        self.spin_vencimiento.setMaximum(90)
        self.spin_vencimiento.setValue(config.dias_vencimiento_presupuesto)
        self.spin_vencimiento.setSuffix(" días")
        frame3.layout().addWidget(self.spin_vencimiento)
        layout.addWidget(frame3)
        
        # Garantía
        frame4 = self.crear_frame_config(
            "🛡️ Días de garantía de reparación:",
            "Tiempo de garantía que se ofrece al finalizar una reparación exitosa"
        )
        self.spin_garantia = QSpinBox()
        self.spin_garantia.setMinimum(1)
        self.spin_garantia.setMaximum(365)
        self.spin_garantia.setValue(config.dias_garantia_reparacion)
        self.spin_garantia.setSuffix(" días")
        frame4.layout().addWidget(self.spin_garantia)
        layout.addWidget(frame4)
        
        layout.addStretch()
        
        # Botón guardar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_guardar = Boton("💾 Guardar Cambios", "exito")
        boton_guardar.clicked.connect(self.guardar_dias)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_porcentajes(self):
        """Tab porcentajes"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Configuración de Porcentajes y Cantidades", "titulo")
        layout.addWidget(titulo)
        
        # Recargo transferencia
        frame1 = self.crear_frame_config(
            "💳 Porcentaje de recargo por transferencia:",
            "Recargo que se suma al presupuesto si el cliente paga por transferencia"
        )
        layout_recargo = QHBoxLayout()
        self.campo_recargo = CampoTexto()
        self.campo_recargo.setText(str(config.porcentaje_recargo_transferencia))
        self.campo_recargo.setMaximumWidth(100)
        layout_recargo.addWidget(self.campo_recargo)
        layout_recargo.addWidget(QLabel("%"))
        layout_recargo.addStretch()
        frame1.layout().addLayout(layout_recargo)
        layout.addWidget(frame1)
        
        # Anticipo mínimo
        frame2 = self.crear_frame_config(
            "💰 Porcentaje mínimo de anticipo:",
            "Anticipo mínimo que se solicita al aceptar un presupuesto"
        )
        layout_anticipo = QHBoxLayout()
        self.campo_anticipo = CampoTexto()
        self.campo_anticipo.setText(str(config.porcentaje_minimo_anticipo))
        self.campo_anticipo.setMaximumWidth(100)
        layout_anticipo.addWidget(self.campo_anticipo)
        layout_anticipo.addWidget(QLabel("%"))
        layout_anticipo.addStretch()
        frame2.layout().addLayout(layout_anticipo)
        layout.addWidget(frame2)
        
        # Stock mínimo
        frame3 = self.crear_frame_config(
            "📦 Cantidad mínima de stock (alerta):",
            "Cantidad mínima de repuestos antes de mostrar alerta de stock bajo"
        )
        self.spin_stock = QSpinBox()
        self.spin_stock.setMinimum(0)
        self.spin_stock.setMaximum(1000)
        self.spin_stock.setValue(config.cantidad_minima_stock_repuestos)
        self.spin_stock.setSuffix(" unidades")
        frame3.layout().addWidget(self.spin_stock)
        layout.addWidget(frame3)
        
        layout.addStretch()
        
        # Botón guardar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_guardar = Boton("💾 Guardar Cambios", "exito")
        boton_guardar.clicked.connect(self.guardar_porcentajes)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_textos(self):
        """Tab textos personalizables"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Textos Personalizables", "titulo")
        layout.addWidget(titulo)
        
        info = QLabel("Estos textos aparecen en el pie de los documentos generados")
        info.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(info)
        
        # Remito
        layout.addWidget(QLabel("<b>Texto pie de remito:</b>"))
        self.campo_texto_remito = CampoTextoMultilinea()
        self.campo_texto_remito.setPlainText(config.texto_pie_remito)
        self.campo_texto_remito.setMaximumHeight(80)
        layout.addWidget(self.campo_texto_remito)
        
        # Presupuesto
        layout.addWidget(QLabel("<b>Texto pie de presupuesto:</b>"))
        self.campo_texto_presupuesto = CampoTextoMultilinea()
        self.campo_texto_presupuesto.setPlainText(config.texto_pie_presupuesto)
        self.campo_texto_presupuesto.setMaximumHeight(80)
        layout.addWidget(self.campo_texto_presupuesto)
        
        # Garantía
        layout.addWidget(QLabel("<b>Texto de garantía:</b>"))
        self.campo_texto_garantia = CampoTextoMultilinea()
        self.campo_texto_garantia.setPlainText(config.texto_garantia)
        self.campo_texto_garantia.setMaximumHeight(80)
        layout.addWidget(self.campo_texto_garantia)
        
        layout.addStretch()
        
        # Botón guardar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_restaurar = Boton("🔄 Restaurar Textos por Defecto", "neutro")
        boton_restaurar.clicked.connect(self.restaurar_textos_defecto)
        layout_botones.addWidget(boton_restaurar)
        
        boton_guardar = Boton("💾 Guardar Cambios", "exito")
        boton_guardar.clicked.connect(self.guardar_textos)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_logos(self):
        """Tab logos"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Gestión de Logos", "titulo")
        layout.addWidget(titulo)
        
        info = QLabel("Suba los logos que se usarán en el sistema y documentos (formatos: PNG, JPG)")
        info.setStyleSheet("color: #6c757d; font-style: italic;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Logo sistema
        frame1 = QFrame()
        frame1.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout1 = QVBoxLayout()
        
        label1 = QLabel("<b style='font-size: 11pt;'>🖼️ Logo del Sistema</b>")
        layout1.addWidget(label1)
        
        info1 = QLabel("Se muestra en la ventana principal del sistema")
        info1.setStyleSheet("color: #6c757d; font-size: 9pt;")
        layout1.addWidget(info1)
        
        self.label_logo_sistema = QLabel("Sin logo")
        self.label_logo_sistema.setAlignment(Qt.AlignCenter)
        self.label_logo_sistema.setFixedSize(200, 100)
        self.label_logo_sistema.setStyleSheet("""
            QLabel {
                border: 2px dashed #dee2e6;
                border-radius: 5px;
                background-color: white;
            }
        """)
        layout1.addWidget(self.label_logo_sistema, alignment=Qt.AlignCenter)
        
        layout_btn1 = QHBoxLayout()
        boton_subir1 = Boton("📤 Subir Logo", "primario")
        boton_subir1.clicked.connect(lambda: self.subir_logo("sistema"))
        layout_btn1.addWidget(boton_subir1)
        
        boton_eliminar1 = Boton("🗑️ Eliminar", "peligro")
        boton_eliminar1.clicked.connect(lambda: self.eliminar_logo("sistema"))
        layout_btn1.addWidget(boton_eliminar1)
        layout_btn1.addStretch()
        
        layout1.addLayout(layout_btn1)
        frame1.setLayout(layout1)
        layout.addWidget(frame1)
        
        # Logo remitos
        frame2 = QFrame()
        frame2.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout2 = QVBoxLayout()
        
        label2 = QLabel("<b style='font-size: 11pt;'>📋 Logo para Remitos</b>")
        layout2.addWidget(label2)
        
        info2 = QLabel("Aparece en los remitos de ingreso impresos")
        info2.setStyleSheet("color: #6c757d; font-size: 9pt;")
        layout2.addWidget(info2)
        
        self.label_logo_remitos = QLabel("Sin logo")
        self.label_logo_remitos.setAlignment(Qt.AlignCenter)
        self.label_logo_remitos.setFixedSize(200, 100)
        self.label_logo_remitos.setStyleSheet("""
            QLabel {
                border: 2px dashed #dee2e6;
                border-radius: 5px;
                background-color: white;
            }
        """)
        layout2.addWidget(self.label_logo_remitos, alignment=Qt.AlignCenter)
        
        layout_btn2 = QHBoxLayout()
        boton_subir2 = Boton("📤 Subir Logo", "primario")
        boton_subir2.clicked.connect(lambda: self.subir_logo("remitos"))
        layout_btn2.addWidget(boton_subir2)
        
        boton_eliminar2 = Boton("🗑️ Eliminar", "peligro")
        boton_eliminar2.clicked.connect(lambda: self.eliminar_logo("remitos"))
        layout_btn2.addWidget(boton_eliminar2)
        layout_btn2.addStretch()
        
        layout2.addLayout(layout_btn2)
        frame2.setLayout(layout2)
        layout.addWidget(frame2)
        
        # Logo comprobantes
        frame3 = QFrame()
        frame3.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout3 = QVBoxLayout()
        
        label3 = QLabel("<b style='font-size: 11pt;'>📄 Logo para Comprobantes</b>")
        layout3.addWidget(label3)
        
        info3 = QLabel("Aparece en presupuestos y facturas")
        info3.setStyleSheet("color: #6c757d; font-size: 9pt;")
        layout3.addWidget(info3)
        
        self.label_logo_comprobantes = QLabel("Sin logo")
        self.label_logo_comprobantes.setAlignment(Qt.AlignCenter)
        self.label_logo_comprobantes.setFixedSize(200, 100)
        self.label_logo_comprobantes.setStyleSheet("""
            QLabel {
                border: 2px dashed #dee2e6;
                border-radius: 5px;
                background-color: white;
            }
        """)
        layout3.addWidget(self.label_logo_comprobantes, alignment=Qt.AlignCenter)
        
        layout_btn3 = QHBoxLayout()
        boton_subir3 = Boton("📤 Subir Logo", "primario")
        boton_subir3.clicked.connect(lambda: self.subir_logo("comprobantes"))
        layout_btn3.addWidget(boton_subir3)
        
        boton_eliminar3 = Boton("🗑️ Eliminar", "peligro")
        boton_eliminar3.clicked.connect(lambda: self.eliminar_logo("comprobantes"))
        layout_btn3.addWidget(boton_eliminar3)
        layout_btn3.addStretch()
        
        layout3.addLayout(layout_btn3)
        frame3.setLayout(layout3)
        layout.addWidget(frame3)
        
        layout.addStretch()
        
        # Cargar logos existentes
        self.cargar_logos_existentes()
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_colores(self):
        """Tab colores"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Personalización de Colores", "titulo")
        layout.addWidget(titulo)
        
        info = QLabel("Próximamente podrá personalizar los colores del sistema")
        info.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #fff3cd;
                border-radius: 8px;
                color: #856404;
                font-size: 11pt;
            }
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Color primario (placeholder)
        frame1 = self.crear_frame_config(
            "🎨 Color Primario:",
            "Color principal usado en botones, encabezados y elementos destacados"
        )
        
        layout_color1 = QHBoxLayout()
        self.boton_color_primario = QPushButton()
        self.boton_color_primario.setFixedSize(100, 40)
        self.boton_color_primario.setStyleSheet("background-color: #2563eb; border-radius: 5px;")
        self.boton_color_primario.setEnabled(False)
        layout_color1.addWidget(self.boton_color_primario)
        layout_color1.addWidget(QLabel("#2563eb (Por defecto)"))
        layout_color1.addStretch()
        frame1.layout().addLayout(layout_color1)
        layout.addWidget(frame1)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_backups(self):
        """Tab configuración de backups"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Configuración de Backups Automáticos", "titulo")
        layout.addWidget(titulo)
        
        info = QLabel("Los backups se crean automáticamente según estos parámetros. También puede crear backups manuales desde la sección de Backups.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(info)
        
        # Intervalo
        frame1 = self.crear_frame_config(
            "⏱️ Días entre backups automáticos:",
            "Cada cuántos días se crea un backup automático de la base de datos"
        )
        self.spin_backup_intervalo = QSpinBox()
        self.spin_backup_intervalo.setMinimum(1)
        self.spin_backup_intervalo.setMaximum(365)
        self.spin_backup_intervalo.setValue(config.backup_dias_intervalo)
        self.spin_backup_intervalo.setSuffix(" días")
        frame1.layout().addWidget(self.spin_backup_intervalo)
        layout.addWidget(frame1)
        
        # Retención
        frame2 = self.crear_frame_config(
            "📅 Días de retención de backups:",
            "Los backups automáticos más antiguos que este tiempo serán eliminados"
        )
        self.spin_backup_retencion = QSpinBox()
        self.spin_backup_retencion.setMinimum(7)
        self.spin_backup_retencion.setMaximum(3650)
        self.spin_backup_retencion.setValue(config.backup_dias_retencion)
        self.spin_backup_retencion.setSuffix(" días")
        frame2.layout().addWidget(self.spin_backup_retencion)
        layout.addWidget(frame2)
        
        layout.addStretch()
        
        # Botón guardar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_guardar = Boton("💾 Guardar Cambios", "exito")
        boton_guardar.clicked.connect(self.guardar_backups)
        layout_botones.addWidget(boton_guardar)
        
        layout.addLayout(layout_botones)
        
        widget.setLayout(layout)
        return widget
    
    def crear_tab_avanzado(self):
        """Tab opciones avanzadas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = Etiqueta("Opciones Avanzadas", "titulo")
        layout.addWidget(titulo)
        
        # Restaurar valores por defecto
        frame1 = QFrame()
        frame1.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout1 = QVBoxLayout()
        
        label1 = QLabel("<b style='font-size: 11pt; color: #856404;'>⚠️ Restaurar Valores por Defecto</b>")
        layout1.addWidget(label1)
        
        info1 = QLabel("Esta acción restaurará TODOS los valores de configuración a sus valores por defecto. No afecta los datos (clientes, equipos, etc.).")
        info1.setWordWrap(True)
        info1.setStyleSheet("color: #856404;")
        layout1.addWidget(info1)
        
        boton_restaurar = Boton("🔄 Restaurar Todo a Valores por Defecto", "peligro")
        boton_restaurar.clicked.connect(self.restaurar_valores_defecto)
        layout1.addWidget(boton_restaurar)
        
        frame1.setLayout(layout1)
        layout.addWidget(frame1)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def crear_frame_config(self, titulo, descripcion):
        """Crea un frame para una opción de configuración"""
        frame = QWidget()
        frame.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_GRIS_50};
                border: 1px solid {Estilos.COLOR_GRIS_200};
                border: none;
                border: 1px solid {Estilos.COLOR_GRIS_200};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel(f"<b>{titulo}</b>")
        label_titulo.setStyleSheet(f"""
            font-size: {Estilos.TAMANO_NORMAL}pt;
            color: {Estilos.COLOR_TEXTO};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
        """)
        layout.addWidget(label_titulo)
        
        label_desc = QLabel(descripcion)
        label_desc.setWordWrap(True)
        label_desc.setStyleSheet(f"""
            color: {Estilos.COLOR_GRIS_600};
            font-size: {Estilos.TAMANO_XS}pt;
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
        """)
        layout.addWidget(label_desc)
        
        frame.setLayout(layout)
        return frame
    
    # Métodos de guardado
    
    def guardar_datos_negocio(self):
        """Guarda datos del negocio"""
        nombre = self.campo_nombre.text().strip()
        
        if not nombre:
            Mensaje.advertencia("Nombre Requerido", "El nombre del negocio es obligatorio", self)
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloConfiguracion.actualizar_datos_negocio(
            nombre,
            self.campo_direccion.text().strip(),
            self.campo_telefono.text().strip(),
            self.campo_email.text().strip(),
            self.campo_cuit.text().strip(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Guardado", mensaje, self)
            config.cargar_configuracion()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def guardar_dias(self):
        """Guarda días"""
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloConfiguracion.actualizar_dias_alertas(
            self.spin_estancado.value(),
            self.spin_abandonado.value(),
            self.spin_vencimiento.value(),
            self.spin_garantia.value(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Guardado", mensaje, self)
            config.cargar_configuracion()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def guardar_porcentajes(self):
        """Guarda porcentajes"""
        try:
            recargo = float(self.campo_recargo.text().strip().replace(",", "."))
            anticipo = float(self.campo_anticipo.text().strip().replace(",", "."))
            
            if recargo < 0 or anticipo < 0:
                raise ValueError()
        except:
            Mensaje.error("Error", "Los porcentajes deben ser números válidos", self)
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloConfiguracion.actualizar_porcentajes(
            recargo,
            anticipo,
            self.spin_stock.value(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Guardado", mensaje, self)
            config.cargar_configuracion()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def guardar_textos(self):
        """Guarda textos"""
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloConfiguracion.actualizar_textos(
            self.campo_texto_remito.toPlainText().strip(),
            self.campo_texto_presupuesto.toPlainText().strip(),
            "",  # texto_factura
            self.campo_texto_garantia.toPlainText().strip(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Guardado", mensaje, self)
            config.cargar_configuracion()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def restaurar_textos_defecto(self):
        """Restaura textos por defecto"""
        confirmacion = Mensaje.confirmacion(
            "Restaurar Textos",
            "¿Está seguro que desea restaurar los textos a sus valores por defecto?",
            self
        )
        
        if confirmacion:
            self.campo_texto_remito.setPlainText("El cliente se compromete a retirar el equipo en un plazo de 30 días. Pasado ese tiempo el negocio no se hace responsable.")
            self.campo_texto_presupuesto.setPlainText("Presupuesto válido por 7 días. Se requiere anticipo del 50% para iniciar la reparación.")
            self.campo_texto_garantia.setPlainText("Garantía de 90 días sobre la reparación realizada. No cubre daños físicos ni líquidos.")
            Mensaje.informacion("Textos Restaurados", "Los textos han sido restaurados. Presione 'Guardar Cambios' para confirmar.", self)
    
    def guardar_backups(self):
        """Guarda config backups"""
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloConfiguracion.actualizar_config_backups(
            True,  # automático
            self.spin_backup_intervalo.value(),
            self.spin_backup_retencion.value(),
            usuario_actual['id_usuario']
        )
        
        if exito:
            Mensaje.exito("✓ Guardado", mensaje, self)
            config.cargar_configuracion()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def restaurar_valores_defecto(self):
        """Restaura TODA la configuración"""
        confirmacion1 = Mensaje.confirmacion(
            "⚠️ ADVERTENCIA",
            "Esta acción restaurará TODA la configuración a sus valores por defecto.\n\n¿Está SEGURO que desea continuar?",
            self
        )
        
        if not confirmacion1:
            return
        
        confirmacion2 = Mensaje.confirmacion(
            "⚠️ ÚLTIMA CONFIRMACIÓN",
            "ATENCIÓN: Se perderán todos los cambios de configuración realizados.\n\nLos datos (clientes, equipos, etc.) NO se verán afectados.\n\n¿CONFIRMAR?",
            self
        )
        
        if not confirmacion2:
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloConfiguracion.restaurar_valores_defecto(usuario_actual['id_usuario'])
        
        if exito:
            Mensaje.exito("✓ Configuración Restaurada", mensaje, self)
            config.cargar_configuracion()
            # Recargar interfaz
            self.inicializar_ui()
        else:
            Mensaje.error("Error", mensaje, self)
    
    # Métodos de logos
    
    def cargar_logos_existentes(self):
        """Carga los logos existentes"""
        # TODO: Implementar carga de logos desde archivos
        pass
    
    def subir_logo(self, tipo):
        """Sube un logo"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar Logo para {tipo.capitalize()}",
            "",
            "Imágenes (*.png *.jpg *.jpeg)"
        )
        
        if archivo:
            from sistema_base.seguridad import obtener_usuario_actual
            usuario_actual = obtener_usuario_actual()
            
            exito, mensaje = ModuloConfiguracion.subir_logo(
                tipo,
                archivo,
                usuario_actual['id_usuario']
            )
            
            if exito:
                Mensaje.exito("✓ Logo Subido", mensaje, self)
                self.cargar_logos_existentes()
            else:
                Mensaje.error("Error", mensaje, self)
    
    def eliminar_logo(self, tipo):
        """Elimina un logo"""
        confirmacion = Mensaje.confirmacion(
            "Eliminar Logo",
            f"¿Está seguro que desea eliminar el logo de {tipo}?",
            self
        )
        
        if confirmacion:
            Mensaje.informacion("Funcionalidad", "La eliminación de logos estará disponible próximamente", self)

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

