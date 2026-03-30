import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os

# 1. Autenticação
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 2. Abrir a planilha pelo ID
spreadsheet = client.open_by_key("1kIo_svj3RHOHjiOQ7hULX-Vp2o4hfvHLRhN_U7xxcD8")
sheet = spreadsheet.get_worksheet(0) 

# 3. LEITURA BRUTA: Pega todos os valores da aba de uma vez só
# Isso evita o erro "Location not found" de células específicas
dados_brutos = sheet.get_all_values()

# 4. Extração Manual dos Dados
# A mensagem está na Linha 2, Coluna A -> dados_brutos[1][0]
try:
    mensagem_mestra = dados_brutos[1][0]
except:
    mensagem_mestra = "Olá {{nome}}"

print(f"Mensagem carregada: {mensagem_mestra}")

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

# 5. Percorrer os contatos (Começa da linha 2)
for i, linha in enumerate(dados_brutos[1:], start=2):
    # linha[1] é Coluna B (Nome), linha[2] é Coluna C (Telefone)
    if len(linha) < 3:
        continue
        
    nome = linha[1].strip()
    telefone_bruto = linha[2].strip()
    
    # Limpa o telefone
    telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))
    
    if nome and len(telefone) >= 10:
        msg_final = mensagem_mestra.replace("{{nome}}", nome)
        
        payload = {
            "number": telefone,
            "text": msg_final,
            "delay": 1200
        }
        headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}
        
        print(f"Linha {i}: Enviando para {nome}...")
        try:
            res = requests.post(API_URL, json=payload, headers=headers)
            print(f"Status: {res.status_code}")
        except Exception as e:
            print(f"Erro na linha {i}: {e}")
        
        time.sleep(15)

print("🚀 Finalizado!")
