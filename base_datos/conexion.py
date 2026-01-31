# -*- coding: utf-8 -*-
"""
============================================================================
TECHMANAGER v1.0 - CONEXIÓN A BASE DE DATOS
============================================================================
Maneja la conexión a la base de datos SQLite
Implementa el patrón Singleton para una única conexión
============================================================================
"""

import sqlite3
from pathlib import Path
from sistema_base.configuracion import config


class ConexionBD:
    """
    Clase Singleton para manejar la conexión a la base de datos
    """
    _instancia = None
    _conexion = None
    
    def __new__(cls):
        """
        Implementa el patrón Singleton
        Solo puede existir una instancia de ConexionBD
        """
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def conectar(self):
        """
        Establece la conexión con la base de datos
        
        Returns:
            sqlite3.Connection: Objeto de conexión
        """
        if self._conexion is None:
            try:
                # Crear directorio de datos si no existe
                config.ruta_datos.mkdir(parents=True, exist_ok=True)
                
                # Conectar a la base de datos
                self._conexion = sqlite3.connect(
                    str(config.ruta_base_datos),
                    check_same_thread=False
                )
                
                # Habilitar foreign keys
                self._conexion.execute("PRAGMA foreign_keys = ON")
                
                # Configurar row_factory para obtener resultados como diccionarios
                self._conexion.row_factory = sqlite3.Row
                
                config.guardar_log("Conexión a base de datos establecida", "INFO")
                
            except sqlite3.Error as e:
                config.guardar_log(f"Error al conectar a la base de datos: {e}", "ERROR")
                raise
        
        return self._conexion
    
    def desconectar(self):
        """
        Cierra la conexión con la base de datos
        """
        if self._conexion is not None:
            try:
                self._conexion.close()
                self._conexion = None
                config.guardar_log("Conexión a base de datos cerrada", "INFO")
            except sqlite3.Error as e:
                config.guardar_log(f"Error al cerrar conexión: {e}", "ERROR")
    
    def ejecutar_consulta(self, consulta, parametros=None):
        """
        Ejecuta una consulta SQL (INSERT, UPDATE, DELETE)
        
        Args:
            consulta (str): Consulta SQL a ejecutar
            parametros (tuple): Parámetros de la consulta
            
        Returns:
            int: ID del último registro insertado (si aplica)
        """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        try:
            if parametros:
                cursor.execute(consulta, parametros)
            else:
                cursor.execute(consulta)
            
            conexion.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            conexion.rollback()
            config.guardar_log(f"Error al ejecutar consulta: {e}", "ERROR")
            raise
        finally:
            cursor.close()
    
    def ejecutar_muchas(self, consulta, lista_parametros):
        """
        Ejecuta múltiples consultas SQL (para inserciones masivas)
        
        Args:
            consulta (str): Consulta SQL a ejecutar
            lista_parametros (list): Lista de tuplas con parámetros
            
        Returns:
            int: Cantidad de registros afectados
        """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        try:
            cursor.executemany(consulta, lista_parametros)
            conexion.commit()
            return cursor.rowcount
            
        except sqlite3.Error as e:
            conexion.rollback()
            config.guardar_log(f"Error al ejecutar consultas múltiples: {e}", "ERROR")
            raise
        finally:
            cursor.close()
    
    def obtener_uno(self, consulta, parametros=None):
        """
        Ejecuta una consulta SELECT y retorna un solo resultado
        
        Args:
            consulta (str): Consulta SQL a ejecutar
            parametros (tuple): Parámetros de la consulta
            
        Returns:
            dict: Resultado como diccionario (o None si no hay resultados)
        """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        try:
            if parametros:
                cursor.execute(consulta, parametros)
            else:
                cursor.execute(consulta)
            
            resultado = cursor.fetchone()
            
            if resultado:
                return dict(resultado)
            return None
            
        except sqlite3.Error as e:
            config.guardar_log(f"Error al obtener registro: {e}", "ERROR")
            raise
        finally:
            cursor.close()
    
    def obtener_todos(self, consulta, parametros=None):
        """
        Ejecuta una consulta SELECT y retorna todos los resultados
        
        Args:
            consulta (str): Consulta SQL a ejecutar
            parametros (tuple): Parámetros de la consulta
            
        Returns:
            list: Lista de resultados como diccionarios
        """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        try:
            if parametros:
                cursor.execute(consulta, parametros)
            else:
                cursor.execute(consulta)
            
            resultados = cursor.fetchall()
            
            return [dict(row) for row in resultados]
            
        except sqlite3.Error as e:
            config.guardar_log(f"Error al obtener registros: {e}", "ERROR")
            raise
        finally:
            cursor.close()
    
    def tabla_existe(self, nombre_tabla):
        """
        Verifica si una tabla existe en la base de datos
        
        Args:
            nombre_tabla (str): Nombre de la tabla
            
        Returns:
            bool: True si existe, False si no
        """
        consulta = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        resultado = self.obtener_uno(consulta, (nombre_tabla,))
        return resultado is not None
    
    def vaciar_tabla(self, nombre_tabla):
        """
        Elimina todos los registros de una tabla
        
        Args:
            nombre_tabla (str): Nombre de la tabla
        """
        consulta = f"DELETE FROM {nombre_tabla}"
        self.ejecutar_consulta(consulta)
        config.guardar_log(f"Tabla {nombre_tabla} vaciada", "INFO")
    
    def obtener_version_esquema(self):
        """
        Obtiene la versión del esquema de la base de datos
        
        Returns:
            int: Versión del esquema
        """
        try:
            if self.tabla_existe('configuracion_sistema'):
                # La versión se puede guardar en la tabla de configuración
                return 1
            return 0
        except:
            return 0


# ============================================================================
# Instancia global de conexión (Singleton)
# ============================================================================
db = ConexionBD()
