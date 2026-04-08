from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
import os

# Agregamos static_url_path para forzar la ruta de estilos
app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static',
            static_url_path='/static')

# Esto obliga al navegador a no guardar el diseño viejo en memoria
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- CONFIGURACIÓN CON TUS DATOS REALES DE RENDER ---
DB_HOST = 'dpg-d7bbpbqdbo4c73dsa5gg-a.oregon-postgres.render.com'
DB_NAME = 'proyecto_personas_ts11'
DB_USER = 'proyecto_personas_ts11_user'
DB_PASSWORD = 'piiTTVRlztV0rbErYkaPWPqVtOFIiG2v'

def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

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

inicializar_base_de_datos()

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
        cursor.close()
        conn.close()
    # Cambié el nombre a 'personas_list' para evitar conflictos con palabras reservadas
    return render_template('administrar.html', personas_list=registros)

@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_registro(dni):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('administrar'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))    
    app.run(host='0.0.0.0', port=port)