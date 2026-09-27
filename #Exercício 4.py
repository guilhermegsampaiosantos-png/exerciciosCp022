# Exercício 4 — Transação com trilha de auditoria (Aulas 2, 3 e 8/A09):
#  Escreva alterar_nivel(admin_id, alvo_id, novo_nivel) que só grava se tudo der certo,
#  e que registre a tentativa na trilha de auditoria mesmo quando falha — porque ataque que não deixa rastro é ataque invisível (A09).

import os
from datetime import datetime
import mysql.connector
from pymongo import MongoClient


mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="seguranca"
)

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["seguranca"]

cur = mysql.cursor(dictionary=True)

cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    nivel_acesso INT
)
""")

usuarios = [
    (1, "ana", "ana@x.com", 5),
    (2, "bruno", "bruno@x.com", 2),
    (3, "caio", "caio@x.com", 1)
]

cur.executemany("""
INSERT IGNORE INTO usuarios
(id, nome, email, nivel_acesso)
VALUES (%s, %s, %s, %s)
""", usuarios)

mysql.commit()


def alterar_nivel(admin_id, alvo_id, novo_nivel):
    cur = mysql.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM usuarios WHERE id = %s",
        (alvo_id,)
    )

    alvo = cur.fetchone()

    nivel_anterior = alvo["nivel_acesso"] if alvo else None

    resultado = "RECUSADO"

    try:
        cur.execute(
            "SELECT * FROM usuarios WHERE id = %s",
            (admin_id,)
        )

        admin = cur.fetchone()

        if admin is None:
            mysql.rollback()

        elif admin["nivel_acesso"] < 5:
            mysql.rollback()

        elif admin_id == alvo_id:
            mysql.rollback()

        elif alvo is None:
            mysql.rollback()

        else:
            cur.execute(
                """
                UPDATE usuarios
                SET nivel_acesso = %s
                WHERE id = %s
                """,
                (novo_nivel, alvo_id)
            )

            mysql.commit()
            resultado = "OK"

    except Exception:
        mysql.rollback()
        resultado = "RECUSADO"

    db.auditoria.insert_one({
        "quem": admin_id,
        "alvo": alvo_id,
        "nivel_anterior": nivel_anterior,
        "nivel_novo": novo_nivel,
        "resultado": resultado,
        "timestamp": datetime.now()
    })

    return resultado


print(alterar_nivel(1, 2, 4))
print(alterar_nivel(2, 3, 5))
print(alterar_nivel(1, 1, 9))
print(alterar_nivel(1, 99, 3))

print(
    db.auditoria.count_documents({
        "resultado": "RECUSADO"
    })
)