# Sistema POS Kiosco 🛒

Sistema de punto de venta (POS) desarrollado en Python con interfaz gráfica tkinter, diseñado específicamente para kioscos y pequeños comercios.

## 🚀 Características Principales

- **Gestión de Productos**: Agregar, editar, eliminar y buscar productos
- **Control de Stock**: Sistema configurable de inventario (se puede activar/desactivar)
- **Ventas**: Proceso completo de ventas con cálculo automático de totales
- **Reportes**: Generación de reportes de ventas en Excel y PDF
- **Usuarios**: Sistema de autenticación con diferentes niveles de acceso
- **Tickets**: Impresión de tickets de venta en PDF
- **Importación/Exportación**: Soporte para archivos Excel de productos
- **Interfaz Amigable**: Diseño intuitivo y fácil de usar

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- Windows 10/11 (recomendado)

### Dependencias Python

```txt
tkinter (incluido en Python)
sqlite3 (incluido en Python)
pandas
openpyxl
fpdf
Pillow (PIL)
```

## 🛠️ Instalación para Desarrollo

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/JuanM96/ProyectoKiosco.git
   cd ProyectoKiosco
   ```

2. **Instalar dependencias:**
   ```bash
   pip install pandas openpyxl fpdf Pillow
   ```

3. **Ejecutar el programa:**
   ```bash
   python pos-kiosco-python.py
   ```

## 📦 Generar Ejecutable

Para crear un archivo ejecutable (.exe) que funcione sin necesidad de tener Python instalado:

### Instalar PyInstaller:
```bash
pip install pyinstaller
```

### Generar el ejecutable:
```bash
pyinstaller --onefile --windowed --add-data "img;img" --icon "img\kiosco.ico" --clean pos-kiosco-python.py
```

### Parámetros explicados:
- `--onefile`: Genera un solo archivo ejecutable
- `--windowed`: Oculta la consola (solo interfaz gráfica)
- `--add-data "img;img"`: Incluye la carpeta de imágenes en el ejecutable
- `--icon "img\kiosco.ico"`: Establece el ícono del ejecutable
- `--clean`: Limpia archivos temporales antes de compilar

El ejecutable se generará en la carpeta `dist/`.

## 🎯 Uso del Sistema

### Primera Ejecución
1. Al abrir por primera vez, el sistema creará automáticamente la base de datos
2. Usuario administrador por defecto: **admin** / **admin**
3. Se recomienda cambiar la contraseña inmediatamente

### Funcionalidades Principales

#### Gestión de Productos
- **Agregar**: Nombre, código de barras, precio, stock inicial
- **Editar**: Modificar cualquier campo del producto
- **Eliminar**: Borrar productos individuales o todos a la vez
- **Buscar**: Por nombre o código de barras
- **Importar**: Desde archivos Excel (.xlsx)
- **Exportar**: A archivos Excel

#### Sistema de Ventas
1. Seleccionar productos desde la lista o buscar por código/nombre
2. Especificar cantidad
3. El sistema calcula automáticamente el total
4. Generar ticket de venta en PDF
5. Registro automático en base de datos

#### Configuración de Stock
- **Activar/Desactivar**: Control total del sistema de inventario
- **Advertencias**: Confirmación múltiple antes de cambios importantes
- **Reorganización**: Los IDs se reorganizan automáticamente

#### Reportes
- **Ventas por período**: Filtrar por fechas
- **Exportar a Excel**: Datos completos de ventas
- **Tickets PDF**: Guardado automático en carpeta `tickets/`

## 📁 Estructura del Proyecto

```
ProyectoKiosco/
├── pos-kiosco-python.py     # Archivo principal del sistema
├── img/                     # Recursos de imágenes
│   ├── kiosco.ico          # Ícono del programa
│   └── kioscoimg.png       # Logo del sistema
├── tickets/                # Tickets generados (creado automáticamente)
├── kiosco.db               # Base de datos SQLite (creado automáticamente)
├── build/                  # Archivos temporales de compilación
├── dist/                   # Ejecutable generado
└── README.md               # Este archivo
```

## 🗄️ Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **productos**: Información de productos y stock
- **ventas**: Registro de todas las ventas realizadas
- **items_venta**: Detalles de productos vendidos por transacción
- **usuarios**: Cuentas de acceso al sistema
- **configuracion**: Ajustes del sistema (stock habilitado/deshabilitado)

## 🔐 Seguridad

- **Autenticación**: Sistema de usuarios con contraseñas
- **Confirmaciones**: Acciones críticas requieren confirmación múltiple
- **Validaciones**: Entrada de datos validada para prevenir errores

## 🚨 Solución de Problemas

### Error de DLL faltantes
Si al ejecutar el .exe aparecen errores de DLL:
1. Instalar Microsoft Visual C++ Redistributable
2. Regenerar el ejecutable con PyInstaller

### Problemas de permisos
- Ejecutar como administrador si es necesario
- Verificar permisos de escritura en la carpeta del programa

### Base de datos corrupta
- Eliminar el archivo `kiosco.db`
- El sistema recreará la base de datos automáticamente

## 📝 Notas de Desarrollo

- **Versión Python**: Desarrollado y probado en Python 3.8+
- **Interfaz**: tkinter nativo de Python para máxima compatibilidad
- **Base de datos**: SQLite para simplicidad y portabilidad
- **Recursos**: Manejo inteligente de rutas para desarrollo y ejecutable

## 🤝 Contribución

Este proyecto está en desarrollo activo. Las mejoras y sugerencias son bienvenidas.

## 📄 Licencia

Proyecto desarrollado para uso comercial en kioscos y pequeños comercios.

---
**Desarrollado por**: JuanM96  
**Fecha**: Octubre 2025  
**Versión**: 1.0