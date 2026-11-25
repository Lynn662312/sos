# S.O.S interview preparation

Prepared on 25 November 2026. Read this as a study guide, then practise explaining the code in your own words.

## Start here

| Order | Document | What you will learn |
| --- | --- | --- |
| 1 | [Project summary and résumé](01-project-summary-and-resume.md) | What you built, how to introduce it, and which claims need qualification |
| 2 | [Code walkthrough](02-code-walkthrough.md) | Every source file, the actual request flow, models, endpoints, and configuration |
| 3 | [Interview questions and answers](03-interview-questions-and-answers.md) | HR, technical, debugging, design, and ownership questions with sample answers |
| 4 | [Technical study guide](04-technical-study-guide.md) | The concepts behind the code, explained with examples |
| 5 | [Code review and limitations](05-code-review-and-limitations.md) | Issues an interviewer may notice and how to discuss improvements |
| 6 | [Learning plan and mock interview](06-learning-plan-and-mock-interview.md) | A seven-day plan, exercises with expected answers, and a self-assessment |

If your interview is tomorrow, read documents 1 and 5, practise questions 1–8 and 13–26 in document 3, then use the mock interview in document 6.

## What this review covers

The baseline is commit [99f36da](https://github.com/Lynn662312/sos/commit/99f36dafb3bcbec2df1514778f9efb15875c5550). All 19 tracked files were reviewed: application modules, frontend, project documents, dependency/deployment configuration, environment template, and editor/container configuration. Some OneDrive reads timed out, so the matching GitHub commit supplied those files. The initial local status showed only an existing change to `frontend/app.py`; that diff was reviewed separately.

The local frontend adds retry handling that is absent from the committed baseline. This pack labels that behavior explicitly. Application code and that existing change are outside the documentation commit.

This is a source review, not a certification of the deployed service. Live Gemini, ElevenLabs, Pinata, Solana, and disaster-feed workflows were not exercised for this review. Existing deployment claims come from repository documentation/history. No tracked automated test suite or CI workflow was found; local test caches do not establish a passing test suite.

For documentation validation, six groups of isolated checks used extracted functions and fake inputs: summary hashing, regional selection before severity, nationwide fallback, stale same-ID caching, feed-ID deduplication, and JSON/action normalization. These checks made no external-service calls and are not an end-to-end application test suite. Document links, fenced code blocks, and the 45-question count were also checked.

Code describes implementation. Your résumé supplies the solo-developer and 48-hour experience. Git history supports a May 2026 build followed by September maintenance, but cannot prove exact working hours, user impact, or authorship of every line.

## The facts to remember

- The product is a hackathon prototype for making Japanese disaster-feed content easier to understand through English, Simplified Chinese, and audio.
- It reads three Atom feeds. Earthquake, weather, and volcanic information are three subject areas, not three dedicated endpoints or three separate type-specific parsers.
- Refreshing fetches feeds; there is no continuous monitoring, scheduled ingestion, or push notification implementation.
- Deduplication uses feed entry IDs within one fetch. The separate backend cache reuses processed alerts across requests in one process.
- Filtering is substring based, has an incomplete prefecture map, and falls back to nationwide results when no match exists.
- The API selects at most two alerts before translation and severity sorting.
- Gemini output and its “trust score” are model judgments. They do not verify truth or translation accuracy.
- ElevenLabs speech is generated when the user clicks a button. The automatic-audio checkbox is not connected to generation.
- SHA-256 covers the original summary. IPFS pinning is attempted in the main flow. Solana recording exists in a separate manual pipeline.
- You should describe reliability, measured accuracy, scale, and full geographic coverage as future work unless you have independent evidence.

## How to use sample answers

First-person answers are rehearsal drafts based on the code and your stated role. Replace motivations and personal stories with what actually happened. Do not claim a suggested improvement was implemented. Do not invent user counts, accuracy percentages, latency numbers, awards, or time saved.

A useful answer pattern is: **user problem → implementation → reason → limitation → next step**. Aim for 30–60 seconds, then let the interviewer ask for detail.

External learning references were checked on the preparation date. They explain concepts; the repository's pinned versions remain the source of truth for this project's implementation.
