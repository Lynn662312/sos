# Technical concepts to understand

For each topic, learn the definition, find it in this repository, and explain one limitation. You do not need to memorize library versions or provider voice IDs.

## 1. HTTP, APIs, and the application boundary

An API is an agreed way for one program to request something from another. HTTP carries a method, URL, headers, optional body, and response.

In S.O.S:

- `GET /api/alerts?prefecture=Tokyo`: the query parameter chooses a filter.
- `POST /api/translate`: the JSON body supplies an alert.
- `POST /api/generate-audio/example`: the path identifies a nominal alert and the JSON body supplies text.
- JSON responses contain structured text data. The audio response contains bytes with an `audio/mpeg` content type.

The browser talks to Streamlit. Streamlit's Python process then calls FastAPI using Requests. The frontend and backend can run on separate machines.

**Know these statuses:** 200 = successful response; 422 = typical FastAPI request-validation failure; 429 = too many requests; 500 = backend failure; 502/503/504 = gateway, availability, or timeout problems. The app does not implement explicit handling for every case. A 200 response can still contain a translation fallback, so HTTP success is not proof of successful enrichment.

**Explain aloud:** “The UI sends a request, FastAPI interprets it, and the response has a defined format.”

## 2. Python collections, functions, and control flow

A **list** preserves a sequence: the feed entries and selected alerts. A **set** tracks unique values: `seen_ids`. A **dictionary** maps keys to values: prefecture names and cached alerts.

```python
ids = ["a", "b", "a"]
seen = set()
unique = []
for alert_id in ids:
    if alert_id in seen:
        continue
    unique.append(alert_id)
    seen.add(alert_id)
# unique is ["a", "b"]
```

This illustrates the repository's ID rule. It does not compare incident meaning or translated text.

`[:2]` means the first two items, not “the two most important.” Its position in the pipeline matters. A `lambda` provides the tuple key used by the final sort: category priority first, score second.

`getattr(entry, "updated", "")` reads an attribute with a fallback. Dictionary `.get()` does something similar for keys. `x or fallback` uses the fallback for any falsy value, including an empty string or zero, not only None.

`try/except` changes how failure propagates. A broad catch may preserve the UI but hide the difference between configuration failure, provider failure, and bad data.

**Learn next:** functions with type hints, inheritance, list comprehensions, exceptions, imports, and the difference between a string and bytes.

## 3. Models, validation, and serialization

A model is a declared data shape. `Alert` describes source data; `TranslatedAlert` extends it. `AudioRequest` describes a request body.

**Validation** checks whether input fits declared rules. **Serialization** converts an object into a form suitable for transmission or storage. The project uses `model_dump()` for dictionaries and `jsonable_encoder()` for JSON-compatible values. Neither makes text true.

A category field typed as a string can still contain “Urgent-ish.” To restrict it, a future model could use an enum or Literal. A score could use numeric bounds; a language could be restricted to supported values. The repository currently performs only some of those checks.

Optional fields with a default of None represent absent information. Null should mean unknown or unavailable; replacing an unknown severity with Advisory changes the meaning.

Read the official [Pydantic models guide](https://docs.pydantic.dev/latest/concepts/models/) and [FastAPI response-model guide](https://fastapi.tiangolo.com/tutorial/response-model/) for model validation and explicit output contracts.

**Check yourself:** Can a well-typed “Critical” value still be wrong? Yes; data validation cannot establish correct classification.

## 4. Feeds, parsing, and time

Atom is an XML-based feed format. A feed entry can provide an ID, title, update time, link, and content or summary. `feedparser` converts that structure into Python-accessible entries.

S.O.S reads the entry content/summary. It does not retrieve every linked full bulletin. This distinction matters because precise area codes, cancellation information, or detailed instructions may require deeper structured parsing.

JMA documents different feed categories and update cycles. That is a property of the source, not evidence that S.O.S continuously polls it. See [JMA's feed documentation](https://xml.kishou.go.jp/xmlpull.html).

**Timestamp example:**

- `2026-05-10T09:00:00+09:00`
- `2026-05-10T01:00:00+00:00`

The second instant is one hour later, although comparing their raw strings can put the 09:00 string first. Convert to aware datetimes and normalize to UTC before ordering.

The UI converts timestamps to JST (UTC+9), handles a trailing Z, assumes UTC when an offset is missing, and returns the input unchanged if parsing fails. That is display logic, not backend ordering logic.

**Learn next:** source IDs versus incident IDs, update/cancellation lifecycle, aware versus naive datetimes, and source schemas.

## 5. Deduplication, caching, and idempotency

These solve different problems:

| Concept | Plain meaning | S.O.S example |
| --- | --- | --- |
| Deduplication | Remove repeated items | Skip a repeated entry ID during one fetch |
| Cache | Reuse a previous computation | Return a processed alert from `_alert_cache` |
| Idempotency | Repetition has the same intended effect | A proposed enrichment job should not create duplicate work for the same alert version |
| Persistence | Keep data after a process stops | Not supplied by the current dictionary |

If alert ID A changes from summary v1 to v2, an ID-only cache still returns v1. A better key might include source ID, source version/content digest, prompt version, and model identifier. Include all fields relevant to the derived result; the current summary-only digest would miss a title change.

A **TTL** is the time after which a cache item expires. It helps limit staleness but does not replace version detection. A bounded cache also prevents unbounded memory growth.

A **cache stampede** happens when many callers miss the same key and all recompute it. Prevent it with coordinated work per key, rather than assuming a dictionary makes a multi-step operation atomic.

**Check yourself:** Does a cache hit prevent another JMA download? No; fetching happens before cache lookup.

## 6. Synchronous code and concurrency

Synchronous code completes one step before continuing in that call. Asynchronous I/O lets a task yield while waiting so other work can proceed.

FastAPI executes ordinary `def` route functions in a thread pool. Blocking provider calls still consume finite worker capacity. Changing the declaration to `async def` does not make a synchronous SDK or `time.sleep()` nonblocking. See [FastAPI's explanation](https://fastapi.tiangolo.com/async/).

Two uncached alerts are enriched sequentially. A rough reasoning model is:

```text
request time =
    combined sequential feed-fetch time
    + sum of each uncached alert's translation and pinning time
    + parsing and serialization
```

This is an explanatory model, not a measured benchmark.

**Learn next:** blocking I/O, thread pools, event loops, worker processes, task queues, and provider concurrency limits. Do not add concurrency before understanding shared state and rate limits.

## 7. Timeouts, retries, and failure states

A timeout prevents some waits from continuing indefinitely. A retry makes another attempt after a failure. A deadline bounds the whole operation.

Requests' timeout is not a guaranteed total download deadline. Its documentation explains the distinction in [Timeouts](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts).

The local frontend change has fixed six-second pauses. Exponential backoff instead grows the delay, such as 1, 2, 4, and 8 seconds, usually with a cap. **Jitter** adds randomness so many clients do not retry simultaneously.

Retry transient failures selectively. A malformed request usually will not improve by repeating it. A repeated paid synthesis call may create another charge or another artifact. Honor provider rate-limit guidance and make the overall wait visible to users.

A useful result distinguishes:

- Source fetch failed.
- Source fetched but no matching alerts were found.
- Source was fetched but translation failed.
- Translation succeeded but pinning failed.
- Audio generation failed.
- Previously fetched data is being displayed.

S.O.S currently collapses some of these states into empty results, fallback fields, or broad error messages.

## 8. LLM integration and evaluation

S.O.S uses an existing model through an API. This is model integration and prompting, not model training.

The prompt asks Gemini to perform translation, extraction, classification, and scoring in one response. JSON output mode addresses format; temperature influences generation variability. Neither establishes accuracy. A stricter output schema can constrain fields and types, while meaning still needs evaluation. See [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output).

For this project, evaluate:

| Dimension | A concrete failure |
| --- | --- |
| Factual preservation | A location, number, time, or negation changes |
| Completeness | A relevant instruction is omitted |
| Grounding | A shelter or evacuation instruction is invented |
| Regional extraction | A mentioned place is incorrectly treated as the affected area |
| Severity | Model output understates the source warning |
| Language | Japanese fallback text is presented as a successful English translation |

Use a fixed, reviewed set of source bulletins and bilingual expected interpretations. Compare model/prompt versions. Include cancellation messages, multiple regions, missing data, and adversarial instruction-like text. Text being translated should be treated as data, not as an instruction to change the model's task.

Do not use the model's own trust score as the only evaluation of its output. Preserve original text and source URLs so results can be checked. JMA's [multilingual terminology resource](https://www.data.jma.go.jp/developer/multilingual.html) is a relevant starting point for terminology review.

**Know the distinction:** Source authenticity, translation fidelity, geographic relevance, severity, and readability are separate properties.

## 9. Text, bytes, and speech generation

Text is a sequence of characters. Audio is encoded binary data. JSON is suitable for the text request, while an audio content type tells the client how to interpret the response bytes.

The ElevenLabs identifier `mp3_44100_128` specifies MP3 with a 44,100 Hz sample rate and 128 kbps bitrate. The project receives chunks from the SDK but joins them before responding. A **buffered** response waits for the complete result; a **streaming** response can send chunks as they arrive. See the [ElevenLabs conversion API](https://elevenlabs.io/docs/api-reference/text-to-speech/convert).

If you later cache audio, include the text digest, language, voice, and model in the key. An ID and language alone cannot distinguish changed content or a changed voice.

**Check yourself:** Does selecting zh translate arbitrary English audio input? No translation step exists in the audio helper; it synthesizes the supplied text and selects a voice.

## 10. Streamlit reruns and session state

Streamlit reruns Python app code in response to interactions. Session state lets values survive those reruns for a user session. See [Streamlit Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state).

The project uses session state for the alert list and audio bytes. This is separate from the backend's process-level cache.

| State | Who shares it? | What happens on reset? |
| --- | --- | --- |
| Backend `_alert_cache` | Requests handled by that backend process | Lost when that process ends |
| Frontend alert/audio session state | The relevant Streamlit user session | Not durable user storage |

A widget needs a unique key when repeated. Demo mode repeatedly inserts `demo-123`, so two Generate Voice buttons can receive the same key.

**Check yourself:** Why does changing language work without a new Gemini call? Both languages were produced and stored together.

## 11. Hashes, content addressing, and provenance

SHA-256 maps bytes to a 256-bit digest, usually shown as 64 hexadecimal characters. The same input bytes produce the same digest. Changing whitespace or Unicode representation can change the input bytes. See [Python hashlib](https://docs.python.org/3/library/hashlib.html).

A hash is not encryption: it is not designed to be reversed into the source text. It is not a signature: anyone can compute a hash. Verification requires a trustworthy reference value.

IPFS addresses content through CIDs. A CID contains more structure than the application's direct summary digest, and the uploaded JSON is a different object from the original summary. See [IPFS CIDs](https://docs.ipfs.tech/concepts/content-addressing/).

Provenance means a record of origin and transformation. A stronger design would preserve original source URL, source update time, fetch time, complete source snapshot, digest, transformation version, and derived output. The unused `Provenance` class sketches only part of this.

**Check yourself:** Can an incorrect translation be pinned and hashed? Yes. Integrity and truth are different.

## 12. Solana concepts relevant to this helper

An **RPC endpoint** is a server API used to communicate with the network. A **keypair** provides a public identity and a private signing key. An **instruction** asks an existing program to perform an operation. A **transaction** packages instructions and signatures.

The helper builds a Memo Program instruction containing a hash and CID. It gets a recent blockhash, creates a versioned transaction, signs it with the configured payer, and submits it.

The helper does not wait for confirmation. Submission and confirmed inclusion are separate stages; see [Solana sendTransaction](https://solana.com/docs/rpc/http/sendtransaction). Devnet is a development environment. The RPC configuration, not the function name, determines which network receives the request.

The memo records what this signer submitted. It does not prove that JMA signed the content or that the translation is correct. This project did not implement a custom Rust program.

## 13. Configuration, deployment, and Git

Environment variables separate configuration and credentials from source. `.env_sample` documents names. `.env` is ignored, but ignoring a file does not erase earlier commits.

`0.0.0.0` is a bind address that accepts connections on available interfaces. `localhost` points to the current runtime. `$PORT` is supplied by the hosting environment.

A dependency **pin** fixes a direct version. A complete **lock** also captures the resolved dependency graph. Python runtime versions matter too: the current container and runtime pin differ.

Render documents that free web services can spin down after 15 minutes without inbound traffic and may take about a minute to wake. Treat that as hosting behavior, not a latency promise from this app. See [Render's free-service documentation](https://render.com/docs/free).

A Git commit is a snapshot of staged changes. Pushing publishes commits to a remote. A deployment is a separate system action, although a hosting service may automatically react to a push. Keep documentation-only work separate from existing application edits.

## 14. Testing, observability, and a possible next design

A **unit test** isolates small behavior. An **integration test** checks components together. An **end-to-end test** checks a user flow. A **mock** replaces a dependency with controlled behavior. These are proposed learning tasks; no tracked suite exists in the reviewed code.

Useful tests target consequences: same-ID updates must not serve old text; changing the prefecture must update the displayed result; malformed model output must not silently look like a minor advisory.

**Observability** means having enough logs and measurements to understand behavior. Add stage durations, source freshness, translation status, provider failures, cache hit rates, and correlation IDs. Avoid logging credentials.

A future durable design could store:

| Record | Example fields |
| --- | --- |
| Source alert version | source_id, source_updated_at, fetched_at, source_url, full_content_digest, raw_payload |
| Derived text | source_version_id, language, model, prompt_version, translated_text, validation_status |
| Audio artifact | text_digest, language, voice, model, storage_reference |
| Provenance attempt | source_version_id, CID, transaction_signature, status, last_error |

This is a proposal, not existing code. A background ingestion/enrichment process would write these records; the API would read prepared results. Start by making the current behavior correct and testable before adding a distributed architecture.
