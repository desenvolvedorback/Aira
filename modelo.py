import json
import os
from config import CAMINHO_BANCO, CAMINHO_HISTORICO

# Carregar banco de aprendizado
def carregar_conhecimento():
    if not os.path.exists(CAMINHO_BANCO):
        return []
    with open(CAMINHO_BANCO, "r", encoding="utf-8") as f:
        return json.load(f)

# Salvar banco
def salvar_conhecimento(banco):
    with open(CAMINHO_BANCO, "w", encoding="utf-8") as f:
        json.dump(banco, f, indent=4, ensure_ascii=False)

# Histórico de conversas
def salvar_historico(entrada, saida):
    historico = []
    if os.path.exists(CAMINHO_HISTORICO):
        with open(CAMINHO_HISTORICO, "r", encoding="utf-8") as f:
            historico = json.load(f)
    historico.append({"usuario": entrada, "ia": saida})
    with open(CAMINHO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

# Respostas automáticas básicas e personalização
def resposta_automatica(pergunta):
    pergunta = pergunta.lower()
    respostas = {
        "oi": "Olá! Como posso te ajudar hoje?",
        "olá": "Oi! Tudo certo por aí?",
        "tudo bem": "Tudo ótimo por aqui! E contigo?",
        "qual seu nome": "Pode me chamar de Subordinada, se quiser.",
        "quem te criou": "Fui criada por um dev brabo. Ele me ensinou a pensar, falar e te entender.",
        "posso te chamar de subordinada": "Claro! Achei criativo, chefe.",
        "valeu": "Tamo junto, chefe!",
        "bom dia": "Bom dia! Que seu dia seja cheio de bênçãos e paz.",
        "boa noite": "Boa noite! Durma com os anjos, chefe.",
        "obrigado": "Sempre às ordens, chefe!"
    }
    for chave, resposta in respostas.items():
        if chave in pergunta:
            return resposta, True
    return None, False

def resumir_texto(texto):
    return texto if len(texto) < 500 else texto[:500] + "..."

# Busca no banco de conhecimento
def gerar_resposta(pergunta):
    pergunta = pergunta.lower()
    banco = carregar_conhecimento()
    for item in banco:
        if item["pergunta"] in pergunta:
            item["frequencia"] += 1
            salvar_conhecimento(banco)
            return item["resposta"]
    return None