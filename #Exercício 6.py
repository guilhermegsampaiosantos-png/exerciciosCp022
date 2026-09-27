# Exercício 6 — Controle de acesso quebrado (Aulas 3, 6 e 8/A01): 
# Uma API de incidentes em que cada analista só pode ver os seus incidentes, e apenas nível ≥ 5 pode apagar qualquer um. 
# Autenticação por header X-API-Key validado no MySQL com query parametrizada.

import os
import mysql.connector
from flask import Flask, request, jsonify


app = Flask(__name__)


def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="seguranca"
    )


def autenticar():
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return None

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        """
        SELECT id, nome, nivel
        FROM analistas
        WHERE api_key = %s
        """,
        (api_key,)
    )

    analista = cur.fetchone()

    cur.close()
    con.close()

    return analista


@app.route("/api/incidentes/<int:incidente_id>")
def buscar_incidente(incidente_id):
    analista = autenticar()

    if analista is None:
        return jsonify({"erro": "autenticação necessária"}), 401

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        """
        SELECT id, dono_id, titulo, severidade, status
        FROM incidentes
        WHERE id = %s
        """,
        (incidente_id,)
    )

    incidente = cur.fetchone()

    if incidente is None:
        cur.close()
        con.close()
        return jsonify({"erro": "incidente não encontrado"}), 404

    if incidente["dono_id"] != analista["id"]:
        cur.close()
        con.close()
        return jsonify({"erro": "acesso negado"}), 403

    cur.close()
    con.close()

    return jsonify(incidente)


@app.route("/api/incidentes")
def listar_incidentes():
    analista = autenticar()

    if analista is None:
        return jsonify({"erro": "autenticação necessária"}), 401

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        """
        SELECT id, dono_id, titulo, severidade, status
        FROM incidentes
        WHERE dono_id = %s
        """,
        (analista["id"],)
    )

    dados = cur.fetchall()

    cur.close()
    con.close()

    return jsonify(dados)


@app.route("/api/incidentes/<int:incidente_id>", methods=["DELETE"])
def remover_incidente(incidente_id):
    analista = autenticar()

    if analista is None:
        return jsonify({"erro": "autenticação necessária"}), 401

    if analista["nivel"] < 5:
        return jsonify({"erro": "acesso negado"}), 403

    con = db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM incidentes WHERE id = %s",
        (incidente_id,)
    )

    if cur.rowcount == 0:
        con.rollback()
        cur.close()
        con.close()
        return jsonify({"erro": "incidente não encontrado"}), 404

    con.commit()

    cur.close()
    con.close()

    return jsonify({"removido": incidente_id})


if __name__ == "__main__":
    app.run(debug=True)