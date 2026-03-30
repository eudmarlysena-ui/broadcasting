import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os

# 1. Autenticação
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 2. Abrir a planilha pelo ID (mais seguro)
# O ID é aquele código longo na URL da sua planilha
spreadsheet = client.open_by_key("1kIo_svj3RHOHjiOQ7hULX-Vp2o4hfvHLRhN_U7xxcD8")
sheet = spreadsheet.get_worksheet(0) 

# 3. Pegar a Mensagem (Vamos definir que ela ficará na célula B2 para facilitar)
# Você escreve a mensagem na B2, e os contatos começam na linha 3
mensagem_mestra = sheet.acell('B2').value

# 4. Pegar os Contatos (A partir da linha 3)
todos_os_valores = sheet.get_all_values()
# todos_os_valores[2:] pula as duas primeiras linhas (títulos e mensagem)
contatos = todos_os_valores[2:] 

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

print(f"Lida mensagem da célula B2: {mensagem_mestra}")

for linha in contatos:
    # Como a coluna A está vazia:
    # linha[0] é a Coluna A (Vazia)
    # linha[1] é a Coluna B (Nome)
    # linha[2] é a Coluna C (Telefone)
    
    if len(linha) < 3:
        continue
        
    nome = linha[1]
    telefone_bruto = linha[2]
    
    # Limpa o telefone
    telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))
    
    if nome and len(telefone) >= 10:
        msg_final = mensagem_mestra.replace("{{nome}}", str(nome))
        
        payload = {
            "number": telefone,
            "text": msg_final,
            "delay": 1200
        }
        headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}
        
        print(f"Enviando para {nome} ({telefone})...")
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            print(f"Resultado: {response.status_code}")
        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(15)

print("🚀 Fim do envio!")
