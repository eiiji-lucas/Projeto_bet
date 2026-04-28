from sqlalchemy.orm import Session
from models.bet import Bet
from typing import List, Dict, Any
from datetime import datetime, date
import pandas as pd

class BetService:
    def __init__(self, db: Session):
        self.db = db

    def parse_bet_message(self, message: str) -> Dict[str, Any]:
        """
        Parse a bet message in the format: "custo da entrada - odd - green/red - esporte - liga"
        Example: "100 - 2.10 - green - futebol - serie_a"
        Returns a dict with entrada, odd, resultado, esporte, liga
        """
        # Split by " - " to handle the new format
        parts = [part.strip() for part in message.split(" - ")]
        if len(parts) < 5:
            raise ValueError("Mensagem inválida. Formato esperado: 'custo - odd - green/red - esporte - liga'")

        # Parse entrada (allow comma as decimal separator)
        entrada_str = parts[0].replace(',', '.')
        try:
            entrada = float(entrada_str)
        except ValueError:
            raise ValueError(f"Valor de entrada inválido: {parts[0]}")

        # Parse odd (allow comma as decimal separator)
        odd_str = parts[1].replace(',', '.')
        try:
            odd = float(odd_str)
        except ValueError:
            raise ValueError(f"Valor de odd inválido: {parts[1]}")

        resultado = parts[2].lower()
        esporte = parts[3].lower()
        liga = parts[4].lower()

        if resultado not in ['green', 'red']:
            raise ValueError("Resultado deve ser 'green' ou 'red'")

        return {
            'entrada': entrada,
            'odd': odd,
            'resultado': resultado,
            'esporte': esporte,
            'liga': liga
        }

    def calculate_profit(self, entrada: float, odd: float, resultado: str) -> float:
        """
        Calculate profit: win = entrada * (odd - 1), loss = -entrada
        """
        if resultado == 'green':
            return entrada * (odd - 1)
        elif resultado == 'red':
            return -entrada
        else:
            raise ValueError("Resultado inválido")

    def add_bet(self, message: str) -> Bet:
        """
        Parse message, calculate profit, and save to DB
        """
        parsed = self.parse_bet_message(message)
        lucro = self.calculate_profit(parsed['entrada'], parsed['odd'], parsed['resultado'])

        bet = Bet(
            entrada=parsed['entrada'],
            odd=parsed['odd'],
            resultado=parsed['resultado'],
            lucro=lucro,
            esporte=parsed['esporte'],
            liga=parsed['liga']
        )

        self.db.add(bet)
        self.db.commit()
        self.db.refresh(bet)
        return bet

    def get_all_bets(self) -> List[Bet]:
        return self.db.query(Bet).all()

    def get_bets_by_sport(self, esporte: str) -> List[Bet]:
        return self.db.query(Bet).filter(Bet.esporte == esporte).all()

    def get_bets_by_date_range(self, start_date: date, end_date: date) -> List[Bet]:
        return self.db.query(Bet).filter(Bet.data >= start_date, Bet.data <= end_date).all()

    def calculate_roi(self, bets: List[Bet]) -> float:
        """
        ROI = (total profit / total stake) * 100
        """
        total_profit = sum(bet.lucro for bet in bets)
        total_stake = sum(bet.entrada for bet in bets)
        if total_stake == 0:
            return 0.0
        return (total_profit / total_stake) * 100

    def calculate_win_rate(self, bets: List[Bet]) -> float:
        """
        Win rate = (wins / total bets) * 100
        """
        wins = sum(1 for bet in bets if bet.resultado == 'green')
        total = len(bets)
        if total == 0:
            return 0.0
        return (wins / total) * 100

    def get_bank_evolution(self, bets: List[Bet]) -> List[Dict[str, Any]]:
        """
        Calculate bank evolution over time
        """
        bets_sorted = sorted(bets, key=lambda x: x.data)
        cumulative_profit = 0
        evolution = []
        for bet in bets_sorted:
            cumulative_profit += bet.lucro
            evolution.append({
                'data': bet.data,
                'lucro_acumulado': cumulative_profit
            })
        return evolution

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get main metrics
        """
        bets = self.get_all_bets()
        total_profit = sum(bet.lucro for bet in bets)
        total_stake = sum(bet.entrada for bet in bets)
        roi = self.calculate_roi(bets)
        win_rate = self.calculate_win_rate(bets)

        return {
            'lucro_total': total_profit,
            'roi': roi,
            'total_apostado': total_stake,
            'taxa_acerto': win_rate,
            'total_apostas': len(bets)
        }

    def get_profit_by_day(self, bets: List[Bet]) -> pd.DataFrame:
        df = pd.DataFrame([{
            'data': bet.data.date(),
            'lucro': bet.lucro
        } for bet in bets])
        return df.groupby('data').sum().reset_index()

    def get_profit_by_sport(self, bets: List[Bet]) -> pd.DataFrame:
        df = pd.DataFrame([{
            'esporte': bet.esporte,
            'lucro': bet.lucro
        } for bet in bets])
        return df.groupby('esporte').sum().reset_index()

    def get_bets_count_by_sport(self, bets: List[Bet]) -> pd.DataFrame:
        df = pd.DataFrame([{
            'esporte': bet.esporte
        } for bet in bets])
        return df.groupby('esporte').size().reset_index(name='count')