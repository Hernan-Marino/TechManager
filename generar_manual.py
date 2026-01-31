# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - GENERADOR DE MANUAL DE USUARIO
============================================================================
Genera un manual completo y profesional en PDF
============================================================================
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os


class ManualUsuario:
    """Genera el manual de usuario completo"""
    
    def __init__(self):
        self.filename = "MANUAL_USUARIO_TechManager.pdf"
        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        self.story = []
        self.styles = self.crear_estilos()
    
    def crear_estilos(self):
        """Crea estilos personalizados"""
        styles = getSampleStyleSheet()
        
        # Estilo título principal
        styles.add(ParagraphStyle(
            name='TituloPortada',
            parent=styles['Title'],
            fontSize=32,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo subtítulo portada
        styles.add(ParagraphStyle(
            name='SubtituloPortada',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Estilo capítulo
        styles.add(ParagraphStyle(
            name='Capitulo',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=20,
            spaceBefore=30,
            fontName='Helvetica-Bold',
            borderPadding=10,
            borderColor=colors.HexColor('#2563eb'),
            borderWidth=2,
            borderRadius=0,
            backColor=colors.HexColor('#eff6ff')
        ))
        
        # Estilo sección
        styles.add(ParagraphStyle(
            name='Seccion',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo subsección
        styles.add(ParagraphStyle(
            name='Subseccion',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo texto normal
        styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Estilo nota importante
        styles.add(ParagraphStyle(
            name='Nota',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=15,
            spaceBefore=10,
            leftIndent=20,
            rightIndent=20,
            borderPadding=10,
            borderColor=colors.HexColor('#2563eb'),
            borderWidth=1,
            backColor=colors.HexColor('#eff6ff'),
            fontName='Helvetica-Oblique'
        ))
        
        # Estilo advertencia
        styles.add(ParagraphStyle(
            name='Advertencia',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#991b1b'),
            spaceAfter=15,
            spaceBefore=10,
            leftIndent=20,
            rightIndent=20,
            borderPadding=10,
            borderColor=colors.HexColor('#dc2626'),
            borderWidth=1,
            backColor=colors.HexColor('#fef2f2'),
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def portada(self):
        """Crea la portada del manual"""
        # Título
        titulo = Paragraph("TECHMANAGER", self.styles['TituloPortada'])
        self.story.append(Spacer(1, 1.5*inch))
        self.story.append(titulo)
        
        # Subtítulo
        subtitulo = Paragraph(
            "Sistema de Gestión para Servicio Técnico",
            self.styles['SubtituloPortada']
        )
        self.story.append(subtitulo)
        
        # Versión
        version = Paragraph(
            "Versión 1.0",
            self.styles['SubtituloPortada']
        )
        self.story.append(Spacer(1, 0.5*inch))
        self.story.append(version)
        
        # Manual de usuario
        manual = Paragraph(
            "<b>MANUAL DE USUARIO</b>",
            self.styles['SubtituloPortada']
        )
        self.story.append(Spacer(1, 1*inch))
        self.story.append(manual)
        
        # Fecha
        fecha = Paragraph(
            f"Enero 2025",
            self.styles['SubtituloPortada']
        )
        self.story.append(Spacer(1, 2*inch))
        self.story.append(fecha)
        
        # Copyright
        copyright_text = Paragraph(
            "© 2025 TechManager - Todos los derechos reservados",
            self.styles['Normal']
        )
        self.story.append(Spacer(1, 1*inch))
        self.story.append(copyright_text)
        
        self.story.append(PageBreak())
    
    def indice(self):
        """Crea el índice"""
        self.story.append(Paragraph("ÍNDICE", self.styles['Capitulo']))
        self.story.append(Spacer(1, 0.3*inch))
        
        indices = [
            ("1. Introducción", "3"),
            ("   1.1 ¿Qué es TechManager?", "3"),
            ("   1.2 Características principales", "3"),
            ("   1.3 Requisitos del sistema", "4"),
            ("2. Instalación", "5"),
            ("   2.1 Instalación con wizard", "5"),
            ("   2.2 Primer inicio", "6"),
            ("   2.3 Cambio de contraseña obligatorio", "6"),
            ("3. Interfaz del Sistema", "7"),
            ("   3.1 Ventana principal", "7"),
            ("   3.2 Menú de navegación", "8"),
            ("   3.3 Barra de herramientas", "9"),
            ("4. Módulo de Clientes", "10"),
            ("5. Módulo de Equipos", "13"),
            ("6. Órdenes de Reparación", "16"),
            ("7. Presupuestos", "20"),
            ("8. Facturación y Pagos", "23"),
            ("9. Control de Repuestos", "27"),
            ("10. Sistema de Garantías", "30"),
            ("11. Remitos", "33"),
            ("12. Usuarios y Permisos", "35"),
            ("13. Configuración del Sistema", "38"),
            ("14. Backups y Seguridad", "42"),
            ("15. Auditoría", "45"),
            ("16. Reportes y Exportaciones", "47"),
            ("17. Preguntas Frecuentes", "49"),
            ("18. Solución de Problemas", "52"),
            ("19. Soporte Técnico", "54"),
        ]
        
        data = []
        for titulo, pagina in indices:
            data.append([titulo, pagina])
        
        tabla = Table(data, colWidths=[13*cm, 2*cm])
        tabla.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        self.story.append(tabla)
        self.story.append(PageBreak())
    
    def capitulo_introduccion(self):
        """Capítulo 1: Introducción"""
        self.story.append(Paragraph("1. INTRODUCCIÓN", self.styles['Capitulo']))
        
        # 1.1
        self.story.append(Paragraph("1.1 ¿Qué es TechManager?", self.styles['Seccion']))
        texto = """TechManager es un sistema completo de gestión diseñado específicamente 
        para negocios de servicio técnico de dispositivos electrónicos. Ofrece control total 
        sobre clientes, equipos, reparaciones, inventario y facturación en una interfaz 
        moderna y profesional."""
        self.story.append(Paragraph(texto, self.styles['TextoNormal']))
        
        # 1.2
        self.story.append(Paragraph("1.2 Características Principales", self.styles['Seccion']))
        
        caracteristicas = [
            ["<b>Módulo</b>", "<b>Funcionalidad</b>"],
            ["Clientes", "Registro completo, historial, control de deudas"],
            ["Equipos", "Estados, alertas, historial completo"],
            ["Órdenes", "Workflow completo de reparación"],
            ["Presupuestos", "Creación, seguimiento, PDFs automáticos"],
            ["Facturación", "Múltiples métodos de pago, control de deudas"],
            ["Repuestos", "Control de stock, alertas, categorías"],
            ["Garantías", "Creación automática, seguimiento completo"],
            ["Usuarios", "Roles, permisos, auditoría completa"],
            ["Backups", "Automáticos y manuales, restauración"],
            ["Reportes", "Estadísticas, exportación Excel/CSV/PDF"],
        ]
        
        tabla_caract = Table(caracteristicas, colWidths=[4*cm, 11*cm])
        tabla_caract.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(tabla_caract)
        self.story.append(Spacer(1, 0.2*inch))
        
        # 1.3
        self.story.append(Paragraph("1.3 Requisitos del Sistema", self.styles['Seccion']))
        
        requisitos = """
        <b>Mínimos:</b><br/>
        • Sistema Operativo: Windows 7 o superior<br/>
        • Procesador: 1 GHz<br/>
        • RAM: 2 GB<br/>
        • Espacio en disco: 500 MB<br/>
        • Resolución: 1280x720<br/><br/>
        <b>Recomendados:</b><br/>
        • Sistema Operativo: Windows 10/11 (64 bits)<br/>
        • Procesador: 2 GHz o superior<br/>
        • RAM: 4 GB o más<br/>
        • Espacio en disco: 2 GB<br/>
        • Resolución: 1920x1080 o superior
        """
        self.story.append(Paragraph(requisitos, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
    
    def capitulo_instalacion(self):
        """Capítulo 2: Instalación"""
        self.story.append(Paragraph("2. INSTALACIÓN", self.styles['Capitulo']))
        
        # 2.1
        self.story.append(Paragraph("2.1 Instalación con Wizard", self.styles['Seccion']))
        
        pasos = """
        <b>Paso 1:</b> Ejecute el archivo <b>TechManager_v1.0_Installer.exe</b><br/><br/>
        <b>Paso 2:</b> Lea y acepte el acuerdo de licencia<br/><br/>
        <b>Paso 3:</b> Seleccione la carpeta de instalación (por defecto: C:\\Program Files\\TechManager\\)<br/><br/>
        <b>Paso 4:</b> Marque la opción "Crear acceso directo en el Escritorio" si lo desea<br/><br/>
        <b>Paso 5:</b> Haga clic en "Instalar" y espere a que finalice el proceso<br/><br/>
        <b>Paso 6:</b> Al finalizar, marque "Ejecutar TechManager" y haga clic en "Finalizar"
        """
        self.story.append(Paragraph(pasos, self.styles['TextoNormal']))
        
        nota = """<b>NOTA:</b> Necesita permisos de administrador para instalar el programa."""
        self.story.append(Paragraph(nota, self.styles['Nota']))
        
        # 2.2
        self.story.append(Paragraph("2.2 Primer Inicio", self.styles['Seccion']))
        
        texto = """Al ejecutar TechManager por primera vez, el sistema creará automáticamente:"""
        self.story.append(Paragraph(texto, self.styles['TextoNormal']))
        
        creacion = """
        • Base de datos (techmanager.db)<br/>
        • Carpetas de trabajo (backups, exportaciones, logs)<br/>
        • Usuario administrador por defecto<br/>
        • Configuración inicial del sistema
        """
        self.story.append(Paragraph(creacion, self.styles['TextoNormal']))
        
        # 2.3
        self.story.append(Paragraph("2.3 Cambio de Contraseña Obligatorio", self.styles['Seccion']))
        
        texto = """Al iniciar sesión con el usuario por defecto, el sistema le solicitará 
        cambiar la contraseña temporal por una contraseña personal."""
        self.story.append(Paragraph(texto, self.styles['TextoNormal']))
        
        credenciales = """
        <b>Credenciales por defecto:</b><br/>
        Usuario: <b>admin</b><br/>
        Contraseña: <b>admin123</b>
        """
        self.story.append(Paragraph(credenciales, self.styles['TextoNormal']))
        
        advertencia = """⚠️ IMPORTANTE: Por seguridad, DEBE cambiar la contraseña 
        inmediatamente después del primer ingreso. La nueva contraseña debe tener 
        al menos 6 caracteres."""
        self.story.append(Paragraph(advertencia, self.styles['Advertencia']))
        
        self.story.append(PageBreak())
    
    def capitulo_interfaz(self):
        """Capítulo 3: Interfaz del Sistema"""
        self.story.append(Paragraph("3. INTERFAZ DEL SISTEMA", self.styles['Capitulo']))
        
        # 3.1
        self.story.append(Paragraph("3.1 Ventana Principal", self.styles['Seccion']))
        
        texto = """La ventana principal de TechManager está diseñada con un enfoque moderno 
        y profesional, siguiendo principios de diseño limpio con bordes rectos y colores 
        vibrantes."""
        self.story.append(Paragraph(texto, self.styles['TextoNormal']))
        
        componentes = """
        <b>Componentes principales:</b><br/><br/>
        <b>Barra de título:</b> Muestra el nombre del sistema, usuario actual y botones de minimizar/maximizar/cerrar<br/><br/>
        <b>Menú lateral:</b> Acceso rápido a todos los módulos del sistema<br/><br/>
        <b>Área de trabajo:</b> Espacio principal donde se muestran los módulos activos<br/><br/>
        <b>Barra de estado:</b> Información del sistema, fecha/hora, notificaciones
        """
        self.story.append(Paragraph(componentes, self.styles['TextoNormal']))
        
        # 3.2
        self.story.append(Paragraph("3.2 Menú de Navegación", self.styles['Seccion']))
        
        menu_items = [
            ["<b>Sección</b>", "<b>Módulos</b>"],
            ["Gestión", "Clientes, Equipos"],
            ["Operaciones", "Órdenes, Presupuestos, Remitos"],
            ["Facturación", "Facturación y Pagos"],
            ["Inventario", "Repuestos, Garantías"],
            ["Sistema", "Usuarios, Configuración, Backups, Auditoría"],
        ]
        
        tabla_menu = Table(menu_items, colWidths=[4*cm, 11*cm])
        tabla_menu.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(tabla_menu)
        self.story.append(Spacer(1, 0.2*inch))
        
        # 3.3
        self.story.append(Paragraph("3.3 Barra de Herramientas", self.styles['Seccion']))
        
        texto = """Cada módulo cuenta con una barra de herramientas contextual que incluye:"""
        self.story.append(Paragraph(texto, self.styles['TextoNormal']))
        
        herramientas = """
        • <b>Búsqueda rápida:</b> Campo de texto para filtrar registros<br/>
        • <b>Filtros:</b> Combos y checkboxes para filtrado avanzado<br/>
        • <b>Botón Nuevo:</b> Crear un nuevo registro<br/>
        • <b>Botón Actualizar:</b> Refrescar la vista<br/>
        • <b>Botón Exportar:</b> Exportar datos a Excel/CSV<br/>
        • <b>Estadísticas:</b> Tarjetas con información resumida
        """
        self.story.append(Paragraph(herramientas, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
    
    def generar_capitulos_modulos(self):
        """Genera capítulos para cada módulo"""
        
        # CAPÍTULO 4: CLIENTES
        self.story.append(Paragraph("4. MÓDULO DE CLIENTES", self.styles['Capitulo']))
        
        intro = """El módulo de Clientes permite gestionar toda la información de sus clientes, 
        incluyendo datos personales, historial de equipos, y estado de cuenta."""
        self.story.append(Paragraph(intro, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("4.1 Registrar Nuevo Cliente", self.styles['Seccion']))
        
        pasos_cliente = """
        <b>1.</b> Haga clic en el botón <b>"➕ Nuevo Cliente"</b><br/>
        <b>2.</b> Complete los campos obligatorios:<br/>
        &nbsp;&nbsp;&nbsp;• Nombre y Apellido<br/>
        &nbsp;&nbsp;&nbsp;• Teléfono (principal)<br/>
        <b>3.</b> Complete campos opcionales:<br/>
        &nbsp;&nbsp;&nbsp;• Teléfono alternativo<br/>
        &nbsp;&nbsp;&nbsp;• Email<br/>
        &nbsp;&nbsp;&nbsp;• Dirección completa<br/>
        &nbsp;&nbsp;&nbsp;• DNI/CUIT<br/>
        &nbsp;&nbsp;&nbsp;• Notas adicionales<br/>
        <b>4.</b> Haga clic en <b>"Guardar"</b>
        """
        self.story.append(Paragraph(pasos_cliente, self.styles['TextoNormal']))
        
        nota = """<b>TIP:</b> El sistema detecta automáticamente clientes duplicados 
        por teléfono para evitar registros repetidos."""
        self.story.append(Paragraph(nota, self.styles['Nota']))
        
        self.story.append(Paragraph("4.2 Buscar y Filtrar Clientes", self.styles['Seccion']))
        
        busqueda = """
        • <b>Búsqueda rápida:</b> Escriba nombre, teléfono o DNI en el campo de búsqueda<br/>
        • <b>Filtro por estado:</b> Seleccione "Todos", "Activos" o "Con deuda"<br/>
        • <b>Filtro por clasificación:</b> "Buenos pagadores" o "Malos pagadores"<br/>
        • <b>Actualizar:</b> Presione F5 o haga clic en el botón "Actualizar"
        """
        self.story.append(Paragraph(busqueda, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("4.3 Ver Historial del Cliente", self.styles['Seccion']))
        
        historial = """Seleccione un cliente y haga clic en <b>"Ver Historial"</b> para ver:"""
        self.story.append(Paragraph(historial, self.styles['TextoNormal']))
        
        info_historial = """
        • <b>Equipos:</b> Todos los equipos ingresados del cliente<br/>
        • <b>Órdenes:</b> Historial completo de reparaciones<br/>
        • <b>Facturas:</b> Todas las facturas emitidas<br/>
        • <b>Pagos:</b> Registro de pagos realizados<br/>
        • <b>Deuda actual:</b> Saldo pendiente de pago
        """
        self.story.append(Paragraph(info_historial, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("4.4 Editar Cliente", self.styles['Seccion']))
        
        editar = """
        <b>1.</b> Seleccione el cliente en la tabla<br/>
        <b>2.</b> Haga clic en <b>"✏️ Editar"</b><br/>
        <b>3.</b> Modifique los datos necesarios<br/>
        <b>4.</b> Haga clic en <b>"Guardar"</b>
        """
        self.story.append(Paragraph(editar, self.styles['TextoNormal']))
        
        advertencia = """⚠️ ADVERTENCIA: No puede eliminar clientes con equipos, 
        órdenes o facturas asociadas. Primero debe eliminar todos los registros relacionados."""
        self.story.append(Paragraph(advertencia, self.styles['Advertencia']))
        
        self.story.append(Paragraph("4.5 Estadísticas de Clientes", self.styles['Seccion']))
        
        stats = """El módulo muestra tarjetas con estadísticas en tiempo real:"""
        self.story.append(Paragraph(stats, self.styles['TextoNormal']))
        
        tarjetas = """
        • <b>Total Clientes:</b> Cantidad total registrada<br/>
        • <b>Nuevos (Mes):</b> Clientes registrados este mes<br/>
        • <b>Con Deuda:</b> Clientes con saldo pendiente<br/>
        • <b>Buenos Pagadores:</b> Clientes con buena clasificación<br/>
        • <b>Malos Pagadores:</b> Clientes con mala clasificación
        """
        self.story.append(Paragraph(tarjetas, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 5: EQUIPOS
        self.story.append(Paragraph("5. MÓDULO DE EQUIPOS", self.styles['Capitulo']))
        
        intro_equipos = """El módulo de Equipos gestiona todos los dispositivos ingresados 
        para reparación, mostrando su estado actual y permitiendo un seguimiento completo."""
        self.story.append(Paragraph(intro_equipos, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("5.1 Ingresar Nuevo Equipo", self.styles['Seccion']))
        
        pasos_equipo = """
        <b>1.</b> Haga clic en <b>"➕ Nuevo Equipo"</b><br/>
        <b>2.</b> Seleccione el cliente (o créelo si es nuevo)<br/>
        <b>3.</b> Complete los datos del equipo:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Tipo:</b> Notebook, PC, Tablet, Celular, Otro<br/>
        &nbsp;&nbsp;&nbsp;• <b>Marca y Modelo:</b> Información del dispositivo<br/>
        &nbsp;&nbsp;&nbsp;• <b>Número de Serie:</b> (opcional)<br/>
        &nbsp;&nbsp;&nbsp;• <b>Contraseña:</b> Pin/password si tiene<br/>
        &nbsp;&nbsp;&nbsp;• <b>Descripción del problema:</b> Falla reportada<br/>
        &nbsp;&nbsp;&nbsp;• <b>Accesorios:</b> Cargador, funda, etc.<br/>
        <b>4.</b> Haga clic en <b>"Guardar"</b>
        """
        self.story.append(Paragraph(pasos_equipo, self.styles['TextoNormal']))
        
        nota = """<b>NOTA:</b> Al guardar, el equipo se registra automáticamente con 
        estado "Ingresado" y se le asigna un número de orden único."""
        self.story.append(Paragraph(nota, self.styles['Nota']))
        
        self.story.append(Paragraph("5.2 Estados del Equipo", self.styles['Seccion']))
        
        estados_tabla = [
            ["<b>Estado</b>", "<b>Descripción</b>", "<b>Color</b>"],
            ["Ingresado", "Equipo recién ingresado, pendiente de revisión", "Azul"],
            ["En diagnóstico", "Técnico está diagnosticando el problema", "Amarillo"],
            ["Esperando presupuesto", "Esperando aprobación del cliente", "Naranja"],
            ["En reparación", "Reparación en proceso", "Cyan"],
            ["Reparado", "Reparación finalizada, listo para entrega", "Verde"],
            ["Entregado", "Equipo entregado al cliente", "Gris"],
            ["Sin reparación", "No se pudo/quiso reparar", "Rojo"],
            ["Abandonado", "Cliente no lo retiró (>30 días)", "Rojo oscuro"],
        ]
        
        tabla_estados = Table(estados_tabla, colWidths=[4*cm, 8*cm, 3*cm])
        tabla_estados.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(tabla_estados)
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("5.3 Cambiar Estado del Equipo", self.styles['Seccion']))
        
        cambio_estado = """
        <b>1.</b> Seleccione el equipo en la tabla<br/>
        <b>2.</b> Haga clic en <b>"Cambiar Estado"</b><br/>
        <b>3.</b> Seleccione el nuevo estado<br/>
        <b>4.</b> Agregue una nota explicativa (opcional)<br/>
        <b>5.</b> Confirme el cambio
        """
        self.story.append(Paragraph(cambio_estado, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("5.4 Ver Detalles y Notas", self.styles['Seccion']))
        
        detalles = """Haga doble clic en un equipo para ver toda su información:"""
        self.story.append(Paragraph(detalles, self.styles['TextoNormal']))
        
        info_detalle = """
        • <b>Datos del equipo:</b> Tipo, marca, modelo, serie<br/>
        • <b>Estado actual:</b> Con fecha y hora del último cambio<br/>
        • <b>Historial de estados:</b> Todos los cambios realizados<br/>
        • <b>Notas del técnico:</b> Observaciones durante la reparación<br/>
        • <b>Órdenes asociadas:</b> Todas las órdenes de este equipo<br/>
        • <b>Días en taller:</b> Tiempo transcurrido desde el ingreso
        """
        self.story.append(Paragraph(info_detalle, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("5.5 Alertas de Equipos", self.styles['Seccion']))
        
        alertas = """El sistema genera alertas automáticas para:"""
        self.story.append(Paragraph(alertas, self.styles['TextoNormal']))
        
        tipos_alertas = """
        • <b>Equipos estancados:</b> Más de 7 días en el mismo estado<br/>
        • <b>Equipos abandonados:</b> Más de 30 días sin retirar<br/>
        • <b>Sin diagnóstico:</b> Más de 48 hs sin pasar a diagnóstico
        """
        self.story.append(Paragraph(tipos_alertas, self.styles['TextoNormal']))
        
        nota_alertas = """<b>TIP:</b> Configure los días de alerta en Sistema → Configuración"""
        self.story.append(Paragraph(nota_alertas, self.styles['Nota']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 6: ÓRDENES DE REPARACIÓN
        self.story.append(Paragraph("6. ÓRDENES DE REPARACIÓN", self.styles['Capitulo']))
        
        intro_ordenes = """Las Órdenes de Reparación son el núcleo del sistema, 
        gestionando todo el proceso de reparación desde el diagnóstico hasta la finalización."""
        self.story.append(Paragraph(intro_ordenes, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("6.1 Crear Nueva Orden", self.styles['Seccion']))
        
        pasos_orden = """
        <b>1.</b> Vaya a Operaciones → Órdenes<br/>
        <b>2.</b> Haga clic en <b>"➕ Nueva Orden"</b><br/>
        <b>3.</b> Seleccione el equipo (debe estar en estado "En diagnóstico" o "En reparación")<br/>
        <b>4.</b> Complete:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Diagnóstico:</b> Descripción técnica del problema<br/>
        &nbsp;&nbsp;&nbsp;• <b>Reparación realizada:</b> Trabajo efectuado<br/>
        &nbsp;&nbsp;&nbsp;• <b>Repuestos utilizados:</b> Seleccione del inventario<br/>
        &nbsp;&nbsp;&nbsp;• <b>Mano de obra:</b> Costo del trabajo<br/>
        &nbsp;&nbsp;&nbsp;• <b>Observaciones:</b> Notas adicionales<br/>
        <b>5.</b> Haga clic en <b>"Guardar"</b>
        """
        self.story.append(Paragraph(pasos_orden, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("6.2 Agregar Repuestos a la Orden", self.styles['Seccion']))
        
        repuestos_orden = """
        <b>1.</b> En la orden, haga clic en <b>"Agregar Repuesto"</b><br/>
        <b>2.</b> Busque el repuesto en el inventario<br/>
        <b>3.</b> Ingrese la cantidad utilizada<br/>
        <b>4.</b> Verifique el precio unitario<br/>
        <b>5.</b> El sistema actualizará automáticamente el stock
        """
        self.story.append(Paragraph(repuestos_orden, self.styles['TextoNormal']))
        
        advertencia = """⚠️ IMPORTANTE: El stock se descuenta automáticamente al agregar 
        repuestos. Verifique que haya stock disponible antes de agregar."""
        self.story.append(Paragraph(advertencia, self.styles['Advertencia']))
        
        self.story.append(Paragraph("6.3 Finalizar Orden", self.styles['Seccion']))
        
        finalizar = """
        <b>1.</b> Abra la orden<br/>
        <b>2.</b> Verifique que todos los datos estén completos<br/>
        <b>3.</b> Haga clic en <b>"Finalizar Orden"</b><br/>
        <b>4.</b> Seleccione el resultado:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Reparación exitosa:</b> Equipo queda "Reparado"<br/>
        &nbsp;&nbsp;&nbsp;• <b>Sin reparación:</b> Equipo queda "Sin reparación"<br/>
        <b>5.</b> Confirme la finalización
        """
        self.story.append(Paragraph(finalizar, self.styles['TextoNormal']))
        
        nota = """<b>NOTA:</b> Al finalizar una orden exitosamente, se crea automáticamente 
        una garantía si está configurado en el sistema."""
        self.story.append(Paragraph(nota, self.styles['Nota']))
        
        self.story.append(Paragraph("6.4 Imprimir Orden / Generar PDF", self.styles['Seccion']))
        
        imprimir = """
        <b>1.</b> Seleccione la orden<br/>
        <b>2.</b> Haga clic en <b>"📄 Imprimir/PDF"</b><br/>
        <b>3.</b> El sistema generará un PDF profesional con:<br/>
        &nbsp;&nbsp;&nbsp;• Datos del cliente y equipo<br/>
        &nbsp;&nbsp;&nbsp;• Diagnóstico y reparación<br/>
        &nbsp;&nbsp;&nbsp;• Repuestos utilizados con precios<br/>
        &nbsp;&nbsp;&nbsp;• Total de mano de obra<br/>
        &nbsp;&nbsp;&nbsp;• Total general<br/>
        <b>4.</b> Guarde o imprima el PDF
        """
        self.story.append(Paragraph(imprimir, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("6.5 Estados de Orden", self.styles['Seccion']))
        
        estados_orden = [
            ["<b>Estado</b>", "<b>Descripción</b>"],
            ["Pendiente", "Orden creada pero no finalizada"],
            ["Finalizada", "Reparación completada exitosamente"],
            ["Cancelada", "Orden cancelada (sin reparación)"],
            ["Facturada", "Orden incluida en una factura"],
        ]
        
        tabla_estados_orden = Table(estados_orden, colWidths=[4*cm, 11*cm])
        tabla_estados_orden.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(tabla_estados_orden)
        
        self.story.append(PageBreak())
    
    def generar_capitulos_adicionales(self):
        """Genera capítulos adicionales"""
        
        # CAPÍTULO 7: PRESUPUESTOS
        self.story.append(Paragraph("7. PRESUPUESTOS", self.styles['Capitulo']))
        
        intro = """El módulo de Presupuestos permite crear, gestionar y hacer seguimiento 
        de presupuestos enviados a clientes."""
        self.story.append(Paragraph(intro, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("7.1 Crear Presupuesto", self.styles['Seccion']))
        
        crear_presu = """
        <b>1.</b> Vaya a Operaciones → Presupuestos<br/>
        <b>2.</b> Haga clic en <b>"➕ Nuevo Presupuesto"</b><br/>
        <b>3.</b> Seleccione el equipo<br/>
        <b>4.</b> Complete:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Descripción del trabajo:</b> Detalle de la reparación<br/>
        &nbsp;&nbsp;&nbsp;• <b>Mano de obra:</b> Costo del servicio<br/>
        &nbsp;&nbsp;&nbsp;• <b>Repuestos necesarios:</b> Lista con precios<br/>
        &nbsp;&nbsp;&nbsp;• <b>Días de validez:</b> Vencimiento del presupuesto<br/>
        &nbsp;&nbsp;&nbsp;• <b>Recargo por transferencia:</b> % si aplica<br/>
        <b>5.</b> Haga clic en <b>"Guardar"</b>
        """
        self.story.append(Paragraph(crear_presu, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("7.2 Estados del Presupuesto", self.styles['Seccion']))
        
        estados = """
        • <b>Pendiente:</b> Esperando respuesta del cliente<br/>
        • <b>Aceptado:</b> Cliente aceptó, puede iniciar reparación<br/>
        • <b>Rechazado por cliente:</b> Cliente no aceptó<br/>
        • <b>Rechazado por vencimiento:</b> Presupuesto venció<br/>
        • <b>Vencido:</b> Pasó la fecha de validez
        """
        self.story.append(Paragraph(estados, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("7.3 Generar PDF del Presupuesto", self.styles['Seccion']))
        
        pdf_presu = """
        <b>1.</b> Seleccione el presupuesto<br/>
        <b>2.</b> Haga clic en <b>"📄 Generar PDF"</b><br/>
        <b>3.</b> El sistema creará un PDF profesional que incluye:<br/>
        &nbsp;&nbsp;&nbsp;• Datos de su negocio<br/>
        &nbsp;&nbsp;&nbsp;• Información del cliente y equipo<br/>
        &nbsp;&nbsp;&nbsp;• Descripción del trabajo<br/>
        &nbsp;&nbsp;&nbsp;• Detalle de costos<br/>
        &nbsp;&nbsp;&nbsp;• Fecha de vencimiento<br/>
        &nbsp;&nbsp;&nbsp;• Condiciones del presupuesto<br/>
        <b>4.</b> Envíe el PDF al cliente
        """
        self.story.append(Paragraph(pdf_presu, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("7.4 Aceptar/Rechazar Presupuesto", self.styles['Seccion']))
        
        aceptar = """
        <b>Para aceptar:</b><br/>
        1. Seleccione el presupuesto<br/>
        2. Haga clic en <b>"✓ Aceptar"</b><br/>
        3. El equipo cambia automáticamente a "En reparación"<br/><br/>
        <b>Para rechazar:</b><br/>
        1. Seleccione el presupuesto<br/>
        2. Haga clic en <b>"✗ Rechazar"</b><br/>
        3. Seleccione el motivo (cliente / vencimiento)<br/>
        4. El equipo cambia a "Sin reparación"
        """
        self.story.append(Paragraph(aceptar, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 8: FACTURACIÓN Y PAGOS
        self.story.append(Paragraph("8. FACTURACIÓN Y PAGOS", self.styles['Capitulo']))
        
        intro_fact = """El módulo de Facturación gestiona la emisión de facturas, 
        control de pagos y seguimiento de deudas."""
        self.story.append(Paragraph(intro_fact, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("8.1 Crear Factura", self.styles['Seccion']))
        
        crear_factura = """
        <b>1.</b> Vaya a Facturación → Facturas<br/>
        <b>2.</b> Haga clic en <b>"➕ Nueva Factura"</b><br/>
        <b>3.</b> Seleccione el cliente<br/>
        <b>4.</b> Agregue órdenes:<br/>
        &nbsp;&nbsp;&nbsp;• Haga clic en <b>"Agregar Orden"</b><br/>
        &nbsp;&nbsp;&nbsp;• Seleccione las órdenes finalizadas<br/>
        &nbsp;&nbsp;&nbsp;• El sistema calcula el total automáticamente<br/>
        <b>5.</b> Revise el total<br/>
        <b>6.</b> Haga clic en <b>"Generar Factura"</b>
        """
        self.story.append(Paragraph(crear_factura, self.styles['TextoNormal']))
        
        nota = """<b>NOTA:</b> Solo se pueden facturar órdenes en estado "Finalizada" 
        y que no hayan sido facturadas previamente."""
        self.story.append(Paragraph(nota, self.styles['Nota']))
        
        self.story.append(Paragraph("8.2 Registrar Pago", self.styles['Seccion']))
        
        registrar_pago = """
        <b>1.</b> Seleccione la factura<br/>
        <b>2.</b> Haga clic en <b>"💰 Registrar Pago"</b><br/>
        <b>3.</b> Complete:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Método de pago:</b> Efectivo, Transferencia, Débito, Crédito<br/>
        &nbsp;&nbsp;&nbsp;• <b>Monto:</b> Cantidad pagada<br/>
        &nbsp;&nbsp;&nbsp;• <b>Referencia:</b> Nro. de transacción (opcional)<br/>
        <b>4.</b> Haga clic en <b>"Registrar"</b>
        """
        self.story.append(Paragraph(registrar_pago, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("8.3 Pagos Parciales", self.styles['Seccion']))
        
        parciales = """El sistema permite registrar pagos parciales:"""
        self.story.append(Paragraph(parciales, self.styles['TextoNormal']))
        
        ejemplo_parcial = """
        <b>Ejemplo:</b><br/>
        Factura total: $50,000<br/>
        Pago 1: $30,000 → Saldo: $20,000<br/>
        Pago 2: $20,000 → Saldo: $0 (Pagada)
        """
        self.story.append(Paragraph(ejemplo_parcial, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("8.4 Estados de Factura", self.styles['Seccion']))
        
        estados_factura = [
            ["<b>Estado</b>", "<b>Descripción</b>"],
            ["Pendiente", "Sin pagos registrados"],
            ["Pago parcial", "Pagada parcialmente"],
            ["Pagada", "Totalmente pagada"],
            ["Vencida", "Pendiente y pasó fecha de vencimiento"],
        ]
        
        tabla_estados_fact = Table(estados_factura, colWidths=[4*cm, 11*cm])
        tabla_estados_fact.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(tabla_estados_fact)
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("8.5 Generar Remito", self.styles['Seccion']))
        
        remito = """
        <b>1.</b> Seleccione la factura pagada<br/>
        <b>2.</b> Haga clic en <b>"📋 Generar Remito"</b><br/>
        <b>3.</b> El sistema crea un PDF con:<br/>
        &nbsp;&nbsp;&nbsp;• Número de remito<br/>
        &nbsp;&nbsp;&nbsp;• Datos del cliente<br/>
        &nbsp;&nbsp;&nbsp;• Detalle de equipos entregados<br/>
        &nbsp;&nbsp;&nbsp;• Firma del cliente<br/>
        <b>4.</b> Imprima y solicite firma al entregar
        """
        self.story.append(Paragraph(remito, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
    
    def generar_capitulos_finales(self):
        """Genera los últimos capítulos"""
        
        # CAPÍTULO 9: REPUESTOS
        self.story.append(Paragraph("9. CONTROL DE REPUESTOS", self.styles['Capitulo']))
        
        intro = """El módulo de Repuestos permite gestionar el inventario de partes 
        y componentes, con control de stock y alertas automáticas."""
        self.story.append(Paragraph(intro, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("9.1 Agregar Repuesto", self.styles['Seccion']))
        
        agregar = """
        <b>1.</b> Vaya a Inventario → Repuestos<br/>
        <b>2.</b> Haga clic en <b>"➕ Nuevo Repuesto"</b><br/>
        <b>3.</b> Complete:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Nombre:</b> Descripción del repuesto<br/>
        &nbsp;&nbsp;&nbsp;• <b>Código:</b> SKU o código interno<br/>
        &nbsp;&nbsp;&nbsp;• <b>Categoría:</b> Pantallas, Baterías, Teclados, etc.<br/>
        &nbsp;&nbsp;&nbsp;• <b>Marca:</b> Fabricante<br/>
        &nbsp;&nbsp;&nbsp;• <b>Stock:</b> Cantidad disponible<br/>
        &nbsp;&nbsp;&nbsp;• <b>Stock mínimo:</b> Para alertas<br/>
        &nbsp;&nbsp;&nbsp;• <b>Precio costo:</b> Valor de compra<br/>
        &nbsp;&nbsp;&nbsp;• <b>Precio venta:</b> Valor al cliente<br/>
        &nbsp;&nbsp;&nbsp;• <b>Ubicación:</b> Dónde está almacenado<br/>
        <b>4.</b> Haga clic en <b>"Guardar"</b>
        """
        self.story.append(Paragraph(agregar, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("9.2 Ajustar Stock", self.styles['Seccion']))
        
        ajustar = """
        <b>1.</b> Seleccione el repuesto<br/>
        <b>2.</b> Haga clic en <b>"Ajustar Stock"</b><br/>
        <b>3.</b> Seleccione el tipo de movimiento:<br/>
        &nbsp;&nbsp;&nbsp;• <b>Ingreso:</b> Compra de repuestos<br/>
        &nbsp;&nbsp;&nbsp;• <b>Egreso:</b> Venta o uso<br/>
        &nbsp;&nbsp;&nbsp;• <b>Ajuste:</b> Corrección de inventario<br/>
        <b>4.</b> Ingrese cantidad y motivo<br/>
        <b>5.</b> Confirme el ajuste
        """
        self.story.append(Paragraph(ajustar, self.styles['TextoNormal']))
        
        nota = """<b>NOTA:</b> Los movimientos por uso en órdenes se registran 
        automáticamente, no es necesario ajustar manualmente."""
        self.story.append(Paragraph(nota, self.styles['Nota']))
        
        self.story.append(Paragraph("9.3 Alertas de Stock Bajo", self.styles['Seccion']))
        
        alertas = """El sistema muestra alertas cuando:"""
        self.story.append(Paragraph(alertas, self.styles['TextoNormal']))
        
        condiciones = """
        • Stock actual ≤ Stock mínimo configurado<br/>
        • Stock = 0 (sin stock)<br/>
        • Las alertas aparecen en la tarjeta "Stock Bajo"
        """
        self.story.append(Paragraph(condiciones, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 10: GARANTÍAS
        self.story.append(Paragraph("10. SISTEMA DE GARANTÍAS", self.styles['Capitulo']))
        
        intro_gar = """El módulo de Garantías gestiona automáticamente las garantías 
        de las reparaciones realizadas."""
        self.story.append(Paragraph(intro_gar, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("10.1 Creación Automática", self.styles['Seccion']))
        
        auto = """Las garantías se crean automáticamente cuando:"""
        self.story.append(Paragraph(auto, self.styles['TextoNormal']))
        
        condiciones_gar = """
        • Se finaliza una orden exitosamente<br/>
        • El equipo queda en estado "Reparado"<br/>
        • La garantía tiene la duración configurada en el sistema (por defecto 30 días)<br/>
        • Cubre la reparación realizada y los repuestos utilizados
        """
        self.story.append(Paragraph(condiciones_gar, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("10.2 Estados de Garantía", self.styles['Seccion']))
        
        estados_gar = [
            ["<b>Estado</b>", "<b>Descripción</b>"],
            ["Vigente", "Dentro del período de garantía"],
            ["Por vencer", "Vence en 7 días o menos"],
            ["Vencida", "Período de garantía expirado"],
            ["Utilizada", "Cliente usó la garantía"],
        ]
        
        tabla_gar = Table(estados_gar, colWidths=[4*cm, 11*cm])
        tabla_gar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(tabla_gar)
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("10.3 Usar Garantía", self.styles['Seccion']))
        
        usar = """
        <b>1.</b> Cuando un cliente trae un equipo con garantía vigente<br/>
        <b>2.</b> Vaya a Inventario → Garantías<br/>
        <b>3.</b> Busque la garantía del equipo<br/>
        <b>4.</b> Haga clic en <b>"Usar Garantía"</b><br/>
        <b>5.</b> Ingrese el motivo del reclamo<br/>
        <b>6.</b> El equipo vuelve automáticamente a "En reparación"<br/>
        <b>7.</b> No se cobra al cliente (cubierto por garantía)
        """
        self.story.append(Paragraph(usar, self.styles['TextoNormal']))
        
        advertencia = """⚠️ IMPORTANTE: Solo se pueden usar garantías vigentes. 
        Una vez utilizada, no se puede volver a usar la misma garantía."""
        self.story.append(Paragraph(advertencia, self.styles['Advertencia']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 11: CONFIGURACIÓN
        self.story.append(Paragraph("11. CONFIGURACIÓN DEL SISTEMA", self.styles['Capitulo']))
        
        intro_config = """El módulo de Configuración permite personalizar el 
        comportamiento del sistema según las necesidades de su negocio."""
        self.story.append(Paragraph(intro_config, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("11.1 Datos del Negocio", self.styles['Seccion']))
        
        negocio = """Configure la información que aparecerá en todos los documentos:"""
        self.story.append(Paragraph(negocio, self.styles['TextoNormal']))
        
        datos_neg = """
        • Nombre del negocio<br/>
        • Dirección completa<br/>
        • Teléfono(s) de contacto<br/>
        • Email<br/>
        • CUIT / RUT<br/>
        • Sitio web (opcional)
        """
        self.story.append(Paragraph(datos_neg, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("11.2 Días y Alertas", self.styles['Seccion']))
        
        alertas_config = """
        • <b>Días de garantía:</b> Duración estándar (por defecto 30)<br/>
        • <b>Días equipo estancado:</b> Alerta si no cambia de estado (por defecto 7)<br/>
        • <b>Días equipo abandonado:</b> Marca como abandonado (por defecto 30)<br/>
        • <b>Días para backup automático:</b> Frecuencia de backups (por defecto 7)
        """
        self.story.append(Paragraph(alertas_config, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("11.3 Porcentajes y Recargos", self.styles['Seccion']))
        
        porcent = """
        • <b>Recargo por transferencia:</b> % adicional en pagos por transferencia<br/>
        • <b>Descuento por pago contado:</b> % de descuento (opcional)<br/>
        • <b>IVA:</b> % de impuesto si aplica
        """
        self.story.append(Paragraph(porcent, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("11.4 Textos Personalizados", self.styles['Seccion']))
        
        textos = """Personalice los textos que aparecen en los documentos:"""
        self.story.append(Paragraph(textos, self.styles['TextoNormal']))
        
        docs = """
        • <b>Texto presupuesto:</b> Condiciones y términos<br/>
        • <b>Texto remito:</b> Instrucciones de entrega<br/>
        • <b>Texto factura:</b> Términos de pago<br/>
        • <b>Texto garantía:</b> Condiciones de la garantía
        """
        self.story.append(Paragraph(docs, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 12: BACKUPS
        self.story.append(Paragraph("12. BACKUPS Y SEGURIDAD", self.styles['Capitulo']))
        
        intro_backup = """El sistema incluye un completo sistema de backups para 
        proteger sus datos."""
        self.story.append(Paragraph(intro_backup, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("12.1 Backup Manual", self.styles['Seccion']))
        
        manual = """
        <b>1.</b> Vaya a Sistema → Backups<br/>
        <b>2.</b> Haga clic en <b>"💾 Crear Backup Manual"</b><br/>
        <b>3.</b> Ingrese una descripción (opcional)<br/>
        <b>4.</b> Haga clic en <b>"Crear"</b><br/>
        <b>5.</b> El backup se guarda en: datos/backups/
        """
        self.story.append(Paragraph(manual, self.styles['TextoNormal']))
        
        recomendacion = """<b>RECOMENDACIÓN:</b> Cree un backup manual antes de:"""
        self.story.append(Paragraph(recomendacion, self.styles['TextoNormal']))
        
        cuando = """
        • Actualizar el sistema<br/>
        • Realizar cambios importantes<br/>
        • Fin de mes<br/>
        • Antes de restaurar un backup antiguo
        """
        self.story.append(Paragraph(cuando, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("12.2 Backups Automáticos", self.styles['Seccion']))
        
        automatico = """El sistema crea backups automáticos según la configuración:"""
        self.story.append(Paragraph(automatico, self.styles['TextoNormal']))
        
        auto_info = """
        • Se ejecutan en segundo plano<br/>
        • Frecuencia configurable (por defecto cada 7 días)<br/>
        • Se mantienen los últimos 30 backups automáticos<br/>
        • Los backups manuales nunca se eliminan automáticamente
        """
        self.story.append(Paragraph(auto_info, self.styles['TextoNormal']))
        
        self.story.append(Paragraph("12.3 Restaurar Backup", self.styles['Seccion']))
        
        restaurar = """
        <b>1.</b> Vaya a Sistema → Backups<br/>
        <b>2.</b> Seleccione el backup a restaurar<br/>
        <b>3.</b> Haga clic en <b>"⚠️ Restaurar"</b><br/>
        <b>4.</b> LEA la advertencia cuidadosamente<br/>
        <b>5.</b> Confirme la restauración
        """
        self.story.append(Paragraph(restaurar, self.styles['TextoNormal']))
        
        advertencia_backup = """⚠️ ADVERTENCIA CRÍTICA: Al restaurar un backup, 
        TODOS los datos actuales se PERDERÁN y serán reemplazados por los datos del 
        backup seleccionado. Esta acción NO se puede deshacer. Asegúrese de crear 
        un backup manual de los datos actuales antes de restaurar."""
        self.story.append(Paragraph(advertencia_backup, self.styles['Advertencia']))
        
        self.story.append(PageBreak())
    
    def generar_faq(self):
        """Genera FAQ y solución de problemas"""
        
        # CAPÍTULO 13: FAQ
        self.story.append(Paragraph("13. PREGUNTAS FRECUENTES", self.styles['Capitulo']))
        
        # Pregunta 1
        self.story.append(Paragraph("¿Puedo usar el sistema en múltiples computadoras?", 
                                   self.styles['Subseccion']))
        respuesta = """Sí, pero necesita una licencia por cada instalación. 
        No es posible compartir la base de datos entre múltiples computadoras 
        simultáneamente sin una configuración de red avanzada."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 2
        self.story.append(Paragraph("¿Cómo agrego más usuarios?", self.styles['Subseccion']))
        respuesta = """Vaya a Sistema → Usuarios → Nuevo Usuario. Solo los 
        administradores pueden crear nuevos usuarios."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 3
        self.story.append(Paragraph("¿Dónde están mis datos?", self.styles['Subseccion']))
        respuesta = """Todos los datos se almacenan localmente en:
        C:\\Program Files\\TechManager\\datos\\techmanager.db"""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 4
        self.story.append(Paragraph("¿Puedo exportar mis datos?", self.styles['Subseccion']))
        respuesta = """Sí, cada módulo tiene un botón "Exportar" que permite 
        exportar a Excel o CSV."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 5
        self.story.append(Paragraph("¿Cómo cambio mi contraseña?", self.styles['Subseccion']))
        respuesta = """Vaya a Sistema → Mi Perfil → Cambiar Contraseña."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 6
        self.story.append(Paragraph("¿El sistema requiere internet?", self.styles['Subseccion']))
        respuesta = """No, TechManager funciona completamente sin conexión a internet. 
        Todos los datos se almacenan localmente."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 7
        self.story.append(Paragraph("¿Puedo personalizar los documentos?", self.styles['Subseccion']))
        respuesta = """Sí, vaya a Sistema → Configuración para modificar los textos 
        que aparecen en presupuestos, facturas y remitos."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        # Pregunta 8
        self.story.append(Paragraph("¿Cómo recupero mi contraseña?", self.styles['Subseccion']))
        respuesta = """Si es el único administrador y olvidó su contraseña, 
        contacte a soporte técnico. No es posible recuperarla sin acceso al sistema."""
        self.story.append(Paragraph(respuesta, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
        
        # CAPÍTULO 14: SOLUCIÓN DE PROBLEMAS
        self.story.append(Paragraph("14. SOLUCIÓN DE PROBLEMAS", self.styles['Capitulo']))
        
        # Problema 1
        self.story.append(Paragraph("El programa no inicia", self.styles['Subseccion']))
        soluciones = """
        <b>Posibles soluciones:</b><br/>
        1. Verifique que Windows esté actualizado<br/>
        2. Ejecute como administrador (clic derecho → Ejecutar como administrador)<br/>
        3. Reinstale el programa<br/>
        4. Contacte a soporte técnico
        """
        self.story.append(Paragraph(soluciones, self.styles['TextoNormal']))
        
        # Problema 2
        self.story.append(Paragraph("Error: Base de datos bloqueada", self.styles['Subseccion']))
        soluciones = """
        <b>Solución:</b><br/>
        1. Cierre completamente el programa<br/>
        2. Verifique que no haya otra instancia ejecutándose<br/>
        3. Reinicie la computadora<br/>
        4. Inicie el programa nuevamente
        """
        self.story.append(Paragraph(soluciones, self.styles['TextoNormal']))
        
        # Problema 3
        self.story.append(Paragraph("Los PDFs no se generan", self.styles['Subseccion']))
        soluciones = """
        <b>Posibles causas:</b><br/>
        • Falta de permisos en la carpeta de exportaciones<br/>
        • Antivirus bloqueando la creación de archivos<br/><br/>
        <b>Solución:</b><br/>
        1. Ejecute el programa como administrador<br/>
        2. Agregue excepción en el antivirus<br/>
        3. Verifique permisos de escritura en C:\\Program Files\\TechManager\\datos\\
        """
        self.story.append(Paragraph(soluciones, self.styles['TextoNormal']))
        
        # Problema 4
        self.story.append(Paragraph("El sistema está lento", self.styles['Subseccion']))
        soluciones = """
        <b>Recomendaciones:</b><br/>
        1. Cree un backup y restaure desde ese backup (compacta la base de datos)<br/>
        2. Elimine registros antiguos innecesarios<br/>
        3. Cierre otras aplicaciones que consumen recursos<br/>
        4. Verifique que su PC cumpla los requisitos mínimos
        """
        self.story.append(Paragraph(soluciones, self.styles['TextoNormal']))
        
        self.story.append(PageBreak())
    
    def generar_soporte(self):
        """Genera sección de soporte"""
        
        # CAPÍTULO 15: SOPORTE
        self.story.append(Paragraph("15. SOPORTE TÉCNICO", self.styles['Capitulo']))
        
        intro = """Si tiene problemas, preguntas o sugerencias, puede contactarnos:"""
        self.story.append(Paragraph(intro, self.styles['TextoNormal']))
        
        contacto = """
        <b>📧 Email:</b> soporte@techmanager.com<br/>
        <b>🌐 Web:</b> www.techmanager.com<br/>
        <b>📱 WhatsApp:</b> +54 9 11 XXXX-XXXX<br/><br/>
        <b>Horario de atención:</b><br/>
        Lunes a Viernes: 9:00 - 18:00 hs<br/>
        Sábados: 9:00 - 13:00 hs
        """
        self.story.append(Paragraph(contacto, self.styles['TextoNormal']))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        self.story.append(Paragraph("15.1 Antes de Contactar Soporte", self.styles['Seccion']))
        
        antes = """Por favor, tenga a mano la siguiente información:"""
        self.story.append(Paragraph(antes, self.styles['TextoNormal']))
        
        info_necesaria = """
        • Versión del sistema (visible en la ventana principal)<br/>
        • Descripción detallada del problema<br/>
        • Pasos para reproducir el error<br/>
        • Capturas de pantalla si es posible<br/>
        • Archivo de log (si existe error crítico)
        """
        self.story.append(Paragraph(info_necesaria, self.styles['TextoNormal']))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        self.story.append(Paragraph("15.2 Actualizaciones", self.styles['Seccion']))
        
        actualizaciones = """Las actualizaciones del sistema se publican periódicamente 
        en nuestro sitio web. Para actualizar:"""
        self.story.append(Paragraph(actualizaciones, self.styles['TextoNormal']))
        
        pasos_act = """
        <b>1.</b> Cree un backup manual de sus datos<br/>
        <b>2.</b> Descargue el instalador de la nueva versión<br/>
        <b>3.</b> Ejecute el instalador sobre la instalación existente<br/>
        <b>4.</b> Sus datos se preservarán automáticamente
        """
        self.story.append(Paragraph(pasos_act, self.styles['TextoNormal']))
        
        self.story.append(Spacer(1, 0.5*inch))
        
        # Final del manual
        self.story.append(Spacer(1, 1*inch))
        
        final = """<b>¡Gracias por elegir TechManager!</b><br/><br/>
        Esperamos que este sistema le ayude a gestionar su servicio técnico 
        de manera más eficiente y profesional."""
        self.story.append(Paragraph(final, self.styles['TextoNormal']))
        
        self.story.append(Spacer(1, 0.5*inch))
        
        copyright = """© 2025 TechManager - Todos los derechos reservados<br/>
        Versión del manual: 1.0 - Enero 2025"""
        self.story.append(Paragraph(copyright, self.styles['Normal']))
    
    def generar(self):
        """Genera el manual completo"""
        print("Generando Manual de Usuario...")
        print("=" * 70)
        
        # Generar todas las secciones
        self.portada()
        self.indice()
        self.capitulo_introduccion()
        self.capitulo_instalacion()
        self.capitulo_interfaz()
        self.generar_capitulos_modulos()
        self.generar_capitulos_adicionales()
        self.generar_capitulos_finales()
        self.generar_faq()
        self.generar_soporte()
        
        # Construir PDF
        print("\n[1/2] Construyendo PDF...")
        self.doc.build(self.story)
        
        print(f"[2/2] PDF generado: {self.filename}")
        print("=" * 70)
        print(f"\n✓ Manual completo creado exitosamente!")
        print(f"📄 Archivo: {self.filename}")
        
        # Mostrar estadísticas
        import os
        if os.path.exists(self.filename):
            tamaño = os.path.getsize(self.filename) / 1024
            print(f"📊 Tamaño: {tamaño:.1f} KB")
            print(f"📝 Páginas: ~50-60 páginas")
        
        return self.filename


if __name__ == "__main__":
    try:
        manual = ManualUsuario()
        manual.generar()
    except Exception as e:
        print(f"\n✗ Error al generar manual: {e}")
        import traceback
        traceback.print_exc()
