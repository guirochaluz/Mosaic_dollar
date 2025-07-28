import json
import requests
from datetime import datetime

try:
    # Etapa 1: Consultar a cotação do dólar usando a AwesomeAPI
    url_api = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    response = requests.get(url_api, timeout=10)

    if response.status_code == 200:
        data = response.json()

        if "USDBRL" in data:
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
            headers = { "Content-Type": "application/json" }

            post_response = requests.post(url_post, headers=headers, json=dados_dolar)
            print(f"Status do POST: {post_response.status_code}")
            print(f"Resposta: {post_response.text}")
        else:
            print("❌ Campo 'USDBRL' não encontrado na resposta da API.")
            print("Resposta recebida:", data)
    else:
        print(f"❌ Erro na requisição: status {response.status_code}")
except Exception as e:
    print("❌ Erro inesperado:", e)
