from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from app.utils.ipfs import upload_to_ipfs
from app.utils.solana import record_provenance_on_chain
from app.utils.hasher import generate_content_hash
from app.models import Alert, AudioRequest
from app.scraper import fetch_jma_alerts
from app.translator import _model_to_dict, generate_audio, translate_alert_data


app = FastAPI(title="S.O.S API", version="0.1.0")

# Static files (future audio, etc.)
repo_root = Path(__file__).resolve().parents[1]
static_dir = repo_root / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/alerts")
def get_alerts(prefecture: str = "Tokyo"):
    # Step A: Fetch raw Japanese alerts (no AI calls here)
    raw = fetch_jma_alerts()

    # Step B: Filter by prefecture substring match in title or summary
    # pref = (prefecture or "").strip()
    # if not pref:
    #     pref = "Tokyo"
    # pref_l = pref.lower()
    pref_map = {
        "Hokkaido": "北海道", "Aomori": "青森", "Iwate": "岩手",
        "Miyagi": "宮城", "Akita": "秋田", "Yamagata": "山形",
        "Fukushima": "福島", "Ibaraki": "茨城", "Tochigi": "栃木",
        "Gunma": "群馬", "Saitama": "埼玉", "Chiba": "千葉", "Tokyo": "東京",
        "Kanagawa": "神奈川", "Niigata": "新潟", "Toyama": "富山",
        "Ishikawa": "石川", "Fukui": "福井", "Yamanashi": "山梨",
        "Nagano": "長野", "Gifu": "岐阜", "Shizuoka": "静岡", "Aichi": "愛知",
        "Mie": "三重", "Shiga": "滋賀", "Kyoto": "京都", "Osaka": "大阪",
        "Hyogo": "兵庫", "Nara": "奈良", "Wakayama": "和歌山",
        "Tottori": "鳥取", "Shimane": "島根", "Kumamoto": "熊本", 
        "Oita": "大分", "Miyazaki": "宮崎", "Kagoshima": "鹿児島", "Okinawa": "沖縄    "
    }
    search_keyword = pref_map.get(prefecture, prefecture)
    # search_keyword_l = search_keyword.lower()
    if prefecture == "All Prefectures":
        filtered = raw[:3] 
    else:
        filtered = [a for a in raw if search_keyword in f"{a.title}{a.summary}"][:3]
        if not filtered:
            filtered = raw[:3]  # Fallback to top 3 if no matches

    
    # Step C: single loop for hashing, translation, IPFS upload, and provenance recording
    translated = []
    for a in filtered:
        # 1. generate hash
        a.hash = generate_content_hash(a.summary)

        #2. translate
        t_alert = translate_alert_data(a)

        #3. upload to ipfs
        try:
            cid = upload_to_ipfs(_model_to_dict(t_alert))
            t_alert.ipfs_cid = cid
        except Exception as e:
            print(f"IPFS upload failed for alert {a.id}: {e}")
        translated.append(t_alert)

    # Sorting: priority desc, then trust_score desc
    category_priority = {"Critical": 100, "Warning": 50, "Advisory": 10}

    translated.sort(key=lambda x: (category_priority.get(x.category, 0), x.trust_score or 0), reverse=True)
    return jsonable_encoder(translated)


@app.post("/api/translate")
def translate(alert: Alert):
    # On-demand translation endpoint (user can translate more items manually)
    translated = translate_alert_data(alert)
    return jsonable_encoder(translated)


@app.post("/api/generate-audio/{alert_id}")
def generate_audio_endpoint(alert_id: str, body: AudioRequest):
    audio_bytes = generate_audio(body.text, body.language)
    return Response(content=audio_bytes, media_type="audio/mpeg")

