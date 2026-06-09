from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import json
from functools import wraps

app = Flask(__name__)

# Configuração de CORS manual
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configuração do banco de dados
DB_PATH = 'agenda.db'

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS eventos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  titulo TEXT NOT NULL,
                  descricao TEXT,
                  data_inicio DATETIME NOT NULL,
                  data_fim DATETIME,
                  local TEXT,
                  prioridade TEXT DEFAULT 'normal',
                  categoria TEXT,
                  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_db():
    """Retorna conexão com banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Rotas da API
@app.route('/api/eventos', methods=['GET'])
def listar_eventos():
    """Lista todos os eventos"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM eventos ORDER BY data_inicio')
    eventos = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(eventos), 200

@app.route('/api/eventos', methods=['POST'])
def criar_evento():
    """Cria um novo evento"""
    dados = request.json
    
    if not dados.get('titulo') or not dados.get('data_inicio'):
        return jsonify({'erro': 'Título e data são obrigatórios'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO eventos 
                 (titulo, descricao, data_inicio, data_fim, local, prioridade, categoria)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (dados['titulo'], dados.get('descricao'), dados['data_inicio'],
               dados.get('data_fim'), dados.get('local'), dados.get('prioridade', 'normal'),
               dados.get('categoria')))
    conn.commit()
    evento_id = c.lastrowid
    conn.close()
    
    return jsonify({'id': evento_id, 'mensagem': 'Evento criado com sucesso'}), 201

@app.route('/api/eventos/<int:evento_id>', methods=['GET'])
def obter_evento(evento_id):
    """Obtém um evento específico"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM eventos WHERE id = ?', (evento_id,))
    evento = c.fetchone()
    conn.close()
    
    if not evento:
        return jsonify({'erro': 'Evento não encontrado'}), 404
    
    return jsonify(dict(evento)), 200

@app.route('/api/eventos/<int:evento_id>', methods=['PUT'])
def atualizar_evento(evento_id):
    """Atualiza um evento existente"""
    dados = request.json
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM eventos WHERE id = ?', (evento_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'erro': 'Evento não encontrado'}), 404
    
    atualizacoes = []
    valores = []
    
    for campo in ['titulo', 'descricao', 'data_inicio', 'data_fim', 'local', 'prioridade', 'categoria']:
        if campo in dados:
            atualizacoes.append(f'{campo} = ?')
            valores.append(dados[campo])
    
    valores.append(evento_id)
    
    query = f"UPDATE eventos SET {', '.join(atualizacoes)} WHERE id = ?"
    c.execute(query, valores)
    conn.commit()
    conn.close()
    
    return jsonify({'mensagem': 'Evento atualizado com sucesso'}), 200

@app.route('/api/eventos/<int:evento_id>', methods=['DELETE'])
def deletar_evento(evento_id):
    """Deleta um evento"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM eventos WHERE id = ?', (evento_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'erro': 'Evento não encontrado'}), 404
    
    c.execute('DELETE FROM eventos WHERE id = ?', (evento_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'mensagem': 'Evento deletado com sucesso'}), 200

@app.route('/api/eventos/filtro/categoria', methods=['GET'])
def filtrar_por_categoria():
    """Filtra eventos por categoria"""
    categoria = request.args.get('categoria')
    
    if not categoria:
        return jsonify({'erro': 'Categoria é obrigatória'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM eventos WHERE categoria = ? ORDER BY data_inicio', (categoria,))
    eventos = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(eventos), 200

@app.route('/api/eventos/filtro/prioridade', methods=['GET'])
def filtrar_por_prioridade():
    """Filtra eventos por prioridade"""
    prioridade = request.args.get('prioridade')
    
    if not prioridade:
        return jsonify({'erro': 'Prioridade é obrigatória'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM eventos WHERE prioridade = ? ORDER BY data_inicio', (prioridade,))
    eventos = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(eventos), 200

@app.route('/')
def index():
    """Página principal com interface visual"""
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)