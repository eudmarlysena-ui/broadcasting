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
mensagem_mestra = sheet.acell('A2').value

# 4. Pegar os Contatos (Colunas B e C)
# Lemos todos os valores da aba para processar as colunas
todos_os_valores = sheet.get_all_values()

# Configuração Evolution API
API_URL = "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
API_KEY = os.environ.get('2769760D38ED-42D2-BF1E-EE417FAAF255')

print(f"Mensagem carregada: {mensagem_mestra[:30]}...")

# O loop começa da linha 2 (índice 1) onde estão os primeiros dados
for linha in todos_os_valores[1:]:
    # Na sua planilha: 
    # linha[0] é a Coluna A (onde está a mensagem ou vazio)
    # linha[1] é a Coluna B (Nome)
    # linha[2] é a Coluna C (Telefone)
    
    if len(linha) < 3:
        continue
        
    nome = linha[1]
    telefone_bruto = linha[2]
    
    # Limpa o telefone (apenas números)
    telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))
    
    # Validação: só envia se houver nome e telefone preenchidos
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
            print(f"Erro no envio: {e}")
        
        # Delay de segurança (15 segundos)
        time.sleep(15)

print("🚀 Processo concluído!")
