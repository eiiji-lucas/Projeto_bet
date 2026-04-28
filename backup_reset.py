#!/usr/bin/env python3
"""
Script para fazer backup e resetar o banco de dados
"""
import os
import json
import subprocess
import sys
from datetime import datetime

# Adiciona o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.database.db import SessionLocal, create_tables, DATABASE_FILE, engine
from app.services.bet_service import BetService
from models.bet import Bet


def backup_database(allow_empty=False):
    """Faz backup de todas as apostas em JSON"""
    try:
        db = SessionLocal()
        service = BetService(db)
        bets = service.get_all_bets()
        db.close()
        engine.dispose()

        if not bets:
            if not allow_empty:
                print("ℹ️  Nenhum dado para fazer backup")
                return None
            print("ℹ️  Nenhum dado encontrado. Criando backup vazio.")

        # Converte para dicionário
        bets_data = []
        for bet in bets:
            bets_data.append({
                'id': bet.id,
                'data': bet.data.isoformat() if bet.data else None,
                'entrada': bet.entrada,
                'odd': bet.odd,
                'resultado': bet.resultado,
                'lucro': bet.lucro,
                'esporte': bet.esporte,
                'liga': bet.liga
            })

        # Cria diretório de backup se não existir
        backup_dir = os.path.join(current_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')

        # Salva o backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_bets': len(bets_data),
                'bets': bets_data
            }, f, indent=2, ensure_ascii=False)

        print(f"💾 Backup criado: {backup_file}")
        print(f"📊 {len(bets_data)} apostas salvas")
        return backup_file

    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return None

def reset_database():
    """Reseta o banco de dados após backup"""
    print("🔄 Iniciando reset do banco de dados...")

    # Forçar fechamento de conexões SQLite abertas pelo engine
    try:
        engine.dispose()
    except Exception as e:
        print(f"⚠️  Erro ao liberar conexões do engine: {e}")

    # Remove arquivo do banco e arquivos WAL/SHM, usando o mesmo DB do app
    db_file = DATABASE_FILE
    removed_any = False
    for suffix in ["", "-shm", "-wal"]:
        path = f"{db_file}{suffix}"
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🗑️  Removido: {path}")
                removed_any = True
            except Exception as e:
                print(f"❌ Não foi possível remover {path}: {e}")
                return False

    if not removed_any:
        print(f"ℹ️  Nenhum arquivo de banco encontrado em: {db_file}")

    # Recria tabelas
    try:
        create_tables()
        print("✅ Banco resetado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao recriar tabelas: {e}")
        return False

def list_backups():
    """Lista todos os backups disponíveis"""
    backup_dir = os.path.join(current_dir, 'backups')
    if not os.path.exists(backup_dir):
        print("📁 Nenhum backup encontrado")
        return []

    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('backup_') and file.endswith('.json'):
            filepath = os.path.join(backup_dir, file)
            backups.append((file, filepath))

    if backups:
        print("📦 Backups disponíveis:")
        for name, path in backups:
            print(f"  • {name}")
    else:
        print("📁 Nenhum backup encontrado")

    return backups

def restore_backup(backup_file):
    """Restaura dados de um backup"""
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        db = SessionLocal()

        restored = 0
        for bet_data in data['bets']:
            try:
                bet = Bet(
                    data=datetime.fromisoformat(bet_data['data']) if bet_data.get('data') else None,
                    entrada=bet_data['entrada'],
                    odd=bet_data['odd'],
                    resultado=bet_data['resultado'],
                    lucro=bet_data['lucro'],
                    esporte=bet_data['esporte'],
                    liga=bet_data['liga']
                )
                db.add(bet)
                restored += 1
            except Exception:
                pass  # Pula apostas que não puderam ser restauradas

        db.commit()
        db.close()
        engine.dispose()

        print(f"✅ {restored} apostas restauradas de {data['total_bets']}")
        return True

    except Exception as e:
        print(f"❌ Erro na restauração: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python backup_reset.py <comando>")
        print("Comandos:")
        print("  backup    - Faz backup dos dados atuais")
        print("  reset     - Faz backup e reseta o banco")
        print("             Use --yes ou -y para pular confirmação")
        print("  list      - Lista backups disponíveis")
        print("  restore <arquivo> - Restaura backup específico")
        return

    yes_flag = '--yes' in sys.argv or '-y' in sys.argv
    command = sys.argv[1]

    if command == 'backup':
        backup_file = backup_database()
        if backup_file:
            print(f"\n✅ Backup concluído: {os.path.basename(backup_file)}")

    elif command == 'reset':
        if not yes_flag:
            print("⚠️  ATENÇÃO: Isso fará backup e resetará TODOS os dados!")
            confirm = input("Continuar? (digite 'SIM' para confirmar): ")
        else:
            confirm = 'SIM'

        if confirm.upper() == 'SIM':
            backup_file = backup_database(allow_empty=True)
            reset_ok = reset_database()
            if reset_ok:
                print("🎉 Banco resetado com sucesso!")
                if backup_file:
                    print(f"💾 Backup salvo em: {os.path.basename(backup_file)}")
                else:
                    print("⚠️  Nenhum backup foi criado porque não havia apostas no banco.")
                print("🤖 Reinicie os serviços com: python start_all.py")
            else:
                print("❌ Falha ao resetar o banco")
        else:
            print("❌ Operação cancelada")

    elif command == 'list':
        list_backups()

    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Especifique o arquivo de backup")
            list_backups()
            return

        backup_name = sys.argv[2]
        backup_dir = os.path.join(current_dir, 'backups')
        backup_file = os.path.join(backup_dir, backup_name)

        if not os.path.exists(backup_file):
            print(f"❌ Arquivo não encontrado: {backup_name}")
            list_backups()
            return

        print(f"🔄 Restaurando backup: {backup_name}")
        confirm = input("Isso adicionará os dados ao banco atual. Continuar? (SIM/não): ")
        if confirm.upper() in ['SIM', 'S', '']:
            if restore_backup(backup_file):
                print("✅ Restauração concluída!")
            else:
                print("❌ Falha na restauração")
        else:
            print("❌ Operação cancelada")

    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main()