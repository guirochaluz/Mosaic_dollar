import json
import requests
from datetime import datetime, timezone, timedelta
import re
from bs4 import BeautifulSoup

# Configurar fuso horário de São Paulo (UTC-3)
SP_TIMEZONE = timezone(timedelta(hours=-3))

def get_sao_paulo_time():
    """Retorna o horário atual de São Paulo"""
    return datetime.now(SP_TIMEZONE)

def consultar_dolar_investing():
    """Web scraping do Investing.com"""
    url = "https://br.investing.com/currencies/usd-brl"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # Regex para extrair o valor da cotação
            pattern = r'"last":"([0-9,.]+)"'
            match = re.search(pattern, response.text)
            
            if match:
                valor = match.group(1).replace(',', '.')
                return {
                    "data_extracao": get_sao_paulo_time().isoformat(),
                    "valor_dolar_comercial": float(valor),
                    "fonte": "Investing.com"
                }
        return None
    except Exception as e:
        print(f"❌ Erro Investing.com: {e}")
        return None

def consultar_dolar_google():
    """Web scraping do Google Finance"""
    url = "https://www.google.com/search?q=dolar+hoje"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # Procurar por padrões de cotação
            patterns = [
                r'R\$\s*([0-9,]+\.[0-9]+)',
                r'([0-9,]+\.[0-9]+)\s*reais',
                r'"([0-9,]+\.[0-9]+)"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    valor = matches[0].replace(',', '')
                    if 4 <= float(valor) <= 7:  # Validação básica
                        return {
                            "data_extracao": get_sao_paulo_time().isoformat(),
                            "valor_dolar_comercial": float(valor),
                            "fonte": "Google"
                        }
        return None
    except Exception as e:
        print(f"❌ Erro Google: {e}")
        return None

def consultar_dolar_yahoo():
    """Consulta Yahoo Finance API (mais estável)"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/USDBRL=X"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                if 'meta' in result and 'regularMarketPrice' in result['meta']:
                    valor = result['meta']['regularMarketPrice']
                    return {
                        "data_extracao": get_sao_paulo_time().isoformat(),
                        "valor_dolar_comercial": round(float(valor), 4),
                        "fonte": "Yahoo Finance"
                    }
        return None
    except Exception as e:
        print(f"❌ Erro Yahoo: {e}")
        return None

def consultar_dolar_bcb_backup():
    """Tenta o Banco Central com data anterior se hoje falhar"""
    from datetime import datetime, timedelta
    
    for i in range(5):  # Tenta os últimos 5 dias
        # Usar horário de São Paulo para determinar a data
        data_sp = get_sao_paulo_time() - timedelta(days=i)
        data_tentativa = data_sp.strftime("%m-%d-%Y")
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_tentativa}'&$format=json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "value" in data and len(data["value"]) > 0:
                    cotacao = data["value"][-1]
                    return {
                        "data_extracao": get_sao_paulo_time().isoformat(),
                        "valor_dolar_comercial": cotacao["cotacaoVenda"],
                        "data_cotacao": data_tentativa,
                        "fonte": "Banco Central"
                    }
        except:
            continue
    
    return None

def consultar_dolar_currencylayer():
    """API CurrencyLayer (backup)"""
    url = "http://apilayer.net/api/live?access_key=YOUR_KEY&currencies=BRL&source=USD&format=1"
    # Versão sem API key (limitada)
    url_free = "https://api.currencylayer.com/live?access_key=free&currencies=BRL&source=USD"
    
    try:
        # Tenta primeiro sem API key
        response = requests.get("https://api.fixer.io/latest?base=USD", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'BRL' in data['rates']:
                return {
                    "data_extracao": get_sao_paulo_time().isoformat(),
                    "valor_dolar_comercial": data['rates']['BRL'],
                    "fonte": "Fixer"
                }
    except:
        pass
    
    return None

def enviar_para_power_automate(dados):
    """Envia dados para o Power Automate"""
    url_post = "https://prod-148.westus.logic.azure.com:443/workflows/03b78b1fdc274218b46a74212941b110/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=wcqeVoXXQp0w-Ziln67rgTqkeEGDpNYfjXCJFYJpJmc"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url_post, headers=headers, json=dados, timeout=30)
        print(f"✅ Enviado para Power Automate - Status: {response.status_code}")
        return response.status_code in [200, 202]  # 200 = OK, 202 = Accepted
    except Exception as e:
        print(f"❌ Erro no envio: {e}")
        return False

def main():
    """Função principal com múltiplas estratégias"""
    sp_time = get_sao_paulo_time()
    print(f"🚀 Iniciando consulta da cotação do dólar - {sp_time.strftime('%d/%m/%Y %H:%M:%S')} (São Paulo)")
    print(f"🌍 Horário UTC: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Lista de APIs/métodos por ordem de prioridade
    estrategias = [
        ("Yahoo Finance", consultar_dolar_yahoo),
        ("Banco Central (backup)", consultar_dolar_bcb_backup),
        ("Investing.com", consultar_dolar_investing),
        ("Google Search", consultar_dolar_google),
        ("CurrencyLayer", consultar_dolar_currencylayer)
    ]
    
    dados = None
    for nome, funcao in estrategias:
        print(f"🔄 Tentando {nome}...")
        dados = funcao()
        if dados:
            print(f"✅ Sucesso com {nome}")
            print(f"💰 Cotação: R$ {dados['valor_dolar_comercial']}")
            break
        else:
            print(f"❌ Falha com {nome}")
    
    if dados:
        # Validação básica da cotação
        valor = dados['valor_dolar_comercial']
        if not (3.0 <= valor <= 10.0):
            print(f"⚠️  Valor suspeito: R$ {valor} - Pode estar incorreto")
        
        # Salvar localmente
        with open("cotacao_dolar.json", "w") as f:
            json.dump(dados, f, indent=4)
        
        print(f"📊 Dados coletados: {dados}")
        
        # Enviar para Power Automate
        sucesso = enviar_para_power_automate(dados)
        
        if sucesso:
            print("✅ Processo concluído com sucesso!")
        else:
            print("❌ Erro no envio para Power Automate")
            print("⚠️  Mas os dados foram coletados corretamente")
            exit(1)
    else:
        print("❌ Todas as estratégias falharam")
        
        # Criar dados de fallback com timestamp para não parar o fluxo
        dados_fallback = {
            "data_extracao": get_sao_paulo_time().isoformat(),
            "valor_dolar_comercial": 0.0,
            "erro": "Todas as fontes falharam",
            "fonte": "Fallback"
        }
        
        print("🔄 Enviando dados de erro para Power Automate...")
        enviar_para_power_automate(dados_fallback)
        exit(1)

if __name__ == "__main__":
    main()
