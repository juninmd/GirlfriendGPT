# GirlfriendGPT (Edição 2026)

![GirlfriendGPT CI](https://github.com/juninmd/GirlfriendGPT/actions/workflows/ci.yml/badge.svg)

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
3. Configure as variáveis de ambiente. Crie um arquivo `.env` no diretório raiz:
   ```bash
   GOOGLE_API_KEY=sua_chave_gemini
   TELEGRAM_TOKEN=seu_token_telegram
   # Opcional: Configurar voz (padrão: en-US-AriaNeural)
   EDGE_TTS_VOICE=en-US-AriaNeural

   # Opcional: Usar Ollama (padrão: google)
   # LLM_PROVIDER=ollama
   # OLLAMA_BASE_URL=http://localhost:11434
   # OLLAMA_MODEL=llama3
   ```

## Uso

### Modo CLI (Teste Local)
Converse com sua companheira no terminal:
```bash
python main.py --cli
```
Você será solicitado a selecionar uma personalidade.

### Bot do Telegram
Execute o bot do Telegram:
```bash
python main.py
```
Envie `/start` para o seu bot no Telegram para começar.

## Personalidades

As personalidades são definidas em `src/personalities/`. Para adicionar uma nova personalidade:

1. Crie um arquivo JSON (por exemplo, `jane.json`) em `src/personalities/`.
2. Siga a estrutura dos arquivos existentes:
   ```json
   {
     "name": "Jane",
     "byline": "Sua amiga aventureira",
     "identity": ["Você é Jane...", "Você adora caminhar..."],
     "behavior": ["Você é alegre...", "Você usa emojis..."],
     "profile_image": "opcional/caminho.png"
   }
   ```

## Desenvolvimento

Nós impomos estritamente a qualidade do código e a cobertura de testes.

### VS Code Dev Container

Este projeto inclui uma configuração `.devcontainer`. Abra a pasta no VS Code e clique em "Reopen in Container" para obter um ambiente pré-configurado com todas as dependências e ferramentas instaladas.

### Executando Verificações Localmente (Garantia de Qualidade)

Para garantir que seu código atenda a todos os padrões de qualidade (100% de cobertura, linting, segurança e tipagem), execute o script de verificação:

```bash
chmod +x scripts/verify.sh
./scripts/verify.sh
```

Este script automatiza as seguintes verificações:
1. **Instalação de Dependências**: Garante que o ambiente esteja atualizado.
2. **Linting e Formatação (Ruff)**: Verifica estilo e erros de código.
3. **Verificação de Tipos (Mypy)**: Garante a tipagem estrita em `src/`.
4. **Verificação de Segurança (Bandit)**: Busca por vulnerabilidades comuns.
5. **Testes e Cobertura**: Executa `pytest` e falha se a cobertura for inferior a 100%.

### Integração Contínua (CI)

O projeto possui um pipeline automatizado no GitHub Actions (`.github/workflows/ci.yml`) que executa todas as verificações acima (linting, formatação, tipagem, segurança e testes com 100% de cobertura) a cada *push* ou *pull request* para a branch `main`. Isso garante que o código no repositório esteja sempre estável e seguro.

## Licença
MIT

Verified for 2026 update and Gemini integration.
