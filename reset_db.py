#!/usr/bin/env python3
"""
Script para resetar completamente o banco de dados
"""
import os
import subprocess
import sys

def reset_database():
    print("🔄 Iniciando reset do banco de dados...")

    # Para serviços
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe", "/t"], capture_output=True)
        subprocess.run(["taskkill", "/f", "/im", "pythonw.exe", "/t"], capture_output=True)
        print("🛑 Serviços parados!")
    except:
        pass

    # Remove arquivo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(current_dir, "bets.db")
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️  Banco removido!")

    # Recria tabelas
    try:
        # Importa e cria tabelas
        sys.path.insert(0, current_dir)
        from app.database.db import create_tables
        create_tables()
        print("✅ Banco resetado!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("\n🎉 Banco de dados resetado com sucesso!")
        print("📊 Todas as apostas foram removidas.")
        print("🤖 Reinicie os serviços com: python start_all.py")
    else:
        print("\n❌ Falha ao resetar!")
        sys.exit(1)