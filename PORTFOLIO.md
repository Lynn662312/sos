# S.O.S (Source of Safety)

**Slug:** `sos`
**Date:** May 2026 (2026-05-10)
**Status:** Prototype
**Categories:** AI · Backend · Web · Web3 · Voice
**Repo:** [Lynn662312/sos](https://github.com/Lynn662312/sos)
**Live demo:** https://svowjzx4bu4wibaqowyhfa.streamlit.app/
**Hackathon:** Dev3 Hackathon

## Tagline

Instant, verified disaster alerts for foreigners in Japan — JMA feeds translated into English and Chinese, scored for trust, spoken aloud, and fingerprinted for provenance.

## Overview

S.O.S (Source of Safety) is a hackathon MVP that closes the language gap during disasters in Japan. Official Japan Meteorological Agency Atom feeds are Japanese-only, so foreign visitors and residents often cannot act on warnings when seconds matter. S.O.S scrapes those feeds in near real time, filters by prefecture, and uses Gemini to translate titles, summaries, and emergency actions into English and Simplified Chinese while scoring credibility and classifying severity (Critical / Warning / Advisory). Each alert is SHA-256 fingerprinted and pinned to IPFS via Pinata, with optional Solana Devnet memo transactions for lightweight on-chain provenance. Users can hear instructions through ElevenLabs Multilingual v2 — chosen for clarity under stress, hands-free evacuation, and crowd-readable audio. The stack is FastAPI + Streamlit with an in-memory cache; AI runs for translation/scoring and on-demand TTS, while fetch, dedupe, hashing, and IPFS stay deterministic.

## Key Features

- Live JMA Atom feed ingestion (earthquake, weather, volcanic) with ID deduplication
- Prefecture filter (Tokyo-first) with Critical → Warning → Advisory sorting
- Gemini translation to English + Simplified Chinese, including extracted emergency actions
- AI trust scoring (0–10) and severity categorization with color-coded UI
- ElevenLabs TTS ("Generate Voice") for title, summary, and actions
- SHA-256 content fingerprinting + IPFS pinning via Pinata
- Optional Solana Devnet memo provenance (hash + CID)
- Demo Mode: one-click mock Tokyo Critical earthquake alert for presentations
- EN/ZH display toggle and in-memory alert cache to limit repeated AI/IPFS calls

## Tech Stack

Python · FastAPI · Streamlit · Pydantic · Gemini · ElevenLabs · IPFS · Pinata · Solana · feedparser

## Outcomes

- End-to-end MVP loop: JMA scrape → hash/IPFS → Gemini translate/score → Streamlit UI → ElevenLabs audio
- Voice treated as core survival UX, not a demo add-on — TTS for speed, accessibility, and hands-free action
- Tamper-evident provenance via SHA-256 + IPFS, with Solana Devnet memo as bonus on-chain proof
- 48-hour hackathon build with staged delivery; live Streamlit UI preview + documented demo video

## Notes for the record

- The live Streamlit deployment is a UI/UX preview only — the JMA scraper and ElevenLabs voice generation require the FastAPI backend running locally (API keys + `uvicorn app.main:app`), documented in the repo README.
- Solana provenance is implemented (`app/utils/solana.py`) and exercised via the manual `fetch_jma_alerts_verified()` pipeline, but is not wired into the live `/api/alerts` endpoint used by the deployed demo (kept off the hot path to conserve API quota).
