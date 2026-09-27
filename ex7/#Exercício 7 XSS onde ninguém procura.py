#Exercício 7 — XSS onde ninguém procura: dentro do atributo (Aulas 6, 7 e 8/A05): 
# Monte GET /dashboard que renderiza uma tabela de incidentes vindos do MongoDB, 
# incluindo o nome do ativo dentro de um atributo HTML (<img src="/icone.png" alt="...">). 
# Prove que sua defesa segura dois payloads diferentes.

import os
from pymongo import MongoClient
from flask import Flask, render_template, make_response


app = Flask(__name__)

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["seguranca"]


@app.after_request
def headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


@app.route("/dashboard")
def dashboard():
    incidentes = list(db.incidentes.find())

    return render_template(
        "dashboard.html",
        incidentes=incidentes
    )


@app.route("/dashboard-inseguro")
def dashboard_inseguro():
    incidentes = list(db.incidentes.find())

    html = "<h1>Dashboard inseguro</h1>"

    for incidente in incidentes:
        html += f"""
        <p>{incidente["titulo"]}</p>
        <img src="/icone.png" alt="{incidente["ativo"]}">
        """

    return html


if __name__ == "__main__":
    app.run(debug=True)