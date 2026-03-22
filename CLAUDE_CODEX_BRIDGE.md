# Claude ↔ Codex Bridge

> **Protocol:** append-only. Новый блок всегда В НАЧАЛО (после этого заголовка).
> Не перезаписывать, не удалять старые блоки.
> Формат: timestamp, actor, sprint, state, next step.

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
