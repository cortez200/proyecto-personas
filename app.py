from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
import os

app = Flask(__name__, template_folder='templates')

# --- CONFIGURACIÓN CON TUS DATOS REALES DE RENDER ---
DB_HOST = 'dpg-d7bbpbqdbo4c73dsa5gg-a.oregon-postgres.render.com'
DB_NAME = 'proyecto_personas_ts11'
DB_USER = 'proyecto_personas_ts11_user'
DB_PASSWORD = 'piiTTVRlztV0rbErYkaPWPqVtOFIiG2v'

def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASSWORD, 
            host=DB_HOST
        )
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

# --- NUEVO: FUNCIÓN PARA CREAR LA TABLA AUTOMÁTICAMENTE ---
def inicializar_base_de_datos():
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id SERIAL PRIMARY KEY,
                    dni VARCHAR(20) NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    direccion TEXT,
                    telefono VARCHAR(20)
                );
            ''')
            conn.commit()
            print("✅ Tabla 'personas' verificada/creada con éxito.")
            cursor.close()
            conn.close()
        except Exception as e:
            print("❌ Error al crear la tabla:", e)

# Ejecutamos la creación de la tabla al arrancar la app
inicializar_base_de_datos()

# --- RUTAS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personas (dni, nombre, apellido, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
                       (dni, nombre, apellido, direccion, telefono))
        conn.commit()
        conn.close()
    
    return redirect(url_for('administrar'))

@app.route('/administrar')
def administrar():
    conn = conectar_db()
    registros = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas ORDER BY apellido")
        registros = cursor.fetchall()
        conn.close()
    return render_template('administrar.html', registros=registros)

@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_registro(dni):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
        conn.commit()
        conn.close()
    return redirect(url_for('administrar'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))    
    app.run(host='0.0.0.0', port=port)