#Exercício 1 — Assistente de decisão de armazenamento (Aulas 1 e 8): 
#Escreva recomendar(perfil) que recebe o perfil de um conjunto de dados e devolve uma recomendação fundamentada: 
# qual banco usar, qual lado do CAP priorizar e qual risco OWASP a escolha errada cria. Nada de if solto no meio do código — 
# a função precisa explicar a decisão.

def recomendar(perfil):
    if perfil["precisa_acid"] or perfil["schema_fixo"]:
        banco = "MySQL"
    else:
        banco = "MongoDB"

    if perfil["tolera_atraso_de_consistencia"] and perfil["escala_horizontal"]:
        cap = "AP"
    else:
        cap = "CP"

    if perfil["dado_sensivel"] and not perfil["precisa_acid"]:
        risco = "A08"
    elif perfil["dado_sensivel"]:
        risco = "A07"
    else:
        risco = "A09"

    if banco == "MySQL" and cap == "CP":
        justificativa = "o cenário precisa manter os dados consistentes e não pode aceitar divergências"
    elif banco == "MongoDB" and cap == "AP":
        justificativa = "é mais importante continuar aceitando os dados mesmo com eventual atraso de consistência"
    elif banco == "MongoDB" and cap == "CP":
        justificativa = "a estrutura pode ser flexível, mas uma divergência nos dados seria inaceitável"
    else:
        justificativa = "o modelo estruturado facilita o controle dos dados e evita inconsistências"

    return {
        "banco": banco,
        "cap": cap,
        "justificativa": justificativa,
        "risco_owasp": risco
    }


perfis = {
    "credenciais_do_SOC": {
        "schema_fixo": True,
        "precisa_acid": True,
        "escala_horizontal": False,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": True
    },
    "telemetria_de_sensores": {
        "schema_fixo": False,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": True,
        "dado_sensivel": False
    },
    "trilha_de_auditoria": {
        "schema_fixo": False,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": True
    },
    "carrinho_de_licencas": {
        "schema_fixo": True,
        "precisa_acid": True,
        "escala_horizontal": False,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": False
    },
    "cache_de_sessoes": {
        "schema_fixo": True,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": True,
        "dado_sensivel": True
    }
}

for nome, perfil in perfis.items():
    resultado = recomendar(perfil)
    print(nome, "->", resultado)