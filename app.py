import os
import json
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(__file__)
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devsecret123")

DATA_FILE = os.path.join(BASE_DIR, "despesas.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

despesas = []
proximo_id = 1
users = []
categorias_disponiveis = [
    "Moradia",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Lazer",
    "Educação",
    "Cartão",
    "Outros"
]
meses_disponiveis = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

def carregar_usuarios():
    global users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f).get("users", [])

def salvar_usuarios():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, ensure_ascii=False, indent=2)

def username_existe(username):
    return any(u["username"].lower() == username.lower() for u in users)

def criar_usuario(username, senha):
    if not username or not senha:
        return "Usuário e senha são obrigatórios."
    if username_existe(username):
        return "Já existe um usuário com esse nome."
    users.append({
        "username": username,
        "senha": generate_password_hash(senha)
    })
    salvar_usuarios()
    return None

def validar_login(username, senha):
    for usuario in users:
        if usuario["username"].lower() == username.lower():
            return check_password_hash(usuario["senha"], senha)
    return False

def carregar_despesas():
    global despesas, proximo_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            despesas = data.get("despesas", [])
            for despesa in despesas:
                despesa.setdefault("usuario", "")
            proximo_id = data.get("proximo_id", 1)

def salvar_despesas():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"despesas": despesas, "proximo_id": proximo_id}, f, ensure_ascii=False, indent=2)

def adicionar_despesa(descricao, valor, categoria, mes, usuario):
    global proximo_id
    despesa = {
        "id": proximo_id,
        "descricao": descricao,
        "valor": valor,
        "categoria": categoria or "Sem categoria",
        "mes": mes or "Sem mês",
        "usuario": usuario
    }
    despesas.append(despesa)
    proximo_id += 1
    salvar_despesas()
    return despesa

def filtrar_despesas(categoria=None, mes=None, usuario=None):
    resultado = [d for d in despesas if d.get("usuario") == usuario]
    if categoria:
        resultado = [d for d in resultado if d["categoria"] == categoria]
    if mes:
        resultado = [d for d in resultado if d["mes"] == mes]
    return resultado

def agrupar_por_categoria(despesas_filtradas):
    grupos = {}
    for despesa in despesas_filtradas:
        chave = despesa["categoria"] or "Sem categoria"
        grupos.setdefault(chave, []).append(despesa)

    ordem = [c for c in categorias_disponiveis if c in grupos]
    extras = [c for c in grupos if c not in ordem]
    return [
        {"nome": cat, "despesas": grupos[cat], "total": sum(d["valor"] for d in grupos[cat])}
        for cat in ordem + extras
    ]

def gerar_grafico_relatorio(despesas_filtradas):
    df = pd.DataFrame(despesas_filtradas)
    plt.figure(figsize=(14, 6))

    if df.empty:
        plt.text(0.5, 0.5, 'Sem despesas para gerar gráfico',
                 ha='center', va='center', fontsize=16)
        plt.axis('off')
    else:
        if "valor" in df.columns:
            df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
        else:
            df["valor"] = 0.0

        if "mes" in df.columns:
            df["mes"] = df["mes"].astype(str)
        else:
            df["mes"] = ""

        df_mes = df.groupby("mes")["valor"].sum().reindex(
            meses_disponiveis, fill_value=0
        )

        labels = [str(m) for m in df_mes.index]
        x = list(range(len(labels)))
        valores = df_mes.astype(float).tolist()

        plt.plot(x, valores, marker='o', linewidth=2, label='Total mensal')
        plt.bar(x, valores, alpha=0.35, color='#4c72b0')
        plt.xticks(x, labels, rotation=45)

        if any(valores):
            pos_maior = max(range(len(valores)), key=lambda i: valores[i])
            plt.annotate(
                'Maior gasto',
                xy=(pos_maior, valores[pos_maior]),
                xytext=(pos_maior, valores[pos_maior] * 1.1 + 10),
                arrowprops=dict(arrowstyle='->', color='grey'),
                fontsize=12,
                color='grey'
            )

        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xlabel('Mês', fontsize=14)
        plt.ylabel('Despesa total (R$)', fontsize=14)
        plt.legend(loc='upper left', fontsize=12)

    static_dir = app.static_folder or os.path.join(BASE_DIR, "static")
    os.makedirs(static_dir, exist_ok=True)
    caminho = os.path.join(static_dir, 'relatorio_grafico.png')
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()
    return 'relatorio_grafico.png'

def usuario_obrigatorio():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if "usuario" in session:
        return redirect(url_for('home'))

    mensagem_login = None
    if request.method == 'POST':
        username = request.form.get("username", "").strip()
        senha = request.form.get("senha", "").strip()
        if validar_login(username, senha):
            session["usuario"] = username
            return redirect(url_for('home'))
        mensagem_login = "Usuário ou senha inválidos."

    return render_template('login.html', mensagem_login=mensagem_login)

@app.route('/register', methods=['POST'])
def register():
    if "usuario" in session:
        return redirect(url_for('home'))

    username = request.form.get("username_cadastro", "").strip()
    senha = request.form.get("senha_cadastro", "").strip()
    mensagem_cadastro = criar_usuario(username, senha)
    sucesso = mensagem_cadastro is None

    if sucesso:
        session["usuario"] = username
        return redirect(url_for('home'))

    return render_template('login.html', mensagem_cadastro=mensagem_cadastro)

@app.route('/logout')
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

@app.route('/')
def home():
    redirect_login = usuario_obrigatorio()
    if redirect_login:
        return redirect_login

    usuario = session["usuario"]
    categoria_selecionada = request.args.get('categoria')
    mes_selecionado = request.args.get('mes')

    despesas_filtradas = filtrar_despesas(categoria_selecionada, mes_selecionado, usuario)
    grupos = agrupar_por_categoria(despesas_filtradas)
    total = sum(d["valor"] for d in despesas_filtradas)

    return render_template(
        'index.html',
        despesas=despesas_filtradas,
        total=total,
        categorias=categorias_disponiveis,
        meses=meses_disponiveis,
        grupos=grupos,
        categoria_selecionada=categoria_selecionada,
        mes_selecionado=mes_selecionado,
        usuario=usuario
    )

@app.route('/despesas', methods=['GET'])
def get_despesas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    return jsonify(filtrar_despesas(usuario=usuario))

@app.route('/despesas', methods=['POST'])
def post_despesas():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.is_json:
        dados = request.get_json()
    else:
        dados = request.form

    descricao = dados.get("descricao", "").strip()
    valor_raw = str(dados.get("valor", "")).strip().replace(",", ".")
    try:
        valor = float(valor_raw) if valor_raw else 0.0
    except ValueError:
        valor = 0.0

    categoria = dados.get("categoria", "").strip()
    mes = dados.get("mes", "").strip()

    if categoria == "Outros":
        categoria = dados.get("categoria_outra", "").strip() or "Outros"

    adicionar_despesa(descricao, valor, categoria, mes, session["usuario"])

    return redirect(url_for(
        'home',
        categoria=request.args.get('categoria'),
        mes=request.args.get('mes')
    ))

@app.route('/despesas/excluir/<int:despesa_id>', methods=['POST'])
def excluir_despesa(despesa_id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    global despesas
    despesas = [d for d in despesas if not (d["id"] == despesa_id and d.get("usuario") == usuario)]
    salvar_despesas()
    return redirect(url_for(
        'home',
        categoria=request.args.get('categoria'),
        mes=request.args.get('mes')
    ))

@app.route('/despesas/limpar', methods=['POST'])
def limpar_despesas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    global despesas
    despesas = [d for d in despesas if d.get("usuario") != usuario]
    salvar_despesas()
    return redirect(url_for('home'))

@app.route('/relatorio')
def relatorio():
    redirect_login = usuario_obrigatorio()
    if redirect_login:
        return redirect_login

    usuario = session["usuario"]
    categoria_selecionada = request.args.get('categoria')
    mes_selecionado = request.args.get('mes')

    despesas_filtradas = filtrar_despesas(categoria_selecionada, mes_selecionado, usuario)
    total = sum(d["valor"] for d in despesas_filtradas)
    grafico_relatorio = gerar_grafico_relatorio(despesas_filtradas)

    return render_template(
        'relatorio.html',
        despesas=despesas_filtradas,
        total=total,
        categorias=categorias_disponiveis,
        meses=meses_disponiveis,
        categoria_selecionada=categoria_selecionada,
        mes_selecionado=mes_selecionado,
        usuario=usuario,
        grafico_relatorio=grafico_relatorio
    )

carregar_usuarios()
carregar_despesas()

if __name__ == '__main__':
    app.run(debug=True)