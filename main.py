import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os

# 1. Autenticação
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 2. Abrir a planilha (Substitua pelo seu ID)
spreadsheet = client.open_by_key("1kIo_svj3RHOHjiOQ7hULX-Vp2o4hfvHLRhN_U7xxcD8")
sheet = spreadsheet.get_worksheet(0) 

# 3. Pegar a Mensagem (Célula A2)
try:
    mensagem_mestra = sheet.acell('A2').value
    if not mensagem_mestra:
        print("Aviso: Célula A2 está vazia.")
        mensagem_mestra = "Olá {{nome}}"
except Exception as e:
    print(f"Erro ao ler A2: {e}")
    mensagem_mestra = "Olá {{nome}}"

# 4. Pegar os Contatos (Colunas B e C)
# Lemos todos os valores para processar as colunas B (índice 1) e C (índice 2)
todos_os_valores = sheet.get_all_values()

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

print(f"Iniciando disparos...")

# Começamos da linha 2 (índice 1) para pular os títulos B1 e C1
for linha in todos_os_valores[1:]:
    # Garante que a linha tem colunas suficientes (Coluna C é índice 2)
    if len(linha) < 3:
        continue
        
    nome = linha[1]           # Coluna B
    telefone_bruto = linha[2] # Coluna C
    
    # Limpa o telefone (apenas números)
    telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))
    
    if nome and len(telefone) >= 10:
        # Personaliza trocando o marcador {{nome}} pelo nome da coluna B
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
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Erro: {e}")
        
        # Delay de segurança anti-bloqueio
        time.sleep(15)

print("🚀 Processo concluído!")
