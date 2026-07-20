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
    """Conexión robusta a la base de datos local/servidor"""
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_base, 'usuarios.db')
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_base_datos():
    """Asegura la creación limpia de la tabla de usuarios"""
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE,
                username TEXT UNIQUE,
                contrasena TEXT,
                password TEXT,
                rol TEXT DEFAULT 'TSU'
            )
        ''')
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

# Inicializamos
inicializar_base_datos()


# 🔑 RUTA PRINCIPAL Y LOGIN (Acepta cualquier estructura de BD)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Captura flexible del formulario
            val_ingresado = (request.form.get('username') or 
                             request.form.get('usuario') or 
                             request.form.get('user') or '').strip()
            
            pass_ingresada = (request.form.get('password') or 
                              request.form.get('contrasena') or 
                              request.form.get('pass') or '').strip()

            if not val_ingresado or not pass_ingresada:
                return "Por favor, ingresa tu usuario y contraseña."

            conexion = conectar_db()
            cursor = conexion.cursor()
            
            # Consultamos las columnas existentes para no fallar
            cursor.execute("PRAGMA table_info(usuarios)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            # Detectamos si la columna se llama 'usuario' o 'username'
            col_user = 'usuario' if 'usuario' in columnas else 'username'
            col_pass = 'contrasena' if 'contrasena' in columnas else 'password'

            query = f"SELECT * FROM usuarios WHERE ({col_user} = ? OR {col_user} = ?) AND ({col_pass} = ? OR {col_pass} = ?)"
            cursor.execute(query, (val_ingresado, val_ingresado, pass_ingresada, pass_ingresada))
            cuenta = cursor.fetchone()

            # Si no existe ningún usuario aún en la BD guardada, creamos a admin al vuelo
            if not cuenta and val_ingresado == 'admin' and pass_ingresada == '1234':
                try:
                    cursor.execute(f"INSERT INTO usuarios ({col_user}, {col_pass}, rol) VALUES (?, ?, ?)",
                                   ('admin', '1234', 'Veterano'))
                    conexion.commit()
                    cursor.execute(query, (val_ingresado, val_ingresado, pass_ingresada, pass_ingresada))
                    cuenta = cursor.fetchone()
                except Exception:
                    pass

            conexion.close()

            if cuenta:
                nombre = cuenta[col_user] if col_user in cuenta.keys() else val_ingresado
                rol = cuenta['rol'] if 'rol' in cuenta.keys() else 'TSU'
                session['usuario'] = nombre
                session['rol'] = rol
                return f"<h1>¡Inicio de Sesión Exitoso!</h1><p>Bienvenido <b>{nombre}</b> ({rol}).</p>"
            else:
                return "<h1>Error</h1><p>Usuario o contraseña incorrectos.</p><a href='/'>Volver a intentar</a>"

        except Exception as e:
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
            cursor.execute("PRAGMA table_info(usuarios)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            col_user = 'usuario' if 'usuario' in columnas else 'username'
            col_pass = 'contrasena' if 'contrasena' in columnas else 'password'

            cursor.execute(
                f"INSERT INTO usuarios ({col_user}, {col_pass}, rol) VALUES (?, ?, ?)",
                (nuevo_usuario, nueva_contrasena, rol_asignado)
            )
            conexion.commit()
            conexion.close()
            return "<h1>Usuario Registrado</h1><p>El usuario fue creado con éxito.</p><a href='/'>Ir al Login</a>"
        else:
            return "Faltan datos para el registro."
    except Exception as e:
        return f"Error al registrar: {str(e)}"


# 🚪 CERRAR SESIÓN
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)




    
