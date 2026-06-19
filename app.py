from flask import Flask, render_template, request, jsonify, Response, stream_with_context, redirect, url_for, session
import sqlite3
from google import genai
from google.genai import types
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_corporativa_parati'

# 🤖 CONFIGURACIÓN DE GEMINI ORIGINAL
API_KEY = 'AQ.Ab8RN6L1ENU-qk485PaDiNXjVBfCo_1m0cD5N-U0-pxaIu_ug'
cliente_ia = genai.Client(api_key="AQ.Ab8RN6L1ENU-qk485PaDiNXjVBfCo_1m0cD5N-U0-pxaIu_ug")

def conectar_db():
    """Tu función de conexión original"""
    conexion = sqlite3.connect('usuarios.db')
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_base_datos():
    """Garantiza que la tabla exista para registrar a tus compañeros"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT DEFAULT 'TSU'
        )
    ''')
    # Crear un administrador inicial para pruebas si la DB está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
            ("admin", "1234", "Veterano")
        )
        conexion.commit()
    conexion.close()

# Inicializa de forma segura al arrancar
inicializar_base_datos()


# 🔑 RUTA DE LOGIN (Evita el error 415 de tipo de medio)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Leemos los datos tradicionales enviados por el formulario HTML
        usuario_ingresado = request.form.get('username')
        contrasena_ingresada = request.form.get('password')
        
        if not usuario_ingresado or not contrasena_ingresada:
            return "Por favor, rellena todos los campos."

        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", 
                       (usuario_ingresado, contrasena_ingresada))
        cuenta = cursor.fetchone()
        conexion.close()
        
        if cuenta:
            session['usuario'] = cuenta['usuario']
            session['rol'] = cuenta['rol']
            # Aquí puedes cambiarlo a la redirección de tu chat cuando esté listo
            return f"¡Inicio de sesión exitoso! Bienvenido {session['usuario']} ({session['rol']})."
        else:
            return "Usuario o contraseña incorrectos. Intenta de nuevo."
            
    return render_template('index.html')


# 👥 RUTA PARA GUARDAR OTROS USUARIOS (Tus compañeros)
@app.route('/registrar', methods=['POST'])
def registrar():
    nuevo_usuario = request.form.get('username')
    nueva_contrasena = request.form.get('password')
    rol_asignado = request.form.get('rol', 'TSU')
    
    if nuevo_usuario and nueva_contrasena:
        try:
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                (nuevo_usuario, nueva_contrasena, rol_asignado)
            )
            conexion.commit()
            conexion.close()
            return "Usuario registrado con éxito. Ya puede iniciar sesión."
        except sqlite3.IntegrityError:
            return "El nombre de usuario ya existe."
            
    return "Datos inválidos."


# 🚪 CERRAR SESIÓN
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

    
