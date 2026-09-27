import os
import mysql.connector
from flask import Flask, request, jsonify
from markupsafe import escape


app = Flask(__name__)


def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="seguranca"
    )


@app.after_request
def headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    return response


@app.route("/api/usuarios/buscar")
def buscar():
    nome = request.args.get("nome", "")

    con = db()
    cur = con.cursor(dictionary=True)

    try:
        cur.execute(
            """
            SELECT id, nome, email
            FROM usuarios
            WHERE nome LIKE %s
            """,
            (f"%{nome}%",)
        )

        return jsonify(cur.fetchall())

    except mysql.connector.Error:
        return jsonify({
            "erro": "erro interno"
        }), 500

    finally:
        cur.close()
        con.close()


@app.route("/perfil")
def perfil():
    usuario = request.args.get("u", "")

    return (
        "<h1>Bem-vindo, "
        + escape(usuario)
        + "</h1>"
    )


@app.route("/api/usuarios/<int:uid>", methods=["DELETE"])
def remover(uid):
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return jsonify({
            "erro": "autenticação necessária"
        }), 401

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        """
        SELECT nivel
        FROM analistas
        WHERE api_key = %s
        """,
        (api_key,)
    )

    usuario = cur.fetchone()

    if usuario is None:
        cur.close()
        con.close()

        return jsonify({
            "erro": "autenticação inválida"
        }), 401

    if usuario["nivel"] < 5:
        cur.close()
        con.close()

        return jsonify({
            "erro": "acesso negado"
        }), 403

    cur.execute(
        "DELETE FROM usuarios WHERE id = %s",
        (uid,)
    )

    con.commit()

    cur.close()
    con.close()

    return jsonify({
        "removido": uid
    })


@app.route("/api/relatorio")
def relatorio():
    con = db()
    cur = con.cursor()

    try:
        cur.execute(
            "SELECT id, nome FROM usuarios"
        )

        return jsonify(cur.fetchall())

    except mysql.connector.Error:
        return jsonify({
            "erro": "erro interno"
        }), 500

    finally:
        cur.close()
        con.close()


if __name__ == "__main__":
    app.run(
        debug=False,
        host="127.0.0.1"
    )