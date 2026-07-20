from flask import Flask, render_template, request, jsonify, Response, stream_with_context, redirect, url_for, session
import sqlite3
from google import genai
from google.genai import types
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_corporativa_parati'

# 🤖 CONFIGURACIÓN DE GEMINI
API_KEY = 'AQ.Ab8RN6L1ENU-qk485PaDiNXjVBfCo_1m0cD5N-U0-pxaIu_ug'
cliente_ia = genai.Client(api_key="AQ.Ab8RN6L1ENU-qk485PaDiNXjVBfCo_1m0cD5N-U0-pxaIu_ug")

def conectar_db():
    """Conexión robusta a la base de datos"""
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_base, 'usuarios.db')
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_base_datos():
    """Crea la tabla y el usuario administrador inicial si no existe"""
    try:
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
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                ("admin", "1234", "Veterano")
            )
            conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

# Aseguramos la inicialización al arrancar
inicializar_base_datos()


# 🔑 RUTA PRINCIPAL Y LOGIN (A prueba de errores 500)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Captura de datos flexible (funciona con cualquier nombre de campo HTML)
            usuario_ingresado = (request.form.get('username') or 
                                 request.form.get('usuario') or 
                                 request.form.get('user') or '').strip()
            
            contrasena_ingresada = (request.form.get('password') or 
                                    request.form.get('contrasena') or 
                                    request.form.get('pass') or '').strip()

            if not usuario_ingresado or not contrasena_ingresada:
                return "Por favor, ingresa tu usuario y contraseña."

            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", 
                           (usuario_ingresado, contrasena_ingresada))
            cuenta = cursor.fetchone()
            conexion.close()

            if cuenta:
                session['usuario'] = cuenta['usuario']
                session['rol'] = cuenta['rol']
                return f"<h1>¡Inicio de Sesión Exitoso!</h1><p>Bienvenido <b>{cuenta['usuario']}</b> ({cuenta['rol']}).</p>"
            else:
                return "<h1>Error</h1><p>Usuario o contraseña incorrectos. Intenta de nuevo.</p><a href='/'>Volver al inicio</a>"

        except Exception as e:
            # Captura cualquier error de servidor para evitar la pantalla 500
            return f"<h1>Ocurrió un detalle técnico:</h1><p>{str(e)}</p><a href='/'>Volver a intentar</a>"

    return render_template('index.html')


# 👥 RUTA PARA REGISTRAR OTROS USUARIOS
@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        nuevo_usuario = (request.form.get('username') or request.form.get('usuario') or '').strip()
        nueva_contrasena = (request.form.get('password') or request.form.get('contrasena') or '').strip()
        rol_asignado = request.form.get('rol', 'TSU')

        if nuevo_usuario and nueva_contrasena:
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                (nuevo_usuario, nueva_contrasena, rol_asignado)
            )
            conexion.commit()
            conexion.close()
            return "<h1>Usuario Registrado</h1><p>El usuario fue creado con éxito.</p><a href='/'>Ir al Login</a>"
        else:
            return "Faltan datos para el registro."
    except sqlite3.IntegrityError:
        return "El nombre de usuario ya existe."
    except Exception as e:
        return f"Error al registrar: {str(e)}"


# 🚪 CERRAR SESIÓN
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)





    
