# GirlfriendGPT (Edição 2026)

![GirlfriendGPT CI](https://github.com/juninmd/GirlfriendGPT/actions/workflows/ci.yml/badge.svg)
**Verified: February 2026 (Gemini 3.0 Pro Enabled) - Status: Active**

Sua companheira de IA pessoal, atualizada para a era moderna usando **Google Gemini**, **LangGraph** e **LangChain**.

## Funcionalidades

* **Integração com Google Gemini**: Alimentado pelos modelos Gemini mais recentes (Gemini 3.0 Pro) para conversas inteligentes e rápidas.
* **Suporte ao Ollama**: Execute localmente com modelos de código aberto (Llama 3, Mistral, etc.) via Ollama.
* **Voz Personalizada**: Usa `edge-tts` para conversão de texto em fala gratuita e de alta qualidade.
* **Bot do Telegram**: Envie e receba mensagens diretamente de sua companheira de IA via Telegram.
* **Modo CLI**: Converse com sua companheira diretamente no terminal.
* **Personalidade**: Personalize a personalidade da IA através de arquivos JSON.
* **Selfies**: A IA é capaz de gerar selfies usando **Google Imagen 3**.

## Pré-requisitos

* Python 3.9+
* Chave de API do Google Gemini
* (Opcional) Token do Bot do Telegram
* (Opcional) Ollama (para inferência local)

## Instalação

1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` e preencha os valores para `GOOGLE_API_KEY` e `TELEGRAM_TOKEN`.