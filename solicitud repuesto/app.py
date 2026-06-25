from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import requests

app = Flask(__name__)
app.secret_key = "123456789003"




# =========================
# CONEXIÓN MYSQL
# =========================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="Sager",
        password="123456789003",
        database="bodega"
    )

# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE usuario = %s
            AND contraseña = %s
        """, (usuario, contraseña))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session.clear()

            session['id'] = user['id']
            session['nombre'] = user['nombre']
            session['rol'] = user['rol']

            return redirect('/inicio')

        return render_template(
            'login.html',
            error='Usuario o contraseña incorrectos'
        )

    return render_template('login.html')


# =========================
# RAÍZ DEL SISTEMA
# =========================
@app.route('/')
def home():
    return redirect('/inicio')


# =========================
# INICIO
# =========================
@app.route('/inicio')
def index():

    if 'id' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM solicitudes
        ORDER BY id DESC
    """)

    solicitudes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'index.html',
        solicitudes=solicitudes,
        nombre=session['nombre'],
        rol=session['rol']
    )

# =========================
# CREAR SOLICITUD
# =========================
@app.route('/solicitar', methods=['GET', 'POST'])
def solicitar():

    if 'id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        try:

            vendedor = request.form.get('vendedor')
            codigo = request.form.get('codigo')
            cantidad = request.form.get('cantidad')
            sede = request.form.get('sede')

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO solicitudes
                (vendedor, codigo, cantidad, estado, sede)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                vendedor,
                codigo,
                cantidad,
                "Pendiente",
                sede
            ))

            conn.commit()

            cursor.close()
            conn.close()

            flash("✅ Tu solicitud fue registrada exitosamente", "success")

            return redirect('/solicitar')

        except Exception as e:
            print("ERROR AL GUARDAR:", e)
            return f"Error al guardar: {e}"

    return render_template('solicitar.html')


# =========================
# CAMBIAR ESTADO
# =========================
@app.route('/estado/<int:id>/<nuevo_estado>')
def cambiar_estado(id, nuevo_estado):

    if 'id' not in session:
        return redirect('/login')

    estados_validos = [
        'Pendiente',
        'Buscar',
        'Listo',
        'No Disponible'
    ]

    if nuevo_estado not in estados_validos:
        return "Estado no válido"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE solicitudes
        SET estado = %s
        WHERE id = %s
    """, (nuevo_estado, id))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/pendientes')

# =========================
# ELIMINAR
# =========================
@app.route('/estado/<int:id>/Borrar')
def borrar(id):

    if 'id' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM solicitudes
        WHERE id = %s
    """, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/pendientes')


# =========================
# PENDIENTES
# =========================
@app.route('/pendientes')
def pendientes():

    if 'id' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM solicitudes
        ORDER BY id DESC
    """)

    solicitudes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'pendientes.html',
        solicitudes=solicitudes
    )


# =========================
# CERRAR SESIÓN
# =========================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# =========================
# EJECUTAR APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)