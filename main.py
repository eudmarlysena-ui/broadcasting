import gspread
from google.oauth2.service_account import Credentials
import requests
import os

# Autenticação
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# Abre a planilha
sheet = client.open("BroadcastWhatsapp").get_worksheet(0)

# Pega a mensagem (A2) e os contatos (B2 em diante)
mensagem_base = sheet.acell('A2').value
contatos = sheet.get_all_records() # Ele usa a linha 1 como cabeçalho automaticamente

for c in contatos:
    nome = c.get('Nome')
    fone = str(c.get('Telefone (DDD)')).split('.')[0] # Limpa o número
    
    if nome and fone:
        msg = mensagem_base.replace("{{nome}}", nome)
        # Envio para Evolution API
        requests.post(
            "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast",
            json={"number": fone, "text": msg},
            headers={"apikey": os.environ['2769760D38ED-42D2-BF1E-EE417FAAF255']}
        )
    
    # Delay de segurança entre mensagens (15 segundos)
    time.sleep(15)
