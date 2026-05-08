# Project: S.O.S (Source of Safety)
**Goal**: A disaster transparency platform for foreigners in Japan.
**Core Value**: Instant translation + Source traceability (IPFS) + AI Trust Scoring.

## 🛠 Tech Stack
- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Streamlit
- **AI Engine**: Google Gemini API (using `google-genai`)
- **Web3 Layer**: IPFS via Pinata API (Content Fingerprinting)
- **Blockchain Proof**: Solana devnet for light on-chain provenance
- **Optional Audio**: ElevenLabs TTS for accessibility and demo polish
- **Source**: JMA High-Frequency Atom Feeds (XML)

## 📂 Project Structure
sos_project/
├── .env                # API Keys: GEMINI_API_KEY, PINATA_API_KEY, PINATA_SECRET_KEY, SOLANA_RPC_URL
├── app/
│   ├── main.py         # FastAPI routes & CORS
│   ├── models.py       # Pydantic schemas (Alert with pub_date as datetime, TranslatedAlert, Provenance)
│   ├── scraper.py      # feedparser logic for JMA (eqvol.xml, extra.xml)
│   ├── translator.py   # Gemini API integration (Translation & Trust Scoring)
│   └── utils/
│       ├── hasher.py   # SHA-256 fingerprinting
│       ├── ipfs.py     # Pinata/IPFS JSON pinning
│       └── solana.py   # optional Solana devnet provenance helper

└── frontend/
    └── app.py          # Streamlit UI

## 🗓 48-Hour Roadmap (Optimized for ElevenLabs + Optional Solana Bonus)

**Focus**: ElevenLabs track primary. Solana devnet memo as bonus-at-end if time allows.
**Available time**: ~39 hours (May 9 12:41 AM → May 10 4 PM)

### Stage 1: Foundation (Day 1 Morning) [12-16 hours]
- [done] **Environment**: Initialize venv, install `fastapi uvicorn feedparser pydantic python-dotenv google-generativeai requests streamlit elevenlabs`.
- [done] **Scraper**: Implement `fetch_jma_alerts()` in `scraper.py`. Deduplicate using `entry.id`.
- [done] **Models**: Define Pydantic models. Ensure `TranslatedAlert` inherits from `Alert`.
- [done] **AI (Gemini)**: Implement `translate_text()` in `translator.py` using `gemini-2.5-flash`.
- [ ] **API**: Set up FastAPI app with CORS in `main.py`. Add `GET /alerts` endpoint.
- [ ] **UI**: Build basic Streamlit dashboard in `frontend/app.py` to display alerts.

### Stage 2: Traceability (Day 1 Afternoon) [8-12 hours]
- [done] **Hasher**: Create SHA-256 hash of raw Japanese alert content.
- [ ] **IPFS**: Implement `upload_to_ipfs()` in `utils/ipfs.py` using Pinata.
- [ ] **Integration**: Update Scraper to include `hash` and `ipfs_cid` for each alert.

### Stage 3: Trust Scoring (Day 2 Morning) [6-10 hours]
- [ ] **Scoring Logic**: In `translator.py`, use Gemini to rate credibility (0-10) based on official vs social markers.
- [ ] **API**: Connect everything in `main.py` endpoints: `GET /alerts` and `POST /translate`.

### Stage 4A: ElevenLabs Integration (PRIMARY - Day 2 Afternoon) [2-4 hours]
- [ ] **Audio TTS**: Integrate ElevenLabs in `translator.py`. Add `generate_audio(text, language)` function.
- [ ] **UI**: Add "Play Audio" button in Streamlit for alert title + summary.
- [ ] **Frontend**: Show audio player or download link for generated speech.
- [ ] **README**: Document ElevenLabs integration path (which integration method used).
- **This completes the ElevenLabs track requirement.**

### Stage 4B: Solana Bonus (OPTIONAL - if time allows) [1-2 hours]
- [ ] **Solana Memo**: Use `@solana/web3.js` via simple Python wrapper or direct devnet transaction.
- [ ] **Minimal approach**: Store alert hash + IPFS CID in a Solana devnet memo transaction (not a full program).
- [ ] **Track reference**: Add devnet transaction signature to README for provenance.
- **Note**: This is a lightweight add-on; full Rust program is NOT required for this minimal approach.
