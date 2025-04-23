from flask import (Flask, request, jsonify, send_from_directory,
                   render_template_string, session, redirect, url_for)
import requests, time, logging, re, os, sqlite3, csv, io
from bs4 import BeautifulSoup
from googlesearch import search

# ----------------- CONFIG -------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque_esta_chave")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "1234")

UA_HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/124.0 Safari/537.36")}

DB = "logs.db"

# ----------------- BD -----------------------------------------------------
def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS log(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                       pergunta TEXT,
                       resposta TEXT)""")
init_db()

def grava_log(pergunta, resposta):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO log(pergunta,resposta) VALUES(?,?)",
                    (pergunta, resposta))

# ----------------- UTILIDADES --------------------------------------------
def resposta_automatica(p):
    p = p.lower().strip()
    cortesias = {
        "oi": "Oi! Como posso te ajudar?",
        "olá": "Oi! Como posso te ajudar?",
        "tudo bem": "Tudo ótimo por aqui! E com você?",
        "bom dia": "Bom dia! Que hoje seja um dia abençoado.",
        "boa noite": "Boa noite! Que você tenha um descanso top!",
        "obrigado": "De nada! Qualquer coisa, tô por aqui.",
        "obrigada": "De nada! Qualquer coisa, tô por aqui.",
        "valeu": "Tamo junto!",
    }
    for k, resp in cortesias.items():
        if k == p or k in p:
            return resp
    return None

def resumir(texto, n=2):
    frases = re.split(r'(?<=[.!?]) +', texto)
    return " ".join(frases[:n]).strip()

def extrair_resumo(link):
    try:
        r = requests.get(link, headers=UA_HEADERS, timeout=6)
        if r.status_code in (401, 403):
            r = requests.get(f"https://r.jina.ai/http://{link}",
                             headers=UA_HEADERS, timeout=6)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        parags = [p.get_text(" ", strip=True) for p in soup.find_all("p")
                  if len(p.get_text(strip=True)) >= 20]
        return resumir(" ".join(parags[:8]))
    except Exception as e:
        logging.warning("Falha em %s: %s", link, e)
        return None

def obter_links(q, mx=3):
    vistos, links = set(), []
    for url in search(q, num_results=20):
        if any(bad in url for bad in ("google.", "pinterest.")) or url.startswith("/"):
            continue
        if url in vistos:
            continue
        vistos.add(url); links.append(url)
        if len(links) == mx:
            break
    return links

# ----------------- AUTH DECORATOR ----------------------------------------
from functools import wraps
def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if session.get("auth"):
            return f(*a, **kw)
        return redirect(url_for("login"))
    return wrapper

# ----------------- HTML EMBUTIDO -----------------------------------------
LOGIN_HTML = """
<!DOCTYPE html><html><head><meta charset='utf-8'><title>Login</title>
<style>
body{font-family:Arial;display:flex;justify-content:center;
align-items:center;height:100vh;background:#f5f5f5}
form{background:#fff;padding:30px;border-radius:8px;box-shadow:0 0 10px #0003}
input{display:block;width:250px;padding:8px;margin:10px 0;border:1px solid #ccc;border-radius:4px}
button{padding:8px 20px;border:none;background:#4CAF50;color:#fff;border-radius:4px;cursor:pointer}
</style></head><body>
<form method=post>
<h3>Login admin</h3>
<input name=user placeholder=Usuário>
<input name=pass type=password placeholder=Senha>
<button>Entrar</button>
</form></body></html>
"""

ADMIN_HTML = """
<!DOCTYPE html><html><head><meta charset='utf-8'><title>Painel</title>
<style>
body{font-family:Arial;padding:20px;background:#fafafa}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid #ddd;padding:8px;vertical-align:top}
tr:nth-child(even){background:#f2f2f2}
th{background:#4CAF50;color:#fff}
a.btn{display:inline-block;margin:0 5px 15px 0;padding:6px 12px;background:#4CAF50;color:#fff;text-decoration:none;border-radius:4px}
</style></head><body>
<h2>Painel Administrativo</h2>
<a class='btn' href='/logout'>Logout</a>
<a class='btn' href='/download'>Baixar CSV</a>
<a class='btn' href='/limpar'>Limpar log</a>
<table>
<tr><th>ID</th><th>Data/Hora</th><th>Pergunta</th><th>Resposta</th></tr>
{% for row in rows %}
<tr><td>{{row[0]}}</td><td>{{row[1]}}</td>
<td style='max-width:260px'>{{row[2]}}</td>
<td style='max-width:400px'>{{row[3]|safe}}</td></tr>
{% endfor %}
</table></body></html>
"""

# ----------------- ROTAS PÚBLICAS ----------------------------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    pergunta = request.get_json().get("pergunta", "")
    auto = resposta_automatica(pergunta)
    if auto:
        grava_log(pergunta, auto)
        return jsonify({"resposta": auto})

    links = obter_links(pergunta)
    respostas = [r for r in (extrair_resumo(l) for l in links) if r]

    if respostas:
        resp = (f"Então, eu pesquisei algumas fontes e aqui vai um resumo sobre "
                f"<b>{pergunta}</b>:<br><br>{respostas[0]}")
    else:
        resp = ("Poxa, procurei bastante, mas não achei uma resposta clara. "
                "Quer tentar formular de outro jeito?")

    if links:
        fontes = "<br>".join(f'<a href="{x}" target="_blank">{x}</a>' for x in links)
        resp += f"<br><br><b>Fontes:</b><br>{fontes}"

    grava_log(pergunta, resp)
    return jsonify({"resposta": resp})

@app.route("/avaliar", methods=["POST"])
def avaliar():
    logging.info("Feedback: %s", request.get_json())
    return jsonify({"status": "Valeu pelo feedback!"})

# ----------------- ROTAS ADMIN -----------------------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("user")
        p = request.form.get("pass")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["auth"] = True
            return redirect("/admin")
        return "Credenciais inválidas", 403
    return render_template_string(LOGIN_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return "Saiu!"

@app.route("/admin")
@login_required
def admin():
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT * FROM log ORDER BY id DESC LIMIT 100").fetchall()
    return render_template_string(ADMIN_HTML, rows=rows)

@app.route("/download")
@login_required
def download():
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT * FROM log").fetchall()
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue(), 200, {"Content-Type":"text/csv",
                                 "Content-Disposition":"attachment; filename=log.csv"}

@app.route("/limpar")
@login_required
def limpar():
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM log")
    return redirect("/admin")

# ----------------- RUN ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)