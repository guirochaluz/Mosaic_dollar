import json
import requests
from datetime import datetime

def consultar_dolar_awesome():
    """Consulta cotação do dólar na AwesomeAPI"""
    url = "https://economia.awesomeapi.com.br/last/USD-BRL"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cotacao = data["USDBRL"]
            
            dados_dolar = {
                "data_extracao": datetime.now().isoformat(),
                "valor_dolar_comercial": float(cotacao["bid"]),
                "valor_compra": float(cotacao["ask"]),
                "variacao": cotacao["pctChange"],
                "alta": float(cotacao["high"]),
                "baixa": float(cotacao["low"]),
                "fonte": "AwesomeAPI"
            }
            return dados_dolar
        else:
            print(f"❌ Erro na API: status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        return None

def enviar_para_power_automate(dados):
    """Envia dados para o Power Automate"""
    url_post = "https://prod-148.westus.logic.azure.com:443/workflows/03b78b1fdc274218b46a74212941b110/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=wcqeVoXXQp0w-Ziln67rgTqkeEGDpNYfjXCJFYJpJmc"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url_post, headers=headers, json=dados, timeout=30)
        print(f"✅ Enviado para Power Automate - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no envio: {e}")
        return False

def main():
    """Função principal"""
    print(f"🚀 Iniciando consulta da cotação do dólar - {datetime.now()}")
    
    # Consultar cotação
    dados = consultar_dolar_awesome()
    
    if dados:
        print(f"💰 Cotação atual: R$ {dados['valor_dolar_comercial']}")
        print(f"📈 Variação: {dados['variacao']}%")
        
        # Salvar localmente (opcional, para logs)
        with open("cotacao_dolar.json", "w") as f:
            json.dump(dados, f, indent=4)
        
        # Enviar para Power Automate
        sucesso = enviar_para_power_automate(dados)
        
        if sucesso:
            print("✅ Processo concluído com sucesso!")
        else:
            print("❌ Erro no envio para Power Automate")
            exit(1)
    else:
        print("❌ Falha na consulta da cotação")
        exit(1)

if __name__ == "__main__":
    main()
