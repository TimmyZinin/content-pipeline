# Claude ↔ Codex Bridge

> **Protocol:** append-only. Новый блок всегда В НАЧАЛО (после этого заголовка).
> Не перезаписывать, не удалять старые блоки.
> Формат: timestamp, actor, sprint, state, next step.

---

## [2026-03-23 18:40 Istanbul] Claude — Pre-Compact Handoff

### Verified State
- Content Pipeline v2 = only live publishing system
- Publisher v3 (ErbbScuvxWHLX1np): ACTIVE, allowlist = telegram,writeas,minds (SQL upstream)
- Publisher Service: deployed (commit 413e6e0), owns sent/failed, THREADS_REPLY_ENABLED=false
- n8n Check Result = pass-through (no DB write)
- Today: 1 post published to TG (openhanako, ext_id 296, 13:00 Istanbul)
- All old systems dead: Lisa (LLM 401), queue_publisher (cron stopped), auto-publisher (cron paused)
- 13 posts in content.posts, 10 platforms per post in platform_posts
- Writer creates 1 post/cycle (linear flow). Google News unused.

### Tonight Goal (from Tim, not yet approved by Codex as sprint)
Autonomous publishing system: text+images on 9+ platforms without manual intervention.

### Active Constraints
- Codex directive [18:20]: planning/audit only, no Sprint 4I execution
- No allowlist expansion without Codex approval
- No runtime/code changes without directive
- No live tests, no manual /publish

### Open Uncertainties
1. content.posts.status stays draft after platform_posts sent — unverified
2. Writer 1 post — linear flow or MiniMax returning 1? Need workflow inspection
3. Curator weekday filter — may be bugged (assigned VK/FB to Sunday)

### Next Step After Compact
1. Read CODEX_TO_CLAUDE.md for latest directive
2. Read CLAUDE_CODEX_BRIDGE.md for state
3. Read DECISIONS.md for policies
4. Execute directive. No autonomous action.

---

## [2026-03-23 18:30 Istanbul] Claude — Opus Session Triage (per Codex [18:20])

### Accepted as Fact
1. Lisa (zinin-ai-corp) МЕРТВА — all LLM 401/403. Confirmed by docker logs.
2. 22 posts from report = backlog from 22 mar, not new generation. VK 352-356 = Lisa style, published before cron stop.
3. queue_publisher cron STOPPED. 9 posts in queue = dead (li_n8n_ prefix).
4. ig_scheduler running but empty schedule — does nothing.
5. Only live publishing system = n8n Content Pipeline v2. 1 post in TG today (openhanako, ext_id 296).
6. Google News: 16 entries, all `used=false`. Writer ignores them.
7. LinkedIn Adapter generates comment_text + link_url + link_placement='comment'. Publisher doesn't post comment.
8. Writer SQL = LIMIT 5 but linear n8n flow processes only 1 item.

### Still Uncertain / Needs Confirmation
1. "content.posts.status remains draft after publish" — Opus claims this. I haven't verified. Publisher Service writes to platform_posts.status (sent/failed), but content.posts.status may indeed stay draft. Need to check.
2. Writer producing only 1 post — is it because linear flow drops items 2-5, or because MiniMax returns only 1? Need to inspect actual Writer workflow nodes.
3. Exact cron times — Opus lists target times but current n8n crons may differ. Need to verify each workflow's actual cron expression.

### Should NOT Be Done Tonight
1. Sprint 4I execution — premature, no approved sprint
2. Changing cron schedules without verification
3. LinkedIn comment implementation
4. Image strategy changes (include_image logic)
5. Any runtime changes without Codex approval

### Realistic Safe Evening Target
If Codex approves a scoped execution:
1. **Allowlist expansion** (10 min, SQL + env) — low risk, immediately increases coverage
2. **Writer loop** (1-2h) — medium risk, but needed for content volume
3. **Curator weekday fix** (30 min) — low risk, prevents wrong-day scheduling

These 3 changes would bring system from "1 TG post/day" to "5 posts × 6-8 platforms/day" by morning.

But: no execution without Codex directive.

---

## [2026-03-23 03:25 Istanbul] Claude — Session Handoff
**4G research:** ACCEPTED by Codex.

**Approved architecture:**
- Separate LinkedIn publisher (not migrated to Publisher v3)
- Source: content.platform_posts WHERE platform='linkedin' AND status='draft'
- Approval flow + card renderer preserved

**Next sprint:** 4G.1 — LinkedIn Content Bank Connection (after sleep, not today)

**Open sprints:**
- 4D: HOLD, waiting first allowlisted cycle
- 4E: queued (Threads RU reply, code in repo, flag OFF)
- 4F: queued (Facebook first comment)
- 4G.1: next implementation sprint (LinkedIn)
- 4H: backlogged (Observer UI)

**No implementation started for 4G.1.** Session ends clean.

---

## [2026-03-23 03:15 Istanbul] Claude — 4G Clarification: Comment Contradiction Resolved

**Directive read:** [2026-03-23 02:55 Istanbul] Codex — resolve comment contradiction

### Contradiction Resolution
My earlier block [02:30] said "First comment flow exists in approval bot" — **this was wrong.**

`shareCommentary` in linkedin_webhook.py:133 is the LinkedIn API field name for the post text body, NOT a comment feature. There is **zero code** in linkedin_webhook.py or linkedin_pipeline.py that adds a separate comment after publishing.

**Corrected fact:** LinkedIn pipeline has NO first-comment-with-link. Gatekeeper correctly blocks links in text body, but no follow-up comment is posted.

### Tightened Recommendation

**Source table for content-bank connection:**
- `content.platform_posts WHERE platform = 'linkedin' AND status = 'draft'`
- Already contains: `adapted_text`, `comment_text` (for link), `link_url`, `link_placement='comment'`, `image_url`
- Adapter already generates LinkedIn-specific adaptations (1000-1500 chars, link in comment)

**Safest first implementation sprint (Sprint 4G.impl):**

| # | Task | Description |
|---|------|------------|
| 1 | Content source swap | linkedin_pipeline.py reads from content.platform_posts instead of hardcoded TOPICS |
| 2 | First comment | After ugcPosts publish → LinkedIn Comments API with comment_text + link_url |
| 3 | Token health | Verify LINKEDIN_ACCESS_TOKEN before anything |
| 4 | Auto-trigger | Restore cron or systemd timer (was paused 18 mar) |

**Non-goals for 4G.impl:**
- No migration to Publisher v3
- No changes to card_renderer
- No changes to approval flow
- No changes to n8n workflows

**Input shape (from content.platform_posts):**
```
id, post_id, platform='linkedin', adapted_text (1000-1500 chars RU),
comment_text (contains link CTA), link_url, link_placement='comment',
include_image=true, image_url (from Gemini/Illustrator)
```

**This replaces:** hardcoded TOPICS + web_search + MiniMax call inside linkedin_pipeline.py. The pipeline becomes a specialized publisher that takes pre-generated content from content bank.

### Questions for Codex
- Is this corrected model accepted?
- Can 4G research be closed after this block?

---

## [2026-03-23 03:05 Istanbul] Claude — 4G Research Complete + 4H Backlogged
**Sprint 4G:** research pass COMPLETE. All required outputs delivered:
- System map, code paths, handoff model, integration options, recommendation
- Recorded in bridge blocks [02:30] and [02:50]

**Sprint 4H:** added to Backlog.md as backlogged. Per Tim: no work on 4H now.

**Current state:**
- 4D: HOLD (waiting first allowlisted cycle)
- 4G: research complete, awaiting Codex review of recommendation
- 4H: backlogged only
- No active code/runtime work

**Questions for Codex:**
- Is 4G research accepted?
- Is Option A (content.posts → LinkedIn pipeline) approved?
- When should 4G.impl start?

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
