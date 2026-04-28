import os
import sys
# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.services.bet_service import BetService
from datetime import date

st.set_page_config(page_title="Bet Tracker Dashboard", layout="wide")

def get_data():
    db = SessionLocal()
    service = BetService(db)
    bets = service.get_all_bets()
    db.close()
    return bets

bets = get_data()

if not bets:
    st.write("Nenhuma aposta registrada ainda.")
else:
    # Métricas principais
    st.header("📊 Métricas Principais")
    col1, col2, col3, col4 = st.columns(4)

    total_profit = sum(b.lucro for b in bets)
    total_stake = sum(b.entrada for b in bets)
    roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
    win_rate = (sum(1 for b in bets if b.resultado == 'green') / len(bets)) * 100

    col1.metric("Lucro Total", f"R$ {total_profit:.2f}")
    col2.metric("ROI (%)", f"{roi:.2f}%")
    col3.metric("Total Apostado", f"R$ {total_stake:.2f}")
    col4.metric("Taxa de Acerto (%)", f"{win_rate:.2f}%")

    # Filtros
    st.header("🔎 Filtros")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Data Inicial", value=date.today().replace(day=1))
    end_date = col2.date_input("Data Final", value=date.today())
    sports = list(set(b.esporte for b in bets))
    selected_sport = st.selectbox("Esporte", ["Todos"] + sports)

    # Filtrar dados
    filtered_bets = [b for b in bets if start_date <= b.data.date() <= end_date]
    if selected_sport != "Todos":
        filtered_bets = [b for b in filtered_bets if b.esporte == selected_sport]

    # Gráficos
    st.header("📈 Gráficos")

    if not filtered_bets:
        st.info("Nenhum dado disponível para o filtro selecionado.")
    else:
        # Lucro por dia
        df_profit_day = pd.DataFrame([{'data': b.data.date(), 'lucro': b.lucro} for b in filtered_bets], columns=['data', 'lucro'])
        if not df_profit_day.empty:
            df_profit_day = df_profit_day.groupby('data').sum().reset_index()
        fig1 = px.bar(df_profit_day, x='data', y='lucro', title="Lucro por Dia")
        st.plotly_chart(fig1)

        # Lucro acumulado
        df_cumulative = pd.DataFrame([{'data': b.data, 'lucro': b.lucro} for b in filtered_bets], columns=['data', 'lucro'])
        if not df_cumulative.empty:
            df_cumulative = df_cumulative.sort_values('data')
            df_cumulative['lucro_acumulado'] = df_cumulative['lucro'].cumsum()
        fig2 = px.line(df_cumulative, x='data', y='lucro_acumulado', title="Lucro Acumulado (Banca)")
        st.plotly_chart(fig2)

        # Lucro por esporte
        df_profit_sport = pd.DataFrame([{'esporte': b.esporte, 'lucro': b.lucro} for b in filtered_bets], columns=['esporte', 'lucro'])
        if not df_profit_sport.empty:
            df_profit_sport = df_profit_sport.groupby('esporte').sum().reset_index()
        fig3 = px.bar(df_profit_sport, x='esporte', y='lucro', title="Lucro por Esporte")
        st.plotly_chart(fig3)

    # Métricas por esporte
    st.header("🏆 Estatísticas por Esporte")

    # Calcular métricas por esporte
    sport_stats = {}
    for bet in bets:
        sport = bet.esporte
        if sport not in sport_stats:
            sport_stats[sport] = {
                'total_bets': 0,
                'total_profit': 0.0,
                'total_stake': 0.0,
                'wins': 0
            }
        sport_stats[sport]['total_bets'] += 1
        sport_stats[sport]['total_profit'] += bet.lucro
        sport_stats[sport]['total_stake'] += bet.entrada
        if bet.resultado == 'green':
            sport_stats[sport]['wins'] += 1

    # Preparar dados para exibição
    sports_data = []
    for sport, stats in sport_stats.items():
        roi = (stats['total_profit'] / stats['total_stake']) * 100 if stats['total_stake'] > 0 else 0
        win_rate = (stats['wins'] / stats['total_bets']) * 100
        sports_data.append({
            'Esporte': sport,
            'Total de Apostas': stats['total_bets'],
            'Lucro Total': stats['total_profit'],
            'ROI (%)': roi,
            'Taxa de Acerto (%)': win_rate
        })

    # Ordenar por lucro total (mais lucrativo primeiro)
    sports_data.sort(key=lambda x: x['Lucro Total'], reverse=True)

    # Mostrar tabela
    if sports_data:
        st.subheader("📋 Ranking de Esportes por Lucratividade")
        df_sports = pd.DataFrame(sports_data)
        st.dataframe(df_sports, use_container_width=True)

        # Destaque do esporte mais lucrativo
        most_profitable = sports_data[0]
        st.success(f"🥇 **Esporte mais lucrativo**: {most_profitable['Esporte']} "
                  f"(R$ {most_profitable['Lucro Total']:.2f} de lucro, "
                  f"{most_profitable['Total de Apostas']} apostas)")

        # Gráfico de distribuição de apostas por esporte
        fig_sports_dist = px.bar(df_sports, x='Esporte', y='Total de Apostas',
                                title="Distribuição de Apostas por Esporte",
                                color='Lucro Total',
                                color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_sports_dist)

        # Gráfico de ROI por esporte
        fig_roi = px.bar(df_sports, x='Esporte', y='ROI (%)',
                        title="ROI por Esporte",
                        color='ROI (%)',
                        color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_roi)
    else:
        st.info("Nenhuma aposta registrada ainda para mostrar estatísticas por esporte.")