#!/usr/bin/env python3
"""
Administrador de licencias con Firebase Admin SDK
Este script usa credenciales administrativas para gestionar licencias sin modificar reglas
"""

import firebase_admin
from firebase_admin import credentials, db
import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import requests

class SecureLicenseAdmin:
    def __init__(self):
        self.config = self.load_config()
        self.firebase_url = self.config['firebase']['url']
        self.firebase_initialized = False
        
        # Intentar inicializar Firebase Admin SDK
        if self.init_firebase_admin():
            self.use_admin_sdk = True
            print("✅ Firebase Admin SDK inicializado correctamente")
        else:
            self.use_admin_sdk = False
            print("⚠️ Firebase Admin SDK no disponible, usando método HTTP directo")
            
    def load_config(self):
        """Carga la configuración desde config.json"""
        # Lista de posibles ubicaciones del archivo config.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_paths = [
            os.path.join(script_dir, "config.json"),           # En el mismo directorio que el script
            "config.json",                                     # En el directorio actual de trabajo
            "../config.json",                                  # En el directorio padre
            os.path.join(script_dir, "../config.json")        # Directorio padre relativo al script
        ]
        
        for config_path in config_paths:
            try:
                if os.path.exists(config_path):
                    print(f"📄 Cargando configuración desde: {os.path.abspath(config_path)}")
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception as e:
                print(f"⚠️ Error leyendo {config_path}: {e}")
                continue
        
        # Si no se encontró ningún config.json válido
        print("❌ No se pudo encontrar config.json en ninguna ubicación")
        print("📍 Ubicaciones buscadas:")
        for path in config_paths:
            exists = "✅" if os.path.exists(path) else "❌"
            print(f"   {exists} {os.path.abspath(path)}")
        
        print("\n💡 Soluciones:")
        print("1. Asegúrate de que config.json existe en license_management/")
        print("2. Ejecuta el script desde license_management/: cd license_management && python secure_license_admin.py")
        print("3. O usa el launcher: python license_launcher.py")
        sys.exit(1)
    
    def init_firebase_admin(self):
        """Inicializa Firebase Admin SDK"""
        try:
            # Buscar archivo de credenciales
            credential_files = [
                "firebase-admin-key.json",
                "serviceAccountKey.json", 
                "firebase-adminsdk.json"
            ]
            
            credential_path = None
            for file in credential_files:
                if os.path.exists(file):
                    credential_path = file
                    break
            
            if not credential_path:
                print("📄 No se encontró archivo de credenciales Firebase Admin")
                print("💡 Coloca tu archivo de credenciales como 'firebase-admin-key.json'")
                return False
            
            # Verificar si ya está inicializado
            if len(firebase_admin._apps) > 0:
                self.app = firebase_admin.get_app()
            else:
                cred = credentials.Certificate(credential_path)
                self.app = firebase_admin.initialize_app(cred, {
                    'databaseURL': self.firebase_url
                })
            
            # Obtener referencia a la base de datos
            self.db_ref = db.reference()
            self.firebase_initialized = True
            return True
            
        except Exception as e:
            print(f"⚠️ Error inicializando Firebase Admin: {e}")
            return False
    
    def generate_machine_id(self, computer_name, username):
        """Genera un ID de máquina basado en los datos del cliente"""
        unique_string = f"{computer_name}_{username}_win32"
        machine_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]
        return machine_id
    
    def add_license_admin_sdk(self, computer_name, username, months=1):
        """Agrega licencia usando Firebase Admin SDK"""
        try:
            machine_id = self.generate_machine_id(computer_name, username)
            expiry_date = datetime.now() + timedelta(days=30 * months)
            
            # Verificar si ya existe una licencia para esta máquina
            license_ref = self.db_ref.child('licenses').child(machine_id)
            existing_license = license_ref.get()
            
            if existing_license:
                print(f"⚠️ Ya existe una licencia para esta máquina")
                print(f"   Máquina: {existing_license.get('computer_name', 'N/A')}")
                print(f"   Usuario: {existing_license.get('username', 'N/A')}")
                
                # Preguntar si quiere extender en lugar de sobrescribir
                print("💡 ¿Quieres extender la licencia existente en lugar de crear una nueva?")
                choice = input("   (s/N): ").strip().lower()
                if choice == 's':
                    return self.extend_license(machine_id, months)
            
            license_data = {
                "machine_id": machine_id,
                "computer_name": computer_name,
                "username": username,
                "active": True,  # Siempre activa para licencias nuevas
                "created_date": datetime.now().isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "months": months
            }
            
            # Escribir directamente en Firebase usando Admin SDK
            licenses_ref = self.db_ref.child('licenses')
            licenses_ref.child(machine_id).set(license_data)
            
            print(f"✅ Licencia creada exitosamente con Admin SDK!")
            print(f"   🆔 ID de Máquina: {machine_id}")
            print(f"   💻 Computer: {computer_name}")
            print(f"   👤 Usuario: {username}")
            print(f"   ⏰ Expira: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True, machine_id
            
        except Exception as e:
            print(f"❌ Error creando licencia con Admin SDK: {e}")
            return False, None
    
    def add_license_http(self, computer_name, username, months=1):
        """Agrega licencia usando HTTP directo (fallback)"""
        machine_id = self.generate_machine_id(computer_name, username)
        expiry_date = datetime.now() + timedelta(days=30 * months)
        
        license_data = {
            "machine_id": machine_id,
            "computer_name": computer_name,
            "username": username,
            "active": True,
            "created_date": datetime.now().isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "months": months
        }
        
        print("⚠️ Intentando con método HTTP directo...")
        print("📝 Si esto falla, necesitas cambiar las reglas temporalmente")
        
        try:
            url = f"{self.firebase_url}/licenses/{machine_id}.json"
            response = requests.put(url, json=license_data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Licencia creada exitosamente con HTTP!")
                print(f"   🆔 ID de Máquina: {machine_id}")
                print(f"   💻 Computer: {computer_name}")
                print(f"   👤 Usuario: {username}")
                print(f"   ⏰ Expira: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                return True, machine_id
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                self.show_manual_instructions(machine_id, license_data)
                return False, machine_id
                
        except Exception as e:
            print(f"❌ Error de conexión HTTP: {e}")
            self.show_manual_instructions(machine_id, license_data)
            return False, machine_id
    
    def add_license(self, computer_name, username, months=1):
        """Agrega una nueva licencia (método principal)"""
        if self.use_admin_sdk:
            return self.add_license_admin_sdk(computer_name, username, months)
        else:
            return self.add_license_http(computer_name, username, months)
    
    def show_manual_instructions(self, machine_id, license_data):
        """Muestra instrucciones para agregar manualmente"""
        print("\n" + "="*60)
        print("📋 AGREGAR MANUALMENTE EN FIREBASE CONSOLE")
        print("="*60)
        print(f"🔗 Ve a: {self.firebase_url.replace('.json', '')}")
        print("📍 Pestaña 'Datos' → Agregar 'licenses' si no existe")
        print(f"🔑 Clave: {machine_id}")
        print("📦 Valor (copia este JSON):")
        print("-" * 40)
        print(json.dumps(license_data, indent=2, ensure_ascii=False))
        print("-" * 40)
    
    def extend_license(self, machine_id, additional_months=1):
        """Extiende una licencia existente"""
        try:
            if self.use_admin_sdk:
                # Obtener licencia actual
                license_ref = self.db_ref.child('licenses').child(machine_id)
                license_data = license_ref.get()
                
                if license_data:
                    # Calcular nueva fecha
                    current_expiry = datetime.fromisoformat(license_data['expiry_date'])
                    new_expiry = current_expiry + timedelta(days=30 * additional_months)
                    
                    # Actualizar datos
                    license_data['expiry_date'] = new_expiry.isoformat()
                    license_data['months'] = license_data.get('months', 1) + additional_months
                    license_data['last_extended'] = datetime.now().isoformat()
                    
                    # 🔧 CORRECCIÓN: Reactivar la licencia si se extiende a una fecha futura válida
                    current_date = datetime.now()
                    if new_expiry > current_date:
                        license_data['active'] = True
                        print("🔄 Licencia reactivada automáticamente")
                    
                    license_ref.set(license_data)
                    
                    print(f"✅ Licencia extendida exitosamente!")
                    print(f"   Nueva fecha: {new_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Estado: {'🟢 ACTIVA' if license_data['active'] else '🔴 INACTIVA'}")
                    return True
                else:
                    print(f"❌ No se encontró la licencia: {machine_id}")
                    return False
            else:
                print("❌ Extensión requiere Firebase Admin SDK")
                return False
                
        except Exception as e:
            print(f"❌ Error extendiendo licencia: {e}")
            return False
    
    def deactivate_license(self, machine_id):
        """Desactiva una licencia específica"""
        try:
            if not self.use_admin_sdk:
                print("❌ Desactivar licencia requiere Firebase Admin SDK")
                return False
                
            # Obtener licencia actual
            license_ref = self.db_ref.child('licenses').child(machine_id)
            license_data = license_ref.get()
            
            if not license_data:
                print(f"❌ No se encontró la licencia: {machine_id}")
                return False
            
            # Verificar estado actual
            if not license_data.get('active', True):
                print(f"⚠️ La licencia ya está desactivada")
                return True
            
            # Desactivar licencia
            license_data['active'] = False
            license_data['deactivated_date'] = datetime.now().isoformat()
            
            license_ref.set(license_data)
            
            print(f"✅ Licencia desactivada exitosamente!")
            print(f"   ID: {machine_id}")
            print(f"   Fecha desactivación: {license_data['deactivated_date']}")
            return True
                
        except Exception as e:
            print(f"❌ Error desactivando licencia: {e}")
            return False
    
    def check_license(self, machine_id):
        """Verifica el estado de una licencia específica"""
        try:
            url = f"{self.firebase_url}/licenses/{machine_id}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200 and response.json():
                data = response.json()
                
                print(f"\n🔍 Información de Licencia: {machine_id}")
                print("-" * 50)
                print(f"💻 Computer: {data.get('computer_name', 'N/A')}")
                print(f"👤 Usuario: {data.get('username', 'N/A')}")
                print(f"✅ Activa: {'Sí' if data.get('active') else 'No'}")
                print(f"📅 Creada: {data.get('created_date', 'N/A')}")
                print(f"⏰ Expira: {data.get('expiry_date', 'N/A')}")
                print(f"📦 Meses: {data.get('months', 1)}")
                
                # Verificar vigencia
                try:
                    expiry = datetime.fromisoformat(data.get('expiry_date', ''))
                    if expiry < datetime.now():
                        print("🔴 ESTADO: EXPIRADA")
                    elif data.get('active'):
                        days_left = (expiry - datetime.now()).days
                        print(f"🟢 ESTADO: VIGENTE ({days_left} días restantes)")
                    else:
                        print("🟠 ESTADO: DESACTIVADA")
                except:
                    print("⚠️ Error verificando fecha")
                    
                return True
            else:
                print(f"❌ No se encontró la licencia con ID: {machine_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def list_licenses(self):
        """Lista todas las licencias"""
        try:
            url = f"{self.firebase_url}/licenses.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                licenses = response.json() or {}
                
                if not licenses:
                    print("📝 No hay licencias registradas")
                    return
                
                print(f"\n📋 Licencias registradas ({len(licenses)}):")
                print("=" * 80)
                
                for machine_id, data in licenses.items():
                    status = "🟢 ACTIVA" if data.get('active') else "🔴 INACTIVA"
                    try:
                        expiry = datetime.fromisoformat(data.get('expiry_date', ''))
                        expired = "⚠️ EXPIRADA" if expiry < datetime.now() else "✅ VIGENTE"
                        expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        expired = "❓ FECHA INVÁLIDA"
                        expiry_str = data.get('expiry_date', 'N/A')
                    
                    print(f"🆔 ID: {machine_id}")
                    print(f"   💻 Computer: {data.get('computer_name', 'N/A')}")
                    print(f"   👤 Usuario: {data.get('username', 'N/A')}")
                    print(f"   📊 Estado: {status} | {expired}")
                    print(f"   ⏰ Expira: {expiry_str}")
                    print(f"   📅 Meses: {data.get('months', 1)}")
                    print("-" * 40)
                    
        except Exception as e:
            print(f"❌ Error listando licencias: {e}")
    
    def reactivate_license(self, machine_id):
        """Reactiva una licencia desactivada si aún está vigente"""
        try:
            if not self.use_admin_sdk:
                print("❌ Reactivar licencia requiere Firebase Admin SDK")
                return False
                
            # Obtener licencia actual
            license_ref = self.db_ref.child('licenses').child(machine_id)
            license_data = license_ref.get()
            
            if not license_data:
                print(f"❌ No se encontró la licencia: {machine_id}")
                return False
            
            # Verificar si la licencia está vigente por fecha
            try:
                expiry_date = datetime.fromisoformat(license_data['expiry_date'])
                current_date = datetime.now()
                
                if current_date <= expiry_date:
                    # La licencia está vigente, se puede reactivar
                    license_data['active'] = True
                    license_data['reactivated_date'] = current_date.isoformat()
                    
                    license_ref.set(license_data)
                    
                    days_left = (expiry_date - current_date).days
                    print(f"✅ Licencia reactivada exitosamente!")
                    print(f"   Expira: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Días restantes: {days_left}")
                    return True
                else:
                    print(f"❌ No se puede reactivar - licencia expirada")
                    print(f"   Expiró: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print("💡 Usa 'Extender licencia' para agregar más tiempo")
                    return False
                    
            except Exception as e:
                print(f"❌ Error verificando fecha de expiración: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error reactivando licencia: {e}")
            return False
    
    def show_setup_instructions(self):
        """Muestra instrucciones de configuración"""
        print("\n📖 CONFIGURACIÓN FIREBASE ADMIN SDK")
        print("=" * 50)
        print("1. Ve a Firebase Console → Tu proyecto")
        print("2. Configuración (⚙️) → Cuentas de servicio")
        print("3. 'Generar nueva clave privada' → Generar clave")
        print("4. Descarga el archivo JSON")
        print("5. Guárdalo como 'firebase-admin-key.json' en este directorio")
        print("6. Ejecuta este script nuevamente")
        print()
        print("🔒 IMPORTANTE: No subas este archivo a Git!")

def main():
    admin = SecureLicenseAdmin()
    
    while True:
        print("\n" + "="*70)
        print("🔐 ADMINISTRADOR SEGURO DE LICENCIAS")
        method = "🔑 Admin SDK" if admin.use_admin_sdk else "🌐 HTTP"
        print(f"    Método activo: {method}")
        print("="*70)
        print("1. 📝 Agregar nueva licencia")
        print("2. 🔍 Verificar licencia específica")
        print("3. 📋 Listar todas las licencias")
        print("4. ⏰ Extender licencia")
        print("5. ❌ Desactivar licencia")
        print("6. ✅ Reactivar licencia")
        print("7. 💡 Generar ID de máquina")
        print("8. 📖 Configurar Firebase Admin SDK")
        print("9. 🚪 Salir")
        
        try:
            choice = input("\n➡️ Seleccione una opción (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break
        
        if choice == '1':
            print("\n📝 AGREGAR NUEVA LICENCIA")
            computer_name = input("Nombre del computador: ").strip()
            username = input("Nombre de usuario: ").strip()
            
            try:
                months = int(input("Meses de licencia (por defecto 1): ") or "1")
            except ValueError:
                months = 1
            
            if computer_name and username:
                admin.add_license(computer_name, username, months)
            else:
                print("❌ Debe proporcionar computer name y username")
        
        elif choice == '2':
            print("\n🔍 VERIFICAR LICENCIA")
            machine_id = input("ID de máquina: ").strip()
            if machine_id:
                admin.check_license(machine_id)
            else:
                print("❌ Debe proporcionar un ID de máquina")
        
        elif choice == '3':
            admin.list_licenses()
        
        elif choice == '4':
            if not admin.use_admin_sdk:
                print("❌ Extender licencias requiere Firebase Admin SDK")
                print("💡 Configura Admin SDK primero (opción 6)")
            else:
                print("\n⏰ EXTENDER LICENCIA")
                machine_id = input("ID de máquina: ").strip()
                try:
                    months = int(input("Meses adicionales (por defecto 1): ") or "1")
                except ValueError:
                    months = 1
                
                if machine_id:
                    admin.extend_license(machine_id, months)
                else:
                    print("❌ Debe proporcionar un ID de máquina")
        
        elif choice == '5':
            if not admin.use_admin_sdk:
                print("❌ Desactivar licencias requiere Firebase Admin SDK")
                print("💡 Configura Admin SDK primero (opción 8)")
            else:
                print("\n❌ DESACTIVAR LICENCIA")
                machine_id = input("ID de máquina a desactivar: ").strip()
                
                if machine_id:
                    admin.deactivate_license(machine_id)
                else:
                    print("❌ Debe proporcionar un ID de máquina")
        
        elif choice == '6':
            if not admin.use_admin_sdk:
                print("❌ Reactivar licencias requiere Firebase Admin SDK")
                print("💡 Configura Admin SDK primero (opción 8)")
            else:
                print("\n✅ REACTIVAR LICENCIA")
                machine_id = input("ID de máquina a reactivar: ").strip()
                
                if machine_id:
                    admin.reactivate_license(machine_id)
                else:
                    print("❌ Debe proporcionar un ID de máquina")
        
        elif choice == '7':
            print("\n💡 GENERAR ID DE MÁQUINA")
            computer_name = input("Nombre del computador: ").strip()
            username = input("Nombre de usuario: ").strip()
            
            if computer_name and username:
                machine_id = admin.generate_machine_id(computer_name, username)
                print(f"🔑 ID de Máquina: {machine_id}")
            else:
                print("❌ Debe proporcionar computer name y username")
        
        elif choice == '8':
            admin.show_setup_instructions()
        
        elif choice == '9':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")
        
        input("\n⏎ Presione Enter para continuar...")

if __name__ == "__main__":
    main()