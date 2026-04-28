#!/usr/bin/env python3
"""
Script para iniciar o dashboard Streamlit
"""
import os
import sys
import subprocess

def main():
    # Adicionar diretório raiz ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    print("🚀 Iniciando Dashboard Bet Tracker...")
    print("📊 URL: http://localhost:8501")
    print("❌ Pressione Ctrl+C para parar")

    # Comando para executar o dashboard
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "dashboard/dashboard_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]

    try:
        subprocess.run(cmd, cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 Dashboard parado!")

if __name__ == "__main__":
    main()