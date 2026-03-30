import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os

# 1. Autenticação
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 2. Abrir a planilha
spreadsheet = client.open_by_key("1kIo_svj3RHOHjiOQ7hULX-Vp2o4hfvHLRhN_U7xxcD8")
sheet = spreadsheet.get_worksheet(0) 

# 3. Leitura Bruta
dados_brutos = sheet.get_all_values()

# 4. Extração da Mensagem (Célula A2)
try:
    mensagem_mestra = dados_brutos[1][0]
    print(f"Mensagem carregada: {mensagem_mestra}")
except:
    mensagem_mestra = "Olá {{nome}}"

# 5. Configuração da API (Ajustado aqui!)
API_KEY = '2769760D38ED-42D2-BF1E-EE417FAAF255'
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"

# 6. Percorrer os contatos (Começa da linha 2)
for i, linha in enumerate(dados_brutos[1:], start=2):
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
            "text": msg_final
        }
        headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}
        
        print(f"Linha {i}: Enviando para {nome} ({telefone})...")
        try:
            res = requests.post(API_URL, json=payload, headers=headers)
            print(f"Status: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Erro na linha {i}: {e}")
        
        time.sleep(10) # Delay entre envios

print("🚀 Finalizado!")
