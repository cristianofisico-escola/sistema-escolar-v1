from flask import Flask, render_template, request, jsonify
import database
from datetime import datetime, timedelta

app = Flask(__name__)

# --- FUNÇÃO DE LIMPEZA (Blindagem de espaços) ---
def limpar_nome(nome):
    """ Transforma '8A - 2 - NOME' em '8A-2-NOME' """
    if not nome:
        return ""
    return nome.replace(" - ", "-").strip()

def hora_brasilia():
    # Usando utcnow() conforme seu original, mas corrigindo para o padrão atual se necessário
    return (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M')

@app.route('/')
def index():
    profs, motivos, l_turmas, l_alunos = database.buscar_dados()
    # Limpa os nomes na carga do dicionário de turmas
    turmas_dict = {t: [limpar_nome(a[1]) for a in l_alunos if a[0] == t] for t in l_turmas}
    return render_template('index.html', dados={"professores": profs, "motivos": motivos, "turmas": turmas_dict})

@app.route('/consultar')
def consultar():
    regs = database.listar_registros()
    _, motivos, l_turmas, l_alunos = database.buscar_dados()
    # Limpa os nomes na carga do dicionário de turmas para o modal
    turmas_dict = {t: [limpar_nome(a[1]) for a in l_alunos if a[0] == t] for t in l_turmas}
    return render_template('consulta.html', registros=regs, turmas=turmas_dict, lista_motivos=motivos)

@app.route('/gravar', methods=['POST'])
def gravar():
    alunos = request.form.getlist('alunos')
    # Limpa cada aluno individualmente antes de juntar em uma string
    alunos_limpos = [limpar_nome(a) for a in alunos]
    
    linha = [
        hora_brasilia(), 
        request.form.get('professor'), 
        request.form.get('turma'), 
        request.form.get('motivo'), 
        ",".join(alunos_limpos), # Salva sem espaços após a vírgula
        request.form.get('descricao'), 
        "Ativo"
    ]
    database.salvar_registro(linha)
    return jsonify({"status": "sucesso"})

@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    alunos = request.form.getlist('alunos')
    # Limpa cada aluno individualmente na edição
    alunos_limpos = [limpar_nome(a) for a in alunos]
    
    linha = [
        request.form.get('data_original'), 
        request.form.get('professor'), 
        request.form.get('turma'), 
        request.form.get('motivo'), 
        ",".join(alunos_limpos), # Salva sem espaços após a vírgula
        request.form.get('descricao'), 
        "Ativo"
    ]
    database.atualizar_registro(id, linha)
    return jsonify({"status": "sucesso"})

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    database.desativar_registro(id)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    # Adicionei host='0.0.0.0' para garantir que o Codespaces sempre consiga expor a porta corretamente
    app.run(debug=True, host='0.0.0.0', port=5000)
    