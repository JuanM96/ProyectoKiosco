# � Sistema de Licencias - POS Kiosco

Este directorio contiene el sistema de gestión de licencias mensuales para el software POS Kiosco.

## � Archivos principales

### `secure_license_admin.py`
**Administrador principal de licencias** con Firebase Admin SDK
- ✅ Crear nuevas licencias
- ✅ Verificar licencias existentes  
- ✅ Extender licencias
- ✅ Listar todas las licencias
- ✅ Generar Machine IDs

### `config.json`
**Configuración del sistema**
- URL de Firebase Database
- Configuración de soporte (email, teléfono)
- Tolerancia offline para validación

### `firebase-admin-key.json`
**Credenciales de Firebase** (privado)
- Archivo de credenciales del Admin SDK
- **NO subir al repositorio** (protegido por .gitignore)

## 🚀 Uso

### Para crear una nueva licencia:
```bash
python secure_license_admin.py
# Seleccionar opción 1: Agregar nueva licencia
```

### Para verificar una licencia:
```bash
python secure_license_admin.py
# Seleccionar opción 2: Verificar licencia específica
```

### Para ver todas las licencias:
```bash
python secure_license_admin.py
# Seleccionar opción 3: Listar todas las licencias
```

## 📋 Información requerida para nuevas licencias

Para crear una licencia, necesitas del cliente:
- **Nombre del computador** (ej: TIENDA-CAJA01)
- **Usuario de Windows** (ej: Vendedor)
- **Duración en meses** (ej: 1, 3, 6, 12)

## 🔧 Configuración

El sistema está preconfigurado y listo para usar. Solo necesitas:
1. Tener las credenciales Firebase en `firebase-admin-key.json`
2. Ejecutar `secure_license_admin.py`

## 🛡️ Seguridad

- Las credenciales están protegidas por .gitignore
- Solo el administrador puede crear/modificar licencias
- Validación automática de expiración
- Sistema offline con tolerancia configurable

---
**Versión:** 2.0  
**Autor:** JuanM96  
**Licencia:** Privado

- ⚠️ **NUNCA subas** `firebase-admin-key.json` a Git
- 🔐 Mantén las credenciales **solo en tu computadora**
- 📁 Esta carpeta debe estar en `.gitignore` para producción

## 🆘 **Soporte:**

Si tienes problemas:
1. Verifica que `config.json` tenga la URL correcta de Firebase
2. Asegúrate de que las reglas de Firebase estén configuradas
3. Para Firebase Admin SDK, verifica que las credenciales sean válidas