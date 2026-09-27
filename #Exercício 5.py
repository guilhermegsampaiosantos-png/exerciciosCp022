#Exercício 5 — O ORDER BY que o %s não protege (Aulas 3, 6, 7 e 8/A05): 
# Crie GET /api/eventos?ordenar_por=&ordem=&tamanho= sobre o MySQL. 
# Descubra na prática que placeholder não parametriza nome de coluna e defenda com whitelist.


import os
import mysql.connector
from flask import Flask, request, jsonify


app = Flask(__name__)

COLUNAS = {
    "data": "criado_em",
    "sev": "severidade",
    "ip": "ip_origem"
}

ORDEM = {
    "asc": "ASC",
    "desc": "DESC"
}


def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="seguranca"
    )


@app.route("/api/eventos")
def eventos():
    col = request.args.get("ordenar_por", "data")
    ordem = request.args.get("ordem", "asc")
    tamanho = request.args.get("tamanho", "10")

    if col not in COLUNAS:
        return jsonify({
            "erro": "campo de ordenação inválido"
        }), 400

    if ordem not in ORDEM:
        return jsonify({
            "erro": "ordem inválida"
        }), 400

    try:
        tamanho = int(tamanho)
    except ValueError:
        return jsonify({
            "erro": "tamanho deve ser inteiro"
        }), 400

    if tamanho < 1:
        return jsonify({
            "erro": "tamanho deve ser maior que zero"
        }), 400

    if tamanho > 100:
        tamanho = 100

    con = db()
    cur = con.cursor(dictionary=True)

    query = f"""
        SELECT id, criado_em, severidade, ip_origem
        FROM eventos
        ORDER BY {COLUNAS[col]} {ORDEM[ordem]}
        LIMIT %s
    """

    cur.execute(query, (tamanho,))

    dados = cur.fetchall()

    cur.close()
    con.close()

    return jsonify(dados)


if __name__ == "__main__":
    app.run(debug=True)

# LIMIT %s funciona porque o tamanho é um dado que pode ser passado como
# parâmetro para a consulta.
# ORDER BY %s não funciona para nome de coluna porque o nome da coluna é
# um identificador da estrutura SQL e não um valor.
# Por isso a coluna e a ordem precisam ser escolhidas através de uma whitelist.