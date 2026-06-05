from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import sqlite3
from google import genai
from google.genai import types

app = Flask(__name__)

# CONFIGURACIÓN DE GEMINI (Asegúrate de que se llame exactamente 'cliente_ia')
API_KEY = 'AQ.Ab8RN6L1ENU-qk485PaDiNXjVBfnCo_1m0cD5N-U0-pxaIu_ug'
cliente_ia = genai.Client(api_key="AQ.Ab8RN6L1ENU-qk485PaDiNXjVBfnCo_1m0cD5N-U0-pxaIu_ug")

def conectar_db():
    conexion = sqlite3.connect('usuarios.db')
    conexion.row_factory = sqlite3.Row
    return conexion

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    usuario_ingresado = datos.get('usuario')
    contrasena_ingresada = datos.get('contrasena')
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE nombre = ? AND contrasena = ?', (usuario_ingresado, contrasena_ingresada))
    usuario_encontrado = cursor.fetchone()
    conexion.close()
    
    if usuario_encontrado:
        return jsonify({"status": "ok", "mensaje": f"Bienvenido, {usuario_ingresado}!"})
    else:
        return jsonify({"status": "error", "mensaje": "❌ Usuario o contraseña incorrectos."})

@app.route('/preguntar-ia', methods=['POST'])
def preguntar_ia():
    datos = request.json
    mensaje_usuario = datos.get('mensaje')
    nivel = datos.get('nivel')
    
    # 🌟 NORMAS ESTRICTAS DE CALIDAD
    guia_estilo = (
        "REGLA DE ORO: No uses la palabra 'pass' ni dejes funciones vacías. "
        "Todo código debe incluir un bloque 'if __name__ == \"__main__\":' al final con un caso de prueba "
        "real y datos simulados para ejecutarse inmediatamente en la terminal de VS Code. "
        "Encierra el código OBLIGATORIAMENTE entre las etiquetas [CODIGO] y [/CODIGO]. Cero texto de relleno afuera."
    )

    # 🎯 CONFIGURACIÓN QUIRÚRGICA DE LOS NIVELES CON EJEMPLOS MODELO
    if nivel == "TSU":
        ejemplo_tsu = (
            "EJEMPLO MODELO TSU (Programación Estructurada):\n"
            "[CODIGO]\n"
            "def calcular_promedio_estudiante():\n"
            "    # Diccionario simple y funciones nativas\n"
            "    estudiante = {\n"
            "        \"nombre\": \"Wilfredo Salcedo\",\n"
            "        \"carrera\": \"PNF en Informática\",\n"
            "        \"notas\": [16, 18, 15, 17]\n"
            "    }\n"
            "    promedio = sum(estudiante[\"notas\"]) / len(estudiante[\"notas\"])\n"
            "    print(f\"Estudiante: {estudiante['nombre']} - Promedio: {promedio:.2f}\")\n\n"
            "if __name__ == \"__main__\":\n"
            "    calcular_promedio_estudiante()\n"
            "[/CODIGO]"
        )
        instrucciones_contexto = f"Actúa como un programador experto a nivel de TSU en Informática. Resuelve usando funciones limpias, secuenciales y modulares. Sigue este estilo de referencia:\n{ejemplo_tsu}\n{guia_estilo}"

    elif nivel == "Ingeniero":
        ejemplo_ingeniero = (
            "EJEMPLO MODELO INGENIERO (Programación Orientada a Objetos y Excepciones):\n"
            "[CODIGO]\n"
            "class GestorAcademico:\n"
            "    def __init__(self, nombre: str, notas: list):\n"
            "        self.nombre = nombre\n"
            "        self.notas = notas\n\n"
            "    def calcular_promedio(self) -> float:\n"
            "        try:\n"
            "            return sum(self.notas) / len(self.notas) if self.notas else 0.0\n"
            "        except Exception as e:\n"
            "            print(f\"Error de cálculo: {e}\")\n"
            "            return 0.0\n\n"
            "if __name__ == \"__main__\":\n"
            "    alumno = GestorAcademico(\"Wilfredo Salcedo\", [19, 17, 18, 20])\n"
            "    print(f\"Ingeniería -> Alumno: {alumno.nombre} | Promedio: {alumno.calcular_promedio()}\")\n"
            "[/CODIGO]"
        )
        instrucciones_contexto = f"Actúa como un Ingeniero de Software Senior. Resuelve implementando Clases (POO), tipado de datos y robustez contra fallos. Sigue este estilo de referencia:\n{ejemplo_ingeniero}\n{guia_estilo}"

    elif nivel == "Veterano":
        ejemplo_veterano = (
            "EJEMPLO MODELO VETERANO (Código Avanzado, Compacto y de Alto Rendimiento):\n"
            "[CODIGO]\n"
            "from typing import List, Dict\n\n"
            "def procesar_metricas(estudiantes: List[Dict]) -> None:\n"
            "    # Comprensión de diccionarios avanzada con cálculo inline y tipado estricto\n"
            "    analisis = {\n"
            "        e[\"nombre\"]: round(sum(e[\"notas\"]) / len(e[\"notas\"]), 2) \n"
            "        for e in estudiantes if e.get(\"notas\")\n"
            "    }\n"
            "    \n"
            "    for clave, valor in analisis.items():\n"
            "        print(f\"[PRODUCCIÓN-SENIOR] -> {clave}: {valor} pts\")\n\n"
            "if __name__ == \"__main__\":\n"
            "    data_pool = [{\"nombre\": \"Wilfredo Salcedo\", \"notas\": [20, 19, 18, 20]}]\n"
            "    procesar_metricas(data_pool)\n"
            "[/CODIGO]"
        )
        instrucciones_contexto = f"Actúa como un Arquitecto de Software Senior / Veterano. Entrega código compacto, avanzado, usando azúcar sintáctico de Python, comprensión de estructuras y tipado estricto (typing). Cero introducciones teóricas. Sigue este estilo de referencia:\n{ejemplo_veterano}\n{guia_estilo}"
    
    else:
        instrucciones_contexto = f"Actúa como un desarrollador experto. {guia_estilo}"

    prompt_final = f"Instrucciones de rol y nivel académico:\n{instrucciones_contexto}\n\nRequerimiento del usuario a resolver con este estándar: {mensaje_usuario}"

    def generar_respuesta():
        try:
            response_stream = cliente_ia.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=prompt_final,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print("Error en el stream:", e)
            yield "❌ Error en el motor de IA."

    return Response(stream_with_context(generar_respuesta()), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5000)