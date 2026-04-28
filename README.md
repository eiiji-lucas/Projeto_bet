python init_db.py# Bet Tracker

Sistema para automatizar o registro e análise de apostas esportivas via Telegram, com backend em Python e dashboard interativo.

## � Persistência de Dados

**Os dados são salvos permanentemente** no arquivo `bets.db` (SQLite) na raiz do projeto. As apostas **NUNCA são perdidas** - ficam armazenadas mesmo após reiniciar o computador.

## 🚀 Como rodar o projeto

### Opção 1: Iniciar Tudo de Uma Vez (Recomendado)

```bash
python start_all.py
```

Este comando inicia automaticamente:
- 🤖 Bot Telegram
- 📊 Dashboard Streamlit (http://localhost:8501)
- 🔌 API FastAPI (http://localhost:8000)

### Opção 2: Executar em Background (24/7)

Para deixar rodando o tempo todo, use os scripts de background:

#### Windows Batch (.bat)
```cmd
# Iniciar em background
start_bet_tracker.bat

# Parar
stop_bet_tracker.bat
```

#### PowerShell (.ps1)
```powershell
# Iniciar em background
.\Start-BetTracker.ps1

# Parar
.\Stop-BetTracker.ps1
```

**Nota:** Estes scripts executam sem console visível, mantendo o sistema rodando em background.

### Opção 3: Iniciar Serviços Individualmente

```bash
# Bot Telegram
python run_bot.py

# Dashboard (em outro terminal)
python run_dashboard.py

# API (em outro terminal)
python run_api.py
```

### 3. Configuração Inicial (apenas na primeira vez)

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python init_db.py

# Configurar token do Telegram em .env
# TELEGRAM_BOT_TOKEN=seu_token_aqui
```

### 4. Backup e Reset de Dados

**Para resetar os dados mas manter backup seguro:**

```bash
# Faz backup automático e reseta tudo
python backup_reset.py reset

# Apenas faz backup (sem resetar)
python backup_reset.py backup

# Lista todos os backups disponíveis
python backup_reset.py list

# Restaura dados de um backup específico
python backup_reset.py restore backup_20260427_143000.json
```

**Os backups ficam salvos na pasta `backups/` com timestamp automático.**

## 📩 Como usar

### Formato das Mensagens no Telegram:
```
valor - odd - green/red - esporte - liga
```

**Exemplos:**
- `100 - 2,5 - green - futebol - serie_a`
- `50 - 1.85 - red - basquete - nba`
- `200 - 3.20 - green - tênis - wimbledon`

### Acessar o Sistema:
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Bot Telegram**: Procure por @seu_bot_username

## 📊 Funcionalidades do Dashboard

- 📈 Métricas gerais (ROI, lucro total, taxa de acerto)
- 📊 Gráficos de evolução temporal
- 🏆 Estatísticas por esporte (mais lucrativo, distribuição)
- 🎯 Filtros por data e esporte
- 📋 Lista completa de apostas

3. API disponível em http://localhost:8000 com endpoints `/metrics` e `/bets`.

## 🧱 Estrutura do projeto

- `/app/bot`: Bot Telegram
- `/app/api`: API FastAPI
- `/app/database`: Configuração do banco
- `/app/services`: Lógica de negócio
- `/dashboard`: Dashboard Streamlit
- `/models`: Modelos de dados

## 🧠 Futuras melhorias

- Migração para PostgreSQL
- Docker para deploy
- Autenticação na API
- Notificações push