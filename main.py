import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import os
import json

# ============================================================
# 1. Autenticação via variável de ambiente (seguro para CI/CD)
# ============================================================
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# Lê as credenciais de uma variável de ambiente (Secret no GitHub)
credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
if not credentials_json:
    raise EnvironmentError("Variável GOOGLE_CREDENTIALS não encontrada.")

credentials_dict = json.loads(credentials_json)
creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
client = gspread.authorize(creds)

# ============================================================
# 2. Abrir a planilha
# ============================================================
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "1kIo_svj3RHOHjiOQ7hULX-Vp2o4hfvHLRhN_U7xxcD8")

try:
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.get_worksheet(0)
except Exception as e:
    raise ConnectionError(f"Erro ao abrir a planilha: {e}")

# ============================================================
# 3. Leitura dos dados
# ============================================================
dados_brutos = sheet.get_all_values()

if len(dados_brutos) < 2:
    raise ValueError("A planilha está vazia ou sem dados suficientes.")

# ============================================================
# 4. Extração da Mensagem (Célula A2) — linha índice 1, coluna 0
# ============================================================
try:
    mensagem_mestra = dados_brutos[1][0].strip()
    if not mensagem_mestra:
        raise ValueError("Mensagem vazia na célula A2.")
    print(f"✅ Mensagem carregada: {mensagem_mestra}")
except Exception as e:
    print(f"⚠️ Erro ao carregar mensagem: {e}. Usando mensagem padrão.")
    mensagem_mestra = "Olá {{nome}}, tudo bem?"

# ============================================================
# 5. Configuração da API via variável de ambiente
# ============================================================
API_KEY = os.environ.get("2769760D38ED-42D2-BF1E-EE417FAAF255")
if not API_KEY:
    raise EnvironmentError("Variável EVOLUTION_API_KEY não encontrada.")

API_URL = os.environ.get(
    "EVOLUTION_API_URL",
    "https://eudmarly-evolution-api.4eivnx.easypanel.host/message/sendText/WhatsappBroadcast"
)

headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}

# ============================================================
# 6. Percorrer contatos — pula linha 2 (mensagem) e cabeçalho
#    Estrutura: linha 1 = cabeçalho, linha 2 = mensagem (col A)
#    Contatos começam na linha 3 (índice 2)
# ============================================================
contatos = dados_brutos[2:]  # ← CORREÇÃO: antes começava em [1:] e reprocessava a mensagem

enviados = 0
erros = 0

for i, linha in enumerate(contatos, start=3):
    if len(linha) < 3:
        print(f"⚠️ Linha {i}: dados insuficientes, pulando.")
        continue

    nome = linha[1].strip()
    telefone_bruto = linha[2].strip()

    # Limpa o telefone (remove decimais e caracteres não numéricos)
    telefone = "".join(filter(str.isdigit, str(telefone_bruto).split('.')[0]))

    # Validação: mínimo 12 dígitos (55 + DDD + número)
    if not nome:
        print(f"⚠️ Linha {i}: nome vazio, pulando.")
        continue

    if len(telefone) < 12:
        print(f"⚠️ Linha {i}: telefone inválido '{telefone}' ({len(telefone)} dígitos), pulando.")
        continue

    msg_final = mensagem_mestra.replace("{{nome}}", nome)

    payload = {
        "number": telefone,
        "text": msg_final
    }

    print(f"📤 Linha {i}: Enviando para {nome} ({telefone})...")

    try:
        res = requests.post(API_URL, json=payload, headers=headers, timeout=30)  # ← timeout adicionado
        print(f"   Status: {res.status_code} - {res.text[:100]}")

        if res.status_code == 200:
            enviados += 1
        else:
            print(f"   ⚠️ Resposta inesperada na linha {i}.")
            erros += 1

    except requests.exceptions.Timeout:
        print(f"   ❌ Linha {i}: Timeout na requisição.")
        erros += 1
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Linha {i}: Erro de conexão - {e}")
        erros += 1
    except Exception as e:
        print(f"   ❌ Linha {i}: Erro inesperado - {e}")
        erros += 1

    time.sleep(10)

# ============================================================
# 7. Relatório final
# ============================================================
print(f"\n🚀 Finalizado! Enviados: {enviados} | Erros: {erros} | Total processado: {enviados + erros}")
