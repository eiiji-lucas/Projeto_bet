from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Bet(Base):
    __tablename__ = 'bets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(DateTime, default=datetime.utcnow)
    entrada = Column(Float, nullable=False)
    odd = Column(Float, nullable=False)
    resultado = Column(String, nullable=False)  # 'green' or 'red'
    lucro = Column(Float, nullable=False)
    esporte = Column(String, nullable=False)
    liga = Column(String, nullable=False)