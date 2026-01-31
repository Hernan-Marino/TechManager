# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - MÓDULO DE CONFIGURACIÓN
============================================================================
Lógica de negocio para gestión de configuración del sistema
(Complementa sistema_base.configuracion)
============================================================================
"""

import os
import shutil
from base_datos.conexion import db
from sistema_base.configuracion import config


class ModuloConfiguracion:
    """Clase para manejar la lógica de negocio de configuración"""
    
    @staticmethod
    def obtener_configuracion_completa():
        """
        Obtiene toda la configuración del sistema
        
        Returns:
            dict: Configuración completa
        """
        try:
            configuracion = {}
            
            # Datos del negocio
            configuracion['nombre_negocio'] = config.nombre_negocio
            configuracion['direccion_negocio'] = config.direccion_negocio
            configuracion['telefono_negocio'] = config.telefono_negocio
            configuracion['email_negocio'] = config.email_negocio
            configuracion['cuit_negocio'] = config.cuit_negocio
            
            # Colores
            configuracion['color_primario'] = config.color_primario
            configuracion['color_secundario'] = config.color_secundario
            configuracion['color_acento'] = config.color_acento
            
            # Logos
            configuracion['ruta_logo_sistema'] = config.ruta_logo_sistema
            configuracion['ruta_logo_remitos'] = config.ruta_logo_remitos
            configuracion['ruta_logo_comprobantes'] = config.ruta_logo_comprobantes
            
            # Alertas y días
            configuracion['dias_alerta_equipo_estancado'] = config.dias_alerta_equipo_estancado
            configuracion['dias_alerta_equipo_abandonado'] = config.dias_alerta_equipo_abandonado
            configuracion['dias_vencimiento_presupuesto'] = config.dias_vencimiento_presupuesto
            configuracion['dias_garantia_reparacion'] = getattr(config, "dias_garantia_reparacion", 90)
            
            # Porcentajes y montos
            configuracion['porcentaje_recargo_transferencia'] = config.porcentaje_recargo_transferencia
            configuracion['porcentaje_minimo_anticipo'] = config.porcentaje_minimo_anticipo
            configuracion['cantidad_minima_stock_repuestos'] = config.cantidad_minima_stock_repuestos
            
            # Textos personalizables
            configuracion['texto_pie_remito'] = config.texto_pie_remito
            configuracion['texto_pie_presupuesto'] = config.texto_pie_presupuesto
            configuracion['texto_pie_factura'] = config.texto_pie_factura
            configuracion['texto_garantia'] = config.texto_garantia
            
            # Backups
            configuracion['backup_automatico_habilitado'] = config.backup_automatico_habilitado
            configuracion['backup_dias_intervalo'] = config.backup_dias_intervalo
            configuracion['backup_dias_retencion'] = config.backup_dias_retencion
            
            return configuracion
            
        except Exception as e:
            config.guardar_log(f"Error al obtener configuración: {e}", "ERROR")
            return {}
    
    @staticmethod
    def actualizar_datos_negocio(nombre, direccion, telefono, email, cuit, id_usuario):
        """
        Actualiza los datos del negocio
        
        Args:
            nombre (str): Nombre del negocio
            direccion (str): Dirección
            telefono (str): Teléfono
            email (str): Email
            cuit (str): CUIT
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            # Solo admin
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración"
            
            # Actualizar en BD
            consulta = """
            UPDATE configuracion_sistema
            SET valor = ?
            WHERE clave = ?
            """
            
            db.ejecutar_consulta(consulta, (nombre, 'nombre_negocio'))
            db.ejecutar_consulta(consulta, (direccion, 'direccion_negocio'))
            db.ejecutar_consulta(consulta, (telefono, 'telefono_negocio'))
            db.ejecutar_consulta(consulta, (email, 'email_negocio'))
            db.ejecutar_consulta(consulta, (cuit, 'cuit_negocio'))
            
            # Recargar configuración
            config.cargar_configuracion()
            
            # Registrar en auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo="Datos del negocio actualizados"
            )
            
            config.guardar_log("Datos del negocio actualizados", "INFO")
            return True, "Datos del negocio actualizados"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar datos del negocio: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def actualizar_colores(color_primario, color_secundario, color_acento, id_usuario):
        """
        Actualiza los colores del sistema
        
        Args:
            color_primario (str): Color primario (hex)
            color_secundario (str): Color secundario (hex)
            color_acento (str): Color de acento (hex)
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración"
            
            # Actualizar en BD
            consulta = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
            
            db.ejecutar_consulta(consulta, (color_primario, 'color_primario'))
            db.ejecutar_consulta(consulta, (color_secundario, 'color_secundario'))
            db.ejecutar_consulta(consulta, (color_acento, 'color_acento'))
            
            # Recargar
            config.cargar_configuracion()
            
            # Auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo="Colores del sistema actualizados"
            )
            
            config.guardar_log("Colores actualizados", "INFO")
            return True, "Colores actualizados. Reinicie para ver los cambios."
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar colores: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def actualizar_dias_alertas(dias_estancado, dias_abandonado, dias_vencimiento, 
                               dias_garantia, id_usuario):
        """
        Actualiza los días de alertas
        
        Args:
            dias_estancado (int): Días para alerta de equipo estancado
            dias_abandonado (int): Días para alerta de equipo abandonado
            dias_vencimiento (int): Días de vencimiento de presupuestos
            dias_garantia (int): Días de garantía de reparación
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración"
            
            consulta = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
            
            db.ejecutar_consulta(consulta, (str(dias_estancado), 'dias_alerta_equipo_estancado'))
            db.ejecutar_consulta(consulta, (str(dias_abandonado), 'dias_alerta_equipo_abandonado'))
            db.ejecutar_consulta(consulta, (str(dias_vencimiento), 'dias_vencimiento_presupuesto'))
            db.ejecutar_consulta(consulta, (str(dias_garantia), 'dias_garantia_reparacion'))
            
            config.cargar_configuracion()
            
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo="Días de alertas actualizados"
            )
            
            config.guardar_log("Días de alertas actualizados", "INFO")
            return True, "Días de alertas actualizados"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar días de alertas: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def actualizar_porcentajes(recargo_transferencia, minimo_anticipo, 
                              stock_minimo, id_usuario):
        """
        Actualiza porcentajes y montos
        
        Args:
            recargo_transferencia (float): Porcentaje de recargo
            minimo_anticipo (float): Porcentaje mínimo de anticipo
            stock_minimo (int): Cantidad mínima de stock
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración"
            
            consulta = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
            
            db.ejecutar_consulta(consulta, (str(recargo_transferencia), 'porcentaje_recargo_transferencia'))
            db.ejecutar_consulta(consulta, (str(minimo_anticipo), 'porcentaje_minimo_anticipo'))
            db.ejecutar_consulta(consulta, (str(stock_minimo), 'cantidad_minima_stock_repuestos'))
            
            config.cargar_configuracion()
            
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo="Porcentajes y montos actualizados"
            )
            
            config.guardar_log("Porcentajes actualizados", "INFO")
            return True, "Porcentajes actualizados"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar porcentajes: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def actualizar_textos(texto_remito, texto_presupuesto, texto_factura, 
                         texto_garantia, id_usuario):
        """
        Actualiza textos personalizables
        
        Args:
            texto_remito (str): Texto pie de remito
            texto_presupuesto (str): Texto pie de presupuesto
            texto_factura (str): Texto pie de factura
            texto_garantia (str): Texto de garantía
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración"
            
            consulta = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
            
            db.ejecutar_consulta(consulta, (texto_remito, 'texto_pie_remito'))
            db.ejecutar_consulta(consulta, (texto_presupuesto, 'texto_pie_presupuesto'))
            db.ejecutar_consulta(consulta, (texto_factura, 'texto_pie_factura'))
            db.ejecutar_consulta(consulta, (texto_garantia, 'texto_garantia'))
            
            config.cargar_configuracion()
            
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo="Textos personalizables actualizados"
            )
            
            config.guardar_log("Textos actualizados", "INFO")
            return True, "Textos actualizados"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar textos: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def subir_logo(tipo_logo, archivo_origen, id_usuario):
        """
        Sube un logo al sistema
        
        Args:
            tipo_logo (str): 'sistema', 'remitos', o 'comprobantes'
            archivo_origen (str): Ruta del archivo a subir
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje, ruta_destino)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración", None
            
            # Verificar que el archivo existe
            if not os.path.exists(archivo_origen):
                return False, "El archivo no existe", None
            
            # Crear carpeta de logos si no existe
            carpeta_logos = os.path.join(config.directorio_base, "recursos", "logos")
            if not os.path.exists(carpeta_logos):
                os.makedirs(carpeta_logos)
            
            # Obtener extensión
            extension = os.path.splitext(archivo_origen)[1]
            
            # Nombre del archivo destino
            nombre_destino = f"logo_{tipo_logo}{extension}"
            ruta_destino = os.path.join(carpeta_logos, nombre_destino)
            
            # Copiar archivo
            shutil.copy2(archivo_origen, ruta_destino)
            
            # Actualizar en BD
            clave = f"ruta_logo_{tipo_logo}"
            consulta = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
            db.ejecutar_consulta(consulta, (ruta_destino, clave))
            
            # Recargar
            config.cargar_configuracion()
            
            # Auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo=f"Logo de {tipo_logo} actualizado"
            )
            
            config.guardar_log(f"Logo de {tipo_logo} actualizado", "INFO")
            return True, f"Logo de {tipo_logo} actualizado", ruta_destino
            
        except Exception as e:
            config.guardar_log(f"Error al subir logo: {e}", "ERROR")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def actualizar_config_backups(automatico, dias_intervalo, dias_retencion, id_usuario):
        """
        Actualiza configuración de backups
        
        Args:
            automatico (bool): Si está habilitado el backup automático
            dias_intervalo (int): Días entre backups automáticos
            dias_retencion (int): Días de retención de backups
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden modificar la configuración"
            
            consulta = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
            
            db.ejecutar_consulta(consulta, (str(1 if automatico else 0), 'backup_automatico_habilitado'))
            db.ejecutar_consulta(consulta, (str(dias_intervalo), 'backup_dias_intervalo'))
            db.ejecutar_consulta(consulta, (str(dias_retencion), 'backup_dias_retencion'))
            
            config.cargar_configuracion()
            
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Modificar",
                modulo="Configuración",
                id_registro=0,
                motivo="Configuración de backups actualizada"
            )
            
            config.guardar_log("Configuración de backups actualizada", "INFO")
            return True, "Configuración de backups actualizada"
            
        except Exception as e:
            config.guardar_log(f"Error al actualizar config de backups: {e}", "ERROR")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def restaurar_valores_defecto(id_usuario):
        """
        Restaura todos los valores a los valores por defecto
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            tuple: (exito, mensaje)
        """
        try:
            if not config.es_admin:
                return False, "Solo administradores pueden restaurar valores"
            
            # Restaurar valores por defecto en la BD
            config.inicializar_configuracion_defecto()
            
            # Recargar
            config.cargar_configuracion()
            
            # Auditoría
            from sistema_base.seguridad import registrar_accion_auditoria
            registrar_accion_auditoria(
                id_usuario=id_usuario,
                accion="Restaurar",
                modulo="Configuración",
                id_registro=0,
                motivo="Configuración restaurada a valores por defecto",
                es_critica=True
            )
            
            config.guardar_log("Configuración restaurada a valores por defecto", "WARNING")
            return True, "Configuración restaurada a valores por defecto"
            
        except Exception as e:
            config.guardar_log(f"Error al restaurar valores: {e}", "ERROR")
            return False, f"Error: {str(e)}"
