# Learn it, practise it, explain it

The goal is understanding, not memorizing 45 answers. Work in a separate practice area or branch if you later implement exercises. This documentation task did not change application code.

## A seven-day plan

Plan for roughly 60–90 minutes a day, adjusting to your starting level.

| Day | Read and study | Concrete output | You are ready when… |
| --- | --- | --- | --- |
| 1 | Project summary and résumé audit | Record a 30-second and 90-second explanation | You can explain the user, problem, contribution, and limits without listing tools only |
| 2 | Models, routes, and scraper walkthrough | Draw the flow from Refresh to displayed alert | You can identify every stage and explain the two-alert limit |
| 3 | Python collections, filtering, and cache concepts | Complete exercises 1–4 below | You can predict duplicates, selection, ordering, and same-ID revisions |
| 4 | Translator and audio helper | Explain normal and failed translation, then trace audio | You distinguish valid JSON, correct meaning, and successful HTTP |
| 5 | Streamlit state, HTTP, deployment, retries | Explain why a region change may show old data and why localhost can fail | You can diagnose state and configuration separately |
| 6 | Hashing, IPFS, Solana, and review findings | Write your top three improvements and their tests | You can explain what provenance proves and what it does not |
| 7 | Interview Q&A and mock interview | Record a full rehearsal; revise weak answers | You can answer follow-ups with code evidence and honest uncertainty |

If you have one evening, focus on the summary, request trace, cache/filter behavior, AI failure path, on-demand audio, and your own contribution story.

## Exercises with expected answers

### 1. Distinguish duplicates from similar content

Combined entries, newest first: A, B, A, C, plus one entry without an ID. A and B happen to have identical summary text.

**Predict:** Which entries survive?

**Expected:** The first A, B, and C survive. The repeated A and missing ID are skipped. Identical summaries with different IDs are not removed. The “first A” rule assumes it was successfully added; malformed-entry fallback handling can alter what gets returned.

### 2. Follow filtering and limiting

Raw entries are A (Osaka), B (Tokyo), C (Tokyo), D (Tokyo), in that order. Imagine D is a severe alert.

**Predict:** Which IDs are selected for Tokyo, All Prefectures, and an unmatched region?

**Expected:** Tokyo selects B and C. All Prefectures selects A and B. The unmatched region also selects A and B through fallback. D never reaches severity sorting.

**Explain:** Why can a severity sort after slicing not repair the loss of D?

### 3. Sort severity and score

Assume selected alerts are X = Warning with score 10 and Y = Critical with score 2.

**Predict:** Which comes first?

**Expected:** Y. Category priority is the first element of the sort key; trust score is secondary. A high score does not mean high severity.

### 4. Detect stale cache behavior

Fetch A with summary v1. It is translated and cached. Later, JMA returns the same ID with summary v2.

**Predict:** What does the current route return for A?

**Expected:** The cached processed v1 object. It checks the ID before hashing or translating the new object. A new digest cannot help unless the code computes and uses it for cache validity.

### 5. Separate format from meaning

Gemini returns valid JSON with category “VeryBad,” a missing English summary, and an invented shelter name.

**Predict:** Which defects are guaranteed to be rejected by current declared model types?

**Expected:** None of those specific semantic issues is guaranteed to be rejected: category is a string, translated summary is optional, and a shelter name can be ordinary string text. Other type errors may trigger fallback. Parsing JSON is not an evaluation of truth.

### 6. Explain the failure sequence

Gemini fails once; the fallback object is returned and cached. The provider later recovers.

**Predict:** Does refreshing automatically retry translation for the same selected ID?

**Expected:** No. The cache hit returns the fallback object. The feeds are fetched again, but enrichment is skipped for that ID.

### 7. Separate hash, CID, and source authenticity

Change only an alert's title while keeping its summary unchanged.

**Predict:** Would the repository's summary hash change? What if the whole JSON snapshot were uploaded again?

**Expected:** The summary digest would remain the same. A new JSON snapshot with changed title normally has a different content address under the same IPFS settings. Neither artifact alone proves JMA authored the data.

### 8. Diagnose a frontend report

A user says: “I selected Osaka, but the old Tokyo alerts are still visible.”

**Expected investigation:** Check whether the session already contains alerts and whether Refresh was clicked. The current fetch condition ignores selection changes when data is nonempty. This is independent of the backend's own matching/fallback limitations.

### 9. Explain language and audio state

Generate English audio, switch to Chinese, and inspect the player.

**Expected:** Audio is keyed by ID and language, so English bytes are not automatically the Chinese player. Chinese audio needs its own generation. Switching language does not itself call Gemini because both text languages were already returned. The auto-audio checkbox does not change this.

### 10. Reason about retries without overpromising

The local retry change permits five attempts and waits six seconds between failed attempts. Assume, for this exercise only, that each failed request takes exactly 20 seconds.

**Expected:** 5 × 20 + 4 × 6 = 124 seconds. This arithmetic is not a real upper bound because Requests timeouts are not total operation deadlines. The UI's approximate 30-second wording is therefore not a guarantee.

## A 30-minute mock interview

| Time | Interviewer prompt | What a strong answer contains |
| --- | --- | --- |
| 0–3 min | Introduce yourself through this project | User problem, role, result, scope |
| 3–7 min | Draw the architecture and trace Refresh | Streamlit server, API, feeds, selection, enrichment, cache |
| 7–11 min | Explain deduplication and a same-ID update | Set versus cache, per-fetch scope, stale revision behavior |
| 11–15 min | Explain Gemini failure and trust score | Original-text fallback, misleading Advisory, unverified score |
| 15–18 min | Trace Generate Voice | Text composition, JSON request, provider, buffered bytes, session key |
| 18–21 min | Explain hash, CID, and Solana | Different artifacts, optional manual path, authenticity limits |
| 21–25 min | Choose the first two improvements | Concrete user effect and a meaningful test for each |
| 25–28 min | Describe a real difficulty and any AI assistance | Personal evidence, ownership, validation, no invented story |
| 28–30 min | Summarize what you learned | Specific growth areas and a realistic next step |

If you get stuck, say what you know, point to the relevant function, and explain how you would verify the uncertain part. Do not guess confidently.

## Score your readiness

Give each area 0–2 points:

| Area | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Product explanation | Tool list only | Clear problem | Clear problem, user, and contribution |
| Request trace | Cannot trace | Mostly correct | Includes limit, fallback, cache, and ordering |
| Data/state understanding | Mixes concepts | Understands some | Separates IDs, revisions, cache, and session state |
| AI/audio understanding | Treats provider as magic | Explains integration | Explains integration and failure/validation limits |
| Provenance | Claims hash proves truth | Partial distinction | Correctly separates integrity, identity, and meaning |
| Ownership | Repeats a script | Some real examples | Specific decisions and honest assistance disclosure |
| Improvement plan | Vague scaling claims | Names fixes | Prioritizes user consequences and tests |

11–14 points suggests you are ready for a detailed discussion of this project. At 7–10, revisit weaker areas. Below 7, focus on the walkthrough before rehearsing polished answers. This is a self-check, not a hiring prediction.

## Your personal story worksheet

Fill these privately from memory and evidence before rehearsing:

- The feature or decision I personally owned was…
- The specific error or difficulty I encountered was…
- I investigated it by…
- The change I made was…
- I verified the result by…
- A tool or person helped me with…
- A claim I can support with evidence is…
- Something I did not measure or complete is…
- The next improvement I would implement first is… because…

A useful STAR answer describes Situation, Task, Action, and Result. Keep the action concrete and the result within your evidence. “The UI displayed the translated result and audio played in my demo” is different from “users became safer.”

## Final rehearsal checklist

- [ ] I can explain every field in Alert and TranslatedAlert.
- [ ] I know the three routes and their request/response formats.
- [ ] I can explain why the cache and deduplication are different.
- [ ] I know region filtering is partial and falls back nationwide.
- [ ] I know severity sorting happens after selecting two alerts.
- [ ] I can describe Gemini failure without calling it successful translation.
- [ ] I can explain why the trust score is not proof.
- [ ] I know audio is on demand and buffered.
- [ ] I know Solana is outside the main request path.
- [ ] I can name three improvements and a test for each.
- [ ] My 48-hour story, tool-use disclosure, and outcome claims match what happened.
