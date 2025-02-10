from flask import jsonify
from flask import Flask, render_template, flash, request, redirect, url_for
from sqlalchemy.inspection import inspect
from functools import wraps
from models.base import *
from models.User import *
from models.Filmes import *
from models.preferencias import *
from models.avaliacao import *
import os

# # Resto do código sem importações circulares
app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return redirect('login')

# Decorador para verificar o login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@login_required
def home():
    filmes_recentes = db_session.query(Filmes).order_by(Filmes.created_at.desc()).limit(10).all()
    filmes = listarFilmes()
    
    # Buscar filmes por gênero
    generos = db_session.query(Filmes.genero).distinct().all()
    filmes_por_genero = {
        genero[0]: db_session.query(Filmes).filter(Filmes.genero == genero[0]).limit(10).all()
        for genero in generos
    }
    user = buscarUser()
    return render_template("home.html", user=user,filmes = filmes, filmes_recentes=filmes_recentes, filmes_por_genero=filmes_por_genero)

@app.route('/login')
def login():
    return render_template("login.html") 

@app.route('/register')
def register():
    return render_template("register.html") 

@app.route('/criar_user', methods=['GET', 'POST'])
def criar_user():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']   
        senha = request.form['senha']

        # Chamar a função para adicionar o usuário
        adicionarUser(email=email, nome=nome, senha=senha)

        return redirect(url_for('home'))  # Redireciona para a página inicial após a criação

    return render_template('home.html')  # Exibe o formulário para criação


@app.route('/fazer_login', methods=['POST'])
def fazer_login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        loginUser(email, senha)

        return redirect(url_for('home'))  # Redireciona para a página inicial após a criação

    return render_template('home.html')  # Exibe o formulário para criação

@app.route('/fazer_logout')
@login_required
def fazer_logout():
    logoutUser()  # Remove o id do usuário da sessão
    return redirect(url_for('login'))  # Redireciona para a página inicial após a criação


@app.route('/Filmes')
@login_required
def filmes():
    user = buscarUser()
    filmes = listarFilmes()
    # Filmes = listarFilmes()
    return render_template("Filmes.html", user=user, filmes=filmes) 

@app.route('/adicionar_filme', methods=['POST'])
@login_required
def adicionar_filme():
    nome = request.form['nome']
    descricao = request.form['descricao']
    ano = request.form['ano']
    genero = request.form['genero']
    imagem = request.files.get('imagem')  # Obtenha o arquivo de imagem

    adicionarFilme(nome, descricao, ano, genero, imagem)
    return redirect(url_for('Filmes'))

@app.route('/filtrar_filmes', methods=['POST'])
@login_required
def filtrar_filmes():
    user = buscarUser()
    generos = request.form.getlist("genero")  # Pega os gêneros marcados no formulário
    nome_filme = request.form.get("nome", "").strip()  # Nome do filme (caso tenha um input de nome)

    if generos and "todos" not in generos:
        filmes_filtrados = buscarFilmesPorGenero(generos)
    elif nome_filme:
        filmes_filtrados = buscarFilmesPorNome(nome_filme)
    else:
        filmes_filtrados = listarFilmes()  # Se nada for passado, lista todos

    return render_template("Filmes.html", filmes=filmes_filtrados, user=user)



# # Função para adicionar um novo KanbanBoard
# @app.route('/adicionar_kanban', methods=['POST'])
# @login_required
# def adicionar_kanban():
#     data = request.get_json()
#     if data:
#         name = data.get('name')
#         description = data.get('description')
        
#     try:
#         # Certifique-se de que o usuário autenticado é o dono do KanbanBoard
#         user_email = session.get('user_email')
#         user = db_session.query(User).filter_by(email=user_email).first()

#         if user:
#             # Crie um novo KanbanBoard para o usuário
#             new_kanban = KanbanBoard(name=name, description=description, user=user)
#             db_session.add(new_kanban)
#             db_session.commit()
#             # Feche a sessão após obter os resultados
#             db_session.close()
#             return jsonify({'success': True})
#         else:
#             return jsonify({'error': 'Usuário não encontrado.'}), 404
#     except Exception as e:
#         return jsonify({'error': 'Erro ao adicionar o KanbanBoard.'}), 500
    

# @app.route('/edit_kanban/<int:kanban_id>', methods=['PUT'])
# @login_required
# def edit_kanban(kanban_id):
#     try:
#         data = request.get_json()
#         if data:
#             newname = data.get('newname')
#             newDescription = data.get('newDescription')

#             # Busque o quadro do Kanban pelo ID
#             kanban = db_session.query(KanbanBoard).filter_by(id=kanban_id).first()

#             if kanban:
#                 # Atualize os dados do quadro com os novos valores
#                 kanban.name = newname
#                 kanban.description = newDescription

#                 # Commit as mudanças no banco de dados

#                 db_session.commit()

#                 return jsonify({'message': 'Quadro atualizado com sucesso!'})
#             else:
#                 return jsonify({'message': 'Quadro não encontrado.'}), 404
#     except Exception as e:
#         # Lide com exceções, se necessário
#         db_session.rollback()
#         return jsonify({'message': 'Erro ao atualizar o quadro: ' + str(e)}), 500


# @app.route('/remover_kanban/<int:kanban_id>', methods=['DELETE'])
# @login_required
# def remover_kanban(kanban_id):
#     try:
#         # Busque o KanbanBoard pelo ID
#         kanban = db_session.query(KanbanBoard).filter_by(id=kanban_id).first()
        
#         if kanban:
#             tasks = db_session.query(KanbanCard).filter_by(KanbanBoards_id=kanban_id).all()

#             # Exclui cada tarefa associada ao KanbanBoard
#             for task in tasks:
#                 db_session.delete(task)

#             # Exclui todas as tarefas no backlog
#             backlog_tasks = db_session.query(Backlog).filter_by(kanbanboard_id=kanban_id).all()

#             for backlog_task in backlog_tasks:
#                 db_session.delete(backlog_task)
#             # Remova o KanbanBoard
#             db_session.delete(kanban)
#             db_session.commit()
#             return jsonify({'success': True, 'message': 'KanbanBoard removido com sucesso!'})
#         else:
#             return jsonify({'success': False, 'message': 'Nenhum KanbanBoard encontrado para remover.'}), 404
#     except Exception as e:
#         return jsonify({'success': False, 'error': f'Erro ao remover o KanbanBoard: {str(e)}'}), 500



# # Rota para o Kanban
# @app.route("/kanban<int:kanban_id>")
# @login_required
# def kanban(kanban_id):
#     if check_tables_exist(engine):
#         return "Falha na criação das tabelas!"
#     else:
#         user_email = session['user_email']
#         # Abra uma nova sessão para esta visualização
#         db_session = Session()
        
#         try:
#             user = db_session.query(User).filter_by(email=user_email).first()
#             kanban = db_session.query(KanbanBoard).filter_by(user=user, id=kanban_id).first()

#             backlog_tasks = db_session.query(KanbanCard).filter_by(status="backlog", KanbanBoards_id=kanban.id).all()
#             a_fazer_tasks = db_session.query(KanbanCard).filter_by(status="a fazer", KanbanBoards_id=kanban.id).all()
#             em_andamento_tasks = db_session.query(KanbanCard).filter_by(status="em andamento", KanbanBoards_id=kanban.id).all()
#             concluido_tasks = db_session.query(KanbanCard).filter_by(status="concluido", KanbanBoards_id=kanban.id).all()
            

#             return render_template("kanban.html", user=user, kanban=kanban, em_andamento_tasks=em_andamento_tasks, backlog_tasks=backlog_tasks, a_fazer_tasks=a_fazer_tasks, concluido_tasks=concluido_tasks)
#         except Exception as e:
#             # Lide com exceções, se necessário
#             db_session.rollback()
#             return "Erro: " + str(e)
        
        
# # Função para remover uma tarefa
# @app.route('/remover_tarefa/<int:task_id>', methods=['DELETE'])
# @login_required
# def remover_tarefa(task_id):
#     try:
#         kanbancard = db_session.query(KanbanCard).filter_by(id=task_id).first()
#         if kanbancard:
#             db_session.delete(kanbancard)
#             db_session.commit()
#             return jsonify({'message': 'Tarefa removida com sucesso!'})
#         else:
#             return jsonify({'error': 'Tarefa não encontrada.'}), 404
#     except Exception as e:
#         return jsonify({'error': 'Erro ao remover a tarefa.'}), 500
    

    
# @app.route('/adicionar_tarefa', methods=['POST'])
# def adicionar_tarefa():
#     data = request.get_json()
#     if data:
#         title = data.get('title')
#         description = data.get('description')
#         status = data.get('status')
#         kanban_id = data.get('kanban_id')
        
#         # Certifique-se de que o usuário autenticado é o dono do KanbanBoard
#         user_email = session.get('user_email')
#         user = db_session.query(User).filter_by(email=user_email).first()
        
#         # Crie a nova tarefa vinculada ao Kanban do usuário
#         kanban = db_session.query(KanbanBoard).filter_by(user=user, id=kanban_id).first()
#         if kanban:
#             kanbancard = KanbanCard(title=title, description=description, status=status, KanbanBoards_id=kanban.id)
#             db_session.add(kanbancard)
#             db_session.commit()
            
#             return jsonify({'success': True})
#         else:
#             return jsonify({'success': False, 'error': 'KanbanBoard não encontrado para o usuário.'})
    
#     return jsonify({'success': False})

# @app.route('/mover_tarefa/<int:cardId>/<newStatus>', methods=['PUT'])
# @login_required
# def mover_tarefa(cardId, newStatus):
#     try:
#         data = request.get_json()
#         if data:
#             cardId = data.get('cardId')
#             newStatus = data.get('newStatus')

#             kanbancard = db_session.query(KanbanCard).filter_by(id=cardId).first()
#             if kanbancard:
#                 kanbancard.status = newStatus
#                 db_session.commit()
#                 return jsonify({'message': 'Tarefa movida com sucesso!'})
#             else:
#                 return jsonify({'error': 'Tarefa não encontrada.'}), 404
#     except Exception as e:
#         return jsonify({'error': 'Erro ao mover a tarefa.'}), 500

    
# # Defina uma rota para editar uma tarefa existente
# @app.route('/edit_task/<int:cardId>', methods=['PUT'])
# @login_required  # Certifique-se de ter configurado a autenticação do Flask-Login
# def edit_task(cardId):
#     try:
#         data = request.get_json()
#         if data:
#             newTitle = data.get('newTitle')
#             newDescription = data.get('newDescription')

#             # Encontre a tarefa com base no ID
#             kanbancard = db_session.query(KanbanCard).filter_by(id=cardId).first()
            
#             if kanbancard:
#                 # Atualize os dados da tarefa
#                 kanbancard.title = newTitle
#                 kanbancard.description = newDescription
#                 db_session.commit()
#                 return jsonify({'message': 'Tarefa alterada com sucesso!'})
#             else:
#                 return jsonify({'error': 'Tarefa não encontrada.'}), 404
#     except Exception as e:
#         return jsonify({'error': 'Erro ao alterar a tarefa.'}), 500


# # Rota para a página do backlog
# @app.route('/backlog<int:kanban_id>')
# @login_required
# def backlog(kanban_id):
#     if check_tables_exist(engine):
#         return "Falha na criação das tabelas!"
#     else:
#         user_email = session['user_email']
#         user = db_session.query(User).filter_by(email=user_email).first()
#         kanban = db_session.query(KanbanBoard).filter_by(user=user, id=kanban_id).first()

#         # Obtenha as tarefas do backlog
#         backlog_tasks = db_session.query(Backlog).filter_by(kanbanboard_id=kanban_id).all()

#         return render_template("backlog.html", user=user, kanban_id=kanban_id, kanban=kanban, backlog_tasks=backlog_tasks)

    
# # Rota para adicionar uma tarefa ao backlog
# @app.route('/adicionar_tarefa_backlog/<int:kanban_id>', methods=['POST'])
# @login_required
# def adicionar_tarefa_backlog(kanban_id):
#     data = request.get_json()
#     if data:
#         backlog_title = data.get('title')
#         backlog_description = data.get('description')
#         backlog_date = data.get('date')

#         try:
#             # Certifique-se de que o usuário autenticado é o dono do KanbanBoard
#             user_email = session.get('user_email')
#             user = db_session.query(User).filter_by(email=user_email).first()

#             if user:
#                 # Adicionar tarefa ao backlog no banco de dados
#                 backlog_task = Backlog(title=backlog_title, description=backlog_description, date=backlog_date, user=user, kanbanboard_id=kanban_id)
#                 db_session.add(backlog_task)
#                 db_session.commit()
#                 # Obtenha a ID da tarefa após a adição
#                 task_id = backlog_task.id
#                 # Feche a sessão após obter os resultados
#                 db_session.close()
#                 return jsonify({'success': True, 'message': 'Tarefa adicionada com sucesso.', 'task_id': task_id})
#             else:
#                 return jsonify({'error': 'Usuário não encontrado.'}), 404
#         except Exception as e:
#             return jsonify({'error': 'Erro ao adicionar a tarefa ao backlog.'}), 500
#     else:
#         return jsonify({'error': 'Dados inválidos.'}), 400




# # Rota para remover uma tarefa do backlog
# @app.route('/remover_tarefa_backlog/<int:task_id>', methods=['DELETE'])
# @login_required
# def remover_tarefa_backlog(task_id):
#     try:
#         # Busque o KanbanBoard pelo ID
#         print(task_id)
#         task_backlog = db_session.query(Backlog).filter_by(id=task_id).first()
#         if task_backlog:
#             # Remova o KanbanBoard
#             db_session.delete(task_backlog)
#             db_session.commit()
#             return jsonify({'success': True, 'message': 'tarefa do backlog removido com sucesso!'})
#         else:
#             return jsonify({'success': False, 'message': 'Nenhuma tarefa do backlog encontrado para remover.'}), 404
#     except Exception as e:
#         return jsonify({'success': False, 'error': f'Erro ao remover a tarefa do backlog: {str(e)}'}), 500



if __name__ == '__main__':
    # db_session.commit()
    app.run(debug=True)