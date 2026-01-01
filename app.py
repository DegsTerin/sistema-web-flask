from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "troque-por-uma-chave-forte"

def conectar():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    nome = dados["nome"]
    senha = dados["senha"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT senha FROM usuarios WHERE usuario = %s",
        (nome,)
    )
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row[0], senha):
        session["usuario"] = nome
        return jsonify({"mensagem": "Login realizado com sucesso"})

    return jsonify({"mensagem": "Usuário ou senha inválidos"}), 401

@app.route("/criar", methods=["POST"])
def criar():
    dados = request.get_json()
    nome = dados["nome"]
    senha = generate_password_hash(dados["senha"])

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)",
    (nome, senha)
)

    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Usuário criado"})

@app.route("/listar")
def listar():
    if "usuario" not in session:
        return jsonify([]), 401

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    return jsonify(dados)

@app.route("/deletar/<int:id>", methods=["DELETE"])
def deletar(id):
    if "usuario" not in session:
        return jsonify({"mensagem": "Não autorizado"}), 401

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Usuário removido"})

# garante que a tabela exista antes do servidor subir
criar_tabela()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)