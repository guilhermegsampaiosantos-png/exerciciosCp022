import os
from pymongo import MongoClient

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["seguranca"]

# p1
p1 = "<script>alert('xss1')</script>"

# p2
p2 = 'x" onerror="alert(\'xss2\')'

db.incidentes.delete_many({})

db.incidentes.insert_many([
    {
        "titulo": p1,
        "ativo": "Servidor 01"
    },
    {
        "titulo": "Incidente 2",
        "ativo": p2
    }
])