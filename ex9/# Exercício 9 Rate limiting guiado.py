# Exercício 9 — Rate limiting guiado por anomalia (Aulas 2, 4, 6 e 8/A09): A própria API vira fonte de dados: 
# registre cada requisição no MongoDB, extraia por agregação o comportamento de cada IP e use IsolationForest para decidir quem é bloqueado com 429.

import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from pymongo import MongoClient

from sklearn.ensemble import IsolationForest


app = Flask(__name__)

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["seguranca"]


def obter_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


@app.before_request
def registrar_inicio():
    request.registro_id = db.acessos.insert_one({
        "ip": obter_ip(),
        "rota": request.path,
        "metodo": request.method,
        "timestamp": datetime.now()
    }).inserted_id


@app.after_request
def registrar_status(response):
    db.acessos.update_one(
        {"_id": request.registro_id},
        {
            "$set": {
                "status": response.status_code
            }
        }
    )

    return response


def analisar_ips():
    agora = datetime.now()
    inicio = agora - timedelta(minutes=1)

    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": inicio
                }
            }
        },
        {
            "$group": {
                "_id": "$ip",
                "total": {"$sum": 1},
                "erros": {
                    "$sum": {
                        "$cond": [
                            {"$gte": ["$status", 400]},
                            1,
                            0
                        ]
                    }
                },
                "rotas": {
                    "$addToSet": "$rota"
                }
            }
        }
    ]

    dados = list(db.acessos.aggregate(pipeline))

    if len(dados) < 2:
        return []

    features = []

    for item in dados:
        total = item["total"]
        taxa_4xx = item["erros"] / total if total else 0
        rotas = len(item["rotas"])

        features.append([
            total,
            taxa_4xx,
            rotas
        ])

    modelo = IsolationForest(
        contamination=0.2,
        random_state=42
    )

    resultados = modelo.fit_predict(features)

    saida = []

    for i, item in enumerate(dados):
        total = item["total"]

        saida.append({
            "ip": item["_id"],
            "req_por_minuto": total,
            "taxa_4xx": item["erros"] / total if total else 0,
            "rotas_distintas": len(item["rotas"]),
            "anomalia": resultados[i] == -1
        })

    return saida


def ip_bloqueado(ip):
    analises = analisar_ips()

    for item in analises:
        if item["ip"] == ip:
            return item["anomalia"]

    return False


@app.before_request
def bloquear_anomalia():
    if ip_bloqueado(obter_ip()):
        return jsonify({
            "erro": "muitas requisições"
        }), 429, {
            "Retry-After": "60"
        }


@app.route("/")
def inicio():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(debug=True)