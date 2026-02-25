from flask import Flask, make_response, render_template, request, redirect
import mysql.connector
from forms import LoginForm
from flask import flash
from flask import session

from functools import wraps

#Essa função garante que certas rotas só sejam acessadas por usuários logados.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect('login')
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

################################################

#Verifica as credenciais do usuário e atualiza a sessão.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM logins WHERE login = %s AND senha = %s", (form.username.data, form.password.data))
        user = mycursor.fetchone()

        if user:
            session['logged_in'] = True
            flash('Login bem-sucedido!', 'success')
            return redirect('/')
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login.html', form=form)

########################################################################


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



@app.route('/')#Rota inicial
@login_required # acessar essa rota exige login
def home():
    return render_template('entrada_registros.html')

############################################################

#Insere novos registros no banco de dados.
@app.route("/entrada", methods=['POST'])
def inserir():
    nome_candidato = request.form.get('nome_candidato')
    login = request.form.get('login')
    senha = request.form.get('senha')
    
    if mydb.is_connected():
        mycursor = mydb.cursor()
        mycursor.execute(f"INSERT INTO logins VALUES (default, '{nome_candidato}', '{login}', '{senha}')")
        mydb.commit()

    return redirect('/dados')  # Redirecione para '/dados' para exibir a tabela atualizada

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
