import os
import sys
# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.bet_service import BetService
from typing import Dict, Any

app = FastAPI(title="Bet Tracker API", version="1.0.0")

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    service = BetService(db)
    return service.get_metrics()

@app.get("/bets")
def get_bets(db: Session = Depends(get_db)):
    service = BetService(db)
    bets = service.get_all_bets()
    return [{"id": b.id, "data": b.data, "entrada": b.entrada, "odd": b.odd, "resultado": b.resultado, "lucro": b.lucro, "esporte": b.esporte} for b in bets]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)