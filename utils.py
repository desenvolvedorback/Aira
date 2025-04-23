import requests
from bs4 import BeautifulSoup
from googlesearch import search
from modelo import resumir_texto, carregar_conhecimento, salvar_conhecimento

def pesquisar_na_web(pergunta):
    links = []
    for url in search(pergunta, num_results=5):
        if "google.com" in url or "pinterest.com" in url:
            continue
        links.append(url)
        if len(links) >= 3:
            break

    respostas = []
    for link in links:
        try:
            html = requests.get(link, timeout=5).text
            soup = BeautifulSoup(html, 'html.parser')
            texto = " ".join([p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 60])
            resumo = resumir_texto(texto)
            if resumo:
                respostas.append((resumo, link))
        except:
            continue

    if respostas:
        resposta, _ = respostas[0]
        salvar_resposta_no_banco(pergunta, resposta)
        return resposta, links
    return None, []

def salvar_resposta_no_banco(pergunta, resposta):
    banco = carregar_conhecimento()
    if not any(item["pergunta"] == pergunta for item in banco):
        banco.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "frequencia": 1
        })
        salvar_conhecimento(banco)