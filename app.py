from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
import requests
from datetime import datetime, timedelta
from pywebpush import webpush, WebPushException
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Permitir HTTP para desenvolvimento local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações do Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Configurações Web Push
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')
VAPID_CLAIM_EMAIL = os.getenv('VAPID_CLAIM_EMAIL')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Cliente OAuth
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return render_template('welcome.html')

@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["name"]
        picture = userinfo_response.json()["picture"]
        
        user = User.query.filter_by(email=users_email).first()
        if not user:
            user = User(
                email=users_email,
                name=users_name,
                profile_pic=picture
            )
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return "User email not verified by Google.", 400

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rotas para medicamentos e alarmes
@app.route('/novo-medicamento', methods=['GET', 'POST'])
@login_required
def novo_medicamento():
    return render_template('novo_medicamento.html')

@app.route('/novo-alarme', methods=['GET', 'POST'])
@login_required
def novo_alarme():
    return render_template('novo_alarme.html')

@app.route('/estoque')
@login_required
def estoque():
    return render_template('estoque.html')

@app.route('/adesao')
@login_required
def adesao():
    # Buscar registros de medicação do usuário
    registros = []  # Aqui você deve buscar os registros do banco de dados
    
    # Criar gráfico com plotly se houver dados
    grafico = None
    if registros:
        import plotly.express as px
        import pandas as pd
        
        # Criar DataFrame com os dados
        # Aqui você deve adaptar de acordo com a estrutura dos seus dados
        df = pd.DataFrame(registros)
        
        # Criar gráfico
        fig = px.line(df, title='Adesão ao Tratamento')
        grafico = fig.to_html(full_html=False)
    
    return render_template('adesao.html', registros=registros, grafico=grafico)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
