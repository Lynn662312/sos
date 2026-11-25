# What an interviewer may challenge

These are source-review findings, not results of a live penetration test or production incident investigation. Suggested changes were not applied to application code. Priorities below are learning and improvement priorities.

A good response is: “The current implementation does X. Under condition Y, that can cause Z. I would change it to W and verify it with this case.”

## Address these first: relevance, freshness, and meaning

| Finding and code | Trigger and consequence | Proposed improvement and a meaningful check |
| --- | --- | --- |
| Incomplete prefecture mapping — `get_alerts()` in [main.py](../app/main.py) | The UI offers 47 prefectures but only 37 have Japanese mappings. An English name searched in Japanese text can miss its alerts. | Complete mappings, then move toward official area codes. Verify every UI choice has supported matching behavior. |
| Unlabeled nationwide fallback — same function | No regional match returns the first two raw alerts, which may concern other regions. | Return explicit no-match/fallback metadata and clearly separate national results. Test an unmatched region with unrelated source entries. |
| Limit before severity — same function | A third or older matching entry is dropped before AI classification; it could be more severe. | Determine authoritative severity before limiting and expose all relevant results or pagination. Test three matching entries where the third is Critical. |
| ID-only cache — `_alert_cache` | Same ID with changed title, summary, or update time returns the previous processed object. | Key by complete source version and transformation version; add bounds/expiry. Test same ID with revised content. |
| Cached failures — same route | A transient Gemini or Pinata failure can remain in the cached object until restart or another invalidation outside the code. | Track processing status; retry failed enrichment separately. Test a failure followed by recovery for the same source version. |
| Misleading translation fallback — [translator.py](../app/translator.py) | Failure places Japanese text in translated fields and sets Advisory, even if the source is serious. | Keep translation status separate from source severity and language. Simulate provider failure for a severe source alert. |
| Generated instructions beyond the source — translator prompt | Generic-procedure instructions can produce actions not stated in the bulletin. | Separate faithful extraction from reviewed general guidance and preserve evidence. Test a bulletin with no action instructions. |
| Weak source/AI distinction — frontend and translator | “Trust Score” and “Verified” wording can imply authenticity or validated accuracy that the code does not establish. | Explain source and transformation status separately; avoid treating model score as proof. Verify that a fallback cannot be displayed as verified translation. |

These limits matter particularly because the product concerns time-sensitive information. They are concrete behavior in this project, not a claim that an actual user was harmed.

## Reliability, API design, and UI behavior

| Finding and code | Trigger and consequence | Proposed improvement and a meaningful check |
| --- | --- | --- |
| Request-driven enrichment — main route | Feed downloads, Gemini, and pinning contribute to response time. Every request fetches feeds even on enrichment cache hits. | Separate ingestion/enrichment from reads after correctness fixes; measure each stage. Compare warm and uncached requests with controlled providers. |
| Feed failures lack explicit status — [scraper.py](../app/scraper.py) | The caller does not inspect feed HTTP/parse status, and the URL fetch has no explicit application timeout. An empty result can be mistaken for no alerts. | Add bounded transport behavior, per-feed error reporting, and last-success metadata. Test one failed feed and one successful feed together. |
| Limited model constraints — [models.py](../app/models.py) | Arbitrary category/language strings and plain timestamp strings pass the declared shape. Missing translated fields can fall back silently. | Add enums, timestamp types, text bounds, and explicit response models. Test unknown categories and invalid language values. |
| Greedy JSON extraction — translator helper | Text containing multiple brace objects can be captured as one invalid JSON string. | Prefer a schema-constrained provider response and one validated object. Test fenced JSON, empty output, wrong field types, and two objects. |
| Public paid-work endpoints — translate/audio routes | Unrestricted callers can submit text that consumes provider quota. The audio route does not validate or retrieve its path ID. | Add appropriate authentication/usage limits, text-size limits, and deliberate ID semantics. Test rejection before any provider call. |
| Frontend region state — [frontend/app.py](../frontend/app.py) | Changing the selector with a nonempty alert list does not refetch. Old-region results remain displayed. | Refresh on selection change or store results by selection. Test Tokyo → Osaka without clicking Refresh. |
| Unused auto-audio control — frontend | Toggling the checkbox changes a variable but never generates speech. | Implement the intended behavior with cost controls or remove the control. Test whether toggling actually changes requests. |
| Repeated demo IDs — frontend | Repeated insertion of `demo-123` can produce duplicate button keys; mock proof values look like real fields. | Use one clearly labeled replaceable demo object or unique keys; mark proof placeholders. Test repeated demo clicks. |
| Local retry behavior — pre-existing local frontend change | All HTTPError exceptions are retried with fixed delays, and the message attributes failures to waking hosting. Invalid payloads are not retried. | Classify errors, cap the overall wait, and report uncertainty accurately. Test transient 503, persistent 400, timeout, and malformed JSON separately. |

The local retry change is not part of baseline commit `99f36da` and was not included in the documentation commit.

## Provenance boundaries you must understand

The SHA-256 digest covers only `summary`. A title or action change with an unchanged summary is outside that digest. A fuller fingerprint should cover a defined, canonical source representation. “Canonical” means the same logical data is serialized consistently before hashing.

Pinata receives the translated alert snapshot before the returned CID is assigned. The CID refers to that snapshot; it is not necessarily a byte-for-byte representation of the later API object with a populated `ipfs_cid`.

The ordinary alert route never calls `record_provenance_on_chain()`. The separate manual pipeline calls it but discards its returned signature or failure marker. The helper submits a transaction without explicitly waiting for confirmation. No transaction ID is attached to `TranslatedAlert`, and no Solana explorer link is rendered in the frontend.

Hashing, pinning, and recording a memo can support tracing content. They do not establish official authorship, correct translation, current relevance, or safe advice. Explain each claim independently.

## Smaller details a careful reviewer might notice

- **Timestamp ordering:** scraper sorts update strings; UI later parses timestamps only for display. Normalize source times before ordering.
- **Global cache coordination:** no TTL, eviction, persistence, per-key lock, or sharing between worker processes.
- **Source links:** the model retains `link`, but the frontend does not display an original-source button.
- **Chinese presentation:** the card title follows the selected language, but the expander subheading always uses the English title.
- **Scraper manual diagnostic:** it receives raw Alert objects but tries to access translated fields; that print path can raise AttributeError.
- **Unused pieces:** `Provenance`, the scraper's `PRIORITY` constant, and several imports do not establish functioning features. The mounted static directory is not where current audio is saved.
- **Development parity:** Python 3.11 in the container differs from the 3.12.9 runtime pin. Direct dependency pins do not lock all transitive dependencies.
- **CORS configuration:** wildcard origins plus credentials needs review for browser clients. CORS is not authentication for server-side Requests calls.
- **Development launch flags:** the devcontainer disables Streamlit CORS/XSRF protections; do not use that as evidence of production hardening.
- **Secrets history:** a commit message says .env was removed from tracking. Ignoring/untracking does not erase history. No secret values were inspected for this review, and credential validity or rotation was not established.
- **Testing evidence:** helper `__main__` blocks and a local pytest cache do not constitute a tracked regression suite. No coverage or pass rate can be inferred.

## Documentation versus implementation

| Existing description | More accurate interview wording |
| --- | --- |
| Instant / real-time alerts | Fetches recent feed entries when requested; no measured delivery guarantee |
| Japanese-only JMA alerts | The ingested feed text is Japanese; JMA also offers multilingual resources |
| Verified / trust score | Official-source ingestion plus experimental AI enrichment; accuracy not independently verified |
| Tamper-proof | Content fingerprints and content-addressed snapshots support tamper evidence relative to trusted references |
| Every alert on Solana | A separate manual pipeline can submit memos; the main route does not |
| Automatic voice for Critical alerts | The checkbox exists; implemented speech is on demand |
| Full prefecture filtering | Basic substring filtering with incomplete mapping and a nationwide fallback |
| Hash/IPFS before translation | Main route hashes, translates, then attempts to pin the translated object |

## A practical improvement order

1. Fix regional relevance, explicit fallback, and translation/severity status.
2. Make revisions invalidate cached results and failed enrichment retryable.
3. Add controlled tests for those behaviors and complete source parsing where needed.
4. Add input limits, usage controls, provider timeouts, and structured diagnostics.
5. Measure latency and freshness; then consider background ingestion and shared storage.
6. Improve accessibility, source linking, and incomplete UI controls.
7. Expand optional provenance only if it serves a clear user need.

In an interview, choosing and defending the first two improvements is more valuable than naming many infrastructure tools.
