import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os

# 1. Autenticação
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 2. Abrir a planilha e a aba "Página1"
spreadsheet = client.open("BroadcastWhatsapp")
sheet = spreadsheet.get_worksheet(0) 

# 3. Pegar a Mensagem (Célula A2)
# Como você disse, o texto que você altera pelo celular fica aqui.
mensagem_mestra = sheet.acell('A2').value

# 4. Pegar os Contatos (A partir da Linha 3)
# Pegamos todos os valores da planilha como uma lista de listas
todos_os_valores = sheet.get_all_values()

# O cabeçalho real (títulos) está na linha 1 (índice 0)
# Os contatos reais começam na linha 3 (índice 2)
contatos = todos_os_valores[2:] 

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

print(f"Iniciando disparos com a mensagem de A2...")

for linha in contatos:
    nome = linha[0]      # Coluna A (Nome)
    telefone_bruto = linha[1] # Coluna B (Telefone)
    
    # Limpa o telefone (pega apenas números)
    telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))
    
    if nome and len(telefone) >= 10:
        # Personaliza a mensagem trocando {{nome}} pelo nome da coluna A
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
            if response.status_code in [200, 201]:
                print("✅ Sucesso")
            else:
                print(f"❌ Erro API: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        # Delay de 15 segundos entre cada mensagem
        time.sleep(15)

print("🚀 Processo concluído!")
    time.sleep(15)
