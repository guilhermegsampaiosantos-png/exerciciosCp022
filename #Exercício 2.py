#Exercício 2 — Migração relacional → documentos (Aulas 1, 2 e 3): O cadastro está normalizado em MySQL (ativos 1—N alertas). 
# Migre para o MongoDB no modelo de documentos, aninhando os dados do ativo dentro de cada alerta, e prove que nada se perdeu no caminho.

import os
import mysql.connector
from pymongo import MongoClient


mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="seguranca"
)

mongo = MongoClient(os.getenv("MONGO_URI"))
db_mongo = mongo["seguranca"]

cur = mysql.cursor(dictionary=True)

cur.execute("""
CREATE TABLE IF NOT EXISTS ativos (
    id INT PRIMARY KEY,
    nome VARCHAR(100),
    ip VARCHAR(50) UNIQUE,
    criticidade ENUM('baixa','media','alta')
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS alertas (
    id INT PRIMARY KEY,
    ativo_id INT,
    tipo VARCHAR(100),
    severidade VARCHAR(50),
    criado_em DATETIME,
    FOREIGN KEY (ativo_id) REFERENCES ativos(id)
)
""")

ativos = [
    (1, "SRV-WEB01", "192.168.1.10", "alta"),
    (2, "PC-RH03", "192.168.1.45", "baixa")
]

alertas = [
    (1, 1, "BRUTE_FORCE", "critica"),
    (2, 1, "PORT_SCAN", "alta"),
    (3, 2, "XSS", "media")
]

cur.executemany("""
INSERT IGNORE INTO ativos
(id, nome, ip, criticidade)
VALUES (%s, %s, %s, %s)
""", ativos)

cur.executemany("""
INSERT IGNORE INTO alertas
(id, ativo_id, tipo, severidade)
VALUES (%s, %s, %s, %s)
""", alertas)

mysql.commit()

cur.execute("""
SELECT
    alertas.id,
    alertas.tipo,
    alertas.severidade,
    ativos.nome,
    ativos.ip,
    ativos.criticidade
FROM alertas
JOIN ativos ON alertas.ativo_id = ativos.id
""")

dados = cur.fetchall()

documentos = []

for alerta in dados:
    documento = {
        "tipo": alerta["tipo"],
        "severidade": alerta["severidade"],
        "ativo": {
            "nome": alerta["nome"],
            "ip": alerta["ip"],
            "criticidade": alerta["criticidade"]
        }
    }

    documentos.append(documento)

db_mongo.alertas.delete_many({})

if documentos:
    db_mongo.alertas.insert_many(documentos)

cur.execute("SELECT COUNT(*) AS total FROM alertas")
total_mysql = cur.fetchone()["total"]

total_mongo = db_mongo.alertas.count_documents({})

print(f"MySQL: {total_mysql} alertas")
print(f"MongoDB: {total_mongo} documentos")

if total_mysql == total_mongo:
    print("MIGRAÇÃO ÍNTEGRA")

resultado = db_mongo.alertas.find({
    "ativo.criticidade": "alta"
})

print("Alertas de ativos com criticidade alta:")

for alerta in resultado:
    print(alerta)

# No MongoDB, os dados do ativo ficam dentro de cada alerta.
# Isso permite consultar o alerta sem fazer JOIN.
# A desvantagem é a duplicação dos dados do ativo.
# Se o nome ou IP mudar, pode ser necessário atualizar vários documentos.