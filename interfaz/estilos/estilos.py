# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - SISTEMA DE DISEÑO PROFESIONAL
============================================================================
Sistema de diseño moderno tipo Canva con sombras, gradientes y animaciones
============================================================================
"""

from sistema_base.configuracion import config


class Estilos:
    """
    Sistema de diseño profesional completo
    """
    
    # ========================================================================
    # PALETA DE COLORES MODERNA
    # ========================================================================
    
    @staticmethod
    def obtener_color_primario():
        """Retorna el color primario configurado"""
        return config.color_primario
    
    @staticmethod
    def obtener_color_secundario():
        """Retorna el color secundario configurado"""
        return config.color_secundario
    
    # Colores base
    COLOR_FONDO = "#f5f7fa"
    COLOR_FONDO_CLARO = "#ffffff"
    COLOR_TEXTO = "#1e293b"
    COLOR_TEXTO_SECUNDARIO = "#64748b"
    COLOR_BLANCO = "#ffffff"
    COLOR_NEGRO = "#0f172a"
    
    # Colores de marca (modernos y vibrantes)
    COLOR_PRIMARIO = "#2563eb"
    COLOR_PRIMARIO_HOVER = "#1d4ed8"
    COLOR_PRIMARIO_ACTIVE = "#1e40af"
    COLOR_SECUNDARIO = "#64748b"
    COLOR_SECUNDARIO_HOVER = "#475569"
    
    # Colores de estado (más vibrantes)
    COLOR_EXITO = "#10b981"
    COLOR_EXITO_HOVER = "#059669"
    COLOR_ERROR = "#ef4444"
    COLOR_ERROR_HOVER = "#dc2626"
    COLOR_ADVERTENCIA = "#f59e0b"
    COLOR_ADVERTENCIA_HOVER = "#d97706"
    COLOR_INFO = "#06b6d4"
    COLOR_INFO_HOVER = "#0891b2"
    
    # Colores neutrales (escala de grises moderna)
    COLOR_GRIS_50 = "#f8fafc"
    COLOR_GRIS_100 = "#f1f5f9"
    COLOR_GRIS_200 = "#e2e8f0"
    COLOR_GRIS_300 = "#cbd5e1"
    COLOR_GRIS_400 = "#94a3b8"
    COLOR_GRIS_500 = "#64748b"
    COLOR_GRIS_600 = "#475569"
    COLOR_GRIS_700 = "#334155"
    COLOR_GRIS_800 = "#1e293b"
    COLOR_GRIS_900 = "#0f172a"
    
    # ========================================================================
    # SOMBRAS (ELEVACIÓN)
    # ========================================================================
    
    SOMBRA_XS = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SOMBRA_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"
    SOMBRA_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"
    SOMBRA_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"
    SOMBRA_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"
    
    # ========================================================================
    # FUENTES (SISTEMA MODERNO)
    # ========================================================================
    
    FUENTE_PRINCIPAL = "Segoe UI"
    FUENTE_ALTERNATIVA = "Inter, -apple-system, system-ui, Arial"
    FUENTE_MONO = "Consolas, Monaco, monospace"
    
    TAMANO_XL = 24
    TAMANO_LG = 20
    TAMANO_TITULO = 18
    TAMANO_SUBTITULO = 14
    TAMANO_NORMAL = 11
    TAMANO_SM = 10
    TAMANO_XS = 9
    
    # ========================================================================
    # ESPACIADO (SISTEMA 8PX)
    # ========================================================================
    
    ESPACIADO_XS = "4px"
    ESPACIADO_SM = "8px"
    ESPACIADO_MD = "12px"
    ESPACIADO_LG = "16px"
    ESPACIADO_XL = "20px"
    ESPACIADO_2XL = "24px"
    ESPACIADO_3XL = "32px"
    
    # ========================================================================
    # BORDES (SIN REDONDEO - RECTOS)
    # ========================================================================
    
    RADIO_XS = "0px"
    RADIO_SM = "0px"
    RADIO_MD = "0px"
    RADIO_LG = "0px"
    RADIO_XL = "0px"
    RADIO_FULL = "0px"
    
    # ========================================================================
    # ESTILOS DE BOTONES MODERNOS (CON SOMBRAS Y TRANSICIONES)
    # ========================================================================
    
    @staticmethod
    def boton_primario():
        """Botón principal moderno con sombra y gradiente sutil"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Estilos.COLOR_PRIMARIO},
                    stop:1 {Estilos.COLOR_PRIMARIO_HOVER});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
            QPushButton:hover {{
                background: {Estilos.COLOR_PRIMARIO_HOVER};
            }}
            QPushButton:pressed {{
                background: {Estilos.COLOR_PRIMARIO_ACTIVE};
                padding: 13px 24px 11px 24px;
            }}
            QPushButton:disabled {{
                background-color: {Estilos.COLOR_GRIS_300};
                color: {Estilos.COLOR_GRIS_500};
            }}
        """
    
    @staticmethod
    def boton_secundario():
        """Botón secundario con borde"""
        return f"""
            QPushButton {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                color: {Estilos.COLOR_PRIMARIO};
                border: 2px solid {Estilos.COLOR_PRIMARIO};
                padding: 10px 24px;
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_GRIS_50};
                border-color: {Estilos.COLOR_PRIMARIO_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Estilos.COLOR_GRIS_100};
            }}
            QPushButton:disabled {{
                background-color: {Estilos.COLOR_GRIS_100};
                border-color: {Estilos.COLOR_GRIS_300};
                color: {Estilos.COLOR_GRIS_400};
            }}
        """
    
    @staticmethod
    def boton_exito():
        """Botón de éxito (verde moderno)"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Estilos.COLOR_EXITO},
                    stop:1 {Estilos.COLOR_EXITO_HOVER});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
            QPushButton:hover {{
                background: {Estilos.COLOR_EXITO_HOVER};
            }}
            QPushButton:pressed {{
                background: #047857;
                padding: 13px 24px 11px 24px;
            }}
            QPushButton:disabled {{
                background-color: {Estilos.COLOR_GRIS_300};
                color: {Estilos.COLOR_GRIS_500};
            }}
        """
    
    @staticmethod
    def boton_peligro():
        """Botón de peligro (rojo moderno)"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Estilos.COLOR_ERROR},
                    stop:1 {Estilos.COLOR_ERROR_HOVER});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
            QPushButton:hover {{
                background: {Estilos.COLOR_ERROR_HOVER};
            }}
            QPushButton:pressed {{
                background: #b91c1c;
                padding: 13px 24px 11px 24px;
            }}
            QPushButton:disabled {{
                background-color: {Estilos.COLOR_GRIS_300};
                color: {Estilos.COLOR_GRIS_500};
            }}
        """
    
    @staticmethod
    def boton_neutro():
        """Botón neutro moderno"""
        return f"""
            QPushButton {{
                background-color: {Estilos.COLOR_GRIS_500};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
            QPushButton:hover {{
                background-color: {Estilos.COLOR_GRIS_600};
            }}
            QPushButton:pressed {{
                background-color: {Estilos.COLOR_GRIS_700};
                padding: 13px 24px 11px 24px;
            }}
            QPushButton:disabled {{
                background-color: {Estilos.COLOR_GRIS_300};
                color: {Estilos.COLOR_GRIS_500};
            }}
        """
    
    # ========================================================================
    # ESTILOS DE CAMPOS DE ENTRADA MODERNOS
    # ========================================================================
    
    @staticmethod
    def campo_entrada():
        """Campo de texto moderno con sombra interna"""
        return f"""
            QLineEdit {{
                padding: 12px 16px;
                border: 1px solid {Estilos.COLOR_GRIS_200};
                border-radius: {Estilos.RADIO_SM};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                background-color: white;
                color: {Estilos.COLOR_TEXTO};
            }}
            QLineEdit:focus {{
                border: 2px solid {Estilos.COLOR_PRIMARIO};
                background-color: white;
                padding: 11px 15px;
            }}
            QLineEdit:hover {{
                border-color: {Estilos.COLOR_GRIS_300};
            }}
            QLineEdit:disabled {{
                background-color: {Estilos.COLOR_GRIS_100};
                color: {Estilos.COLOR_GRIS_500};
                border-color: {Estilos.COLOR_GRIS_200};
            }}
            QLineEdit::placeholder {{
                color: {Estilos.COLOR_GRIS_400};
            }}
        """
    
    @staticmethod
    def campo_texto_multilinea():
        """Campo de texto multilínea moderno"""
        return f"""
            QTextEdit {{
                padding: 12px 16px;
                border: 2px solid {Estilos.COLOR_GRIS_300};
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                background-color: {Estilos.COLOR_FONDO_CLARO};
                color: {Estilos.COLOR_TEXTO};
            }}
            QTextEdit:focus {{
                border: 2px solid {Estilos.COLOR_PRIMARIO};
            }}
            QTextEdit:hover {{
                border-color: {Estilos.COLOR_GRIS_400};
            }}
            QTextEdit:disabled {{
                background-color: {Estilos.COLOR_GRIS_100};
                color: {Estilos.COLOR_GRIS_500};
                border-color: {Estilos.COLOR_GRIS_200};
            }}
        """
    
    @staticmethod
    def combobox():
        """Combobox moderno con flecha personalizada"""
        return f"""
            QComboBox {{
                padding: 12px 16px;
                padding-right: 40px;
                border: 2px solid {Estilos.COLOR_GRIS_300};
                border-radius: {Estilos.RADIO_MD};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                background-color: {Estilos.COLOR_FONDO_CLARO};
                color: {Estilos.COLOR_TEXTO};
            }}
            QComboBox:hover {{
                border-color: {Estilos.COLOR_GRIS_400};
            }}
            QComboBox:focus {{
                border: 2px solid {Estilos.COLOR_PRIMARIO};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 35px;
                padding-right: 10px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {Estilos.COLOR_GRIS_600};
                margin-right: 8px;
            }}
            QComboBox:disabled {{
                background-color: {Estilos.COLOR_GRIS_100};
                color: {Estilos.COLOR_GRIS_500};
                border-color: {Estilos.COLOR_GRIS_200};
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid {Estilos.COLOR_GRIS_300};
                border-radius: {Estilos.RADIO_MD};
                background-color: {Estilos.COLOR_FONDO_CLARO};
                selection-background-color: {Estilos.COLOR_PRIMARIO};
                selection-color: white;
                padding: 4px;
            }}
        """
    
    # ========================================================================
    # ESTILOS DE ETIQUETAS MODERNOS
    # ========================================================================
    
    @staticmethod
    def etiqueta_titulo():
        """Título moderno con espaciado"""
        return f"""
            QLabel {{
                font-size: {Estilos.TAMANO_TITULO}pt;
                font-weight: 700;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                letter-spacing: -0.5px;
            }}
        """
    
    @staticmethod
    def etiqueta_subtitulo():
        """Subtítulo moderno"""
        return f"""
            QLabel {{
                font-size: {Estilos.TAMANO_SUBTITULO}pt;
                font-weight: 600;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_GRIS_700};
                letter-spacing: -0.3px;
            }}
        """
    
    @staticmethod
    def etiqueta_normal():
        """Etiqueta normal"""
        return f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
            }}
        """
    
    @staticmethod
    def etiqueta_error():
        """Mensaje de error"""
        return f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_ERROR};
                font-weight: 600;
                padding: {Estilos.ESPACIADO_SM};
                background-color: rgba(239, 68, 68, 0.1);
                border-radius: {Estilos.RADIO_SM};
            }}
        """
    
    @staticmethod
    def etiqueta_exito():
        """Mensaje de éxito"""
        return f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_EXITO};
                font-weight: 600;
                padding: {Estilos.ESPACIADO_SM};
                background-color: rgba(16, 185, 129, 0.1);
                border-radius: {Estilos.RADIO_SM};
            }}
        """
    
    # ========================================================================
    # ESTILOS DE TABLAS MODERNOS
    # ========================================================================
    
    @staticmethod
    def tabla():
        """Tabla moderna con sombra y hover"""
        return f"""
            QTableWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border: 1px solid {Estilos.COLOR_GRIS_200};
                border-radius: {Estilos.RADIO_MD};
                gridline-color: {Estilos.COLOR_GRIS_200};
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
            }}
            QTableWidget::item {{
                padding: {Estilos.ESPACIADO_MD} {Estilos.ESPACIADO_LG};
                border-bottom: 1px solid {Estilos.COLOR_GRIS_100};
            }}
            QTableWidget::item:selected {{
                background-color: {Estilos.COLOR_PRIMARIO};
                color: white;
            }}
            QTableWidget::item:hover {{
                background-color: {Estilos.COLOR_GRIS_50};
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Estilos.COLOR_GRIS_50},
                    stop:1 {Estilos.COLOR_GRIS_100});
                padding: {Estilos.ESPACIADO_MD} {Estilos.ESPACIADO_LG};
                border: none;
                border-bottom: 2px solid {Estilos.COLOR_GRIS_300};
                font-weight: 600;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                color: {Estilos.COLOR_GRIS_700};
            }}
        """
    
    # ========================================================================
    # ESTILOS DE VENTANAS Y CONTENEDORES
    # ========================================================================
    
    @staticmethod
    def ventana_principal():
        """Ventana principal moderna"""
        return f"""
            QMainWindow {{
                background-color: {Estilos.COLOR_FONDO};
            }}
        """
    
    @staticmethod
    def panel_lateral():
        """Panel lateral moderno con gradiente"""
        return f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b,
                    stop:1 #0f172a);
                color: white;
            }}
        """
    
    @staticmethod
    def area_trabajo():
        """Área de trabajo con sombra"""
        return f"""
            QWidget {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border-radius: {Estilos.RADIO_LG};
                padding: {Estilos.ESPACIADO_3XL};
            }}
        """
    
    @staticmethod
    def dialogo():
        """Diálogo moderno"""
        return f"""
            QDialog {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
            }}
        """
    
    # ========================================================================
    # ESTILOS ESPECIALES (TARJETAS, BADGES, ETC)
    # ========================================================================
    
    @staticmethod
    def tarjeta():
        """Tarjeta moderna con sombra"""
        return f"""
            QFrame {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border: 1px solid {Estilos.COLOR_GRIS_200};
                border-radius: {Estilos.RADIO_LG};
                padding: {Estilos.ESPACIADO_2XL};
            }}
            QFrame:hover {{
                border-color: {Estilos.COLOR_PRIMARIO};
            }}
        """
    
    @staticmethod
    def tarjeta_hover():
        """Tarjeta con efecto hover pronunciado"""
        return f"""
            QFrame {{
                background-color: {Estilos.COLOR_FONDO_CLARO};
                border: 2px solid {Estilos.COLOR_GRIS_200};
                border-radius: {Estilos.RADIO_LG};
                padding: {Estilos.ESPACIADO_2XL};
            }}
            QFrame:hover {{
                border-color: {Estilos.COLOR_PRIMARIO};
                border-width: 3px;
            }}
        """
    
    @staticmethod
    def separador():
        """Línea separadora sutil"""
        return f"""
            QFrame {{
                background-color: {Estilos.COLOR_GRIS_200};
                max-height: 1px;
            }}
        """
    
    @staticmethod
    def badge_exito():
        """Badge de éxito (verde)"""
        return f"""
            QLabel {{
                background-color: {Estilos.COLOR_EXITO};
                color: white;
                padding: 4px 12px;
                border-radius: {Estilos.RADIO_FULL};
                font-size: {Estilos.TAMANO_XS}pt;
                font-weight: 600;
            }}
        """
    
    @staticmethod
    def badge_error():
        """Badge de error (rojo)"""
        return f"""
            QLabel {{
                background-color: {Estilos.COLOR_ERROR};
                color: white;
                padding: 4px 12px;
                border-radius: {Estilos.RADIO_FULL};
                font-size: {Estilos.TAMANO_XS}pt;
                font-weight: 600;
            }}
        """
    
    @staticmethod
    def badge_advertencia():
        """Badge de advertencia (amarillo)"""
        return f"""
            QLabel {{
                background-color: {Estilos.COLOR_ADVERTENCIA};
                color: white;
                padding: 4px 12px;
                border-radius: {Estilos.RADIO_FULL};
                font-size: {Estilos.TAMANO_XS}pt;
                font-weight: 600;
            }}
        """
    
    @staticmethod
    def badge_info():
        """Badge de información (azul)"""
        return f"""
            QLabel {{
                background-color: {Estilos.COLOR_INFO};
                color: white;
                padding: 4px 12px;
                border-radius: {Estilos.RADIO_FULL};
                font-size: {Estilos.TAMANO_XS}pt;
                font-weight: 600;
            }}
        """
    
    # ========================================================================
    # ESTILOS ESPECÍFICOS - MÓDULOS
    # ========================================================================
    
    # --- ESPACIADOS PARA FORMULARIOS ---
    SPACING_LABEL_CAMPO = 0      # Entre etiqueta y su campo (pegado)
    SPACING_ENTRE_GRUPOS = 8     # Entre grupos de campos
    SPACING_DESPUES_TITULO = 8   # Después de títulos de sección
    
    @staticmethod
    def frame_seccion(color_borde):
        """Frame para secciones con color de borde personalizado"""
        return f"""
            QFrame {{
                background: white;
                border: 2px solid {color_borde};
                border-radius: 8px;
                padding: 15px;
            }}
        """
    
    @staticmethod
    def label_campo():
        """Etiqueta de campo de formulario (sin borde, sin fondo)"""
        return """
            QLabel {
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """
    
    @staticmethod
    def label_campo_negrita():
        """Etiqueta de campo de formulario en negrita"""
        return """
            QLabel {
                border: none;
                background: transparent;
                font-weight: bold;
                padding: 0;
                margin: 0;
            }
        """
    
    @staticmethod
    def label_campo_con_margen(margen_left=0):
        """Etiqueta de campo con margen izquierdo"""
        return f"""
            QLabel {{
                border: none;
                background: transparent;
                margin-left: {margen_left}px;
                padding: 0;
                margin-top: 0;
                margin-right: 0;
                margin-bottom: 0;
            }}
        """
    
    @staticmethod
    def frame_cliente():
        """Frame para sección de datos del cliente (gris)"""
        return f"""
            QFrame {{
                background: {Estilos.COLOR_GRIS_50};
                border: 1px solid {Estilos.COLOR_GRIS_300};
                border-radius: 8px;
                padding: 15px;
            }}
        """
    
    @staticmethod
    def frame_equipo():
        """Frame para sección de datos del equipo (azul)"""
        return Estilos.frame_seccion(Estilos.COLOR_PRIMARIO)
    
    @staticmethod
    def frame_estado():
        """Frame para sección de estado y diagnóstico (verde)"""
        return Estilos.frame_seccion(Estilos.COLOR_EXITO)
    
    @staticmethod
    def frame_accesorios():
        """Frame para sección de accesorios (amarillo)"""
        return Estilos.frame_seccion(Estilos.COLOR_ADVERTENCIA)
    
    @staticmethod
    def scroll_area():
        """Área de scroll sin borde"""
        return "QScrollArea { border: none; }"
    
    @staticmethod
    def widget_sin_borde():
        """Widget genérico sin borde"""
        return "QWidget { border: none; }"
    
    @staticmethod
    def label_info_cliente():
        """Label con info del cliente en dialogo"""
        return f"""
            QLabel {{
                font-size: {Estilos.TAMANO_NORMAL}pt;
                font-family: '{Estilos.FUENTE_PRINCIPAL}', Arial;
                color: {Estilos.COLOR_TEXTO};
                padding: 8px;
                background-color: {Estilos.COLOR_GRIS_50};
                border-radius: 4px;
            }}
        """
    
    @staticmethod
    def label_estado_actual():
        """Label para mostrar estado actual del equipo"""
        return f"""
            font-weight: bold;
            font-size: {Estilos.TAMANO_SUBTITULO}pt;
        """
    
    # --- ESTILOS PARA MÓDULO CLIENTES ---
    
    @staticmethod
    def label_info_destacada():
        """Label con info destacada (teléfono, etc)"""
        return """
            font-weight: bold;
            font-size: 14px;
            padding: 5px 10px;
        """
    
    @staticmethod
    def label_info_normal():
        """Label con info normal"""
        return """
            font-size: 13px;
            padding: 5px 10px;
        """
    
    @staticmethod
    def combo_estado_cliente():
        """ComboBox para estado del cliente"""
        return f"""
            QComboBox {{
                padding: 8px 12px;
                border: 2px solid {Estilos.COLOR_GRIS_300};
                border-radius: 4px;
                background: white;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                min-width: 200px;
            }}
            QComboBox:hover {{
                border-color: {Estilos.COLOR_PRIMARIO};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
        """
    
    @staticmethod
    def campo_motivo():
        """Campo de texto para motivo"""
        return f"""
            QTextEdit {{
                padding: 8px;
                border: 2px solid {Estilos.COLOR_GRIS_300};
                border-radius: 4px;
                background: white;
                font-size: {Estilos.TAMANO_NORMAL}pt;
                min-height: 80px;
            }}
            QTextEdit:focus {{
                border-color: {Estilos.COLOR_PRIMARIO};
            }}
        """
    
    @staticmethod
    def advertencia_incobrable():
        """Advertencia para cliente incobrable"""
        return f"""
            QLabel {{
                background-color: {Estilos.COLOR_ERROR};
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: {Estilos.TAMANO_NORMAL}pt;
            }}
        """
    
    @staticmethod
    def label_cliente_dialogo():
        """Label con nombre del cliente en diálogo"""
        return f"""
            QLabel {{
                font-size: 20pt;
                font-weight: bold;
                color: {Estilos.COLOR_PRIMARIO};
                padding: 10px;
            }}
        """
    
    @staticmethod
    def tabs_style():
        """Estilo para pestañas (tabs)"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {Estilos.COLOR_GRIS_200};
                border-radius: 4px;
                background: white;
            }}
            QTabBar::tab {{
                background: {Estilos.COLOR_GRIS_100};
                border: 1px solid {Estilos.COLOR_GRIS_300};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {Estilos.COLOR_PRIMARIO};
                color: white;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: {Estilos.COLOR_GRIS_200};
            }}
        """
    
    @staticmethod
    def frame_info_cliente():
        """Frame con información del cliente"""
        return f"""
            QFrame {{
                background: {Estilos.COLOR_GRIS_50};
                border: 2px solid {Estilos.COLOR_PRIMARIO};
                border-radius: 8px;
                padding: 15px;
            }}
        """
    
    @staticmethod
    def label_titulo_seccion_cliente():
        """Label título de sección en módulo clientes"""
        return f"""
            QLabel {{
                font-size: 16pt;
                font-weight: bold;
                color: {Estilos.COLOR_TEXTO};
                padding: 5px 0px;
            }}
        """

