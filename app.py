from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import secrets
import os
import bcrypt
import hashlib
import time
# Importar el script de generación de la base de datos
from gen_db import initialize_database

# Inicializar la base de datos
initialize_database()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Genera un secret_key aleatorio de 32 caracteres (16 bytes)

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Configura la conexión para retornar filas como diccionarios
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def list_farmacos():
    db = get_db()
    query = "SELECT * FROM farmacos"
    farmacos = db.execute(query).fetchall()
    
    set_admin_session_cookie(1)

    return render_template('list_farmacos.html', farmacos=farmacos)

@app.route('/filter', methods=['GET'])
def filter_farmacos():
    if 'id' in request.args:
        db = get_db()
        id = request.args.get('id')
        query = f"SELECT * FROM farmacos WHERE id = {id}"
        farmacos = db.execute(query).fetchall()
        return render_template('list_farmacos.html', farmacos=farmacos)
    return redirect(url_for('list_farmacos'))

def set_admin_session_cookie(user_id):
    # Invalidar cualquier sesión previa del administrador
    #invalidate_admin_sessions(user_id)

    # Generar un nuevo hash de sesión
    session_hash = hashlib.sha256(f"{user_id}{time.time()}{secrets.token_hex(16)}".encode()).hexdigest()

    # Guardar el nuevo hash de sesión en la base de datos
    db = get_db()
    db.execute("INSERT INTO session_cookies (user_id, session_cookie) VALUES (?, ?)", 
               (user_id, session_hash))
    db.commit()

    return session_hash
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        query = "SELECT * FROM usuarios WHERE username = ?"
        user = db.execute(query, (username,)).fetchone()

        if user is not None and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']

            if user['is_admin']:
                # Establecer la cookie de sesión del administrador
                session_hash = set_admin_session_cookie(user['id'])
                # Establecer la cookie de sesión en el navegador
                response = redirect(url_for('admin_panel'))
                response.set_cookie('session_hash', session_hash)
                return response
            else:
                # Si no es administrador, redirigir a otra página
                return redirect(url_for('list_farmacos'))
        else:
            return render_template('login.html', error="Credenciales inválidas.")
    
    return render_template('login.html')

@app.route('/admin')
def admin_panel():
    # Recuperar la cookie de sesión desde el navegador
    session_hash = request.cookies.get('session_hash')
    
    if not session_hash:
        return redirect(url_for('login'))
    
    db = get_db()

    # Verificar que la cookie exista en la base de datos y que pertenezca a un administrador
    session_in_db = db.execute("""
        SELECT u.* FROM session_cookies sc
        JOIN usuarios u ON sc.user_id = u.id
        WHERE sc.session_cookie = ? AND u.is_admin = 1
    """, (session_hash,)).fetchone()

    if session_in_db:
        # Cargar los datos del panel si la sesión es válida y el usuario es administrador
        farmacos = db.execute("SELECT * FROM farmacos").fetchall()
        usuarios = db.execute("SELECT * FROM usuarios").fetchall()
        return render_template('admin_panel.html', farmacos=farmacos, usuarios=usuarios)
    else:
        # Si la cookie no es válida o el usuario no es administrador, redirigir al login
        return redirect(url_for('login'))

@app.route('/admin/delete_user/<string:id>', methods=['POST'])
def delete_user(id):
    db = get_db()
    query = f"DELETE FROM usuarios WHERE id = {id}"
    db.execute(query)
    db.commit()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

