from flask import Flask, request, jsonify
import sqlite3
import datetime
import json

app = Flask(__name__)

# Criar banco de dados e tabelas se não existirem
def init_db():
    conn = sqlite3.connect('ia.db')
    cursor = conn.cursor()

    # Tabela de conhecimento manual
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conhecimento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT UNIQUE,
            resposta TEXT,
            vezes_perguntada INTEGER DEFAULT 1
        )
    ''')

    # Tabela de histórico de conversas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            pergunta TEXT,
            resposta TEXT,
            data TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Carregar base de conhecimento inicial
def carregar_conhecimento():
    conn = sqlite3.connect('ia.db')
    cursor = conn.cursor()

    try:
        with open('básico.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            for item in dados.get("conhecimento", []):
                cursor.execute("INSERT OR IGNORE INTO conhecimento (pergunta, resposta) VALUES (?, ?)", 
                               (item["pergunta"], item["resposta"]))
        conn.commit()
    except Exception as e:
        print("Erro ao carregar base de conhecimento:", e)

    conn.close()

# Inicializar banco e carregar conhecimento
init_db()
carregar_conhecimento()

# Endpoint para ensinar a IA manualmente
@app.route('/ensinar', methods=['POST'])
def ensinar():
    data = request.json
    pergunta = data.get('pergunta')
    resposta = data.get('resposta')

    if not pergunta or not resposta:
        return jsonify({'erro': 'Pergunta e resposta são obrigatórias'}), 400

    conn = sqlite3.connect('ia.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO conhecimento (pergunta, resposta) VALUES (?, ?)", (pergunta, resposta))
        conn.commit()
        msg = 'Aprendi uma nova resposta!'
    except sqlite3.IntegrityError:
        msg = 'Já sei a resposta para essa pergunta!'

    conn.close()
    return jsonify({'mensagem': msg})

# Endpoint para perguntar algo à IA
@app.route('/perguntar', methods=['POST'])
def perguntar():
    data = request.json
    pergunta = data.get('pergunta')
    usuario = data.get('usuario', 'desconhecido')  # Nome do usuário opcional

    if not pergunta:
        return jsonify({'erro': 'Pergunta é obrigatória'}), 400

    conn = sqlite3.connect('ia.db')
    cursor = conn.cursor()

    # Verificar se já tem uma resposta ensinada
    cursor.execute("SELECT resposta, vezes_perguntada FROM conhecimento WHERE pergunta = ?", (pergunta,))
    resultado = cursor.fetchone()

    if resultado:
        resposta, vezes_perguntada = resultado
        cursor.execute("UPDATE conhecimento SET vezes_perguntada = ? WHERE pergunta = ?", 
                       (vezes_perguntada + 1, pergunta))
    else:
        resposta = 'Não sei responder isso ainda! Me ensine.'
        cursor.execute("INSERT INTO conhecimento (pergunta, resposta, vezes_perguntada) VALUES (?, ?, 1)", 
                       (pergunta, resposta))

    # Salvar no histórico de conversas
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico (usuario, pergunta, resposta, data) VALUES (?, ?, ?, ?)",
                   (usuario, pergunta, resposta, data_atual))
    
    conn.commit()
    conn.close()

    return jsonify({'resposta': resposta})

# Endpoint para visualizar histórico de conversas
@app.route('/historico', methods=['GET'])
def historico():
    conn = sqlite3.connect('ia.db')
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, pergunta, resposta, data FROM historico ORDER BY id DESC")
    historico = cursor.fetchall()
    conn.close()

    return jsonify([{'usuario': h[0], 'pergunta': h[1], 'resposta': h[2], 'data': h[3]} for h in historico])

# Endpoint para atualizar respostas erradas e aprendizado automático
@app.route('/atualizar_resposta', methods=['POST'])
def atualizar_resposta():
    data = request.json
    pergunta = data.get('pergunta')
    nova_resposta = data.get('nova_resposta')

    if not pergunta or not nova_resposta:
        return jsonify({'erro': 'Pergunta e nova resposta são obrigatórias'}), 400

    conn = sqlite3.connect('ia.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE conhecimento SET resposta = ?, vezes_perguntada = vezes_perguntada + 2 WHERE pergunta = ?", 
                   (nova_resposta, pergunta))
    if cursor.rowcount == 0:
        return jsonify({'erro': 'Pergunta não encontrada no banco de dados'}), 404

    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Resposta atualizada com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True)