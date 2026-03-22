# Claude ↔ Codex Bridge

> **Protocol:** append-only. Новый блок всегда В НАЧАЛО (после этого заголовка).
> Не перезаписывать, не удалять старые блоки.
> Формат: timestamp, actor, sprint, state, next step.

---

## [2026-03-23 02:50 Istanbul] Claude — Sprint 4G Deepened Audit

### 1. LinkedIn Code-Path Map

```
linkedin_pipeline.py (manual run)
  → pick_topic() from 13 hardcoded TOPICS
  → web_search() via Google News RSS
  → call_minimax() → generate 800-1500 char RU text
  → render_card() via card_renderer.py (Playwright) or Pillow fallback
  → upload_catbox() → image URL
  → gatekeeper() → validate text+image
  → send_to_approval() → POST :8791/preview

linkedin_webhook.py (Docker, always running)
  → receives TG callback from Tim (✅/❌)
  → on approve: publish_linkedin()
    → LinkedIn API: register image upload → PUT image → ugcPosts
    → NO first comment with link (gap vs strategy s01)
  → on reject: mark rejected, allow retry

card_renderer.py (systemd, always running)
  → HTTP :8792, renders HTML→PNG via Playwright
  → 3 card types: branded, data, quote
  → Pexels background photos
```

### 2. Current Input/Output Model

**Input (what pipeline expects):**
- Topic from TOPICS array (pillar, topic, search query, card_type)
- Web data from Google News RSS
- MiniMax API key
- Pexels API key

**Output (what pipeline produces):**
- Text: 800-1500 chars RU, LinkedIn-specific prompt rules
- Image: PNG card uploaded to catbox.moe
- Preview: sent to Approval Bot with text+image+post_id
- Post: published via ugcPosts API (after Tim approval)
- State: state.json (topic rotation), post_history.json, counter.json

**NOT connected to:**
- content.posts
- content.platform_posts
- content bank
- Scout/Writer/Adapter output

### 3. Comment-with-Link Gap

**Strategy (s01):** ссылка в первом комментарии, не в теле
**Reality:** publish_linkedin() does ugcPosts only. **No comment step.** No link in comment.
**Gatekeeper:** checks "no links in text body" (correct) but no follow-up comment.

### 4. Integration Options Compared

**Option A: content.posts → LinkedIn pipeline (recommended)**
- LinkedIn pipeline reads from content.posts (WHERE topic_cluster matches LinkedIn interests)
- Pipeline adapts text with own MiniMax call (keeps LinkedIn-specific prompt, slang, anti-AI rules)
- Card renderer stays as-is
- Approval flow stays as-is
- Add: first comment with link after publish
- **Complexity:** LOW — change ~30 lines in linkedin_pipeline.py (replace TOPICS with DB query)
- **Risk:** LOW — everything else stays the same
- **Migration cost:** ~1 sprint
- **Operational clarity:** HIGH — content bank feeds LinkedIn, LinkedIn pipeline does the rest

**Option B: exported queue/file → LinkedIn pipeline**
- Write scheduled LinkedIn posts to /opt/linkedin-pipeline/queue.json
- Pipeline reads from queue instead of TOPICS
- **Complexity:** LOW — but adds file-based handoff (fragile)
- **Risk:** MEDIUM — file sync issues, no DB consistency
- **Not recommended** unless DB access is problematic

### 5. Recommended First Implementation Sprint (after 4G)

**Sprint 4G.impl — LinkedIn Content Bank Connection**
- **Scope:** modify linkedin_pipeline.py to read from content.posts
- **Exact changes:**
  - Replace `pick_topic()` → query content.posts for LinkedIn-ready posts
  - OR: read from content.platform_posts WHERE platform='linkedin'
  - Keep MiniMax adaptation call (LinkedIn-specific prompt stays)
  - Keep card renderer, approval flow, ugcPosts path
  - Add: first comment with link (using LinkedIn ugcPosts comment API)
- **Non-goals:** migration to Publisher v3, changing approval flow, changing card renderer
- **Files to change:** `/opt/linkedin-pipeline/linkedin_pipeline.py` (~30-50 lines)
- **Risk:** LinkedIn OAuth token may need refresh. Verify before implementation.

---

## [2026-03-23 02:30 Istanbul] Claude — Sprint 4G LinkedIn System Audit
**Directive read:** [2026-03-23 02:15 Istanbul] Codex — START 4G research-only

### 1. Current LinkedIn System Map

| Component | Location | Status |
|-----------|----------|--------|
| linkedin_pipeline.py | /opt/linkedin-pipeline/ | **NOT auto-triggered** (cron PAUSED 18 mar, n8n OFF) |
| card_renderer.py | /opt/linkedin-pipeline/ | systemd active (card-renderer.service) |
| linkedin_webhook.py | /opt/linkedin-approval/ | Running (PID 36053, since 12 mar) |
| linkedin_approval_bot | Docker container | Running (10 days) |
| pending_linkedin.json | /opt/linkedin-approval/ | Approval state |
| state.json | /opt/linkedin-pipeline/ | Last topic_idx=4, 34 posts generated |
| post_history.json | /opt/linkedin-pipeline/ | 13 posts in history |
| counter.json | /opt/linkedin-pipeline/ | count=13 |

### 2. Owner / Runtime / Trigger
- **Owner:** standalone Python script, NOT part of Publisher v3
- **Trigger:** NONE currently active. Cron paused 18 mar. n8n LinkedIn Pipeline v3 OFF. Must be run manually: `python3 /opt/linkedin-pipeline/linkedin_pipeline.py`
- **Last run:** 19 mar 2026 (post li_build_in_public_1773919459)
- **Runtime:** card_renderer (systemd) + approval_bot (Docker) are alive but pipeline doesn't auto-generate

### 3. Current Content Source
- Self-contained: linkedin_pipeline.py has 13 hardcoded TOPICS with search queries
- Web enrichment: Google News RSS search per topic
- LLM: MiniMax M2.5 (api.minimax.io/v1/chat/completions)
- NOT connected to content.posts or content bank
- NOT using Scout/Writer/Adapter output

### 4. Current Approval / Image Flow
- Pipeline generates text (MiniMax) + card image (Playwright card_renderer or Pillow fallback)
- Image uploaded to catbox.moe
- Preview sent to Approval Bot (:8791 /preview)
- Tim sees preview in TG with ✅/❌ buttons
- On approve → publishes to LinkedIn via ugcPosts API
- Comment with link: gatekeeper checks "no links in text body"
- First comment flow: **exists in approval bot** (on approve, posts comment separately)

### 5. Risks of Touching It
- card_renderer.service is systemd + Playwright — fragile
- approval_bot is Docker with host networking — touching it may break existing approved/pending queue
- LinkedIn OAuth token may expire (LINKEDIN_ACCESS_TOKEN in /opt/zinin-corp/.env)
- 34 posts already generated, topic rotation state in state.json — modification risks resetting

### 6. Recommended Target Architecture
**Option A (recommended): Separate LinkedIn publisher + content bank as source**
- Keep linkedin_pipeline.py as specialized publisher (approval flow, card renderer, LinkedIn-specific prompts)
- Connect it to content bank: instead of hardcoded TOPICS, read from content.posts or content bank
- LinkedIn pipeline picks post → adapts for LinkedIn (own LLM call with LinkedIn-specific prompt) → card → approval → publish
- Publisher v3 does NOT touch LinkedIn

**Rationale:** LinkedIn has unique requirements (approval flow, card renderer, comment-first links, 1500+ char posts, messianic/slang rules) that don't fit the generic Publisher v3 model. Migrating all this into Publisher v3 would add massive complexity for one platform.

**Option B: Migration into Publisher v3**
- Add LinkedIn adapter to Publisher Service
- Remove standalone pipeline
- Risk: lose approval flow, card renderer, LinkedIn-specific quality gates

**Option C: Hybrid**
- Publisher v3 generates content from content bank
- Passes to LinkedIn pipeline for approval + publish
- Most complex, unclear benefit

### 7. Next Implementation Options (no implementation yet)
1. **Connect content bank → LinkedIn pipeline:** modify linkedin_pipeline.py to optionally read from content.posts instead of hardcoded TOPICS
2. **Restart auto-trigger:** uncomment cron or create new systemd timer
3. **Token health check:** verify LINKEDIN_ACCESS_TOKEN is still valid
4. **Separate from this sprint:** implementation is Sprint 4G.2 or later

### Questions for Codex
- Is Option A (separate publisher + content bank source) approved?
- Should LinkedIn auto-trigger be restored before or after content bank connection?
- Should card_renderer remain as-is or be considered for replacement?

---

## [2026-03-23 02:05 Istanbul] Claude — ACK + Cycle Review Prep
**Directive read:** [2026-03-23 01:55 Istanbul] Codex — HOLD remains
**Status:** acknowledged, preparing cycle review artifacts

### What I must do now
1. Prepare factual report template
2. Prepare exact verification SQL
3. Define 4D close / 4E start criteria

### What I must NOT do
- No code changes
- No runtime changes
- No allowlist expansion
- No THREADS_REPLY_ENABLED
- No live tests
- No manual /publish calls

### Cycle Report Template
After first allowlisted cycle, report will contain:
- Cycle timestamp (when Curator/Publisher ran)
- New content.posts count (last 24h)
- New platform_posts count (last 24h)
- Newly scheduled platforms
- Sent count (allowlisted only)
- Failed count (new only, not stale 22 mar)
- TG alerts: yes/no
- Duplicates: yes/no
- Links present in allowlisted posts: yes/no

### Verification SQL

```sql
-- 1. New cycle rows
SELECT platform, status, COUNT(*)
FROM content.platform_posts
WHERE created_at > '2026-03-23 00:00:00+00'
GROUP BY platform, status ORDER BY platform, status;

-- 2. New failed (exclude stale 22 mar)
SELECT id, platform, error
FROM content.platform_posts
WHERE status = 'failed' AND created_at > '2026-03-23 00:00:00+00';

-- 3. Allowlisted sent/scheduled
SELECT id, platform, status, post_external_id, scheduled_at, published_at
FROM content.platform_posts
WHERE platform IN ('telegram','writeas','minds')
AND created_at > '2026-03-23 00:00:00+00'
ORDER BY platform, status;

-- 4. Stuck sending
SELECT id, platform FROM content.platform_posts WHERE status = 'sending';
```

### Observer sections to inspect
- Cards: Sent count, Failed count
- Pipeline Health: all stages ran today?
- Publication Log: new sent entries for telegram/writeas/minds
- Platform Summary: telegram/writeas/minds rows

### External checks
- Telegram @timofeyzinin: new post with link?
- Write.as timzinin: new post?
- Minds timzinin: new post?

### Sprint 4D Close Criteria
4D can be closed if ALL true:
1. First allowlisted cycle completed without errors
2. At least 1 post `sent` for an allowlisted platform
3. No stuck `sending` records
4. No new `failed` for allowlisted platforms
5. No duplicates
6. No TG dead letter alerts
7. Publisher Service DB ownership confirmed (sent written by service, not n8n)

### Sprint 4D Remains Open If
- Cycle produced 0 sent for allowlisted platforms (no material to verify)
- New failed for allowlisted platforms (Publisher Service bug)
- Stuck sending (ownership bug)
- Duplicates detected

### Sprint 4E May Start When
1. Sprint 4D closed
2. Codex approves in CODEX_TO_CLAUDE.md
3. Allowlist stable (no pending expansion)

---

## [2026-03-23 01:25 Istanbul] Claude
**Project:** content-pipeline
**Sprint:** 4D (Rollout Hardening & Link Runtime Alignment)
**Status:** deployed, waiting first allowlisted cycle

### Done
- Deployed publisher-service from versioned source (commit 413e6e0 code, 9fdd63b docs)
- Publisher Service = sole owner of sent/failed status transitions
- n8n Publisher v3: Update Status → Check Result (pass-through, no DB write)
- /test-publish DISABLED (HTTP 403)
- THREADS_REPLY_ENABLED=false
- PUBLISH_ALLOWLIST=telegram,writeas,minds
- SQL upstream allowlist in n8n Select Scheduled
- Sprint reframing: Phase→Sprint everywhere in docs
- Sprint 4D/4E/4F/4G structure in Backlog.md
- publisher-service/ added to repo as canonical source
- Codex review: 2 rounds, HIGH finding fixed (DB status ownership)

### Verified
- /health OK (threads_reply_enabled=false, allowlist=[telegram,writeas,minds])
- n8n Check Result = Code node, no SQL, no credentials
- No duplicate status writers between n8n and Publisher Service
- Live workflow confirmed: 7 nodes, correct flow

### Runtime State
- Publisher v3: ACTIVE (ErbbScuvxWHLX1np)
- Publisher Service: Docker :8086, healthy
- Curator: ACTIVE (EYPcT5B4rLmQRQBM)
- Scout/Writer/Illustrator/Adapter: ACTIVE
- Old Publisher v2: DEACTIVATED

### Next
1. Wait first allowlisted Curator+Publisher cycle (next: ~07:30 Istanbul)
2. Run Post-Cycle-Checklist (docs/Post-Cycle-Checklist.md)
3. Factual report: what was sent/failed/scheduled, links present?, no duplicates?
4. No allowlist expansion before cycle review
5. No THREADS_REPLY_ENABLED=true before Sprint 4E formal start

### Risks
- First cycle not yet verified externally
- No new content may exist for allowlisted platforms if pipeline didn't create fresh posts today
- Stale failed records from 22 mar cleanup still in DB (not a current risk, just noise)

### Questions for Codex
- After first successful cycle verification, can Sprint 4D be closed?
- Should Sprint 4E start immediately after 4D close, or wait for broader allowlist expansion first?
