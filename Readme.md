

# Inteligência Artificial — Chatbot com a Aira

Chatbot conversacional que busca respostas na web, resume conteúdos e registra todo o histórico em **SQLite**.  
Inclui **painel administrativo** protegido por login para visualizar, baixar ou limpar os logs.

---

## ✨ Funcionalidades

- Respostas automáticas para saudações e agradecimentos.  
- Pesquisa Google ⇒ extração de resumo dos 3 primeiros links relevantes.  
- Históricos salvos em SQLite (pergunta, resposta, timestamp).  
- Painel `/admin` (login + senha) com:
  - Tabela das 100 interações mais recentes  
  - Botão “Baixar CSV”  
  - Botão “Limpar log”  
- API REST simples (`/perguntar`, `/avaliar`).  
- Dependências 100 % gratuitas, roda em qualquer **Python 3.10+** (Windows, Linux, Termux).

---

## 🚀 Instalação

1. **Instale as dependências necessárias**:

```bash
pip install flask
pip install requests
pip install beautifulsoup4
pip install googlesearch-python

2. SQLite já faz parte da biblioteca padrão do Python, então não é necessário instalá-lo separadamente.




---

🔧 Variáveis de ambiente (opcionais)

export ADMIN_USER="admin"          # usuário painel
export ADMIN_PASS="1234"           # senha painel
export SECRET_KEY="chave-secreta"  # sessão Flask

Sem definir, os valores acima são usados como padrão.


---

🏃‍♂️ Execução

python app.py

Abra em seu navegador:

Recurso: Chat público
URL: http://localhost:5000
Descrição: Interface do usuário

Recurso: Login admin
URL: http://localhost:5000/login
Descrição: Acesso ao painel

Recurso: Painel
URL: http://localhost:5000/admin
Descrição: Após login


---

📑 Rotas de API

Método: POST
Rota: /perguntar
Corpo JSON: { "pergunta": "texto" }
Retorno: { "resposta": "HTML" }

Método: POST
Rota: /avaliar
Corpo JSON: { "pergunta": "...", "resposta": "...", "avaliacao": 1 }
Retorno: { "status": "ok" }


---

📄 Licença

Distribuído sob Creative Commons Attribution‑NoDerivatives 4.0 (CC BY‑ND 4.0).
Você pode compartilhar e usar comercialmente, desde que atribua e não modifique o código original.

Mais detalhes: https://creativecommons.org/licenses/by-nd/4.0/


---

💬 Suporte & Manutenção (30 dias)



Incluído:

Suporte via WhatsApp ou Teams durante 30 dias (9h-18h, BRT).

Correção de bugs no código original.

Pequenos ajustes (ex.: mudança de texto ou cor).

Atualização de dependências de segurança.

Não incluído:

Suporte para o deploy/configuração em provedores (ex.: Render, Vercel, VPS etc.).

Integrações externas ou novos recursos (por exemplo, conexão com novas APIs).

Refatorações grandes de código.

Suporte após 30 dias de uso (pode ser contratado à parte).

> Observação: atualizações de sistema (features extras) são orçadas separadamente.




---

Sinta-se à vontade para abrir issues ou entrar em contato para personalizações.



