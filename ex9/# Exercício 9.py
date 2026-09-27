# Exercício 9

import requests
import time

url = "http://127.0.0.1:5000"

for i in range(5):
    resposta = requests.get(
        url,
        headers={"X-Forwarded-For": "192.168.1.10"}
    )
    print("normal:", resposta.status_code)
    time.sleep(1)

for i in range(60):
    resposta = requests.get(
        url + "/rota-inexistente",
        headers={"X-Forwarded-For": "185.220.101.1"}
    )

    print("hostil:", resposta.status_code)