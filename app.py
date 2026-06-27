from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "123456789003"

# ==========================================
# CONEXIÓN A RAILWAY
# ==========================================

def get_db():
    return mysql.connector.connect(
        host="reseau.proxy.rlwy.net",
        port=25403,
        user="root",
        password="EaOMUSwcZDBQOhbWCDTnMudaBGwtyrRu",
        database="railway"
    )

# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        try:

            usuario = request.form["usuario"]
            contraseña = request.form["contraseña"]

            conn = get_db()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM usuarios
                WHERE usuario=%s
                AND contraseña=%s
            """, (usuario, contraseña))

            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:

                session.clear()

                session["id"] = user["id"]
                session["nombre"] = user["nombre"]
                session["rol"] = user["rol"]
                session["sede"] = user["sede"]

                return redirect("/inicio")

            return render_template(
                "login.html",
                error="Usuario o contraseña incorrectos"
            )

        except Exception as e:
            return f"ERROR LOGIN: {e}"

    return render_template("login.html")


# ==========================================
# INICIO
# ==========================================

@app.route("/")
def home():
    return redirect("/inicio")


@app.route("/inicio")
def inicio():

    if "id" not in session:
        return redirect("/login")

    try:

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
            "index.html",
            solicitudes=solicitudes,
            nombre=session["nombre"],
            rol=session["rol"]
        )

    except Exception as e:
        return f"ERROR INICIO: {e}"


# ==========================================
# CREAR SOLICITUD
# ==========================================

@app.route("/solicitar", methods=["GET", "POST"])
def solicitar():

    if "id" not in session:
        return redirect("/login")

    if request.method == "POST":

        try:

            vendedor = request.form["vendedor"]
            codigo = request.form["codigo"]
            cantidad = request.form["cantidad"]
            sede = request.form["sede"]

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO solicitudes
                (vendedor,codigo,cantidad,estado,sede)
                VALUES(%s,%s,%s,%s,%s)
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

            flash("Solicitud registrada correctamente", "success")

            return redirect("/solicitar")

        except Exception as e:
            return f"ERROR AL INSERTAR: {e}"

    return render_template("solicitar.html")


# ==========================================
# CAMBIAR ESTADO
# ==========================================

@app.route("/estado/<int:id>/<nuevo_estado>")
def cambiar_estado(id, nuevo_estado):

    if "id" not in session:
        return redirect("/login")

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE solicitudes
            SET estado=%s
            WHERE id=%s
        """, (nuevo_estado, id))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/pendientes")

    except Exception as e:
        return str(e)


# ==========================================
# ELIMINAR
# ==========================================

@app.route("/estado/<int:id>/Borrar")
def borrar(id):

    if "id" not in session:
        return redirect("/login")

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM solicitudes
            WHERE id=%s
        """, (id,))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/pendientes")

    except Exception as e:
        return str(e)


# ==========================================
# PENDIENTES
# ==========================================

@app.route("/pendientes")
def pendientes():

    if "id" not in session:
        return redirect("/login")

    try:

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
            "pendientes.html",
            solicitudes=solicitudes
        )

    except Exception as e:
        return str(e)


# ==========================================
# CERRAR SESIÓN
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ==========================================
# RENDER
# ==========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)