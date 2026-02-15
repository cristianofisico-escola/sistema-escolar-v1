import gspread
from google.oauth2.service_account import Credentials

ARQUIVO_CHAVE = 'credenciais-ocorrencias-profs.json'
NOME_PLANILHA = "Ocorrencias_profs_01" 
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def conectar_planilha():
    creds = Credentials.from_service_account_file(ARQUIVO_CHAVE, scopes=SCOPE)
    return gspread.authorize(creds).open(NOME_PLANILHA)

def buscar_dados():
    doc = conectar_planilha()
    profs = doc.worksheet("Pag_Professores").col_values(1)[1:]
    motivos = ["Indisciplina", "Tarefa", "Ensalamento", "Outros"]
    
    # Busca turmas na aba Pag_Turmas
    lista_turmas = doc.worksheet("Pag_Turmas").col_values(1)[1:]
    lista_turmas = [t.strip().upper() for t in lista_turmas if t.strip()]

    # Busca alunos e limpa cada coluna (Trim) antes de montar o nome
    aba_a = doc.worksheet("Pag_Alunos").get_all_values()[1:]
    lista_alunos = []
    for r in aba_a:
        if len(r) >= 3:
            t = str(r[0]).strip().upper()
            n = str(r[1]).strip()
            nome = str(r[2]).strip()
            # Montagem idêntica ao que você tem gravado
            nome_completo = f"{t} - {n} - {nome}"
            lista_alunos.append([t, nome_completo])
            
    return profs, motivos, lista_turmas, lista_alunos

def salvar_registro(linha):
    conectar_planilha().worksheet("Pag_Ocorrencias").append_row(linha)
    return True

def listar_registros():
    aba = conectar_planilha().worksheet("Pag_Ocorrencias")
    dados = aba.get_all_values()
    if len(dados) <= 1: return []
    # Retorna registros ativos (Coluna G / índice 6)
    return [r for r in dados[1:] if len(r) >= 7 and r[6].strip().upper() != "INATIVO"]

def atualizar_registro(indice_id, novos_dados):
    aba = conectar_planilha().worksheet("Pag_Ocorrencias")
    todos = aba.get_all_values()[1:]
    # Mapeia apenas as linhas que não são "Inativas" para achar o índice real na planilha
    mapeamento = [i+2 for i, r in enumerate(todos) if len(r) >= 7 and r[6].strip().upper() != "INATIVO"]
    aba.update(f"A{mapeamento[indice_id]}:G{mapeamento[indice_id]}", [novos_dados])
    return True

def desativar_registro(indice_id):
    aba = conectar_planilha().worksheet("Pag_Ocorrencias")
    todos = aba.get_all_values()[1:]
    mapeamento = [i+2 for i, r in enumerate(todos) if len(r) >= 7 and r[6].strip().upper() != "INATIVO"]
    aba.update_cell(mapeamento[indice_id], 7, "Inativo")
    return True
