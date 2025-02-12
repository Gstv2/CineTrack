from flask import Flask, render_template, flash, request, redirect, url_for
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

Base.metadata.create_all(engine)

@app.route('/')
def index():
    check_tables_exist(engine)
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
    filmes_recomendados = recomendar_filme()
    preferences = recomendarFilmes(user.email)
    preferences_id = listaPreferencias(user.email)
    combined_preferences = [
        {"preference": preference, "preference_id": preference_id}
        for preference, preference_id in zip(preferences, preferences_id)
    ]

    return render_template("home.html", combined_preferences=combined_preferences, filmes_recomendados=filmes_recomendados, user=user, filmes=filmes, filmes_recentes=filmes_recentes, filmes_por_genero=filmes_por_genero)

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
        if loginUser(email, senha):
            return redirect(url_for('home'))  # Redireciona para a home se o login for bem-sucedido
        else:
            flash("Usuário ou senha incorreta", "danger")  # Flash para exibir mensagem de erro
            return redirect(url_for('login'))  # Redireciona de volta ao login

@app.route('/fazer_logout')

@login_required
def fazer_logout():
    logoutUser()  # Remove o id do usuário da sessão
    return redirect(url_for('login'))  # Redireciona para a página inicial após a criação


@app.route('/Filmes')
@login_required
def filmes():
    user = buscarUser()
    # Obtendo os parâmetros da query string
    generos = request.args.get("genero", "")
    generos = generos.split(",") if generos else []  # Garante que seja uma lista
    generos = [g for g in generos if g]  # Remove valores vazios

    nome_filme = request.args.get("nome", "").strip()

    # Aplica os filtros
    if "todos" in generos:
        filmes_filtrados = listarFilmes()
    elif generos:  # Verifica se a lista de gêneros não está vazia
        filmes_filtrados = buscarFilmesPorGenero(generos)
    elif nome_filme:  # Se o nome for informado, faz o filtro
        filmes_filtrados = buscarFilmesPorNome(nome_filme)
    else:  # Caso contrário, lista todos os filmes
        filmes_filtrados = listarFilmes()

    filmes_filtrados = filmes_filtrados if filmes_filtrados else []
    preferences = recomendarFilmes(user.email)
    preferences_id = listaPreferencias(user.email)
    combined_preferences = [
        {"preference": preference, "preference_id": preference_id}
        for preference, preference_id in zip(preferences, preferences_id)
    ]
    return render_template("Filmes.html", combined_preferences = combined_preferences, user=user, filmes_filtrados=filmes_filtrados, preferences = preferences) 

@app.route('/adicionar_filme', methods=['POST'])

@login_required
def adicionar_filme():
    nome = request.form['nome']
    descricao = request.form['descricao']
    ano = request.form['ano']
    genero = request.form['genero']
    imagem = request.files.get('imagem')  # Obtenha o arquivo de imagem

    adicionarFilme(nome, descricao, ano, genero, imagem)
    return redirect(url_for('filmes'))


@app.route('/filtrar_por_genero', methods=['POST'])
@login_required
def filtrar_por_genero():
    """Redireciona para a página de filmes com o filtro de gênero aplicado."""
    generos = request.form.getlist("genero")
    generos = [g for g in generos if g]  # Remove valores vazios, caso o campo tenha sido enviado vazio
    return redirect(url_for("filmes", genero=",".join(generos)))  # Passa os gêneros como query string

@app.route('/filtrar_por_nome', methods=['POST'])
@login_required
def filtrar_por_nome():
    """Redireciona para a página de filmes com o filtro de nome aplicado."""
    nome_filme = request.form.get("nome", "").strip()
    return redirect(url_for("filmes", nome=nome_filme))  # Passa o nome como query string

# Rota para remover um filme
@app.route('/remover_filme/<int:filme_id>', methods=['POST'])

@login_required
def remover_filme(filme_id):
    if removerFilme(filme_id):
        flash(f"Filme {filme_id} removido com sucesso.", "success")
    else:
        flash("Filme não encontrado.", "danger")
    return redirect(url_for('filmes'))  # Redireciona para a página principal

@app.route('/adicionar_preferencia', methods=['POST'])

@login_required
def adicionar_preferencia():
    user = buscarUser()
    genero = request.form.get("genero")
    
    adicionarPreferencias(user.email, genero)

    # Após adicionar a preferência, você pode redirecionar para a página desejada ou retornar um JSON
    return redirect(request.referrer) # Redireciona para a página inicial ou outra página

@app.route('/remover_preferencia/<int:preferencia_id>', methods=['POST'])

@login_required
def remover_preferencia(preferencia_id):
    # Tente remover a preferência com o id fornecido
    if removerPreferencia(preferencia_id):
        flash(f"Preferência {preferencia_id} removida com sucesso.", "success")
    else:
        flash("Preferência não encontrada.", "danger")
    
    return redirect(request.referrer)  # Redireciona para a página principal


@app.route('/recomendar_filme', methods=['POST'])

@login_required
def recomendar_filme():
    user = buscarUser()
    generos_preferidos = [preferencia.genero for preferencia in listaPreferencias(user.email)]
    filmes_recomendados = db_session.query(Filmes).filter(Filmes.genero.in_(generos_preferidos)).all()

    return filmes_recomendados


@app.route('/avaliar_filme/<int:filme_id>', methods=['POST'])

@login_required
def avaliar_filme(filme_id):
    user = buscarUser()
    usuario_id = user.email  # Assumindo que você usa o email para identificar o usuário
    avaliacao = request.form.get('rating')  # Obtendo a avaliação enviada pelo usuário (de 1 a 5)

    # Verifica se uma avaliação foi enviada
    if avaliacao:
        adicionar_avaliacao(Avaliacao, usuario_id, filme_id, int(avaliacao))
        # Atualizar a classificação média do filme
        filme = db_session.query(Filmes).get(filme_id)
        if filme:
            # Calcular a média das avaliações
            media = obter_media_avaliacoes(Avaliacao, filme_id)
            filme.classificacao = media  # Atualiza o atributo classificacao com a média
            db_session.commit()
    
    # Redireciona para a página de onde veio (para o modal se fechar)
    return redirect(request.referrer)



if __name__ == '__main__':
    # db_session.commit()
    app.run(debug=True)