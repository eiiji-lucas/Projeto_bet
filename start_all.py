#!/usr/bin/env python3
"""
Script principal para iniciar todos os serviços do Bet Tracker
"""
import os
import sys
import socket
import subprocess
import time
import threading

def port_in_use(port, host='0.0.0.0'):
    """Verifica se uma porta já está em uso."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return False
        except OSError:
            return True

def run_service(name, cmd, cwd):
    """Executa um serviço em background"""
    print(f"🚀 Iniciando {name}...")
    try:
        # Garantir que o ambiente virtual está ativado
        env = os.environ.copy()
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'venv')
        env['VIRTUAL_ENV'] = venv_path
        env['PATH'] = os.path.join(venv_path, 'Scripts') + ';' + env.get('PATH', '')
        process = subprocess.Popen(cmd, cwd=cwd, env=env)
        return process
    except Exception as e:
        print(f"❌ Erro ao iniciar {name}: {e}")
        return None

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    processes = []

    print("🎯 Bet Tracker - Iniciando todos os serviços...")
    print("=" * 50)

    # 1. Iniciar API
    api_started = False
    api_cmd = [sys.executable, "app/api/main.py"]
    if port_in_use(8000):
        print("⚠️  Porta 8000 já está em uso. A API não será iniciada.")
    else:
        api_process = run_service("API FastAPI", api_cmd, current_dir)
        if api_process:
            processes.append({"name": "API", "process": api_process})
            api_started = True
            time.sleep(2)  # Aguardar API iniciar

    # 2. Iniciar Dashboard
    dashboard_started = False
    if port_in_use(8501):
        print("⚠️  Porta 8501 já está em uso. O Dashboard não será iniciado.")
    else:
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'venv')
        env = os.environ.copy()
        env['VIRTUAL_ENV'] = venv_path
        env['PATH'] = os.path.join(venv_path, 'Scripts') + ';' + env.get('PATH', '')
        dashboard_cmd = [
            sys.executable, "-m", "streamlit", "run",
            "dashboard/dashboard_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        dashboard_process = run_service("Dashboard Streamlit", dashboard_cmd, current_dir)
        if dashboard_process:
            processes.append({"name": "Dashboard", "process": dashboard_process})
            dashboard_started = True
            time.sleep(3)  # Aguardar dashboard iniciar

    # 3. Iniciar Bot
    bot_started = False
    bot_cmd = [sys.executable, "app/bot/bot.py"]
    bot_process = run_service("Bot Telegram", bot_cmd, current_dir)
    if bot_process:
        processes.append({"name": "Bot", "process": bot_process})
        bot_started = True

    print("\n" + "=" * 50)
    if processes:
        print("✅ Serviços iniciados!")
    else:
        print("⚠️  Nenhum serviço iniciado.")
    print(f"📊 Dashboard: {'http://localhost:8501' if dashboard_started else 'não iniciado'}")
    print(f"🔌 API: {'http://localhost:8000' if api_started else 'não iniciado'}")
    print(f"🤖 Bot: {'Aguardando mensagens no Telegram' if bot_started else 'não iniciado'}")
    print("❌ Pressione Ctrl+C para parar todos os serviços")
    print("=" * 50)

    try:
        # Manter executando enquanto houver serviços ativos
        active_services = processes.copy()
        while active_services:
            time.sleep(1)
            alive_services = []
            for item in active_services:
                if item["process"].poll() is None:
                    alive_services.append(item)
                else:
                    print(f"⚠️  {item['name']} parou inesperadamente!")
            active_services = alive_services

    except KeyboardInterrupt:
        print("\n🛑 Parando todos os serviços...")

        # Parar processos
        for item in processes:
            process = item["process"]
            name = item["name"]
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ {name} parado")
                except:
                    process.kill()
                    print(f"💀 {name} forçado a parar")
            else:
                print(f"ℹ️  {name} já estava parado")

        print("👋 Todos os serviços foram parados!")

if __name__ == "__main__":
    main()