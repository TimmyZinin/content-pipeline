# Decisions — устойчивые решения

> Только то, что не должно теряться между сессиями.
> Не operational state — только policy и architecture decisions.

---

## Planning Model
- **Only Sprint naming.** "Phase" запрещён в planning/roadmap/docs.
- Допустимо: Sprint 4D, Sprint 4D.1, rollout stage within sprint.
- Недопустимо: Phase 1, Phase 2, Phase 2A.
- Зафиксировано: 23 мар 2026.

## Sprint Structure
- Sprint 4D — Rollout Hardening & Link Runtime Alignment
- Sprint 4E — Threads RU Reply Orchestration
- Sprint 4F — Facebook First Comment
- Sprint 4G — LinkedIn System Audit & Integration Design

## Publisher Service
- **Canonical repo:** content-pipeline/publisher-service/
- **Publisher Service owns sent/failed.** n8n = orchestration only.
- **n8n Check Result** = pass-through Code node, no DB write.
- **/test-publish disabled permanently in prod** (HTTP 403). Инцидент 22 мар.

## Allowlist
- Current: telegram, writeas, minds
- Primary filter: SQL upstream in n8n Select Scheduled
- Secondary guard: PUBLISH_ALLOWLIST env var in Publisher Service
- Expansion: both places must be updated synchronously

## Feature Flags
- THREADS_REPLY_ENABLED=false (Sprint 4E scope, not yet started)

## Timezone
- Storage: UTC
- Display: Istanbul (UTC+3)
- Подписывать везде.

## Source of Truth
- docs/ = source of truth
- Wiki = mirror
- При расхождении — docs/ приоритет

## Definition of Done
- Runtime changed
- Repo updated
- Docs updated
- Changelog updated
- Verification evidence
