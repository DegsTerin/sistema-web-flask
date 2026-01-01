from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-secreta-simples"

def conectar():
    return sqlite3.connect("banco.db")

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    nome = request.json["nome"]
    senha = request.json["senha"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, senha FROM usuarios WHERE nome = ?", (nome,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario[1], senha):
        session["usuario_id"] = usuario[0]
        return jsonify({"mensagem": "Login realizado"})
    else:
        return jsonify({"mensagem": "Login inválido"}), 401

@app.route("/criar", methods=["POST"])
def criar():
    nome = request.json["nome"]
    senha = generate_password_hash(request.json["senha"])

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
            (nome, senha)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"mensagem": "Usuário já existe"}), 400

    conn.close()
    return jsonify({"mensagem": "Usuário criado"})

@app.route("/listar", methods=["GET"])
def listar():
    if "usuario_id" not in session:
        return jsonify({"mensagem": "Não autorizado"}), 401

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    return jsonify(usuarios)

@app.route("/deletar/<int:id>", methods=["DELETE"])
def deletar(id):
    if "usuario_id" not in session:
        return jsonify({"mensagem": "Não autorizado"}), 401

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Usuário removido"})

# garante que a tabela exista antes do servidor subir
criar_tabela()

if __name__ == "__main__":
    app.run()

