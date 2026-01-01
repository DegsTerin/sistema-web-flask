import os
import psycopg2
from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-local-dev")

def conectar():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(100) UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            descricao TEXT NOT NULL,
            status VARCHAR(30) DEFAULT 'aberta',
            prioridade VARCHAR(20) DEFAULT 'normal',
            criado_por INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP,
            CONSTRAINT fk_usuario
                FOREIGN KEY (criado_por)
                REFERENCES usuarios(id)
                ON DELETE CASCADE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/criar_usuario", methods=["POST"])
def criar_usuario():
    dados = request.get_json()
    usuario = dados["usuario"]
    senha = generate_password_hash(dados["senha"])

    conn = conectar()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)",
            (usuario, senha)
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"erro": "Usuário já existe"}), 400
    finally:
        cur.close()
        conn.close()

    return jsonify({"mensagem": "Usuário criado"})

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = dados["usuario"]
    senha = dados["senha"]

    conn = conectar()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, senha FROM usuarios WHERE usuario = %s",
        (usuario,)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row and check_password_hash(row[1], senha):
        session["usuario_id"] = row[0]
        session["usuario_nome"] = usuario
        return jsonify({"mensagem": "Login ok"})

    return jsonify({"erro": "Credenciais inválidas"}), 401

@app.route("/ocorrencias", methods=["POST"])
def criar_ocorrencia():
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autenticado"}), 401

    dados = request.get_json()

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ocorrencias (titulo, descricao, prioridade, criado_por)
        VALUES (%s, %s, %s, %s)
    """, (
        dados["titulo"],
        dados["descricao"],
        dados.get("prioridade", "normal"),
        session["usuario_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"mensagem": "Ocorrência criada"})

@app.route("/ocorrencias", methods=["GET"])
def listar_ocorrencias():
    if "usuario_id" not in session:
        return jsonify([]), 401

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, titulo, status, prioridade, criado_em
        FROM ocorrencias
        WHERE criado_por = %s
        ORDER BY criado_em DESC
    """, (session["usuario_id"],))

    dados = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(dados)

# cria tabelas apenas no startup
criar_tabelas()

if __name__ == "__main__":
    app.run(debug=True)
