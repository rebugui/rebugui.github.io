# Security·AI news automation implementation plan

> AI worker: execute the checked steps using executing-plans or subagent-driven-development; inspect existing dirty files before edits. Never run a live publication as a test.

**Goal:** Generate category-specific current-issue reports and publish only mechanically verified, capped security/AI posts; route failures to Notion review.

**Architecture:** A single daily Hermes script invokes a collector/selector/writer to persist drafts, then a separate gate validates original sources and draft claims before any GitHub publication. Human-approved lane remains `검토 완료`; new auto lane is explicitly opt-in and has independent safety caps and deploy read-back.

**Stack:** Python 3.11, feedparser, arxiv, SQLite, Ollama, Notion API, Hugo, GitHub Actions, Hermes cron. Design: `docs/superpowers/specs/2026-09-23-security-ai-autonomous-news-design.md`.

**Files and ownership:**
- `~/.hermes/skills/auto-sec-blogger/scripts/collector.py`: candidate intake and commit-on-persist seen semantics.
- `~/.hermes/skills/auto-sec-blogger/scripts/news_quality.py` (new): pure freshness, canonical URL, category, source and draft quality checks.
- `~/.hermes/skills/auto-sec-blogger/scripts/intelligence_pipeline.py`: per-category quotas and stable draft/seen accounting.
- `~/.hermes/skills/auto-sec-blogger/scripts/notion_publisher.py`: persist source and gate outcome in Notion.
- `~/.hermes/skills/auto-sec-blogger/scripts/auto_verified_publisher.py` (new): fetch drafted articles, gate, daily cap, verified publish and deploy read-back.
- `~/.hermes/skills/auto-sec-blogger/scripts/auto_publish_approved.py`: reuse content conversion and GitHub publisher only; preserve approved-lane query and statuses.
- `~/.hermes/scripts/run-auto-sec-blogger.sh`: exclusive lock, opt-in dry run, per-stage failure signals.
- `~/.hermes/scripts/run-blog-ops-watch.sh`, `~/.hermes/scripts/run-adsense-stabilize-check.sh`: read-only production monitoring.
- `~/.hermes/skills/auto-sec-blogger/tests/test_news_quality.py`, `tests/test_auto_verified_publisher.py`, `tests/test_collector_retry.py`: deterministic fixtures with no external write.

### Task 1 — Freeze baseline and tests
- [ ] Check `git status --short` in both blog repo and skill repo; do not overwrite preexisting changes in `SKILL.md`, `scripts/config.py`, `scripts/publisher_github.py`. Record currently scheduled jobs, publish status, source DB row count and disabled launchd status.
- [ ] Write failing tests with synthetic published timestamps (aware KST/UTC), a primary source URL, a stale source, forged `CVE-2024-XXXX`, duplicated canonical URLs and prompt-injection text. Execute `python3.11 -m pytest -q tests/test_news_quality.py`; expect assertion failures before implementation.
- [ ] Add `news_quality.py` pure functions `canonical_url(url)`, `is_recent(published, now, hours=72)`, `classify_candidate(article)` and `check_draft(article, markdown, fetched_source_text)` returning `(passed: bool, reasons: list[str])`. Unknown date/URL, missing source, invalid CVE identifier, missing source citation or mismatched category returns explicit reasons; ignore any source text that looks like instructions. No URL fetch in this module. Re-run focused tests until green; commit only files created/modified by this task.

### Task 2 — Reliable two-category intake
- [ ] Test `NewsCollector.fetch_all` on mocked feeds to require nonempty security and AI query groups, stable category tags, and retry after downstream failure. A failed Notion create must not add the URL to `seen_articles`; a successful create adds exactly once.
- [ ] Replace `self.keywords[:3]` query selection with explicit security and AI queries; preserve HN/Hada/arXiv as supplementary sources. Parse publication dates with `email.utils.parsedate_to_datetime` or supplied aware datetime and reject unknown/stale/future records for the automated lane. Canonicalize original links (not tracking links) and dedupe by canonical URL. Add a `mark_seen(url)` call only after successful Notion persistence in `intelligence_pipeline.py`. Track terminal rejection separately from retryable failures.
- [ ] Limit selected drafts to at most two per category per run; skip near-duplicate event titles within a seven-day run ledger in SQLite. Tests for repeated events and AI/security quota; run the entire skill test suite. Commit this task separately.

### Task 3 — Conservative verification and Notion state
- [ ] Using a mocked Notion database schema, test that unknown status/property never publishes. Inspect actual Notion database's `상태` options and only then create/confirm `자동 검증 통과` (API if allowed, otherwise keep dry run and request schema change). Never rename `검토 완료` or `게시 완료`.
- [ ] Add a fetcher with HTTPS-only, timeout, max body size, response content type check and domain allowlist for authoritative original sources. Reject Google News, HN and Hada intermediary URLs as auto-publication sources unless their original first-party article can be resolved and independently fetched. Explicit source-derived evidence for each CVE ID; unresolved or ambiguous text -> review. `check_draft` rejects empty citation, placeholder IDs, dates/versions/benchmarks absent from visible primary text, low-substance prose, category mismatch, duplicated article and content that copies source instructions. Add unit tests for each rejection.
- [ ] Save all drafts to Notion `검토중` first. Route only passing drafts to the new explicit state; retain failure reasons in a local JSON run report even if Notion has no failure-reason property. Dry run must not PATCH Notion or push Git. Commit.

### Task 4 — Publication, caps and idempotency
- [ ] Mock Notion, GitHub publisher and site fetch; prove a nonpassing post never reaches Git; two passing security articles result in at most one security post/day; one AI may also publish; rerun publishes none. Check that `AUTO_PUBLISH_STATUS` for the human lane is still `검토 완료`.
- [ ] Implement `auto_verified_publisher.py` as a separate entrypoint with explicit `--dry-run` and `--enable-auto-publish` flags (default dry-run). Maintain daily ledger per category and a single-writer lock, cache source evidence and link it to the Notion page ID. Before push re-fetch Notion status and re-run quality checks; only a page in `자동 검증 통과` qualifies. If GitHub succeeds, verify deploy run for the exact commit and then HTTP 200 live URL + sitemap inclusion before `게시 완료`; on failure leave recoverable and alert. Never invoke `auto_publish_approved.py` with `검토중` as gate.
- [ ] Run `python3.11 -m pytest -q tests`, `python3.11 -m compileall -q scripts`; commit only relevant files.

### Task 5 — Schedule and observability
- [ ] Modify `run-auto-sec-blogger.sh` to acquire a lock before both pipelines, emit structured per-category counters, run the verified entrypoint in **dry-run mode** for rollout, and keep human-approved publishing as a separate call. Add nonzero exit for failed mandatory stages and a distinct `skipped_duplicate` outcome. Confirm launchd remains disabled and only one Hermes blogger cron is enabled.
- [ ] Monitor category-specific last successful draft and last verified publication, reason codes, deploy failure and placeholder CVE; never mutate source/front matter in monitors. Test scripts via `bash -n`, mocked summary fixtures and actual read-only health checks; inspect logs for secrets and redact.
- [ ] Execute one real-feed **dry run** with Notion/Git writes disabled; show actual security and AI candidate counts and report results, including empty/blocked reasons. Fix defects and rerun.

### Task 6 — Controlled activation and verification
- [ ] Inspect the real dry-run report and at least one draft from each category. If an eligible draft and valid Notion status exist, switch only the verified publisher to `--enable-auto-publish` with a hard cap of 1 per category/day; otherwise keep dry-run and report the exact blocker, never lower the gate merely to get a publication.
- [ ] If real publication occurs, capture commit SHA and GitHub Actions run URL, verify exact live URL, source citation and sitemap, then read back the Notion status. If no article qualifies, verify that `0 auto-published` and queued review reasons are persisted; never manufacture a test post on the live site.
- [ ] Confirm cron configuration, launchd disabled, status of old `blog-ops-agent` (paused), `adsense-stabilize-check`, shell syntax, test suite and Git state. Report AdSense approval as unverified unless independently confirmed.

**Rollout stop rule:** Any evidence of unsourced claim, unexpected Notion status, concurrent writers or uncertain deployment immediately keeps auto publishing disabled, while drafting and human-approved publication may continue.
