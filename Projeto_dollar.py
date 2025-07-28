import json
import requests
from datetime import datetime

# Etapa 1: Consultar a cotação do dólar usando a AwesomeAPI
url_api = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
response = requests.get(url_api)
data = response.json()

# Extrair o valor do dólar e a data da extração
valor_dolar = float(data["USDBRL"]["bid"])
data_extracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Criar o dicionário com os dados
dados_dolar = {
    "data_extracao": data_extracao,
    "valor_dolar_comercial": valor_dolar
}

# Salvar os dados em um arquivo JSON
with open("cotacao_dolar.json", "w") as f:
    json.dump(dados_dolar, f, indent=4)

# Etapa 2: Fazer o POST do JSON para a URL fornecida
url_post = "https://prod-148.westus.logic.azure.com:443/workflows/03b78b1fdc274218b46a74212941b110/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=wcqeVoXXQp0w-Ziln67rgTqkeEGDpNYfjXCJFYJpJmc"

headers = {
    "Content-Type": "application/json"
}

# Enviar os dados via POST
post_response = requests.post(url_post, headers=headers, json=dados_dolar)

# Exibir o status da requisição
print(f"Status do POST: {post_response.status_code}")
print(f"Resposta: {post_response.text}")
