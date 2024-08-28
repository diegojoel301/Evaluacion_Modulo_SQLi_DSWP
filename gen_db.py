import sqlite3
import bcrypt
import os
import secrets  # Asegúrate de importar el módulo secrets

DATABASE = 'database.db'

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def initialize_database():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Crear tablas
        cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
        ''')

        cursor.execute('''
        CREATE TABLE farmacos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE session_cookies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_cookie TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        )
        ''')

        # Inserción de usuarios con contraseñas cifradas aleatoriamente
        users = [
            ('admin', hash_password(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(24))), 1),
            ('user1', hash_password(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(24))), 0),
            ('user2', hash_password(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(24))), 0),
            ('user3', hash_password("password123"), 1)
        ]

        cursor.executemany('INSERT INTO usuarios (username, password, is_admin) VALUES (?, ?, ?)', users)

        # Inserción de fármacos de ejemplo
        farmacos = [
            ('Aspirina', 'Analgésico'),
            ('Paracetamol', 'Antipirético')
        ]

        cursor.executemany('INSERT INTO farmacos (nombre, descripcion) VALUES (?, ?)', farmacos)

        conn.commit()
        conn.close()
        print("Database initialized with random bcrypt passwords.")
    else:
        print("Database already exists, skipping initialization.")

