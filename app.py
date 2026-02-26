from flask import Flask, make_response, render_template, request, redirect
import mysql.connector
from flask import flash
from flask import session
from forms import LoginForm, CadastroCandidatoForm, CadastroOngForm
from functools import wraps

#Essa função garante que certas rotas só sejam acessadas por usuários logados.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect('/escolha')
        return f(*args, **kwargs)
    return decorated_function
#####################################

#Configuração básica do Flask, incluindo uma chave secreta para sessões.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Cincity09!'
app.config["TEMPLATES_AUTO_RELOAD"] = True

###############################################

# Conexão com o banco de dados MySQL
mydb = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='formulario'
)

@app.route('/')#Rota inicial
@login_required # acessar essa rota exige login
def home():
    return render_template('/escolha.html')

############################################################

################################################
#Rota inicial:
@app.route('/escolha')
def escolha():
    return render_template('escolha.html')

##################################################################
#Verifica as credenciais do usuário e atualiza a sessão.


########################################################################
# novas rotas login candidato:
@app.route('/login_candidato', methods=['GET', 'POST'])
def login_candidato():
    form = LoginForm() 
    if form.validate_on_submit(): 
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM logins WHERE login = %s AND senha = %s",
                         (form.username.data, form.password.data))
        user = mycursor.fetchone()

        if user:
            session['logged_in'] = True
            session['tipo'] = 'candidato'
            flash('Login candidadato bem-sucedido!', 'success')
            return redirect('/')
        
        else:
            flash('Usuario ou senha incorretos.', 'danger')
            return render_template('login_candidato.html', form=form)
        
#sempre retorna o template no GET
    return render_template('login_candidato.html', form=form)
        
###############################################################################
# login ONG:
@app.route('/login_ong', methods=['GET', 'POST'])
def login_ong():
    form = LoginForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM login_ong WHERE login = %s AND senha = %s", 
                         (form.username.data, form.password.data))
        user = mycursor.fetchone()

        if user:
            session['logged_in'] = True
            session['tipo'] = 'ong'
            flash('Login ONG bem-sucedido!', 'success')
            return redirect('/')
        
        else:
            flash('Usuario ou senha incorretos.', 'danger')
            return render_template('login_ong.html', form=form)
        
        #sempre retorna o template no GET
    return render_template('login_ong.html', form=form)
        


############################################################################

#Rotas Insere novos registros no banco de dados.
@app.route('/cadastro_candidato', methods=['GET', 'POST'])
def cadastro_candidato():
    form = CadastroCandidatoForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()
        mycursor.execute( 
            "INSERT INTO logins (nome_candidato, login, senha) VALUES (%s, %s, %s)", 
                      (form.nome.data, form.login.data, form.senha.data) 
        )
        mydb.commit()
        flash('CAndidato cadastrado com sucesso!', 'success')
        return redirect('/login_candidato')
    return render_template('cadastro_candidato.html', form=form)


@app.route('/cadastro_ong', methods=['GET', 'POST'])
def cadastro_ong():
    form = CadastroOngForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()
        mycursor.execute(
            "INSERT INTO login_ong (nome_ong, login, senha) VALUES (%s, %s, %s)", 
            (form.nome.data, form.login.data, form.senha.data)
        )
        mydb.commit()
        flash('ONG cadastrada com sucesso!', 'success')
        return redirect('/login_ong')
    return render_template('cadastro_ong.html', form=form)

################################################################################## 
      
      

#Recupera dados do banco de dados e os exibe.
@app.route('/dados', methods=['GET'])
def get_dados():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM logins")
    meus_dados = mycursor.fetchall()

    dados = []
    for dado in meus_dados:
        dados.append(
            {
                'id': dado[0],
                'nome_candidato': dado[1],
                'login': dado[2],
                'senha': dado[3]
            }
        )

    return make_response(
        render_template('registros.html', dados=dados)
    )
#################################################################






    

      # Redirecione para '/dados' para exibir a tabela atualizada

################################################################################

#Exclui registros do banco de dados.
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM logins WHERE id = %s", (id,))
    mydb.commit()
    return redirect('/dados')
#########################################

#Executa o aplicativo no modo de depuração.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
