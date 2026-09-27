#Exercício 3 — Retenção e janela temporal (Aula 2): Um SOC não guarda log para sempre nem olha o total — olha a janela. 
# Crie a coleção eventos com um índice TTL, popule 200 eventos espalhados em 24 horas e produza, por agregação, a distribuição de falhas por hora do dia.

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import os


mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["seguranca"]

eventos = db["eventos"]

eventos.delete_many({})

eventos.create_index(
    "timestamp",
    expireAfterSeconds=604800
)

agora = datetime.now()

dados = []

for i in range(200):
    minutos = random.randint(0, 24 * 60 - 1)

    dados.append({
        "tipo": "falha",
        "timestamp": agora - timedelta(minutes=minutos)
    })

eventos.insert_many(dados)

pipeline = [
    {
        "$group": {
            "_id": {
                "$hour": "$timestamp"
            },
            "total": {
                "$sum": 1
            }
        }
    },
    {
        "$sort": {
            "_id": 1
        }
    }
]

resultado = list(eventos.aggregate(pipeline))

print("=== Falhas por hora (últimas 24h) ===")

hora_pico = None
maior_total = 0

for item in resultado:
    hora = item["_id"]
    total = item["total"]

    print(f"{hora:02d}h | {total}")

    if total > maior_total:
        maior_total = total
        hora_pico = hora

print(f"Hora de pico: {hora_pico:02d}h ({maior_total} falhas)")
print("Índice TTL ativo: eventos com mais de 7 dias serão removidos automaticamente.")

# O TTL também é uma decisão de segurança porque reduz o tempo em que
# informações de eventos ficam armazenadas e disponíveis para acesso.