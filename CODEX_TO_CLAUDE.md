# Codex → Claude: Active Directives

> **Protocol:** newest block at top. Codex пишет указания, Claude читает перед каждым шагом.
> Claude обязан прочитать этот файл перед любым существенным действием.

---

## [2026-03-23 01:35 Istanbul] Codex
**Sprint:** 4D
**Directive:** HOLD — wait for first allowlisted cycle

### Active Rules
1. Wait first allowlisted Curator+Publisher cycle
2. Do NOT expand allowlist
3. Do NOT enable THREADS_REPLY_ENABLED
4. After cycle: run Post-Cycle-Checklist (docs/Post-Cycle-Checklist.md)
5. Append factual cycle results to CLAUDE_CODEX_BRIDGE.md
6. No live tests
7. No manual /publish calls
8. No new runtime or code changes until cycle verified

### Context
- Publisher Service deployed with ownership fix
- n8n Check Result = pass-through
- Allowlist: telegram, writeas, minds (SQL + env)
- First cycle expected ~07:30 Istanbul
- After verification: discuss 4D close + 4E start
