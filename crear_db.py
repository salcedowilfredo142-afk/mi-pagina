import sqlite3

# Conectamos con la base de datos (si no existe, Python la crea automáticamente)
conexion = sqlite3.connect('usuarios.db')

# Creamos un "cursor" para poder ejecutar órdenes SQL
cursor = conexion.cursor()

# Creamos la tabla de usuarios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        contrasena TEXT NOT NULL
    )
''')

# Insertamos un usuario de prueba para poder ingresar más tarde
try:
    cursor.execute('''
        INSERT INTO usuarios (nombre, contrasena) 
        VALUES ('wilfredo', '12345')
    ''')
    conexion.commit()
    print("¡Base de datos creada y usuario 'wilfredo' registrado con éxito!")
except sqlite3.IntegrityError:
    print("La base de datos ya existía y el usuario ya estaba registrado.")

# Cerramos la conexión
conexion.close()