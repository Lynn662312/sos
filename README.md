# 🆘 S.O.S — Source of Safety

Instant, verified disaster alerts for foreigners in Japan.

Real-time translation · AI trust scoring · Voice instructions · Blockchain provenance

## 🌏 The Problem

When a foreigner travels to a country whose language they don't speak and whose local systems they don't know, a natural disaster becomes doubly dangerous. During earthquakes, floods, or severe weather, reliable information is hard to find fast — and when chaos spreads, so does misinformation. Fake alerts circulate while official warnings go unread, putting lives at risk. This is especially dangerous for young travellers (under 21) and solo female travellers who may have fewer local support networks.

Japan is a clear example: the country communicates primarily in Japanese, creating a significant language barrier for foreign visitors and residents during emergencies. Official disaster alerts from the Japan Meteorological Agency (JMA) are published in Japanese only.

**S.O.S** intercepts those official alerts the moment they are published, filters them by prefecture, translates them into English and Simplified Chinese, scores their credibility with AI, and reads them aloud — so anyone can understand and act fast.

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
  - Alert hash + IPFS CID recorded on Solana devnet as a lightweight on-chain memo
- **Prefecture Filter**
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
    - Note: This specific voice was selected for its high clarity and authoritative tone, ensuring it remains intelligible even in noisy, high-stress disaster environments.
5. Raw MP3 bytes are returned and played instantly in the Streamlit audio player.

### Why ElevenLabs matters

In a disaster, information is a survival tool. S.O.S uses the ElevenLabs Multilingual v2 model because text alone is insufficient during a crisis for three critical reasons:

1. **Speed & Accessibility**: Reading requires focus that a person in a state of panic often lacks. Spoken instructions in a native language are processed faster and are accessible to those who may be visually impaired or unfamiliar with specific scripts.  

2. **Crowd Leadership & Calm**: In a crowded environment—like a train station or a tourist landmark—one person playing a clear, authoritative audio alert can inform an entire group of people at once. This collective listening helps synchronize the crowd’s movement, reducing the risk of stampedes and helping people stay calm under pressure.

3. **Hands-Free Safety**: During an evacuation, users need their hands to carry belongings, hold children, or navigate obstacles. Audio allows them to receive life-saving instructions without being tethered to a screen.
   
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
git clone https://github.com/Lynn662312/sos
cd sos
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
5. Gemini extracts category (Critical/Warning/Advisory) and prefecture
6. FastAPI serves translated alerts
7. Streamlit displays color-coded alerts (🔴 red / 🟡 yellow / 🔵 blue)
8. User clicks `Generate Voice`
9. ElevenLabs reads the alert aloud in the selected language

## ⛓️ Solana Devnet

To ensure the source of safety is tamper-proof, alert hashes and IPFS CIDs are recorded on the Solana devnet.

- On-Chain Evidence: Every verified alert creates a lightweight memo transaction.

- Transaction Signature: 3rHmdxNzDtZwiLXEGu1EADTbp4q5ykjN7v57D9snDRcedKZTsDwpUtftYhwXTCrM5kQZoPAqxDPdjf8bFAW5nznc

- Verification: You can verify this transaction on the Solana Explorer (Devnet) : https://explorer.solana.com/?cluster=devnet.

## 🎬 Demo

- **Demo video**: (https://youtu.be/TjSqSvkygRo)
- **Demo link**: 

**Demo Mode**
Click "**🚀 Trigger Demo Mode**" in the sidebar to load a mock Critical earthquake alert for Tokyo — no real disaster needed to see the full UI and audio experience.

## 🔮 Future Features

- Evacuation shelter locator integrated with Japan's official shelter database
- Embassy contacts by nationality for repatriation assistance
- Relief supplies distribution points map
- GPS-based auto prefecture detection
- Push notifications for Critical alerts
- Support for more languages (Korean, Vietnamese, Tagalog)
- Community reports: allow locals to submit ground-level updates, with IPFS content addressing to trace origin and combat misinformation
- Web3 identity verification for community contributors to ensure accountability

## ✅ Hackathon fit

This project is submitted for the **ElevenLabs — Best ElevenLabs Integration** track.
It uses ElevenLabs Generate Speech to deliver life-critical disaster instructions in natural voice across multiple languages. The integration is core to the product — not decorative — because in a real emergency, voice is faster and more accessible than text for people unfamiliar with the local language.

---
