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
spreadsheet = client.open("BroadcastWhatsapp")
sheet = spreadsheet.get_worksheet(0) 

# 3. Pegar a Mensagem (Célula A2)
mensagem_mestra = sheet.acell('A2').value

# 4. Pegar os Contatos (Colunas B e C)
# Lemos todos os valores da aba
todos_os_valores = sheet.get_all_values()

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

print(f"Iniciando disparos...")

# Começamos a ler da linha 2 (índice 1) para pegar os dados abaixo dos títulos B1 e C1
for linha in todos_os_valores[1:]:
    # Na sua estrutura: Coluna B é índice 1 (Nome), Coluna C é índice 2 (Telefone)
    if len(linha) < 3:
        continue
        
    nome = linha[1]      
    telefone_bruto = linha[2]
    
    # Limpa o telefone (apenas números)
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
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Erro: {e}")
        
        # Intervalo de segurança
        time.sleep(15)

print("🚀 Processo concluído!")
