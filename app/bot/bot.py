import os
import sys
from telegram.error import Conflict

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from app.database.db import SessionLocal
from app.services.bet_service import BetService

PID_FILE = os.path.join(project_root, 'bot.pid')


def write_pid_file():
    pid = os.getpid()
    with open(PID_FILE, 'w', encoding='utf-8') as f:
        f.write(str(pid))


def remove_pid_file():
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except OSError:
        pass


def is_bot_already_running():
    if not os.path.exists(PID_FILE):
        return False

    try:
        with open(PID_FILE, 'r', encoding='utf-8') as f:
            pid = int(f.read().strip())
    except Exception:
        return False

    if pid <= 0:
        return False

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá! Envie suas apostas no formato: "custo - odd - green/red - esporte - liga"\nExemplo: "100 - 2.10 - green - futebol - serie_a"')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    db = SessionLocal()
    service = BetService(db)
    try:
        bet = service.add_bet(message_text)
        await update.message.reply_text(f'Aposta registrada! Lucro: {bet.lucro:.2f}')
    except ValueError as e:
        await update.message.reply_text(f'Erro: {str(e)}')
    finally:
        db.close()

def main():
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN não configurado. Configure o arquivo .env e tente novamente.")
        return

    if is_bot_already_running():
        print("⚠️  Um bot já está em execução neste computador. Pare-o antes de iniciar outro.")
        return

    write_pid_file()
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.run_polling()
    except Conflict:
        print("⚠️  O bot não pôde iniciar: outro processo já está usando o mesmo token Telegram.")
        print("Certifique-se de que apenas uma instância do bot esteja ativa e pare a outra.")
    except Exception as e:
        print(f"❌ Erro no bot: {e}")
    finally:
        remove_pid_file()

if __name__ == '__main__':
    main()