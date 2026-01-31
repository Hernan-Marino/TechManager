# 🔧 TechManager v1.0

**Sistema de Gestión para Servicio Técnico de Dispositivos**

Sistema profesional para talleres de reparación de celulares, tablets, PCs, consolas y otros dispositivos tecnológicos.

---

## 📋 Características Principales

✅ Gestión completa de clientes y dispositivos  
✅ Control de órdenes de trabajo y reparaciones  
✅ Sistema de presupuestos con vencimiento automático  
✅ Inventario de repuestos (nuevos y recuperados)  
✅ Control de pagos y facturación  
✅ Garantías con vencimiento automático  
✅ Reportes en PDF y Excel  
✅ Sistema de alertas (equipos estancados, deudas)  
✅ Búsqueda global unificada  
✅ Panel de notificaciones  
✅ Auditoría completa del sistema  
✅ Backups automáticos (local + nube)  
✅ Importación masiva desde Excel  
✅ Permisos por rol (Admin / Técnico)  
✅ Impresión térmica y A4  
✅ Personalización completa (logos, colores)  

---

## 🖥️ Requisitos del Sistema

- **Sistema Operativo:** Windows 7/10/11, Linux, macOS
- **Python:** 3.10 o superior
- **Espacio en disco:** 50 MB
- **RAM:** 2 GB mínimo

---

## 🚀 Instalación

### Opción 1: Instalador (Recomendado)
1. Descargar `TechManager_v1.0_Setup.exe`
2. Ejecutar el instalador
3. Seguir las instrucciones en pantalla
4. ¡Listo! El sistema se abre automáticamente

### Opción 2: Desde código fuente
```bash
# 1. Clonar o descargar el proyecto
cd techmanager

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el sistema
python main.py
```

---

## 📚 Estructura del Proyecto

```
techmanager/
├── main.py                     # Punto de entrada
├── requirements.txt            # Dependencias
├── base_datos/                 # Base de datos SQLite
├── sistema_base/               # Configuración y seguridad
├── modulos/                    # Lógica de negocio
├── interfaz/                   # Interfaz gráfica
├── impresion/                  # PDFs y documentos
├── datos/                      # Base de datos y archivos
└── recursos/                   # Imágenes, logos, fuentes
```

---

## 👤 Primer Uso

1. Al iniciar por primera vez, se crea automáticamente:
   - Base de datos vacía
   - Usuario Admin por defecto:
     - **Usuario:** `admin`
     - **Contraseña:** `admin123`
   
2. **IMPORTANTE:** Cambiar la contraseña del admin inmediatamente

---

## 🔐 Roles y Permisos

### Admin (Administrador)
- Acceso total al sistema
- Gestión de usuarios
- Configuración del sistema
- Marcar deudas como incobrables
- Eliminar registros
- Ver reportes financieros completos

### Técnico
- Ver todos los registros
- Crear y modificar clientes, equipos, órdenes
- Registrar pagos
- Usar inventario
- Ver reportes básicos
- **No puede:** eliminar, modificar configuración, marcar incobrables

---

## 📖 Manual de Uso

### Registrar un nuevo equipo:
1. Ir a **Equipos** → **Nuevo Equipo**
2. Completar datos del cliente (si es nuevo)
3. Seleccionar tipo de dispositivo
4. Ingresar marca, modelo, falla
5. Generar remito de ingreso
6. Imprimir y hacer firmar

### Crear presupuesto:
1. Ir a **Presupuestos** → **Nuevo**
2. Seleccionar equipo
3. Describir reparación
4. Ingresar monto
5. Seleccionar método de pago (si es transferencia → +10% automático)
6. Enviar al cliente
7. Presupuesto vence automáticamente a los 7 días

### Registrar reparación:
1. Cliente acepta presupuesto
2. Cobrar 50% de anticipo
3. Sistema genera orden de trabajo automáticamente
4. Técnico realiza reparación
5. Registrar repuestos usados (si aplica)
6. Finalizar orden
7. Avisar al cliente que está listo

---

## 🛠️ Soporte

Para soporte técnico o consultas:
- **Email:** soporte@techmanager.com
- **WhatsApp:** +54 9 221 XXX-XXXX

---

## 📄 Licencia

Propietario. Todos los derechos reservados.

---

## 🔄 Versiones

- **v1.0** (Actual) - Versión inicial con todas las funcionalidades base
- **v2.0** (Próximamente) - Versión Network para múltiples PCs en red

---

## 👨‍💻 Desarrollado por

**TechManager Development Team**  
© 2025 - Todos los derechos reservados

---

¡Gracias por usar TechManager! 🚀
