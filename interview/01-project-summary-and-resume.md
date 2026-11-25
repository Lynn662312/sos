# What you built and how to present it

## The project in plain English

S.O.S, or Source of Safety, is a Python web application for foreign visitors and residents in Japan. It takes Japanese alert titles and summaries from Japan Meteorological Agency feeds, attempts to select relevant prefecture information, and uses Gemini to produce English and Simplified Chinese text. A Streamlit dashboard displays the results. Users can ask ElevenLabs to read the selected language's title, summary, and emergency actions aloud.

Your engineering contribution is connecting the complete application flow: source ingestion, data models, filtering, API endpoints, AI integration, frontend state, and audio delivery. You also implemented content fingerprinting and IPFS storage, plus an optional Solana memo experiment.

This demonstrates an end-to-end prototype. It does not establish production emergency-service reliability or measured safety outcomes.

## A 30-second introduction

> I built S.O.S, a disaster-alert prototype for foreigners in Japan, during a 48-hour Dev3 hackathon. I connected JMA's Japanese feeds to a FastAPI backend and Streamlit interface, added ID deduplication and basic prefecture filtering, and used Gemini for English and Simplified Chinese translations. I also integrated ElevenLabs so users could hear the alert and emergency actions. The project taught me how to connect external APIs and manage cost, state, and failure handling across a full application.

Use the event duration only if it matches your own experience; the repository alone cannot establish exact working hours.

## A 90-second technical introduction

> The problem I focused on was making Japanese disaster-feed content easier for foreign users to understand. I built the application in Python, with FastAPI handling data processing and Streamlit providing the interface.
>
> When the user refreshes, the backend fetches three JMA Atom feeds, merges their entries, sorts by update strings, and removes duplicate entry IDs. It applies a basic Japanese-keyword prefecture filter and limits the selection to two alerts to control downstream API use. For an uncached alert, it hashes the original summary, asks Gemini for translations and emergency-action text, attempts to pin the result to IPFS, and caches the processed object. The interface then displays the results and supports on-demand ElevenLabs speech.
>
> The prototype has clear limits: regional matching is heuristic, the cache is in memory, and AI output is not verified. I would improve those before expanding features, especially structured location matching, update-aware caching, explicit translation-failure states, and tests for incorrect or missing data.

## How an interviewer could evaluate this project

| Evaluation area | Evidence the repository offers | What you need to demonstrate verbally |
| --- | --- | --- |
| Product thinking | Language selection, audio, region selection, severity styling | Explain the user journey and why each feature helps |
| End-to-end ownership | Backend, UI, integrations, configuration in one project | Trace one alert without relying on buzzwords |
| Backend fundamentals | Three routes, Pydantic models, deduplication, processing cache | Explain inputs, outputs, validation, state, and failure behavior |
| API integration | JMA, Gemini, ElevenLabs, Pinata, optional Solana | Explain what you implemented versus what providers supply |
| Time management | A bounded prototype and staged roadmap | Give your actual prioritization story, including omitted work |
| Engineering maturity | Identifiable tradeoffs and limitations | Recognize unsafe assumptions and propose focused fixes |
| Production readiness | Limited evidence: no tracked CI/tests, persistence, or monitoring | Be candid about what has not been validated |

A strong junior-level discussion can come from this project if you understand its mechanics. Listing technologies without explaining the two-alert limit, cache, filter behavior, and AI failure path will invite difficult follow-ups.

## Your résumé, checked against the implementation

| Claim | Assessment | Precise explanation |
| --- | --- | --- |
| Solo Developer | Your stated experience | A repository cannot establish who personally wrote or reviewed every line. Explain your own role and any assistance honestly. |
| Dev3 Hackathon, 48 hours, May 2026 | Supported as project context by your account, roadmap, portfolio, and May history | Later September fixes also exist. Separate the original prototype from later maintenance. |
| Full-stack app | Supported | Python frontend and backend communicate through HTTP. Full-stack does not require React. |
| Three JMA alert types | Supported as broad source coverage, with limits | `extra.xml` contains weather-related information; `eqvol.xml` combines earthquakes and volcanoes; `other.xml` contains other information. There are no three dedicated parsers or comprehensive per-type tests. |
| FastAPI REST API | Supported | `GET /api/alerts`, `POST /api/translate`, and `POST /api/generate-audio/{alert_id:path}`. |
| Deduplication | Supported | A set removes repeated feed entry IDs within each fetch. SHA-256 is not the deduplication key. |
| Region filtering | Partially qualified | Japanese substring matching; 37 mapped prefectures versus 47 UI choices; two-result limit; nationwide fallback. |
| English and Simplified Chinese | Supported as implemented capability | Gemini is prompted for both. Failed translations return original Japanese text in the translation fields. Accuracy is unmeasured. |
| Reads emergency actions aloud | Supported | The user clicks Generate Voice; title, summary, and action text are sent to ElevenLabs. |
| “Japanese-only warnings” | Narrow the wording | Say “Japanese-language JMA feed content.” JMA also provides multilingual information. |

JMA's official [feed classification](https://xml.kishou.go.jp/xmlpull.html) supports the feed distinction. Its [multilingual information page](https://www.jma.go.jp/jma/kokusai/multi.html) is why you should avoid claiming that all JMA information exists only in Japanese.

## Suggested résumé wording

**S.O.S (Source of Safety) — Disaster Alert Web App for Foreigners in Japan**  
**Solo Developer | Dev3 Hackathon (48-hour prototype) | May 2026**  
**FastAPI, Streamlit, Gemini, ElevenLabs**

- Built a full-stack prototype integrating JMA feeds for earthquake, weather, and volcanic information, with a FastAPI backend, ID deduplication, and basic prefecture filtering.
- Integrated Gemini to translate Japanese alert titles and summaries into English and Simplified Chinese, and ElevenLabs to read translated alerts and emergency-action text aloud on demand.

If your own build fits the 48-hour claim, you can instead start the first bullet with “Delivered a full-stack prototype during a 48-hour hackathon.” Do not replace a working prototype outcome with invented impact metrics.

## What you can claim beyond the two bullets

You can discuss SHA-256 summary fingerprints, best-effort Pinata/IPFS pinning, an ID-based process cache, language-specific audio stored in Streamlit session state, and a Solana Memo Program helper exercised through a separate manual pipeline.

Explain the distinction between implementing a provider integration and building the provider's technology: you built the pipeline, prompts, data handling, UI, and failure behavior. You did not train Gemini, build a speech model, operate JMA's alert network, or write a custom Solana program.

## Keep the timeline accurate

The repository contains May 8–10 development activity. September 6 activity, in Asia/Kuala_Lumpur time, includes deployment configuration, dependency/runtime pinning, a missing-Gemini-key fallback fix, and deployment documentation. Those commits are dated September 5 in UTC.

The documented dependency incident is a useful later-maintenance story: an unpinned Solana dependency changed an import path, after which versions and Python were pinned. Explain it as recorded in commit history unless you personally handled and remember the incident.

Several September commits include AI co-author trailers. If asked about AI assistance, explain your actual workflow and what you checked. “Solo developer” can describe project responsibility without implying that you never used tools or assistance.

## Evidence you should prepare yourself

Before an interview, be ready to describe one real difficult moment, one decision you personally made, and one verification you actually performed. Have the demo video or screenshots available if live hosting is unavailable. Existing README links are evidence of a documented demo, not a guarantee that the service is healthy today.

If asked for results, distinguish implementation from validation:

> I completed the integrated prototype. I do not have measured adoption, translation-accuracy, or disaster-response outcome data, so I would not claim those results.
