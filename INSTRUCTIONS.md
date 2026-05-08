# Project: S.O.S (Source of Safety)
**Goal**: A disaster transparency platform for foreigners in Japan.
**Core Value**: Instant translation + Source traceability (IPFS) + AI Trust Scoring.

## 🛠 Tech Stack
- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Streamlit
- **AI Engine**: Google Gemini API (using `google-genai`)
- **Web3 Layer**: IPFS via Pinata API (Content Fingerprinting)
- **Source**: JMA High-Frequency Atom Feeds (XML)

## 📂 Project Structure
sos_project/
├── .env                # API Keys: GEMINI_API_KEY, PINATA_API_KEY, PINATA_SECRET_KEY
├── app/
│   ├── main.py         # FastAPI routes & CORS
│   ├── models.py       # Pydantic schemas (Alert with pub_date as datetime, TranslatedAlert, Provenance)
│   ├── scraper.py      # feedparser logic for JMA (eqvol.xml, extra.xml)
│   ├── translator.py   # Gemini API integration (Translation & Trust Scoring)
│   └── utils/
│       ├── hasher.py   # SHA-256 fingerprinting
│       └── ipfs.py     # Pinata/IPFS JSON pinning
└── frontend/
    └── app.py          # Streamlit UI

## 🗓 48-Hour Roadmap (Vibe Coding Guide)

### Stage 1: Foundation (Day 1 Morning) [12-16 hours]
- [done] **Environment**: Initialize venv, install `fastapi uvicorn feedparser pydantic python-dotenv google-generativeai requests streamlit`.
- [done] **Scraper**: Implement `fetch_jma_alerts()` in `scraper.py`. Deduplicate using `entry.id`.
- [done] **Models**: Define Pydantic models. Ensure `TranslatedAlert` inherits from `Alert`.
- [done] **AI (Gemini)**: Implement `translate_text()` in `translator.py` using `gemini-2.5-flash`.
- [ ] **API**: Set up FastAPI app with CORS in `main.py`. Add GET /alerts endpoint.
- [ ] **UI**: Build basic Streamlit dashboard in `frontend/app.py` to display alerts.

### Stage 2: Traceability (Day 1 Afternoon) [8-12 hours]
- [done] **Hasher**: Create SHA-256 hash of raw Japanese alert content.
- [ ] **IPFS**: Implement `upload_to_ipfs()` in `utils/ipfs.py` using Pinata.
- [ ] **Integration**: Update Scraper to include `hash` and `ipfs_cid` for each alert.

### Stage 3: Trust Scoring (Day 2 Morning)  [6-10 hours]
- [ ] **Scoring Logic**: In `translator.py`, use Gemini to rate credibility (0-10) based on official vs social markers.
- [ ] **API**: Connect everything in `main.py` endpoints: `GET /alerts` and `POST /translate`.

### Stage 4: Frontend & Polish (Day 2 Afternoon) [4-6 hours]
- [ ] **UI**: Build Streamlit dashboard. Show colors based on `trust_score`.
- [ ] **Rumor Checker**: Add a search bar to verify external text against our internal hash database.
- [ ] **Demo**: Add ElevenLabs audio (Optional) and record demo video.