import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os

# 1. Autenticação (O arquivo credentials.json deve estar no seu GitHub)
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 2. Abrir a planilha
# Substitua pelo nome exato do seu arquivo no Google Sheets
#spreadsheet = client.open("BroadcastWhatsapp")
spreadsheet = cliente.open_by_key("1kIo_svj3RHOHjiOQ7hULX-Vp2o4hfvHLRhN_U7xxcD8")
sheet = spreadsheet.get_worksheet(0) 

# 3. Pega a Mensagem (Célula A2)
mensagem_mestra = sheet.acell('A2').value

# 4. Pega os Contatos (Colunas B e C)
# Lemos todos os registros; o gspread identificará "Nome" e "Telefone (DDD)" como cabeçalhos
records = sheet.get_all_records()

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

print("Iniciando disparos via Python...")

for row in records:
    nome = row.get('Nome')
    telefone_bruto = row.get('Telefone (DDD)')
    
    # Limpa o telefone (remove .0, espaços e traços)
    if telefone_bruto:
        telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))
        
        # Só envia se tiver nome e um número de telefone plausível
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
                print(f"Erro na conexão: {e}")
            
            # Delay de segurança (15 segundos) para evitar banimento
            time.sleep(15)

print("🚀 Processo concluído com sucesso!")
