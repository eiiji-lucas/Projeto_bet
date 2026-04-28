#!/usr/bin/env python3
"""
Script para iniciar a API FastAPI
"""
import os
import sys
import subprocess

def main():
    # Adicionar diretório raiz ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    print("🔌 Iniciando API FastAPI...")
    print("📡 URL: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("❌ Pressione Ctrl+C para parar")

    # Comando para executar a API
    cmd = [sys.executable, "app/api/main.py"]

    try:
        subprocess.run(cmd, cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 API parada!")

if __name__ == "__main__":
    main()