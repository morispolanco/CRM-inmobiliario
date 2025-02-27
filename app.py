# app.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Configuración inicial de la base de datos
def init_db():
    conn = sqlite3.connect('crm_inmobiliario.db')
    c = conn.cursor()
    
    # Tabla de proyectos
    c.execute('''CREATE TABLE IF NOT EXISTS proyectos 
                 (id INTEGER PRIMARY KEY, nombre TEXT, ubicacion TEXT, 
                  fecha_inicio TEXT, estado TEXT)''')
    
    # Tabla de clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                 (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT, 
                  telefono TEXT, tipo TEXT, proyecto_id INTEGER)''')
    
    # Tabla de propiedades
    c.execute('''CREATE TABLE IF NOT EXISTS propiedades 
                 (id INTEGER PRIMARY KEY, proyecto_id INTEGER, 
                  numero TEXT, precio REAL, estado TEXT)''')
    
    # Tabla de pagos
    c.execute('''CREATE TABLE IF NOT EXISTS pagos 
                 (id INTEGER PRIMARY KEY, cliente_id INTEGER, 
                  propiedad_id INTEGER, monto REAL, fecha TEXT, 
                  concepto TEXT)''')
    
    # Tabla de garantías
    c.execute('''CREATE TABLE IF NOT EXISTS garantias 
                 (id INTEGER PRIMARY KEY, propiedad_id INTEGER, 
                  cliente_id INTEGER, descripcion TEXT, 
                  fecha_reclamo TEXT, estado TEXT)''')
    
    conn.commit()
    conn.close()

# Funciones de la base de datos
def agregar_proyecto(nombre, ubicacion, fecha_inicio, estado):
    conn = sqlite3.connect('crm_inmobiliario.db')
    c = conn.cursor()
    c.execute("INSERT INTO proyectos (nombre, ubicacion, fecha_inicio, estado) VALUES (?, ?, ?, ?)",
              (nombre, ubicacion, fecha_inicio, estado))
    conn.commit()
    conn.close()

def agregar_cliente(nombre, email, telefono, tipo, proyecto_id):
    conn = sqlite3.connect('crm_inmobiliario.db')
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nombre, email, telefono, tipo, proyecto_id) VALUES (?, ?, ?, ?, ?)",
              (nombre, email, telefono, tipo, proyecto_id))
    conn.commit()
    conn.close()

def agregar_propiedad(proyecto_id, numero, precio, estado):
    conn = sqlite3.connect('crm_inmobiliario.db')
    c = conn.cursor()
    c.execute("INSERT INTO propiedades (proyecto_id, numero, precio, estado) VALUES (?, ?, ?, ?)",
              (proyecto_id, numero, precio, estado))
    conn.commit()
    conn.close()

def registrar_pago(cliente_id, propiedad_id, monto, fecha, concepto):
    conn = sqlite3.connect('crm_inmobiliario.db')
    c = conn.cursor()
    c.execute("INSERT INTO pagos (cliente_id, propiedad_id, monto, fecha, concepto) VALUES (?, ?, ?, ?, ?)",
              (cliente_id, propiedad_id, monto, fecha, concepto))
    conn.commit()
    conn.close()

def registrar_garantia(propiedad_id, cliente_id, descripcion, fecha_reclamo, estado):
    conn = sqlite3.connect('crm_inmobiliario.db')
    c = conn.cursor()
    c.execute("INSERT INTO garantias (propiedad_id, cliente_id, descripcion, fecha_reclamo, estado) VALUES (?, ?, ?, ?, ?)",
              (propiedad_id, cliente_id, descripcion, fecha_reclamo, estado))
    conn.commit()
    conn.close()

# Interfaz de Streamlit
def main():
    init_db()
    
    st.title("CRM Inmobiliario")
    menu = ["Proyectos", "Clientes", "Ventas", "Garantías"]
    opcion = st.sidebar.selectbox("Menú", menu)
    
    # Módulo de Proyectos
    if opcion == "Proyectos":
        st.header("Administración de Proyectos")
        with st.form("nuevo_proyecto"):
            nombre = st.text_input("Nombre del Proyecto")
            ubicacion = st.text_input("Ubicación")
            fecha_inicio = st.date_input("Fecha de Inicio")
            estado = st.selectbox("Estado", ["Activo", "En Planeación", "Finalizado"])
            submit = st.form_submit_button("Registrar Proyecto")
            if submit:
                agregar_proyecto(nombre, ubicacion, str(fecha_inicio), estado)
                st.success("Proyecto registrado exitosamente")
        
        conn = sqlite3.connect('crm_inmobiliario.db')
        df = pd.read_sql_query("SELECT * FROM proyectos", conn)
        st.dataframe(df)
        conn.close()
    
    # Módulo de Clientes
    elif opcion == "Clientes":
        st.header("Gestión de Clientes")
        with st.form("nuevo_cliente"):
            nombre = st.text_input("Nombre")
            email = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            tipo = st.selectbox("Tipo", ["Prospecto", "Cliente"])
            conn = sqlite3.connect('crm_inmobiliario.db')
            proyectos = pd.read_sql_query("SELECT id, nombre FROM proyectos", conn)
            proyecto_id = st.selectbox("Proyecto", proyectos['nombre'])
            submit = st.form_submit_button("Registrar Cliente")
            if submit:
                proyecto_seleccionado = proyectos[proyectos['nombre'] == proyecto_id]['id'].iloc[0]
                agregar_cliente(nombre, email, telefono, tipo, proyecto_seleccionado)
                st.success("Cliente registrado exitosamente")
        
        conn = sqlite3.connect('crm_inmobiliario.db')
        df = pd.read_sql_query("SELECT c.*, p.nombre as proyecto FROM clientes c LEFT JOIN proyectos p ON c.proyecto_id = p.id", conn)
        st.dataframe(df)
        conn.close()
    
    # Módulo de Ventas
    elif opcion == "Ventas":
        st.header("Gestión de Ventas")
        
        # Registro de propiedades
        st.subheader("Registro de Propiedades")
        with st.form("nueva_propiedad"):
            conn = sqlite3.connect('crm_inmobiliario.db')
            proyectos = pd.read_sql_query("SELECT id, nombre FROM proyectos", conn)
            proyecto_id = st.selectbox("Proyecto", proyectos['nombre'], key="prop_proy")
            numero = st.text_input("Número de Propiedad")
            precio = st.number_input("Precio", min_value=0.0)
            estado = st.selectbox("Estado", ["Disponible", "Reservada", "Vendida"])
            submit_prop = st.form_submit_button("Registrar Propiedad")
            if submit_prop:
                proyecto_seleccionado = proyectos[proyectos['nombre'] == proyecto_id]['id'].iloc[0]
                agregar_propiedad(proyecto_seleccionado, numero, precio, estado)
                st.success("Propiedad registrada exitosamente")
        
        # Registro de pagos
        st.subheader("Control de Pagos")
        with st.form("nuevo_pago"):
            clientes = pd.read_sql_query("SELECT id, nombre FROM clientes", conn)
            propiedades = pd.read_sql_query("SELECT id, numero FROM propiedades", conn)
            cliente_id = st.selectbox("Cliente", clientes['nombre'])
            propiedad_id = st.selectbox("Propiedad", propiedades['numero'])
            monto = st.number_input("Monto", min_value=0.0)
            fecha = st.date_input("Fecha de Pago")
            concepto = st.selectbox("Concepto", ["Enganche", "Mensualidad", "Liquidación"])
            submit_pago = st.form_submit_button("Registrar Pago")
            if submit_pago:
                cliente_seleccionado = clientes[clientes['nombre'] == cliente_id]['id'].iloc[0]
                propiedad_seleccionada = propiedades[propiedades['numero'] == propiedad_id]['id'].iloc[0]
                registrar_pago(cliente_seleccionado, propiedad_seleccionada, monto, str(fecha), concepto)
                st.success("Pago registrado exitosamente")
        
        # Mostrar propiedades y pagos
        st.subheader("Resumen")
        df_prop = pd.read_sql_query("SELECT p.*, pr.nombre as proyecto FROM propiedades p LEFT JOIN proyectos pr ON p.proyecto_id = pr.id", conn)
        df_pagos = pd.read_sql_query("SELECT pg.*, c.nombre as cliente, pr.numero as propiedad FROM pagos pg LEFT JOIN clientes c ON pg.cliente_id = c.id LEFT JOIN propiedades pr ON pg.propiedad_id = pr.id", conn)
        st.dataframe(df_prop)
        st.dataframe(df_pagos)
        conn.close()
    
    # Módulo de Garantías
    elif opcion == "Garantías":
        st.header("Control de Garantías")
        
        with st.form("nueva_garantia"):
            conn = sqlite3.connect('crm_inmobiliario.db')
            clientes = pd.read_sql_query("SELECT id, nombre FROM clientes", conn)
            propiedades = pd.read_sql_query("SELECT id, numero FROM propiedades", conn)
            cliente_id = st.selectbox("Cliente", clientes['nombre'], key="gar_cli")
            propiedad_id = st.selectbox("Propiedad", propiedades['numero'], key="gar_prop")
            descripcion = st.text_area("Descripción del Reclamo")
            fecha_reclamo = st.date_input("Fecha de Reclamo")
            estado = st.selectbox("Estado", ["Pendiente", "En Proceso", "Resuelto"])
            submit_gar = st.form_submit_button("Registrar Reclamo")
            if submit_gar:
                cliente_seleccionado = clientes[clientes['nombre'] == cliente_id]['id'].iloc[0]
                propiedad_seleccionada = propiedades[propiedades['numero'] == propiedad_id]['id'].iloc[0]
                registrar_garantia(propiedad_seleccionada, cliente_seleccionado, descripcion, str(fecha_reclamo), estado)
                st.success("Reclamo de garantía registrado exitosamente")
        
        # Mostrar garantías
        df_gar = pd.read_sql_query("SELECT g.*, c.nombre as cliente, p.numero as propiedad FROM garantias g LEFT JOIN clientes c ON g.cliente_id = c.id LEFT JOIN propiedades p ON g.propiedad_id = p.id", conn)
        st.dataframe(df_gar)
        conn.close()

if __name__ == '__main__':
    if "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    main()
