# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - INTERFAZ COMPLETA MÓDULO DE BACKUPS
============================================================================
Gestión completa de backups de la base de datos
============================================================================
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QLabel,
                             QFrame, QAbstractItemView, QProgressDialog, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from interfaz.componentes.componentes import (Boton, CampoTexto, Etiqueta,
                                              Mensaje, CampoTextoMultilinea)
from interfaz.estilos.estilos import Estilos
from modulos.backups_LOGICA import ModuloBackups
from sistema_base.configuracion import config
from datetime import datetime
import os


class VentanaBackups(QWidget):
    """Ventana de gestión de backups"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        self.cargar_backups()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        frame_titulo = QWidget()
        frame_titulo.setStyleSheet("QWidget { background-color: white; border: none; padding: 15px; }")
        layout_titulo = QHBoxLayout()
        
        titulo = Etiqueta("💾 Gestión de Backups", "titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_titulo.addWidget(titulo)
        
        frame_titulo.setLayout(layout_titulo)
        layout.addWidget(frame_titulo)
        
        # Barra de herramientas
        barra = self.crear_barra_herramientas()
        layout.addWidget(barra)
        
        # Tarjetas estadísticas
        self.frame_stats = QFrame()
        self.layout_stats = QHBoxLayout()
        self.layout_stats.setSpacing(15)
        self.frame_stats.setLayout(self.layout_stats)
        layout.addWidget(self.frame_stats)
        
        self.actualizar_estadisticas()
        
        # Tabla
        self.tabla = self.crear_tabla_backups()
        layout.addWidget(self.tabla, 1)
        
        self.setLayout(layout)
    
    def crear_barra_herramientas(self):
        """Crea la barra de herramientas"""
        barra = QWidget()
        barra.setStyleSheet(f"QWidget {{ background-color: {Estilos.COLOR_FONDO_CLARO}; padding: 20px; border: none; }}")
        
        layout = QHBoxLayout()
        layout.setSpacing(15)        
        # Botón Volver
        boton_volver = Boton("← Volver", "primario")
        boton_volver.clicked.connect(self.volver_dashboard)
        layout.addWidget(boton_volver)
        

        
        # Búsqueda
        self.campo_busqueda = CampoTexto("Buscar por descripción...")
        self.campo_busqueda.textChanged.connect(self.cargar_backups)
        layout.addWidget(self.campo_busqueda, 1)
        
        # Solo manuales
        from PyQt5.QtWidgets import QCheckBox
        self.check_solo_manuales = QCheckBox("Solo manuales")
        self.check_solo_manuales.stateChanged.connect(self.cargar_backups)
        layout.addWidget(self.check_solo_manuales)
        
        # Botones
        boton_limpiar = Boton("🧹 Limpiar Antiguos", "peligro")
        boton_limpiar.setToolTip("Elimina backups automáticos más antiguos que el tiempo de retención")
        boton_limpiar.clicked.connect(self.limpiar_antiguos)
        layout.addWidget(boton_limpiar)
        
        boton_actualizar = Boton("🔄", "secundario")
        boton_actualizar.setMaximumWidth(50)
        boton_actualizar.setToolTip("Actualizar")
        boton_actualizar.clicked.connect(self.cargar_backups)
        layout.addWidget(boton_actualizar)
        
        barra.setLayout(layout)
        return barra
    
    def actualizar_estadisticas(self):
        """Actualiza estadísticas"""
        # Limpiar layout
        while self.layout_stats.count():
            child = self.layout_stats.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        stats = ModuloBackups.obtener_estadisticas_backups()
        
        # Crear tarjetas
        self.layout_stats.addWidget(self.crear_tarjeta("Total Backups", str(stats.get('total_backups', 0)), "#3498db"))
        self.layout_stats.addWidget(self.crear_tarjeta("Manuales", str(stats.get('manuales', 0)), "#28a745"))
        self.layout_stats.addWidget(self.crear_tarjeta("Automáticos", str(stats.get('automaticos', 0)), "#17a2b8"))
        
        # Tamaño total
        tamanio_mb = stats.get('tamanio_total_mb', 0)
        if tamanio_mb > 1024:
            tamanio_texto = f"{tamanio_mb/1024:.2f} GB"
        else:
            tamanio_texto = f"{tamanio_mb:.2f} MB"
        
        self.layout_stats.addWidget(self.crear_tarjeta("Espacio Usado", tamanio_texto, "#ffc107"))
        
        # Último backup
        if stats.get('ultimo_backup'):
            try:
                fecha = datetime.fromisoformat(str(stats['ultimo_backup']).replace('Z', '+00:00'))
                hace = datetime.now() - fecha
                if hace.days == 0:
                    ultimo_texto = "Hoy"
                elif hace.days == 1:
                    ultimo_texto = "Ayer"
                else:
                    ultimo_texto = f"Hace {hace.days} días"
            except:
                ultimo_texto = "N/A"
        else:
            ultimo_texto = "Nunca"
        
        self.layout_stats.addWidget(self.crear_tarjeta("Último Backup", ultimo_texto, "#6c757d"))
    
    def crear_tarjeta(self, titulo, valor, color):
        """Crea tarjeta"""
        tarjeta = QWidget()
        tarjeta.setStyleSheet(f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-left: 4px solid {color};
                border: none;
                border-left: 4px solid {color};
                padding: 20px;
                min-width: 150px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            font-size: {Estilos.TAMANO_XS}pt;
            color: {Estilos.COLOR_GRIS_600};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            font-weight: 500;
            border: none;
        """)
        label_titulo.setWordWrap(True)
        layout.addWidget(label_titulo)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            font-size: 22pt;
            font-weight: 700;
            color: {color};
            font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            border: none;
            padding: 4px 0px;
        """)
        label_valor.setWordWrap(True)
        layout.addWidget(label_valor)
        
        tarjeta.setLayout(layout)
        return tarjeta
    
    def crear_tabla_backups(self):
        """Crea la tabla de backups"""
        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels([
            "Tipo", "Fecha/Hora", "Archivo", "Tamaño", "Descripción", "Verificado", "Acciones"
        ])
        
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(True)
        
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        tabla.setColumnWidth(6, 220)
        
        tabla.setStyleSheet(Estilos.tabla())
        return tabla
    
    def cargar_backups(self):
        """Carga los backups"""
        try:
            # Simplificado - listar todos los backups sin filtros
            backups = ModuloBackups.listar_backups()
            
            self.tabla.setRowCount(0)
            
            for backup in backups:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                
                # Tipo
                item_tipo = QTableWidgetItem(backup['tipo'])
                if backup['tipo'] == "Manual":
                    item_tipo.setForeground(QColor("#28a745"))
                    item_tipo.setFont(QFont("Arial", 10, QFont.Bold))
                else:
                    item_tipo.setForeground(QColor("#17a2b8"))
                self.tabla.setItem(fila, 0, item_tipo)
                
                # Fecha/Hora
                try:
                    fecha = datetime.fromisoformat(str(backup['fecha_hora']).replace('Z', '+00:00'))
                    fecha_texto = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    fecha_texto = str(backup['fecha_hora'])
                self.tabla.setItem(fila, 1, QTableWidgetItem(fecha_texto))
                
                # Archivo
                self.tabla.setItem(fila, 2, QTableWidgetItem(backup['nombre_archivo']))
                
                # Tamaño
                tamanio_mb = backup['tamanio_mb']
                if tamanio_mb > 1:
                    tamanio_texto = f"{tamanio_mb:.2f} MB"
                else:
                    tamanio_texto = f"{tamanio_mb*1024:.0f} KB"
                self.tabla.setItem(fila, 3, QTableWidgetItem(tamanio_texto))
                
                # Descripción
                desc = backup['descripcion'] if backup['descripcion'] else "-"
                self.tabla.setItem(fila, 4, QTableWidgetItem(desc))
                
                # Verificado
                if backup['verificado']:
                    item_verif = QTableWidgetItem("✓ SÍ")
                    item_verif.setForeground(QColor("#28a745"))
                    item_verif.setFont(QFont("Arial", 10, QFont.Bold))
                else:
                    item_verif = QTableWidgetItem("✗ NO")
                    item_verif.setForeground(QColor("#6c757d"))
                self.tabla.setItem(fila, 5, item_verif)
                
                # Acciones
                widget = self.crear_botones_acciones(backup)
                self.tabla.setCellWidget(fila, 6, widget)
            
            # Actualizar stats
            self.actualizar_estadisticas()
        
        except Exception as e:
            config.guardar_log(f"Error al cargar backups: {e}", "ERROR")
            Mensaje.error("Error", f"Error al cargar backups: {str(e)}", self)
    
    def crear_botones_acciones(self, backup):
        """Crea botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Botón Ver
        boton_ver = Boton("👁️", "primario")
        boton_ver.setToolTip("Ver detalle")
        boton_ver.setMaximumWidth(50)
        boton_ver.clicked.connect(lambda: self.ver_detalle(backup['id_backup']))
        layout.addWidget(boton_ver)
        
        # Botón Verificar
        boton_verificar = Boton("✓", "exito")
        boton_verificar.setToolTip("Verificar integridad")
        boton_verificar.setMaximumWidth(50)
        boton_verificar.clicked.connect(lambda: self.verificar_backup(backup['id_backup']))
        layout.addWidget(boton_verificar)
        
        # Botón Restaurar
        boton_restaurar = Boton("⚡", "secundario")
        boton_restaurar.setToolTip("Restaurar backup")
        boton_restaurar.setMaximumWidth(50)
        boton_restaurar.clicked.connect(lambda: self.restaurar_backup(backup['id_backup']))
        layout.addWidget(boton_restaurar)
        
        # Botón Eliminar
        boton_eliminar = Boton("🗑️", "peligro")
        boton_eliminar.setToolTip("Eliminar backup")
        boton_eliminar.setMaximumWidth(50)
        boton_eliminar.clicked.connect(lambda: self.eliminar_backup(backup['id_backup']))
        layout.addWidget(boton_eliminar)
        
        widget.setLayout(layout)
        return widget
    
    def crear_backup_manual(self):
        """Crear backup manual"""
        dialogo = DialogoCrearBackupManual(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_backups()
    
    def ver_detalle(self, id_backup):
        """Ver detalle del backup"""
        dialogo = DialogoDetalleBackup(id_backup, self)
        dialogo.exec_()
    
    def verificar_backup(self, id_backup):
        """Verificar integridad del backup"""
        confirmacion = Mensaje.confirmacion(
            "Verificar Backup",
            "¿Desea verificar la integridad de este backup?\n\nEsto puede tardar unos momentos.",
            self
        )
        
        if not confirmacion:
            return
        
        # Progress dialog
        progress = QProgressDialog("Verificando integridad del backup...", None, 0, 0, self)
        progress.setWindowTitle("Verificando")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloBackups.verificar_integridad_backup(id_backup, usuario_actual['id_usuario'])
        
        progress.close()
        
        if exito:
            Mensaje.exito("✓ Verificación Exitosa", mensaje, self)
            self.cargar_backups()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def restaurar_backup(self, id_backup):
        """Restaurar backup"""
        dialogo = DialogoRestaurarBackup(id_backup, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_backups()
    
    def eliminar_backup(self, id_backup):
        """Eliminar backup"""
        confirmacion = Mensaje.confirmacion(
            "⚠️ Eliminar Backup",
            "¿Está seguro que desea eliminar este backup?\n\nEsta acción es IRREVERSIBLE.",
            self
        )
        
        if not confirmacion:
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloBackups.eliminar_backup(id_backup, usuario_actual['id_usuario'])
        
        if exito:
            Mensaje.exito("✓ Backup Eliminado", mensaje, self)
            self.cargar_backups()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def limpiar_antiguos(self):
        """Limpiar backups antiguos"""
        confirmacion = Mensaje.confirmacion(
            "Limpiar Backups Antiguos",
            f"Esta acción eliminará todos los backups AUTOMÁTICOS más antiguos que {getattr(config, 'backup_dias_retencion', 30)} días.\n\n" +
            "Los backups MANUALES NO serán eliminados.\n\n¿Continuar?",
            self
        )
        
        if not confirmacion:
            return
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, cantidad = ModuloBackups.limpiar_backups_antiguos(usuario_actual['id_usuario'])
        
        if exito:
            Mensaje.exito("✓ Limpieza Completada", f"Se eliminaron {cantidad} backups antiguos.", self)
            self.cargar_backups()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def volver_dashboard(self):
        """Vuelve al dashboard principal"""
        self.parent().setCurrentIndex(0)


class DialogoCrearBackupManual(QDialog):
    """Diálogo para crear backup manual"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Crear Backup Manual")
        self.setFixedSize(600, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("💾 Crear Backup Manual", "titulo")
        layout.addWidget(titulo)
        
        # Info
        info = QLabel("Se creará una copia de seguridad completa de la base de datos en este momento.")
        info.setWordWrap(True)
        info.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #d1ecf1;
                border: 1px solid #17a2b8;
                border-radius: 5px;
                color: #0c5460;
            }
        """)
        layout.addWidget(info)
        
        # Descripción/Notas
        label_desc = Etiqueta("Descripción del Backup:")
        layout.addWidget(label_desc)
        
        sublabel = QLabel("Agregue una descripción o notas sobre este backup (opcional)")
        sublabel.setStyleSheet("color: #6c757d; font-size: 9pt; margin-bottom: 5px;")
        layout.addWidget(sublabel)
        
        self.campo_descripcion = CampoTextoMultilinea("Ejemplo: Backup antes de actualización del sistema")
        self.campo_descripcion.setMaximumHeight(100)
        layout.addWidget(self.campo_descripcion)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_crear = Boton("💾 Crear Backup", "exito")
        self.boton_crear.clicked.connect(self.crear_backup)
        layout_botones.addWidget(self.boton_crear)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def crear_backup(self):
        """Crea el backup"""
        descripcion = self.campo_descripcion.toPlainText().strip()
        
        if not descripcion:
            descripcion = "Backup manual"
        
        self.boton_crear.setEnabled(False)
        self.boton_crear.setText("Creando...")
        
        # Progress dialog
        progress = QProgressDialog("Creando backup de la base de datos...", None, 0, 0, self)
        progress.setWindowTitle("Creando Backup")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje, id_backup = ModuloBackups.crear_backup_manual(
            descripcion,
            usuario_actual['id_usuario']
        )
        
        progress.close()
        
        if exito:
            Mensaje.exito("✓ Backup Creado", mensaje, self)
            self.accept()
        else:
            Mensaje.error("Error", mensaje, self)
            self.boton_crear.setEnabled(True)
            self.boton_crear.setText("💾 Crear Backup")


class DialogoRestaurarBackup(QDialog):
    """Diálogo para restaurar backup con confirmación seria"""
    
    def __init__(self, id_backup, parent=None):
        super().__init__(parent)
        self.id_backup = id_backup
        self.backup = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("⚠️ Restaurar Backup")
        self.setFixedSize(650, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = Etiqueta("⚠️ RESTAURAR BACKUP", "titulo")
        titulo.setStyleSheet("QLabel { color: #dc3545; }")
        layout.addWidget(titulo)
        
        # ADVERTENCIA GRANDE
        advertencia = QLabel("⚠️ ATENCIÓN: OPERACIÓN CRÍTICA ⚠️")
        advertencia.setWordWrap(True)
        advertencia.setAlignment(Qt.AlignCenter)
        advertencia.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #f8d7da;
                border: 3px solid #dc3545;
                border-radius: 10px;
                color: #721c24;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(advertencia)
        
        # Info crítica
        info = QLabel(
            "• Esta acción REEMPLAZARÁ toda la base de datos actual\n"
            "• Se perderán TODOS los cambios realizados después de este backup\n"
            "• El sistema se cerrará y deberá reiniciarlo manualmente\n"
            "• Se creará un backup de seguridad antes de restaurar"
        )
        info.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #fff3cd;
                border-radius: 5px;
                color: #856404;
                font-size: 10pt;
            }
        """)
        layout.addWidget(info)
        
        # Info del backup
        self.label_backup = QLabel()
        self.label_backup.setWordWrap(True)
        self.label_backup.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.label_backup)
        
        # Confirmación explícita
        label_confirm = QLabel("<b>Para confirmar, escriba: RESTAURAR</b>")
        layout.addWidget(label_confirm)
        
        self.campo_confirmacion = CampoTexto("Escriba aquí...")
        self.campo_confirmacion.textChanged.connect(self.validar_confirmacion)
        layout.addWidget(self.campo_confirmacion)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        boton_cancelar = Boton("Cancelar", "neutro")
        boton_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(boton_cancelar)
        
        self.boton_restaurar = Boton("⚡ CONFIRMAR: Restaurar Backup", "peligro")
        self.boton_restaurar.setEnabled(False)
        self.boton_restaurar.clicked.connect(self.restaurar_backup)
        layout_botones.addWidget(self.boton_restaurar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos del backup"""
        self.backup = ModuloBackups.obtener_backup_por_id(self.id_backup)
        
        if self.backup:
            try:
                fecha = datetime.fromisoformat(str(self.backup['fecha_hora']).replace('Z', '+00:00'))
                fecha_texto = fecha.strftime('%d/%m/%Y a las %H:%M')
            except:
                fecha_texto = str(self.backup['fecha_hora'])
            
            texto = f"<b>Archivo:</b> {self.backup['nombre_archivo']}<br>"
            texto += f"<b>Fecha del backup:</b> {fecha_texto}<br>"
            texto += f"<b>Tipo:</b> {self.backup['tipo']}<br>"
            
            if self.backup['descripcion']:
                texto += f"<b>Descripción:</b> {self.backup['descripcion']}"
            
            self.label_backup.setText(texto)
    
    def validar_confirmacion(self):
        """Valida la confirmación"""
        texto = self.campo_confirmacion.text().strip().upper()
        self.boton_restaurar.setEnabled(texto == "RESTAURAR")
    
    def restaurar_backup(self):
        """Restaura el backup"""
        # Triple confirmación
        confirmacion1 = Mensaje.confirmacion(
            "⚠️ PRIMERA CONFIRMACIÓN",
            "¿Está SEGURO que desea restaurar este backup?\n\n" +
            "Se perderán todos los cambios realizados después de este backup.",
            self
        )
        
        if not confirmacion1:
            return
        
        confirmacion2 = Mensaje.confirmacion(
            "⚠️ SEGUNDA CONFIRMACIÓN",
            "ÚLTIMA ADVERTENCIA:\n\n" +
            "• El sistema se cerrará después de restaurar\n" +
            "• Deberá reiniciarlo manualmente\n" +
            "• Se creará un backup de seguridad antes\n\n" +
            "¿Desea CONTINUAR?",
            self
        )
        
        if not confirmacion2:
            return
        
        self.boton_restaurar.setEnabled(False)
        self.boton_restaurar.setText("Restaurando...")
        
        # Progress dialog
        progress = QProgressDialog("Restaurando backup...", None, 0, 0, self)
        progress.setWindowTitle("Restaurando")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloBackups.restaurar_backup(
            self.id_backup,
            usuario_actual['id_usuario']
        )
        
        progress.close()
        
        if exito:
            Mensaje.informacion(
                "✓ Backup Restaurado",
                f"{mensaje}\n\nEl sistema se cerrará ahora.\n\nREINICIE LA APLICACIÓN para continuar.",
                self
            )
            # Cerrar aplicación
            import sys
            sys.exit(0)
        else:
            Mensaje.error("Error", mensaje, self)
            self.boton_restaurar.setEnabled(True)
            self.boton_restaurar.setText("⚡ CONFIRMAR: Restaurar Backup")


class DialogoDetalleBackup(QDialog):
    """Diálogo para ver detalle completo del backup"""
    
    def __init__(self, id_backup, parent=None):
        super().__init__(parent)
        self.id_backup = id_backup
        self.backup = None
        self.inicializar_ui()
        self.cargar_datos()
    
    def inicializar_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Detalle del Backup")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        self.label_titulo = Etiqueta("", "titulo")
        layout.addWidget(self.label_titulo)
        
        # Frame de datos
        frame_datos = QFrame()
        frame_datos.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout_datos = QVBoxLayout()
        layout_datos.setSpacing(15)
        
        # Información general
        label_general = QLabel("<b style='color: #2563eb; font-size: 12pt;'>📋 INFORMACIÓN GENERAL</b>")
        layout_datos.addWidget(label_general)
        
        self.label_info_general = QLabel()
        self.label_info_general.setWordWrap(True)
        self.label_info_general.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_info_general)
        
        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("background-color: #dee2e6;")
        layout_datos.addWidget(sep1)
        
        # Detalles técnicos
        label_tecnico = QLabel("<b style='color: #2563eb; font-size: 12pt;'>⚙️ DETALLES TÉCNICOS</b>")
        layout_datos.addWidget(label_tecnico)
        
        self.label_detalles = QLabel()
        self.label_detalles.setWordWrap(True)
        self.label_detalles.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout_datos.addWidget(self.label_detalles)
        
        # Estado de verificación
        self.frame_verificacion = QFrame()
        self.frame_verificacion.setStyleSheet("""
            QFrame {
                padding: 15px;
                border-radius: 5px;
            }
        """)
        layout_verif = QVBoxLayout()
        
        self.label_verificacion_titulo = QLabel()
        self.label_verificacion_titulo.setAlignment(Qt.AlignCenter)
        layout_verif.addWidget(self.label_verificacion_titulo)
        
        self.frame_verificacion.setLayout(layout_verif)
        layout_datos.addWidget(self.frame_verificacion)
        
        frame_datos.setLayout(layout_datos)
        layout.addWidget(frame_datos)
        
        layout.addStretch()
        
        # Botones
        layout_botones = QHBoxLayout()
        
        self.boton_verificar = Boton("✓ Verificar Integridad", "exito")
        self.boton_verificar.clicked.connect(self.verificar_integridad)
        layout_botones.addWidget(self.boton_verificar)
        
        self.boton_restaurar = Boton("⚡ Restaurar", "secundario")
        self.boton_restaurar.clicked.connect(self.restaurar)
        layout_botones.addWidget(self.boton_restaurar)
        
        layout_botones.addStretch()
        
        boton_cerrar = Boton("Cerrar", "neutro")
        boton_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(boton_cerrar)
        
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga datos del backup"""
        self.backup = ModuloBackups.obtener_backup_por_id(self.id_backup)
        
        if not self.backup:
            return
        
        # Título
        self.label_titulo.setText(f"Backup: {self.backup['nombre_archivo']}")
        
        # Info general
        try:
            fecha = datetime.fromisoformat(str(self.backup['fecha_hora']).replace('Z', '+00:00'))
            fecha_texto = fecha.strftime('%d/%m/%Y a las %H:%M:%S')
        except:
            fecha_texto = str(self.backup['fecha_hora'])
        
        tamanio_mb = self.backup['tamanio_mb']
        if tamanio_mb > 1:
            tamanio_texto = f"{tamanio_mb:.2f} MB"
        else:
            tamanio_texto = f"{tamanio_mb*1024:.0f} KB"
        
        texto_general = f"<b>Tipo:</b> {self.backup['tipo']}<br>"
        texto_general += f"<b>Fecha y hora:</b> {fecha_texto}<br>"
        texto_general += f"<b>Tamaño:</b> {tamanio_texto}<br>"
        
        if self.backup['descripcion']:
            texto_general += f"<br><b>Descripción:</b><br>{self.backup['descripcion']}"
        
        self.label_info_general.setText(texto_general)
        
        # Detalles técnicos
        texto_detalles = f"<b>Nombre archivo:</b> {self.backup['nombre_archivo']}<br>"
        texto_detalles += f"<b>Ruta completa:</b> {self.backup['ruta_completa']}"
        
        # Verificar si existe el archivo
        if os.path.exists(self.backup['ruta_completa']):
            texto_detalles += "<br><span style='color: #28a745;'>✓ Archivo existe en disco</span>"
        else:
            texto_detalles += "<br><span style='color: #dc3545;'>✗ Archivo no encontrado</span>"
        
        self.label_detalles.setText(texto_detalles)
        
        # Estado de verificación
        if self.backup['verificado']:
            self.frame_verificacion.setStyleSheet("""
                QFrame {
                    background-color: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                    padding: 15px;
                }
            """)
            self.label_verificacion_titulo.setText("✓ BACKUP VERIFICADO")
            self.label_verificacion_titulo.setStyleSheet("""
                QLabel {
                    color: #155724;
                    font-size: 13pt;
                    font-weight: bold;
                }
            """)
        else:
            self.frame_verificacion.setStyleSheet("""
                QFrame {
                    background-color: #fff3cd;
                    border: 2px solid #ffc107;
                    border-radius: 5px;
                    padding: 15px;
                }
            """)
            self.label_verificacion_titulo.setText("⚠️ BACKUP NO VERIFICADO")
            self.label_verificacion_titulo.setStyleSheet("""
                QLabel {
                    color: #856404;
                    font-size: 13pt;
                    font-weight: bold;
                }
            """)
    
    def verificar_integridad(self):
        """Verifica integridad"""
        self.boton_verificar.setEnabled(False)
        self.boton_verificar.setText("Verificando...")
        
        from sistema_base.seguridad import obtener_usuario_actual
        usuario_actual = obtener_usuario_actual()
        
        exito, mensaje = ModuloBackups.verificar_integridad_backup(
            self.id_backup,
            usuario_actual['id_usuario']
        )
        
        self.boton_verificar.setEnabled(True)
        self.boton_verificar.setText("✓ Verificar Integridad")
        
        if exito:
            Mensaje.exito("✓ Verificación Exitosa", mensaje, self)
            self.cargar_datos()
            if self.parent():
                self.parent().cargar_backups()
        else:
            Mensaje.error("Error", mensaje, self)
    
    def restaurar(self):
        """Restaurar backup"""
        dialogo = DialogoRestaurarBackup(self.id_backup, self)
        if dialogo.exec_() == QDialog.Accepted:
            if self.parent():
                self.parent().cargar_backups()
