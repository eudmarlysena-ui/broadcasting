import requests
import pandas as pd
import time

# Configurações da Evolution API
API_URL = "https://seu-host.com/message/sendText/WhatsappBroadcast"
API_KEY = "SUA_API_KEY_AQUI"

# 1. Carregar dados (Exemplo usando CSV ou Excel do GitHub)
# Para usar Google Sheets direto no Python, recomendo a lib 'gspread'
df_contatos = pd.read_csv('contatos.csv') 
mensagem_base = "Olá {{nome}}, esta é uma mensagem via Python!"

def enviar_mensagem(numero, texto):
    payload = {
        "number": str(numero),
        "text": texto,
        "delay": 1200,
        "linkPreview": True
    }
    headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(API_URL, json=payload, headers=headers)
    return response.status_code

# Loop de envio
for index, row in df_contatos.iterrows():
    # Personaliza a mensagem
    msg_personalizada = mensagem_base.replace("{{nome}}", row['Nome'])
    
    print(f"Enviando para {row['Nome']}...")
    status = enviar_mensagem(row['Telefone'], msg_personalizada)
    
    if status == 201 or status == 200:
        print("Sucesso!")
    else:
        print(f"Erro no envio: {status}")
    
    # Delay de segurança entre mensagens (15 segundos)
    time.sleep(15)
