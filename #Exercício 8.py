#Exercício 8 — Modelo de ML servido por API, com métricas auditáveis (Aulas 2, 4, 6 e 7): Treine um classificador de risco e exponha-o.
#  O ponto do exercício é que entrada de modelo também é entrada de usuário: precisa ser validada.

import os
from datetime import datetime

import numpy as np
from flask import Flask, request, jsonify
from pymongo import MongoClient

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


app = Flask(__name__)

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["seguranca"]

X = np.array([
    [0, 1, 1000, 8],
    [1, 2, 2000, 10],
    [2, 2, 3000, 12],
    [3, 3, 4000, 13],
    [4, 3, 5000, 14],
    [5, 4, 7000, 15],
    [8, 5, 20000, 2],
    [10, 6, 50000, 3],
    [12, 7, 90000, 3],
    [15, 8, 120000, 4],
    [20, 10, 150000, 1],
    [18, 9, 130000, 2]
])

y = np.array([
    0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1
])

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

modelo.fit(X_treino, y_treino)

previsoes = modelo.predict(X_teste)

precisao = precision_score(y_teste, previsoes, zero_division=0)
recall = recall_score(y_teste, previsoes, zero_division=0)
f1 = f1_score(y_teste, previsoes, zero_division=0)
matriz = confusion_matrix(y_teste, previsoes).tolist()


@app.route("/api/triagem", methods=["POST"])
def triagem():
    dados = request.get_json(silent=True)

    if not dados or "features" not in dados:
        return jsonify({
            "erro": "corpo inválido"
        }), 400

    features = dados["features"]

    if len(features) != 4:
        return jsonify({
            "erro": f"esperadas 4 features, recebidas {len(features)}"
        }), 400

    if not all(isinstance(x, (int, float)) for x in features):
        return jsonify({
            "erro": "features devem ser numéricas"
        }), 400

    entrada = np.array([features])

    risco_numero = modelo.predict(entrada)[0]
    probabilidades = modelo.predict_proba(entrada)[0]
    confianca = float(max(probabilidades))

    risco = "alto" if risco_numero == 1 else "baixo"

    db.previsoes.insert_one({
        "entrada": features,
        "saida": risco,
        "confianca": confianca,
        "timestamp": datetime.now()
    })

    return jsonify({
        "risco": risco,
        "confianca": round(confianca, 2)
    })


@app.route("/api/modelo/metricas")
def metricas():
    return jsonify({
        "precisao": round(precisao, 2),
        "recall": round(recall, 2),
        "f1": round(f1, 2),
        "matriz": matriz,
        "aviso": "A acurácia foi omitida porque uma classe majoritária pode mascarar erros importantes na classificação."
    })


if __name__ == "__main__":
    app.run(debug=True)