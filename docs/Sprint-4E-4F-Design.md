# Sprint 4E + 4F Design: Comment/Reply Orchestration

> Design doc. НЕ implementation — только архитектура.

## Sprint 4E — Threads RU Reply Orchestration

**Цель:** после publish Threads RU → создать reply с CTA/ссылкой
**Scope:** Publisher Service, feature flag, Threads Graph API
**Non-goals:** Threads EN, Facebook, LinkedIn

**Целевой flow:**
```
publish (text+image) → get post_id → create reply container (reply_to_id) → publish reply
```

**Реализация:** Threads RU direct API: create container → publish → create reply → publish reply
**Feature flag:** `THREADS_REPLY_ENABLED`, default OFF
**Data model:** `reply_text` уже есть. Достаточно.
**Risks:** API rate limits, 5s hardcoded wait
**DoD:** versioned code + codex review + flag OFF + docs + verification plan

## Sprint 4F — Facebook First Comment

**Цель:** после publish Facebook → первый комментарий с ссылкой
**Scope:** Publer comment API или Graph API

**Целевой flow:**
```
Publer publish → get post_id → comment API → first comment with link
```

**Data model:** `comment_text` уже есть. Достаточно.

## n8n Changes

Publisher v3 workflow не меняется (7 нод). Изменения только в Publisher Service.

## Rollout

| Sprint | Платформы | Что добавляется |
|--------|-----------|----------------|
| 4E | Threads RU | Reply с ссылкой после основного поста |
| 4F | Facebook | First comment с ссылкой |

## Не делаем

- LinkedIn implementation (Sprint 4G — research only)
- Multi-step warm-up chains
- Отдельный n8n workflow
- Новые таблицы в БД
