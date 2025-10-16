import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import os
import logging
from PIL import Image, ImageTk

class KioscoPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema POS - Kiosco Argentina")
        self.root.geometry("1200x700")
        self.root.configure(bg="#FAF2E3")
        #self.root.iconbitmap(os.path.join("img", "kiosco.ico"))
        
        base_path = os.path.dirname(__file__)
        self.root.iconbitmap(os.path.join(base_path, "img", "kiosco.ico"))
        # Usuario actual
        self.usuario_actual = None
        
        # Inicializar base de datos
        self.init_database()
        
        # Carrito de compras
        self.carrito = []
        
        # Mostrar login
        self.mostrar_login()
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    def init_database(self):
        """Inicializa la base de datos y crea las tablas"""
        self.conn = sqlite3.connect('kiosco.db')
        self.cursor = self.conn.cursor()
        
        # Tabla de usuarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        ''')
        
        # Tabla de productos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                costo REAL NOT NULL,
                stock INTEGER NOT NULL,
                categoria TEXT,
                codigo_barras TEXT
            )
        ''')
        
        # Tabla de ventas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                usuario TEXT NOT NULL,
                metodo_pago TEXT NOT NULL,
                total REAL NOT NULL,
                costo_total REAL NOT NULL,
                turno TEXT NOT NULL
            )
        ''')
        
        # Tabla de items de venta
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                costo_unitario REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas (id)
            )
        ''')
        
        # Insertar usuario admin por defecto si no existe
        self.cursor.execute("SELECT * FROM usuarios WHERE nombre = 'Administrador'")
        if not self.cursor.fetchone():
            self.cursor.execute('''
                INSERT INTO usuarios (nombre, password, rol) 
                VALUES ('Administrador', 'admin123', 'admin')
            ''')
        
        # Insertar productos de ejemplo si no existen
        self.cursor.execute("SELECT COUNT(*) FROM productos")
        if self.cursor.fetchone()[0] == 0:
            productos_ejemplo = [
                ('Coca Cola 500ml', 800, 500, 50, 'Bebidas', '7790895602764'),
                ('Alfajor Milka', 600, 400, 30, 'Golosinas', '7622210805164'),
                ('Papas Lays', 950, 650, 25, 'Snacks', '7790310510186')
            ]
            self.cursor.executemany('''
                INSERT INTO productos (nombre, precio, costo, stock, categoria, codigo_barras)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', productos_ejemplo)
        
        self.conn.commit()
    
    def mostrar_login(self):
        """Muestra la ventana de login"""
        self.login_frame = tk.Frame(self.root, bg='#FAF2E3')
        self.login_frame.place(relx=0.5, rely=0.5, anchor='center')

        try:
            ruta_logo = os.path.join("img", "kioscoimg.png")
            imagen_logo = Image.open(ruta_logo)
            imagen_logo = imagen_logo.resize((350, 350))  # tamaño ajustable
            self.logo_img = ImageTk.PhotoImage(imagen_logo)
            tk.Label(
                self.login_frame,
                image=self.logo_img,
                bg='#FAF2E3'
            ).pack(pady=5)
        except Exception as e:
            print("No se pudo cargar el logo:", e)

        # Logo/Título
        # tk.Label(
        #     self.login_frame, 
        #     text="Sistema POS - Kiosco", 
        #     font=('Arial', 24, 'bold'),
        #     bg='#FAF2E3',
        #     fg='#2563eb'
        # ).pack(pady=20)
        
        # Usuario
        tk.Label(
            self.login_frame, 
            text="Usuario:", 
            font=('Arial', 12),
            bg='#FAF2E3'
        ).pack(pady=5)
        
        self.entry_usuario = tk.Entry(self.login_frame, font=('Arial', 12), width=25)
        self.entry_usuario.pack(pady=5)
        
        # Contraseña
        tk.Label(
            self.login_frame, 
            text="Contraseña:", 
            font=('Arial', 12),
            bg='#FAF2E3'
        ).pack(pady=5)
        
        self.entry_password = tk.Entry(self.login_frame, font=('Arial', 12), width=25, show='*')
        self.entry_password.pack(pady=5)
        self.entry_password.bind('<Return>', lambda e: self.login())
        
        # Botón login
        tk.Button(
            self.login_frame,
            text="Iniciar Sesión",
            font=('Arial', 12, 'bold'),
            bg='#2563eb',
            fg='white',
            command=self.login,
            width=20,
            cursor='hand2'
        ).pack(pady=20)
        
        # Texto ayuda
        # tk.Label(
        #     self.login_frame,
        #     text="Usuario demo: Administrador / admin123",
        #     font=('Arial', 9),
        #     bg='#FAF2E3',
        #     fg='gray'
        # ).pack()
    
    def login(self):
        """Procesa el login del usuario"""
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        
        self.cursor.execute(
            "SELECT * FROM usuarios WHERE nombre = ? AND password = ?",
            (usuario, password)
        )
        user = self.cursor.fetchone()
        
        if user:
            self.usuario_actual = {
                'id': user[0],
                'nombre': user[1],
                'rol': user[3]
            }
            self.login_frame.destroy()
            self.mostrar_interfaz_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def mostrar_interfaz_principal(self):
        """Muestra la interfaz principal del sistema"""
        # Header
        header = tk.Frame(self.root, bg='#D94A2B', height=60)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="Sistema POS - Kiosco",
            font=('Arial', 18, 'bold'),
            bg='#D94A2B',
            fg='white'
        ).pack(side='left', padx=20, pady=10)
        
        tk.Label(
            header,
            text=f"👤 {self.usuario_actual['nombre']}",
            font=('Arial', 11),
            bg='#D94A2B',
            fg='white'
        ).pack(side='right', padx=10)
        
        tk.Button(
            header,
            text="Cerrar Sesión",
            font=('Arial', 10),
            bg="#d10909",
            fg='white',
            command=self.logout,
            cursor='hand2'
        ).pack(side='right', padx=10)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.notebook.style = ttk.Style()
        self.notebook.style.configure('TNotebook', background='#FAF2E3')
        
        # Crear pestañas
        self.turno_actual = None
        if self.usuario_actual['rol'] == 'empleado':
            self.seleccionar_turno()
        else:
            self.crear_pestaña_venta()
            self.crear_pestaña_usuarios()
            self.crear_pestaña_productos()
            self.crear_pestaña_reportes()
    
    def crear_pestaña_venta(self):
        """Crea la pestaña de punto de venta"""
        frame_venta = tk.Frame(self.notebook, bg='#FAF2E3')
        self.notebook.add(frame_venta, text='🛒 Punto de Venta')

        # Frame izquierdo - Búsqueda de productos
        frame_izq = tk.Frame(frame_venta, bg='#FAF2E3')
        frame_izq.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            frame_izq,
            text="Buscar Productos",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=5)
        
        # Búsqueda por nombre
        tk.Label(frame_izq, text="Buscar por nombre o categoría:", bg='#FAF2E3').pack(pady=5)
        self.entry_buscar = tk.Entry(frame_izq, font=('Arial', 11), width=40)
        self.entry_buscar.pack(pady=5)
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.actualizar_lista_productos())
        
        # Búsqueda por código de barras
        tk.Label(frame_izq, text="Código de barras (presiona Enter):", bg='#FAF2E3').pack(pady=5)
        self.entry_barcode = tk.Entry(frame_izq, font=('Arial', 11), width=40)
        self.entry_barcode.pack(pady=5)
        self.entry_barcode.bind('<Return>', self.buscar_por_barcode)
        
        # Lista de productos
        frame_lista = tk.Frame(frame_izq, bg='#FAF2E3')
        frame_lista.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        self.lista_productos = tk.Listbox(
            frame_lista,
            font=('Arial', 10),
            yscrollcommand=scrollbar.set,
            height=20
        )
        self.lista_productos.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.lista_productos.yview)
        
        self.lista_productos.bind('<Double-Button-1>', lambda e: self.agregar_al_carrito())
        
        tk.Button(
            frame_izq,
            text="Agregar al Carrito",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            command=self.agregar_al_carrito,
            cursor='hand2'
        ).pack(pady=10)
        
        # Frame derecho - Carrito
        frame_der = tk.Frame(frame_venta, bg='#FAF2E3', width=400)
        frame_der.pack(side='right', fill='both', padx=10, pady=10)
        frame_der.pack_propagate(False)
        
        tk.Label(
            frame_der,
            text="Carrito de Venta",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=5)
        
        # Lista del carrito
        frame_carrito = tk.Frame(frame_der, bg='#FAF2E3')
        frame_carrito.pack(fill='both', expand=True, pady=10)
        
        scrollbar_carrito = tk.Scrollbar(frame_carrito)
        scrollbar_carrito.pack(side='right', fill='y')
        
        self.lista_carrito = tk.Listbox(
            frame_carrito,
            font=('Arial', 10),
            yscrollcommand=scrollbar_carrito.set
        )
        self.lista_carrito.pack(side='left', fill='both', expand=True)
        scrollbar_carrito.config(command=self.lista_carrito.yview)
        
        # Botones de carrito
        frame_botones = tk.Frame(frame_der, bg='#FAF2E3')
        frame_botones.pack(fill='x', pady=5)
        
        tk.Button(
            frame_botones,
            text="Eliminar",
            font=('Arial', 10),
            bg='#dc2626',
            fg='white',
            command=self.eliminar_del_carrito,
            cursor='hand2'
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botones,
            text="Eliminar Unidad",
            font=('Arial', 10),
            bg='#dc2626',
            fg='white',
            command=self.eliminar_uno_del_carrito,
            cursor='hand2'
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botones,
            text="Vaciar Carrito",
            font=('Arial', 10),
            bg='#ef4444',
            fg='white',
            command=self.vaciar_carrito,
            cursor='hand2'
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botones,
            text="Restar Stock",
            font=('Arial', 10),
            bg='#f59e0b',
            fg='white',
            command=self.restar_stock_interno,
            cursor='hand2'
        ).pack(side='left', padx=5)

        # Total
        self.label_total = tk.Label(
            frame_der,
            text="TOTAL: $0",
            font=('Arial', 18, 'bold'),
            bg='#FAF2E3',
            fg='#2563eb'
        )
        self.label_total.pack(pady=10)
        
        # Métodos de pago
        tk.Label(
            frame_der,
            text="Método de Pago:",
            font=('Arial', 11, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=5)
        
        metodos = ['Efectivo', 'Transferencia', 'Débito', 'Crédito']
        for metodo in metodos:
            tk.Button(
                frame_der,
                text=f"Cobrar - {metodo}",
                font=('Arial', 11, 'bold'),
                bg='#16a34a',
                fg='white',
                command=lambda m=metodo: self.finalizar_venta(m),
                cursor='hand2'
            ).pack(fill='x', pady=2)
        
        # Cargar productos
        self.actualizar_lista_productos()
    
    def crear_pestaña_productos(self):
        """Crea la pestaña de gestión de productos"""
        frame_productos = tk.Frame(self.notebook, bg='#FAF2E3')
        self.notebook.add(frame_productos, text='📦 Productos')
        
        # Frame izquierdo - Formulario
        frame_form = tk.Frame(frame_productos, bg='#FAF2E3', width=350)
        frame_form.pack(side='left', fill='y', padx=10, pady=10)
        frame_form.pack_propagate(False)
        
        tk.Label(
            frame_form,
            text="Agregar/Editar Producto",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=10)
        
        # Campos del formulario
        self.producto_id = None
        
        tk.Label(frame_form, text="Nombre:", bg='#FAF2E3').pack(pady=2)
        self.prod_nombre = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.prod_nombre.pack(pady=2)
        
        tk.Label(frame_form, text="Precio de Venta ($):", bg='#FAF2E3').pack(pady=2)
        self.prod_precio = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.prod_precio.pack(pady=2)
        
        tk.Label(frame_form, text="Costo ($):", bg='#FAF2E3').pack(pady=2)
        self.prod_costo = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.prod_costo.pack(pady=2)
        
        tk.Label(frame_form, text="Stock:", bg='#FAF2E3').pack(pady=2)
        self.prod_stock = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.prod_stock.pack(pady=2)
        
        tk.Label(frame_form, text="Categoría:", bg='#FAF2E3').pack(pady=2)
        self.prod_categoria = ttk.Combobox(
            frame_form,
            font=('Arial', 11),
            width=28,
            values=['Bebidas', 'Golosinas', 'Snacks', 'Cigarrillos', 'Lácteos', 'Panificados', 'Limpieza', 'Otros']
        )
        self.prod_categoria.pack(pady=2)
        
        tk.Label(frame_form, text="Código de Barras:", bg='#FAF2E3').pack(pady=2)
        self.prod_barcode = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.prod_barcode.pack(pady=2)
        
        # Botones
        frame_botones_prod = tk.Frame(frame_form, bg='#FAF2E3')
        frame_botones_prod.pack(pady=20)
        
        tk.Button(
            frame_botones_prod,
            text="Guardar",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            command=self.guardar_producto,
            width=12,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_botones_prod,
            text="Limpiar",
            font=('Arial', 11),
            bg='#6b7280',
            fg='white',
            command=self.limpiar_formulario_producto,
            width=12,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        # Frame derecho - Lista de productos
        frame_lista_prod = tk.Frame(frame_productos, bg='#FAF2E3')
        frame_lista_prod.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            frame_lista_prod,
            text="Inventario de Productos",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=10)
        
        # Tabla de productos
        frame_tabla = tk.Frame(frame_lista_prod, bg='#FAF2E3')
        frame_tabla.pack(fill='both', expand=True)
        
        scrollbar_tabla = tk.Scrollbar(frame_tabla)
        scrollbar_tabla.pack(side='right', fill='y')
        
        self.tabla_productos = ttk.Treeview(
            frame_tabla,
            columns=('ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Categoría', 'Código'),
            show='headings',
            yscrollcommand=scrollbar_tabla.set
        )
        
        self.tabla_productos.heading('ID', text='ID', command=lambda: self.ordenar_tabla_productos('ID'))
        self.tabla_productos.heading('Nombre', text='Nombre', command=lambda: self.ordenar_tabla_productos('Nombre'))
        self.tabla_productos.heading('Precio', text='Precio', command=lambda: self.ordenar_tabla_productos('Precio'))
        self.tabla_productos.heading('Costo', text='Costo', command=lambda: self.ordenar_tabla_productos('Costo'))
        self.tabla_productos.heading('Stock', text='Stock', command=lambda: self.ordenar_tabla_productos('Stock'))
        self.tabla_productos.heading('Categoría', text='Categoría', command=lambda: self.ordenar_tabla_productos('Categoría'))
        self.tabla_productos.heading('Código', text='Código Barras', command=lambda: self.ordenar_tabla_productos('Código'))
            
        self.tabla_productos.column('ID', width=50)
        self.tabla_productos.column('Nombre', width=200)
        self.tabla_productos.column('Precio', width=80)
        self.tabla_productos.column('Costo', width=80)
        self.tabla_productos.column('Stock', width=60)
        self.tabla_productos.column('Categoría', width=100)
        self.tabla_productos.column('Código', width=120)
        
        self.tabla_productos.pack(side='left', fill='both', expand=True)
        scrollbar_tabla.config(command=self.tabla_productos.yview)
        
        self.tabla_productos.bind('<Double-Button-1>', self.editar_producto)
        
        # Botones de acción
        frame_acciones = tk.Frame(frame_lista_prod, bg='#FAF2E3')
        frame_acciones.pack(fill='x', pady=10)
        
        tk.Button(
            frame_acciones,
            text="Editar Seleccionado",
            font=('Arial', 10),
            bg='#ea580c',
            fg='white',
            command=self.editar_producto,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_acciones,
            text="Eliminar Seleccionado",
            font=('Arial', 10),
            bg='#dc2626',
            fg='white',
            command=self.eliminar_producto,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_acciones,
            text="Exportar a Excel",
            font=('Arial', 10),
            bg='#16a34a',
            fg='white',
            command=self.exportar_productos_excel,
            cursor='hand2'
        ).pack(side='right', padx=5)
        tk.Button(
        frame_acciones,
        text="Importar Productos",
        font=('Arial', 10),
        bg='#0ea5e9',
        fg='white',
        command=self.importar_productos,
        cursor='hand2'
        ).pack(side='right', padx=5)
        # Cargar productos
        self.actualizar_tabla_productos()
    
    def crear_pestaña_reportes(self):
        """Crea la pestaña de reportes"""
        frame_reportes = tk.Frame(self.notebook, bg='#FAF2E3')
        self.notebook.add(frame_reportes, text='📊 Reportes')
        
        # Frame superior - Resumen
        frame_resumen = tk.Frame(frame_reportes, bg='#FAF2E3')
        frame_resumen.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            frame_resumen,
            text="Resumen de Ventas",
            font=('Arial', 16, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=10)
        
        # Tarjetas de resumen
        frame_tarjetas = tk.Frame(frame_resumen, bg='#FAF2E3')
        frame_tarjetas.pack(fill='x', pady=10)
        
        # Calcular estadísticas
        # self.actualizar_estadisticas()
        
        # Hoy
        self.card_hoy = tk.Frame(frame_tarjetas, bg='#dbeafe', relief='raised', bd=2)
        self.card_hoy.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(self.card_hoy, text="Ventas Hoy", font=('Arial', 12, 'bold'), bg='#dbeafe').pack(pady=5)
        self.label_hoy_total = tk.Label(self.card_hoy, text="$0", font=('Arial', 18, 'bold'), bg='#dbeafe', fg='#2563eb')
        self.label_hoy_total.pack()
        self.label_hoy_ventas = tk.Label(self.card_hoy, text="0 ventas", font=('Arial', 10), bg='#dbeafe')
        self.label_hoy_ventas.pack()
        self.label_hoy_ganancia = tk.Label(self.card_hoy, text="Ganancia: $0", font=('Arial', 11, 'bold'), bg='#dbeafe', fg='#16a34a')
        self.label_hoy_ganancia.pack(pady=5)
        
        # Mes
        self.card_mes = tk.Frame(frame_tarjetas, bg='#e0e7ff', relief='raised', bd=2)
        self.card_mes.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(self.card_mes, text="Ventas Este Mes", font=('Arial', 12, 'bold'), bg='#e0e7ff').pack(pady=5)
        self.label_mes_total = tk.Label(self.card_mes, text="$0", font=('Arial', 18, 'bold'), bg='#e0e7ff', fg='#4f46e5')
        self.label_mes_total.pack()
        self.label_mes_ventas = tk.Label(self.card_mes, text="0 ventas", font=('Arial', 10), bg='#e0e7ff')
        self.label_mes_ventas.pack()
        self.label_mes_ganancia = tk.Label(self.card_mes, text="Ganancia: $0", font=('Arial', 11, 'bold'), bg='#e0e7ff', fg='#16a34a')
        self.label_mes_ganancia.pack(pady=5)
        
        # Año
        self.card_anio = tk.Frame(frame_tarjetas, bg='#fce7f3', relief='raised', bd=2)
        self.card_anio.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(self.card_anio, text="Ventas Este Año", font=('Arial', 12, 'bold'), bg='#fce7f3').pack(pady=5)
        self.label_anio_total = tk.Label(self.card_anio, text="$0", font=('Arial', 18, 'bold'), bg='#fce7f3', fg='#ec4899')
        self.label_anio_total.pack()
        self.label_anio_ventas = tk.Label(self.card_anio, text="0 ventas", font=('Arial', 10), bg='#fce7f3')
        self.label_anio_ventas.pack()
        self.label_anio_ganancia = tk.Label(self.card_anio, text="Ganancia: $0", font=('Arial', 11, 'bold'), bg='#fce7f3', fg='#16a34a')
        self.label_anio_ganancia.pack(pady=5)
        
        # Frame tabla de ventas
        tk.Label(
            frame_reportes,
            text="Historial de Ventas",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=10)
        
        frame_tabla_ventas = tk.Frame(frame_reportes, bg='#FAF2E3')
        frame_tabla_ventas.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar_ventas = tk.Scrollbar(frame_tabla_ventas)
        scrollbar_ventas.pack(side='right', fill='y')
        
        self.tabla_ventas = ttk.Treeview(
            frame_tabla_ventas,
            columns=('ID', 'Fecha', 'Usuario', 'Método', 'Total', 'Ganancia', 'Turno'),
            show='headings',
            yscrollcommand=scrollbar_ventas.set
        )
        
        self.tabla_ventas.heading('ID', text='ID')
        self.tabla_ventas.heading('Fecha', text='Fecha')
        self.tabla_ventas.heading('Usuario', text='Usuario')
        self.tabla_ventas.heading('Método', text='Método Pago')
        self.tabla_ventas.heading('Total', text='Total')
        self.tabla_ventas.heading('Ganancia', text='Ganancia')
        self.tabla_ventas.heading('Turno', text='Turno')

        self.tabla_ventas.column('ID', width=50)
        self.tabla_ventas.column('Fecha', width=150)
        self.tabla_ventas.column('Usuario', width=150)
        self.tabla_ventas.column('Método', width=120)
        self.tabla_ventas.column('Total', width=100)
        self.tabla_ventas.column('Ganancia', width=100)
        self.tabla_ventas.column('Turno', width=80)
        
        self.tabla_ventas.pack(side='left', fill='both', expand=True)
        scrollbar_ventas.config(command=self.tabla_ventas.yview)
        
        # Botones de exportación
        frame_exportar = tk.Frame(frame_reportes, bg='#FAF2E3')
        frame_exportar.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            frame_exportar,
            text="Exportar Todo a Excel",
            font=('Arial', 11, 'bold'),
            bg='#16a34a',
            fg='white',
            command=self.exportar_todo_excel,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_exportar,
            text="Actualizar Reportes",
            font=('Arial', 11),
            bg='#2563eb',
            fg='white',
            command=self.actualizar_estadisticas,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Label(
            frame_exportar,
            text="Fecha (YYYY-MM-DD):",
            font=('Arial', 10),
            bg='#FAF2E3'
        ).pack(side='left', padx=5)

        self.entry_fecha_reporte = tk.Entry(frame_exportar, font=('Arial', 10), width=12)
        self.entry_fecha_reporte.pack(side='left', padx=5)

        tk.Button(
            frame_exportar,
            text="Exportar Ventas por Día a Excel",
            font=('Arial', 10, 'bold'),
            bg='#0ea5e9',
            fg='white',
            command=self.exportar_ventas_dia_excel,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Label(
            frame_exportar,
            text="Turno:",
            font=('Arial', 10),
            bg='#FAF2E3'
        ).pack(side='left', padx=5)
        self.combo_turno_reporte = ttk.Combobox(frame_exportar, values=['', 'MAÑANA', 'TARDE', 'NOCHE'], width=10, state='readonly')
        self.combo_turno_reporte.pack(side='left', padx=5)
        self.combo_turno_reporte.set('')
        tk.Button(
            frame_exportar,
            text="Filtrar",
            font=('Arial', 10),
            bg='#2563eb',
            fg='white',
            command=self.actualizar_tabla_ventas,
            cursor='hand2'
        ).pack(side='left', padx=5)
                
        # Calcular estadísticas
        self.actualizar_estadisticas()
        # Cargar ventas
        self.actualizar_tabla_ventas()
    
    def crear_pestaña_usuarios(self):
        """Crea la pestaña de gestión de usuarios (solo admin)"""
        frame_usuarios = tk.Frame(self.notebook, bg='#FAF2E3')
        self.notebook.add(frame_usuarios, text='👥 Usuarios')
        
        # Frame izquierdo - Formulario
        frame_form_user = tk.Frame(frame_usuarios, bg='#FAF2E3', width=350)
        frame_form_user.pack(side='left', fill='y', padx=10, pady=10)
        frame_form_user.pack_propagate(False)
        
        tk.Label(
            frame_form_user,
            text="Agregar Usuario",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=10)
        
        tk.Label(frame_form_user, text="Nombre de Usuario:", bg='#FAF2E3').pack(pady=5)
        self.user_nombre = tk.Entry(frame_form_user, font=('Arial', 11), width=30)
        self.user_nombre.pack(pady=5)
        
        tk.Label(frame_form_user, text="Contraseña:", bg='#FAF2E3').pack(pady=5)
        self.user_password = tk.Entry(frame_form_user, font=('Arial', 11), width=30, show='*')
        self.user_password.pack(pady=5)
        
        tk.Label(frame_form_user, text="Rol:", bg='#FAF2E3').pack(pady=5)
        self.user_rol = ttk.Combobox(
            frame_form_user,
            font=('Arial', 11),
            width=28,
            values=['empleado', 'admin'],
            state='readonly'
        )
        self.user_rol.set('empleado')
        self.user_rol.pack(pady=5)
        
        tk.Button(
            frame_form_user,
            text="Agregar Usuario",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            command=self.agregar_usuario,
            cursor='hand2'
        ).pack(pady=20)
        
        # Frame derecho - Lista de usuarios
        frame_lista_users = tk.Frame(frame_usuarios, bg='#FAF2E3')
        frame_lista_users.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            frame_lista_users,
            text="Lista de Usuarios",
            font=('Arial', 14, 'bold'),
            bg='#FAF2E3'
        ).pack(pady=10)
        
        frame_tabla_users = tk.Frame(frame_lista_users, bg='#FAF2E3')
        frame_tabla_users.pack(fill='both', expand=True)
        
        scrollbar_users = tk.Scrollbar(frame_tabla_users)
        scrollbar_users.pack(side='right', fill='y')
        
        self.tabla_usuarios = ttk.Treeview(
            frame_tabla_users,
            columns=('ID', 'Nombre', 'Contraseña', 'Rol'),
            show='headings',
            yscrollcommand=scrollbar_users.set
        )
        
        self.tabla_usuarios.heading('ID', text='ID')
        self.tabla_usuarios.heading('Nombre', text='Nombre')
        self.tabla_usuarios.heading('Contraseña', text='Contraseña')
        self.tabla_usuarios.heading('Rol', text='Rol')
        
        self.tabla_usuarios.column('ID', width=80)
        self.tabla_usuarios.column('Nombre', width=250)
        self.tabla_usuarios.column('Contraseña', width=200)
        self.tabla_usuarios.column('Rol', width=150)
        
        self.tabla_usuarios.pack(side='left', fill='both', expand=True)
        scrollbar_users.config(command=self.tabla_usuarios.yview)
        
        tk.Button(
            frame_lista_users,
            text="Eliminar Usuario Seleccionado",
            font=('Arial', 10),
            bg='#dc2626',
            fg='white',
            command=self.eliminar_usuario,
            cursor='hand2'
        ).pack(pady=10)
        tk.Button(
            frame_lista_users,
            text="Editar Usuario Seleccionado",
            font=('Arial', 10),
            bg='#ea580c',
            fg='white',
            command=self.editar_usuario,
            cursor='hand2'
        ).pack(pady=5) 
        self.actualizar_tabla_usuarios()
    
    # ===== MÉTODOS DE VENTA =====
    
    def actualizar_lista_productos(self):
        """Actualiza la lista de productos en el punto de venta"""
        busqueda = self.entry_buscar.get().lower()
        self.lista_productos.delete(0, tk.END)
        
        if busqueda:
            self.cursor.execute('''
                SELECT * FROM productos 
                WHERE LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ?
                ORDER BY nombre
            ''', (f'%{busqueda}%', f'%{busqueda}%'))
        else:
            self.cursor.execute('SELECT * FROM productos ORDER BY nombre')
        
        productos = self.cursor.fetchall()
        for producto in productos:
            texto = f"{producto[1]} - ${producto[2]} - Stock: {producto[4]} - {producto[5]}"
            self.lista_productos.insert(tk.END, texto)
            self.lista_productos.itemconfig(tk.END, {'bg': '#fee2e2' if producto[4] <= 5 else 'white'})
    
    def buscar_por_barcode(self, event):
        """Busca y agrega producto por código de barras"""
        codigo = self.entry_barcode.get()
        if not codigo:
            return
        
        self.cursor.execute('SELECT * FROM productos WHERE codigo_barras = ?', (codigo,))
        producto = self.cursor.fetchone()
        
        if producto:
            if producto[4] <= 0:
                messagebox.showwarning("Sin Stock", "No hay stock disponible de este producto")
                return
            
            # Verificar si ya está en el carrito
            for item in self.carrito:
                if item['id'] == producto[0]:
                    if item['cantidad'] >= producto[4]:
                        messagebox.showwarning("Stock Insuficiente", "No hay más stock disponible")
                        return
                    item['cantidad'] += 1
                    self.actualizar_carrito_display()
                    self.entry_barcode.delete(0, tk.END)
                    return
            
            # Agregar nuevo item
            self.carrito.append({
                'id': producto[0],
                'nombre': producto[1],
                'precio': producto[2],
                'costo': producto[3],
                'cantidad': 1,
                'stock_disponible': producto[4]
            })
            self.actualizar_carrito_display()
            self.entry_barcode.delete(0, tk.END)
        else:
            messagebox.showerror("No encontrado", "Producto no encontrado con ese código de barras")
    
    def agregar_al_carrito(self):
        """Agrega el producto seleccionado al carrito"""
        seleccion = self.lista_productos.curselection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un producto")
            return
        
        # Obtener el producto de la base de datos
        busqueda = self.entry_buscar.get().lower()
        if busqueda:
            self.cursor.execute('''
                SELECT * FROM productos 
                WHERE LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ?
                ORDER BY nombre
            ''', (f'%{busqueda}%', f'%{busqueda}%'))
        else:
            self.cursor.execute('SELECT * FROM productos ORDER BY nombre')
        
        productos = self.cursor.fetchall()
        producto = productos[seleccion[0]]
        
        if producto[4] <= 0:
            messagebox.showwarning("Sin Stock", "No hay stock disponible de este producto")
            return
        
        # Verificar si ya está en el carrito
        for item in self.carrito:
            if item['id'] == producto[0]:
                if item['cantidad'] >= producto[4]:
                    messagebox.showwarning("Stock Insuficiente", "No hay más stock disponible")
                    return
                item['cantidad'] += 1
                self.actualizar_carrito_display()
                return
        
        # Agregar nuevo item
        self.carrito.append({
            'id': producto[0],
            'nombre': producto[1],
            'precio': producto[2],
            'costo': producto[3],
            'cantidad': 1,
            'stock_disponible': producto[4]
        })
        self.actualizar_carrito_display()
    
    def actualizar_carrito_display(self):
        """Actualiza la visualización del carrito"""
        self.lista_carrito.delete(0, tk.END)
        total = 0
        
        for item in self.carrito:
            subtotal = item['precio'] * item['cantidad']
            total += subtotal
            texto = f"{item['nombre']} x{item['cantidad']} - ${subtotal}"
            self.lista_carrito.insert(tk.END, texto)
        
        self.label_total.config(text=f"TOTAL: ${total}")
    
    def eliminar_del_carrito(self):
        """Elimina el item seleccionado del carrito"""
        seleccion = self.lista_carrito.curselection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un item del carrito")
            return
        print(self.carrito[seleccion[0]]['id'])
        #logging.info(seleccion.id)
        # messagebox.showwarning(seleccion[0])
        del self.carrito[seleccion[0]]
        self.actualizar_carrito_display()

    def eliminar_uno_del_carrito(self):
        """Elimina el item seleccionado del carrito"""
        seleccion = self.lista_carrito.curselection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un item del carrito")
            return
        index = seleccion[0]
        producto = self.carrito[index]

        # Restar una unidad
        producto["cantidad"] -= 1

        # Si llega a 0, eliminar completamente
        if producto["cantidad"] <= 0:
            del self.carrito[index]

        # Actualizar la interfaz
        self.actualizar_carrito_display()
        self.lista_carrito.selection_set(index)

    def vaciar_carrito(self):
        """Vacía completamente el carrito"""
        if self.carrito and messagebox.askyesno("Confirmar", "¿Vaciar el carrito?"):
            self.carrito = []
            self.actualizar_carrito_display()
    
    def restar_stock_interno(self):
        """Resta stock usando los productos del carrito sin registrar una venta."""
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito para restar stock.")
            return

        if not messagebox.askyesno("Confirmar", "¿Deseas restar el stock de los productos del carrito sin registrar una venta?"):
            return

        for item in self.carrito:
            self.cursor.execute('''
                UPDATE productos SET stock = stock - ? WHERE id = ?
            ''', (item['cantidad'], item['id']))

        self.conn.commit()

        self.carrito = []
        self.actualizar_carrito_display()
        self.actualizar_lista_productos()

        messagebox.showinfo("Stock actualizado", "El stock fue actualizado correctamente (sin registrar venta).")
    def finalizar_venta(self, metodo_pago):
        """Finaliza la venta y la registra"""
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "El carrito está vacío")
            return
        
        # Calcular totales
        total = sum(item['precio'] * item['cantidad'] for item in self.carrito)
        costo_total = sum(item['costo'] * item['cantidad'] for item in self.carrito)
        
        # Registrar venta
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO ventas (fecha, usuario, metodo_pago, total, costo_total)
            VALUES (?, ?, ?, ?, ?)
        ''', (fecha, self.usuario_actual['nombre'], metodo_pago, total, costo_total))
        
        # Registrar turno si aplica
        turno = self.turno_actual if hasattr(self, 'turno_actual') and self.turno_actual else 'MAÑANA'
        self.cursor.execute('''
            INSERT INTO ventas (fecha, usuario, metodo_pago, total, costo_total, turno)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha, self.usuario_actual['nombre'], metodo_pago, total, costo_total, turno))

        venta_id = self.cursor.lastrowid
        
        # Registrar items de la venta
        for item in self.carrito:
            self.cursor.execute('''
                INSERT INTO items_venta (venta_id, producto_nombre, cantidad, precio_unitario, costo_unitario)
                VALUES (?, ?, ?, ?, ?)
            ''', (venta_id, item['nombre'], item['cantidad'], item['precio'], item['costo']))
            
            # Actualizar stock
            self.cursor.execute('''
                UPDATE productos SET stock = stock - ? WHERE id = ?
            ''', (item['cantidad'], item['id']))
        
        self.conn.commit()
        
        # Generar ticket
        if messagebox.askyesno("Ticket", "¿Deseas generar el ticket de venta?"):
            self.generar_ticket(venta_id, metodo_pago, total)
        
        # Limpiar carrito
        self.carrito = []
        self.actualizar_carrito_display()
        self.actualizar_lista_productos()
        
        messagebox.showinfo("Éxito", f"Venta registrada exitosamente\nTotal: ${total}")
    
    def generar_ticket(self, venta_id, metodo_pago, total):
        """Genera un ticket PDF de la venta"""
        try:
            # Crear carpeta 'tickets' si no existe
            carpeta_tickets = "tickets"
            if not os.path.exists(carpeta_tickets):
                os.makedirs(carpeta_tickets)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Encabezado
            pdf.cell(0, 10, 'KIOSCO - TICKET DE VENTA', 0, 1, 'C')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f'Ticket N: {venta_id}', 0, 1, 'C')
            pdf.cell(0, 5, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
            pdf.cell(0, 5, f'Vendedor: {self.usuario_actual["nombre"]}', 0, 1, 'C')
            pdf.ln(5)
            
            # Línea separadora
            pdf.cell(0, 0, '', 'T', 1)
            pdf.ln(3)
            
            # Items
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(100, 5, 'Producto', 0, 0)
            pdf.cell(30, 5, 'Cant.', 0, 0, 'C')
            pdf.cell(40, 5, 'Precio', 0, 1, 'R')
            
            pdf.set_font('Arial', '', 9)
            self.cursor.execute('''
                SELECT producto_nombre, cantidad, precio_unitario
                FROM items_venta WHERE venta_id = ?
            ''', (venta_id,))
            
            items = self.cursor.fetchall()
            for item in items:
                pdf.cell(100, 5, item[0][:30], 0, 0)
                pdf.cell(30, 5, str(item[1]), 0, 0, 'C')
                pdf.cell(40, 5, f'${item[2] * item[1]:.2f}', 0, 1, 'R')
            
            pdf.ln(3)
            pdf.cell(0, 0, '', 'T', 1)
            pdf.ln(3)
            
            # Total
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(130, 8, 'TOTAL:', 0, 0, 'R')
            pdf.cell(40, 8, f'${total:.2f}', 0, 1, 'R')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f'Metodo de pago: {metodo_pago}', 0, 1, 'C')
            
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 5, 'Gracias por su compra!', 0, 1, 'C')
            
            # Guardar en subcarpeta 'tickets'
            filename = os.path.join(carpeta_tickets, f'ticket_{venta_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
            pdf.output(filename)
            messagebox.showinfo("Ticket Generado", f"Ticket guardado como: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar ticket: {str(e)}")
    
    # ===== MÉTODOS DE PRODUCTOS =====
    
    def guardar_producto(self):
        """Guarda o actualiza un producto"""
        nombre = self.prod_nombre.get()
        precio = self.prod_precio.get()
        costo = self.prod_costo.get()
        stock = self.prod_stock.get()
        categoria = self.prod_categoria.get()
        codigo_barras = self.prod_barcode.get()
        
        if not all([nombre, precio, costo, stock]):
            messagebox.showwarning("Campos Vacíos", "Por favor completa todos los campos obligatorios")
            return
        
        try:
            precio = float(precio)
            costo = float(costo)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Error", "Precio, costo y stock deben ser números válidos")
            return
        
        if self.producto_id:
            # Actualizar
            self.cursor.execute('''
                UPDATE productos 
                SET nombre=?, precio=?, costo=?, stock=?, categoria=?, codigo_barras=?
                WHERE id=?
            ''', (nombre, precio, costo, stock, categoria or 'Otros', codigo_barras, self.producto_id))
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
        else:
            # Insertar
            self.cursor.execute('''
                INSERT INTO productos (nombre, precio, costo, stock, categoria, codigo_barras)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, precio, costo, stock, categoria or 'Otros', codigo_barras))
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
        
        self.conn.commit()
        self.limpiar_formulario_producto()
        self.actualizar_tabla_productos()
        self.actualizar_lista_productos()
    
    def limpiar_formulario_producto(self):
        """Limpia el formulario de productos"""
        self.producto_id = None
        self.prod_nombre.delete(0, tk.END)
        self.prod_precio.delete(0, tk.END)
        self.prod_costo.delete(0, tk.END)
        self.prod_stock.delete(0, tk.END)
        self.prod_categoria.set('')
        self.prod_barcode.delete(0, tk.END)
    
    def actualizar_tabla_productos(self):
        """Actualiza la tabla de productos"""
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        self.cursor.execute('SELECT * FROM productos ORDER BY nombre')
        productos = self.cursor.fetchall()
        
        for producto in productos:
            tag = 'bajo_stock' if producto[4] <= 5 else ''
            self.tabla_productos.insert('', 'end', values=producto, tags=(tag,))
        
        self.tabla_productos.tag_configure('bajo_stock', background='#fee2e2')
    
    def editar_producto(self, event=None):
        """Carga el producto seleccionado en el formulario para editar"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un producto")
            return
        
        item = self.tabla_productos.item(seleccion[0])
        valores = item['values']
        
        self.producto_id = valores[0]
        self.prod_nombre.delete(0, tk.END)
        self.prod_nombre.insert(0, valores[1])
        self.prod_precio.delete(0, tk.END)
        self.prod_precio.insert(0, valores[2])
        self.prod_costo.delete(0, tk.END)
        self.prod_costo.insert(0, valores[3])
        self.prod_stock.delete(0, tk.END)
        self.prod_stock.insert(0, valores[4])
        self.prod_categoria.set(valores[5])
        self.prod_barcode.delete(0, tk.END)
        self.prod_barcode.insert(0, valores[6] if valores[6] else '')
    
    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un producto")
            return
        
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este producto?"):
            item = self.tabla_productos.item(seleccion[0])
            producto_id = item['values'][0]
            
            self.cursor.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
            self.conn.commit()
            
            self.actualizar_tabla_productos()
            self.actualizar_lista_productos()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
    def ordenar_tabla_productos(self, col, reverse=False):
        """Ordena la tabla de productos por la columna seleccionada"""
        l = [(self.tabla_productos.set(k, col), k) for k in self.tabla_productos.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]) if col in ['ID', 'Precio', 'Costo', 'Stock'] else t[0], reverse=reverse)
        except ValueError:
            l.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tabla_productos.move(k, '', index)
        # Alterna el orden para el próximo click
        self.tabla_productos.heading(col, command=lambda: self.ordenar_tabla_productos(col, not reverse))
    def exportar_productos_excel(self):
        """Exporta los productos a Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                self.cursor.execute('SELECT * FROM productos')
                productos = self.cursor.fetchall()
                
                df = pd.DataFrame(productos, columns=['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Categoría', 'Código Barras'])
                df.to_excel(filename, index=False)
                
                messagebox.showinfo("Éxito", f"Productos exportados a: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    def importar_productos(self):
        """Importa productos desde un archivo Excel o CSV"""
        file_path = filedialog.askopenfilename(
            title="Selecciona archivo de productos",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if not file_path:
            return
    
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
    
            # Espera columnas: Nombre, Precio, Costo, Stock, Categoría, Código Barras
            for _, row in df.iterrows():
                nombre = row.get('Nombre')
                precio = row.get('Precio')
                costo = row.get('Costo')
                stock = row.get('Stock')
                categoria = row.get('Categoría', 'Otros')
                codigo_barras = row.get('Código Barras', '')
    
                if pd.isnull(nombre) or pd.isnull(precio) or pd.isnull(costo) or pd.isnull(stock):
                    continue  # Salta productos incompletos
    
                try:
                    self.cursor.execute('''
                        INSERT INTO productos (nombre, precio, costo, stock, categoria, codigo_barras)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (nombre, float(precio), float(costo), int(stock), categoria, str(codigo_barras)))
                except sqlite3.IntegrityError:
                    continue  # Salta duplicados
    
            self.conn.commit()
            self.actualizar_tabla_productos()
            self.actualizar_lista_productos()
            messagebox.showinfo("Éxito", "Productos importados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar: {str(e)}")
    # ===== MÉTODOS DE REPORTES =====
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas de ventas"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        mes_actual = datetime.now().strftime('%Y-%m')
        anio_actual = datetime.now().strftime('%Y')
        
        # Ventas de hoy
        self.cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(total), 0), COALESCE(SUM(total - costo_total), 0)
            FROM ventas WHERE DATE(fecha) = ?
        ''', (hoy,))
        ventas_hoy = self.cursor.fetchone()
        
        # Ventas del mes
        self.cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(total), 0), COALESCE(SUM(total - costo_total), 0)
            FROM ventas WHERE strftime('%Y-%m', fecha) = ?
        ''', (mes_actual,))
        ventas_mes = self.cursor.fetchone()
        
        # Ventas del año
        self.cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(total), 0), COALESCE(SUM(total - costo_total), 0)
            FROM ventas WHERE strftime('%Y', fecha) = ?
        ''', (anio_actual,))
        ventas_anio = self.cursor.fetchone()
        
        # Actualizar labels
        self.label_hoy_total.config(text=f"${ventas_hoy[1]:.2f}")
        self.label_hoy_ventas.config(text=f"{ventas_hoy[0]} ventas")
        self.label_hoy_ganancia.config(text=f"Ganancia: ${ventas_hoy[2]:.2f}")
        
        self.label_mes_total.config(text=f"${ventas_mes[1]:.2f}")
        self.label_mes_ventas.config(text=f"{ventas_mes[0]} ventas")
        self.label_mes_ganancia.config(text="Ganancia: ${:.2f}".format(ventas_mes[2]))
        
        self.label_anio_total.config(text=f"${ventas_anio[1]:.2f}")
        self.label_anio_ventas.config(text=f"{ventas_anio[0]} ventas")
        self.label_anio_ganancia.config(text="Ganancia: ${:.2f}".format(ventas_anio[2]))
        
        self.actualizar_tabla_ventas()
    
    def actualizar_tabla_ventas(self):
        """Actualiza la tabla de ventas con filtro por turno y fecha"""
        for item in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(item)
        
        fecha = self.entry_fecha_reporte.get()
        turno = self.combo_turno_reporte.get()
        query = 'SELECT * FROM ventas'
        params = []
        where = []
        if fecha:
            where.append('DATE(fecha) = ?')
            params.append(fecha)
        if turno:
            where.append('turno = ?')
            params.append(turno)
        if where:
            query += ' WHERE ' + ' AND '.join(where)
        query += ' ORDER BY fecha DESC LIMIT 100'
        self.cursor.execute(query, params)
        ventas = self.cursor.fetchall()
        for venta in ventas:
            ganancia = venta[4] - venta[5]
            valores = (venta[0], venta[1], venta[2], venta[3], f'${venta[4]:.2f}', f'${ganancia:.2f}', venta[6])
            self.tabla_ventas.insert('', 'end', values=valores)
    
    def exportar_todo_excel(self):
        """Exporta todos los datos a Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"reporte_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Productos
                    self.cursor.execute('SELECT * FROM productos')
                    productos = self.cursor.fetchall()
                    df_productos = pd.DataFrame(productos, columns=['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Categoría', 'Código Barras'])
                    df_productos.to_excel(writer, sheet_name='Productos', index=False)
                    
                    # Ventas (agrega columna Turno)
                    self.cursor.execute('SELECT * FROM ventas')
                    ventas = self.cursor.fetchall()
                    df_ventas = pd.DataFrame(ventas, columns=['ID', 'Fecha', 'Usuario', 'Método Pago', 'Total', 'Costo Total', 'Turno'])
                    df_ventas['Ganancia'] = df_ventas['Total'] - df_ventas['Costo Total']
                    df_ventas.to_excel(writer, sheet_name='Ventas', index=False)
                    
                    # Items de ventas
                    self.cursor.execute('SELECT * FROM items_venta')
                    items = self.cursor.fetchall()
                    df_items = pd.DataFrame(items, columns=['ID', 'ID Venta', 'Producto', 'Cantidad', 'Precio Unit.', 'Costo Unit.'])
                    df_items.to_excel(writer, sheet_name='Detalle Ventas', index=False)
                    
                    # Resumen
                    hoy = datetime.now().strftime('%Y-%m-%d')
                    mes_actual = datetime.now().strftime('%Y-%m')
                    anio_actual = datetime.now().strftime('%Y')
                    
                    self.cursor.execute('SELECT COUNT(*), SUM(total), SUM(total - costo_total) FROM ventas WHERE DATE(fecha) = ?', (hoy,))
                    resumen_hoy = self.cursor.fetchone()
                    
                    self.cursor.execute('SELECT COUNT(*), SUM(total), SUM(total - costo_total) FROM ventas WHERE strftime("%Y-%m", fecha) = ?', (mes_actual,))
                    resumen_mes = self.cursor.fetchone()
                    
                    self.cursor.execute('SELECT COUNT(*), SUM(total), SUM(total - costo_total) FROM ventas WHERE strftime("%Y", fecha) = ?', (anio_actual,))
                    resumen_anio = self.cursor.fetchone()
                    
                    df_resumen = pd.DataFrame({
                        'Período': ['Hoy', 'Este Mes', 'Este Año'],
                        'Cantidad Ventas': [resumen_hoy[0], resumen_mes[0], resumen_anio[0]],
                        'Total Vendido': [resumen_hoy[1] or 0, resumen_mes[1] or 0, resumen_anio[1] or 0],
                        'Ganancia': [resumen_hoy[2] or 0, resumen_mes[2] or 0, resumen_anio[2] or 0]
                    })
                    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            messagebox.showinfo("Éxito", f"Reporte completo exportado a: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    def exportar_ventas_dia_excel(self):
        """Exporta las ventas de un día específico a Excel con totales"""
        fecha = self.entry_fecha_reporte.get()
        if not fecha:
            messagebox.showwarning("Fecha requerida", "Por favor ingresa una fecha en formato YYYY-MM-DD")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"ventas_{fecha.replace('-', '')}.xlsx"
            )
            if filename:
                # Ventas del día
                self.cursor.execute('''
                    SELECT * FROM ventas WHERE DATE(fecha) = ?
                ''', (fecha,))
                ventas = self.cursor.fetchall()
                df_ventas = pd.DataFrame(ventas, columns=['ID', 'Fecha', 'Usuario', 'Método Pago', 'Total', 'Costo Total', 'Turno'])
                df_ventas['Ganancia'] = df_ventas['Total'] - df_ventas['Costo Total']

                # Items de ventas del día
                venta_ids = [v[0] for v in ventas]
                if venta_ids:
                    placeholders = ','.join(['?'] * len(venta_ids))
                    self.cursor.execute(f'''
                        SELECT * FROM items_venta WHERE venta_id IN ({placeholders})
                    ''', venta_ids)
                    items = self.cursor.fetchall()
                else:
                    items = []
                df_items = pd.DataFrame(items, columns=['ID', 'ID Venta', 'Producto', 'Cantidad', 'Precio Unit.', 'Costo Unit.'])

                # Totales
                total_vendido = df_ventas['Total'].sum() if not df_ventas.empty else 0
                total_ganancia = df_ventas['Ganancia'].sum() if not df_ventas.empty else 0

                # Exportar a Excel
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df_ventas.to_excel(writer, sheet_name='Ventas', index=False)
                    df_items.to_excel(writer, sheet_name='Detalle Ventas', index=False)
                    # Totales
                    df_totales = pd.DataFrame({
                        'Total Vendido': [total_vendido],
                        'Total Ganancia': [total_ganancia]
                    })
                    df_totales.to_excel(writer, sheet_name='Totales', index=False)

                messagebox.showinfo("Éxito", f"Reporte de ventas del {fecha} exportado a: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    # ===== MÉTODOS DE USUARIOS =====
    
    def agregar_usuario(self):
        """Agrega o actualiza un usuario"""
        nombre = self.user_nombre.get()
        password = self.user_password.get()
        rol = self.user_rol.get()
        
        if not all([nombre, password, rol]):
            messagebox.showwarning("Campos Vacíos", "Por favor completa todos los campos")
            return
        
        try:
            if hasattr(self, 'usuario_id') and self.usuario_id:
                # Actualizar usuario
                self.cursor.execute('''
                    UPDATE usuarios SET nombre=?, password=?, rol=? WHERE id=?
                ''', (nombre, password, rol, self.usuario_id))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                self.usuario_id = None
                self.actualizar_tabla_usuarios()
            else:
                self.cursor.execute('''
                    INSERT INTO usuarios (nombre, password, rol)
                    VALUES (?, ?, ?)
                ''', (nombre, password, rol))
                messagebox.showinfo("Éxito", "Usuario agregado correctamente")
                self.conn.commit()
                
                self.user_nombre.delete(0, tk.END)
                self.user_password.delete(0, tk.END)
                self.user_rol.set('empleado')
                
                self.actualizar_tabla_usuarios()
                messagebox.showinfo("Éxito", "Usuario agregado correctamente")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un usuario con ese nombre")
    
    def actualizar_tabla_usuarios(self):
        """Actualiza la tabla de usuarios"""
        for item in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(item)
        
        self.cursor.execute('SELECT id, nombre, password, rol FROM usuarios')
        usuarios = self.cursor.fetchall()
        
        for usuario in usuarios:
            self.tabla_usuarios.insert('', 'end', values=usuario)
    
    def eliminar_usuario(self):
        """Elimina el usuario seleccionado"""
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un usuario")
            return
        
        self.cursor.execute('SELECT COUNT(*) FROM usuarios')
        if self.cursor.fetchone()[0] <= 1:
            messagebox.showwarning("Advertencia", "Debe haber al menos un usuario en el sistema")
            return
        
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este usuario?"):
            item = self.tabla_usuarios.item(seleccion[0])
            usuario_id = item['values'][0]
            
            self.cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            self.conn.commit()
            
            self.actualizar_tabla_usuarios()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
    def editar_usuario(self):
        """Carga el usuario seleccionado en el formulario para editar"""
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor selecciona un usuario")
            return

        item = self.tabla_usuarios.item(seleccion[0])
        valores = item['values']

        self.usuario_id = valores[0]
        self.user_nombre.delete(0, tk.END)
        self.user_nombre.insert(0, valores[1])
        self.user_password.delete(0, tk.END)
        self.user_password.insert(0, valores[2])
        self.user_rol.set(valores[3])
    # ===== OTROS MÉTODOS =====
    
    def logout(self):
        """Cierra sesión"""
        if messagebox.askyesno("Cerrar Sesión", "¿Deseas cerrar sesión?"):
            self.usuario_actual = None
            for widget in self.root.winfo_children():
                widget.destroy()
            self.mostrar_login()
    
    def seleccionar_turno(self):
        """Solicita al empleado seleccionar el turno antes de mostrar el punto de venta"""
        turno_win = tk.Toplevel(self.root)
        turno_win.title("Seleccionar Turno")
        turno_win.geometry("400x300")
        turno_win.resizable(False, False)
        turno_win.grab_set()
        turno_win.transient(self.root)

        # Centrar ventana
        turno_win.update_idletasks()
        x = (turno_win.winfo_screenwidth() // 2) - (400 // 2)
        y = (turno_win.winfo_screenheight() // 2) - (300 // 2)
        turno_win.geometry(f"+{x}+{y}")

        # Deshabilitar botón de cerrar
        turno_win.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(turno_win, text="Selecciona el turno:", font=('Arial', 18, 'bold')).pack(pady=15)
        turno_var = tk.StringVar()
        turno_var.set('MAÑANA')
        for t in ['MAÑANA', 'TARDE', 'NOCHE']:
            tk.Radiobutton(turno_win, text=t, variable=turno_var, value=t, font=('Arial', 14)).pack(anchor='w', padx=80, pady=10)

        def confirmar():
            if not turno_var.get():
                messagebox.showwarning("Turno", "Debes seleccionar un turno")
                return
            self.turno_actual = turno_var.get()
            turno_win.grab_release()
            turno_win.destroy()
            self.crear_pestaña_venta()

        tk.Button(turno_win, text="Confirmar", font=('Arial', 14, 'bold'), bg='#2563eb', fg='white', command=confirmar, width=15, height=2).pack(pady=10)
    
    def __del__(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == '__main__':
    root = tk.Tk()
    app = KioscoPOS(root)
    root.mainloop()