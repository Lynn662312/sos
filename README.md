# 🆘 S.O.S — Source of Safety

Instant, verified disaster alerts for foreigners in Japan.

Real-time translation · AI trust scoring · Voice instructions · Blockchain provenance

## 🌏 The Problem

When a foreigner travels to a country whose language they don't speak and whose local systems they don't know, a natural disaster becomes doubly dangerous. During earthquakes, floods, or severe weather, reliable information is hard to find fast — and when chaos spreads, so does misinformation. Fake alerts circulate while official warnings go unread, putting lives at risk.

Japan is a clear example: the country publishes official disaster alerts from the Japan Meteorological Agency (JMA) in Japanese only. S.O.S intercepts those official alerts the moment they are published, filters them by prefecture, translates them into English and Simplified Chinese, scores their credibility with AI, and reads them aloud — so anyone can understand and act fast.

## ✨ Key Features

- **Real-time Alerts**
  - Live JMA official Atom feed ingestion for earthquake, weather, and volcanic alerts.
- **Instant Translation**
  - Gemini AI translates alert title, summary, and emergency instructions into English + Chinese.
- **Voice Instructions**
  - ElevenLabs TTS reads alert content aloud in a natural voice.
- **Trust Scoring**
  - Gemini rates credibility 0–10 based on official source markers.
- **IPFS Provenance**
  - Alerts are SHA-256 hashed and pinned to IPFS via Pinata for tamper-proof traceability.
- **Solana Devnet Proof**
  - Optional lightweight Solana devnet memo for on-chain recording of alert hash + IPFS CID.
- **Tokyo-first Filter**
  - Prefecture selection with Tokyo as the default.
- **Demo Mode**
  - One-click mock Critical alert for testing and presentation.

## 🎙️ ElevenLabs Integration

### Integration Path: Generate Speech (Text-to-Speech)

S.O.S uses ElevenLabs Multilingual v2 to convert translated alert content into natural-sounding voice instructions.

### How it works

1. User clicks `Generate Voice` on an alert.
2. The frontend builds a TTS script from:
   - alert title
   - translated summary
   - emergency actions
3. A `POST /api/generate-audio/{alert_id}` request is sent to the backend.
4. The backend calls ElevenLabs:

```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text=text,
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)
return b"".join(audio)
```

5. Raw MP3 bytes are returned and played instantly in the Streamlit audio player.

### Why ElevenLabs matters

In a disaster, reading is slower than listening. A foreigner who can't read Japanese or English well can still follow spoken instructions in their preferred language. ElevenLabs’ multilingual model supports both English and Simplified Chinese in one flow.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.10+) |
| Frontend | Streamlit |
| AI Translation + Trust Scoring | Google Gemini 2.5 Flash |
| Voice | ElevenLabs Multilingual v2 |
| Content Fingerprinting | SHA-256 + IPFS via Pinata |
| On-chain Provenance | Solana Devnet (memo transaction) |
| Alert Source | JMA Atom Feeds (`extra.xml`, `eqvol.xml`, `other.xml`) |

## 📂 Project Structure

```text
sos_project/
├── .env                    # API keys (not committed)
├── app/
│   ├── main.py             # FastAPI routes
│   ├── models.py           # Pydantic schemas
│   ├── scraper.py          # JMA feed parser
│   ├── translator.py       # Gemini translation + ElevenLabs TTS
│   └── utils/
│       ├── hasher.py       # SHA-256 fingerprinting
│       ├── ipfs.py         # Pinata IPFS pinning
│       └── solana.py       # Solana devnet memo
└── frontend/
    └── app.py              # Streamlit UI
```

## 🚀 Setup & Run

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/sos-source-of-safety.git
cd sos-source-of-safety
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configure `.env`

Copy the template and add your API keys:

```bash
copy .env_sample .env
```

Then edit `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
ELEVENLABS_API_KEY=your_elevenlabs_api_key
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PRIVATE_KEY=your_base58_private_key
```

- `ELEVENLABS_API_KEY` is required for voice generation.
- `SOLANA_RPC_URL` and `SOLANA_PRIVATE_KEY` are optional for the Solana bonus.

### 3. Start the backend

```bash
uvicorn app.main:app --reload
```

### 4. Start the frontend

```bash
streamlit run frontend/app.py
```

Then visit `http://localhost:8501`.

## 🗺️ User Flow

1. JMA publishes alert (Japanese)
2. S.O.S scraper fetches the feed
3. SHA-256 hash is generated and pinned to IPFS
4. Gemini translates to English + Chinese and scores credibility
5. Gemini extracts category and prefecture
6. FastAPI serves translated alerts
7. Streamlit displays color-coded alerts
8. User clicks `Generate Voice`
9. ElevenLabs reads the alert aloud in the selected language

## ⛓️ Solana Devnet

Alert hashes and IPFS CIDs are prepared for optional Solana devnet memo proof. This is a lightweight provenance add-on to strengthen traceability.

## ✅ Hackathon fit

This project is well suited for the **ElevenLabs** track because it combines:
- voice-first disaster accessibility
- AI translation + trust scoring
- official alert provenance

It also supports a **Solana bonus** path for on-chain provenance, but the core submission is already strong without it.

---
