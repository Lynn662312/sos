from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

from app.scraper import fetch_jma_alerts


app = FastAPI(title="S.O.S API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/alerts")
def get_alerts():
    alerts = fetch_jma_alerts()
    return jsonable_encoder(alerts)

