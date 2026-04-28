#!/usr/bin/env python3
"""
Script para iniciar o bot Telegram
"""
import os
import sys
import subprocess

def main():
    # Adicionar diretório raiz ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    print("🤖 Iniciando Bot Telegram...")
    print("📱 Bot está ouvindo mensagens...")
    print("❌ Pressione Ctrl+C para parar")

    # Comando para executar o bot
    cmd = [sys.executable, "app/bot/bot.py"]

    try:
        subprocess.run(cmd, cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 Bot parado!")

if __name__ == "__main__":
    main()