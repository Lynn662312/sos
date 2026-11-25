# Interview questions and sample answers

Use these to practise, not to memorize a script. Answers about behavior are grounded in code. Answers about your motivation, time management, and tool use must match your real experience. “I would” describes future work.

## HR and project ownership

### 1. Tell me about S.O.S.

**What is being assessed:** Can you explain the project clearly?

**Sample answer:** “S.O.S is a disaster-alert prototype for foreigners in Japan. I connected Japanese JMA feed content to a FastAPI backend and Streamlit interface, with English and Simplified Chinese translation through Gemini. Users can generate spoken versions through ElevenLabs. I built the prototype during a 48-hour hackathon, focusing on a complete flow from official source content to understandable text and audio.”

**Likely follow-up:** What happens when the user clicks Refresh? Practise question 12.

### 2. What problem were you solving? Doesn't JMA already provide translations?

**Sample answer:** “The specific problem I explored was presenting Japanese feed content in one simple interface with regional selection and on-demand speech. JMA does already provide multilingual information, so I would not claim that I invented multilingual disaster alerts. My contribution was building and integrating this particular user flow.”

**Evidence:** [JMA multilingual information](https://www.jma.go.jp/jma/kokusai/multi.html). Avoid repeating the README's broader Japanese-only claim.

### 3. What did you personally build?

**Sample answer:** “My role covered the application pipeline: feed parsing, data models, routes, filtering, deduplication, prompts and response handling, the Streamlit UI, and audio delivery. The repository also includes hashing, Pinata integration, and an optional Solana memo helper. External providers supplied the language model, speech synthesis, and underlying data.”

**Personalize:** State what you personally implemented, reviewed, or debugged. Repository ownership does not prove unaided authorship.

### 4. Why FastAPI and Streamlit?

**Sample answer:** “They allowed a complete Python implementation with separate API and UI responsibilities. FastAPI gave me typed request handling and API documentation. Streamlit made it quick to create interactive selectors, alert cards, and audio playback. That fit a short prototype. For a more complex consumer interface I would reassess the frontend, but changing frameworks would not fix the current data-correctness issues.”

**Follow-up:** Why not React? Explain the time and familiarity tradeoff if that was actually your reason.

### 5. How did you prioritize work within 48 hours?

**Sample answer:** “I prioritized a usable end-to-end path: ingest alerts, translate them, display them, then add voice. The roadmap separates foundation, provenance, scoring, and audio, with Solana as an optional addition. I limited the processing scope instead of trying to implement accounts, GPS, shelter maps, and notifications at the same time.”

**Personalize:** Describe your actual order and time use. The roadmap is a plan, not a timesheet.

### 6. What was the hardest challenge?

**Code-supported topic:** Coordinating external API calls while keeping the demo usable.

**Sample answer:** “One challenge was that translation and pinning happen during an alert request. Their latency and quotas affect the UI. The design filters before enrichment, processes two alerts, and caches results by ID. That limits repeated work, but I now recognize that the cap can hide important alerts and the cache can retain stale data.”

**Personalize:** Only call this your hardest challenge if it was. Otherwise use a real incident and explain symptoms, investigation, change, and verification.

### 7. What was the outcome? How many users did you help?

**Sample answer:** “The outcome was an integrated prototype with a documented demo. I can demonstrate the data flow and language/audio features. I do not have measured user adoption, comprehension improvement, or emergency-response impact, so I would not claim those numbers.”

**Follow-up:** What would you measure? Translation factual accuracy, action fidelity, location relevance, freshness, successful playback, provider failures, and request latency.

### 8. Did you use AI coding tools?

**Answer structure:** “I used [actual tools] for [actual tasks]. I personally checked [specific behavior]. I found or corrected [a real issue]. I remain responsible for understanding and maintaining the result.”

**Evidence:** Some September maintenance commits contain AI co-author trailers. Do not claim every line was written unaided if that is inaccurate. A strong answer describes concrete verification and current understanding; it does not equate generating code with validating it.

### 9. What would you do differently?

**Sample answer:** “I would improve correctness before adding features. First I would make region matching structured and make nationwide fallback explicit. Then I would separate translation status from severity, make caching version-aware, and add tests for those cases. After that I would move expensive processing out of the request path and measure performance.”

### 10. What does this project show about you?

**Sample answer:** “It shows that I can connect a user problem to a working application across several components. The stronger evidence is my ability to explain each boundary and its tradeoffs. It also gave me specific areas to improve: validation, failure states, testing, and operational reliability.”

**Avoid:** “It proves I can build a production emergency platform.” That is not established.

## Backend and data flow

### 11. What makes this full-stack?

**Sample answer:** “I implemented the interface and the backend. Streamlit handles user interaction and display; FastAPI handles feed processing, translation, and audio generation. They communicate using HTTP and JSON, except that audio is returned as binary MP3. Full-stack refers to covering these application layers; a database or JavaScript framework is not required for this prototype.”

### 12. Walk me through one alert request.

**Sample answer:** “The frontend requests `/api/alerts` with a prefecture. The backend fetches three feeds, merges and sorts their entries, and removes duplicate IDs. It filters by Japanese prefecture keywords and selects at most two. For each cache miss it hashes the summary, calls Gemini, attempts IPFS pinning, and caches the result. It sorts those selected results by severity and score, then returns JSON for the UI.”

**Follow-up:** Is Solana in that route? No.

### 13. What are the three JMA types and three feeds?

**Sample answer:** “The résumé refers to earthquake, weather, and volcanic information. The implementation reads `extra.xml` for irregular weather-related information, `eqvol.xml` for earthquake and volcanic information together, and `other.xml` for other information. There is one common Atom-entry parser, not a separate parser for each disaster type.”

**Follow-up:** Are all bulletins covered? No completeness test is present, and the route returns a limited subset.

### 14. How does deduplication work?

**Sample answer:** “Each fetch creates a `seen_ids` set. After combining and sorting entries, the loop skips an entry if its ID is missing or already present. That removes repeat IDs within that fetch. It does not persist deduplication across process restarts, identify all updates to the same real-world incident, or use the summary hash.”

**Follow-up:** Same summary, different IDs? Both can remain.

### 15. What is the time complexity?

**Sample answer:** “For n combined feed entries, sorting is O(n log n). The ID-deduplication loop is expected O(n), using average constant-time set membership and O(n) auxiliary space. Region matching also scans the raw alerts; its work depends on total text length. The final result sort is tiny because there are at most two items. In practice, remote I/O is likely the main latency cost, but I have not benchmarked it.”

### 16. How does prefecture filtering work, and what can go wrong?

**Sample answer:** “The backend maps an English prefecture to Japanese characters and checks for that substring in title plus summary. It maps 37 of the 47 UI prefectures, limits results to two, and returns nationwide results when there is no match. It can miss regional names or relevant areas absent from the summary. I would use official area identifiers and explicit fallback metadata.”

**Follow-up:** Does Gemini do the filtering? No; filtering happens before Gemini's prefecture extraction.

### 17. Why cache alerts? How is that different from deduplication?

**Sample answer:** “Deduplication removes repeated feed entries within one fetch. The backend cache reuses an already processed alert across requests, saving Gemini and Pinata calls. It is a process-local dictionary keyed only by ID. It has no TTL, size limit, persistence, or content-version check, so updates can remain stale and failed translations can stay cached.”

### 18. Is the cache safe under concurrent requests or multiple workers?

**Sample answer:** “The check-then-compute sequence is not coordinated. Two requests can both miss and perform duplicate external calls. Separate worker processes have separate dictionaries. I would use shared storage with a versioned key and per-key coordination or idempotent background jobs. A Python dictionary alone does not make the whole workflow atomic.”

### 19. Are the most severe alerts always shown first?

**Sample answer:** “Only within the selected subset. The code first chooses two recent matching entries, then translates and sorts them by Critical, Warning, Advisory, followed by score. An older Critical alert may never reach that sort. I would use authoritative severity information before applying a display limit, and support pagination or complete relevant-alert coverage.”

### 20. Why use Pydantic?

**Sample answer:** “Pydantic defines the expected shape of alerts and request bodies. `TranslatedAlert` inherits the source fields and adds translated text and enrichment. FastAPI uses the request models for validation. But these models still accept arbitrary category and language strings, and timestamps are plain strings. I would add explicit constraints and output models; type validation does not establish factual correctness.”

### 21. What do the other two endpoints do?

**Sample answer:** “`POST /api/translate` takes an Alert body and returns translation output or fallback. It does not invoke the main route's cache, hashing, or pinning. The audio endpoint takes text and language, calls ElevenLabs, and returns MP3. Its path ID is accepted but not used to retrieve an alert, so arbitrary submitted text can be synthesized.”

### 22. What happens when Gemini fails?

**Sample answer:** “The translation function catches exceptions and returns the original Japanese title and summary in the translation fields, with a null score, Unknown prefecture, Advisory category, and generic failure actions. That prevents one class of crash, but it can misrepresent language and severity. The main route also caches this fallback. I would expose translation failure separately and preserve source severity.”

### 23. How do you ensure Gemini returns usable JSON?

**Sample answer:** “The request asks for JSON output and the prompt lists expected fields. The parser removes optional code fences, extracts a brace-delimited object, and uses `json.loads`. It normalizes action lists and clamps the score. However, it does not send a schema to Gemini or enforce a category enum, and the regex is greedy. I would add schema-constrained output and validate all required fields.”

**Follow-up:** Does correct JSON mean correct translation? No.

### 24. What does your trust score mean?

**Sample answer:** “It is an experimental model-generated rating based on whether wording appears official. It is not a verified probability, calibrated confidence score, or authentication mechanism. The normal feed source is already JMA. I would make source provenance explicit and avoid presenting the score as proof that translated instructions are correct.”

### 25. Can Gemini invent emergency actions?

**Sample answer:** “Yes. The prompt asks it to extract official actions but also asks for generic procedures when details are missing. That creates a risk of adding advice not present in the bulletin. I would separate faithful translation from any general guidance, preserve the official source link, use reviewed templates where needed, and evaluate omissions and unsupported additions with bilingual reviewers.”

**Follow-up:** Is temperature 0.1 enough? No; it is not an accuracy guarantee.

### 26. Explain the ElevenLabs integration.

**Sample answer:** “The UI builds text from the displayed language's title, summary, and emergency actions. It sends a POST with text and language. The backend chooses a voice, uses Multilingual v2, and requests MP3 output. It joins the returned chunks into bytes and sends them back as `audio/mpeg`. Streamlit saves those bytes by alert ID and language and displays a player.”

**Follow-up:** Is it streaming or automatic? It is buffered and triggered by a button; the auto-generate checkbox is unused.

## Frontend, networking, and deployment

### 27. Why does changing the prefecture sometimes leave the old alerts?

**Sample answer:** “The selected widget value changes, but a request only occurs when Refresh is clicked or the session alert list is empty. Existing data is not keyed by prefecture. I would fetch when the selection changes or cache results separately by selection, and make it clear which region the displayed results belong to.”

**Evidence:** `if refresh or not st.session_state.alerts` in the frontend.

### 28. Your functions use def. Does that block all FastAPI traffic?

**Sample answer:** “FastAPI runs ordinary synchronous route functions in a thread pool. A route's blocking external calls still occupy a worker thread, so concurrency is finite. Merely replacing `def` with `async def` while keeping blocking calls would be a mistake. I would choose async-compatible clients or offload work deliberately and measure the bottleneck.”

**Reference:** [FastAPI concurrency](https://fastapi.tiangolo.com/async/).

### 29. What is CORS? Does it secure this API?

**Sample answer:** “CORS controls which browser origins may read cross-origin responses. It is not authentication or a rate limit. This app allows all origins and credentials, which needs review for a browser-facing production API. Here, the Streamlit Python server makes Requests calls, so browser CORS rules are not the authorization mechanism for those calls.”

**Reference:** [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/).

### 30. How do you handle slow hosting and retries?

**Sample answer:** “The committed frontend sends one GET with a 60-second timeout. The local change reviewed with this pack adds up to five attempts, a 20-second request timeout, and fixed six-second waits. It retries all caught HTTP errors, not just 502/503/504. I would retry only appropriate transient failures, use bounded backoff with jitter, and show a realistic deadline rather than assuming every error is a cold start.”

**Follow-up:** Is 5 × 20 + 4 × 6 a guaranteed maximum? No. That is 124 seconds under a simplified assumption; Requests timeouts are not total wall-clock deadlines. See [Requests timeouts](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts).

### 31. How is it deployed?

**Sample answer:** “The repository documents separate Render services for FastAPI and Streamlit. The backend blueprint installs requirements and runs Uvicorn bound to the platform's port. The frontend uses `API_BASE_URL` to reach it. Secrets are environment settings. Python and direct dependency versions are pinned. I would verify current service health before a demo because repository configuration alone cannot prove the deployment is working today.”

### 32. Why does localhost work locally but fail between hosted services?

**Sample answer:** “Localhost refers to the machine or runtime making the request. On my computer both apps can run there. In a hosted frontend, localhost refers to the frontend's own environment, not a separately deployed backend. That is why `API_BASE_URL` must point to the reachable backend address.”

### 33. What dependency problem appears in the history?

**Sample answer:** “A September commit records that an unpinned Solana version removed the imported `solana.rpc.api` path and broke deployment. A later change pinned dependencies and Python. This illustrates why reproducible environments matter. The current repo still has a devcontainer/runtime mismatch, and direct pins are not the same as a complete transitive lock.”

**Personalize:** Present it as your own debugging story only if you actually performed it.

### 34. Is the application real-time?

**Sample answer:** “It reads live feeds when the API is requested. The UI fetches on initial empty state or explicit refresh. There is no scheduler, continuous ingestion, or pushed notification implementation, so I would describe it as on-demand access to recent feed data. I have not measured end-to-end alert delivery latency.”

## Provenance, reliability, and engineering judgment

### 35. What does SHA-256 prove?

**Sample answer:** “It gives a deterministic fingerprint of the exact summary bytes. Comparing against a trusted reference digest can reveal a change. It does not encrypt the content, identify who wrote it, or prove it is true. In this app the hash excludes title, timestamp, translations, and emergency actions, so it does not cover the complete displayed alert.”

### 36. What is the difference between the SHA-256 field and the IPFS CID?

**Sample answer:** “The SHA-256 field hashes the Japanese summary directly. The CID addresses the JSON snapshot uploaded through Pinata and reflects IPFS's representation of that content. They refer to different data and are not interchangeable. Pinning supports retrievability; it does not guarantee permanent availability or correct content.”

**Reference:** [IPFS content identifiers](https://docs.ipfs.tech/concepts/content-addressing/).

### 37. Did you build a smart contract? Is every alert on Solana?

**Sample answer:** “I integrated the existing Solana Memo Program from Python; I did not build a custom program. The helper signs and submits a memo containing a summary hash and CID. A separate manual pipeline invokes it. The main alerts route does not, and the alert model does not store a transaction signature. I would not claim that every displayed alert has an on-chain record.”

### 38. What happens if Pinata or Solana fails?

**Sample answer:** “The main route catches Pinata failures and still returns the translated alert, then caches it without a CID. It does not retry that upload on later ID cache hits. The manual Solana helper returns a failure sentinel for caught send errors, but the caller ignores it; missing configuration raises earlier. I would track explicit provenance status and retry optional work independently.”

### 39. How would you test this project?

**Sample answer:** “I would use fixed feed entries and mocked providers to test duplicate IDs, missing fields, prefecture matches and fallback, two-result selection, same-ID revisions, malformed model output, translation failure, Pinata failure, and audio content type. UI tests would cover changing prefecture, changing language, and repeated demo clicks. Live integration checks would be separate and limited because they consume quota.”

**Follow-up:** Did you already implement those tests? No tracked automated suite is present in the reviewed snapshot.

### 40. What are the main security concerns?

**Sample answer:** “Translation and audio endpoints accept public input that can trigger paid calls, without application-level authentication, rate limits, or text-size limits. I would add usage controls and validation. I would also keep credentials server-side, use least-privilege credentials, and review logs. CORS cannot prevent direct HTTP clients from calling these endpoints.”

**Follow-up:** Is ignoring .env sufficient after it was committed? No; stopping tracking does not remove history or rotate credentials. Do not claim rotation happened without evidence.

### 41. How would you scale it to many users?

**Sample answer:** “I would ingest and normalize feed entries in a background process, store source versions durably, and enrich each version once. The read API would serve prepared results, with shared caching and independently retried enrichment jobs. Audio could be cached by text hash, language, model, and voice. I would measure freshness, latency, provider errors, cost, and cache hit rates before deciding how many workers to add.”

**Follow-up:** What do you store? See the proposed schema in the study guide.

### 42. Is GET /api/alerts a simple read? Are retries harmless?

**Sample answer:** “To the caller it retrieves alerts, but a cache miss can generate translations and create an IPFS pin. Repeating requests can repeat that work after restarts or concurrent misses. I would separate ingestion/enrichment from reads and give enrichment work a content-version key. I would also avoid automatically retrying paid POST operations without considering duplicate charges.”

### 43. Why didn't you use a database?

**Sample answer:** “An in-memory cache was enough to connect the prototype with less setup. Its limitations are clear: no durable history, cross-worker sharing, or robust revision tracking. For a longer-lived service I would store source versions and derived artifacts in a database and use a cache only as an optimization.”

**Personalize:** Use the time/setup explanation only if it was your actual decision.

### 44. What feature looks implemented but is incomplete?

**Sample answer:** “The automatic-audio checkbox is present but never used. Also, region selection does not trigger a fetch by itself, and repeated demo inserts reuse the same ID. These are examples of why a visible control is not evidence that its full behavior works. I would either connect the control, remove it, or label the limitation.”

### 45. Why should we hire you based on this project?

**Sample answer:** “This project gives me concrete experience connecting backend data processing, external APIs, and a user interface. I can explain the code, identify where the prototype makes compromises, and propose a focused validation plan. I would bring that ownership and willingness to investigate to the role, while continuing to improve my testing and production engineering skills.”

**What makes the answer convincing:** Follow it with a real example of your contribution and explain one function without notes. Do not rely on the sample wording alone.
